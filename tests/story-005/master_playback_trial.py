#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Master background-preparation-only playback cohort; no pointer input.

Explicit plan shares master_control_trial input/ownership vocabulary. Per arm:
geometry window/timeline/roi/window_id, cache_root; candidate expected_cache_key,
selection dictionary and fresh_cache_receipt. --pair1..3 uses AB,BA,AB order.
Default validates only. Native-owner setup and exact reviewed handoff are required.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import time

import master_control_trial as common

ORDER = [('baseline', 'candidate'), ('candidate', 'baseline'), ('baseline', 'candidate')]


def rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.endswith('}')]


class ProcessSnapshotError(RuntimeError):
    def __init__(self, message, evidence):
        super().__init__(message)
        self.evidence = evidence


def process_snapshot(arm):
    # Darwin's nonfinal comm column truncates; obtain executable identity from libproc.
    import ctypes, errno
    begin = time.monotonic()
    evidence = {'read_start': begin, 'ps': [], 'path_queries': [], 'unknown_exited_children': [],
                'scope': 'Raw ps retained only for exact app and its immediate children'}
    fields = 'pid=,ppid=,uid=,lstart=,rss=,%cpu=,time=,args='
    try:
        library = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
        library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        library.proc_pidpath.restype = ctypes.c_int

        def table(argv, selected=None):
            start = time.monotonic()
            record = {'argv': argv, 'read_start': start, 'rows': []}
            evidence['ps'].append(record)
            try:
                reply = subprocess.run(argv, capture_output=True, text=True, timeout=2, check=False)
            except Exception as error:
                record.update(read_end=time.monotonic(), error=str(error)[:131072])
                raise
            record.update(read_end=time.monotonic(), returncode=reply.returncode, stderr=reply.stderr[:131072])
            result = {}
            for line in reply.stdout.splitlines():
                prefix = line.split(None, 2)
                if len(prefix) < 2 or not all(x.isdigit() for x in prefix[:2]):
                    continue
                pid, parent = map(int, prefix[:2])
                if selected is None:
                    keep = pid == arm['pid'] or parent == arm['pid']
                else:
                    keep = pid in selected
                if not keep:
                    continue
                record['rows'].append(line[:131072])
                values = line.split(None, 11)
                if len(values) != 12 or pid in result:
                    raise RuntimeError('Malformed/duplicate owned process row')
                result[pid] = {'pid': pid, 'ppid': parent, 'uid': int(values[2]),
                    'start_identity': ' '.join(values[3:8]), 'rss_kib': int(values[8]),
                    'cpu_percent': float(values[9]), 'cpu_time': values[10], 'argv': values[11]}
            if reply.returncode != 0:
                raise RuntimeError('Process table query failed')
            return result

        def executable(pid, allow_extra_exit=False):
            start = time.monotonic()
            buffer = ctypes.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
            ctypes.set_errno(0)
            record = {'pid': pid, 'read_start': start}
            evidence['path_queries'].append(record)
            try:
                size = library.proc_pidpath(pid, buffer, len(buffer))
                record.update(read_end=time.monotonic(), returned_bytes=size, errno=ctypes.get_errno(), path_bytes_hex=buffer.value.hex())
                record['path'] = buffer.value.decode('utf-8', errors='strict')
            except Exception as error:
                record.update(read_end=time.monotonic(), error=str(error)[:131072])
                raise
            if allow_extra_exit and size == 0 and record['errno'] == errno.ESRCH:
                return None
            if size <= 0 or size >= len(buffer) or not record['path'].startswith('/'):
                raise RuntimeError('Native executable path query failed')
            return record['path']

        def confirm_extra_exit(record):
            pid = record['pid']
            argv = ['/bin/ps', '-p', str(pid), '-o', 'pid=,ppid=,uid=,lstart=,stat=']
            proof = {'argv': argv, 'read_start': time.monotonic(), 'extra_pid': pid}
            evidence['ps'].append(proof)
            try:
                reply = subprocess.run(argv, capture_output=True, text=True, timeout=2, check=False)
            except Exception as error:
                proof.update(read_end=time.monotonic(), error=str(error)[:131072])
                raise
            proof.update(read_end=time.monotonic(), returncode=reply.returncode,
                         stdout=reply.stdout[:131072], stderr=reply.stderr[:131072])
            if reply.returncode == 1 and not reply.stdout.strip() and not reply.stderr.strip():
                kind = 'absent_after_ESRCH'
            elif reply.returncode == 0 and not reply.stderr.strip():
                rows = reply.stdout.splitlines()
                values = rows[0].split() if len(rows) == 1 else []
                if len(values) != 9 or (int(values[0]), int(values[1]), int(values[2]), ' '.join(values[3:8])) != (pid, record['ppid'], record['uid'], record['start_identity']) or not values[8].startswith('Z'):
                    raise RuntimeError('Extra child exit/zombie identity not confirmed')
                kind = 'same_identity_zombie_after_ESRCH'
            else:
                raise RuntimeError('Extra child exit query failed')
            evidence['unknown_exited_children'].append({'pid': pid, 'ppid': record['ppid'],
                'uid': record['uid'], 'start_identity': record['start_identity'], 'classification': kind,
                'scope': 'Unknown exited child only; no executable/resource/worker claim'})

        before = table(['/bin/ps', '-axo', fields])
        if arm['pid'] not in before:
            raise RuntimeError('Owned attached app disappeared')
        helper = str(Path(arm['executable']).parent / 'vlc-timeline-preview')
        pinned_worker = arm.get('retained_worker_pid')
        if pinned_worker is not None and pinned_worker not in before:
            raise RuntimeError('Retained source worker disappeared')
        excluded = []
        for pid, record in before.items():
            words = shlex.split(record['argv'])
            expected_worker = bool(words) and words[0] == helper and '--worker' in words
            protected = pid == arm['pid'] or pid == pinned_worker or expected_worker
            path = executable(pid, allow_extra_exit=not protected)
            if path is None:
                confirm_extra_exit(record)
                excluded.append(pid)
            else:
                record['executable'] = path
        for pid in excluded:
            del before[pid]
        app = before[arm['pid']]
        if app['executable'] != arm['executable'] or app['uid'] != os.getuid():
            raise RuntimeError('Exact app executable/UID identity changed')
        helper = str(Path(arm['executable']).parent / 'vlc-timeline-preview')
        worker = None
        for record in before.values():
            if record['ppid'] != arm['pid'] or record['executable'] != helper:
                continue
            words = shlex.split(record['argv'])
            if '--worker' not in words:
                continue
            def argument(flag):
                if words.count(flag) != 1:
                    raise RuntimeError('Missing/duplicate worker selection argument')
                return words[words.index(flag) + 1]
            if record['uid'] != os.getuid() or argument('--input') != arm['fixture'] or argument('--video-input-id') != str(arm['selection']['video_input_id']) or argument('--video-count') != str(arm['selection']['video_count']):
                raise RuntimeError('Exact worker input/selection/UID context mismatch')
            if worker is not None:
                raise RuntimeError('More than one retained decoder worker')
            worker = record
        if pinned_worker is not None and (worker is None or worker['pid'] != pinned_worker):
            raise RuntimeError('Retained source worker identity/selection changed')
        retained = {app['pid']}
        if worker is not None:
            retained.add(worker['pid'])
        after = table(['/bin/ps', '-p', ','.join(map(str, sorted(retained))), '-o', fields], retained)
        for pid in retained:
            if pid not in after or any(after[pid][k] != before[pid][k] for k in ('ppid', 'uid', 'start_identity', 'argv')) or executable(pid) != before[pid]['executable']:
                raise RuntimeError('Retained process identity changed during read')
        evidence['read_end'] = time.monotonic()
        return {'read_start': begin, 'read_end': evidence['read_end'], 'app': app, 'worker': worker,
                'load': os.getloadavg(), 'scope': 'Sampled CPU/RSS, not exact peaks or continuous occupancy',
                'identity_diagnostics': evidence}
    except Exception as error:
        evidence.update(read_end=time.monotonic(), failure=str(error))
        raise ProcessSnapshotError('Process snapshot failed: ' + str(error), evidence) from error


