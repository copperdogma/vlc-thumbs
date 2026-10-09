/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Diagnostic LibVLC playback clock + memory video sink; no native UI proof. */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <vlc_common.h>
#include <vlc_threads.h>
#include <vlc/vlc.h>
#include <vlc/libvlc_media_track.h>
#include <unistd.h>
#include <signal.h>
#define BYTES (320*180*4)
struct context { vlc_mutex_t lock; vlc_cond_t cond; unsigned count; unsigned inflight; libvlc_state_t state; libvlc_time_t position; uint8_t last[BYTES]; };
static void timeout(int sig) { (void)sig; _exit(124); }
static void state_changed(void *opaque, libvlc_state_t state) { struct context *c=opaque;vlc_mutex_lock(&c->lock);c->state=state;vlc_cond_signal(&c->cond);vlc_mutex_unlock(&c->lock); }
static void position_changed(void *opaque,libvlc_time_t time,double pos) { (void)pos;struct context*c=opaque;vlc_mutex_lock(&c->lock);c->position=time;vlc_cond_signal(&c->cond);vlc_mutex_unlock(&c->lock); }
static void *lock_video(void *opaque, void **planes) { struct context*c=opaque;vlc_mutex_lock(&c->lock);if(++c->inflight>32)_exit(125);vlc_mutex_unlock(&c->lock);void*p=malloc(BYTES);if(!p)_exit(125);planes[0]=p;return p; }
static void display_video(void *opaque,void *pixels) { struct context*c=opaque;vlc_mutex_lock(&c->lock);memcpy(c->last,pixels,BYTES);c->count++;c->inflight--;vlc_cond_signal(&c->cond);vlc_mutex_unlock(&c->lock);free(pixels); }
static bool wait_state(struct context*c,libvlc_state_t state,unsigned seconds) { vlc_tick_t end=vlc_tick_now()+VLC_TICK_FROM_SEC(seconds);vlc_mutex_lock(&c->lock);while(c->state!=state&&vlc_cond_timedwait(&c->cond,&c->lock,end)==0){}bool ok=c->state==state;vlc_mutex_unlock(&c->lock);return ok; }
static bool wait_position(struct context*c,unsigned before,unsigned seconds) { vlc_tick_t end=vlc_tick_now()+VLC_TICK_FROM_SEC(seconds);vlc_mutex_lock(&c->lock);while(c->count<=before&&vlc_cond_timedwait(&c->cond,&c->lock,end)==0){}bool ok=c->count>before;vlc_mutex_unlock(&c->lock);return ok; }
static void string(const char*s) { putchar('"');for(const unsigned char*p=(const unsigned char*)(s?s:"");*p;p++){if(*p=='"'||*p=='\\')printf("\\%c",*p);else if(*p<32)printf("\\u%04x",*p);else putchar(*p);}putchar('"'); }
int main(int argc,char**argv) {
 if(argc<4||argc>5){fprintf(stderr,"Usage: %s MEDIA OUTPUT_RGBA TARGET_US [ENUMERATED_STABLE_ID]\n",argv[0]);return 2;}
 char*end;int64_t target=strtoll(argv[3],&end,10);if(*end||target<0)return 2;
 signal(SIGALRM,timeout);alarm(30);struct context c={0};vlc_mutex_init(&c.lock);vlc_cond_init(&c.cond);
 const char*options[]={"--ignore-config","--demux=avformat","--no-audio","--no-spu","--avcodec-hw=none","--verbose=2"};libvlc_instance_t*vlc=libvlc_new(ARRAY_SIZE(options),options);if(!vlc)return 3;
 const struct libvlc_media_player_cbs callbacks={.version=0,.on_state_changed=state_changed,.on_position_changed=position_changed};libvlc_media_player_t*player=libvlc_media_player_new(vlc,&callbacks,&c);libvlc_media_t*media=libvlc_media_new_path(argv[1]);if(!player||!media)return 3;
 libvlc_video_set_callbacks(player,lock_video,NULL,display_video,&c);libvlc_video_set_format(player,"RGBA",320,180,320*4);libvlc_media_player_set_media(player,media);int play=libvlc_media_player_play(player);bool playing=wait_state(&c,libvlc_Playing,5);vlc_tick_wait(vlc_tick_now()+VLC_TICK_FROM_SEC(1));
 libvlc_media_tracklist_t*tracks=libvlc_media_player_get_tracklist(player,libvlc_track_video,false);size_t count=tracks?libvlc_media_tracklist_count(tracks):0;bool found=argc==4;
 printf("{\"play_status\":%d,\"playing\":%s,\"target_us\":%"PRId64",\"tracks_before\":[",play,playing?"true":"false",target);
 for(size_t i=0;i<count;i++){libvlc_media_track_t*t=libvlc_media_tracklist_at(tracks,i);printf("%s{\"id\":",i?",":"");string(t->psz_id);printf(",\"stable\":%s,\"selected\":%s}",t->id_stable?"true":"false",t->selected?"true":"false");if(argc==5&&t->id_stable&&strcmp(t->psz_id,argv[4])==0)found=true;}
 printf("],\"requested_id\":");string(argc==5?argv[4]:"");printf(",\"requested_id_found_stable\":%s",found?"true":"false");
 if(found&&argc==5)libvlc_media_player_select_tracks_by_ids(player,libvlc_track_video,argv[4]);if(tracks)libvlc_media_tracklist_delete(tracks);
 libvlc_media_player_set_pause(player,1);bool paused=wait_state(&c,libvlc_Paused,3);vlc_mutex_lock(&c.lock);unsigned before=c.count;c.position=-1;vlc_mutex_unlock(&c.lock);int seek=found?libvlc_media_player_set_time(player,target,false):-1;bool display_ready=seek==0&&wait_position(&c,before,5);vlc_tick_wait(vlc_tick_now()+VLC_TICK_FROM_MS(500));vlc_mutex_lock(&c.lock);bool frame=display_ready&&c.count>before;vlc_mutex_unlock(&c.lock);libvlc_time_t movie=libvlc_media_player_get_time(player);libvlc_state_t state=libvlc_media_player_get_state(player);
 tracks=libvlc_media_player_get_tracklist(player,libvlc_track_video,true);count=tracks?libvlc_media_tracklist_count(tracks):0;printf(",\"paused_before_seek\":%s,\"seek_status\":%d,\"display_ready\":%s,\"new_display_frame\":%s,\"movie_time_us\":%"PRId64",\"state\":%d,\"selected_after\":[",paused?"true":"false",seek,display_ready?"true":"false",frame?"true":"false",movie,state);
 for(size_t i=0;i<count;i++){libvlc_media_track_t*t=libvlc_media_tracklist_at(tracks,i);if(i)putchar(',');string(t->psz_id);}printf("]");if(tracks)libvlc_media_tracklist_delete(tracks);
 vlc_mutex_lock(&c.lock);FILE*f=found&&frame?fopen(argv[2],"wb"):NULL;bool saved=f&&fwrite(c.last,1,BYTES,f)==BYTES;if(f)fclose(f);printf(",\"display_count\":%u,\"rgba_saved\":%s,\"width\":320,\"height\":180}\n",c.count,saved?"true":"false");vlc_mutex_unlock(&c.lock);fflush(stdout);
 libvlc_media_player_stop_async(player);libvlc_media_player_release(player);libvlc_media_release(media);libvlc_release(vlc);alarm(0);return saved?0:6;
}
