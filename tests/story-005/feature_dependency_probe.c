/* SPDX-License-Identifier: LGPL-2.1-or-later */
/* Direct identity/selector/packet observation: no ffprobe display assumptions. */
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <libavformat/avformat.h>
#include <libavutil/md5.h>
#include <libavutil/avutil.h>

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    AVFormatContext *fmt = NULL;
    int ret = avformat_open_input(&fmt, argv[1], NULL, NULL);
    if (ret < 0) { printf("{\"open_error\":%d}\n", ret); return 3; }
    ret = avformat_find_stream_info(fmt, NULL);
    if (ret < 0) { printf("{\"info_error\":%d}\n", ret); avformat_close_input(&fmt); return 4; }
    printf("{\"avformat_version\":%u,\"streams\":%u,\"groups\":%u}\n",
           avformat_version(), fmt->nb_streams, fmt->nb_stream_groups);
    const char *selectors[] = {"#0", "#7", "i:7", "#31", "i:31", "#47", "#63", "#2147483647"};
    for (unsigned i = 0; i < fmt->nb_streams; ++i) {
        AVStream *s = fmt->streams[i];
        printf("{\"stream\":%u,\"id\":%d,\"type\":%d,\"codec\":%d,\"disposition\":%d,\"selectors\":[",
               i, s->id, s->codecpar->codec_type, s->codecpar->codec_id, s->disposition);
        for (unsigned j = 0; j < sizeof(selectors)/sizeof(selectors[0]); ++j)
            printf("%s%d", j ? "," : "", avformat_match_stream_specifier(fmt, s, selectors[j]));
        printf("]}\n");
    }
    for (unsigned i = 0; i < fmt->nb_stream_groups; ++i)
        printf("{\"group\":%u,\"id\":%"PRIu64",\"type\":%d}\n", i, fmt->stream_groups[i]->id, fmt->stream_groups[i]->type);
    AVPacket *packet = av_packet_alloc();
    if (!packet) { avformat_close_input(&fmt); return 5; }
    unsigned count = 0;
    while ((ret = av_read_frame(fmt, packet)) >= 0 && count < 1000) {
        uint8_t digest[16];
        av_md5_sum(digest, packet->data, packet->size);
        printf("{\"packet\":%u,\"stream\":%d,\"pts\":%"PRId64",\"dts\":%"PRId64",\"duration\":%"PRId64",\"flags\":%d,\"md5\":\"",
               count++, packet->stream_index, packet->pts, packet->dts, packet->duration, packet->flags);
        for (unsigned i = 0; i < 16; ++i) printf("%02x", digest[i]);
        printf("\"}\n");
        av_packet_unref(packet);
    }
    av_packet_free(&packet);
    avformat_close_input(&fmt);
    return ret == AVERROR_EOF ? 0 : 6;
}
