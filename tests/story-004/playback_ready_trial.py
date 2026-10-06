#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Unchanged playback protocol with bounded observed activation readiness first."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/story-002'))
import playback_benchmark as playback
original=playback.command;observations=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ready_command(tool,args,*pos,**kwargs):
 result=original(tool,args,*pos,**kwargs)
 if args and args[0]=='activate':
  started=time.monotonic();deadline=started+8;attempts=[]
  while True:
   focus=json.loads(original(tool,['focus',args[1]]));attempts.append({'at_s':time.monotonic()-started,'focus':focus})
   if focus.get('app_active'):break
   if time.monotonic()>=deadline:raise RuntimeError('Owned app did not become frontmost within8s readiness bound')
   time.sleep(.1)
  observations.append({'pid':args[1],'wait_s':time.monotonic()-started,'attempts':attempts})
 return result
output=Path(sys.argv[sys.argv.index('--output')+1]);before=sha(Path(__file__));playback.command=ready_command
try:playback.main()
finally:
 playback.command=original
 if output.is_dir():
  (output/'activation-readiness.json').write_text(json.dumps({'scope':'Acquisition before active measurement; no observer/pointer/scoring change','runner_sha256':before,'runner_unchanged':before==sha(Path(__file__)),'observations':observations},indent=2)+'\n')
