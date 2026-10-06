#!/usr/bin/env python3
"""Matched ordinary-control latency on preserved baseline and current feature.

Example (root owns native setup/qualification):
  python3 tests/story-002/baseline_control_trial.py \
    --baseline work/build/VLCBaseline.app --feature work/build/vlc-arm64/VLC.app \
    --media work/fixtures/story-002/standard-cache-pressure.mp4 \
    --output work/validation/story002/control-paired-001

Both exact apps run concurrently, paused, with separate owned configurations
and RC sockets. Four rounds AB,BA,BA,AB contain samples/4 clicks per arm/block.
Default 100 samples/arm qualifies a global p95 comparison; --samples 8 is only
a setup diagnostic, never a p95 result. --allowed-percent defaults to zero
added latency. No absolute latency target, overhead subtraction or thumbnail
regression denominator is introduced. This measures ordinary light-style knob
feedback from physical input and actual display frames, not completed seeking
or hover-to-thumbnail latency. Existing thumbnail evidence stays separate.

--observer-diagnostic selects a separate 2x2 diagnostic: baseline/feature x
per-frame/phase AX, eight scored clicks per condition (32 total), four balanced
rounds, a declared 3000ms observation bound in every condition. No p95 or
qualification. Passive exact-PID tagged event receipts establish routing, not
AppKit handling. Phase AX ownership is checked pre/post only and is not claimed
equivalent to per-frame ownership. Missing routing stops collection, no retries.
"""
import argparse
import json
import math
import os
from pathlib import Path
import plistlib
import re
import socket
import stat
import subprocess
import time

import native_hover_benchmark as hover
import playback_benchmark as playback
from native_hover_trial import bundle_digest

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
GEOMETRY = [42, 33, 1680, 1013]
SLIDER = (208., 1020., 1330., 16.)
CROP = [900, 1016, 240, 28]
FOREGROUND_POLICY = 'workspace-frontmost-retained-instance-v4'
OBSERVER_VERSION = 4
POINTS = {'left': [950, 1028], 'right': [1090, 1028]}
ORDERS = [('baseline', 'feature'), ('feature', 'baseline'),
          ('feature', 'baseline'), ('baseline', 'feature')]

