/* VLC Timeline Thumbnails private helper.
 * Copyright (C) 2026 VLC timeline enhancements contributors.
 * SPDX-License-Identifier: GPL-2.0-or-later
 * This program is free software; you may redistribute and/or modify it under
 * the GNU General Public License, version 2 or (at your option) any later version.
 * This program is distributed WITHOUT ANY WARRANTY. See the GPL for details.
 */
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>
#include <mach/mach.h>
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/display.h>
#include <libavutil/imgutils.h>
#include <libavutil/pixdesc.h>
#include <libavutil/time.h>
#include <libavutil/sha.h>
#include <libswscale/swscale.h>

#define RSS_LIMIT (512ULL * 1024 * 1024)
#define ALLOC_LIMIT (128ULL * 1024 * 1024)
#define DECODE_BUFFER_LIMIT (320ULL * 1024 * 1024)
#define MAX_PIXELS (4096LL * 4096)
#define MAX_PACKETS 200000
#define MAX_FRAMES 100000
#define DEADLINE_US 5000000
#define WORKER_DEADLINE_US 15000000

/* The independent watchdog also covers codecs/demuxers that do not poll an
 * AVIO interrupt callback. Darwin RLIMIT_RSS is advisory; measure real memory.
 * Per-allocation, pixel and stream limits prevent metadata-sized allocations;
 * a 10ms RSS/physical-footprint sample kills a decoder exceeding the budget. */
typedef struct {
    int fd; int64_t size; atomic_int_fast64_t deadline, cpu_deadline; atomic_int stop;
    int worker; uint64_t bytes_read, read_calls, seek_calls;
    atomic_size_t decoder_bytes;
} Guard;
static const char *const timeout_reply = "{\"version\":2,\"ok\":false,\"error\":\"timeout\"}\n";
static const char *const resource_reply = "{\"version\":2,\"ok\":false,\"error\":\"resource_limit\"}\n";
static void emergency_exit(const char *reply)
{
    (void)write(STDOUT_FILENO, reply, strlen(reply));
    _exit(1);
}
static int64_t cpu_time_us(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &now)) return INT64_MAX;
    return (int64_t)now.tv_sec * 1000000 + now.tv_nsec / 1000;
}
static int expired(Guard *g)
{
    return av_gettime_relative() >= atomic_load(&g->deadline) ||
           cpu_time_us() >= atomic_load(&g->cpu_deadline);
}
static void begin_operation(Guard *g)
{
    atomic_store(&g->cpu_deadline, cpu_time_us() + (g->worker ? WORKER_DEADLINE_US : DEADLINE_US));
    atomic_store(&g->deadline, av_gettime_relative() + (g->worker ? WORKER_DEADLINE_US : DEADLINE_US));
}
static void idle_operation(Guard *g)
{
    atomic_store(&g->deadline, INT64_MAX);
    atomic_store(&g->cpu_deadline, INT64_MAX);
}
static void *watchdog(void *opaque)
{
    Guard *g = opaque;
    while (!atomic_load(&g->stop)) {
        if (expired(g)) emergency_exit(g->worker ? "" : timeout_reply);
        task_vm_info_data_t info;
        mach_msg_type_number_t count = TASK_VM_INFO_COUNT;
        if (task_info(mach_task_self(), TASK_VM_INFO, (task_info_t)&info, &count) != KERN_SUCCESS)
            emergency_exit(g->worker ? "" : resource_reply);
        if (info.resident_size > RSS_LIMIT || info.phys_footprint > RSS_LIMIT)
            emergency_exit(g->worker ? "" : resource_reply);
        struct timespec delay = {0, 10000000};
        nanosleep(&delay, NULL);
    }
    return NULL;
}
static int interrupt_io(void *opaque) { return expired(opaque); }
static int read_local(void *opaque, uint8_t *buffer, int size)
{
    Guard *g = opaque;
    if (expired(g)) return AVERROR_EXIT;
    ssize_t result;
    do { result = read(g->fd, buffer, (size_t)size); } while (result < 0 && errno == EINTR && !expired(g));
    ++g->read_calls;
    if (result > 0) g->bytes_read += (uint64_t)result;
    return result > 0 ? (int)result : result == 0 ? AVERROR_EOF : AVERROR(errno);
}
static int64_t seek_local(void *opaque, int64_t offset, int whence)
{
    Guard *g = opaque;
    if (expired(g)) return AVERROR_EXIT;
    if (whence == AVSEEK_SIZE) return g->size;
    whence &= ~AVSEEK_FORCE;
    if (whence != SEEK_SET && whence != SEEK_CUR && whence != SEEK_END) return AVERROR(EINVAL);
    ++g->seek_calls;
    off_t position = lseek(g->fd, offset, whence);
    return position < 0 ? AVERROR(errno) : position;
}
static int deny_secondary_io(AVFormatContext *s, AVIOContext **pb, const char *url,
                             int flags, AVDictionary **options)
{
    (void)s; (void)pb; (void)url; (void)flags; (void)options;
    return AVERROR(EPERM);
}
/* Allocate frame buffers directly, without FFmpeg's default reusable pool.
 * This makes the aggregate live allocation bound inspectable and enforceable
 * before allocating another reference picture. Decoder scratch/demux metadata
 * remain covered by the per-allocation and process memory watchdog limits. */
