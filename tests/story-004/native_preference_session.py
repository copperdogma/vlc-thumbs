#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Owned paused preference session; native UI changes supplied by test operator.
Commands on stdin: status LABEL, hover LABEL, restart LABEL, seek LABEL, finish.
Never reads/writes ordinary VLC configuration or the daily preview profile.
"""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/story-002'))
import baseline_control_trial as control
import playback_benchmark as playback
from native_hover_trial import bundle_digest
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output=playback.owned(a.output)
if a.output.exists():ap.error('Fresh owned output required')
a.output.mkdir();a.app=ROOT/'work/build/vlc-arm64/VLC.app';a.pointer=ROOT/'work/validation/story002/native-pointer';a.media=ROOT/'work/fixtures/story-002/standard-cache-pressure.mp4';config=a.output/'vlcrc';config.write_text('');trace=a.output/'timeline.jsonl';trace.touch(mode=0o600);log=playback.Log(a.output/'actions.jsonl');arm=None;launches=0;state={'scope':'Owned native preference/seek session, operator observations recorded separately','checkpoints':[]}
def frozen():return {'app':bundle_digest(a.app,playback.digest),'runner':playback.digest(Path(__file__)),'media':playback.digest(a.media),'pointer':playback.digest(a.pointer)}
def checkpoint(label):
 cfg=[line for line in config.read_text().splitlines()if line.startswith('macosx-timeline-previews=')]
 processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True)
 children=[row for row in processes.splitlines()if len(row.split(None,2))==3 and int(row.split(None,2)[1])==arm.process.pid and 'vlc-thumbnail-helper' in row]
 rows=[json.loads(line)for line in trace.read_text().splitlines()if line.endswith('}')]
 row={'label':label,'pid':arm.process.pid,'config_value':cfg,'helper_children':children,'paused':arm.paused(),'focus':json.loads(playback.command(a.pointer,['focus',arm.process.pid])),'ax':playback.command(a.pointer,['ax',arm.process.pid]),'recent_trace':rows[-15:]};state['checkpoints'].append(row);(a.output/'session.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({'label':label,'pid':row['pid'],'config_value':cfg,'helper_count':len(children),'paused':row['paused'],'focus':row['focus']}),flush=True)
def launch():
 global arm,launches
 if arm:arm.close()
 arm=control.Arm('launch'+str(launches),a.app,SimpleNamespace(**vars(a)),log);launches+=1
 original=subprocess.Popen
 def owned_launch(argv,*args,**kw):
  if argv and argv[0]==str(arm.executable) and '--intf=macosx' in argv:
   argv=[x for x in argv if x!='--ignore-config'];argv=[('--config='+str(config)if x.startswith('--config=')else x)for x in argv];kw['env']=dict(kw['env'],VLC_TIMELINE_DIAGNOSTICS=str(trace));state.setdefault('effective_launches',[]).append(argv)
  return original(argv,*args,**kw)
 subprocess.Popen=owned_launch
 try:arm.launch()
 finally:subprocess.Popen=original
 playback.command(a.pointer,['activate',arm.process.pid]);time.sleep(.4);playback.command(a.pointer,['place',arm.process.pid,42,33,1680,1013]);time.sleep(.4)
try:
 state['before']=frozen();launch();checkpoint('initial')
 for line in sys.stdin:
  action,_,label=line.strip().partition(' ')
  if action=='finish':break
  if action=='restart':launch()
  elif action in ('hover','seek'):
   rect,_=playback.slider_rect(a.pointer,arm.process.pid);playback.command(a.pointer,['activate',arm.process.pid]);playback.command(a.pointer,['move'if action=='hover'else'click',arm.process.pid,rect[0]+rect[2]*.6,rect[1]+rect[3]/2]);time.sleep(.8)
  elif action!='status':raise RuntimeError('Unknown action')
  checkpoint(label or action)
finally:
 if arm:arm.close()
 state['after']=frozen();state['inputs_unchanged']=state.get('before')==state['after'];log.file.close();(a.output/'session.json').write_text(json.dumps(state,indent=2)+'\n')
