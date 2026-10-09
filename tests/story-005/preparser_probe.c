/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Bounded experiment using VLC's unmodified internal preparser API.
 * API/ownership pattern follows VLC test/src/preparser/thumbnail.c.
 * This is a diagnostic caller, not a product implementation or acceptance test.
 */
#ifdef HAVE_CONFIG_H
# include "config.h"
#endif
#include <vlc_common.h>
#include <vlc/vlc.h>
#include <vlc/libvlc_media_track.h>
#include "lib/libvlc_internal.h"
#include <vlc_preparser.h>
#include <vlc_input_item.h>
#include <vlc_picture.h>
#include <vlc_block.h>
#include <vlc_url.h>
#include <signal.h>
#include <unistd.h>
#include <math.h>

struct result {
    vlc_mutex_t lock;
    vlc_cond_t cond;
    bool done;
    int status;
    picture_t *picture;
    vlc_tick_t completed;
};

static void hard_timeout(int sig)
{
    (void)sig;
    static const char message[] = "{\"probe_error\":\"overall_timeout\"}\n";
    (void)write(STDOUT_FILENO, message, sizeof(message) - 1);
    _exit(124);
}

static void ended(vlc_preparser_req *req, int status, picture_t *picture,
                  void *opaque)
{
    (void)req;
    struct result *result = opaque;
    vlc_mutex_lock(&result->lock);
    result->status = status;
    result->picture = picture ? picture_Hold(picture) : NULL;
    result->completed = vlc_tick_now();
    result->done = true;
    vlc_cond_signal(&result->cond);
    vlc_mutex_unlock(&result->lock);
}

static void json_string(const char *text)
{
    putchar('"');
    for (const unsigned char *p = (const unsigned char *)(text ? text : ""); *p; p++) {
        if (*p == '"' || *p == '\\') printf("\\%c", *p);
        else if (*p < 0x20) printf("\\u%04x", *p);
        else putchar(*p);
    }
    putchar('"');
}

static int enumerate_tracks(const char *media)
{
    /* Diagnostic playback uses dummy output, never the native interface.
     * Five seconds is an observation window, not exhaustive track discovery. */
    signal(SIGALRM, hard_timeout);
    alarm(30);
    const char *options[] = { "--ignore-config", "--no-audio", "--no-spu",
                              "--vout=dummy", "--verbose=2" };
    libvlc_instance_t *instance = libvlc_new(ARRAY_SIZE(options), options);
    if (!instance) return 3;
    libvlc_media_t *item = strstr(media, "://")
                        ? libvlc_media_new_location(media) : libvlc_media_new_path(media);
    libvlc_media_player_t *player = libvlc_media_player_new(instance, NULL, NULL);
    if (!item || !player) {
        if (item) libvlc_media_release(item);
        if (player) libvlc_media_player_release(player);
        libvlc_release(instance);
        return 3;
    }
    libvlc_media_player_set_media(player, item);
    int started = libvlc_media_player_play(player);
    if (started == 0) vlc_tick_wait(vlc_tick_now() + VLC_TICK_FROM_SEC(5));
    libvlc_media_tracklist_t *tracks = libvlc_media_player_get_tracklist(
                                       player, libvlc_track_video, false);
    size_t count = tracks ? libvlc_media_tracklist_count(tracks) : 0;
    printf("{\"mode\":\"enumerate\",\"play_status\":%d,\"observation_seconds\":5,"
           "\"video_track_count\":%zu,\"tracks\":[", started, count);
    for (size_t i = 0; i < count; i++) {
        libvlc_media_track_t *track = libvlc_media_tracklist_at(tracks, i);
        printf("%s{\"id\":", i ? "," : "");
        json_string(track->psz_id);
        printf(",\"id_stable\":%s,\"selected\":%s,\"codec\":%u}",
               track->id_stable ? "true" : "false", track->selected ? "true" : "false",
               track->i_codec);
    }
    printf("]}\n");
    fflush(stdout);
    if (tracks) libvlc_media_tracklist_delete(tracks);
    libvlc_media_player_stop_async(player);
    libvlc_media_player_release(player);
    libvlc_media_release(item);
    libvlc_release(instance);
    alarm(0);
    return started == 0 && count > 0 ? 0 : 6;
}