# Each condition occupies every block position once; eight clicks/condition.
DIAGNOSTIC_ORDERS = [
    [('baseline', 'per-frame'), ('feature', 'phase'), ('feature', 'per-frame'), ('baseline', 'phase')],
    [('feature', 'per-frame'), ('baseline', 'phase'), ('baseline', 'per-frame'), ('feature', 'phase')],
    [('baseline', 'phase'), ('feature', 'per-frame'), ('feature', 'phase'), ('baseline', 'per-frame')],
    [('feature', 'phase'), ('baseline', 'per-frame'), ('baseline', 'phase'), ('feature', 'per-frame')],
]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def eligible(row, post, mode="per-frame"):
    """Only actual complete owned presentations; no callback-time substitution."""
    if row.get('kind') != ('display_frame' if post else 'readiness_frame'):
        return False
    if row.get('frame_status') != 0 or not row.get('result'):
        return False
    if row.get('observer_version') != OBSERVER_VERSION or row.get('ax_check_scope') != ('complete-presentations-only' if mode == 'per-frame' else 'phase-only-unqualified'):
        raise RuntimeError('Observer version/complete-frame AX scope mismatch')
    if not all(row.get(key) for key in ['app_active', 'parent_window_contains_crop']):
        raise RuntimeError('Actual frame ownership guard failed')
    if row.get('ax_mode') != mode or row.get('ax_checked_this_frame') != (mode == 'per-frame'):
        raise RuntimeError('AX observer mode/measurement mismatch')
    if (row.get('foreground_policy') != FOREGROUND_POLICY or
            row.get('frontmost_pid') != row.get('retained_target_pid') or
            not isinstance(row.get('frontmost_pid'), int) or row['frontmost_pid'] <= 0 or
            row.get('frontmost_bundle') != playback.BUNDLE_ID or
            row.get('retained_target_bundle') != playback.BUNDLE_ID or
            row.get('retained_target_present') is not True or row.get('retained_target_os_exists') is not True or
            row.get('retained_target_terminated') is not False or row.get('frontmost_equals_retained_target') is not True or
            not isinstance(row.get('expected_executable_path'), str) or not Path(row['expected_executable_path']).is_absolute() or
            row.get('retained_target_executable_path') != row.get('expected_executable_path')):
        raise RuntimeError('Foreground process identity/existence guard failed')
    for prefix in ['app', 'frontmost', 'retained_target']:
        begin, end = row.get(prefix + '_query_begin_uptime_s'), row.get(prefix + '_query_end_uptime_s')
        if not finite(begin) or not finite(end) or end < begin:
            raise RuntimeError('Foreground query timing missing or reversed')
    if mode == 'per-frame' and not row.get('ax_input_point_owned'):
        raise RuntimeError('Actual frame AX ownership guard failed')
    if mode == 'per-frame' and (not finite(row.get('ax_query_begin_uptime_s')) or not finite(row.get('ax_query_end_uptime_s')) or row['ax_query_end_uptime_s'] < row['ax_query_begin_uptime_s']):
        raise RuntimeError('Per-frame AX query timing missing or reversed')
    if mode == 'phase' and row.get('ax_input_point_owned') is not False:
        raise RuntimeError('Phase frame falsely claims AX ownership')
    if row.get('crop_screen_points') != CROP or row.get('pixel_width') != 480 or row.get('pixel_height') != 56:
        raise RuntimeError('Capture geometry/scale changed')
    pts, shown = row.get('presentation_pts_seconds'), row.get('display_time_uptime_seconds')
    if not finite(pts) or not finite(shown) or not row.get('display_time_present') or not row.get('display_time_mach_ticks', 0):
        raise RuntimeError('Complete frame missing actual presentation timestamps')
    if post:
        t0 = row.get('input_t0_uptime_s')
        if not finite(t0) or pts < t0 or shown < t0:
            return False
        if not row.get('post_input_complete_presentation'):
            raise RuntimeError('Probe post-input presentation guard disagrees')
    return True


def knob_center(row):
    """Pixel-only light-style knob; invalid/ambiguous shapes never match."""
    knob = row.get('knob', {})
    center = knob.get('center_x_global_points')
    if not knob.get('valid') or knob.get('ambiguous') or not finite(center):
        return None
    if knob.get('consistent_rows', 0) < 3 or not finite(knob.get('center_spread_pixels')) or knob['center_spread_pixels'] > 2:
        return None
    widths = knob.get('widths_pixels', [])
    if len(widths) != knob['consistent_rows'] or any(not finite(w) or not 6 <= w <= 32 for w in widths):
        return None
    return center


def near(center, expected):
    return center is not None and abs(center-expected) <= 2.


