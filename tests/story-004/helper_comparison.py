#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only old/new initialization comparison; private results stay in work/."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
import helper_worker_contract as worker
ROOT=Path(__file__).resolve().parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--media',required=True,type=Path);ap.add_argument('--targets',required=True);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    output=args.output.resolve();assert output.is_relative_to(ROOT/'work/validation/story004') and not output.exists();output.mkdir(parents=True)
    baseline=ROOT/'work/validation/story004/baseline-155231/VLCStory002.app/Contents/MacOS/vlc-thumbnail-helper'
    candidate=ROOT/'work/build/thumbnail-helper/thumbnail-helper';media=args.media.resolve();targets=[round(float(s)*1e6) for s in args.targets.split(',')]
    if not media.is_file():
        (output/'results.json').write_text(json.dumps({'valid':False,'classification':'setup-invalid','reason':'source not mounted or not a readable regular file','media':str(media)},indent=2)+'\n')
        print('Invalid setup: media unavailable; no trial collected');return
    record={'scope':'Isolated helper repeated initialization and requested sample delivery, not native UI/playback or cold-NAS timing. AB then BA, OS/source cache warmth uncontrolled.', 'inputs':{'baseline_sha256':digest(baseline),'candidate_sha256':digest(candidate),'media':str(media),'stat_before':list(media.stat()),'targets_us':targets},'arms':[]}
    def save(): (output/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    save()
    for block,order in enumerate([['baseline','candidate'],['candidate','baseline']]):
        for arm in order:
            process=None;state={'block':block,'arm':arm,'requests':[]};record['arms'].append(state);start=time.monotonic()
            try:
                if arm=='candidate':process,ready=worker.start(candidate,media);state.update(startup_ms=(time.monotonic()-start)*1000,ready=ready)
                for ident,target in enumerate(targets,1):
                    t=time.monotonic()
                    try:
                        if arm=='baseline':
                            run=subprocess.run([str(baseline),'--input',str(media),'--time-us',str(target),'--video-ordinal','0','--video-count','1','--max-width','320','--max-height','180'],capture_output=True,timeout=7)
                            line,sep,pixels=run.stdout.partition(b'\n');header=json.loads(line);header['process_exit']=run.returncode
                        else:
                            process.stdin.write(f'{ident} {target}\n'.encode());header,pixels=worker.reply(process)
                        result={'target_us':target,'elapsed_ms':(time.monotonic()-t)*1000,'header':header,'pixels_sha256':hashlib.sha256(pixels).hexdigest() if pixels else None,'usable':bool(header['ok']) and bool(pixels)}
                    except Exception as e:result={'target_us':target,'elapsed_ms':(time.monotonic()-t)*1000,'usable':False,'error':str(e)}
                    state['requests'].append(result);save()
                if process:worker.finish(process)
            except Exception as e:state['startup_or_shutdown_error']=str(e)
            finally:
                if process and process.poll() is None:process.kill();process.wait(timeout=3)
                state['total_ms']=(time.monotonic()-start)*1000;save()
    t=time.monotonic()
    run=subprocess.run([str(candidate),'--fingerprint','sampled','--input',str(media)],capture_output=True,timeout=17)
    record['proposed_sampled_fingerprint']={'elapsed_ms':(time.monotonic()-t)*1000,'exit':run.returncode,'reply':json.loads(run.stdout) if run.stdout else None,'scope':'Read-only proposed-policy cost measurement; not app enablement or complete-content equality'}
    record['inputs']['stat_after']=list(media.stat());record['inputs']['helper_hashes_unchanged']=digest(baseline)==record['inputs']['baseline_sha256'] and digest(candidate)==record['inputs']['candidate_sha256'];save()
    print(json.dumps({'arms':[{'arm':s['arm'],'block':s['block'],'total_ms':s['total_ms'],'usable':sum(r['usable'] for r in s['requests']),'startup_ms':s.get('startup_ms')} for s in record['arms']],'fingerprint_ms':record['proposed_sampled_fingerprint']['elapsed_ms']}))
if __name__=='__main__':main()
