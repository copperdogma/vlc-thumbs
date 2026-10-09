#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Bounded packet-identity/timestamp diagnostic for baseline and MP4 scratch candidate.

A match does not prove decoding, presentation, clock synchronization or trimming.
Repeated packet hashes in multiple edits retain all independent timestamp options.
"""
import argparse, hashlib, json, os, subprocess
from decimal import Decimal
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe',type=Path,required=True)
    p.add_argument('--candidate-probe',type=Path,required=True)
    p.add_argument('--baseline-build',type=Path,required=True)
    p.add_argument('--candidate-build',type=Path,required=True)
    p.add_argument('--fixtures',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():p.error('output already exists')
    args.output.mkdir();out=args.output.resolve()
    cases=[('base.mp4',0,'precise'),('base.mp4',9125000,'fast'),('base.mp4',10125000,'precise'),
           ('nonkeyframe-trim.mp4',0,'precise'),('nonkeyframe-trim.mp4',125000,'fast'),
           ('two-edits.mp4',-1,'precise'),('two-edits.mp4',3125000,'precise'),
           ('negative-ctts.mp4',0,'precise'),('negative-ctts-trim.mp4',0,'precise'),
           ('dwell-control.mp4',0,'precise')]
    results=[]
    for mode,build in [('baseline',args.baseline_build),('candidate',args.candidate_build)]:
        env=os.environ.copy();env.update(VLC_LIB_PATH=str(build.resolve()/'modules'),VLC_PLUGIN_PATH=str(build.resolve()/'modules/.libs'))
        for index,(name,seek,speed) in enumerate(cases):
            label=f'{index:02d}-{mode}-{Path(name).stem}-{seek}-{speed}'
            executable=args.probe if mode=='baseline' else args.candidate_probe
            cmd=[str(executable.resolve()),str((args.fixtures/name).resolve()),str(seek),speed]
            with (out/(label+'.jsonl')).open('xb') as dest,(out/(label+'.log')).open('xb') as log:
                r=subprocess.run(cmd,env=env,stdout=dest,stderr=log,timeout=35)
            rows=[json.loads(l) for l in (out/(label+'.jsonl')).read_text().splitlines()]
            packets=[row for row in rows if row['event']=='packet']
            refs=json.loads((args.fixtures/(name+'.packets.json')).read_text())['packets']
            by_hash={}
            for ref in refs:by_hash.setdefault(ref['data_hash'].split(':')[-1],[]).append(ref)
            errors=[];missing=0;ambiguous=0;valid=0;invalid=0
            for pkt in packets:
                options=by_hash.get(pkt['md5'],[])
                if not options:missing+=1;continue
                if len(options)>1:ambiguous+=1
                choices=[]
                for ref in options:
                    if 'pts_time' not in ref or 'dts_time' not in ref:continue
                    # Compare with full precision before assigning an integer-us tolerance.
                    dp=Decimal(pkt['pts']-1)-Decimal(ref['pts_time'])*1000000
                    dd=Decimal(pkt['dts']-1)-Decimal(ref['dts_time'])*1000000
                    choices.append((max(abs(dp),abs(dd)),dp,dd,ref.get('flags')))
                if not choices:missing+=1;continue
                _,dp,dd,flags=min(choices,key=lambda c:c[0])
                if abs(dp)<=2 and abs(dd)<=2:valid+=1
                else:
                    invalid+=1
                    if len(errors)<10:errors.append({'ordinal':pkt['ordinal'],'md5':pkt['md5'],'pts_error_us':str(dp),'dts_error_us':str(dd),'reference_flags':flags})
            pcr=[row['value'] for row in rows if row['event']=='pcr']
            results.append({'label':label,'mode':mode,'fixture':name,'seek_us':seek,'speed':speed,'command':cmd,'environment':{k:env[k] for k in ['VLC_LIB_PATH','VLC_PLUGIN_PATH']},'returncode':r.returncode,'end':rows[-1] if rows else None,'packets':len(packets),'oracle_matching':valid,'oracle_mismatching':invalid,'oracle_missing':missing,'ambiguous_hashes':ambiguous,'pcr_count':len(pcr),'negative_pcr_count':sum(x<0 for x in pcr),'invalid_pcr_count':sum(x==0 for x in pcr),'first_errors':errors})
    provenance={'sha256':{str(x.resolve()):hashlib.sha256(x.read_bytes()).hexdigest() for x in [args.probe,args.candidate_probe,args.fixtures/'manifest.json',args.baseline_build/'modules/.libs/libmp4_plugin.dylib',args.candidate_build/'modules/.libs/libmp4_plugin.dylib',args.baseline_build/'src/.libs/libvlccore.9.dylib',args.candidate_build/'src/.libs/libvlccore.9.dylib'] if x.exists()},'tolerance_us':2,'scope':'Packet identity and raw timestamps only. Multiple-edit duplicate hashes permit multiple independent timestamp options; ambiguous count is explicit. No presentation or clock proof.'}
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n');(out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    for r in results:print(r['label'],r['returncode'],r['oracle_matching'],r['oracle_mismatching'],r['oracle_missing'],r['negative_pcr_count'])
if __name__=='__main__':main()
