#!/usr/bin/env python3
"""Analyze completed paired playback artifacts; no UI and no automatic verdict.

python3 tests/story-002/playback_analysis.py --output work/validation/story002/playback-analysis.json
Only completed collections with a finished observer are comparison-eligible.
Failed/incomplete attempts remain diagnostics. All thresholds identify evidence
candidates, never VLC attribution. Setup counters are subtracted from final
counters. Audio/screen PTS and Python/Foundation monotonic timestamps use the
same host clock in these local runs; callback-arrival timestamps cross-check it.
"""
import argparse
import json
import math
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
WORK = (ROOT / 'work').resolve()
COUNTERS = ['video decoded', 'frames displayed', 'frames lost', 'audio decoded', 'buffers played', 'buffers lost']


def rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def percentile(values, p):
    return sorted(values)[max(0, math.ceil(len(values) * p) - 1)] if values else None


def overlaps(start, end, low, high):
    return end > low and start < high


def interval(start, end, low, high, **extra):
    start, end = max(start, low), min(end, high)
    return {'start_relative_s': start - low, 'end_relative_s': end - low,
            'duration_s': max(0, end - start), **extra}


def gaps(buffers, start, end, observer_begin, audio=False):
    timestamp, callbacks, clock_offsets = [], [], []
    for row in buffers:
        pts = row.get('pts_s')
        if pts is None:
            continue
        duration = row.get('duration_s', 0)
        if not (start <= pts <= end or overlaps(pts, pts + duration, start, end)):
            continue
        delta = row.get('pts_gap_s', 0)
        if (audio and abs(delta) > .002) or (not audio and delta > .1):
            timestamp.append({'at_relative_s': pts - start, 'gap_s': delta,
                              'classification': 'capture_timestamp_discontinuity_not_vlc_attribution'})
        callback = row.get('observer_gap_s', 0)
        if callback > max(.1, duration * 3 if audio else .1):
            callbacks.append({'at_relative_s': pts - start, 'gap_s': callback,
                              'classification': 'observer_callback_gap'})
        if 'arrival_s' in row:
            clock_offsets.append(observer_begin + row['arrival_s'] - pts)
    return {'timestamp_discontinuities': timestamp, 'observer_callback_gaps': callbacks,
            'callback_arrival_minus_pts_s': {'median': statistics.median(clock_offsets) if clock_offsets else None,
                                           'p95': percentile(clock_offsets, .95), 'max': max(clock_offsets, default=None)}}


def audio_report(events, start, end, observer_begin, threshold):
    buffers = [r for r in events if r.get('kind') == 'buffer']
    levels = [r for r in events if r.get('kind') == 'rms_10ms' and overlaps(r['pts_s'], r['pts_s'] + r['duration_s'], start, end)]
    audible = [r for r in levels if r['dbfs'] >= threshold]
    first_tone = min((r['pts_s'] for r in audible), default=None)
    last_tone = max((r['pts_s'] + r['duration_s'] for r in audible), default=None)
    silent = []
    run_start = run_end = None
    def finish():
        if run_start is not None:
            location = 'interior'
            if first_tone is None:
                location = 'all_silent'
            elif run_end <= first_tone + .000001:
                location = 'leading_boundary'
            elif run_start >= last_tone - .000001:
                location = 'trailing_boundary'
            silent.append(interval(run_start, run_end, start, end, location=location,
                                   classification='low_digital_app_audio_candidate_not_vlc_attribution'))
    for row in levels:
        left, right = max(row['pts_s'], start), min(row['pts_s'] + row['duration_s'], end)
        if row['dbfs'] < threshold:
            if run_end is not None and left - run_end > .002:
                finish(); run_start = run_end = None
            if run_start is None:
                run_start = left
            run_end = right
        elif run_start is not None:
            finish(); run_start = run_end = None
    finish()
    formats = [r['format'] for r in events if r.get('kind') == 'format']
    errors = [r for r in events if r.get('kind') in ['invalid_audio', 'audio_analysis_error']]
    return {'threshold_dbfs': threshold, 'rms_windows_overlapping_active_interval': len(levels),
            'covered_audio_window_s': sum(min(r['pts_s'] + r['duration_s'], end) - max(r['pts_s'], start) for r in levels),
            'first_audible_relative_s': None if first_tone is None else max(first_tone, start) - start,
            'last_audible_relative_s': None if last_tone is None else min(last_tone, end) - start,
            'below_threshold_intervals': silent,
            'interior_below_threshold_total_s': sum(x['duration_s'] for x in silent if x['location'] == 'interior'),
            'formats': formats, 'analysis_error_count_all_capture': len(errors),
            **gaps(buffers, start, end, observer_begin, audio=True)}