typedef struct { AVBufferRef *owned; Guard *guard; size_t size; } BufferAccount;
static void release_frame_buffer(void *opaque, uint8_t *data)
{
    (void)data;
    BufferAccount *account = opaque;
    atomic_fetch_sub(&account->guard->decoder_bytes, account->size);
    av_buffer_unref(&account->owned);
    av_free(account);
}
static int bounded_get_buffer(AVCodecContext *codec, AVFrame *frame, int flags)
{
    (void)flags;
    Guard *guard = codec->opaque;
    if (expired(guard)) return AVERROR_EXIT;
    int width = frame->width, height = frame->height, aligned_w = width, aligned_h = height;
    int stride_alignment[AV_NUM_DATA_POINTERS] = {0}, alignment = 64;
    avcodec_align_dimensions2(codec, &aligned_w, &aligned_h, stride_alignment);
    for (int i = 0; i < AV_NUM_DATA_POINTERS; ++i)
        if (stride_alignment[i] > alignment) alignment = stride_alignment[i];
    if (aligned_w <= 0 || aligned_h <= 0 || (int64_t)aligned_w * aligned_h > MAX_PIXELS + 65536)
        return AVERROR(ENOMEM);
    int estimate = av_image_get_buffer_size(frame->format, aligned_w, aligned_h, alignment);
    size_t used = atomic_load(&guard->decoder_bytes);
    if (estimate < 0 || (size_t)estimate + 65536 > ALLOC_LIMIT ||
        used > DECODE_BUFFER_LIMIT - ((size_t)estimate + 65536)) return AVERROR(ENOMEM);
    frame->width = aligned_w; frame->height = aligned_h;
    int result = av_frame_get_buffer(frame, alignment);
    frame->width = width; frame->height = height;
    if (result < 0) return result;
    for (int i = 0; i < AV_NUM_DATA_POINTERS; ++i) {
        AVBufferRef *original = frame->buf[i];
        if (!original) continue;
        BufferAccount *account = av_malloc(sizeof(*account));
        used = atomic_load(&guard->decoder_bytes);
        if (!account || original->size > DECODE_BUFFER_LIMIT - used) {
            av_free(account); av_frame_unref(frame); return AVERROR(ENOMEM);
        }
        *account = (BufferAccount){original, guard, original->size};
        AVBufferRef *tracked = av_buffer_create(original->data, original->size,
            release_frame_buffer, account, 0);
        if (!tracked) { av_free(account); av_frame_unref(frame); return AVERROR(ENOMEM); }
        atomic_fetch_add(&guard->decoder_bytes, original->size);
        frame->buf[i] = tracked;
    }
    return 0;
}
static int same_file(const struct stat *a, const struct stat *b)
{
    return a->st_dev == b->st_dev && a->st_ino == b->st_ino && a->st_size == b->st_size &&
           a->st_mtimespec.tv_sec == b->st_mtimespec.tv_sec &&
           a->st_mtimespec.tv_nsec == b->st_mtimespec.tv_nsec &&
           a->st_ctimespec.tv_sec == b->st_ctimespec.tv_sec &&
           a->st_ctimespec.tv_nsec == b->st_ctimespec.tv_nsec;
}
static int parse_number(const char *text, int64_t maximum, int64_t *result)
{
    if (!text || !*text) return 0;
    for (const char *p = text; *p; ++p) if (*p < '0' || *p > '9') return 0;
    char *end = NULL;
    errno = 0;
    int64_t value = strtoll(text, &end, 10);
    if (errno || *end || value < 0 || value > maximum) return 0;
    *result = value;
    return 1;
}
static int origin_for(AVFormatContext *fmt, int64_t *origin)
{
    /* VLC 3.0.24's Matroska demuxer exposes block timecodes directly through
     * GET_TIME/SET_TIME. A positive container start is an initial timeline gap,
     * not an offset to subtract (native seek 6s in a +5s MKV shows source 1s).
     * This policy covers flat Matroska/WebM; ordered editions are unqualified. */
    if (fmt->iformat && fmt->iformat->name &&
        strcmp(fmt->iformat->name, "matroska,webm") == 0) {
        if (fmt->start_time != AV_NOPTS_VALUE && fmt->start_time < 0) return 0;
        *origin = 0;
        return 1;
    }
    if (fmt->start_time != AV_NOPTS_VALUE) { *origin = fmt->start_time; return 1; }
    int found = 0;
    int64_t earliest = INT64_MAX;
    /* An unknown start for any timeline-bearing stream makes an earliest-stream
     * origin ambiguous. Attachments/data/subtitles do not define playback zero. */
    for (unsigned i = 0; i < fmt->nb_streams; ++i) {
        AVStream *s = fmt->streams[i];
        if ((s->disposition & AV_DISPOSITION_ATTACHED_PIC) ||
            (s->codecpar->codec_type != AVMEDIA_TYPE_VIDEO && s->codecpar->codec_type != AVMEDIA_TYPE_AUDIO)) continue;
        if (s->start_time == AV_NOPTS_VALUE || s->time_base.num <= 0 || s->time_base.den <= 0) return 0;
        int64_t start = av_rescale_q(s->start_time, s->time_base, AV_TIME_BASE_Q);
        if (start == INT64_MIN || start == INT64_MAX) return 0;
        if (start < earliest) earliest = start;
        found = 1;
    }
    if (found) *origin = earliest;
    return found;
}

