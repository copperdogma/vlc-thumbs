#!/usr/bin/env python3
"""Owned real-pointer CLI-off proof: default-enabled preview option overridden."""
import argparse,json,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/story-002'))
import baseline_control_trial as c
import playback_benchmark as p
from native_hover_trial import bundle_digest
ap=argparse.ArgumentParser();ap.add_argument('--app',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
a.app=p.owned(a.app);a.output=p.owned(a.output)
if a.output.exists():ap.error('Fresh owned output required')
a.output.mkdir(parents=True);a.media=ROOT/'work/fixtures/story-002/standard-cache-pressure.mp4';a.pointer=ROOT/'work/validation/story002/native-pointer'
log=p.Log(a.output/'actions.jsonl');arm=None;original=subprocess.Popen;state={}
trace=a.output/'timeline.jsonl';trace.touch(mode=0o600)
def frozen():return {'app':bundle_digest(a.app,p.digest),'runner':p.digest(Path(__file__)),'media':p.digest(a.media),'pointer':p.digest(a.pointer)}
def launch(argv,*args,**kw):
 if argv and argv[0].endswith('/Contents/MacOS/VLC') and '--intf=macosx' in argv:
  argv=list(argv);argv.insert(-1,'--no-macosx-timeline-previews');kw['env']=dict(kw['env'],VLC_TIMELINE_DIAGNOSTICS=str(trace));state['effective_argv']=argv
 return original(argv,*args,**kw)
try:
 state['before']=frozen();subprocess.Popen=launch;arm=c.Arm('feature',a.app,a,log);arm.launch();subprocess.Popen=original
 state['geometry']=arm.activate_geometry();rect=state['geometry']['slider_rect'];state['before_pause']=arm.paused()
 for fraction in [.2,.5,.8]:p.command(a.pointer,['move',arm.process.pid,rect[0]+rect[2]*fraction,rect[1]+rect[3]/2]);time.sleep(.5)
 rows=[json.loads(l)for l in trace.read_text().splitlines()if l.endswith('}')];state['feature_events']=[r for r in rows if r.get('event')in ['hover','dispatch','service','display']]
 processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True);state['helper_children']=[r for r in processes.splitlines()if len(r.split(None,2))==3 and int(r.split(None,2)[1])==arm.process.pid and 'vlc-thumbnail-helper' in r]
 state['after_pause']=arm.paused();state['position_ax']=p.command(a.pointer,['ax',arm.process.pid]);state['passed']=not state['feature_events'] and not state['helper_children'] and 'title Position' in state['position_ax'] and state['after_pause']['media_time_seconds']==state['before_pause']['media_time_seconds']
except Exception as e:state['error']=str(e);state['passed']=False
finally:
 subprocess.Popen=original
 if arm:arm.close()
 state['after']=frozen();state['inputs_unchanged']=state['before']==state['after'];state['passed']=state.get('passed',False) and state['inputs_unchanged'];log.file.close();(a.output/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({'passed':state['passed'],'error':state.get('error'),'output':str(a.output)}));sys.exit(0 if state['passed']else 1)