def screen_report(events, start, end, observer_begin):
    frames = [r for r in events if r.get('kind') == 'frame' and start <= r.get('pts_s', -1) <= end]
    candidates = []
    last_hash = run_start = run_end = None
    def finish(reason):
        if run_start is not None and run_end - run_start >= .1:
            candidates.append(interval(run_start, run_end, start, end, end_reason=reason,
                                       classification='unchanged_roi_candidate_not_vlc_attribution'))
    for row in frames:
        capture_gap = row.get('pts_gap_s', 0) > .1 or row.get('observer_gap_s', 0) > .1
        supported = row.get('status') in [0, 1] and 'roi_fnv1a64' in row
        if capture_gap or not supported:
            finish('observer_gap' if capture_gap else 'unsupported_status')
            last_hash = run_start = run_end = None
        if not supported:
            continue
        h, pts = row['roi_fnv1a64'], row['pts_s']
        if last_hash == h:
            run_end = pts
        else:
            finish('roi_changed')
            last_hash = h; run_start = run_end = pts
    finish('active_interval_ended')
    spacing = [b['pts_s'] - a['pts_s'] for a, b in zip(frames, frames[1:]) if b['pts_s'] > a['pts_s']]
    roi_sets = sorted(set(tuple(r['roi_pixels']) for r in frames if 'roi_pixels' in r))
    return {'frames_in_active_interval': len(frames), 'status_counts': {str(k): sum(r.get('status') == k for r in frames) for k in sorted(set(r.get('status', -1) for r in frames))},
            'roi_pixel_rectangles': roi_sets, 'capture_spacing_median_s': statistics.median(spacing) if spacing else None,
            'unchanged_roi_intervals_at_least_100ms': candidates,
            **gaps(frames, start, end, observer_begin)}


def resources_report(events, start, end, app_pid):
    samples = [r for r in events if r.get('kind') == 'sample' and start <= r['monotonic_s'] <= end]
    pids = {}
    for row in samples:
        for proc in row.get('processes', []):
            pid = proc['pid']; name = Path(proc['command']).name
            kind = 'app' if pid == app_pid else 'thumbnail_helper' if name == 'vlc-thumbnail-helper' else 'observer' if name == 'playback-capture' else 'other_app_descendant'
            pids.setdefault(pid, {'kind': kind, 'command': proc['command'], 'records': []})['records'].append((row['monotonic_s'], proc))
    results = []
    for pid, entry in sorted(pids.items()):
        values = entry['records']; cpus = [v[1]['cpu_percent'] for v in values]; rss = [v[1]['rss_kib'] / 1024 for v in values]
        used = [v[1]['cumulative_cpu_s'] for v in values]
        results.append({'pid': pid, 'kind': entry['kind'], 'command': entry['command'], 'sample_count': len(values),
                        'first_sample_relative_s': values[0][0] - start, 'last_sample_relative_s': values[-1][0] - start,
                        'sampled_cpu_percent_mean': statistics.mean(cpus), 'sampled_cpu_percent_p95': percentile(cpus, .95),
                        'sampled_cpu_percent_max': max(cpus), 'sampled_rss_mib_max': max(rss),
                        'cpu_time_s_between_first_last_samples': max(used) - min(used),
                        'lifetime_cpu_s_at_last_sample': used[-1]})
    loads = [r['system_load'][0] for r in samples if r.get('system_load')]
    return {'sample_count': len(samples), 'sample_spacing_s_p95': percentile([r['spacing_s'] for r in samples if r.get('spacing_s')], .95),
            'sample_spacing_s_max': max((r.get('spacing_s') or 0 for r in samples), default=None),
            'system_one_minute_load_range': [min(loads), max(loads)] if loads else None,
            'processes': results,
            'limits': 'Sampled peaks only. ps percent CPU is a moving statistic; cumulative CPU deltas omit window edges. Short helper lifetimes may have no samples; helper last-seen lifetime CPU is not an exact active-window aggregate.'}


