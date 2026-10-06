#!/usr/bin/env python3
"""Bounded actual-app hover checks on detached and fullscreen timelines.

The runner uses the Story 002 RC/AX/pointer primitives, but accepts the app
bundle explicitly. It proves successful native display assignments and keeps
an owned-panel screenshot for each settled target. It is applicability evidence,
not a visible-latency or full Story 004 qualification runner.
"""
import argparse
import json
import math
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
sys.path.insert(0, str(ROOT / 'tests/story-002'))
import baseline_control_trial as control
import playback_benchmark as playback
from native_hover_trial import bundle_digest, trace_events

BUILD_MANIFEST = WORK / 'validation/story002/app-build-20261005T213341.544120Z.json'
DEFAULT_MEDIA = WORK / 'fixtures/story-002/standard-cache-pressure.mp4'
DEFAULT_DURATION = 90.037333
POINTER = WORK / 'validation/story002/native-pointer'
TRACE_WAIT_SECONDS = 20
PANEL_HEIGHT = 240


def sha256_file(path):
    return playback.digest(path)


def contained_in_work(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(WORK.resolve()) or path.is_symlink():
        raise ValueError(f'Path must be a non-symlink path beneath work/: {path}')
    return resolved


def command(args, action, *values, timeout=5):
    result = subprocess.run([str(args.pointer), action, str(args.pid), *map(str, values)],
                            capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'native-pointer {action} failed: {result.stderr}{result.stdout}')
    return result.stdout


def trace_rows(path):
    return trace_events(path)


def duration_us(trace):
    for event in trace:
        if event.get('event') == 'context' and isinstance(event.get('duration'), (int, float)):
            # Context traces store the VLC timeline duration in microseconds.
            value = int(event['duration'])
            if value > 0:
                return value
    return int(round(DEFAULT_DURATION * 1_000_000))


def matching_display(trace, hover_event):
    wanted_generation = hover_event.get('generation')
    wanted_request = hover_event.get('requested_us')
    for display in reversed(trace):
        if (display.get('event') == 'display' and bool(display.get('ok')) and
                not display.get('verification_pending') and not display.get('preparing') and
                display.get('generation') == wanted_generation and
                display.get('requested_us') == wanted_request and
                isinstance(display.get('actual_us'), int) and display['actual_us'] >= 0):
            return display
    return None


def source_fingerprint(manifest):
    data = json.loads(manifest.read_text())
    inputs = data.get('inputs_sha256', {})
    source_inputs = {}
    for relative, expected in inputs.items():
        path = ROOT / relative
        if not path.is_file():
            source_inputs[relative] = {'exists': False, 'manifest_sha256': expected}
        else:
            actual = sha256_file(path)
            source_inputs[relative] = {'sha256': actual, 'matches_manifest': actual == expected}
    return {
        'source_pin': data.get('source_pin'),
        'manifest_path': str(manifest),
        'manifest_sha256': sha256_file(manifest),
        'manifest_inputs': source_inputs,
    }


def fingerprint(app, media, runner, manifest):
    return {
        'app_path': str(app),
        'app_bundle_sha256': bundle_digest(app, sha256_file),
        'media_path': str(media),
        'media_sha256': sha256_file(media),
        'runner_path': str(runner),
        'runner_sha256': sha256_file(runner),
        'window_helper_sha256': sha256_file(WORK / 'validation/story004/native-window'),
        'window_helper_source_sha256': sha256_file(ROOT / 'tests/story-004/native-window.m'),
        'production_source': source_fingerprint(manifest),
    }


def panel_windows(pid, pointer=POINTER):
    output = subprocess.run([str(pointer), 'inspect', str(pid)], capture_output=True,
                            text=True, timeout=5)
    if output.returncode:
        raise RuntimeError('native-pointer inspect failed: ' + output.stderr)
    return [w for w in json.loads(output.stdout)
            if abs(float(w['bounds']['Height']) - PANEL_HEIGHT) < 0.1 and
            float(w['bounds']['Width']) > 336]


def slider_rect(pointer, pid, mode):
    output = subprocess.run([str(pointer), 'ax', str(pid)], capture_output=True,
                            text=True, timeout=5)
    if output.returncode:
        raise RuntimeError('native-pointer ax failed: ' + output.stderr)
    matches = [tuple(map(float, m[:4])) for m in re.findall(
        r'slider ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) value ([^ ]+) title ([^\n]*)',
        output.stdout)]
    wide = [r for r in matches if r[2] > 300]
    if not wide:
        raise RuntimeError('No wide visible timeline slider in current surface AX tree')
    if mode == 'detached':
        return max(wide, key=lambda r: r[2]), output.stdout
    return min(wide, key=lambda r: r[1]), output.stdout


def save_panel_capture(pid, out, label, pointer):
    panels = panel_windows(pid, pointer)
    if len(panels) != 1:
        raise RuntimeError(f'Expected one visible preview panel, found {len(panels)}')
    panel = panels[0]
    image = out / f'{label}.png'
    capture = subprocess.run(['/usr/sbin/screencapture', '-x', '-o', '-l',
                              str(panel['id']), str(image)], capture_output=True,
                             text=True, timeout=5)
    if capture.returncode or not image.is_file():
        raise RuntimeError('Owned preview panel capture failed: ' + capture.stderr)
    return {'window': panel, 'path': str(image), 'sha256': sha256_file(image)}


def wait_for_display(trace_path, prior_hover_count, allow_same_hover,
                     timeout=TRACE_WAIT_SECONDS):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        rows = trace_rows(trace_path)
        hovers = [e for e in rows if e.get('event') == 'hover']
        new_hovers = hovers[prior_hover_count:]
        hover_event = new_hovers[-1] if new_hovers else None
        if hover_event is None and allow_same_hover and hovers:
            # A same-bucket revisit has no new hover request. Reuse the exact
            # already-displayed sample and preserve its actual PTS.
            hover_event = hovers[-1]
        display = matching_display(rows, hover_event) if hover_event else None
        if display is not None:
            return rows, hover_event, display
        time.sleep(0.1)
    rows = trace_rows(trace_path)
    hovers = [e for e in rows if e.get('event') == 'hover']
    new_hovers = hovers[prior_hover_count:]
    hover_event = new_hovers[-1] if new_hovers else (hovers[-1] if allow_same_hover and hovers else None)
    display = matching_display(rows, hover_event) if hover_event else None
    return rows, hover_event, display


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=('detached', 'native', 'custom'))
    parser.add_argument('--media', type=Path, default=DEFAULT_MEDIA)
    parser.add_argument('--duration', type=float, default=DEFAULT_DURATION)
    parser.add_argument('--pointer', type=Path, default=POINTER)
    parser.add_argument('--build-manifest', type=Path, default=BUILD_MANIFEST,
                        help='Build manifest matching --app')
    args = parser.parse_args()

    try:
        app, media, out = map(contained_in_work, (args.app, args.media, args.output))
        pointer = contained_in_work(args.pointer)
        manifest = contained_in_work(args.build_manifest)
        if out.exists():
            raise ValueError('Output directory must be fresh')
        if not app.is_dir() or not (app / 'Contents/MacOS/VLC').is_file():
            raise ValueError('App bundle is missing Contents/MacOS/VLC')
        if not media.is_file() or not pointer.is_file():
            raise ValueError('Media and native-pointer executable must exist')
        if not manifest.is_file():
            raise ValueError('Build manifest must exist')
        if not math.isfinite(args.duration) or args.duration <= 0:
            raise ValueError('Duration must be a positive finite number')
        with (app / 'Contents/Info.plist').open('rb') as handle:
            bundle_id = plistlib.load(handle).get('CFBundleIdentifier')
        if bundle_id != control.playback.BUNDLE_ID:
            raise ValueError('Only the isolated VLC development bundle is allowed')
        out.mkdir(parents=True)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    args.app, args.media, args.output, args.pointer, args.build_manifest = app, media, out, pointer, manifest
    trace_path = out / 'timeline.jsonl'
    trace_path.touch(mode=0o600)
    state = {
        'schema_version': 1,
        'scope': 'Story 004 native surface hover applicability; not latency qualification',
        'mode': args.mode,
        'qualified': False,
        'trace_wait_seconds': TRACE_WAIT_SECONDS,
        'target_labels': ['left', 'middle', 'right', 'return-middle', 'above', 'below', 'leave', 'reenter'],
        'started': playback.stamp(),
    }
    actions = playback.Log(out / 'actions.jsonl')
    arm = None
    original_popen = subprocess.Popen
    args.pid = 0

    def traced_popen(argv, *pos, **kwargs):
        env = dict(kwargs.get('env') or os.environ)
        env['VLC_TIMELINE_DIAGNOSTICS'] = str(trace_path)
        kwargs['env'] = env
        argv = list(argv) if isinstance(argv, (list, tuple)) else argv
        if (isinstance(argv, list) and argv and argv[0].endswith('/Contents/MacOS/VLC') and
                any(str(value).startswith('--rc-unix=') for value in argv)):
            if args.mode == 'detached':
                argv.insert(-1, '--no-embedded-video')
            elif args.mode == 'native':
                argv = [('--macosx-nativefullscreenmode' if x == '--no-macosx-nativefullscreenmode' else x)
                        for x in argv]
            state['effective_argv'] = argv
        return original_popen(argv, *pos, **kwargs)

    try:
        state['before'] = fingerprint(app, media, Path(__file__).resolve(), manifest)
        args.state = state
        args.probe = WORK / 'validation/story002/control-response-probe'
        args.observer_diagnostic = True
        args.pointer = pointer
        subprocess.Popen = traced_popen
        arm = control.Arm('feature', app, args, actions)
        arm.launch()
        args.pid = arm.process.pid
        state['initial_pause'] = arm.paused()
        initial_media_time = state['initial_pause'].get('media_time_seconds')
        if state['initial_pause'].get('state') != 'pause' or initial_media_time is None:
            raise RuntimeError('App did not establish a readable paused playback state')
        command(args, 'activate')
        time.sleep(0.4)
        command(args, 'place', 42, 33, 1680, 1013)
        time.sleep(0.5)
        if args.mode != 'detached':
            arm.rc.send(['f on'])
            time.sleep(2.0)
            # Reveal from the video area, not the old main-window toolbar.
            # VLCFSPanelController.fadeIn animates for0.4s; AX exposes the
            # hidden panel too, so wait for the actual reveal before probing.
            command(args, 'move', 800, 300)
            time.sleep(0.6)

        rect, ax_text = slider_rect(pointer, arm.process.pid, args.mode)
        if args.mode == 'detached':
            # AX exposes timelines in overlapping windows. Raise the exact
            # window containing the selected slider before physical pointer input.
            selected_index = None
            for group in ax_text.split('window_index ')[1:]:
                lines = group.splitlines()
                for match in re.findall(r'slider ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) value', group):
                    if tuple(map(float, match)) == tuple(rect):
                        selected_index = int(lines[0])
            if selected_index is None:
                raise RuntimeError('Selected timeline has no owning AX window')
            raised = subprocess.run([str(WORK / 'validation/story004/native-window'), str(arm.process.pid), str(selected_index)], capture_output=True, text=True, timeout=5)
            state['selected_window_raise'] = {'returncode': raised.returncode, 'stdout': raised.stdout, 'stderr': raised.stderr}
            if raised.returncode:
                raise RuntimeError('Could not raise selected detached timeline window')
            time.sleep(.4)
            rect, ax_text = slider_rect(pointer, arm.process.pid, args.mode)
        state['timeline_rect'] = rect
        state['surface_ax'] = ax_text
        left, top, width, height = rect
        y = top + height / 2
        context_rows = trace_rows(trace_path)
        actual_duration_us = duration_us(context_rows)
        if not any(event.get('event') == 'context' for event in context_rows):
            actual_duration_us = int(round(args.duration * 1_000_000))
        state['media_duration_us'] = actual_duration_us
        state['pixel_time_resolution_us'] = int(math.ceil(actual_duration_us / max(1.0, width)))
        target_points = [
            ('left', left + 2, y),
            ('middle', left + width / 2, y),
            ('right', left + width - 2, y),
            ('return-middle', left + width / 2, y),
            ('above', left + width / 2, y - 12),
            ('below', left + width / 2, y + 12),
        ]
        points_all_pass = True
        for label, x, py in target_points:
            previous_rows = trace_rows(trace_path)
            previous_hover_count = sum(1 for event in previous_rows if event.get('event') == 'hover')
            command(args, 'move', round(x), round(py))
            time.sleep(0.5)
            focus = json.loads(command(args, 'focus'))
            if not focus.get('app_active'):
                raise RuntimeError(f'App lost foreground at {label}')
            allow_same_hover = label in ('return-middle', 'above', 'below')
            point_result = {'label': label, 'point': [round(x), round(py)]}
            try:
                rows, hover_event, display = wait_for_display(
                    trace_path, previous_hover_count, allow_same_hover)
                if display is None:
                    raise RuntimeError(f'No successful trace display within {TRACE_WAIT_SECONDS}s')
                if display['actual_us'] >= actual_duration_us:
                    raise RuntimeError('Displayed sample is outside the media duration')
                panel = save_panel_capture(arm.process.pid, out, label, pointer)
                point_result.update({
                    'trace_point_x': hover_event.get('point_x'),
                    'trace_track_bounds': [hover_event.get('left'), hover_event.get('right')],
                    'trace_bucket_us': hover_event.get('bucket_us'),
                    'hover': hover_event, 'display': display, 'panel_capture': panel,
                })
            except Exception as error:
                points_all_pass = False
                point_result['error'] = f'{type(error).__name__}: {error}'
            pause = arm.paused()
            if (pause.get('state') != 'pause' or pause.get('media_time_seconds') is None or
                    abs(float(pause['media_time_seconds']) - float(initial_media_time)) > 0.02):
                raise RuntimeError(f'Playback state/time changed at {label}: {pause}')
            point_result.update(focus=focus, pause=pause)
            state.setdefault('points', []).append(point_result)

        command(args, 'move', 800, 300)
        time.sleep(0.5)
        if panel_windows(arm.process.pid):
            raise RuntimeError('Preview panel remained visible after leaving timeline')
        state['leave_hidden'] = True
        prior_rows = trace_rows(trace_path)
        prior_hover_count = sum(1 for event in prior_rows if event.get('event') == 'hover')
        command(args, 'move', round(left + width * 0.6), round(y))
        rows, hover_event, display = wait_for_display(
            trace_path, prior_hover_count, False)
        if display is None:
            raise RuntimeError(f'No successful matching image on reentry within {TRACE_WAIT_SECONDS}s')
        state['reentry'] = {
            'hover': hover_event, 'display': display,
            'panel_capture': save_panel_capture(arm.process.pid, out, 'reenter', pointer),
            'pause': arm.paused(),
        }
        state['all_point_displays_passed'] = points_all_pass
        state['completed_interactions'] = True
    except Exception as error:
        state['collection_error'] = f'{type(error).__name__}: {error}'
    finally:
        subprocess.Popen = original_popen
        if arm:
            try:
                if args.mode != 'detached' and arm.rc:
                    arm.rc.send(['f off'])
                    time.sleep(0.5)
                arm.close()
            except Exception as error:
                state['cleanup_error'] = f'{type(error).__name__}: {error}'
        state['after'] = fingerprint(app, media, Path(__file__).resolve(), manifest)
        state['integrity_unchanged'] = state['before'] == state['after']
        state['finished'] = playback.stamp()
        (out / 'results.json').write_text(json.dumps(state, indent=2) + '\n')
    print(json.dumps({key: state.get(key) for key in
                      ('completed_interactions', 'collection_error', 'leave_hidden',
                       'integrity_unchanged', 'cleanup_error')}), flush=True)
    return 0 if (state.get('completed_interactions') and state.get('all_point_displays_passed') and
                 state.get('integrity_unchanged')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
