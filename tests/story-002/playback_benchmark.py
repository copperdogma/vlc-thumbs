#!/usr/bin/env python3
"""One bounded native playback trial; paired interpretation belongs to the owner.

Run from this workspace. Build playback-capture/native-pointer first. Example:
  python3 tests/story-002/playback_benchmark.py --app work/build/vlc-arm64/VLC.app \
    --media work/fixtures/story-002/standard.mp4 --variant feature \
    --output work/validation/story002/playback-feature-001

The baseline app must already contain baseline-libmacosx_plugin.dylib. This
runner never swaps plugins, signs/builds apps, changes installed VLC or scores
the result. Optional --rect x,y,w,h supplies the global timeline rectangle;
otherwise exactly one AX slider titled Position must be discoverable. --seconds
can shorten a setup smoke; only the default 60 seconds exercises the full gate.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import socket
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = (ROOT / 'work').resolve()
BUNDLE_ID = 'org.videolan.vlc-thumbs.development'
COUNTERS = ['video decoded', 'frames displayed', 'frames lost', 'audio decoded', 'buffers played', 'buffers lost']
OBSERVER_FINISH_GRACE_S = 20


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def owned(path):
    path = Path(path).resolve()
    if not path.is_relative_to(WORK) or path == WORK:
        raise ValueError(f'Path must resolve beneath workspace work/: {path}')
    return path


def stamp():
    return {'unix_s': time.time(), 'monotonic_s': time.monotonic()}


class Log:
    def __init__(self, path):
        self.file = path.open('x')
        self.lock = threading.Lock()

    def add(self, event):
        with self.lock:
            self.file.write(json.dumps({**stamp(), **event}, allow_nan=False) + '\n')
            self.file.flush()


class RC:
    def __init__(self, sock, log):
        self.sock, self.log = sock, log
        self.lock = threading.Lock()
        self.send_lock = threading.Lock()
        self.stop = threading.Event()
        self.state = None
        self.elapsed = None
        self.states, self.snapshots = [], []
        self.last_stats = {}
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def send(self, commands):
        self.log.add({'kind': 'command', 'commands': commands})
        with self.send_lock:
            self.sock.sendall(('\n'.join(commands) + '\n').encode())

    def read(self):
        pending = ''
        current = {}
        while not self.stop.is_set():
            try:
                data = self.sock.recv(65536)
                if not data:
                    break
            except socket.timeout:
                continue
            except OSError:
                break
            pending += data.decode('utf-8', errors='replace')
            while '\n' in pending:
                line, pending = pending.split('\n', 1)
                line = line.strip().lstrip('> ').strip()
                self.log.add({'kind': 'reply', 'line': line})
                with self.lock:
                    state = re.search(r'\( (play|pause|stop) state: (\d+)', line)
                    if state:
                        self.state = state.group(1)
                        self.states.append({**stamp(), 'state': self.state, 'raw_state': int(state.group(2))})
                    if re.fullmatch(r'\d+', line):
                        self.elapsed = int(line)  # This runner requests get_time, never get_length.
                    if 'begin of statistical info' in line:
                        current = {}
                    match = re.search(r'\|\s*(video decoded|frames displayed|frames lost|audio decoded|buffers played|buffers lost)\s*:\s*(\d+)', line)
                    if match:
                        current[match.group(1)] = int(match.group(2))
                    if 'end of statistical info' in line:
                        self.last_stats = dict(current)
                        self.snapshots.append({**stamp(), 'media_time_seconds': self.elapsed, 'counters': dict(current)})

    def snapshot(self):
        with self.lock:
            return {'state': self.state, 'media_time_seconds': self.elapsed, 'counters': dict(self.last_stats)}


def cpu_seconds(value):
    days = 0
    if '-' in value:
        day, value = value.split('-', 1); days = int(day)
    parts = [float(x) for x in value.split(':')]
    return days * 86400 + sum(n * 60 ** i for i, n in enumerate(reversed(parts)))


def resources(app, capture_pid, stop, log):
    """Sample the exact app, its current descendants and observer; no peak claims."""
    previous = None
    while not stop.is_set():
        begin = time.monotonic()
        try:
            result = subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,%cpu=,rss=,time=,comm='], capture_output=True, text=True, timeout=2)
            rows = {}
            for line in result.stdout.splitlines():
                fields = line.split(None, 5)
                if len(fields) != 6:
                    continue
                pid, ppid, cpu, rss, used, command = fields
                rows[int(pid)] = {'pid': int(pid), 'ppid': int(ppid), 'cpu_percent': float(cpu),
                                  'rss_kib': int(rss), 'cumulative_cpu_s': cpu_seconds(used), 'command': command}
            selected = {app.pid}
            for _ in range(8):
                added = {pid for pid, row in rows.items() if row['ppid'] in selected}
                if added <= selected:
                    break
                selected |= added
            selected.update(pid for pid in list(capture_pid) if pid)
            now = time.monotonic()
            log.add({'kind': 'sample', 'spacing_s': None if previous is None else begin - previous,
                     'sample_cost_s': now - begin, 'system_load': os.getloadavg(),
                     'processes': [rows[pid] for pid in sorted(selected) if pid in rows],
                     'ps_exit_code': result.returncode})
            previous = begin
        except Exception as error:
            log.add({'kind': 'sample_error', 'message': str(error)})
        stop.wait(max(0, 0.1 - (time.monotonic() - begin)))


def command(tool, arguments):
    result = subprocess.run([str(tool), *map(str, arguments)], capture_output=True, text=True, timeout=5)
    if result.returncode:
        raise RuntimeError(f'{tool.name} failed ({result.returncode}): {result.stderr} {result.stdout}')
    return result.stdout


def slider_rect(pointer, pid):
    output = command(pointer, ['ax', pid])
    found = []
    for line in output.splitlines():
        if not line.endswith('title Position'):
            continue
        match = re.match(r'slider ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+) ', line)
        if match:
            found.append(tuple(map(float, match.groups())))
    if len(found) != 1:
        raise RuntimeError(f'Expected one AX Position slider, found {len(found)}; provide --rect. AX output: {output}')
    return found[0], output


def paused_zero(rc, actions, timeout=8):
    """Establish current paused zero twice; do not accept historical pause events.

    oldrc rejects seek while paused. Resume a nonzero paused input first, then
    queue seek-zero and pause while playing. Numeric event values are logged
    verbatim: playlist and input enums differ, so state comes from event words.
    """
    deadline = time.monotonic() + timeout
    stable = 0
    control_pending_until = 0
    while time.monotonic() < deadline:
        rc.send(['get_time', 'stats', 'status'])
        time.sleep(0.25)
        snapshot = rc.snapshot()
        if snapshot['state'] == 'pause' and snapshot['media_time_seconds'] == 0 and all(k in snapshot['counters'] for k in COUNTERS):
            stable += 1
            if stable >= 2:
                actions.add({'kind': 'paused_zero_stable', 'snapshot': snapshot, 'consecutive_observations': stable})
                return snapshot
            continue
        stable = 0
        if time.monotonic() < control_pending_until:
            continue
        if snapshot['state'] == 'play' and snapshot['media_time_seconds'] is not None:
            actions.add({'kind': 'prepare_seek_zero_then_pause', 'prior': snapshot})
            rc.send(['seek 0', 'pause'])
            control_pending_until = time.monotonic() + 0.75
        elif snapshot['state'] == 'pause' and snapshot['media_time_seconds'] is not None:
            actions.add({'kind': 'prepare_resume_nonzero_pause', 'prior': snapshot})
            rc.send(['pause'])
            control_pending_until = time.monotonic() + 0.5
    raise RuntimeError(f'Cannot establish stable current paused time-zero input: {rc.snapshot()}')


def pointer_sweep(tool, pid, rect, start, seconds, stop, log):
    # Identical 750ms deterministic settled-hover schedule in both variants.
    index = 0
    while not stop.is_set():
        due = start + 0.25 + index * 0.75
        if due >= start + seconds:
            break
        if stop.wait(max(0, due - time.monotonic())):
            break
        fraction = 0.03 + 0.94 * ((index * 37) % 100) / 99
        x, y = rect[0] + rect[2] * fraction, rect[1] + rect[3] / 2
        try:
            output = command(tool, ['move', pid, x, y])
            log.add({'kind': 'move', 'index': index, 'scheduled_relative_s': due - start,
                     'requested': [x, y], 'actual': json.loads(output), 'late_by_s': max(0, time.monotonic() - due)})
        except Exception as error:
            log.add({'kind': 'move_error', 'index': index, 'message': str(error)})
            stop.set()
            break
        index += 1


def display_capture_loop(probe, pointer, pid, window, screen_file, stop, result, out):
    """Finite actual display-space counter observations; no inferred capture PTS."""
    try:
        first = next(json.loads(line) for line in screen_file.read_text().splitlines()
                     if json.loads(line).get('kind') == 'frame' and 'roi_pixels' in json.loads(line))
        px, py, pw, ph = first['roi_pixels']; bw, bh = first['buffer_size']; bounds = window['bounds']
        rect = [bounds['X'] + px / bw * bounds['Width'], bounds['Y'] + py / bh * bounds['Height'],
                pw / bw * bounds['Width'], ph / bh * bounds['Height']]
        out.mkdir()
        result.update(rect_screen_points=rect, window=window, probe_sha256=digest(probe),
                      reference_window_frame=first, batches=[], errors=[], scope='Actual display rectangle matching window-stream burned-counter ROI. Each capture has request/callback interval, no invented PTS; overhead retained.')
        for index in range(60):  # Finite cap even if caller's stop signal fails.
            if stop.is_set():
                break
            focus = json.loads(command(pointer, ['focus', pid]))
            windows = json.loads(command(pointer, ['inspect', pid]))
            current = next((w for w in windows if w['id'] == window['id']), None)
            if not focus.get('app_active') or not current or current['bounds'] != bounds:
                raise RuntimeError('Display observer lost active owned app or fixed window geometry')
            argv = [str(probe), '--rect', ','.join(map(str, rect)), '--count', '100', '--output', str(out / f'batch-{index:03}.jsonl')]
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=5)
            result['batches'].append({'index': index, 'argv': argv, 'focus': focus,
                                      'returncode': completed.returncode, 'stderr': completed.stderr})
            if completed.returncode:
                raise RuntimeError('Display capture failed: ' + completed.stderr)
        result['finished'] = stamp()
    except Exception as error:
        result.setdefault('errors', []).append(str(error))
        stop.set()


def terminate(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=5)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--app', required=True, type=Path)
    ap.add_argument('--media', required=True, type=Path)
    ap.add_argument('--variant', required=True, choices=['baseline', 'feature'])
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--rect', help='Global timeline rectangle x,y,width,height; default unique AX Position slider')
    ap.add_argument('--roi', default='0.2,0.15,0.6,0.35', help='Normalized upper-video capture ROI')
    ap.add_argument('--seconds', type=float, default=60, help='Active trial duration (0,60]; shorter is only a smoke')
    ap.add_argument('--observer', type=Path, default=WORK / 'validation/story002/playback-capture')
    ap.add_argument('--pointer', type=Path, default=WORK / 'validation/story002/native-pointer')
    ap.add_argument('--no-timeline-diagnostics', action='store_true', help='Measure the production path without opt-in feature tracing; qualify hover separately')
    ap.add_argument('--window-geometry', help='Owned focused window AX x,y,width,height before measurement; actual geometry is recorded')
    ap.add_argument('--display-probe', type=Path, help='Owned actual display-space screenshot probe; supplementary strict-stall evidence')
    ap.add_argument('--display-stream', action='store_true', help='Supplement window/audio stream with qualified continuous owned-display crop')
    ap.add_argument('--owned-display-audio', action='store_true', help='Single display crop and owned-app audio stream; qualified separately')
    args = ap.parse_args()
    if args.owned_display_audio and (args.display_stream or args.display_probe):
        ap.error('Single owned display/audio observer cannot be combined with another display observer')
    if args.display_stream and args.display_probe:
        ap.error('Select one supplementary display observer')
    if not math.isfinite(args.seconds) or not 0 < args.seconds <= 60:
        ap.error('--seconds must be in (0,60]')
    try:
        roi = tuple(map(float, args.roi.split(',')))
        if len(roi) != 4 or not all(math.isfinite(n) and n >= 0 for n in roi) or min(roi[2:]) <= 0 or roi[0] + roi[2] > 1 or roi[1] + roi[3] > 1:
            raise ValueError()
    except ValueError:
        ap.error('Invalid normalized --roi')
    app, media, out = map(owned, [args.app, args.media, args.output])
    observer, pointer = map(owned, [args.observer, args.pointer])
    with (app / 'Contents/Info.plist').open('rb') as f:
        info = plistlib.load(f)
    if info.get('CFBundleIdentifier') != BUNDLE_ID:
        ap.error('Only the isolated development VLC bundle is allowed')
    executable = app / 'Contents/MacOS' / info.get('CFBundleExecutable', 'VLC')
    plugin = app / 'Contents/MacOS/plugins/libmacosx_plugin.dylib'
    baseline = WORK / 'validation/story002/baseline-libmacosx_plugin.dylib'
    if args.variant == 'baseline' and digest(plugin) != digest(baseline):
        ap.error('Baseline app native plugin does not match the saved baseline plugin; runner never swaps it')
    if out.exists():
        ap.error('Use a fresh output directory')
    for path in [executable, observer, pointer, media]:
        if not path.is_file():
            ap.error(f'Missing input: {path}')
    rect = None
    if args.rect:
        try:
            rect = tuple(map(float, args.rect.split(',')))
            if len(rect) != 4 or not all(math.isfinite(n) for n in rect) or min(rect[2:]) <= 0:
                raise ValueError()
        except ValueError:
            ap.error('Invalid --rect')
    out.mkdir(parents=True)
    actions, rc_log, resource_log, pointer_log = [Log(out / name) for name in ['actions.jsonl', 'rc.jsonl', 'resources.jsonl', 'pointer.jsonl']]
    before_hash = digest(media)
    binaries = {str(path.relative_to(WORK)): digest(path) for path in [executable, plugin, observer, pointer]}
    historic = ROOT / 'docs/evidence/story-001/build-attempt-009/verification.json'
    baseline_provenance = {'historic_manifest': str(historic.relative_to(ROOT)), 'manifest_sha256': digest(historic),
                           'historic_result': json.loads(historic.read_text()),
                           'saved_plugin_sha256': digest(baseline),
                           'scope': 'Historic manifest pins baseline build source; it contains no saved-plugin hash. Current saved-plugin producer identity must be independently established.'}
    state = {'schema': 1, 'variant': args.variant, 'app': str(app), 'media': str(media),
             'source_sha256_before': before_hash, 'binary_sha256': binaries,
             'requested_playback_s': args.seconds, 'baseline_provenance': baseline_provenance,
             'observer_finish_grace_s': OBSERVER_FINISH_GRACE_S,
             'timeline_diagnostics_enabled': not args.no_timeline_diagnostics,
             'observer_load': 'Same observer, 640px longest raster edge and 30fps, applied to both variants. Opt-in diagnostics setting recorded separately; resource sampling can miss short helper lifetimes/peaks.',
             'scope': 'One native trial, no pass claim. CPU/RSS are sampled; gaps require attribution. Source hashes do not qualify audio, controls or feature exposure.'}
    app_process = capture = rc = None
    socket_path = Path(f'/tmp/vlc002-{os.getpid()}.sock')
    if socket_path.exists():
        raise RuntimeError(f'Refusing existing socket {socket_path}')
    stop_resources, stop_pointer, stop_display = threading.Event(), threading.Event(), threading.Event()
    capture_pid = [None]
    worker_threads = []
    try:
        env = os.environ.copy()
        if args.no_timeline_diagnostics:
            env.pop('VLC_TIMELINE_DIAGNOSTICS', None)
        else:
            env['VLC_TIMELINE_DIAGNOSTICS'] = str(out / 'timeline.jsonl')
        argv = [str(executable), '--ignore-config', f'--config={out / "vlcrc"}', '--intf=macosx', '--extraintf=oldrc',
                f'--rc-unix={socket_path}', '--rc-fake-tty', '--stats', '--play-and-pause', '--start-time=0',
                '--no-media-library',
                '--no-metadata-network-access', '--macosx-control-itunes=0', '--no-macosx-mediakeys',
                '--no-macosx-recentitems', '--macosx-continue-playback=2', '--no-video-title-show',
                '--no-loop', '--no-repeat', '--no-random', '--verbose=2', str(media)]
        # one-instance flags are guarded by _WIN32/HAVE_DBUS/__OS2__ in pinned
        # libvlc-module.c, so this macOS build does not declare them. Check every
        # remaining flag against this exact app's compiled help before GUI launch.
        # oldrc.c checks isatty(0) before opening rc-unix; rc-fake-tty is necessary
        # with this runner's DEVNULL stdin even though commands use a Unix socket.
        help_result = subprocess.run([str(executable), '--longhelp', '--advanced', '--help-verbose'],
                                     capture_output=True, text=True, timeout=10, env=env)
        (out / 'compiled-options.txt').write_text(help_result.stdout)
        (out / 'compiled-options.stderr').write_text(help_result.stderr)
        declared = set(re.findall(r'--([a-z][a-z0-9-]*)', help_result.stdout))
        requested = [arg[2:].split('=', 1)[0] for arg in argv[1:] if arg.startswith('--')]
        missing = sorted(set(requested) - declared)
        state['argument_validation'] = {'method': 'Exact app compiled help; source pin confirms core/macOS declarations',
                                        'help_exit_code': help_result.returncode, 'missing_options': missing,
                                        'requested_options': requested,
                                        'preparation': 'Ordinary startup; require latest paused/time-zero state twice after explicit RC preparation. start-paused is supported but native startup overrode its transient pause in smoke003.'}
        if help_result.returncode or missing:
            raise RuntimeError(f'Compiled launch option validation failed: {missing}, exit {help_result.returncode}')
        state['app_command'] = argv
        app_process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=(out / 'app.stdout').open('xb'),
                                       stderr=(out / 'app.stderr').open('xb'), env=env)
        state['pid'] = app_process.pid
        actions.add({'kind': 'app_launch', 'pid': app_process.pid, 'argv': argv})
        sampler = threading.Thread(target=resources, args=(app_process, capture_pid, stop_resources, resource_log), daemon=True)
        sampler.start(); worker_threads.append(sampler)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        deadline = time.monotonic() + 12
        while True:
            if app_process.poll() is not None:
                raise RuntimeError(f'Native app exited before RC connection: {app_process.returncode}')
            try:
                sock.connect(str(socket_path)); break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() > deadline:
                    raise RuntimeError('RC socket startup timeout')
                time.sleep(0.1)
        sock.settimeout(0.2)
        rc = RC(sock, rc_log)
        deadline = time.monotonic() + 10
        while True:
            rc.send(['status', 'get_time', 'stats'])
            time.sleep(0.25)
            snapshot = rc.snapshot()
            if snapshot['state'] in ('play', 'pause') and snapshot['media_time_seconds'] is not None and all(k in snapshot['counters'] for k in COUNTERS):
                break
            if time.monotonic() > deadline:
                raise RuntimeError(f'Cannot establish ready input: {snapshot}')
        time.sleep(0.5)
        actions.add({'kind': 'prepare_app_activation', 'result': command(pointer, ['activate', app_process.pid])})
        time.sleep(.3)
        state['prepared_focus'] = json.loads(command(pointer, ['focus', app_process.pid]))
        if not state['prepared_focus'].get('app_active'):
            raise RuntimeError('Owned app could not become active before visible playback measurement')
        if args.window_geometry:
            geometry = tuple(map(float, args.window_geometry.split(',')))
            if len(geometry) != 4 or not all(math.isfinite(n) for n in geometry):
                raise RuntimeError('Invalid --window-geometry')
            state['requested_window_geometry'] = geometry
            actions.add({'kind': 'prepare_window_geometry', 'requested': geometry,
                         'result': command(pointer, ['place', app_process.pid, *geometry])})
            time.sleep(1)
        if rect is None:
            rect, ax = slider_rect(pointer, app_process.pid)
            state['ax_position_inventory'] = ax
        state['timeline_global_rect'] = rect
        windows = json.loads(command(pointer, ['inspect', app_process.pid]))
        candidates = [w for w in windows if w['layer'] == 0 and w['bounds']['Width'] >= 320 and w['bounds']['Height'] >= 180]
        if not candidates:
            raise RuntimeError('No eligible native window for capture')
        window = max(candidates, key=lambda w: w['bounds']['Width'] * w['bounds']['Height'])
        state['window_inventory'] = windows
        state['prepared_before_observer'] = paused_zero(rc, actions)
        capture_command = [str(observer), '--pid', str(app_process.pid), '--window-id', str(window['id']),
                           '--output', str(out / 'capture'), '--duration', str(args.seconds + 5), '--roi', args.roi]
        if args.owned_display_audio:
            capture_command.append('--owned-display-audio')
        state['capture_command'] = capture_command
        capture = subprocess.Popen(capture_command, stdout=subprocess.PIPE, stderr=(out / 'capture.stderr').open('xb'), text=True, cwd=ROOT)
        capture_pid[0] = capture.pid
        # readline has a bounded watchdog; permission/startup must not hang the trial.
        ready_lines = []
        ready_event = threading.Event()
        def read_ready():
            ready_lines.append(capture.stdout.readline()); ready_event.set()
        threading.Thread(target=read_ready, daemon=True).start()
        if not ready_event.wait(10):
            raise RuntimeError('Observer ready timeout; inspect capture.stderr/host permission')
        if not ready_lines[0]:
            raise RuntimeError('Observer exited before ready; inspect capture.stderr')
        ready = json.loads(ready_lines[0])
        if ready.get('event') != 'ready' or ready.get('pid') != app_process.pid:
            raise RuntimeError(f'Unexpected observer ready event: {ready}')
        actions.add({'kind': 'capture_ready', 'ready': ready})
        state['capture_ready'] = ready
        state['initial'] = paused_zero(rc, actions)
        if args.display_probe:
            state['display_observer'] = {}
            display_thread = threading.Thread(target=display_capture_loop, args=(owned(args.display_probe), pointer, app_process.pid, window, out / 'capture/screen.jsonl', stop_display, state['display_observer'], out / 'display-capture'), daemon=True)
            display_thread.start(); worker_threads.append(display_thread)
            display_ready_deadline = time.monotonic() + 5
            display_first = out / 'display-capture/batch-000.jsonl'
            while not display_first.exists() or display_first.stat().st_size == 0:
                if state['display_observer'].get('errors') or time.monotonic() >= display_ready_deadline:
                    raise RuntimeError('Display observer not ready before playback: ' + str(state['display_observer']))
                time.sleep(.02)
        if args.display_stream:
            from display_stream_runner import collect
            state['display_observer'] = {}
            display_thread = threading.Thread(target=collect, args=(observer, pointer, app_process.pid, window, out / 'capture/screen.jsonl', stop_display, state['display_observer'], out / 'display-stream', args.seconds, capture_pid), daemon=True)
            display_thread.start(); worker_threads.append(display_thread)
            ready_deadline = time.monotonic() + 12
            while not state['display_observer'].get('capture_ready'):
                if state['display_observer'].get('errors') or time.monotonic() >= ready_deadline:
                    raise RuntimeError('Continuous display observer not ready: ' + str(state['display_observer']))
                time.sleep(.02)
        start = time.monotonic()
        state['playback_start'] = stamp()
        rc.send(['pause'])  # Resume known initial pause; oldrc rejects seek while paused.
        actions.add({'kind': 'resume_time_zero', 'initial': state['initial']})
        sweeper = threading.Thread(target=pointer_sweep, args=(pointer, app_process.pid, rect, start, args.seconds, stop_pointer, pointer_log), daemon=True)
        sweeper.start(); worker_threads.append(sweeper)
        deadline = start + args.seconds
        active_samples = []
        next_focus_check = start
        state['active_focus_checks'] = []
        while time.monotonic() < deadline:
            if app_process.poll() is not None:
                raise RuntimeError('App exited during playback')
            if stop_pointer.is_set():
                raise RuntimeError('Real-pointer schedule failed; inspect pointer.jsonl')
            if args.owned_display_audio and time.monotonic() >= next_focus_check:
                focus = json.loads(command(pointer, ['focus', app_process.pid]))
                current = next((w for w in json.loads(command(pointer, ['inspect', app_process.pid])) if w['id'] == window['id']), None)
                state['active_focus_checks'].append({'at': stamp(), 'focus': focus, 'bounds': current['bounds'] if current else None})
                if not focus.get('app_active') or not current or current['bounds'] != window['bounds']:
                    raise RuntimeError('Single display/audio observer lost active owned app or fixed geometry')
                next_focus_check = time.monotonic() + 1
            rc.send(['get_time', 'stats', 'status'])
            time.sleep(min(0.25, max(0, deadline - time.monotonic())))
            active_samples.append({**stamp(), **rc.snapshot()})
        stop_display.set()
        stop_pointer.set(); sweeper.join(timeout=5)
        state['trial_end'] = stamp()
        # Capture final EOF-pause counters where retained; shortened smoke is not EOF proof.
        if args.seconds == 60:
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                rc.send(['get_time', 'stats', 'status']); time.sleep(0.25)
                if rc.snapshot()['state'] == 'pause':
                    break
        rc.send(['get_time', 'stats', 'status']); time.sleep(0.5)
        state['final'] = rc.snapshot()
        state['active_samples'] = active_samples
        observed_times = [sample['media_time_seconds'] for sample in active_samples if sample['media_time_seconds'] is not None]
        max_time = max(observed_times + [state['final']['media_time_seconds'] or 0], default=0)
        required_time = max(0, args.seconds - 1)
        state['playback_advance'] = {'maximum_media_time_seconds': max_time,
                                     'minimum_required_media_time_seconds': required_time,
                                     'observed_current_play_state': any(sample['state'] == 'play' for sample in active_samples),
                                     'limitation': 'RC time is whole seconds; this rejects a silent nonplaying collection but is not fine-grained seek/stall proof.'}
        with rc.lock:
            state['state_events'] = list(rc.states)
            state['stats_snapshots'] = list(rc.snapshots)
        state['observer_finish_wait_start'] = stamp()
        actions.add({'kind': 'observer_finish_wait_start', 'grace_s': OBSERVER_FINISH_GRACE_S,
                     'active_trial_already_ended': True})
        try:
            capture.wait(timeout=OBSERVER_FINISH_GRACE_S)
        except subprocess.TimeoutExpired:
            state['observer_finish_timeout'] = stamp()
            actions.add({'kind': 'observer_finish_timeout', 'grace_s': OBSERVER_FINISH_GRACE_S})
            raise RuntimeError(f'Observer did not finish within {OBSERVER_FINISH_GRACE_S}s bounded post-trial grace')
        state['observer_finish_wait_end'] = stamp()
        actions.add({'kind': 'observer_finish_wait_end', 'exit_code': capture.returncode})
        remaining = capture.stdout.read()
        (out / 'capture.stdout').write_text(ready_lines[0] + remaining)
        state['capture_exit_code'] = capture.returncode
        if capture.returncode:
            raise RuntimeError(f'Observer failed: {capture.returncode}')
        if max_time < required_time or not state['playback_advance']['observed_current_play_state']:
            raise RuntimeError(f'Active playback did not advance as required: {state["playback_advance"]}')
        if args.display_stream:
            display_thread.join(timeout=OBSERVER_FINISH_GRACE_S)
            if display_thread.is_alive() or 'finished' not in state['display_observer']:
                raise RuntimeError('Continuous display observer did not finish successfully')
        if (args.display_probe or args.display_stream) and state['display_observer'].get('errors'):
            raise RuntimeError('Display observer incomplete: ' + str(state['display_observer']['errors']))
        state['completed_collection'] = True
    except Exception as error:
        state['completed_collection'] = False
        state['collection_error'] = str(error)
        actions.add({'kind': 'collection_error', 'message': str(error)})
    finally:
        stop_pointer.set(); stop_resources.set(); stop_display.set()
        for thread in worker_threads:
            thread.join(timeout=5)
        terminate(capture)
        if rc:
            try:
                rc.send(['quit'])
            except OSError:
                pass
            rc.stop.set(); rc.sock.close(); rc.thread.join(timeout=2)
        terminate(app_process)
        if socket_path.exists():
            socket_path.unlink()
        state['app_exit_code'] = app_process.returncode if app_process else None
        state['source_sha256_after'] = digest(media)
        state['source_hash_unchanged'] = before_hash == state['source_sha256_after']
        state['finished'] = stamp()
        (out / 'summary.json').write_text(json.dumps(state, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'summary': str(out / 'summary.json'), 'completed_collection': state.get('completed_collection', False),
                          'collection_error': state.get('collection_error')}), flush=True)
    return 0 if state.get('completed_collection') else 1


if __name__ == '__main__':
    raise SystemExit(main())