typedef struct {
    AVFrame *frame, *best;
    AVStream *stream;
    int64_t origin, requested, actual, last_pts;
    int decoded, reached;
    const char *error;
} Selection;
static int receive_available(AVCodecContext *codec, Selection *s)
{
    for (;;) {
        int result = avcodec_receive_frame(codec, s->frame);
        if (result == AVERROR(EAGAIN) || result == AVERROR_EOF) return result;
        if (result < 0) { s->error = "decode_failed"; return result; }
        if (++s->decoded > MAX_FRAMES) { s->error = "resource_limit"; return AVERROR(ENOMEM); }
        if (!(s->frame->flags & AV_FRAME_FLAG_KEY)) {
            av_frame_unref(s->frame);
            continue;
        }
        int64_t stamp = s->frame->best_effort_timestamp;
        /* best_effort_timestamp may synthesize a value from DTS. Require an
         * actual presentation timestamp too; unknown PTS is never a success. */
        if (stamp == AV_NOPTS_VALUE || s->frame->pts == AV_NOPTS_VALUE ||
            (s->frame->flags & AV_FRAME_FLAG_CORRUPT)) {
            s->error = "unknown_timing"; return AVERROR_INVALIDDATA;
        }
        if (s->last_pts != AV_NOPTS_VALUE && stamp < s->last_pts) {
            s->error = "ambiguous_timing"; return AVERROR_INVALIDDATA;
        }
        s->last_pts = stamp;
        int64_t absolute = av_rescale_q(stamp, s->stream->time_base, AV_TIME_BASE_Q);
        if (absolute == INT64_MIN || absolute == INT64_MAX ||
            (s->origin > 0 && absolute < INT64_MIN + s->origin) ||
            (s->origin < 0 && absolute > INT64_MAX + s->origin)) {
            s->error = "unknown_timing"; return AVERROR_INVALIDDATA;
        }
        int64_t normalized = absolute - s->origin;
        /* Ignore negative preroll but keep decoding it for reference pictures. */
        if (normalized >= 0) {
            /* v2 returns the first qualified keyframe from the backward seek.
             * Usually this precedes the pointer. Some demuxers/codecs can only
             * deliver a later keyframe; return its truthful PTS without scanning
             * across the GOP for a closer/future candidate. The GUI labels it.
             */
            av_frame_unref(s->best);
            if (av_frame_ref(s->best, s->frame) < 0) {
                s->error = "resource_limit"; return AVERROR(ENOMEM);
            }
            s->actual = normalized;
            s->reached = 1;
        }
        av_frame_unref(s->frame);
        if (s->reached) return 0;
    }
}
static const char *decode_keyframe(AVFormatContext *fmt, AVCodecContext *codec,
                                 int stream_index, Selection *selection, AVPacket *packet)
{
    int draining = 0, drain_sent = 0;
    for (int packets = 0; packets < MAX_PACKETS; ++packets) {
        int read_result = draining ? AVERROR_EOF : av_read_frame(fmt, packet);
        if (read_result == AVERROR_EOF) draining = 1;
        else if (read_result < 0) return "read_failed";
        if (!draining && packet->stream_index != stream_index) { av_packet_unref(packet); continue; }
        int send_result;
        for (;;) {
            send_result = avcodec_send_packet(codec, draining ? NULL : packet);
            if (send_result != AVERROR(EAGAIN)) break;
            int previous_frames = selection->decoded;
            int receive_result = receive_available(codec, selection);
            if (selection->error) return selection->error;
            if (selection->reached) return NULL;
            /* FFmpeg's API forbids send/receive both returning EAGAIN without
             * progress. Fail rather than spinning if a codec violates it. */
            if (receive_result == AVERROR(EAGAIN) && previous_frames == selection->decoded) return "decode_failed";
        }
        av_packet_unref(packet);
        if (send_result < 0 && send_result != AVERROR_EOF) return "decode_failed";
        if (draining) drain_sent = 1;
        int receive_result = receive_available(codec, selection);
        if (selection->error) return selection->error;
        if (selection->reached || receive_result == AVERROR_EOF) break;
        if (drain_sent && receive_result == AVERROR(EAGAIN)) return "decode_failed";
    }
    if (!selection->best->data[0]) return "no_frame";
    if (!selection->reached && !drain_sent) return "resource_limit";
    return NULL;
}

/* Orthogonal matrices cover rotations and mirrors without interpolation.
 * Reject shear, arbitrary angle, perspective and scaling rather than guessing. */
