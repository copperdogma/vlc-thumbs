#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Explicit-input master knob-response adapter. Default validates only, never inputs.

--plan JSON supplies fixture, fixture_manifest, pointer, observer and arms
baseline/candidate: app, bundle_id, pid, rc_socket, geometry (window, crop,
points left/right, centers left/right, classifier), and qualified pilot_receipt.
Acquisition additionally requires an exact-plan handoff receipt from root/native.
Cohort: ordinary playback then actual Pause (state4), followed by rendered knob
feedback only. Never resume these seeked sessions; playback uses fresh sessions.
This measures paused rendered knob feedback, not completed seeks or clock updates.
"""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import socket
import statistics
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
RESERVE = 1024 ** 3
OUTPUT_CAP = 512 * 1024 ** 2
CLASSIFIER = [190, 12, 48]
ORDERS = [('baseline', 'candidate'), ('candidate', 'baseline'),
          ('candidate', 'baseline'), ('baseline', 'candidate')]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 ** 2), b''):
            digest.update(block)
    return digest.hexdigest()


def owned(path):
    path = Path(path).resolve()
    if path == WORK.resolve() or not path.is_relative_to(WORK.resolve()):
        raise ValueError('Inputs/outputs must remain under owned work/: ' + str(path))
    return path


def cache_root(arm):
    # Read-only exception for the service's exact isolated NSCachesDirectory path.
    bundle = arm['bundle_id']
    if not re.fullmatch(r'org\.videolan\.vlc\.story005\.[A-Za-z0-9.-]+', bundle):
        raise ValueError('Exact isolated cache bundle required')
    expected = Path.home() / 'Library' / 'Caches' / bundle / 'TimelineThumbnails'
    supplied = Path(arm['cache_root']).absolute()
    if supplied != expected or supplied.resolve() != expected:
        raise ValueError('Cache must be the exact real isolated service directory')
    proof = json.loads(owned(arm['cache_setup_receipt']).read_text())
    if any(proof.get(k) != v for k, v in {'cache_root': str(expected), 'bundle_id': bundle,
            'pid': arm['pid'], 'uid': os.getuid(), 'empty_before_media_open': True,
            'original_cache_preserved': True}.items()):
        raise ValueError('Exact preserved/fresh isolated cache setup receipt required')
    for node in [expected, *expected.parents]:
        info = node.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise ValueError('Cache ancestor must be a real directory')
        if node == expected or node == expected.parent:
            if info.st_uid != os.getuid() or info.st_mode & 0o022:
                raise ValueError('Isolated cache ownership/mode unsafe')
    return expected


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def bounded(out):
    if os.statvfs(WORK).f_bavail * os.statvfs(WORK).f_frsize < RESERVE:
        raise RuntimeError('1GiB free-space reserve reached')
    if sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) > OUTPUT_CAP:
        raise RuntimeError('512MiB output cap reached')


def retire(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(5)
    # A descendant surviving leader exit remains owned and is killed, never adopted.
    inventory = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid='], capture_output=True,
                               text=True, timeout=2, check=True).stdout
    members = [int(row.split()[0]) for row in inventory.splitlines()
               if len(row.split()) == 2 and int(row.split()[1]) == process.pid]
    if members:
        os.killpg(process.pid, signal.SIGKILL)
        raise RuntimeError('Observer group retained descendants: ' + repr(members))


def run(argv, out, name, timeout=12):
    bounded(out)
    with (out / (name + '.stdout')).open('xb') as stdout, (out / (name + '.stderr')).open('xb') as stderr:
        process = subprocess.Popen(list(map(str, argv)), stdout=stdout, stderr=stderr,
                                   start_new_session=True, stdin=subprocess.DEVNULL)
        try:
            process.wait(timeout)
        finally:
            retire(process)
    if process.returncode:
        raise RuntimeError('Owned command failed: ' + name)
    return (out / (name + '.stdout')).read_text()


def load_plan(path, controls=True):
    plan = json.loads(path.read_text())
    hashes = {'plan': sha(path)}
    for field in ('fixture', 'fixture_manifest', 'pointer', 'observer'):
        item = owned(plan[field])
        if not item.is_file():
            raise ValueError('Missing explicit input: ' + field)
        plan[field] = str(item)
        hashes[field] = sha(item)
    if plan.get('fixture_sha256') != hashes['fixture']:
        raise ValueError('Fixture does not match prospectively pinned SHA256')
    manifest = json.loads(Path(plan['fixture_manifest']).read_text())
    records = manifest.get('fixtures', []) + manifest.get('files', [])
    if isinstance(manifest.get('fixture'), dict):
        records.append(manifest['fixture'])
    if not any(record.get('name') == Path(plan['fixture']).name and
               record.get('sha256') == hashes['fixture'] and
               record.get('bytes') == Path(plan['fixture']).stat().st_size for record in records):
        raise ValueError('Fixture manifest does not pin this exact media name/hash/size')
    for name in ('baseline', 'candidate'):
        arm = plan['arms'][name]
        arm['fixture'] = plan['fixture']
        app = owned(arm['app'])
        info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
        if not arm['bundle_id'].startswith('org.videolan.vlc.story005.') or info['CFBundleIdentifier'] != arm['bundle_id']:
            raise ValueError('Explicit isolated bundle identity mismatch')
        executable = (app / 'Contents/MacOS' / info['CFBundleExecutable']).resolve()
        if not isinstance(arm['pid'], int) or arm['pid'] <= 0:
            raise ValueError('Positive exact PID required')
        arm['executable'] = str(executable)
        hashes[name + '_executable'] = sha(executable)
        arm['rc_socket'] = str(owned(arm['rc_socket']))
        geometry = arm['geometry']
        for field, count in ([('window', 4), ('crop', 4), ('classifier', 3)] if controls else [('window', 4), ('timeline', 4), ('roi', 4)]):
            if len(geometry[field]) != count or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in geometry[field]):
                raise ValueError('Invalid geometry/profile: ' + field)
        if geometry['window'][2] <= 0 or geometry['window'][3] <= 0:
            raise ValueError('Positive window dimensions required')
        if controls and geometry['classifier'] != CLASSIFIER:
            raise ValueError('Prospective fixed matched-arm classifier must be190,12,48')
        if not controls:
            arm['cache_root'] = str(cache_root(arm))
            hashes[name + '_cache_setup'] = sha(owned(arm['cache_setup_receipt']))
            continue
        for side in ('left', 'right'):
            if len(geometry['points'][side]) != 2 or not math.isfinite(geometry['centers'][side]):
                raise ValueError('Qualified point/center missing')
        if abs(geometry['centers']['right'] - geometry['centers']['left']) < 40:
            raise ValueError('Knob templates must be distinguishable')
        pilot = owned(arm['pilot_receipt'])
        proof = json.loads(pilot.read_text())
        if proof.get('bundle_id') != arm['bundle_id'] or proof.get('observer_sha256') != hashes['observer'] or proof.get('geometry') != geometry or proof.get('live_positive_negative_ownership_qualified') is not True:
            raise ValueError('Current master observer/geometry pilot is unqualified')
        hashes[name + '_pilot'] = sha(pilot)
    return plan, hashes


def handoff(path, plan_hash, mode):
    receipt = json.loads(owned(path).read_text())
    if receipt.get('plan_sha256') != plan_hash or receipt.get('exclusive_native_handoff') is not True or receipt.get('protocol') != mode:
        raise ValueError('Exact reviewed plan and exclusive native handoff required')
    if mode == 'master-controls-v1' and receipt.get('cg_inputs_allowed') is not True:
        raise ValueError('This protocol needs separately authorized CG inputs')
    return receipt


class RCBarrierError(RuntimeError):
    """Failed stream barrier with bounded bytes and request-boundary evidence."""
    def __init__(self, evidence):
        super().__init__(evidence['error'])
        self.evidence = evidence


def rc_barrier(arm, expected):
    start = time.monotonic()
    request = b'status\nget_time\nstats\n'
    raw = bytearray()
    reply_limit = 256 * 1024
    truncated = False
    try:
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(.2)
            sock.connect(arm['rc_socket'])
            sock.sendall(request)
            deadline = start + 3
            while time.monotonic() < deadline:
                try:
                    data = sock.recv(65536)
                    if not data:
                        break
                    remaining = reply_limit - len(raw)
                    raw.extend(data[:remaining])
                    if len(data) > remaining:
                        truncated = True
                        raise RuntimeError('RC reply exceeded256KiB diagnostic bound')
                except socket.timeout:
                    continue
                if b'end of statistical info' in raw:
                    break
            text = raw.decode(errors='replace')
            state, uri = validate_rc(text, arm['fixture'], expected)
            return {'read_start': start, 'read_end': time.monotonic(), 'raw': text,
                    'state': state, 'source_uri': uri}
    except Exception as error:
        # Preserve the asynchronous stream before rejecting its semantics. No
        # state/source relaxation or inferred response-to-request framing.
        evidence = {'read_start': start, 'read_end': time.monotonic(),
                    'request': request.decode('ascii'), 'rc_socket': arm['rc_socket'],
                    'expected_source_uri': Path(arm['fixture']).resolve().as_uri(),
                    'expected_state_name': expected,
                    'expected_state': {'play': 3, 'pause': 4}.get(expected),
                    'raw': raw.decode(errors='replace'),
                    'raw_reply_base64': base64.b64encode(raw).decode('ascii'),
                    'reply_bytes_retained': len(raw), 'reply_truncated': truncated,
                    'error_type': type(error).__name__, 'error': str(error),
                    'scope': 'Asynchronous stream/request-boundary observability; rejected barrier'}
        raise RCBarrierError(evidence) from error


def validate_rc(text, fixture, expected):
    expected_state = {'play': ('play', 3), 'pause': ('pause', 4)}[expected]
    states = re.findall(r'status change: \( (play|pause|stop) state: (\d+) \)', text)
    sources = re.findall(r'status change: \( new input: (.*?) \)', text)
    uri = Path(fixture).resolve().as_uri()
    if states != [(expected_state[0], str(expected_state[1]))] or sources != [uri] or 'end of statistical info' not in text:
        raise RuntimeError('Fresh exact numeric RC state/source/counter barrier failed')
    return expected_state[1], uri


def center(row):
    knob = row.get('knob', {})
    value = knob.get('center_x_global_points')
    return value if knob.get('valid') and not knob.get('ambiguous') and isinstance(value, (int, float)) and math.isfinite(value) else None


def evaluate(rows, arm, expected, old):
    sessions = [r for r in rows if r.get('kind') == 'session']
    inputs = [r for r in rows if r.get('kind') == 'input_posted']
    ends = [r for r in rows if r.get('kind') == 'completion']
    if len(sessions) != 1 or len(inputs) != 1 or len(ends) != 1:
        raise RuntimeError('Incomplete capture lifecycle')
    session, event, end = sessions[0], inputs[0], ends[0]
    if session.get('observer_version') != 5 or session.get('expected_bundle_id') != arm['bundle_id'] or session.get('pid') != arm['pid'] or session.get('expected_executable_path') != arm['executable'] or not end.get('after_owned') or not end.get('input_routed_sequence') or not event.get('warp_success'):
        raise RuntimeError('Observer/input ownership mismatch')
    phases = [r for r in rows if r.get('kind') == 'ax_phase']
    if [r.get('phase') for r in phases] != ['pre', 'post'] or not all(r.get('owned') for r in phases):
        raise RuntimeError('Pre/post AX ownership failed')
    t0 = event['input_t0_uptime_s']
    routed = [r for r in rows if r.get('kind') == 'input_routed']
    if len(routed) != 3 or [r.get('type') for r in routed] != [5, 1, 2] or any(
        r.get('pid') != arm['pid'] or r.get('event_tag') != event.get('event_tag') or
        r.get('sequence_index') != i or not isinstance(r.get('received_uptime_s'), (int, float)) or
        r['received_uptime_s'] < t0 for i, r in enumerate(routed)):
        raise RuntimeError('Exact tagged input routing sequence absent')
    if session.get('rect_screen_points') != arm['geometry']['crop'] or session.get('scale') != 2 or session.get('ax_check_scope') != 'phase-only-unqualified':
        raise RuntimeError('Observer geometry/ownership boundary mismatch')
    frames = []
    warm_count = 0
    for row in rows:
        if row.get('kind') not in ('display_frame', 'readiness_frame') or row.get('frame_status') != 0:
            continue
        checks = {'app_bundle': arm['bundle_id'], 'retained_target_bundle': arm['bundle_id'],
                  'retained_target_pid': arm['pid'], 'retained_target_executable_path': arm['executable'],
                  'retained_target_terminated': False, 'retained_target_os_exists': True,
                  'frontmost_equals_retained_target': True, 'app_active': True,
                  'parent_window_contains_crop': True}
        if any(row.get(k) != v for k, v in checks.items()):
            raise RuntimeError('Complete frame target ownership lost')
        if row.get('kind') == 'readiness_frame':
            warm_count += 1
            if old is not None and (center(row) is None or abs(center(row) - old) > 2):
                raise RuntimeError('Old rendered knob absent before input')
            continue
        shown, pts = row.get('display_time_uptime_seconds'), row.get('presentation_pts_seconds')
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (shown, pts)) or not row.get('display_time_present'):
            raise RuntimeError('Actual complete-frame timing missing')
        if shown >= t0 and pts >= t0:
            frames.append(row)
    if not warm_count:
        raise RuntimeError('Complete pre-input readiness frame absent')
    matched = [r for r in frames if center(r) is not None and abs(center(r) - expected) <= 2]
    if not matched:
        raise RuntimeError('No rendered response within fixed observation bound')
    response = min(matched, key=lambda r: r['display_time_uptime_seconds'])
    return {'latency_ms': (response['display_time_uptime_seconds'] - t0) * 1000,
            'input_t0': t0, 'display_time': response['display_time_uptime_seconds'],
            'presentation_pts': response['presentation_pts_seconds'], 'center': center(response),
            'boundary': 'Paused complete rendered knob response; not completed seeking'}


def acquire(plan, out, state):
    for block, order in enumerate(ORDERS):
        for name in order:
            arm = plan['arms'][name]
            g = arm['geometry']
            label = f'block{block}-{name}'
            run([plan['pointer'], 'activate', arm['pid']], out, label + '-activate', 5)
            focus = json.loads(run([plan['pointer'], 'focus', arm['pid']], out, label + '-focus', 5))
            if not focus.get('app_active') or focus.get('window_position') != g['window'][:2] or focus.get('window_size') != g['window'][2:]:
                raise RuntimeError('Prospective geometry/frontmost instance changed')
            state['barriers'].append({'arm': name, 'block': block, **rc_barrier(arm, 'pause')})
            old = None
            for index, side in enumerate(['right', 'left', 'right', 'left', 'right', 'left']):
                label = f'block{block}-{name}-{index}'
                raw = out / (label + '.jsonl')
                attempt = {'arm': name, 'block': block, 'index': index, 'scored': index != 0,
                           'raw': str(raw), 'side': side}
                state['attempts'].append(attempt)
                try:
                    argv = [plan['observer'], '--bundle-id', arm['bundle_id'], '--pid', arm['pid'],
                            '--expected-executable', arm['executable'], '--classifier', ','.join(map(str, g['classifier'])),
                            '--rect', ','.join(map(str, g['crop'])), '--point', ','.join(map(str, g['points'][side])),
                            '--click', '--count', 180, '--duration-ms', 3000, '--ax-mode', 'phase', '--output', raw]
                    run(argv, out, label)
                    rows = [json.loads(line) for line in raw.read_text().splitlines()]
                    attempt['result'] = evaluate(rows, arm, g['centers'][side], old)
                    attempt['valid'] = True
                except Exception as error:
                    attempt.update(valid=False, exclusion=str(error))
                    raise
                finally:
                    write(out / 'summary.json', state)
                old = g['centers'][side]
            state['barriers'].append({'arm': name, 'block': block, **rc_barrier(arm, 'pause')})
    samples = {n: [a['result']['latency_ms'] for a in state['attempts'] if a['arm'] == n and a['scored'] and a['valid']] for n in ('baseline', 'candidate')}
    if any(len(v) != 20 for v in samples.values()):
        raise RuntimeError('Incomplete prospective20-valid-per-arm cohort')
    results = {n: {'samples_ms': v, 'median_ms': statistics.median(v), 'range_ms': [min(v), max(v)]} for n, v in samples.items()}
    delta = 100 * (results['candidate']['median_ms'] / results['baseline']['median_ms'] - 1)
    state.update(status='valid', results=results, median_delta_percent=delta, within20percent=delta <= 20)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mode', choices=['validate', 'acquire'], default='validate')
    parser.add_argument('--handoff', type=Path)
    args = parser.parse_args()
    out = owned(args.output)
    if out.exists():
        parser.error('Fresh output required')
    plan, hashes = load_plan(args.plan)
    out.mkdir(parents=True)
    state = {'status': 'validated-only', 'hashes': hashes, 'attempts': [], 'barriers': [],
             'cohort': 'Paused rendered knob feedback after ordinary playback then actual Pause',
             'resume_seeked_sessions': False,
             'scope': '20 valid controls per arm; median plus20percent; not completed seek or hover latency; playback uses fresh sessions'}
    try:
        if args.mode == 'acquire':
            if not args.handoff:
                raise ValueError('Reviewed handoff required')
            state['handoff'] = handoff(args.handoff, hashes['plan'], 'master-controls-v1')
            state['status'] = 'acquiring'
            acquire(plan, out, state)
            if sha(plan['fixture']) != hashes['fixture']:
                raise RuntimeError('Fixture changed during collection')
    except Exception as error:
        state.update(status='excluded', error=str(error))
        if isinstance(error, RCBarrierError):
            state['barrier_failure'] = error.evidence
    finally:
        write(out / 'summary.json', state)
    print(json.dumps({'status': state['status'], 'output': str(out)}))
    return 0 if state['status'] in ('valid', 'validated-only') else 1


if __name__ == '__main__':
    raise SystemExit(main())