def analyze(path, match):
    summary = json.loads((path / 'summary.json').read_text())
    result = {'directory': str(path.relative_to(ROOT)), 'pair': int(match[1]), 'variant': match[2], 'attempt': int(match[3]),
              'completed_collection': summary.get('completed_collection', False), 'collection_error': summary.get('collection_error'),
              'eligible_for_pair_comparison': False, 'source_hash_unchanged': summary.get('source_hash_unchanged'),
              'fixture_sha256': summary.get('source_sha256_before'), 'requested_playback_s': summary.get('requested_playback_s'),
              'timeline_diagnostics_enabled': summary.get('timeline_diagnostics_enabled', True),
              'binary_sha256': summary.get('binary_sha256')}
    capture_path = path / 'capture/summary.json'
    capture = json.loads(capture_path.read_text()) if capture_path.exists() else {}
    result['capture_finalized'] = bool(capture)
    result['capture_config'] = {k: capture.get(k) for k in ['requested_fps', 'normalized_roi', 'window_frame', 'silence_threshold_dbfs']}
    result['timeline_global_rect'] = summary.get('timeline_global_rect')
    if not all(k in summary for k in ['playback_start', 'trial_end', 'initial', 'final']):
        result['analysis_limit'] = 'No complete active interval/counters; setup diagnostic only.'
        return result
    start, end = summary['playback_start']['monotonic_s'], summary['trial_end']['monotonic_s']
    result['active_interval'] = {'start_monotonic_s': start, 'end_monotonic_s': end, 'duration_s': end - start,
                                 'selection': 'Runner resume-command timestamp through scheduled trial end; leading/trailing audio boundaries shown separately.',
                                 'captured_pts_clock': 'Host monotonic seconds, not media seconds. Callback arrival minus PTS provides an alignment cross-check.'}
    initial, final = summary['initial']['counters'], summary['final']['counters']
    delta = {k: final[k] - initial[k] for k in COUNTERS if k in final and k in initial}
    displayed, lost, decoded = (delta.get(k, 0) for k in ['frames displayed', 'frames lost', 'video decoded'])
    result['counter_delta'] = delta
    result['lost_picture_rate'] = {'displayed_plus_lost_denominator': displayed + lost,
                                   'displayed_plus_lost_percent': 100 * lost / (displayed + lost) if displayed + lost > 0 else None,
                                   'decoded_denominator': decoded, 'decoded_percent': 100 * lost / decoded if decoded > 0 else None,
                                   'interpretation': 'Use displayed+lost consistently for paired percentage-point change; decoded shown separately. Seek preparation/decode-ahead means decoded totals are not unique source-frame counts.'}
    states = [e for e in summary.get('state_events', []) if start <= e['monotonic_s'] <= end + 2]
    result['state_observation'] = {'first_play_relative_s': next((e['monotonic_s'] - start for e in states if e['state'] == 'play'), None),
                                   'first_pause_relative_s': next((e['monotonic_s'] - start for e in states if e['state'] == 'pause'), None),
                                   'final': summary['final'], 'playback_advance': summary.get('playback_advance'),
                                   'limit': 'Status polling repeats states; numeric input/playlist enums differ. Whole-second RC time cannot exclude small hover seeks.'}
    begin = summary['capture_ready']['start_uptime_s']
    result['audio'] = audio_report(rows(path / 'capture/audio.jsonl'), start, end, begin, capture.get('silence_threshold_dbfs', -60))
    result['screen'] = screen_report(rows(path / 'capture/screen.jsonl'), start, end, begin)
    result['resources'] = resources_report(rows(path / 'resources.jsonl'), start, end, summary['pid'])
    pointers = rows(path / 'pointer.jsonl')
    result['pointer_schedule'] = {'successful_moves': sum(r.get('kind') == 'move' for r in pointers),
                                 'failed_moves': sum(r.get('kind') == 'move_error' for r in pointers),
                                 'scope': 'Real pointer reach only; native preview deliveries/fixture correspondence require timeline diagnostics and separate native evidence.'}
    result['timeline_events'] = len(rows(path / 'timeline.jsonl'))
    result['observer_finish'] = {k: summary.get(k) for k in ['observer_finish_grace_s', 'observer_finish_wait_start', 'observer_finish_wait_end', 'observer_finish_timeout']}
    result['eligible_for_pair_comparison'] = bool(summary.get('completed_collection') and summary.get('requested_playback_s') == 60 and end - start >= 59.99 and capture and not capture.get('io_error') and not capture.get('capture_error') and summary.get('source_hash_unchanged') and not any(v < 0 for v in delta.values()))
    if not result['eligible_for_pair_comparison']:
        result['analysis_limit'] = 'Diagnostic only: collection/finalization/source integrity incomplete. Excluded from paired comparisons.'
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, default=WORK / 'validation/story002')
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if not root.is_relative_to(WORK) or not output.is_relative_to(WORK) or output.name == 'summary.json':
        ap.error('Read root/output must be beneath work/; output must not replace a trial summary.json')
    runs, pending = [], []
    for path in sorted(root.iterdir()):
        match = re.fullmatch(r'playback-pair-(\d+)-(baseline|feature)-(\d+)', path.name)
        if not match or not path.is_dir():
            continue
        if not (path / 'summary.json').exists():
            pending.append(str(path.relative_to(ROOT))); continue
        runs.append(analyze(path, match))
    selected = {}
    for run in runs:
        key = (run['pair'], run['variant'])
        if run['eligible_for_pair_comparison'] and (key not in selected or selected[key]['attempt'] < run['attempt']):
            selected[key] = run
    pairs = []
    for pair in sorted({r['pair'] for r in runs}):
        baseline, feature = selected.get((pair, 'baseline')), selected.get((pair, 'feature'))
        item = {'pair': pair, 'both_collections_eligible': bool(baseline and feature)}
        if baseline and feature:
            bcfg, fcfg = baseline['capture_config'], feature['capture_config']
            matches = {'fixture_sha256': baseline['fixture_sha256'] == feature['fixture_sha256'],
                       'timeline_diagnostics_enabled': baseline['timeline_diagnostics_enabled'] == feature['timeline_diagnostics_enabled'],
                       'requested_playback_s': baseline['requested_playback_s'] == feature['requested_playback_s'],
                       'capture_fps': bcfg['requested_fps'] == fcfg['requested_fps'],
                       'normalized_roi': bcfg['normalized_roi'] == fcfg['normalized_roi'],
                       'silence_threshold': bcfg['silence_threshold_dbfs'] == fcfg['silence_threshold_dbfs'],
                       'capture_window_size': (bcfg['window_frame'] or [None] * 4)[2:] == (fcfg['window_frame'] or [None] * 4)[2:],
                       'timeline_rect_size': (baseline['timeline_global_rect'] or [None] * 4)[2:] == (feature['timeline_global_rect'] or [None] * 4)[2:]}
            item.update({'baseline': baseline['directory'], 'feature': feature['directory'],
                         'matched_conditions': matches,
                         'diagnostics_cohort': ('enabled' if baseline['timeline_diagnostics_enabled'] else 'disabled') if matches['timeline_diagnostics_enabled'] else 'mixed_incompatible',
                         'baseline_lost_picture_percent': baseline['lost_picture_rate']['displayed_plus_lost_percent'],
                         'feature_lost_picture_percent': feature['lost_picture_rate']['displayed_plus_lost_percent'],
                         'lost_picture_increase_percentage_points': feature['lost_picture_rate']['displayed_plus_lost_percent'] - baseline['lost_picture_rate']['displayed_plus_lost_percent'],
                         'baseline_decoded_denominator_percent': baseline['lost_picture_rate']['decoded_percent'],
                         'feature_decoded_denominator_percent': feature['lost_picture_rate']['decoded_percent'],
                         'interpretation': 'Numerical paired comparison only; no attribution or passing verdict.'})
        pairs.append(item)
    report = {'schema': 1, 'runs': runs, 'pending_runs': pending, 'pairs': pairs,
              'diagnostics_cohorts': {cohort: [p['pair'] for p in pairs if p.get('diagnostics_cohort') == cohort] for cohort in ['enabled', 'disabled', 'mixed_incompatible']},
              'excluded_diagnostics': [r['directory'] for r in runs if not r['eligible_for_pair_comparison']],
              'limitations': ['No automatic pass/fail or VLC attribution. Compare each of three matched pairs, including load/order, not only aggregate means.',
                              'Diagnostics-enabled and disabled cohorts are listed separately; do not combine them into one three-pair qualification. A mixed-incompatible pair has unmatched measurement settings.',
                              'PTS alignment assumes same local host monotonic clock; inspect callback-minus-PTS diagnostics. Arrivals show processing timing, PTS locates captured content.',
                              'Audio levels observe digital app output; calibrate against synthetic tone. Boundary startup/EOF silence is reported separately, never silently removed.',
                              'Screen ROI must be verified to include continuously moving video and exclude controls/preview/letterboxing. Hash repetition is only a freeze candidate; capture gaps are separate.',
                              'Counter deltas subtract initial setup. Displayed/lost totals and decoded totals have different semantics; counters alone cannot attribute lost frames or establish 100ms stalls.',
                              'Resource sampling adds load, misses short peaks, and does not enforce worker/caching bounds. Native controls/accessibility and feature exposure need their separate evidence.']}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'report': str(output), 'runs_analyzed': len(runs), 'eligible_pairs': sum(p['both_collections_eligible'] for p in pairs), 'pending': len(pending)}))


if __name__ == '__main__':
    main()
