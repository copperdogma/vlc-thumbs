#!/usr/bin/env python3
"""Bounded real-pointer Story004 main preview checks; trace timing is diagnostic.
Parent owns launch, pause, geometry, provenance and shutdown. No absolute SLA.
"""
import argparse,json,sys,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/story-002'))
import native_hover_benchmark as h
import playback_benchmark as p
ap=argparse.ArgumentParser();ap.add_argument('--pid',type=int,required=True);ap.add_argument('--rect',required=True);ap.add_argument('--duration',type=float,required=True);ap.add_argument('--trace',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
out=h.owned(a.output);out.mkdir();pointer=ROOT/'work/validation/story002/native-pointer';rect=list(map(float,a.rect.split(',')));rows=[]
def move(seconds,offset=0):
    point=[rect[0]+7+seconds/a.duration*(rect[2]-14),rect[1]+rect[3]/2+offset]
    return json.loads(p.command(pointer,['move',a.pid,*point]))
def collect(label,seconds,burst=False,offset=0):
    tail=h.Tail(a.trace);record={'label':label,'target_seconds':seconds,'input_wall':time.monotonic()};events=[]
    try:
        if burst:
            for t in [12+i*.1 for i in range(30)]:move(t)
        record['pointer']=move(seconds,offset);deadline=time.monotonic()+20;hover=None;display=None;final=None
        while time.monotonic()<deadline and final is None:
            for event in tail.read():
                events.append(event)
                if event.get('event')=='hover':hover=event;display=None
                if hover and event.get('generation')==hover.get('generation'):
                    if event.get('event')=='display' and event.get('requested_us')==hover.get('requested_us'):display=event
                    if event.get('event')=='service':
                        result=event.get('result',{})
                        if result.get('requested_us')==hover.get('bucket_us') and not result.get('preparing') and not result.get('verification_pending'):
                            final=event
            if final is None:time.sleep(.01)
        record.update(hover=hover,display=display,final_service=final,events=events)
        record['passed']=bool(hover and display and display.get('ok') and final and final['result'].get('ok'))
        if record['passed']:
            windows=json.loads(p.command(pointer,['inspect',a.pid]));owned=[w for w in windows if w['layer']==0 and w['bounds']['Width']>=320 and w['bounds']['Height']>=180]
            window=max(owned,key=lambda w:w['bounds']['Width']*w['bounds']['Height']);image=out/(label+'.png')
            subprocess.run(['/usr/sbin/screencapture','-x','-o','-l'+str(window['id']),str(image)],check=True,timeout=5);record['owned_window_image']=str(image)
    finally:tail.handle.close();rows.append(record);(out/'results.json').write_text(json.dumps({'scope':'Main-window actual-pointer trace plus owned screenshots; diagnostic assignment timing, not compositor latency','passed':all(r.get('passed') for r in rows),'rows':rows},indent=2)+'\n')
    if not record['passed']:raise RuntimeError('No final matching hover image: '+label)
try:
    for i,t in enumerate([7,1,9,0,7,1,9,0]):collect('settled-'+str(i),t)
    collect('rapid-latest',15,burst=True)
    p.command(pointer,['move',a.pid,rect[0],rect[1]-100]);time.sleep(.2)
    collect('reenter-tall-target',15,offset=-12)
    print(json.dumps({'passed':True,'requests':len(rows),'output':str(out)}))
except Exception as e:
    print(str(e));sys.exit(1)