static int orientation_for(AVFrame *frame, AVStream *stream, int *a, int *b, int *c, int *d)
{
    const int32_t *matrix = NULL;
    AVFrameSideData *side = av_frame_get_side_data(frame, AV_FRAME_DATA_DISPLAYMATRIX);
    const AVPacketSideData *coded = av_packet_side_data_get(stream->codecpar->coded_side_data,
        stream->codecpar->nb_coded_side_data, AV_PKT_DATA_DISPLAYMATRIX);
    if (side) { if (side->size != 9 * sizeof(int32_t)) return 0; matrix = (const int32_t *)side->data; }
    else if (coded) { if (coded->size != 9 * sizeof(int32_t)) return 0; matrix = (const int32_t *)coded->data; }
    *a = *d = 1; *b = *c = 0;
    if (!matrix) {
        AVDictionaryEntry *rotate = av_dict_get(stream->metadata, "rotate", NULL, 0);
        if (rotate) {
            char *end;
            errno = 0;
            double angle = strtod(rotate->value, &end);
            if (errno || *end || !isfinite(angle) || fabs(angle / 90.0 - round(angle / 90.0)) > 0.0001) return 0;
            int quarter = (int)fmod(round(angle / 90.0), 4.0);
            if (quarter < 0) quarter += 4;
            if (quarter == 1) { *a = *d = 0; *b = 1; *c = -1; }
            if (quarter == 2) { *a = *d = -1; }
            if (quarter == 3) { *a = *d = 0; *b = -1; *c = 1; }
        }
        return 1;
    }
    if (matrix[2] || matrix[5] || matrix[8] != (1 << 30)) return 0;
    int positions[] = {0, 1, 3, 4}, values[4];
    for (int i = 0; i < 4; ++i) {
        int32_t value = matrix[positions[i]];
        if (value != 0 && value != 65536 && value != -65536) return 0;
        values[i] = value / 65536;
    }
    *a = values[0]; *b = values[1]; *c = values[2]; *d = values[3];
    return abs(*a) + abs(*c) == 1 && abs(*b) + abs(*d) == 1 && *a * *b + *c * *d == 0;
}
static int sdr_supported(AVFrame *frame, AVStream *stream)
{
    enum AVPacketSideDataType unsupported_coded[] = {
        AV_PKT_DATA_MASTERING_DISPLAY_METADATA, AV_PKT_DATA_CONTENT_LIGHT_LEVEL,
        AV_PKT_DATA_DOVI_CONF, AV_PKT_DATA_DYNAMIC_HDR10_PLUS, AV_PKT_DATA_ICC_PROFILE
    };
    for (size_t i = 0; i < sizeof(unsupported_coded) / sizeof(unsupported_coded[0]); ++i)
        if (av_packet_side_data_get(stream->codecpar->coded_side_data,
                stream->codecpar->nb_coded_side_data, unsupported_coded[i])) return 0;
    if (frame->color_trc == AVCOL_TRC_UNSPECIFIED) frame->color_trc = stream->codecpar->color_trc;
    if (frame->color_primaries == AVCOL_PRI_UNSPECIFIED) frame->color_primaries = stream->codecpar->color_primaries;
    if (frame->colorspace == AVCOL_SPC_UNSPECIFIED) frame->colorspace = stream->codecpar->color_space;
    if (frame->color_range == AVCOL_RANGE_UNSPECIFIED) frame->color_range = stream->codecpar->color_range;
    if (frame->color_trc == AVCOL_TRC_SMPTE2084 || frame->color_trc == AVCOL_TRC_ARIB_STD_B67 ||
        frame->color_trc == AVCOL_TRC_BT2020_10 || frame->color_trc == AVCOL_TRC_BT2020_12 ||
        frame->color_primaries == AVCOL_PRI_BT2020) return 0;
    enum AVFrameSideDataType unsupported[] = {
        AV_FRAME_DATA_MASTERING_DISPLAY_METADATA, AV_FRAME_DATA_CONTENT_LIGHT_LEVEL,
        AV_FRAME_DATA_DYNAMIC_HDR_PLUS, AV_FRAME_DATA_DYNAMIC_HDR_VIVID,
        AV_FRAME_DATA_DOVI_RPU_BUFFER, AV_FRAME_DATA_DOVI_METADATA, AV_FRAME_DATA_ICC_PROFILE
    };
    for (size_t i = 0; i < sizeof(unsupported) / sizeof(unsupported[0]); ++i)
        if (av_frame_get_side_data(frame, unsupported[i])) return 0;
    switch (frame->color_trc) {
        case AVCOL_TRC_UNSPECIFIED: case AVCOL_TRC_BT709: case AVCOL_TRC_GAMMA22:
        case AVCOL_TRC_GAMMA28: case AVCOL_TRC_SMPTE170M: case AVCOL_TRC_SMPTE240M:
        case AVCOL_TRC_IEC61966_2_1: return 1;
        default: return 0;
    }
}
static const char *render_frame(AVFrame *frame, AVStream *stream, int max_w, int max_h,
                               uint8_t **rgba, int *width, int *height)
{
    if (!sdr_supported(frame, stream)) return "unsupported_color";
    if (frame->width <= 0 || frame->height <= 0 || (int64_t)frame->width * frame->height > MAX_PIXELS)
        return "resource_limit";
    const AVPixFmtDescriptor *descriptor = av_pix_fmt_desc_get(frame->format);
    if (!descriptor || (descriptor->flags & AV_PIX_FMT_FLAG_HWACCEL)) return "unsupported_format";
    int a, b, c, d;
    if (!orientation_for(frame, stream, &a, &b, &c, &d)) return "unsupported_transform";
    AVRational sar = frame->sample_aspect_ratio;
    if (sar.num == 0 && sar.den > 0) sar = stream->sample_aspect_ratio;
    if (sar.num == 0 && sar.den > 0) sar = (AVRational){1, 1};
    if (sar.num <= 0 || sar.den <= 0) return "unsupported_aspect";
    double display_w = frame->width * av_q2d(sar), display_h = frame->height;
    if (!isfinite(display_w) || display_w <= 0 || display_w / display_h < 0.01 || display_w / display_h > 100)
        return "unsupported_aspect";
    if (b || c) { double swap = display_w; display_w = display_h; display_h = swap; }
    double fit = fmin(max_w / display_w, max_h / display_h);
    *width = (int)fmax(1, floor(display_w * fit + 0.000001));
    *height = (int)fmax(1, floor(display_h * fit + 0.000001));
    int source_w = b || c ? *height : *width;
    int source_h = b || c ? *width : *height;
    size_t bytes = (size_t)*width * *height * 4;
    uint8_t *scaled = av_malloc(bytes);
    *rgba = av_malloc(bytes);
    struct SwsContext *scale = sws_getContext(frame->width, frame->height, frame->format,
        source_w, source_h, AV_PIX_FMT_RGBA, SWS_BILINEAR, NULL, NULL, NULL);
    if (!scaled || !*rgba || !scale) { av_free(scaled); sws_freeContext(scale); return "resource_limit"; }
    int matrix = SWS_CS_DEFAULT;
    switch (frame->colorspace) {
        case AVCOL_SPC_BT709: matrix = SWS_CS_ITU709; break;
        case AVCOL_SPC_FCC: matrix = SWS_CS_FCC; break;
        case AVCOL_SPC_BT470BG: case AVCOL_SPC_SMPTE170M: matrix = SWS_CS_ITU601; break;
        case AVCOL_SPC_SMPTE240M: matrix = SWS_CS_SMPTE240M; break;
        case AVCOL_SPC_UNSPECIFIED: matrix = frame->height >= 720 ? SWS_CS_ITU709 : SWS_CS_ITU601; break;
        case AVCOL_SPC_RGB: if (!(descriptor->flags & AV_PIX_FMT_FLAG_RGB)) matrix = -1; break;
        default: matrix = -1; break;
    }
    if (matrix < 0) { av_free(scaled); sws_freeContext(scale); return "unsupported_color"; }
    int legacy_full_range = frame->format == AV_PIX_FMT_YUVJ420P || frame->format == AV_PIX_FMT_YUVJ422P ||
        frame->format == AV_PIX_FMT_YUVJ444P || frame->format == AV_PIX_FMT_YUVJ440P || frame->format == AV_PIX_FMT_YUVJ411P;
    int full = frame->color_range == AVCOL_RANGE_JPEG || (descriptor->flags & AV_PIX_FMT_FLAG_RGB) ||
        (frame->color_range == AVCOL_RANGE_UNSPECIFIED && legacy_full_range);
    const int *coefficients = sws_getCoefficients(matrix);
    if (sws_setColorspaceDetails(scale, coefficients, full, coefficients, 1, 0, 1 << 16, 1 << 16) < 0) {
        av_free(scaled); sws_freeContext(scale); return "unsupported_color";
    }
    uint8_t *output[] = {scaled, NULL, NULL, NULL};
    int strides[] = {source_w * 4, 0, 0, 0};
    int rows = sws_scale(scale, (const uint8_t *const *)frame->data, frame->linesize,
                         0, frame->height, output, strides);
    sws_freeContext(scale);
    if (rows != source_h) { av_free(scaled); return "scale_failed"; }
    int offset_x = (a < 0 ? source_w - 1 : 0) + (c < 0 ? source_h - 1 : 0);
    int offset_y = (b < 0 ? source_w - 1 : 0) + (d < 0 ? source_h - 1 : 0);
    for (int y = 0; y < source_h; ++y) for (int x = 0; x < source_w; ++x) {
        int dst_x = a * x + c * y + offset_x, dst_y = b * x + d * y + offset_y;
        memcpy(*rgba + ((size_t)dst_y * *width + dst_x) * 4, scaled + ((size_t)y * source_w + x) * 4, 4);
    }
    av_free(scaled);
    return NULL;
}