def cache_snapshot(arm, expected_key, selection):
    start = time.monotonic()
    root = common.cache_root(arm)
    manifests = list(root.glob('*.json'))
    if not expected_key:
        if manifests or list(root.glob('*.rgba')):
            raise RuntimeError('Matched baseline cache must stay empty')
        return {'read_start': start, 'read_end': time.monotonic(), 'targets': [], 'payloads': []}
    if len(manifests) > 1 or (manifests and manifests[0].name != expected_key + '.json'):
        raise RuntimeError('Cache namespace/source/track/render key mismatch')
    if not manifests:
        return {'read_start': start, 'read_end': time.monotonic(), 'targets': [], 'payloads': []}
    path = manifests[0]
    if path.is_symlink() or path.stat().st_size > 256 * 1024:
        raise RuntimeError('Unsafe/oversized cache manifest')
    data = path.read_bytes()
    manifest = json.loads(data)
    if manifest.get('version') != 5 or manifest.get('key') != expected_key:
        raise RuntimeError('Wrong cache identity/version')
    targets, samples = manifest['targets'], manifest['samples']
    if len(targets) > 2048 or len(samples) > 512:
        raise RuntimeError('Cache manifest bounds exceeded')
    payloads = []
    for stamp in set(targets.values()):
        record = samples[stamp]
        file = record['file']
        if not re.fullmatch('[0-9a-f]{64}', file) or not str(stamp).isdigit():
            raise RuntimeError('Invalid sample identity')
        payload = root / (file + '.rgba')
        if payload.is_symlink() or payload.stat().st_size > 4096 + 320 * 180 * 4:
            raise RuntimeError('Unsafe/oversized cache payload')
        raw = payload.read_bytes()
        head, pixels = raw.split(b'\n', 1)
        header = json.loads(head)
        if hashlib.sha256(raw).hexdigest() != record['sha256'] or header.get('version') != 4 or not header.get('ok') or header.get('sampling') != 'keyframe' or header.get('actual_us') != record['actual_us'] or int(stamp) != record['actual_us']:
            raise RuntimeError('Referenced payload integrity/time mismatch')
        width, height = header['width'], header['height']
        if not (1 <= width <= 320 and 1 <= height <= 180) or header.get('channels') != 4 or len(pixels) != width * height * 4 or header['payload_bytes'] != len(pixels):
            raise RuntimeError('Payload shape mismatch')
        if any(header.get(k) != v for k, v in selection.items()):
            raise RuntimeError('Payload selected-source/track mapping mismatch')
        payloads.append({'file': file, 'sha256': record['sha256'], 'actual_us': record['actual_us']})
    if any(not str(t).isdigit() or target not in samples for t, target in targets.items()):
        raise RuntimeError('Invalid target alias')
    return {'read_start': start, 'read_end': time.monotonic(), 'targets': sorted(targets),
            'manifest_sha256': hashlib.sha256(data).hexdigest(), 'key': expected_key, 'payloads': payloads}


