/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Bounded diagnostic using VLC's demux API and the callback pattern in
 * test/src/input/demux-run.c. No decoding, playback or clock proof is implied.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <vlc_common.h>
#include <vlc/vlc.h>
#include "lib/libvlc_internal.h"
#include <vlc_demux.h>
#include <vlc_stream.h>
#include <vlc_es_out.h>
#include <vlc_block.h>
#include <vlc_hash.h>
#include <vlc_strings.h>
#include <vlc_url.h>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>

void vlc_object_InitInputConfig(vlc_object_t *, bool, bool);
struct es_out_id_t { struct es_out_id_t *next; unsigned index; int cat; };
struct capture { es_out_t out; es_out_id_t *ids; unsigned next_id, packets; };
static es_out_id_t *add(es_out_t *out, input_source_t *in, const es_format_t *fmt)
{
    (void)in;
    struct capture *c = (struct capture *)out;
    es_out_id_t *id = calloc(1, sizeof(*id));
    if (!id) return NULL;
    id->index = c->next_id++; id->cat = fmt->i_cat;
    id->next = c->ids; c->ids = id;
    printf("{\"event\":\"track\",\"track\":%u,\"cat\":%d,\"codec\":%u}\n",id->index,id->cat,fmt->i_codec);
    return id;
}
static int send_block(es_out_t *out, es_out_id_t *id, block_t *block)
{
    struct capture *c = (struct capture *)out;
    vlc_hash_md5_t hash; char hex[33];
    vlc_hash_md5_Init(&hash); vlc_hash_md5_Update(&hash,block->p_buffer,block->i_buffer);
    vlc_hash_FinishHex(&hash,hex);
    printf("{\"event\":\"packet\",\"ordinal\":%u,\"track\":%u,\"cat\":%d,\"dts\":%"PRId64",\"pts\":%"PRId64",\"duration\":%"PRId64",\"flags\":%u,\"bytes\":%zu,\"md5\":\"%s\"}\n",c->packets++,id->index,id->cat,block->i_dts,block->i_pts,block->i_length,block->i_flags,block->i_buffer,hex);
    block_Release(block); return VLC_SUCCESS;
}
static void del(es_out_t *out, es_out_id_t *id)
{
    struct capture *c=(struct capture *)out;
    es_out_id_t **slot=&c->ids;
    while (*slot && *slot!=id) slot=&(*slot)->next;
    if (!*slot) abort();
    *slot=id->next; free(id);
}
static int control(es_out_t *out,input_source_t *in,int query,va_list ap)
{
    (void)out; (void)in;
    switch(query) {
    case ES_OUT_GET_ES_STATE: (void)va_arg(ap,es_out_id_t *); *va_arg(ap,bool *)=true; break;
    case ES_OUT_IS_EMPTY: *va_arg(ap,bool *)=true; break;
    case ES_OUT_SET_GROUP_PCR: (void)va_arg(ap,int); /* fall through */
    case ES_OUT_SET_PCR:
        printf("{\"event\":\"pcr\",\"value\":%"PRId64"}\n",va_arg(ap,vlc_tick_t)); break;
    case ES_OUT_SET_NEXT_DISPLAY_TIME:
        printf("{\"event\":\"display_target\",\"value\":%"PRId64"}\n",va_arg(ap,vlc_tick_t)); break;
    case ES_OUT_RESET_PCR: puts("{\"event\":\"pcr_reset\"}"); break;
    case ES_OUT_SET_ES: case ES_OUT_SET_ES_DEFAULT: case ES_OUT_SET_ES_STATE:
    case ES_OUT_SET_ES_CAT_POLICY: case ES_OUT_SET_GROUP: case ES_OUT_SET_ES_FMT:
    case ES_OUT_SET_GROUP_META: case ES_OUT_SET_GROUP_EPG: case ES_OUT_DEL_GROUP:
    case ES_OUT_SET_ES_SCRAMBLED_STATE: case ES_OUT_DRAIN: case ES_OUT_SET_META:
    case ES_OUT_RESTART_ES: break;
    default: return VLC_EGENERIC;
    }
    return VLC_SUCCESS;
}
static void destroy(es_out_t *out) { (void)out; }
static const struct es_out_callbacks callbacks={.add=add,.send=send_block,.del=del,.control=control,.destroy=destroy};
static void timeout(int sig) { (void)sig; _exit(124); }
int main(int argc,char **argv)
{
    if(argc!=4) { fprintf(stderr,"Usage: %s MEDIA SEEK_US|-1 fast|precise\n",argv[0]); return 2; }
    char *end; int64_t seek=strtoll(argv[2],&end,10);
    if(*end || seek < -1 || (strcmp(argv[3],"fast") && strcmp(argv[3],"precise"))) return 2;
    signal(SIGALRM,timeout); alarm(30);
    const char *opts[]={"--ignore-config","--no-audio","--no-spu","--verbose=2"};
    libvlc_instance_t *vlc=libvlc_new(ARRAY_SIZE(opts),opts);
    if(!vlc) return 3;
    vlc_object_t *root=VLC_OBJECT(vlc->p_libvlc_int);
    vlc_object_InitInputConfig(root,true,false);
    char *url=vlc_path2uri(argv[1],NULL);
    stream_t *stream=url?vlc_stream_NewURL(root,url):NULL;
    struct capture c={.out={.cbs=&callbacks}};
    demux_t *demux=stream?demux_New(VLC_OBJECT(stream),"avformat",url,stream,&c.out):NULL;
    free(url);
    if(!demux) { if(stream) vlc_stream_Delete(stream); libvlc_release(vlc); return 4; }
    if(seek>=0 && demux_Control(demux,DEMUX_SET_TIME,(vlc_tick_t)seek,!strcmp(argv[3],"precise"))) {
        demux_Delete(demux); libvlc_release(vlc); return 5;
    }
    unsigned loops=0; int status;
    do { status=demux_Demux(demux); } while(status==VLC_DEMUXER_SUCCESS && ++loops<10000 && c.packets<10000);
    printf("{\"event\":\"end\",\"status\":%d,\"packets\":%u,\"loops\":%u,\"bounded\":%s}\n",status,c.packets,loops,loops<10000&&c.packets<10000?"true":"false");
    demux_Delete(demux);
    while(c.ids) del(&c.out,c.ids);
    libvlc_release(vlc); alarm(0);
    return status==VLC_DEMUXER_EOF && loops<10000 && c.packets<10000?0:6;
}