static int save_rgba(vlc_object_t *object, picture_t *picture,
                     const char *prefix, unsigned index)
{
    video_format_t display = picture->format;
    video_format_TransformTo(&display, ORIENT_NORMAL);
    double width = display.i_visible_width;
    double height = display.i_visible_height;
    if (display.i_sar_den > 0 && display.i_sar_num > 0)
        width *= (double)display.i_sar_num / display.i_sar_den;
    if (width <= 0 || height <= 0 || !isfinite(width)) {
        printf("\"export_status\":%d,\"export_saved\":false", VLC_EGENERIC);
        return VLC_EGENERIC;
    }
    double scale = fmin(320.0 / width, 180.0 / height);
    int output_width = (int)fmax(1, floor(width * scale));
    int output_height = (int)fmax(1, floor(height * scale));
    const char *geometry = getenv("VLC_PROBE_EXPORT_GEOMETRY");
    if (!geometry) geometry = "display-fit";
    if (strcmp(geometry, "naive") == 0) {
        output_width = 320;
        output_height = 180;
    } else if (strcmp(geometry, "auto-height") == 0) {
        output_width = 0;
        output_height = 180;
    } else if (strcmp(geometry, "display-fit") != 0) {
        printf("\"export_status\":%d,\"export_saved\":false", VLC_EGENERIC);
        return VLC_EGENERIC;
    }
    printf("\"export_geometry\":\"%s\",\"export_requested_width\":%d,"
           "\"export_requested_height\":%d,", geometry, output_width, output_height);
    block_t *block = NULL;
    video_format_t exported;
    int status = picture_Export(object, &block, &exported, picture,
                                VLC_CODEC_RGBA, output_width, output_height, false);
    if (status != VLC_SUCCESS || block == NULL) {
        printf("\"export_status\":%d,\"export_saved\":false", status);
        return status == VLC_SUCCESS ? VLC_EGENERIC : status;
    }
    bool bounded = exported.i_width <= 320 && exported.i_height <= 180
                   && block->i_buffer <= 320 * 180 * 4;
    char *path = NULL;
    FILE *file = NULL;
    if (bounded && asprintf(&path, "%s-%03u.rgba", prefix, index) >= 0)
        file = fopen(path, "wb");
    bool saved = file && fwrite(block->p_buffer, 1, block->i_buffer, file)
                         == block->i_buffer;
    if (file && fclose(file) != 0)
        saved = false;
    printf("\"export_status\":%d,\"export_saved\":%s,"
           "\"export_width\":%u,\"export_height\":%u,\"export_bytes\":%zu,"
           "\"export_orientation\":%d,\"export_sar_num\":%u,\"export_sar_den\":%u",
           status, saved ? "true" : "false", exported.i_width,
           exported.i_height, block->i_buffer, exported.orientation,
           exported.i_sar_num, exported.i_sar_den);
    free(path);
    block_Release(block);
    video_format_Clean(&exported);
    return saved ? VLC_SUCCESS : VLC_EGENERIC;
}

