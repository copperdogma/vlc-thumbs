#!/usr/bin/env python3
"""Owned, bounded real-pointer NAS preview trial; run only with an idle desktop.

Trace endpoints describe image assignment, not compositor latency. Samples keep
timeouts/failures rather than censoring them. Media verification samples at most
1 MiB; it cannot prove unchanged bytes outside those ranges. Never hashes/copies
the complete NAS movie, clears shared caches, or modifies the video.
"""
import argparse
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/story-002'))
import baseline_control_trial as control
import native_hover_benchmark as hover
import playback_benchmark as playback

TARGETS = [1493, 3200, 6000, 4600]
WAIT_SECONDS = 40
FINGERPRINT_HELPER = ROOT / 'work/build/vlc-arm64/VLC.app/Contents/MacOS/vlc-thumbnail-helper'
POINTER = ROOT / 'work/validation/story002/native-pointer'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def file_state(path):
    s = path.stat()
    return dict(device=s.st_dev, inode=s.st_ino, size=s.st_size,
                mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)


def fingerprint(media, output, label):
    before = file_state(media)
    started = time.monotonic()
    result = subprocess.run([str(FINGERPRINT_HELPER), '--fingerprint', 'sampled',
                             '--input', str(media)], capture_output=True, timeout=20)
    (output / (label + '.stdout')).write_bytes(result.stdout)
    (output / (label + '.stderr')).write_bytes(result.stderr)
    value = json.loads(result.stdout)
    after = file_state(media)
    if result.returncode or not value.get('ok') or value.get('policy') != 'sampled':
        raise RuntimeError('Sampled media fingerprint failed: ' + label)
    if before != after:
        raise RuntimeError('Media changed during sampled verification')
    return {'stat': before, 'result': value, 'wall_ms': (time.monotonic()-started)*1000}


def freeze(app):
    files = [Path(__file__), POINTER, FINGERPRINT_HELPER,
             ROOT / 'tests/story-002/baseline_control_trial.py',
             ROOT / 'tests/story-002/native_hover_benchmark.py',
             ROOT / 'tests/story-002/native_hover_trial.py',
             ROOT / 'tests/story-002/playback_benchmark.py']
    files += sorted((ROOT / 'src/macosx').glob('VLCThumbnail*'))
    files += sorted((ROOT / 'src/macosx').glob('VLCTimeline*'))
    files += sorted((ROOT / 'src/thumbnail-helper').glob('*'))
    return {'app_tree': control.bundle_digest(app, hover.digest),
            'files': {str(p): hover.digest(p) for p in files if p.is_file()}}


def screenshot(pointer, pid, output, label):
    # Capture owned windows separately: the floating thumbnail panel is not
    # necessarily composited into a parent-window-only screenshot.
    inventory = json.loads(playback.command(pointer, ['inspect', pid]))
    windows = [w for w in inventory if w.get('layer') == 0 and
               w.get('bounds', {}).get('Width', 0) >= 100 and
               w.get('bounds', {}).get('Height', 0) >= 80]
    if not windows:
        raise RuntimeError('No owned window available for screenshot')
    images = []
    for index, window in enumerate(windows[:6]):
        image = output / f'{label}-window-{index}-{window["id"]}.png'
        subprocess.run(['/usr/sbin/screencapture', '-x', '-o',
                        '-l' + str(window['id']), str(image)], check=True, timeout=5)
        images.append({'window': window, 'path': str(image)})
    return images


def launch_with_trace(arm, trace):
    # Arm deliberately disables traces for control measurements. Scope this
    # adapter to its one executable launch; do not modify the shared old runner.
    original = subprocess.Popen
    def traced(argv, *args, **kwargs):
        if argv and argv[0] == str(arm.executable) and '--intf=macosx' in argv:
            allowed = {'PATH', 'HOME', 'USER', 'LOGNAME', 'TMPDIR', 'LANG', 'LC_CTYPE'}
            env = {k: v for k, v in kwargs.get('env', os.environ).items() if k in allowed}
            env['VLC_TIMELINE_DIAGNOSTICS'] = str(trace)
            kwargs['env'] = env
        return original(argv, *args, **kwargs)
    subprocess.Popen = traced
    try:
        arm.launch()
    finally:
        subprocess.Popen = original
    arm.state['timeline_diagnostics_enabled'] = True