def counters(text):
    return {key: int(value) for key, value in re.findall(r'\|\s*(video decoded|frames displayed|frames lost|audio decoded|buffers played|buffers lost)\s*:\s*(\d+)', text)}


def trial(plan, name, pair, out, state):
    arm = plan['arms'][name]
    arm['fixture'] = plan['fixture']
    g = arm['geometry']
    expected = arm.get('expected_cache_key') if name == 'candidate' else None
    selection = arm.get('selection', {})
    if name == 'candidate':
        fresh = json.loads(common.owned(arm['fresh_cache_receipt']).read_text())
        if fresh.get('cache_root') != arm['cache_root'] or fresh.get('empty_before_media_open') is not True or fresh.get('pid') != arm['pid'] or fresh.get('fixture_sha256') != plan['fixture_sha256'] or fresh.get('cache_key') != expected or fresh.get('selection') != selection:
            raise RuntimeError('Fresh source/track/render cache qualification receipt missing')
        if not re.fullmatch('[0-9a-f]{64}', expected or '') or not selection:
            raise RuntimeError('Explicit qualified cache key/selection required')
    capture = out / 'capture'
    capture.mkdir()
    argv = [plan['observer'], '--bundle-id', arm['bundle_id'], '--expected-executable', arm['executable'],
            '--pid', arm['pid'], '--window-id', g['window_id'], '--timeline-rect', ','.join(map(str, g['timeline'])),
            '--roi', ','.join(map(str, g['roi'])), '--owned-display-audio', '--duration', 65, '--output', capture]
    process = None
    with (out / 'observer.stdout').open('xb') as stdout, (out / 'observer.stderr').open('xb') as stderr:
        try:
            process = subprocess.Popen(list(map(str, argv)), stdout=stdout, stderr=stderr,
                                       start_new_session=True, stdin=subprocess.DEVNULL)
            deadline = time.monotonic() + 4
            while time.monotonic() < deadline:
                ready = rows(out / 'observer.stdout')
                screen, audio = rows(capture / 'screen.jsonl'), rows(capture / 'audio.jsonl')
                if ready and any(r.get('status') == 0 for r in screen) and any(r.get('kind') == 'rms_10ms' and r.get('dbfs', -math.inf) > -60 for r in audio):
                    break
                if process.poll() is not None:
                    raise RuntimeError('Observer exited before audio/screen readiness')
                time.sleep(.05)
            else:
                raise RuntimeError('Pre-t0 owned screen/audio readiness failed')
            if ready[0].get('pid') != arm['pid'] or ready[0].get('bundle_id') != arm['bundle_id']:
                raise RuntimeError('Observer ready identity mismatch')
            state['initial_rc'] = common.rc_barrier(arm, 'play')
            state['initial_processes'] = process_snapshot(arm)
            if name == 'candidate' and state['initial_processes']['worker'] is None:
                raise RuntimeError('Candidate must have exact source worker before t0')
            if name == 'candidate':
                arm['retained_worker_pid'] = state['initial_processes']['worker']['pid']
            t0 = time.monotonic()
            if t0 - ready[0]['start_uptime_s'] >= 4:
                raise RuntimeError('Setup consumed capture headroom; cannot span t1')
            state.update(t0=t0, t1=t0 + 60, cohort='background preparation during playback',
                         occupancy_claim=False, hover_inputs=False, observation_boundaries='Same-host monotonic; cache completion only bracketed by read intervals')
            state['initial_cache'] = cache_snapshot(arm, expected, selection)
            if state['initial_cache']['read_start'] < t0 or state['initial_cache']['read_end'] >= t0 + .75:
                raise RuntimeError('Initial witness snapshot exceeded inside-interval bound')
            previous = set(state['initial_cache']['targets'])
            # Cache witnesses are inside [t0,t1], with750ms acquisition headroom.
            # The retained observer checks foreground/window/pointer every100ms;
            # no periodic focus subprocess delays the endpoint snapshots.
            events = sorted([(t0 + second, 'resource', second) for second in range(61)] +
                            [(t0 + end - .75, 'witness', end) for end in range(10, 61, 10)])
            for scheduled, kind, second in events:
                common.bounded(out)
                time.sleep(max(0, scheduled - time.monotonic()))
                if process.poll() is not None:
                    raise RuntimeError('Capture does not span the entire active interval')
                if kind == 'witness':
                    current = cache_snapshot(arm, expected, selection)
                    if current['read_start'] < t0 or current['read_end'] >= t0 + second - .1:
                        raise RuntimeError('Witness read crossed prospective inside-bin deadline')
                    new = sorted(set(current['targets']) - previous)
                    sample = process_snapshot(arm)
                    row = {'nominal_bin_end': t0 + second, 'scheduled_read': scheduled,
                           'snapshot': current, 'new_target_keys': new, 'processes': sample,
                           'scope': 'Inside60s interval-bracketed sampled proactive completions; not exact completion timestamps/continuous occupancy'}
                    state['preparation_bins'].append(row)
                    if name == 'candidate' and (not new or sample['worker'] is None):
                        raise RuntimeError('Preparation completed early or lacks a valid bin/worker witness')
                    previous = set(current['targets'])
                    state['playing_barriers'].append(common.rc_barrier(arm, 'play'))
                else:
                    sample = process_snapshot(arm)
                    state['resources'].append(sample)
                if sample['app']['start_identity'] != state['initial_processes']['app']['start_identity']:
                    raise RuntimeError('Attached app PID/start identity changed')
                if name == 'candidate' and sample['worker'] is not None and (sample['worker']['pid'], sample['worker']['start_identity']) != (state['initial_processes']['worker']['pid'], state['initial_processes']['worker']['start_identity']):
                    raise RuntimeError('Retained source worker replaced during trial')
                common.write(out / 'summary.json', state)
            state['final_rc'] = common.rc_barrier(arm, 'play')
            # Capture runs65s, spanning t0+60 with setup limited above to4s.
            process.wait(timeout=max(1, 70 - (time.monotonic() - t0)))
            if process.returncode:
                raise RuntimeError('Observer capture/identity error')
            final = json.loads((capture / 'summary.json').read_text())
            if final.get('capture_error') or final.get('io_error'):
                raise RuntimeError('Observer reports capture errors')
            screen, audio = rows(capture / 'screen.jsonl'), rows(capture / 'audio.jsonl')
            complete = [r for r in screen if r.get('status') == 0]
            if any('display_time_uptime_s' not in r or r.get('mach_timebase_numer', 0) <= 0 or r.get('mach_timebase_denom', 0) <= 0 for r in complete):
                raise RuntimeError('Complete screen lacks actual displayTime/timebase')
            buffers = [r for r in audio if r.get('kind') == 'buffer']
            if not complete or not buffers or min(r['pts_s'] for r in complete) > t0 or max(r['pts_s'] for r in complete) < t0 + 60 or min(r['pts_s'] for r in buffers) > t0 or max(r['pts_s'] + r['duration_s'] for r in buffers) < t0 + 60:
                raise RuntimeError('Audio/complete-screen coverage does not span t0/t1')
            before, after = counters(state['initial_rc']['raw']), counters(state['final_rc']['raw'])
            if before.keys() != after.keys() or len(before) != 6 or any(after[k] < before[k] for k in before):
                raise RuntimeError('Missing/reset current playback counters')
            state['counter_deltas'] = {k: after[k] - before[k] for k in before}
            state['observer_summary'] = final
            state['status'] = 'collected-unscored'
        except ProcessSnapshotError as error:
            state['snapshot_failure'] = error.evidence
            common.write(out / 'snapshot-failure.json', error.evidence)
            common.write(out / 'summary.json', state)
            raise
        except common.RCBarrierError as error:
            # Preserve before observer cleanup, which may itself report failure.
            state['barrier_failure'] = error.evidence
            raise
        finally:
            if process:
                common.retire(process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--arm', required=True, choices=['baseline', 'candidate'])
    parser.add_argument('--pair', required=True, type=int, choices=[1, 2, 3])
    parser.add_argument('--mode', choices=['validate', 'acquire'], default='validate')
    parser.add_argument('--handoff', type=Path)
    args = parser.parse_args()
    plan, hashes = common.load_plan(args.plan, controls=False)
    out = common.owned(args.output)
    if out.exists():
        parser.error('Fresh output required')
    out.mkdir(parents=True)
    state = {'status': 'validated-only', 'arm': args.arm, 'pair': args.pair,
             'prospective_order': ORDER[args.pair - 1], 'hashes': hashes, 'resources': [],
             'preparation_bins': [], 'playing_barriers': [], 'cohort': 'background preparation during playback',
             'scope': 'One unscored60s trial;3 matched pairs required;not simultaneous hover/worst-case playback'}
    try:
        if args.mode == 'acquire':
            if not args.handoff:
                raise ValueError('Reviewed exclusive handoff required')
            state['handoff'] = common.handoff(args.handoff, hashes['plan'], 'master-background-playback-v1')
            trial(plan, args.arm, args.pair, out, state)
            if common.sha(plan['fixture']) != hashes['fixture']:
                raise RuntimeError('Fixture changed during acquisition')
    except Exception as error:
        state.update(status='excluded', exclusion=str(error))
        if isinstance(error, ProcessSnapshotError):
            state['snapshot_failure'] = error.evidence
            common.write(out / 'snapshot-failure.json', error.evidence)
        if isinstance(error, common.RCBarrierError):
            state['barrier_failure'] = error.evidence
    finally:
        common.write(out / 'summary.json', state)
    print(json.dumps({'status': state['status'], 'output': str(out)}))
    return 0 if state['status'] in ('validated-only', 'collected-unscored') else 1


if __name__ == '__main__':
    raise SystemExit(main())