int main(int argc, char **argv)
{
    if (argc == 3 && strcmp(argv[1], "enumerate") == 0)
        return enumerate_tracks(argv[2]);
    if (argc < 7 || argc > 8 ||
        (strcmp(argv[1], "internal") != 0 && strcmp(argv[1], "external") != 0)) {
        fprintf(stderr, "Usage:\n  %s enumerate MEDIA\n  %s internal|external MEDIA OUTPUT_PREFIX TARGET_US REPEATS fast|precise [VLC_ES_STRING_ID]\n", argv[0], argv[0]);
        return 2;
    }
    bool external = strcmp(argv[1], "external") == 0;
    argc--; argv++;
    if (argc == 7 && (argv[6][0] == '\0' || strchr(argv[6], ','))) {
        fprintf(stderr, "Explicit track ID must be one nonempty canonical ES string ID; commas are rejected.\n");
        return 2;
    }
    char *end;
    int64_t target = strtoll(argv[3], &end, 10);
    if (*end || target < 0 || target > INT64_MAX / 2)
        return 2;
    unsigned long repeats = strtoul(argv[4], &end, 10);
    if (*end || repeats == 0 || repeats > 20)
        return 2;
    bool fast = strcmp(argv[5], "fast") == 0;
    if (!fast && strcmp(argv[5], "precise") != 0)
        return 2;
    /* Covers init, cancellation and teardown as well as request waiting.
     * Emergency exit reports invalid acquisition; it is never a success. */
    signal(SIGALRM, hard_timeout);
    alarm((unsigned)(repeats * 20 + 30));
    const char *options[] = { "--ignore-config", "--no-audio", "--no-spu", "--verbose=2" };
    libvlc_instance_t *instance = libvlc_new(ARRAY_SIZE(options), options);
    if (!instance)
        return 3;
    const struct vlc_preparser_cfg cfg = {
        .types = VLC_PREPARSER_TYPE_THUMBNAIL,
        .timeout = VLC_TICK_FROM_SEC(15),
        .external_process = external,
    };
    vlc_object_t *object = VLC_OBJECT(instance->p_libvlc_int);
    vlc_preparser_t *preparser = vlc_preparser_New(object, &cfg);
    char *uri = strstr(argv[1], "://") ? strdup(argv[1]) : vlc_path2uri(argv[1], NULL);
    input_item_t *item = uri ? input_item_New(uri, "synthetic preparser probe") : NULL;
    free(uri);
    if (!preparser || !item) {
        if (item) input_item_Release(item);
        if (preparser) vlc_preparser_Delete(preparser);
        libvlc_release(instance);
        return 3;
    }
    if (argc == 7) {
        char *option = NULL;
        if (asprintf(&option, "video-track-id=%s", argv[6]) < 0) {
            input_item_Release(item);
            vlc_preparser_Delete(preparser);
            libvlc_release(instance);
            return 3;
        }
        input_item_AddOption(item, option, VLC_INPUT_OPTION_TRUSTED);
        input_item_AddOption(item, "video-track=-1", VLC_INPUT_OPTION_TRUSTED);
        free(option);
    }
    int exit_status = 0;
    for (unsigned index = 0; index < repeats; index++) {
        struct result result = {0};
        vlc_mutex_init(&result.lock);
        vlc_cond_init(&result.cond);
        struct vlc_thumbnailer_arg argument = {
            .seek = { .type = VLC_THUMBNAILER_SEEK_TIME,
                      .time = target,
                      .speed = fast ? VLC_THUMBNAILER_SEEK_FAST : VLC_THUMBNAILER_SEEK_PRECISE },
            .hw_dec = false,
        };
        static const struct vlc_thumbnailer_cbs callbacks = { .on_ended = ended };
        vlc_preparser_req *request = vlc_preparser_req_NewThumbnail(preparser, item,
                                      &argument, &callbacks, &result);
        vlc_tick_t started = vlc_tick_now();
        if (!request || vlc_preparser_Submit(preparser, request) != VLC_SUCCESS) {
            if (request) vlc_preparser_req_Release(request);
            exit_status = 4;
            break;
        }
        vlc_mutex_lock(&result.lock);
        while (!result.done && vlc_cond_timedwait(&result.cond, &result.lock,
                                          started + VLC_TICK_FROM_SEC(17)) == 0) {}
        bool timed_out = !result.done;
        vlc_mutex_unlock(&result.lock);
        if (timed_out) {
            /* Cancel may invoke callback synchronously; hold no callback lock. */
            vlc_preparser_Cancel(preparser, request);
            vlc_mutex_lock(&result.lock);
            vlc_tick_t cancel_deadline = vlc_tick_now() + VLC_TICK_FROM_SEC(2);
            while (!result.done && vlc_cond_timedwait(&result.cond, &result.lock,
                                                    cancel_deadline) == 0) {}
            vlc_mutex_unlock(&result.lock);
            if (!result.done) hard_timeout(SIGALRM);
        }
        printf("{\"mode\":\"%s\",\"request_index\":%u,\"requested_us\":%"PRId64","
               "\"fast\":%s,\"explicit_track_id\":%s,\"status\":%d,"
               "\"outer_timeout\":%s,\"elapsed_us\":%"PRId64",\"has_picture\":%s",
               external ? "external" : "internal", index, target,
               fast ? "true" : "false", argc == 7 ? "true" : "false",
               result.status, timed_out ? "true" : "false", result.completed - started,
               result.picture ? "true" : "false");
        if (result.picture) {
            picture_t *picture = result.picture;
            const video_format_t *format = &picture->format;
            printf(",\"picture_date\":%"PRId64",\"date_valid\":%s,"
                   "\"date_minus_tick_zero\":%"PRId64",\"chroma\":%u,"
                   "\"visible_width\":%u,\"visible_height\":%u,"
                   "\"orientation\":%d,\"sar_num\":%u,\"sar_den\":%u,",
                   picture->date, picture->date != VLC_TICK_INVALID ? "true" : "false",
                   picture->date != VLC_TICK_INVALID ? picture->date - VLC_TICK_0 : 0,
                   format->i_chroma,
                   format->i_visible_width, format->i_visible_height,
                   format->orientation, format->i_sar_num, format->i_sar_den);
            if (save_rgba(object, picture, argv[2], index) != VLC_SUCCESS)
                exit_status = 5;
            picture_Release(picture);
        } else exit_status = 6;
        printf("}\n");
        fflush(stdout);
        vlc_preparser_req_Release(request);
    }
    input_item_Release(item);
    vlc_preparser_Delete(preparser);
    libvlc_release(instance);
    alarm(0);
    return exit_status;
}