def trial(arm, rect, duration, trace, label, seconds, burst=False):
    tail = hover.Tail(trace)
    row = {'label': label, 'target_seconds': seconds, 'bound_seconds': WAIT_SECONDS,
           'faults': [], 'events': [], 'input_wall': time.monotonic()}
    pid = arm.process.pid
    def move(target):
        point = [rect[0]+7+target/duration*(rect[2]-14), rect[1]+rect[3]/2]
        return {'point': point, 'receipt': json.loads(playback.command(arm.args.pointer, ['move', pid, *point]))}
    try:
        arm.paused()
        row['focus_before'] = json.loads(playback.command(arm.args.pointer, ['focus', pid]))
        current_rect, row['ax_inventory_before'] = playback.slider_rect(arm.args.pointer, pid)
        if not row['focus_before'].get('app_active') or tuple(current_rect) != tuple(rect):
            raise RuntimeError('Foreground ownership or main timeline geometry changed')
        if burst:
            row['sweep_inputs'] = [move(1493+i*(6000-1493)/11) for i in range(12)]
        # Discard only preceding records; preserve all subsequent obsolete
        # events in the raw row while refusing to score them as current.
        row['preceding_events'] = tail.read()
        row['input_wall'] = time.monotonic()
        row['input'] = move(seconds)
        deadline = row['input_wall'] + WAIT_SECONDS
        current = first = final = final_service = pending_display = None
        services = []
        while time.monotonic() < deadline and final is None:
            if arm.process.poll() is not None:
                row['faults'].append('owned-app-exited'); break
            for event in tail.read():
                row['events'].append(event)
                if event.get('event') == 'hover':
                    if abs(event.get('bucket_us', -10**12)/1e6-seconds) <= duration/(rect[2]-14)+.5:
                        current = event
                        first = final = final_service = pending_display = None
                        services = []
                    else:
                        # A superseding hover invalidates prior assignment.
                        current = None
                if not current or event.get('generation') != current.get('generation'):
                    continue
                if event.get('event') == 'service':
                    result = event.get('result', {})
                    if result.get('requested_us') == current.get('bucket_us'):
                        services.append(event)
                if (event.get('event') == 'display' and
                        event.get('requested_us') == current.get('requested_us')):
                    good = event.get('ok') and 0 <= event.get('actual_us', -1) < duration*1e6
                    if good and first is None:
                        first = event
                        if getattr(arm.args, 'capture_pending', False) and event.get('verification_pending'):
                            row['pending_window_images'] = screenshot(arm.args.pointer, pid, arm.out, label+'-checking-source')
                    if good:
                        pending_display = event
                    matching = next((s for s in reversed(services)
                                     if s.get('result', {}).get('actual_us') == event.get('actual_us')
                                     and s.get('result', {}).get('cache', 'error') == event.get('cache')), None)
                    if good and matching and not matching['result'].get('preparing') and not matching['result'].get('verification_pending'):
                        final, final_service = event, matching
            # Controller traces display before its service row; correlate both
            # after reading the batch rather than depending on event order.
            if current and pending_display:
                matching = next((s for s in reversed(services)
                    if s['result'].get('actual_us') == pending_display.get('actual_us')
                    and s['result'].get('cache') == pending_display.get('cache')
                    and not s['result'].get('preparing') and not s['result'].get('verification_pending')), None)
                if matching:
                    final, final_service = pending_display, matching
            if final is None:
                time.sleep(.01)
        row.update(hover=current, first_useful_display=first,
                   final_matching_display=final, final_service=final_service,
                   trace_parse_errors=tail.parse_errors)
        for key, event in [('first_useful_assignment_ms', first), ('final_matching_assignment_ms', final)]:
            if event and current and isinstance(event.get('monotonic'), (int, float)):
                row[key] = (event['monotonic']-current['monotonic'])*1000
        if not current: row['faults'].append('matching-hover-not-observed')
        if not first: row['faults'].append('no-useful-image-within-bound')
        if not final: row['faults'].append('no-final-matching-image-within-bound')
        row['owned_window_images'] = screenshot(arm.args.pointer, pid, arm.out, label)
        row['paused_after'] = arm.paused()
        row['focus_after'] = json.loads(playback.command(arm.args.pointer, ['focus', pid]))
        if not row['focus_after'].get('app_active'):
            row['faults'].append('foreground-ownership-lost')
    except Exception as error:
        row['faults'].append('runner-error: ' + str(error))
    finally:
        tail.handle.close()
        row['wall_ms'] = (time.monotonic()-row['input_wall'])*1000
    row['outcome'] = 'matching-image' if not row['faults'] else 'retained-failure'
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--app', type=Path, required=True)
    ap.add_argument('--media', type=Path, required=True)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--variant', choices=['baseline', 'candidate'], required=True)
    ap.add_argument('--capture-pending', action='store_true', help='Capture provisional image immediately; supplementary visual acquisition, not paired latency')
    args = ap.parse_args()
    try:
        args.app, args.output = hover.owned(args.app), hover.owned(args.output)
        media = args.media
        if not media.is_absolute() or not media.is_relative_to('/Volumes') or media.resolve() != media:
            raise ValueError('Media must be an absolute mounted /Volumes/ regular source without symlinks')
        if not stat.S_ISREG(media.lstat().st_mode): raise ValueError('Media must be regular')
        if args.output.exists() or not args.app.is_dir(): raise ValueError('Fresh output/existing owned app required')
        if not math.isfinite(args.duration) or args.duration <= 6001: raise ValueError('Duration must exceed all declared targets')
        for path in [POINTER, FINGERPRINT_HELPER]:
            hover.owned(path)
            if not path.is_file(): raise ValueError('Required owned tool missing: ' + str(path))
    except (ValueError, OSError) as error:
        ap.error(str(error))
    args.output.mkdir(parents=True)
    args.pointer = POINTER
    actions = playback.Log(args.output / 'actions.jsonl')
    state = {'variant': args.variant, 'app': str(args.app), 'media': str(media),
             'targets': TARGETS, 'rows': [], 'status': 'running',
             'scope': 'Main-window physical-pointer image-assignment trace plus owned screenshots; not compositor latency or playback qualification',
             'cache_policy': 'No shared cache clearing; actual hit/miss sources recorded, OS/NAS warmth uncontrolled',
             'pending_capture': args.capture_pending,
             'media_guard': 'Fresh sampled helper fingerprint and stat before/after; no full content identity claim'}
    arm = None
    def save(): write(args.output / 'summary.json', state)
    try:
        state['frozen_before'] = freeze(args.app)
        state['media_before'] = fingerprint(media, args.output, 'media-before')
        arm = control.Arm(args.variant, args.app, SimpleNamespace(**vars(args)), actions)
        state['arm'] = arm.state
        trace = arm.out / 'timeline.jsonl'; trace.touch(exist_ok=False)
        launch_with_trace(arm, trace)
        playback.command(args.pointer, ['activate', arm.process.pid]); time.sleep(.4)
        placement = subprocess.run([str(args.pointer), 'place', str(arm.process.pid), '42', '33', '1680', '1013'], capture_output=True, text=True, timeout=5)
        time.sleep(.5)
        rect, ax = playback.slider_rect(args.pointer, arm.process.pid)
        focus = json.loads(playback.command(args.pointer, ['focus', arm.process.pid]))
        if not focus.get('app_active') or rect[2] <= 300:
            raise RuntimeError('No owned active main timeline after setup')
        state['geometry'] = {'slider_rect': rect, 'ax_inventory': ax, 'focus': focus, 'placement_attempt': {'returncode': placement.returncode, 'stdout': placement.stdout, 'stderr': placement.stderr}, 'policy': 'Observe actual stable main timeline; a refused AX resize is recorded, no fixed observer crop depends on this geometry'}
        arm.paused()
        save()
        for index, seconds in enumerate(TARGETS*2):
            state['rows'].append(trial(arm, rect, args.duration, trace, f'settled-{index}', seconds)); save()
        state['rows'].append(trial(arm, rect, args.duration, trace, 'rapid-sweep-jump', 3200, burst=True)); save()
        state['leave_input'] = playback.command(args.pointer, ['move', arm.process.pid, rect[0], rect[1]-100])
        time.sleep(.25)
        state['rows'].append(trial(arm, rect, args.duration, trace, 'leave-reenter', 3200)); save()
        state['status'] = 'completed-with-retained-outcomes'
    except Exception as error:
        state.update(status='inconclusive', error=str(error))
    finally:
        if arm: arm.close()
        try:
            state['media_after'] = fingerprint(media, args.output, 'media-after')
            before, after = state.get('media_before', {}), state['media_after']
            state['sampled_media_unchanged'] = before.get('stat') == after['stat'] and before.get('result', {}).get('fingerprint') == after['result'].get('fingerprint')
            state['frozen_after'] = freeze(args.app)
            state['frozen_unchanged'] = state.get('frozen_before') == state['frozen_after']
            if not state['sampled_media_unchanged'] or not state['frozen_unchanged']:
                state['status'] = 'inconclusive-input-change'
        except Exception as error:
            state.update(status='inconclusive-final-guard', final_guard_error=str(error))
        save(); actions.file.close()
    print(json.dumps({'status': state['status'], 'rows': len(state['rows']), 'output': str(args.output)}))
    return 0 if state['status'] == 'completed-with-retained-outcomes' else 1


if __name__ == '__main__':
    raise SystemExit(main())
