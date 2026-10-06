#!/usr/bin/env python3
"""Actual-display settled hover trial in one owned native development VLC.

Example (the requested app must not already be running):
  python3 tests/story-002/continuous_hover_trial.py --app work/build/vlc-arm64/VLC.app \
    --media work/fixtures/story-002/standard-cache-pressure.mp4 \
    --duration 90.037333 --output work/validation/story002/continuous-hover-001

Prepare independent continuous-API sRGB templates in a prior media generation,
then ordinary resume/stop/add establishes a fresh generation. Every capture
stream warms BEFORE its own pointer input. Only complete, owned-panel frames
whose WindowServer display time AND presentation PTS are at/after input t0 can
qualify. Callback receipt and native NSImage assignment are diagnostic only.
No installed app, private media, cache clearing, product seam or source mutation.
--count below 100 is a method pilot: it omits disk and cannot qualify percentiles.
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
from native_hover_trial import bundle_digest, trace_events
from visible_hover_observer import VisibleHoverObserver, _hamming

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
GEOMETRY = [42, 33, 1680, 1080]
ORDER = [(37 * i) % 100 for i in range(100)]
# Cam approved these MVP thresholds on 2026-10-04 after inspecting the feature.
# Original 100ms failed cohorts remain immutable; re-scoring is recorded separately.
TARGETS_MS = {'miss': 1000, 'memory': 150, 'disk': 150}
TIME_CAPTION_TARGET_MS = 200


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def display_rows(rows):
    """Filter measurements; pre-input/idle/old-position frames stay in raw JSONL."""
    valid = []
    for row in rows:
        if row.get('error'):
            raise RuntimeError('Capture error: ' + str(row['error']))
        if row.get('kind') != 'display_frame' or row.get('frame_status') != 0:
            continue
        if not row.get('app_active') or not row.get('parent_window_contains_crop'):
            raise RuntimeError('Capture ownership/active-window guard failed')
        if not row.get('panel_rect_matches_crop'):
            continue
        t0, pts, shown = (row.get(k) for k in
                          ['input_t0_uptime_s', 'presentation_pts_seconds', 'display_time_uptime_seconds'])
        if not all(map(finite, [t0, pts, shown])) or not row.get('display_time_present') or not row.get('display_time_mach_ticks', 0):
            raise RuntimeError('Complete panel frame lacks valid input/PTS/WindowServer timestamps')
        if pts < t0 or shown < t0:
            continue
        VisibleHoverObserver._validate_row(row, 'continuous display frame')
        if row['result'].get('scale_from_336_points') != 2:
            raise RuntimeError('Continuous template requires the verified 672x448 sRGB capture scale')
        valid.append(row)
    return valid


def visible_metrics(rows, template, previous=None):
    """Return the first correct time and first correct image+time display frames.

    The helper may stop on image+time before state matches. That is a method
    failure here, never a reason to accept a later frame or weaken the gate.
    """
    valid = display_rows(rows)
    first_time = first_image = None
    for row in valid:
        result = row['result']
        distance = _hamming(result['time_mask_hex'], template['time_mask_hex'])
        nearer = not previous or previous['pointer_caption'] == template['pointer_caption'] or \
            distance < _hamming(result['time_mask_hex'], previous['time_mask_hex'])
        correct_time = distance <= 22 and nearer
        if correct_time and first_time is None:
            first_time = row
        if correct_time and result['image_sample_hash_fnv1a64'].lower() == template['opaque_image_hash']:
            first_image = row
            break
    if not first_time or not first_image:
        raise RuntimeError('No eligible complete display frame with expected image and new time caption')
    state_distance = _hamming(first_image['result']['state_mask_hex'], template['state_mask_hex'])
    if state_distance > 43:
        raise RuntimeError('First image+time frame does not show independently settled Keyframe caption')
    if previous and previous['ready_caption'] != template['ready_caption'] and \
            state_distance >= _hamming(first_image['result']['state_mask_hex'], previous['state_mask_hex']):
        raise RuntimeError('First image+time frame state caption is not nearer new than previous')
    return {'time_visible_ms': (first_time['display_time_uptime_seconds'] - first_time['input_t0_uptime_s']) * 1000,
            'image_and_time_visible_ms': (first_image['display_time_uptime_seconds'] - first_image['input_t0_uptime_s']) * 1000,
            'first_time_callback_ms_diagnostic_only': (first_time['callback_received_uptime_s'] - first_time['input_t0_uptime_s']) * 1000,
            'first_image_and_time_callback_ms_diagnostic_only': (first_image['callback_received_uptime_s'] - first_image['input_t0_uptime_s']) * 1000,
            'first_time_frame': first_time, 'first_image_and_time_frame': first_image,
            'ready_state_hamming': state_distance, 'eligible_complete_frames': len(valid)}


def metadata_record(path, media, source_sha):
    """Read a named fixture record without treating unrelated JSON as provenance."""
    def find(value):
        if isinstance(value, dict):
            name = value.get('name') or Path(value.get('path', '')).name
            if name == media.name and value.get('sha256') == source_sha:
                yield value
            for child in value.values():
                yield from find(child)
        elif isinstance(value, list):
            for child in value:
                yield from find(child)
    matches = list(find(json.loads(path.read_text())))
    if len(matches) != 1:
        raise ValueError('Metadata must contain exactly one named fixture record matching current source SHA256')
    return matches[0]


class Trial:
    def __init__(self, args, state, actions, attempts):
        self.args, self.state, self.actions, self.attempts = args, state, actions, attempts
        self.process = self.rc = self.sock = None
        self.socket_path = Path(f'/tmp/vlc002-continuous-hover-{os.getpid()}.sock')
        self.trace = args.output / 'timeline.jsonl'
        self.trace.touch(mode=0o600)
        self.rect = self.panel_y = self.generation = None
        self.templates = {}

    def pointer(self, action, *arguments):
        result = playback.command(self.args.pointer, [action, self.process.pid, *arguments])
        self.actions.add({'kind': 'pointer', 'action': action, 'arguments': arguments, 'result': result})
        return result

    def events(self):
        events = trace_events(self.trace)
        for event in events:
            if event.get('error') or event.get('event') in ('error', 'trace-error'):
                raise RuntimeError('Native trace error: ' + str(event))
            if event.get('event') == 'display' and not event.get('ok'):
                raise RuntimeError('Native trace displayed an unavailable preview')
            if event.get('event') == 'service' and not event.get('result', {}).get('ok'):
                raise RuntimeError('Native service trace returned an error')
        return events

    def geometry(self):
        self.pointer('place', *GEOMETRY)
        time.sleep(.4)
        rect, inventory = playback.slider_rect(self.args.pointer, self.process.pid)
        if self.rect is not None and tuple(rect) != tuple(self.rect):
            raise RuntimeError('Timeline geometry changed across ordinary reopen')
        self.rect = rect
        self.state.update(timeline_rect=rect, ax_inventory=inventory)

    def observe_paused(self):
        """Observe twice without seek/pause repair commands during measurement."""
        observations = []
        for _ in range(2):
            with self.rc.lock:
                prior_stats = len(self.rc.snapshots)
            reply_path = self.args.output / 'rc.jsonl'
            prior_offset = reply_path.stat().st_size
            self.rc.send(['get_time', 'stats', 'status'])
            deadline = time.monotonic() + 3
            while True:
                with self.rc.lock:
                    fresh_stats = len(self.rc.snapshots) > prior_stats
                # Pinned oldrc Playlist rejects status while paused and emits
                # this marker instead of a repeated state event (oldrc.c:1194).
                # Require the fresh marker and terminal status reply, plus a
                # fresh stats snapshot; historical state alone is insufficient.
                with reply_path.open('rb') as replies:
                    replies.seek(prior_offset)
                    fresh_replies = [json.loads(line) for line in replies.read().splitlines() if line.endswith(b'}')]
                lines = [r.get('line') for r in fresh_replies if r.get('kind') == 'reply']
                fresh = fresh_stats and "Type 'pause' to continue." in lines and 'status: returned 0 (no error)' in lines
                if fresh:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError('Fresh RC state/statistics observation timeout')
                time.sleep(.01)
            snapshot = self.rc.snapshot()
            if snapshot['state'] != 'pause' or snapshot['media_time_seconds'] != 0 or not all(k in snapshot['counters'] for k in playback.COUNTERS):
                raise RuntimeError('Hover changed paused-zero playback state: ' + str(snapshot))
            observations.append(snapshot)
        self.actions.add({'kind': 'observed_paused_zero_without_repair', 'observations': observations})
        return observations[-1]

    def reopen(self):
        self.pointer('move', 800, 300)
        time.sleep(.2)
        before = self.events()
        generations = sorted({e['generation'] for e in before if e.get('event') == 'hover' and e.get('generation')})
        record = {'prior_generations': generations, 'trace_offset_before': self.trace.stat().st_size}
        # Pinned oldrc rejects playlist stop while paused. Resume first and
        # require new state events for both transitions; do not accept history.
        for command, expected in [('pause', 'play'), ('stop', 'stop')]:
            with self.rc.lock:
                prior = len(self.rc.states)
            self.rc.send([command])
            deadline = time.monotonic() + 5
            while True:
                self.rc.send(['status'])
                time.sleep(.1)
                with self.rc.lock:
                    fresh = len(self.rc.states) > prior
                if fresh and self.rc.snapshot()['state'] == expected:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError('Cannot confirm ordinary ' + expected + ' before reopen')
            record[expected + '_snapshot'] = self.rc.snapshot()
        self.rc.send(['add ' + self.args.media.as_uri()])
        record['reopened_paused_zero'] = playback.paused_zero(self.rc, self.actions, timeout=12)
        self.geometry()
        self.state.setdefault('fresh_reopens', []).append(record)
        return generations

    def point(self, bucket):
        seconds = bucket * .5 + .1
        return [round(self.rect[0] + 7 + seconds / self.args.duration * (self.rect[2] - 14)),
                round(self.rect[1] + self.rect[3] / 2)]

    def trace_request(self, before, bucket, expected_cache=None):
        deadline = time.monotonic() + 3
        while True:
            new = self.events()[before:]
            hovers = [e for e in new if e.get('event') == 'hover']
            if len(hovers) > 1 or (hovers and hovers[0].get('bucket_us') != bucket * 500000):
                raise RuntimeError('Demand superseded, duplicate, or wrong native bucket: ' + str(hovers))
            if hovers:
                h = hovers[0]
                if self.generation and h.get('generation') != self.generation:
                    raise RuntimeError('Native media generation changed')
                services = [e for e in new if e.get('event') == 'service']
                displays = [e for e in new if e.get('event') == 'display']
                if len(services) > 1 or len(displays) > 1:
                    raise RuntimeError('Duplicate/unowned service or display trace')
                if services and displays:
                    s, d = services[0], displays[0]
                    result = s.get('result', {})
                    if s.get('generation') != h.get('generation') or d.get('generation') != h.get('generation') or \
                            result.get('requested_us') != bucket * 500000 or d.get('requested_us') != h.get('requested_us'):
                        raise RuntimeError('Trace request ownership mismatch')
                    if (result.get('width'), result.get('height'), result.get('channels'), result.get('payload_bytes')) != (320, 180, 4, 230400):
                        raise RuntimeError('Expected raw 320x180 RGBA cache-pressure output')
                    if result.get('sampling') != 'keyframe' or result.get('actual_us') != d.get('actual_us'):
                        raise RuntimeError('Native service/display keyframe disagreement')
                    if expected_cache and (result.get('cache') != expected_cache or d.get('cache') != expected_cache):
                        raise RuntimeError('Cache mismatch: expected ' + expected_cache + ', got ' + str([result.get('cache'), d.get('cache')]))
                    actual = result.get('actual_us')
                    if not finite(actual) or actual < 0 or actual >= h.get('duration_us', 0) or \
                            actual > h.get('requested_us', -1) or h['requested_us'] - actual > 2100000:
                        raise RuntimeError('Standard fixture keyframe is invalid, after the pointer, or outside its verified two-second GOP bound')
                    # The scored bank lies before the60s stream-copy boundary.
                    # Later derivative timestamps can carry the loop's offset;
                    # do not pretend they equal exact even integer seconds.
                    if bucket < 100 and actual != (bucket // 4) * 2000000:
                        raise RuntimeError('Scored standard fixture keyframe timestamp mismatch')
                    return {'hover': h, 'service': s, 'display': d, 'events': new}
            if time.monotonic() >= deadline:
                raise RuntimeError('Settled native hover/service/display trace timeout')
            time.sleep(.01)

    def calibrate(self, label):
        # Bucket160 (80.1s) lies outside both the100 target bank and50pressure.
        before = len(self.events())
        self.pointer('move', *self.point(160))
        evidence = self.trace_request(before, 160, 'miss')
        self.generation = evidence['hover']['generation']
        windows = json.loads(self.pointer('inspect'))
        panels = [w for w in windows if w['layer'] in (3, 9) and
                  w['bounds']['Width'] == 336 and w['bounds']['Height'] == 224]
        if len(panels) != 1:
            raise RuntimeError('Exactly one owned 336x224 preview panel required')
        if self.panel_y is not None and self.panel_y != panels[0]['bounds']['Y']:
            raise RuntimeError('Preview vertical geometry changed after reopen')
        self.panel_y = panels[0]['bounds']['Y']
        self.state.setdefault('calibrations', []).append({'label': label, **evidence, 'panel': panels[0]})
        return evidence

    def capture(self, record, bucket, *, settle=False, template=None, previous=None, existing_trace=None):
        path = self.args.output / (record['name'] + '.jsonl')
        png = self.args.output / (record['name'] + '.png')
        point = self.point(bucket)
        crop = [point[0] - 168, self.panel_y, 336, 224]
        argv = [str(self.args.probe), '--pid', str(self.process.pid), '--rect', ','.join(map(str, crop)),
                '--point', ','.join(map(str, point)), '--output', str(path), '--save-last-image', str(png)]
        if settle:
            argv += ['--settle-ms', '1000']
        else:
            argv += ['--expected-hash', template['opaque_image_hash'], '--expected-time-mask', template['time_mask_hex']]
            if previous and previous['pointer_caption'] != template['pointer_caption']:
                argv += ['--previous-time-mask', previous['time_mask_hex']]
        record.update(command=argv, raw_jsonl=str(path), last_image=str(png), pointer_target=point, crop=crop)
        before = len(self.events())
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=12)
            record.update(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        except subprocess.TimeoutExpired as error:
            record.update(timed_out=True, stdout=str(error.stdout or ''), stderr=str(error.stderr or ''))
            raise RuntimeError('Continuous capture process timeout') from error
        rows = []
        if path.is_file():
            for number, line in enumerate(path.read_text().splitlines(), 1):
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise RuntimeError('Non-object capture JSON at line ' + str(number))
                rows.append(row)
        record['raw_row_count'] = len(rows)
        valid = display_rows(rows)  # ANY reported capture error invalidates it.
        if completed.returncode or completed.stdout.strip() or completed.stderr.strip() or not png.is_file():
            raise RuntimeError('Continuous capture returned an error/output or omitted its retained PNG')
        record['trace'] = existing_trace or self.trace_request(before, bucket, None if settle else record['expected_cache'])
        if existing_trace:
            # Calibration remains the same demand: another pointer move to
            # its identical point must not invent a second service request.
            unexpected = [e for e in self.events()[before:] if e.get('event') in ('hover', 'service', 'display')]
            if unexpected:
                raise RuntimeError('Repeated settled calibration unexpectedly generated another demand')
        if not valid:
            raise RuntimeError('No complete eligible owned panel display frames')
        return rows, valid

    def attempt(self, phase, bucket, previous=None, existing_trace=None):
        record = {'phase': phase, 'bucket': bucket, 'bucket_us': bucket * 500000,
                  'target_seconds': bucket * .5 + .1, 'name': f'{phase}-{bucket:03}', 'faults': []}
        started = time.monotonic()
        try:
            if phase == 'template':
                rows, valid = self.capture(record, bucket, settle=True, existing_trace=existing_trace)
                if len(valid) < 3:
                    raise RuntimeError('Template has fewer than three eligible complete frames')
                tail = [VisibleHoverObserver._validate_row(r, 'template tail') for r in valid[-3:]]
                if any(r[:3] != tail[-1][:3] for r in tail) or min(tail[-1][3:]) <= 0:
                    raise RuntimeError('Final three opaque image/time/keyframe caption samples are unstable or empty')
                image, time_mask, state_mask, tg, sg = tail[-1]
                evidence = record['trace']
                template = {'bucket': bucket, 'opaque_image_hash': image, 'time_mask_hex': time_mask,
                            'state_mask_hex': state_mask, 'time_glyph_count': tg, 'state_glyph_count': sg,
                            'pointer_caption': f'{int(evidence["hover"]["requested_us"]) // 60000000:02}:{int(evidence["hover"]["requested_us"]) // 1000000 % 60:02}',
                            'actual_keyframe_us': evidence['display']['actual_us'],
                            'ready_caption': f'Keyframe {evidence["display"]["actual_us"] // 60000000}:{evidence["display"]["actual_us"] // 1000000 % 60:02}',
                            'prior_generation': evidence['hover']['generation'], 'stable_final_samples': 3,
                            'reference_frame': valid[-1], 'raw_jsonl': record['raw_jsonl']}
                self.templates[str(bucket)] = template
                record['template'] = template
            else:
                record['expected_cache'] = 'miss' if phase == 'pressure-seed' else phase
                if phase == 'pressure-seed' and bucket != 149:
                    before = len(self.events())
                    self.pointer('move', *self.point(bucket))
                    record['trace'] = self.trace_request(before, bucket, 'miss')
                else:
                    template = self.templates[str(bucket)]
                    rows, valid = self.capture(record, bucket, template=template, previous=previous)
                    record['visible'] = visible_metrics(rows, template, previous)
                    if record['trace']['display']['actual_us'] != template['actual_keyframe_us']:
                        raise RuntimeError('Actual keyframe differs from independently captured template')
                record['paused_snapshot'] = self.observe_paused()
                current, inventory = playback.slider_rect(self.args.pointer, self.process.pid)
                if tuple(current) != tuple(self.rect):
                    raise RuntimeError('Timeline geometry changed during measurement')
                positions = [float(line.split(' value ')[1].split(' title ')[0]) for line in inventory.splitlines()
                             if line.endswith('title Position') and ' value ' in line]
                if positions != [self.state['initial_ax_position']]:
                    raise RuntimeError('Hover changed paused AX Position')
                record['ax_position'] = positions[0]
        except Exception as error:
            record['faults'].append(str(error))
            raise
        finally:
            record['wall_ms'] = (time.monotonic() - started) * 1000
            self.state['attempts'].append(record)
            self.attempts.add(record)
            print(json.dumps({'phase': phase, 'bucket': bucket, 'faults': record['faults'],
                              'image_and_time_visible_ms': record.get('visible', {}).get('image_and_time_visible_ms')}), flush=True)


def phase_summary(records, phase):
    rows = [r for r in records if r['phase'] == phase]
    faults = sum(bool(r['faults']) for r in rows)
    images = [r['visible']['image_and_time_visible_ms'] for r in rows if r.get('visible')]
    times = [r['visible']['time_visible_ms'] for r in rows if r.get('visible')]
    eligible = len(rows) >= 100 and len(images) == len(times) == len(rows) and not faults
    p95_image, p95_time = hover.percentile(images, .95), hover.percentile(times, .95)
    return {'attempts': len(rows), 'faulted_attempts': faults, 'visible_image_and_time_count': len(images),
            'time_caption_count': len(times), 'percentile_qualification_eligible': eligible,
            'image_and_time_p95_ms': p95_image if eligible else None, 'time_caption_p95_ms': p95_time if eligible else None,
            'available_image_and_time_p95_ms_diagnostic_only': p95_image,
            'available_time_caption_p95_ms_diagnostic_only': p95_time,
            'image_and_time_target_ms': TARGETS_MS[phase], 'time_caption_target_ms': TIME_CAPTION_TARGET_MS,
            'meets_targets': eligible and p95_image <= TARGETS_MS[phase] and p95_time <= TIME_CAPTION_TARGET_MS}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--app', required=True, type=Path)
    parser.add_argument('--media', required=True, type=Path)
    parser.add_argument('--duration', type=float, help='Actual container duration; e.g.90.037333 MP4/90.037 MKV')
    parser.add_argument('--media-json', type=Path, help='Owned JSON with named source-SHA and probe.format.duration')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--probe', type=Path, default=WORK / 'validation/story002/continuous-visible-capture-probe')
    parser.add_argument('--pointer', type=Path, default=WORK / 'validation/story002/native-pointer')
    parser.add_argument('--count', type=int, default=100, help='1..100; below100 is method pilot with disk omitted')
    args = parser.parse_args()
    try:
        for name in ['app', 'media', 'output', 'probe', 'pointer']:
            setattr(args, name, hover.owned(getattr(args, name)))
        if args.output.exists() or args.output.is_symlink():
            raise ValueError('A fresh output directory is required')
        if not 1 <= args.count <= 100:
            raise ValueError('--count must be1..100')
        if args.media.parent != WORK / 'fixtures/story-002' or args.media.name not in ['standard-cache-pressure.mp4', 'standard-cache-pressure.mkv']:
            raise ValueError('Only generated standard-cache-pressure MP4/MKV fixtures are allowed; no private media')
        if not args.app.is_dir() or not args.media.is_file() or not all(p.is_file() and os.access(p, os.X_OK) for p in [args.pointer, args.probe]):
            raise ValueError('Existing owned app, standard fixture and executable pointer/probe required')
        with (args.app / 'Contents/Info.plist').open('rb') as handle:
            info = plistlib.load(handle)
        if info.get('CFBundleIdentifier') != playback.BUNDLE_ID:
            raise ValueError('Only the isolated development VLC bundle is allowed')
        executable = hover.owned(args.app / 'Contents/MacOS' / info.get('CFBundleExecutable', 'VLC'))
        plugin = hover.owned(args.app / 'Contents/MacOS/plugins/libmacosx_plugin.dylib')
        if any(str(executable) in line for line in subprocess.check_output(['ps', '-axo', 'command='], text=True).splitlines()):
            raise ValueError('Requested development app already running; existing apps are never stopped')
        source_sha = playback.digest(args.media)
        record = None
        if args.media_json:
            args.media_json = hover.owned(args.media_json)
            record = metadata_record(args.media_json, args.media, source_sha)
        else:
            for candidate in [WORK / 'validation/story002/cache-pressure-regeneration-1931.json',
                              WORK / 'validation/story002/cache-pressure-fixtures.json']:
                if candidate.is_file():
                    try:
                        candidate_record = metadata_record(candidate, args.media, source_sha)
                        if args.duration is None and not candidate_record.get('probe', {}).get('format', {}).get('duration'):
                            continue  # A source-only regeneration record cannot supply a duration.
                        record = candidate_record
                        args.media_json = candidate
                        break
                    except ValueError:
                        continue
            if record is None:
                raise ValueError('Source must match generated-fixture metadata; supply explicit --duration for source-only regeneration records')
        metadata_duration = float(record.get('probe', {}).get('format', {}).get('duration', record.get('duration_seconds', 0))) if record else None
        if args.duration is None:
            args.duration = metadata_duration
        if not finite(args.duration) or args.duration <= 80.25 or args.duration > 91:
            raise ValueError('Declared standard fixture container duration must cover80.1s and be <=91s')
        if metadata_duration and abs(args.duration - metadata_duration) > .05:
            raise ValueError('Explicit duration disagrees with verified metadata')
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.output.mkdir(parents=True)
    actions, attempts, rc_log = [playback.Log(args.output / name) for name in ['actions.jsonl', 'attempts.jsonl', 'rc.jsonl']]
    state = {'schema_version': 1, 'scope': 'Main-window paused native continuous-display settled-hover standard fixture trial',
             'measurement': 'WindowServer display_time uptime minus before-pointer input t0; PTS/display>=t0; complete owned active-panel frames only; no overhead subtraction',
             'os_cache_condition': 'Uncontrolled warm OS/storage caches; templates deliberately prepared before scored generation. First-open latency is not measured.',
             'time_caption_semantics': 'Actual visible new pointer-time caption within200ms (Cam-approved MVP); no Loading claim if first eligible capture already has correct image/time/keyframe.',
             'pilot': args.count < 100, 'percentile_qualification_requested': args.count == 100,
             'duration_seconds': args.duration, 'media': str(args.media), 'app': str(args.app), 'requested_geometry': GEOMETRY,
             'media_json': str(args.media_json) if args.media_json else None,
             'media_json_sha256': playback.digest(args.media_json) if args.media_json else None,
             'source_sha256_before': source_sha, 'app_tree_sha256_before': bundle_digest(args.app, playback.digest),
             'executable_sha256': playback.digest(executable), 'module_sha256_before': playback.digest(plugin),
             'probe_sha256_before': playback.digest(args.probe), 'pointer_sha256_before': playback.digest(args.pointer),
             'runner_sha256': playback.digest(Path(__file__)), 'attempts': [],
             'test_source_sha256': {name: playback.digest(Path(__file__).with_name(name)) for name in
                                    ['continuous_visible_probe.m', 'native_hover_trial.py', 'native_hover_benchmark.py', 'playback_benchmark.py', 'visible_hover_observer.py']},
             'target_permutation': ORDER[:args.count], 'pressure_buckets': list(range(100, 150)) if args.count == 100 else [],
             'cache_condition': {'memory_bytes': 32 * 1024 * 1024, 'raw_entry_bytes': 230400,
                                 'capacity_entries': (32 * 1024 * 1024) // 230400,
                                 'method': 'Full trial:100bank then50new pressure requests; repeated permutation yields verified disk cascade. Small pilot:miss/RAM only. No cache deletion'},
             'started': playback.stamp()}
    trial = Trial(args, state, actions, attempts)
    stdout = stderr = None
    try:
        if trial.socket_path.exists() or trial.socket_path.is_symlink():
            raise RuntimeError('Refusing existing socket path')
        argv = [str(executable), '--ignore-config', f'--config={args.output / "vlcrc"}', '--intf=macosx', '--extraintf=oldrc',
                f'--rc-unix={trial.socket_path}', '--rc-fake-tty', '--stats', '--play-and-pause', '--start-time=0',
                '--no-media-library', '--no-metadata-network-access', '--macosx-control-itunes=0', '--no-macosx-mediakeys',
                '--no-macosx-recentitems', '--macosx-continue-playback=2', '--no-video-title-show', '--no-loop', '--no-repeat',
                '--no-random', '--verbose=2', str(args.media)]
        env = dict(os.environ, VLC_TIMELINE_DIAGNOSTICS=str(trial.trace))
        help_result = subprocess.run([str(executable), '--longhelp', '--advanced', '--help-verbose'], capture_output=True, text=True, timeout=10)
        (args.output / 'compiled-options.txt').write_text(help_result.stdout)
        (args.output / 'compiled-options.stderr').write_text(help_result.stderr)
        declared = set(re.findall(r'--([a-z][a-z0-9-]*)', help_result.stdout))
        missing = sorted({a[2:].split('=', 1)[0] for a in argv[1:] if a.startswith('--')} - declared)
        state['argument_validation'] = {'returncode': help_result.returncode, 'missing_options': missing}
        if help_result.returncode or missing:
            raise RuntimeError('Compiled app option validation failed')
        stdout, stderr = [(args.output / name).open('xb') for name in ['app.stdout', 'app.stderr']]
        trial.process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
        state.update(pid=trial.process.pid, app_command=argv)
        trial.sock = socket.socket(socket.AF_UNIX)
        deadline = time.monotonic() + 12
        while True:
            if trial.process.poll() is not None:
                raise RuntimeError('Owned app exited before RC connection')
            try:
                trial.sock.connect(str(trial.socket_path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() >= deadline:
                    raise RuntimeError('Owned app RC startup timeout')
                time.sleep(.1)
        trial.sock.settimeout(.2)
        trial.rc = playback.RC(trial.sock, rc_log)
        state['startup_paused'] = playback.paused_zero(trial.rc, actions, timeout=12)
        trial.pointer('activate')
        time.sleep(.4)
        trial.geometry()
        # Clear startup pointer contamination through ordinary media lifecycle.
        trial.reopen()
        calibration_reference = trial.calibrate('prior-template-generation')
        trial.attempt('template', 160, existing_trace=calibration_reference)
        # Full qualification has100 independent bank templates. A small
        # method pilot prepares only its explicitly selected targets.
        template_buckets = [*ORDER[:args.count], *([149] if args.count == 100 else [])]
        for bucket in template_buckets:
            trial.attempt('template', bucket)
        json_write(args.output / 'templates.json', {'kind': 'independent_continuous_srgb_templates', 'templates': trial.templates,
                    'timeline_rect': trial.rect, 'settle_ms': 1000, 'probe_sha256': state['probe_sha256_before']})
        trial.generation = None
        prior_generations = trial.reopen()
        calibration = trial.calibrate('fresh-scored-generation')
        hovers = [e for e in trial.events() if e.get('event') == 'hover' and e.get('generation') == trial.generation]
        state['freshness'] = {'generation': trial.generation, 'prior_generations': prior_generations, 'prebank_hovers': hovers}
        if trial.generation in prior_generations or len(hovers) != 1 or hovers[0].get('bucket_us') != 80000000:
            raise RuntimeError('Fresh scored generation has bank/pressure contamination or duplicate calibration demand')
        state['initial_rc'] = trial.observe_paused()
        _, inventory = playback.slider_rect(args.pointer, trial.process.pid)
        positions = [float(line.split(' value ')[1].split(' title ')[0]) for line in inventory.splitlines()
                     if line.endswith('title Position') and ' value ' in line]
        if len(positions) != 1:
            raise RuntimeError('Exactly one initial AX Position value required')
        state['initial_ax_position'] = positions[0]
        # A same-caption previous calibration reference isn't needed for the
        # first bank request: calibration80 is outside target0's time/image.
        previous = trial.templates['160']
        for phase in ['miss', 'memory']:
            if phase == 'memory' and args.count == 1:
                # One-target pilot otherwise never leaves its last demand,
                # so it could not produce an independent RAM request trace.
                trial.pointer('move', 800, 300)
                time.sleep(.2)
            for bucket in ORDER[:args.count]:
                trial.attempt(phase, bucket, previous)
                previous = trial.templates[str(bucket)]
        if args.count == 100:
            for bucket in range(100, 150):
                trial.attempt('pressure-seed', bucket, previous if bucket == 149 else None)
                previous = None  # Uncaptured pressure captions cannot be fabricated.
            previous = trial.templates['149']
            for bucket in ORDER:
                trial.attempt('disk', bucket, previous)
                previous = trial.templates[str(bucket)]
        state['final_rc'] = trial.observe_paused()
        state['completed_collection'] = True
    except Exception as error:
        state.update(completed_collection=False, collection_error=str(error))
        actions.add({'kind': 'collection_error', 'error': str(error)})
    finally:
        if trial.rc:
            try:
                trial.rc.send(['quit'])
            except OSError:
                pass
            trial.rc.stop.set()
            trial.rc.sock.close()
            trial.rc.thread.join(timeout=2)
        elif trial.sock:
            trial.sock.close()
        playback.terminate(trial.process)
        if trial.process and trial.socket_path.exists() and stat.S_ISSOCK(trial.socket_path.lstat().st_mode):
            trial.socket_path.unlink()
        for handle in [stdout, stderr]:
            if handle:
                handle.close()
        for field, path in [('source', args.media), ('module', plugin), ('probe', args.probe), ('pointer', args.pointer)]:
            state[field + '_sha256_after'] = playback.digest(path)
            state[field + '_unchanged'] = state[field + '_sha256_after'] == state[field + '_sha256_before']
        state['app_tree_sha256_after'] = bundle_digest(args.app, playback.digest)
        state['app_unchanged'] = state['app_tree_sha256_after'] == state['app_tree_sha256_before']
        state['phases'] = {phase: phase_summary(state['attempts'], phase) for phase in TARGETS_MS}
        integrity = all(state[k + '_unchanged'] for k in ['source', 'module', 'probe', 'pointer', 'app'])
        state['qualified'] = bool(state.get('completed_collection') and integrity and args.count == 100 and
                                  all(p['meets_targets'] for p in state['phases'].values()))
        state['method_pilot_passed'] = bool(args.count < 100 and state.get('completed_collection') and integrity)
        state['all_attempts_retained'] = True
        state['finished'] = playback.stamp()
        json_write(args.output / 'summary.json', state)
        for log in [actions, attempts, rc_log]:
            log.file.close()
        print(json.dumps({'summary': str(args.output / 'summary.json'), 'qualified': state['qualified'],
                          'method_pilot_passed': state['method_pilot_passed'], 'error': state.get('collection_error')}), flush=True)
    return 0 if state['qualified'] or state['method_pilot_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