class Arm:
    def __init__(self, name, app, args, actions):
        self.name, self.app, self.args, self.actions = name, app, args, actions
        self.out = args.output / name
        self.out.mkdir()
        self.process = self.sock = self.rc = self.rc_log = None
        self.stdout = self.stderr = None
        self.socket_path = Path(f'/tmp/vlc002-control-{os.getpid()}-{name}.sock')
        self.templates = {}
        self.state = {'app': str(app), 'scope': 'Owned paused ordinary-control arm'}
        with (app / 'Contents/Info.plist').open('rb') as handle:
            info = plistlib.load(handle)
        if info.get('CFBundleIdentifier') != playback.BUNDLE_ID:
            raise ValueError('Only isolated development VLC bundles are allowed')
        self.executable = hover.owned(app / 'Contents/MacOS' / info.get('CFBundleExecutable', 'VLC'))

    def launch(self):
        if self.socket_path.exists() or self.socket_path.is_symlink():
            raise RuntimeError('Refusing existing RC socket')
        env = dict(os.environ)
        env.pop('VLC_TIMELINE_DIAGNOSTICS', None)
        argv = [str(self.executable), '--ignore-config', f'--config={self.out / "vlcrc"}',
                '--intf=macosx', '--extraintf=oldrc', f'--rc-unix={self.socket_path}',
                '--rc-fake-tty', '--stats', '--play-and-pause', '--start-time=0',
                '--no-media-library', '--no-metadata-network-access', '--macosx-control-itunes=0',
                '--no-macosx-mediakeys', '--no-macosx-recentitems', '--macosx-continue-playback=2',
                '--no-macosx-nativefullscreenmode', '--no-video-title-show', '--no-loop',
                '--no-repeat', '--no-random', '--verbose=2', str(self.args.media)]
        result = subprocess.run([str(self.executable), '--longhelp', '--advanced', '--help-verbose'],
                                capture_output=True, text=True, env=env, timeout=10)
        (self.out / 'compiled-options.txt').write_text(result.stdout)
        (self.out / 'compiled-options.stderr').write_text(result.stderr)
        declared = set(re.findall(r'--([a-z][a-z0-9-]*)', result.stdout))
        missing = sorted({arg[2:].split('=', 1)[0] for arg in argv[1:] if arg.startswith('--')} - declared)
        self.state['argument_validation'] = {'returncode': result.returncode, 'missing_options': missing}
        if result.returncode or missing:
            raise RuntimeError(f'{self.name} compiled argv validation failed: {missing}')
        self.stdout, self.stderr = [(self.out / name).open('xb') for name in ['app.stdout', 'app.stderr']]
        self.process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, stdout=self.stdout,
                                        stderr=self.stderr, start_new_session=True)
        self.state.update(pid=self.process.pid, argv=argv, timeline_diagnostics_enabled=False)
        self.actions.add({'kind': 'launch', 'arm': self.name, 'pid': self.process.pid, 'argv': argv})
        self.sock = socket.socket(socket.AF_UNIX)
        deadline = time.monotonic() + 12
        while True:
            if self.process.poll() is not None:
                raise RuntimeError('Owned app exited before RC connection')
            try:
                self.sock.connect(str(self.socket_path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() >= deadline:
                    raise RuntimeError('Owned RC startup timeout')
                time.sleep(.1)
        self.sock.settimeout(.2)
        self.rc_log = playback.Log(self.out / 'rc.jsonl')
        self.rc = playback.RC(self.sock, self.rc_log)
        self.state['initial_paused_zero'] = playback.paused_zero(self.rc, self.actions, timeout=12)

    def activate_geometry(self):
        if self.process.poll() is not None:
            raise RuntimeError('Owned app exited')
        playback.command(self.args.pointer, ['activate', self.process.pid])
        time.sleep(.4)
        self.actions.add({'kind': 'place', 'arm': self.name,
                          'result': playback.command(self.args.pointer, ['place', self.process.pid, *GEOMETRY])})
        time.sleep(.4)
        rect, inventory = playback.slider_rect(self.args.pointer, self.process.pid)
        focus = json.loads(playback.command(self.args.pointer, ['focus', self.process.pid]))
        if tuple(rect) != SLIDER or not focus.get('app_active') or focus.get('window_position') != GEOMETRY[:2] or focus.get('window_size') != GEOMETRY[2:]:
            raise RuntimeError(f'Unexpected fixed native geometry: {rect}, {focus}')
        return {'slider_rect': rect, 'focus': focus, 'ax_inventory': inventory}

    def paused(self):
        # Pinned oldrc.c:1194 replies with the pause marker to a status query;
        # it does not emit another state-transition event while already paused.
        # Reuse the existing continuous trial's fresh reply/statistics barrier.
        reply_path = self.out / 'rc.jsonl'
        offset = reply_path.stat().st_size
        with self.rc.lock:
            prior_stats = len(self.rc.snapshots)
        self.rc.send(['get_time', 'stats', 'status'])
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            with self.rc.lock:
                fresh_stats = len(self.rc.snapshots) > prior_stats
            with reply_path.open('rb') as replies:
                replies.seek(offset)
                rows = [json.loads(line) for line in replies.read().splitlines() if line.endswith(b'}')]
            lines = [r.get('line') for r in rows if r.get('kind') == 'reply']
            if fresh_stats and "Type 'pause' to continue." in lines and 'status: returned 0 (no error)' in lines:
                snap = self.rc.snapshot()
                if snap['state'] != 'pause':
                    raise RuntimeError('Ordinary control trial changed paused state')
                return snap
            time.sleep(.05)
        raise RuntimeError('Fresh current RC pause check timed out')

    def capture(self, label, side, expected=None, old=None, png=False, mode="per-frame", scored=False):
        raw = self.out / f'{label}.jsonl'
        stdout, stderr = self.out / f'{label}.stdout', self.out / f'{label}.stderr'
        argv = [str(self.args.probe), '--pid', str(self.process.pid), '--expected-executable', str(self.executable), '--rect', ','.join(map(str, CROP)),
                '--point', ','.join(map(str, POINTS[side])), '--click', '--count',
                '600' if self.args.observer_diagnostic else '90', '--duration-ms',
                '3000' if self.args.observer_diagnostic else '900', '--ax-mode', mode, '--output', str(raw)]
        if png:
            argv += ['--save-last-image', str(self.out / f'{label}.png')]
        record = {'arm': self.name, 'label': label, 'target': side, 'raw': str(raw),
                  'argv': argv, 'stdout': str(stdout), 'stderr': str(stderr), 'faults': [],
                  'ax_mode': mode, 'scored': scored, 'observation_bound_ms': 3000 if self.args.observer_diagnostic else 900}
        try:
            with stdout.open('xb') as out, stderr.open('xb') as err:
                result = subprocess.run(argv, stdout=out, stderr=err, timeout=15 if self.args.observer_diagnostic else 10)
            record['returncode'] = result.returncode
            rows = [json.loads(line) for line in raw.read_text().splitlines()]
            record['ax_phases'] = [r for r in rows if r.get('kind') == 'ax_phase']
            record['input_routed'] = [r for r in rows if r.get('kind') == 'input_routed']
            errors = [r['error'] for r in rows if r.get('error')]
            if result.returncode or errors or stdout.stat().st_size or stderr.stat().st_size:
                raise RuntimeError(f'Probe failed or emitted diagnostics: {errors}')
            sessions = [r for r in rows if r.get('kind') == 'session']
            done = [r for r in rows if r.get('kind') == 'completion']
            inputs = [r for r in rows if r.get('kind') == 'input_posted']
            if len(sessions) != 1 or len(done) != 1 or len(inputs) != 1 or not done[0].get('after_owned') or not inputs[0].get('warp_success') or not done[0].get('input_routed_sequence'):
                raise RuntimeError('Incomplete probe lifecycle')
            if sessions[0].get('observer_version') != OBSERVER_VERSION or sessions[0].get('ax_check_scope') != ('complete-presentations-only' if mode == 'per-frame' else 'phase-only-unqualified') or sessions[0].get('foreground_policy') != FOREGROUND_POLICY or sessions[0].get('target_identity_policy') != 'readiness-retained-no-replacement' or sessions[0].get('expected_executable_path') != str(self.executable) or sessions[0].get('retained_target_executable_path') != str(self.executable) or sessions[0].get('pid') != self.process.pid or sessions[0].get('rect_screen_points') != CROP or sessions[0].get('scale') != 2 or sessions[0].get('input') != 'move-down-up':
                raise RuntimeError('Probe input/session identity mismatch')
            tag = inputs[0].get('event_tag')
            routed = record['input_routed']
            if len(routed) != 3 or [r.get('type') for r in routed] != [5, 1, 2] or any(
                    r.get('event_tag') != tag or r.get('pid') != self.process.pid or
                    r.get('sequence_index') != i or r.get('location') != POINTS[side] or
                    not finite(r.get('received_uptime_s')) or r['received_uptime_s'] < inputs[0]['input_t0_uptime_s']
                    for i, r in enumerate(routed)):
                raise RuntimeError('Own tagged input routing sequence invalid; no retry')
            phases = record['ax_phases']
            if [r.get('phase') for r in phases] != ['pre', 'post'] or any(
                    not r.get('owned') or not r.get('slider_role') or not finite(r.get('slider_value'))
                    for r in phases):
                raise RuntimeError('Pre/post AX slider ownership/value missing')
            t0 = inputs[0]['input_t0_uptime_s']
            if not finite(t0) or any(not finite(r.get('query_begin_uptime_s')) or not finite(r.get('query_end_uptime_s')) or r['query_end_uptime_s'] < r['query_begin_uptime_s'] for r in phases) or phases[0]['query_end_uptime_s'] > t0 or phases[1]['query_begin_uptime_s'] < done[0].get('observation_end_uptime_s', float('inf')):
                raise RuntimeError('Pre/post AX query was not outside scored capture')
            record['input_routed_sequence'] = True
            warm = [r for r in rows if eligible(r, False, mode)]
            valid = [r for r in rows if eligible(r, True, mode)]
            if self.args.observer_diagnostic:
                valid = [r for r in valid if r['display_time_uptime_seconds'] <= t0 + 3 and r['presentation_pts_seconds'] <= t0 + 3]
            record['observation_end_uptime_s'] = done[0].get('observation_end_uptime_s')
            record['observation_bound_reached'] = done[0].get('observation_bound_reached')
            if not warm or not valid:
                raise RuntimeError('Missing complete readiness or post-input presentation')
            record['readiness_hash'] = warm[-1]['result']['sample_hash_fnv1a64']
            record['settled_hash'] = valid[-1]['result']['sample_hash_fnv1a64']
            record['readiness_center_x'] = knob_center(warm[-1])
            record['settled_center_x'] = knob_center(valid[-1])
            record['post_input_centers'] = [knob_center(r) for r in valid]
            record['complete_presentations'] = len(valid)
            t0 = inputs[0]['input_t0_uptime_s']
            if not finite(t0) or any(r['input_t0_uptime_s'] != t0 for r in valid):
                raise RuntimeError('Input timestamp mismatch')
            if old is not None and not near(record['readiness_center_x'], old):
                raise RuntimeError('Independent old light-style knob center absent before input')
            if expected is not None:
                if old is not None and abs(expected-old) <= 100:
                    raise RuntimeError('New control template indistinguishable from old')
                matches = [r for r in valid if near(knob_center(r), expected) and (old is None or abs(knob_center(r)-old) > 100)]
                if not matches:
                    if self.args.observer_diagnostic and scored and done[0].get('observation_bound_reached') and all(near(knob_center(r), old) for r in valid):
                        record.update(outcome='right_censored_no_response', input_t0=t0,
                                      censor_bound_ms=3000, faults=['No new knob frame within declared observation bound'])
                        return record
                    raise RuntimeError('Expected new light-style knob center missing')
                if not near(record['settled_center_x'], expected):
                    raise RuntimeError('Expected new settled light-style knob center missing')
                # Select earliest actual display time, never callback receipt.
                first = min(matches, key=lambda r: r['display_time_uptime_seconds'])
                record.update(outcome='response', first_matching_frame_index=first['index'],
                              first_matching_display_time=first['display_time_uptime_seconds'],
                              input_t0=t0, latency_ms=(first['display_time_uptime_seconds']-t0)*1000)
            elif not near(record['settled_center_x'], POINTS[side][0]):
                raise RuntimeError('Settled pixel knob does not identify expected physical control point')
        except Exception as exc:
            record['faults'].append(str(exc))
            raise
        finally:
            self.actions.add({'kind': 'capture', **record})
            self.args.state['captures'].append(record)
        return record

    def close(self):
        # Stop only this runner's subprocess/socket; never find-and-kill by name.
        errors = []
        if self.rc:
            try:
                self.rc.send(['quit'])
            except OSError as exc:
                errors.append(str(exc))
            self.rc.stop.set()
        if self.sock:
            self.sock.close()
        if self.rc:
            self.rc.thread.join(timeout=2)
        playback.terminate(self.process)
        if self.process and self.socket_path.exists() and stat.S_ISSOCK(self.socket_path.lstat().st_mode):
            self.socket_path.unlink()
        for handle in [self.stdout, self.stderr]:
            if handle:
                handle.close()
        if self.rc_log:
            self.rc_log.file.close()
        self.state['exit_code'] = self.process.returncode if self.process else None
        self.state['cleanup_errors'] = errors


def fingerprints(args):
    result = {'media': playback.digest(args.media), 'probe': playback.digest(args.probe),
              'pointer': playback.digest(args.pointer)}
    for name in ['baseline', 'feature']:
        app = getattr(args, name)
        result[name + '_app_tree'] = bundle_digest(app, playback.digest)
        for key, file in [('plugin', 'plugins/libmacosx_plugin.dylib'), ('helper', 'vlc-thumbnail-helper')]:
            path = app / 'Contents/MacOS' / file
            result[name + '_' + key] = playback.digest(path) if path.is_file() else None
    for name in ['baseline_control_trial.py', 'control_response_probe.m', 'native_hover_trial.py',
                 'native_hover_benchmark.py', 'playback_benchmark.py', 'native-pointer.m']:
        result['test:' + name] = playback.digest(Path(__file__).with_name(name))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--baseline', type=Path, default=WORK / 'build/VLCBaseline.app')
    ap.add_argument('--feature', type=Path, default=WORK / 'build/vlc-arm64/VLC.app')
    ap.add_argument('--media', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--allowed-percent', type=float, default=0.)
    ap.add_argument('--samples', type=int, default=100)
    ap.add_argument('--observer-diagnostic', action='store_true',
                    help='Separate 32-click arm x AX-mode diagnostic, 3000ms bound, no p95 or qualification')
    ap.add_argument('--probe', type=Path, default=WORK / 'validation/story002/control-response-probe-v4')
    ap.add_argument('--pointer', type=Path, default=WORK / 'validation/story002/native-pointer')
    args = ap.parse_args()
    try:
        for name in ['baseline', 'feature', 'media', 'output', 'probe', 'pointer']:
            setattr(args, name, hover.owned(getattr(args, name)))
        if args.baseline != WORK / 'build/VLCBaseline.app' or args.feature != WORK / 'build/vlc-arm64/VLC.app':
            raise ValueError('Only preserved VLCBaseline.app and current vlc-arm64/VLC.app are allowed')
        if args.media.parent != WORK / 'fixtures/story-002' or args.media.name not in ['standard-cache-pressure.mp4', 'standard-cache-pressure.mkv']:
            raise ValueError('Only generated standard-cache-pressure MP4/MKV fixtures are allowed')
        if args.output.exists() or args.output.is_symlink():
            raise ValueError('Use a fresh owned work output directory')
        if not 4 <= args.samples <= 100 or args.samples % 4:
            raise ValueError('--samples must be4..100 and divisible by4')
        if not finite(args.allowed_percent) or args.allowed_percent < 0:
            raise ValueError('--allowed-percent must be finite and nonnegative; default0')
        if not all(p.is_dir() for p in [args.baseline, args.feature]) or not args.media.is_file() or not all(p.is_file() and os.access(p, os.X_OK) for p in [args.probe, args.pointer]):
            raise ValueError('Existing owned apps, fixture, pointer and control probe required')
        commands = subprocess.check_output(['ps', '-axo', 'command='], text=True).splitlines()
        if any(str(app / 'Contents/MacOS/VLC') in line for app in [args.baseline, args.feature] for line in commands):
            raise ValueError('Requested app already running; this runner never stops existing apps')
    except (ValueError, OSError) as exc:
        ap.error(str(exc))
    args.output.mkdir(parents=True)
    actions = playback.Log(args.output / 'actions.jsonl')
    state = args.state = {'schema_version': 4, 'observer_version': OBSERVER_VERSION, 'foreground_policy': FOREGROUND_POLICY, 'scope': 'Matched paused main-window ordinary light-style knob response; not hover-to-thumbnail latency or completed seek',
                         'measurement': 'First independent new light-style knob center within2pt on owned complete WindowServer frame: display_time minus physical input t0; PTS/display>=t0; no subtraction',
                         'samples_per_arm': 16 if args.observer_diagnostic else args.samples, 'pilot': args.samples < 100 and not args.observer_diagnostic,
                         'observer_diagnostic': args.observer_diagnostic, 'diagnostic_samples_per_condition': 8 if args.observer_diagnostic else None,
                         'observation_bound_ms': 3000 if args.observer_diagnostic else 900,
                         'phase_guard_equivalence_proven': False, 'routing_receipt_scope': 'Exact PID nonce-filtered passive tap; routing only, not AppKit handling', 'allowed_percent': args.allowed_percent,
                         'allowance_origin': 'Cam: pre-change baseline comparison; default no additional latency',
                         'os_cache_condition': 'Warm/uncontrolled host caches; two templates and repeated two-position clicks, no cache clearing',
                         'knob_metric_scope': 'Pinned VLCSliderCell light appearance,2x sRGB BGRA; five rows around inputY; unique white6..32px cluster in>=3rows; center spread<=2px; target tolerance2pt; old/new>100pt',
                         'geometry': GEOMETRY, 'slider_rect': SLIDER, 'crop': CROP, 'points': POINTS,
                         'orders': ORDERS, 'captures': [], 'blocks': [], 'arms': {}, 'started': playback.stamp(),
                         'completed_collection': False, 'qualified': False, 'method_pilot_passed': False}
    arms = {}
    before = None
    try:
        before = state['fingerprints_before'] = fingerprints(args)
        for name in ['baseline', 'feature']:
            arms[name] = Arm(name, getattr(args, name), args, actions)
            state['arms'][name] = arms[name].state
            arms[name].launch()
        for arm in arms.values():
            arm.state['template_geometry'] = arm.activate_geometry()
            arm.state['template_pause'] = arm.paused()
            left = arm.capture('template-left', 'left', png=True)
            arm.templates['left'] = left['settled_center_x']
            right = arm.capture('template-right', 'right', old=arm.templates['left'], png=True)
            arm.templates['right'] = right['settled_center_x']
            if abs((arm.templates['right']-arm.templates['left'])-140.) > 4.:
                raise RuntimeError('Independent left/right knob separation disagrees with physical140pt points')
            arm.state['templates'] = dict(arm.templates)
        if any(not near(arms['baseline'].templates[side], arms['feature'].templates[side]) for side in POINTS):
            raise RuntimeError('Baseline/feature corresponding control template centers differ')
        write_json(args.output / 'templates.json', {name: arm.templates for name, arm in arms.items()})
        plan = DIAGNOSTIC_ORDERS if args.observer_diagnostic else [[(name, 'per-frame') for name in order] for order in ORDERS]
        state['condition_orders'] = plan
        for round_id, order in enumerate(plan):
            for name, mode in order:
                arm = arms[name]
                block = {'round': round_id, 'arm': name, 'ax_mode': mode, 'order': list(order), 'records': [],
                         'geometry_before': arm.activate_geometry(), 'pause_before': arm.paused()}
                state['blocks'].append(block)
                arm.capture(f'round-{round_id:02}-{mode}-seed-right', 'right', expected=arm.templates['right'], mode=mode)
                previous = 'right'
                for index in range(2 if args.observer_diagnostic else args.samples // 4):
                    side = 'left' if index % 2 == 0 else 'right'
                    record = arm.capture(f'round-{round_id:02}-{mode}-click-{index:03}', side,
                                         expected=arm.templates[side], old=arm.templates[previous], mode=mode, scored=True)
                    block['records'].append(record)
                    if record.get('outcome') == 'right_censored_no_response':
                        raise RuntimeError('Routed input right-censored at3000ms; dependent sequence halted, no retry')
                    previous = side
                block['pause_after'] = arm.paused()
                rect, inventory = playback.slider_rect(args.pointer, arm.process.pid)
                focus = json.loads(playback.command(args.pointer, ['focus', arm.process.pid]))
                if tuple(rect) != SLIDER or not focus.get('app_active') or focus.get('window_position') != GEOMETRY[:2] or focus.get('window_size') != GEOMETRY[2:]:
                    raise RuntimeError('Block native geometry/activation changed')
                block['geometry_after'] = {'slider_rect': rect, 'focus': focus, 'ax_inventory': inventory}
                actions.add({'kind': 'block_complete', 'round': round_id, 'arm': name, 'count': len(block['records'])})
        state['completed_collection'] = True
    except Exception as exc:
        state['collection_error'] = str(exc)
        actions.add({'kind': 'collection_error', 'message': str(exc)})
    finally:
        for arm in arms.values():
            try:
                arm.close()
            except Exception as exc:
                state.setdefault('cleanup_errors', []).append(f'{arm.name}: {exc}')
        try:
            after = state['fingerprints_after'] = fingerprints(args)
            state['integrity_unchanged'] = before is not None and before == after
            state['changed_inputs'] = [key for key in before or {} if before[key] != after.get(key)]
        except Exception as exc:
            state['integrity_unchanged'] = False
            state['integrity_error'] = str(exc)
        valid = state['completed_collection'] and state['integrity_unchanged'] and not state.get('cleanup_errors')
        values = {name: [r['latency_ms'] for block in state['blocks'] if block['arm'] == name for r in block['records'] if 'latency_ms' in r] for name in ['baseline', 'feature']}
        state['observed_counts'] = {name: len(v) for name, v in values.items()}
        if args.observer_diagnostic:
            conditions = {}
            for name in ['baseline', 'feature']:
                for mode in ['per-frame', 'phase']:
                    records = [r for b in state['blocks'] if b['arm'] == name and b['ax_mode'] == mode for r in b['records']]
                    conditions[name + ':' + mode] = {'scored_count': len(records),
                        'response_count': sum('latency_ms' in r for r in records),
                        'right_censored_count': sum(r.get('outcome') == 'right_censored_no_response' for r in records),
                        'latencies_ms': [r['latency_ms'] for r in records if 'latency_ms' in r],
                        'faults': [r['faults'] for r in records if r['faults']]}
            state['observer_diagnostic_conditions'] = conditions
            valid = valid and all(c['scored_count'] == 8 for c in conditions.values())
            state['diagnostic_completed'] = valid
        else:
            valid = valid and all(len(v) == args.samples for v in values.values())
        state['collection_valid'] = valid
        if valid and args.samples == 100 and not args.observer_diagnostic:
            p95 = {name: sorted(v)[math.ceil(.95*len(v))-1] for name, v in values.items()}
            if p95['baseline'] <= 0:
                state['collection_valid'] = False
                state['comparison_error'] = 'Nonpositive baseline p95 cannot supply relative denominator'
            else:
                limit = p95['baseline'] * (1+args.allowed_percent/100)
                state['comparison'] = {'p95_ms': p95, 'feature_relative_delta_percent': 100*(p95['feature']/p95['baseline']-1),
                                       'feature_allowed_p95_ms_from_measured_baseline': limit,
                                       'meets_relative_target': p95['feature'] <= limit}
                state['qualified'] = state['comparison']['meets_relative_target']
        elif valid and not args.observer_diagnostic:
            # Deliberately no p95 label/qualification on a setup pilot.
            state['diagnostic_range_ms'] = {name: {'min': min(v), 'max': max(v)} for name, v in values.items()}
            state['method_pilot_passed'] = True
        state['finished'] = playback.stamp()
        write_json(args.output / 'results.json', state)
        actions.file.close()
    print(json.dumps({'results': str(args.output / 'results.json'), 'collection_valid': state['collection_valid'],
                      'qualified': state['qualified'], 'method_pilot_passed': state['method_pilot_passed'],
                      'error': state.get('collection_error')}))
    return 0 if state['qualified'] or state['method_pilot_passed'] or state.get('diagnostic_completed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
