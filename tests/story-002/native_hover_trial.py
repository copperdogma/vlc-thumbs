#!/usr/bin/env python3
"""Launch one isolated paused hover trial, calibrate, collect and clean up.

Uses the existing playback runner's guarded oldrc protocol and pointer tool.
Moves off the timeline and reopens the fixture through normal RC stop/add to
avoid startup pointer carryover. Calibration is the sole permitted hover in
the reopened generation before benchmark collection.
The bounded main-window screenshot is for separate owner inspection; collection
proceeds automatically. No installed VLC, real media store or cache is changed.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import plistlib
import re
import socket
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def bundle_digest(app, digest):
    entries = {}
    for path in sorted(app.rglob('*')):
        if path.is_symlink():
            entries[str(path.relative_to(app))] = 'symlink:' + os.readlink(path)
        elif path.is_file():
            entries[str(path.relative_to(app))] = digest(path)
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def trace_events(path):
    events = []
    with path.open('rb') as handle:
        for line in handle:
            if not line.endswith(b'\n'):
                continue  # Writer may currently be completing the last record.
            events.append(json.loads(line))
    return events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', required=True, type=Path)
    parser.add_argument('--media', required=True, type=Path)
    parser.add_argument('--duration', required=True, type=float, help='Actual container duration in seconds')
    parser.add_argument('--output', required=True, type=Path, help='Fresh ignored output directory')
    parser.add_argument('--followup-probe', type=Path, help='Optional owned bounded probe replacing the legacy per-open cache benchmark')
    parser.add_argument('--visible-observer', type=Path, help='Owned screen-space capture probe; prepare templates before a fresh generation')
    parser.add_argument('--loading-mask', type=Path, help='Owned JSON containing verified Loading state mask')
    parser.add_argument('--window-geometry', help='Controlled AX window x,y,width,height before calibration and after reopen')
    args = parser.parse_args()
    if args.followup_probe and (not args.followup_probe.resolve().is_relative_to(ROOT / 'tests') or not args.followup_probe.is_file() or args.followup_probe.is_symlink()):
        parser.error('Followup probe must be an existing regular repository test script')
    playback = module('playback_benchmark')
    hover = module('native_hover_benchmark')
    if not math.isfinite(args.duration) or args.duration <= 80.25:
        parser.error('Calibration at 80 seconds requires duration greater than 80.25 seconds')
    app, media, out = map(hover.owned, [args.app, args.media, args.output])
    pointer = hover.owned(WORK / 'validation/story002/native-pointer')
    if out.exists():
        parser.error('Use a fresh output directory')
    if not app.is_dir() or not media.is_file() or not pointer.is_file():
        parser.error('Existing owned app, media and native-pointer are required')
    with (app / 'Contents/Info.plist').open('rb') as handle:
        info = plistlib.load(handle)
    if info.get('CFBundleIdentifier') != playback.BUNDLE_ID:
        parser.error('Only the isolated development VLC bundle is allowed')
    executable = hover.owned(app / 'Contents/MacOS' / info.get('CFBundleExecutable', 'VLC'))
    plugin = hover.owned(app / 'Contents/MacOS/plugins/libmacosx_plugin.dylib')
    if any(str(executable) in line for line in subprocess.check_output(['ps', '-axo', 'command='], text=True).splitlines()):
        parser.error('The requested development app is already running; this wrapper does not stop existing apps')
    out.mkdir(parents=True)
    trace = out / 'timeline.jsonl'
    trace.touch(mode=0o600)
    actions, rc_log = playback.Log(out / 'actions.jsonl'), playback.Log(out / 'rc.jsonl')
    state = {'schema_version': 1, 'app': str(app.relative_to(ROOT)), 'media': str(media.relative_to(ROOT)),
             'duration_seconds': args.duration, 'runner_sha256': playback.digest(Path(__file__)),
             'source_sha256_before': playback.digest(media), 'app_tree_sha256_before': bundle_digest(app, playback.digest),
             'module_sha256_before': playback.digest(plugin), 'pointer_sha256': playback.digest(pointer),
             'test_module_sha256': {name: playback.digest(Path(__file__).with_name(name)) for name in ['playback_benchmark.py', 'native_hover_benchmark.py', 'visible_hover_observer.py', 'visible_capture_probe.m']},
             'scope': 'One native paused-hover collection; screenshot correspondence and threshold judgment belong to owner.'}
    process = benchmark = rc = sock = None
    stdout_handle = stderr_handle = None
    socket_path = Path(f'/tmp/vlc002-hover-{os.getpid()}.sock')
    try:
        if socket_path.exists() or socket_path.is_symlink():
            raise RuntimeError('Refusing existing socket path')
        env = dict(os.environ, VLC_TIMELINE_DIAGNOSTICS=str(trace))
        argv = [str(executable), '--ignore-config', f'--config={out / "vlcrc"}', '--intf=macosx', '--extraintf=oldrc',
                f'--rc-unix={socket_path}', '--rc-fake-tty', '--stats', '--play-and-pause', '--start-time=0',
                '--no-media-library', '--no-metadata-network-access', '--macosx-control-itunes=0',
                '--no-macosx-mediakeys', '--no-macosx-recentitems', '--macosx-continue-playback=2',
                '--no-video-title-show', '--no-loop', '--no-repeat', '--no-random', '--verbose=2', str(media)]
        help_result = subprocess.run([str(executable), '--longhelp', '--advanced', '--help-verbose'],
                                     capture_output=True, text=True, timeout=10, env=env)
        (out / 'compiled-options.txt').write_text(help_result.stdout)
        (out / 'compiled-options.stderr').write_text(help_result.stderr)
        declared = set(re.findall(r'--([a-z][a-z0-9-]*)', help_result.stdout))
        requested = [arg[2:].split('=', 1)[0] for arg in argv[1:] if arg.startswith('--')]
        missing = sorted(set(requested) - declared)
        state['argument_validation'] = {'help_exit_code': help_result.returncode, 'missing_options': missing,
                                        'requested_options': requested}
        if help_result.returncode or missing:
            raise RuntimeError('Compiled option validation failed: ' + str(missing))
        stdout_handle, stderr_handle = (out / 'app.stdout').open('xb'), (out / 'app.stderr').open('xb')
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout_handle, stderr=stderr_handle,
                                   env=env, start_new_session=True)
        state.update(pid=process.pid, app_command=argv)
        actions.add({'kind': 'app_launch', 'pid': process.pid, 'argv': argv})
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        deadline = time.monotonic() + 12
        while True:
            if process.poll() is not None:
                raise RuntimeError('App exited before RC connection')
            try:
                sock.connect(str(socket_path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() >= deadline:
                    raise RuntimeError('RC startup timeout')
                time.sleep(.1)
        sock.settimeout(.2)
        rc = playback.RC(sock, rc_log)
        state['prepared'] = playback.paused_zero(rc, actions, timeout=12)
        playback.command(pointer, ['activate', process.pid])
        time.sleep(.5)
        if args.window_geometry:
            geometry = [float(v) for v in args.window_geometry.split(',')]
            state['requested_window_geometry'] = geometry
            actions.add({'kind': 'controlled_geometry_before_calibration', 'result': playback.command(pointer, ['place', process.pid, *geometry])})
            time.sleep(.4)
        rect, inventory = playback.slider_rect(pointer, process.pid)
        state.update(timeline_global_rect=rect, ax_position_inventory=inventory)
        windows = json.loads(playback.command(pointer, ['inspect', process.pid]))
        candidates = [w for w in windows if w['layer'] == 0 and w['bounds']['Width'] >= 320 and w['bounds']['Height'] >= 180]
        if not candidates:
            raise RuntimeError('No main owned window for bounded calibration image')
        window = max(candidates, key=lambda w: w['bounds']['Width'] * w['bounds']['Height'])
        state['window_inventory'] = windows
        if args.visible_observer:
            observer_module = module('visible_hover_observer')
            observer = observer_module.Observer(process.pid, rect, args.duration, hover.owned(args.visible_observer), loading_mask=args.loading_mask)
            state['visible_templates'] = str(observer.prepare(out / 'visible-calibration').relative_to(ROOT))
        # The pointer can survive a preceding trial on the timeline and populate
        # startup caches before this runner acquires RC. Move off the timeline,
        # then reopen through ordinary VLC commands to obtain a fresh generation.
        bounds = window['bounds']
        video_center = [bounds['X'] + bounds['Width'] / 2, bounds['Y'] + bounds['Height'] * .35]
        moved = json.loads(playback.command(pointer, ['move', process.pid, *video_center]))
        actions.add({'kind': 'move_off_timeline_before_reopen', 'point': video_center, 'result': moved})
        time.sleep(.2)
        prior_hovers = [event for event in trace_events(trace) if event.get('event') == 'hover']
        prior_generations = sorted({event['generation'] for event in prior_hovers if event.get('generation')})
        state['freshness'] = {'reason': 'A pointer retained from a preceding trial can prewarm startup hover buckets.',
                              'method': 'Move onto owned video center, ordinary RC stop then add the same fixture, establish paused zero twice; no cache clearing or product test seam.',
                              'pre_reopen_hover_count': len(prior_hovers), 'pre_reopen_hover_generations': prior_generations,
                              'pointer_off_timeline': moved, 'pre_reopen_trace_offset': trace.stat().st_size}
        actions.add({'kind': 'fresh_generation_stop', 'reason': state['freshness']['reason']})
        # Pinned oldrc Playlist rejects every playlist command while paused.
        # Resume the known pause off-track before requesting ordinary stop.
        rc.send(['pause'])
        deadline = time.monotonic() + 5
        while True:
            rc.send(['status'])
            time.sleep(.2)
            if rc.snapshot()['state'] == 'play':
                break
            if time.monotonic() >= deadline:
                raise RuntimeError('Cannot confirm playing input before normal stop')
        actions.add({'kind': 'resumed_before_playlist_stop', 'snapshot': rc.snapshot()})
        rc.send(['stop'])
        deadline = time.monotonic() + 5
        while True:
            rc.send(['status'])
            time.sleep(.2)
            if rc.snapshot()['state'] == 'stop':
                break
            if time.monotonic() >= deadline:
                raise RuntimeError('Cannot confirm stopped input before normal reopen')
        state['freshness']['stopped_snapshot'] = rc.snapshot()
        reopen_command = 'add ' + media.as_uri()
        actions.add({'kind': 'fresh_generation_reopen', 'command': reopen_command, 'reason': 'Obtain uncached media generation with pointer outside timeline'})
        rc.send([reopen_command])
        state['reopened_paused'] = playback.paused_zero(rc, actions, timeout=12)
        time.sleep(.3)
        if args.window_geometry:
            actions.add({'kind': 'controlled_geometry_after_reopen', 'result': playback.command(pointer, ['place', process.pid, *geometry])})
            time.sleep(.4)
        rect, inventory = playback.slider_rect(pointer, process.pid)
        state.update(timeline_global_rect=rect, ax_position_inventory=inventory)
        state['initial'] = playback.paused_zero(rc, actions)
        if args.visible_observer and tuple(rect) != observer.rect:
            raise RuntimeError('Window geometry changed between visible calibration and fresh-generation measurement')
        tail = hover.Tail(trace)
        try:
            target = 80.1
            point = [rect[0] + 7 + target / args.duration * (rect[2] - 14), rect[1] + rect[3] / 2]
            calibration = {'target_seconds': target, 'expected_bucket_us': 80000000,
                           'expected_actual_keyframe_us': 80000000,
                           'fixture_note': 'The 90-second stream-copy derivative loops its 60-second source; at PTS 80 seconds the burnt source counter is 20 seconds. Owner inspects correspondence.',
                           'pointer_result': json.loads(playback.command(pointer, ['move', process.pid, *point]))}
            deadline = time.monotonic() + 3
            display = None
            while time.monotonic() < deadline and display is None:
                for event in tail.read():
                    if event.get('event') == 'hover' and event.get('bucket_us') == 80000000:
                        calibration['hover'] = event
                    if event.get('event') == 'display' and calibration.get('hover'):
                        h = calibration['hover']
                        if event.get('generation') == h.get('generation') and event.get('requested_us') == h.get('requested_us'):
                            if not args.followup_probe or event.get('actual_us') == 80000000:
                                display = event
                if display is None:
                    time.sleep(.01)
            calibration['display'] = display
            state['calibration'] = calibration
            if not display or not display.get('ok') or display.get('actual_us') != 80000000:
                raise RuntimeError('Calibration preview missing or unexpected keyframe; preserve traces for inspection')
            generation = calibration['hover'].get('generation')
            hovers = [event for event in trace_events(trace) if event.get('event') == 'hover' and event.get('generation') == generation]
            contaminated = [event for event in hovers if event.get('bucket_us') != 80000000]
            bank_hovers = [event for event in hovers if 0 <= event.get('bucket_us', -1) <= 49500000]
            state['freshness'].update(generation=generation, calibration_generation_is_new=generation not in prior_generations,
                                       generation_hover_count_before_benchmark=len(hovers),
                                       unexpected_generation_hovers=contaminated, miss_bank_hovers_before_benchmark=bank_hovers)
            if not generation or generation in prior_generations or contaminated or bank_hovers:
                raise RuntimeError('Reopened generation was already hovered outside calibration; retain trial as setup failure')
        finally:
            tail.handle.close()
        time.sleep(.25)
        bounds = window['bounds']
        region = ','.join(str(n) for n in [math.floor(bounds['X']), math.floor(bounds['Y']),
                                         math.ceil(bounds['Width']), math.ceil(bounds['Height'])])
        image = out / 'calibration-main-window.png'
        capture = ['/usr/sbin/screencapture', '-x', '-o', '-l' + str(window['id']), str(image)]
        subprocess.run(capture, check=True, capture_output=True, timeout=5)
        state['calibration_image'] = {'path': str(image.relative_to(ROOT)), 'sha256': playback.digest(image),
                                     'command': capture, 'scope': 'Main owned window rectangle only, including its displayed preview; no desktop union.'}
        state['prebenchmark'] = playback.paused_zero(rc, actions)
        benchmark_args = [sys.executable, str(args.followup_probe.resolve() if args.followup_probe else Path(__file__).with_name('native_hover_benchmark.py')),
                          '--pid', str(process.pid), '--rect', ','.join(map(str, rect)),
                          '--duration', str(args.duration), '--trace', str(trace), '--output', str(out / 'benchmark')]
        if args.visible_observer:
            benchmark_args += ['--visible-observer', str(hover.owned(args.visible_observer)), '--visible-templates', str(out / 'visible-calibration/templates.json')]
            if args.loading_mask:
                benchmark_args += ['--loading-mask', str(hover.owned(args.loading_mask))]
        state['benchmark_command'] = benchmark_args
        print(json.dumps({'ready': True, 'pid': process.pid, 'rect': rect, 'calibration_image': str(image),
                          'output': str(out)}), flush=True)
        with (out / 'benchmark.stdout').open('xb') as benchmark_out, (out / 'benchmark.stderr').open('xb') as benchmark_err:
            benchmark = subprocess.Popen(benchmark_args, stdout=benchmark_out, stderr=benchmark_err, cwd=ROOT)
            try:
                state['benchmark_exit_code'] = benchmark.wait(timeout=900)
            except subprocess.TimeoutExpired:
                raise RuntimeError('Bounded benchmark 900-second timeout')
        state['final_pause'] = playback.paused_zero(rc, actions)
        state['completed_collection'] = state['benchmark_exit_code'] == 0
        if not state['completed_collection']:
            raise RuntimeError('Benchmark recorded faults; inspect child summary and samples')
    except Exception as error:
        state['completed_collection'] = False
        state['collection_error'] = str(error)
        actions.add({'kind': 'collection_error', 'message': str(error)})
    finally:
        playback.terminate(benchmark)
        if rc:
            try:
                rc.send(['quit'])
            except OSError:
                pass
            rc.stop.set()
            rc.sock.close()
            rc.thread.join(timeout=2)
        elif sock:
            sock.close()
        playback.terminate(process)
        # Remove only the socket this runner successfully launched/owned.
        if process and socket_path.exists() and stat.S_ISSOCK(socket_path.lstat().st_mode):
            socket_path.unlink()
        for handle in [stdout_handle, stderr_handle]:
            if handle:
                handle.close()
        state['app_exit_code'] = process.returncode if process else None
        state['source_sha256_after'] = playback.digest(media)
        state['app_tree_sha256_after'] = bundle_digest(app, playback.digest)
        state['module_sha256_after'] = playback.digest(plugin)
        state['source_hash_unchanged'] = state['source_sha256_before'] == state['source_sha256_after']
        state['app_hash_unchanged'] = state['app_tree_sha256_before'] == state['app_tree_sha256_after']
        state['module_hash_unchanged'] = state['module_sha256_before'] == state['module_sha256_after']
        state['finished'] = playback.stamp()
        for log in [actions, rc_log]:
            log.file.close()
        (out / 'summary.json').write_text(json.dumps(state, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'summary': str(out / 'summary.json'), 'completed_collection': state.get('completed_collection'),
                          'collection_error': state.get('collection_error')}), flush=True)
    return 0 if state.get('completed_collection') and state['source_hash_unchanged'] and state['app_hash_unchanged'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
