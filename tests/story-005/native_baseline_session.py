#!/usr/bin/env python3
"""Owned unchanged-master native baseline launch; 15 minute absolute cleanup bound."""
import json,os,subprocess,time,socket,hashlib,plistlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/story005-native-baseline'
APP=OUT/'VLCStory005Baseline006.app'
ID='org.videolan.vlc.story005.nativebaseline.discriminator006'
MIN_FREE_BYTES=1024**3
def require_free_space():
 stat=os.statvfs(OUT)
 available=stat.f_bavail*stat.f_frsize
 if available < MIN_FREE_BYTES:
  raise RuntimeError(f'Native launch refused: {available} bytes available, {MIN_FREE_BYTES} required')
require_free_space()  # Fail closed before profile, logs, or process creation.
cache=Path.home()/'Library/Caches'/ID
(OUT/'cache').mkdir(exist_ok=True)
if not cache.exists() and not cache.is_symlink(): cache.symlink_to(OUT/'cache',target_is_directory=True)
if cache.resolve() != (OUT/'cache').resolve(): raise RuntimeError('Unique cache unexpectedly exists')
(OUT/'userdata-discriminator006').mkdir(exist_ok=True)
mode=os.environ.get('VLC_NATIVE_BASELINE_MODE','native')
args=[str(APP/'Contents/MacOS/VLC'),'--ignore-config','--config='+str(OUT/'vlcrc'),'--intf=macosx','--extraintf=oldrc','--rc-unix='+str(OUT/'rc.sock'),'--no-media-library','--no-metadata-network-access','--no-macosx-recentitems','--macosx-continue-playback=2','--macosx-control-itunes=0','--no-macosx-mediakeys','--no-macosx-appleremote','--no-macosx-statusicon','--no-video-title-show','--no-macosx-video-autoresize','--no-playlist-autostart','--macosx-nativefullscreenmode']
if mode=='detached':args.append('--no-embedded-video')
if mode=='custom':args=[('--no-macosx-nativefullscreenmode' if x=='--macosx-nativefullscreenmode' else x)for x in args]
with (OUT/'stderr.log').open('w') as err,(OUT/'stdout.log').open('w') as out:
 p=subprocess.Popen(args,stdout=out,stderr=err,env=dict(os.environ,VLC_USERDATA_PATH=str(OUT/'userdata-discriminator006')))
 (OUT/'session.json').write_text(json.dumps({'argv':args,'pid':p.pid,'bundle_id':ID,'userdata':str(OUT/'userdata-discriminator006'),'cache_symlink':str(cache),'fixture_sha256':hashlib.sha256((ROOT/'work/story005-fixtures/standard.mp4').read_bytes()).hexdigest(),'baseline_manifest':'docs/evidence/story-005/baseline-build-manifest.json'},indent=2))
 try:
  deadline=time.monotonic()+900
  while p.poll() is None and time.monotonic()<deadline and not (OUT/'stop').exists():
   try:require_free_space()
   except RuntimeError:break
   if sum((OUT/name).stat().st_size for name in ('stdout.log','stderr.log'))>2*1024**2:break
   time.sleep(.5)
 finally:
  if p.poll() is None:
   p.terminate()
   try:p.wait(8)
   except subprocess.TimeoutExpired:p.kill();p.wait(5)