/* Isolated identity acquisition: potentially blocking NAS reads stay outside
 * VLC. A failed or timed-out full hash never qualifies persistent cache reuse. */
static int fingerprint_main(int argc, char **argv)
{
    const char *mode = NULL, *path = NULL, *error = NULL;
    Guard guard = {.fd = -1, .worker = 1, .deadline = INT64_MAX, .cpu_deadline = INT64_MAX};
    pthread_t monitor;
    int started = 0;
    struct stat before, after, path_state;
    struct AVSHA *sha = NULL;
    uint8_t *buffer = NULL, digest[32];
    char hex[65];
    if (argc != 5 || strcmp(argv[1], "--fingerprint") || strcmp(argv[3], "--input") ||
        (strcmp(argv[2], "full") && strcmp(argv[2], "sampled") && strcmp(argv[2], "stat")) || argv[4][0] != '/') {
        error = "invalid_arguments"; goto done;
    }
    mode = argv[2]; path = argv[4];
    int metadata_only = !strcmp(mode, "stat");
    begin_operation(&guard);
    if (pthread_create(&monitor, NULL, watchdog, &guard)) { error = "resource_limit"; goto done; }
    started = 1;
    if (metadata_only) {
        /* stat follows the current pathname/symlink target. Metadata-only
         * validation needs no descriptor or SMB open/close round trip. */
        if (stat(path, &before) || !S_ISREG(before.st_mode) || before.st_size <= 0) {
            error = "invalid_input"; goto done;
        }
    } else {
        guard.fd = open(path, O_RDONLY | O_CLOEXEC | O_NONBLOCK);
        if (guard.fd < 0 || fstat(guard.fd, &before) || !S_ISREG(before.st_mode) || before.st_size <= 0 ||
            stat(path, &path_state) || !same_file(&before, &path_state)) { error = "invalid_input"; goto done; }
    }
    guard.size = before.st_size;
    sha = av_sha_alloc(); buffer = av_malloc(65536);
    if (!sha || !buffer || av_sha_init(sha, 256)) { error = "resource_limit"; goto done; }
    int full = !strcmp(mode, "full") || guard.size <= 1048576;
    /* Full hashes are conventional SHA256 over bytes. Sampled hashes are
     * domain-separated, followed by big-endian offset/length and each window. */
    if (!full && strcmp(mode, "stat")) {
        const uint8_t domain[] = "vlc-thumbnail-sampled-v1";
        av_sha_update(sha, domain, sizeof(domain));
    }
    if (metadata_only) {
        char record[256];
        int length = snprintf(record, sizeof(record), "vlc-thumbnail-stat-v1:%" PRIu64 ":%" PRIu64 ":%" PRId64 ":%" PRId64 ":%ld:%" PRId64 ":%ld",
            (uint64_t)before.st_dev, (uint64_t)before.st_ino, (int64_t)before.st_size,
            (int64_t)before.st_mtimespec.tv_sec, before.st_mtimespec.tv_nsec,
            (int64_t)before.st_ctimespec.tv_sec, before.st_ctimespec.tv_nsec);
        if (length < 0 || (size_t)length >= sizeof(record)) { error = "resource_limit"; goto done; }
        /* Metadata digest is only a compact stat record, never content proof. */
        av_sha_update(sha, (const uint8_t *)record, length);
    }
    int windows = metadata_only ? 0 : full ? 1 : 16;
    for (int window = 0; window < windows; ++window) {
        int64_t offset = full ? 0 : ((guard.size - 65536) / 15) * window + ((guard.size - 65536) % 15) * window / 15;
        int64_t remaining = full ? guard.size : 65536;
        if (!full) {
            uint8_t descriptor[16];
            for (int i = 0; i < 8; ++i) {
                descriptor[i] = (uint64_t)offset >> (56 - i * 8);
                descriptor[i + 8] = (uint64_t)remaining >> (56 - i * 8);
            }
            av_sha_update(sha, descriptor, sizeof(descriptor));
        }
        if (seek_local(&guard, offset, SEEK_SET) < 0) { error = "read_failed"; goto done; }
        while (remaining > 0) {
            int chunk = remaining < 65536 ? (int)remaining : 65536;
            int count = read_local(&guard, buffer, chunk);
            if (count <= 0) { error = expired(&guard) ? "timeout" : "read_failed"; goto done; }
            av_sha_update(sha, buffer, count);
            remaining -= count;
        }
    }
    av_sha_final(sha, digest);
    for (int i = 0; i < 32; ++i) snprintf(hex + i * 2, 3, "%02x", digest[i]);
    if (metadata_only) {
        if (stat(path, &after) || !same_file(&before, &after)) error = "media_changed";
    } else if (fstat(guard.fd, &after) || stat(path, &path_state) || !same_file(&before, &after) || !same_file(&before, &path_state))
        error = "media_changed";
    if (expired(&guard)) error = "timeout";
done:
    av_free(sha); av_free(buffer);
    if (guard.fd >= 0) close(guard.fd);
    if (started) { atomic_store(&guard.stop, 1); pthread_join(monitor, NULL); }
    if (error) printf("{\"version\":3,\"type\":\"identity\",\"ok\":false,\"error\":\"%s\",\"payload_bytes\":0}\n", error);
    else printf("{\"version\":3,\"type\":\"identity\",\"ok\":true,\"fingerprint\":\"%s\",\"policy\":\"%s\","
                "\"stat_identity\":\"%" PRIu64 ":%" PRIu64 ":%" PRId64 ":%" PRId64 ":%ld:%" PRId64 ":%ld\","
                "\"bytes_read\":%" PRIu64 ",\"read_calls\":%" PRIu64 ",\"payload_bytes\":0}\n",
                hex, mode, (uint64_t)before.st_dev, (uint64_t)before.st_ino, (int64_t)before.st_size,
                (int64_t)before.st_mtimespec.tv_sec, before.st_mtimespec.tv_nsec,
                (int64_t)before.st_ctimespec.tv_sec, before.st_ctimespec.tv_nsec,
                guard.bytes_read, guard.read_calls);
    return error ? 1 : 0;
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--fingerprint")) return fingerprint_main(argc, argv);
    const char *error = NULL, *path = NULL;
    int64_t requested = -1, ordinal = -1, max_w = -1, max_h = -1, expected_videos = -1;
    int track_number = -1;
    AVFormatContext *fmt = NULL;
    AVIOContext *io = NULL;
    AVCodecContext *codec = NULL;
    AVPacket *packet = NULL;
    AVFrame *frame = NULL, *best = NULL;
    uint8_t *rgba = NULL;
    Guard guard = {.fd = -1, .deadline = INT64_MAX, .cpu_deadline = INT64_MAX};
    int worker = argc > 1 && !strcmp(argv[1], "--worker");
    guard.worker = worker;
    begin_operation(&guard);
    int64_t operation_start = av_gettime_relative();
    int64_t request_id = 0;
    pthread_t monitor;
    int monitor_started = 0, width = 0, height = 0;
    int64_t origin = 0;
    Selection selection = {0};
    struct stat before, after, path_state;
    if ((!worker && argc != 11 && argc != 13) || (worker && argc != 12)) { error = "invalid_arguments"; goto done; }
    for (int i = worker ? 2 : 1; i < argc; i += 2) {
        if (!strcmp(argv[i], "--input") && !path) path = argv[i + 1];
        else if (!worker && !strcmp(argv[i], "--time-us") && requested == -1 && parse_number(argv[i + 1], INT64_MAX, &requested)) {}
        else if (!strcmp(argv[i], "--video-ordinal") && ordinal == -1 && parse_number(argv[i + 1], 127, &ordinal)) {}
        else if (!strcmp(argv[i], "--video-count") && expected_videos == -1 && parse_number(argv[i + 1], 128, &expected_videos) && expected_videos > 0) {}
        else if (!strcmp(argv[i], "--max-width") && max_w == -1 && parse_number(argv[i + 1], 320, &max_w)) {}
        else if (!strcmp(argv[i], "--max-height") && max_h == -1 && parse_number(argv[i + 1], 180, &max_h)) {}
        else { error = "invalid_arguments"; goto done; }
    }
    if (!path || path[0] != '/' || (!worker && requested < 0) || (worker && expected_videos < 1) || ordinal < 0 || max_w < 1 || max_h < 1) {
        error = "invalid_arguments"; goto done;
    }
    av_log_set_level(AV_LOG_QUIET); /* Untrusted metadata/paths never reach stdout or stderr. */
    av_max_alloc(ALLOC_LIMIT);
    struct rlimit cpu_limit = {5, 5};
    if (!worker && setrlimit(RLIMIT_CPU, &cpu_limit)) {
        error = "resource_limit"; goto done;
    }
    if (pthread_create(&monitor, NULL, watchdog, &guard)) { error = "resource_limit"; goto done; }
    monitor_started = 1;
    guard.fd = open(path, O_RDONLY | O_CLOEXEC | O_NONBLOCK);
    if (guard.fd < 0 || fstat(guard.fd, &before) || !S_ISREG(before.st_mode) || before.st_size <= 0 ||
        stat(path, &path_state) || !same_file(&before, &path_state)) { error = "invalid_input"; goto done; }
    guard.size = before.st_size;
    fmt = avformat_alloc_context();
    uint8_t *io_buffer = av_malloc(32768);
    if (!fmt || !io_buffer) { av_free(io_buffer); error = "resource_limit"; goto done; }
    io = avio_alloc_context(io_buffer, 32768, 0, &guard, read_local, NULL, seek_local);
    if (!io) { av_free(io_buffer); error = "resource_limit"; goto done; }
    fmt->pb = io;
    fmt->flags |= AVFMT_FLAG_CUSTOM_IO;
    fmt->interrupt_callback = (AVIOInterruptCB){interrupt_io, &guard};
    fmt->io_open = deny_secondary_io;
    fmt->max_streams = 128;
    fmt->probesize = 4 * 1024 * 1024;
    fmt->max_analyze_duration = 2 * AV_TIME_BASE;
    AVDictionary *options = NULL;
    av_dict_set(&options, "protocol_whitelist", "", 0);
    av_dict_set(&options, "format_whitelist", "mov,matroska,webm,avi,mpegts,mpeg,ogg,flv,asf,rm,nut", 0);
    av_dict_set(&options, "enable_drefs", "0", 0);
    av_dict_set(&options, "use_absolute_path", "0", 0);
    int opened = avformat_open_input(&fmt, NULL, NULL, &options);
    av_dict_free(&options);
    if (opened < 0 || avformat_find_stream_info(fmt, NULL) < 0) { error = "unsupported_input"; goto done; }
    /* VLC's video menu is program-local, while this helper's ordinal is file-
     * global. Never guess which program a local ordinal belongs to. */
    if (fmt->nb_programs > 1) { error = "ambiguous_track_mapping"; goto done; }
    if (fmt->nb_streams > 128) { error = "unsupported_input"; goto done; }
    int videos[128], video_count = 0;
    for (unsigned i = 0; i < fmt->nb_streams; ++i) {
        AVStream *s = fmt->streams[i];
        if (s->codecpar->codec_type == AVMEDIA_TYPE_VIDEO && !(s->disposition & AV_DISPOSITION_ATTACHED_PIC))
            videos[video_count++] = (int)i;
    }
    /* Native menus may omit streams this demuxer recognizes in any container.
     * A supplied count mismatch makes ordinal correspondence ambiguous. Keep
     * the legacy count-less v2 single-stream route, but never guess when the
     * native caller has provided contrary evidence. */
    if (expected_videos > 0 && expected_videos != video_count) {
        error = "ambiguous_track_mapping"; goto done;
    }
    int matroska = strstr(fmt->iformat->name, "matroska") || strstr(fmt->iformat->name, "webm");
    if (matroska && video_count > 1) {
        // The helper-private libavformat exposes TrackNumber in AVStream.id.
        // VLC adds supported AVC videos in that sorted order. Require equal
        // native count, supported codecs and unique positive identities first.
        if (expected_videos != video_count) { error = "ambiguous_track_mapping"; goto done; }
        for (int i = 0; i < video_count; ++i) {
            AVStream *s = fmt->streams[videos[i]];
            if (s->id <= 0 || s->codecpar->codec_id != AV_CODEC_ID_H264) { error = "ambiguous_track_mapping"; goto done; }
            for (int j = 0; j < i; ++j)
                if (s->id == fmt->streams[videos[j]]->id) { error = "ambiguous_track_mapping"; goto done; }
        }
        for (int i = 1; i < video_count; ++i) {
            int item = videos[i], j = i;
            while (j && fmt->streams[videos[j-1]]->id > fmt->streams[item]->id) {
                videos[j] = videos[j-1]; --j;
            }
            videos[j] = item;
        }
    }
    if (fmt->duration == AV_NOPTS_VALUE || fmt->duration <= 0) { error = "unknown_duration"; goto done; }
    if (!origin_for(fmt, &origin)) { error = "ambiguous_origin"; goto done; }
    int selected = ordinal < video_count ? videos[ordinal] : -1;
    if (selected < 0) { error = "track_unavailable"; goto done; }
    AVStream *stream = fmt->streams[selected];
    if (matroska) track_number = stream->id;
    if (stream->time_base.num <= 0 || stream->time_base.den <= 0 ||
        (origin > 0 && requested > INT64_MAX - origin)) { error = "unknown_timing"; goto done; }
    const AVCodec *decoder = avcodec_find_decoder(stream->codecpar->codec_id);
    if (!decoder) { error = "unsupported_codec"; goto done; }
    codec = avcodec_alloc_context3(decoder);
    if (!codec || avcodec_parameters_to_context(codec, stream->codecpar) < 0) { error = "resource_limit"; goto done; }
    if (!(decoder->capabilities & AV_CODEC_CAP_DR1)) { error = "unsupported_codec"; goto done; }
    codec->opaque = &guard;
    codec->get_buffer2 = bounded_get_buffer;
    codec->thread_count = 1;
    codec->thread_type = 0;
    codec->skip_frame = AVDISCARD_NONKEY;
    codec->max_pixels = MAX_PIXELS;
    codec->pkt_timebase = stream->time_base;
    codec->err_recognition = AV_EF_CAREFUL | AV_EF_EXPLODE;
    if (avcodec_open2(codec, decoder, NULL) < 0) { error = "unsupported_codec"; goto done; }
    packet = av_packet_alloc(); frame = av_frame_alloc(); best = av_frame_alloc();
    if (!packet || !frame || !best) { error = "resource_limit"; goto done; }
    if (worker) {
        if (fstat(guard.fd, &after) || stat(path, &path_state) || !same_file(&before, &after) || !same_file(&before, &path_state)) {
            error = "media_changed"; goto done;
        }
        idle_operation(&guard);
        printf("{\"version\":3,\"type\":\"ready\",\"ok\":true,\"duration_us\":%" PRId64
               ",\"bytes_read\":%" PRIu64 ",\"read_calls\":%" PRIu64 ",\"seek_calls\":%" PRIu64
               ",\"open_count\":1,\"operation_us\":%" PRId64 "}\n",
               fmt->duration, guard.bytes_read, guard.read_calls, guard.seek_calls, av_gettime_relative() - operation_start);
        if (fflush(stdout)) _exit(1);
    }
    for (;;) {
        uint64_t initial_bytes = guard.bytes_read, initial_reads = guard.read_calls, initial_seeks = guard.seek_calls;
        if (worker) {
            char line[98], id_text[97], time_text[97];
            if (!fgets(line, sizeof(line), stdin)) break;
            /* One bounded decimal pair, exactly one separating space and newline. */
            size_t length = strlen(line);
            char *space = strchr(line, ' ');
            if (!length || length > 96 || line[length - 1] != '\n' || !space || strchr(space + 1, ' ')) {
                error = "invalid_request"; goto done;
            }
            *space = '\0'; line[length - 1] = '\0';
            snprintf(id_text, sizeof(id_text), "%s", line);
            snprintf(time_text, sizeof(time_text), "%s", space + 1);
            if (!parse_number(id_text, INT64_MAX, &request_id) || !parse_number(time_text, INT64_MAX, &requested)) {
                error = "invalid_request"; goto done;
            }
            begin_operation(&guard);
            operation_start = av_gettime_relative();
        }
        error = NULL; width = height = 0;
        av_freep(&rgba); av_packet_unref(packet); av_frame_unref(frame); av_frame_unref(best);
        if (fstat(guard.fd, &after) || stat(path, &path_state) || !same_file(&before, &after) || !same_file(&before, &path_state)) {
            error = "media_changed"; goto request_done;
        }
        if (origin > 0 && requested > INT64_MAX - origin) { error = "unknown_timing"; goto request_done; }
        int64_t target = av_rescale_q(requested + origin, AV_TIME_BASE_Q, stream->time_base);
        if (target == INT64_MIN || target == INT64_MAX || av_seek_frame(fmt, selected, target, AVSEEK_FLAG_BACKWARD) < 0) {
            error = "seek_failed"; goto request_done;
        }
        avcodec_flush_buffers(codec);
        selection = (Selection){.frame = frame, .best = best, .stream = stream, .origin = origin,
            .requested = requested, .last_pts = AV_NOPTS_VALUE};
        error = decode_keyframe(fmt, codec, selected, &selection, packet);
        if (error) goto request_done;
        if (selection.actual > fmt->duration) { error = "unknown_timing"; goto request_done; }
        error = render_frame(best, stream, (int)max_w, (int)max_h, &rgba, &width, &height);
        if (error) goto request_done;
        if (fstat(guard.fd, &after) || stat(path, &path_state) || !same_file(&before, &after) || !same_file(&before, &path_state))
            error = "media_changed";
        if (expired(&guard)) error = "timeout";
request_done:
        if (worker && (fstat(guard.fd, &after) || stat(path, &path_state) ||
            !same_file(&before, &after) || !same_file(&before, &path_state))) error = "media_changed";
        if (expired(&guard)) error = "timeout";
        if (!worker) break;
        int64_t operation_us = av_gettime_relative() - operation_start;
        /* Watchdog never writes in worker mode. Idle the operation before a
         * response; caller bounds IPC writes/reads and can kill a stuck helper. */
        idle_operation(&guard);
        if (error) {
            printf("{\"version\":3,\"id\":%" PRId64 ",\"requested_us\":%" PRId64
                   ",\"ok\":false,\"error\":\"%s\",\"payload_bytes\":0", request_id, requested, error);
        } else {
            printf("{\"version\":3,\"id\":%" PRId64 ",\"ok\":true,\"sampling\":\"keyframe\",\"requested_us\":%" PRId64 ",\"actual_us\":%" PRId64
                   ",\"width\":%d,\"height\":%d,\"channels\":4,\"payload_bytes\":%zu,\"video_ordinal\":%" PRId64
                   ",\"decoded_frames\":%d,\"timeline_origin_us\":%" PRId64 ",\"video_track_number\":%d",
                   request_id, requested, selection.actual, width, height, (size_t)width * height * 4,
                   ordinal, selection.decoded, origin, track_number);
        }
        printf(",\"bytes_read\":%" PRIu64 ",\"read_calls\":%" PRIu64 ",\"seek_calls\":%" PRIu64
               ",\"request_bytes_read\":%" PRIu64 ",\"request_read_calls\":%" PRIu64 ",\"request_seek_calls\":%" PRIu64
               ",\"open_count\":1,\"operation_us\":%" PRId64 "}\n",
               guard.bytes_read, guard.read_calls, guard.seek_calls, guard.bytes_read - initial_bytes,
               guard.read_calls - initial_reads, guard.seek_calls - initial_seeks, operation_us);
        if ((!error && fwrite(rgba, 1, (size_t)width * height * 4, stdout) != (size_t)width * height * 4) || fflush(stdout)) {
            _exit(1); /* A partial raw payload must not be followed by JSON. */
        }
        if (error && (!strcmp(error, "media_changed") || !strcmp(error, "timeout") || !strcmp(error, "resource_limit"))) {
            error = NULL; break;
        }
        error = NULL;
    }

done:
    /* Worker EOF/retirement can arrive from idle state. Teardown is active work,
     * including potentially blocking descriptor close, with its own watchdog.
     * Preserve the v2 whole-request deadline rather than extending it here. */
    if (worker && monitor_started) begin_operation(&guard);
    /* Stop the monitor before final output; worker hard limits emit no bytes. */
    av_packet_free(&packet); av_frame_free(&frame); av_frame_free(&best);
    avcodec_free_context(&codec); avformat_close_input(&fmt);
    if (io) { av_freep(&io->buffer); avio_context_free(&io); }
    if (guard.fd >= 0) close(guard.fd);
    if (monitor_started) {
        if (expired(&guard)) error = "timeout";
        atomic_store(&guard.stop, 1); pthread_join(monitor, NULL);
    }
    int status = 1;
    if (worker) {
        if (error) printf("{\"version\":3,\"id\":%" PRId64 ",\"ok\":false,\"error\":\"%s\",\"payload_bytes\":0}\n", request_id, error);
        else status = 0;
        fflush(stdout);
        av_free(rgba);
        return status;
    }
    if (error) printf("{\"version\":2,\"ok\":false,\"error\":\"%s\"}\n", error);
    else {
        size_t bytes = (size_t)width * height * 4;
        int written = printf("{\"version\":2,\"ok\":true,\"sampling\":\"keyframe\",\"requested_us\":%" PRId64 ",\"actual_us\":%" PRId64
            ",\"width\":%d,\"height\":%d,\"channels\":4,\"payload_bytes\":%zu,\"video_ordinal\":%" PRId64
            ",\"decoded_frames\":%d,\"timeline_origin_us\":%" PRId64 ",\"video_track_number\":%d}\n",
            requested, selection.actual, width, height, bytes, ordinal, selection.decoded, origin, track_number);
        if (written > 0 && fwrite(rgba, 1, bytes, stdout) == bytes && fflush(stdout) == 0) status = 0;
    }
    av_free(rgba);
    return status;
}
