import sys, os, json, statistics, time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'tests/story-002'))
import baseline_control_trial as c
out=ROOT/'work/validation/story002/control-pragmatic-current-002'
out.mkdir()
a=SimpleNamespace(output=out,media=ROOT/'work/fixtures/story-002/standard-cache-pressure.mp4',baseline=ROOT/'work/build/VLCBaseline.app',feature=ROOT/'work/build/vlc-arm64/VLC.app',probe=ROOT/'work/validation/story002/control-response-probe-v4-frontmost',pointer=ROOT/'work/validation/story002/native-pointer',observer_diagnostic=True,state={'captures':[],'arms':{},'blocks':[],'status':'running','method':'phase AX; validated-frontmost-instance acquisition; actual pixel render; 20 per arm; AB BA BA AB','median_allowance_percent':20})
# Only pass normal desktop launch variables to owned subprocesses.
for k in list(os.environ):
    if k not in ('PATH','HOME','USER','LOGNAME','TMPDIR','LANG','LC_CTYPE'): del os.environ[k]
log=c.playback.Log(out/'actions.jsonl')
arms={}
def save(): c.write_json(out/'summary.json',a.state)
try:
    a.state['fingerprints_before']=c.fingerprints(a)
    for name in ('baseline','feature'):
        arm=c.Arm(name,getattr(a,name),a,log); arms[name]=arm; a.state['arms'][name]=arm.state
        arm.launch(); arm.activate_geometry(); arm.paused()
        l=arm.capture('template-left','left',png=True,mode='phase')
        r=arm.capture('template-right','right',old=l['settled_center_x'],png=True,mode='phase')
        arm.templates={'left':l['settled_center_x'],'right':r['settled_center_x']}
        if abs(arm.templates['right']-arm.templates['left']-140)>4: raise RuntimeError('Template separation mismatch')
        save()
    for side in ('left','right'):
        if abs(arms['baseline'].templates[side]-arms['feature'].templates[side])>2: raise RuntimeError('Cross-arm template mismatch')
    for bi,order in enumerate(c.ORDERS):
        for name in order:
            arm=arms[name]; arm.activate_geometry(); arm.paused()
            arm.capture(f'block{bi}-seed','right',expected=arm.templates['right'],mode='phase')
            old=arm.templates['right']; samples=[]
            for i in range(5):
                side='left' if i%2==0 else 'right'
                row=arm.capture(f'block{bi}-click{i}',side,expected=arm.templates[side],old=old,mode='phase',scored=True)
                if row.get('outcome')!='response': raise RuntimeError('Censored sample: stopping dependent collection')
                samples.append(row['latency_ms']); old=arm.templates[side]; save()
            arm.paused(); arm.activate_geometry()
            a.state['blocks'].append({'block':bi,'arm':name,'samples_ms':samples,'median_ms':statistics.median(samples)})
            print(json.dumps(a.state['blocks'][-1]),flush=True); save()
    a.state['fingerprints_after']=c.fingerprints(a)
    if a.state['fingerprints_before']!=a.state['fingerprints_after']: raise RuntimeError('Frozen inputs changed')
    results={}
    for name in arms:
        rows=[r['latency_ms'] for r in a.state['captures'] if r['arm']==name and r['scored']]
        if len(rows)!=20: raise RuntimeError('Incomplete arm')
        results[name]={'count':len(rows),'median_ms':statistics.median(rows),'min_ms':min(rows),'max_ms':max(rows),'samples_ms':rows}
    delta=100*(results['feature']['median_ms']/results['baseline']['median_ms']-1)
    a.state.update(status='valid',results=results,median_delta_percent=delta,within_allowance=delta<=20)
except Exception as exc:
    a.state.update(status='invalid',error=str(exc)); print(str(exc),flush=True)
finally:
    for arm in arms.values(): arm.close()
    save(); log.file.close()
print(json.dumps({k:a.state[k] for k in ('status','error','results','median_delta_percent','within_allowance') if k in a.state}),flush=True)
