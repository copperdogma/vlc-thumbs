#!/usr/bin/env python3
"""Conservative display-space freeze candidates and window-stream cross-check.

A screenshot has a request/callback interval, not a capture PTS. A repeated
pixel hash establishes a candidate only if the last request minus the first
callback exceeds100ms. Errors, callback delays or sampling gaps >=100ms create
unresolved observation intervals. This report never attributes a freeze to VLC.
"""
import argparse,json,math
from pathlib import Path
import playback_analysis as window_analysis


def analyze(directory):
    summary=json.loads((directory/'summary.json').read_text())
    start=summary['playback_start']['monotonic_s'];end=summary['trial_end']['monotonic_s']
    data=[]
    for path in sorted((directory/'display-capture').glob('batch-*.jsonl')):
        data.extend(window_analysis.rows(path))
    samples=[s for s in data if s.get('started_uptime_s',-1)<end and s.get('callback_received_uptime_s',0)>start]
    unresolved=[];candidates=[];current=[];previous=None
    def finish():
        if len(current)>1:
            low=max(start,current[0]['callback_received_uptime_s']);high=min(end,current[-1]['started_uptime_s'])
            if high-low>.1:
                candidates.append({'start_relative_s':low-start,'end_relative_s':high-start,'duration_lower_bound_s':high-low,'captures':len(current),'classification':'same_display_pixels_candidate_not_feature_attribution'})
    for row in samples:
        request=row.get('started_uptime_s');callback=row.get('callback_received_uptime_s')
        valid=isinstance(request,(int,float)) and isinstance(callback,(int,float)) and callback>=request and row.get('error') is None and 'sample_hash_fnv1a64' in row.get('result',{})
        if not valid:
            finish();current=[];previous=None;unresolved.append({'reason':'capture-error-or-invalid-record','row':row});continue
        if callback-request>=.1 or previous and request-previous['callback_received_uptime_s']>=.1:
            finish();current=[];unresolved.append({'reason':'callback-or-sampling-gap-at-least100ms','request_relative_s':request-start,'callback_relative_s':callback-start,'callback_latency_ms':(callback-request)*1000})
        h=row['result']['sample_hash_fnv1a64']
        if current and h!=current[-1]['result']['sample_hash_fnv1a64']:
            finish();current=[]
        current.append(row);previous=row
    finish()
    if not samples:
        unresolved.append({'reason':'no-display-samples'})
    else:
        if samples[0]['callback_received_uptime_s']-start>=.1:unresolved.append({'reason':'leading-observation-gap','duration_s':samples[0]['callback_received_uptime_s']-start})
        if end-samples[-1]['started_uptime_s']>=.1:unresolved.append({'reason':'trailing-observation-gap','duration_s':end-samples[-1]['started_uptime_s']})
    capture=json.loads((directory/'capture/summary.json').read_text())
    screen=window_analysis.screen_report(window_analysis.rows(directory/'capture/screen.jsonl'),start,end,capture['start_uptime_s'])
    comparisons=[]
    for repeat in screen['unchanged_roi_intervals_at_least_100ms']:
        low=start+repeat['start_relative_s'];high=start+repeat['end_relative_s']
        inside=[r for r in samples if r.get('error') is None and r['started_uptime_s']>=low and r['callback_received_uptime_s']<=high]
        hashes={r['result']['sample_hash_fnv1a64'] for r in inside}
        comparisons.append({'window_repeat':repeat,'display_captures_wholly_inside':len(inside),'display_distinct_hashes':len(hashes),'window_capture_staleness_demonstrated':len(hashes)>1})
    return {'directory':str(directory),'completed_collection':summary.get('completed_collection'),'active_duration_s':end-start,'display_sample_count':len(samples),'display_observer_setup':summary.get('display_observer'),'display_freeze_candidates':candidates,'unresolved_observation_intervals':unresolved,'window_repeat_comparisons':comparisons,'scope':'Actual display counterROI; no callback overhead subtraction or fabricated screenshot PTS. Candidates and gaps require attribution; absence qualifies only the measured scope and coverage.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    root=Path(__file__).resolve().parents[2]/'work'
    for path in [args.directory.absolute(),args.output.absolute()]:
        if path.resolve()!=path or not path.is_relative_to(root):p.error('Paths must stay under owned work without symlinks')
    if args.output.exists():p.error('Use fresh output')
    report=analyze(args.directory);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'samples':report['display_sample_count'],'candidates':len(report['display_freeze_candidates']),'unresolved':len(report['unresolved_observation_intervals'])}))

if __name__=='__main__':main()
