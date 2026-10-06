#!/usr/bin/env python3
"""Measure real settled hover presentation in an already paused development app.

The owner must launch fresh media/generation with VLC_TIMELINE_DIAGNOSTICS set
to --trace and independently calibrate the first native image. --duration is
the media duration in seconds. No app launch, seek, pause, cache clearing, fake
worker or product test seam is used. Each phase retains all 100 trial outcomes.
Miss, memory and disk targets use the fixed out-of-order permutation
bucket(i) = (37*i) mod 100. Identical ordering preserves the LRU disk cascade.
Preview timing ends at image assignment, not compositor presentation. Existing
mouse-move/hover trace timestamps provide a loading-assignment upper-bound proxy.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
POSITION = re.compile(r'^slider ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) value ([-\d.eE+]+) title Position$')


def owned(path):
    path = Path(path).absolute()
    if path.resolve() != path or not path.is_relative_to(WORK) or path == WORK:
        raise ValueError('Path must stay beneath this workspace work/ without symlinks: ' + str(path))
    return path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class Tail:
    def __init__(self, path):
        self.handle = path.open('rb')
        self.start = self.handle.seek(0, 2)
        self.buffer = b''
        self.parse_errors = 0

    def read(self):
        self.buffer += self.handle.read(1024 * 1024)
        lines = self.buffer.split(b'\n')
        self.buffer = lines.pop()
        events = []
        for line in lines:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    events.append(item)
                else:
                    self.parse_errors += 1
            except (ValueError, UnicodeDecodeError):
                self.parse_errors += 1
        return events


def percentile(values, quantile):
    return sorted(values)[math.ceil(quantile * len(values)) - 1] if values else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', required=True, type=int)
    parser.add_argument('--rect', required=True, help='Global AX timeline rectangle x,y,width,height')
    parser.add_argument('--duration', type=float, default=90, help='Media duration in seconds; default 90')
    parser.add_argument('--trace', required=True, type=Path, help='Existing app VLC_TIMELINE_DIAGNOSTICS JSONL path')
    parser.add_argument('--output', required=True, type=Path, help='Fresh ignored output directory')
    parser.add_argument('--pointer', type=Path, default=WORK / 'validation/story002/native-pointer')
    parser.add_argument('--visible-observer', type=Path)
    parser.add_argument('--visible-templates', type=Path)
    parser.add_argument('--loading-mask', type=Path)
    args = parser.parse_args()
    try:
        rect = tuple(float(n) for n in args.rect.split(','))
        if len(rect) != 4 or not all(math.isfinite(n) for n in rect) or rect[2] <= 14 or rect[3] <= 0:
            raise ValueError('Invalid rectangle')
        if not math.isfinite(args.duration) or args.duration <= 74.6 or args.pid <= 0:
            raise ValueError('Positive PID and media duration greater than 74.6 seconds required')
        trace, output, pointer = map(owned, [args.trace, args.output, args.pointer])
        if not trace.is_file() or not pointer.is_file() or output.exists():
            raise ValueError('Existing trace/pointer and fresh output directory required')
    except ValueError as error:
        parser.error(str(error))

    def command(action, *arguments):
        completed = subprocess.run([str(pointer), action, str(args.pid), *map(str, arguments)],
                                   capture_output=True, text=True, timeout=3)
        if completed.returncode:
            raise RuntimeError('Native pointer failed: ' + completed.stderr + completed.stdout)
        return completed.stdout

    def position():
        inventory = command('ax')
        matches = []
        for line in inventory.splitlines():
            match = POSITION.fullmatch(line)
            if match:
                numbers = tuple(map(float, match.groups()))
                if max(abs(numbers[i] - rect[i]) for i in range(4)) <= 1:
                    matches.append(numbers[4])
        if len(matches) != 1:
            raise RuntimeError('Exactly one Position slider must match the requested rectangle:\n' + inventory)
        return matches[0], inventory

    initial_position, initial_inventory = position()
    time.sleep(.15)
    confirmed_position, _ = position()
    if abs(initial_position - confirmed_position) > .000001:
        raise RuntimeError('App must already be paused; AX Position changed during preflight')
    output.mkdir(parents=True)
    observer = None
    if args.visible_observer:
        from visible_hover_observer import Observer
        observer = Observer(args.pid, rect, args.duration, owned(args.visible_observer), loading_mask=args.loading_mask, templates=owned(args.visible_templates))
        observer._load_templates(output)
    tail = Tail(trace)
    generation = None
    samples = []
    outcomes = (output / 'samples.jsonl').open('x')
    x, y, width, height = rect
    left, right = x + 7, x + width - 7

    def sample(phase, bucket, expected_cache):
        nonlocal generation
        target_seconds = bucket * .5 + .1
        point = (left + target_seconds / args.duration * (right - left), y + height / 2)
        record = {'phase': phase, 'bucket_us': bucket * 500000, 'target_seconds': target_seconds,
                  'pointer_target': point, 'expected_cache': expected_cache, 'faults': []}
        hover = service = display = movement = loading_start = None
        started = time.monotonic()
        try:
            # Flush records from preceding samples before issuing this move.
            tail.read()
            if observer and phase != 'pressure-seed':
                record['visible'] = observer.collect(bucket, output / ('visible-' + phase + '-' + str(bucket)), require_distinct=phase != 'pressure-seed')
                record['faults'].extend(record['visible']['faults'])
            else:
                record['pointer_result'] = json.loads(command('move', *point))
            deadline = started + 2
            while time.monotonic() < deadline and display is None:
                for event in tail.read():
                    if event.get('event') == 'mouse-move':
                        movement = event
                    elif event.get('event') == 'hover' and event.get('bucket_us') == record['bucket_us']:
                        hover = event
                        loading_start = movement
                        if generation is None:
                            generation = event.get('generation')
                        elif event.get('generation') != generation:
                            record['faults'].append('generation-changed')
                    elif event.get('event') == 'service' and hover and event.get('generation') == hover.get('generation'):
                        if event.get('result', {}).get('requested_us') == record['bucket_us']:
                            service = event
                    elif event.get('event') == 'display' and hover and event.get('generation') == hover.get('generation'):
                        if event.get('requested_us') == hover.get('requested_us'):
                            display = event
                if display is None:
                    time.sleep(.005)
            record.update(hover=hover, service=service, display=display, mouse_move_before_hover=loading_start)
            if loading_start and hover:
                begin, end = loading_start.get('monotonic'), hover.get('monotonic')
                if isinstance(begin, (int, float)) and isinstance(end, (int, float)) and end >= begin:
                    record['loading_assignment_upper_bound_proxy_ms'] = (end - begin) * 1000
            if not hover:
                record['faults'].append('hover-timeout')
            if not service:
                record['faults'].append('service-timeout')
            elif (service['result'].get('width'), service['result'].get('height')) != (320, 180):
                record['faults'].append('cache-pressure-output-not-320x180')
            if not display:
                record['faults'].append('display-timeout')
            else:
                record['elapsed_ms'] = display.get('elapsed_ms')
                if not display.get('ok'):
                    record['faults'].append('preview-unavailable')
                if display.get('cache') != expected_cache:
                    record['faults'].append('unexpected-cache-' + str(display.get('cache')))
                if service and service['result'].get('cache') != display.get('cache'):
                    record['faults'].append('service-display-cache-disagreement')
                if not isinstance(record['elapsed_ms'], (int, float)) or not math.isfinite(record['elapsed_ms']):
                    record['faults'].append('invalid-latency')
            current, _ = position()
            record['ax_position'] = current
            if abs(current - initial_position) > .000001:
                record['faults'].append('paused-position-changed')
        except (RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
            record['faults'].append('runner-error: ' + str(error))
        record['wall_ms'] = (time.monotonic() - started) * 1000
        samples.append(record)
        outcomes.write(json.dumps(record, allow_nan=False) + '\n')
        outcomes.flush()

    # 37 and 100 are coprime: every target occurs exactly once, out of order.
    # Repeating this permutation sets and then walks the same LRU order.
    # 150 raw 320x180 entries exceed 32 MiB; each disk reload evicts the next
    # target in the permutation after 50 additional pressure entries.
    order = [(37 * i) % 100 for i in range(100)]
    for phase, buckets, expected in [('miss', order, 'miss'), ('memory', order, 'memory'),
                                     ('pressure-seed', range(100, 150), 'miss'), ('disk', order, 'disk')]:
        for bucket in buckets:
            sample(phase, bucket, expected)
    outcomes.close()
    phases = {}
    for phase in ['miss', 'memory', 'pressure-seed', 'disk']:
        records = [s for s in samples if s['phase'] == phase]
        # Failure outcomes stay in the denominator and force qualification false.
        latencies = [s['elapsed_ms'] for s in records if isinstance(s.get('elapsed_ms'), (int, float)) and math.isfinite(s['elapsed_ms'])]
        loading = [s['loading_assignment_upper_bound_proxy_ms'] for s in records
                   if isinstance(s.get('loading_assignment_upper_bound_proxy_ms'), (int, float))]
        faulted = sum(bool(s['faults']) for s in records)
        visible = [s.get('visible', {}).get('image_visible_ms') for s in records]
        visible = [v for v in visible if isinstance(v, (int, float))]
        time_visible = [s.get('visible', {}).get('time_and_state_visible_ms') for s in records]
        time_visible = [v for v in time_visible if isinstance(v, (int, float))]
        phases[phase] = {'visible_image_count': len(visible), 'visible_image_p95_ms': percentile(visible, .95) if not faulted and len(visible) == len(records) else None,
                         'time_and_state_visible_count': len(time_visible), 'time_and_state_visible_p95_ms': percentile(time_visible, .95) if not faulted and len(time_visible) == len(records) else None,
                         'attempts': len(records), 'faulted_attempts': faulted,
                         'completed_latencies': len(latencies),
                         'p95_ms_nearest_rank': percentile(latencies, .95) if not faulted and len(latencies) == len(records) else None,
                         'available_latency_p95_ms_diagnostic_only': percentile(latencies, .95),
                         'loading_assignment_proxy_count': len(loading),
                         'loading_assignment_proxy_p95_ms': percentile(loading, .95),
                         'max_ms': max(latencies) if latencies else None,
                         'cache_counts': {kind: sum((s.get('display') or {}).get('cache') == kind for s in records)
                                          for kind in ['miss', 'memory', 'disk', 'error']}}
    summary = {'schema_version': 1, 'pid': args.pid, 'rect': rect, 'duration_seconds': args.duration,
               'trace': str(trace.relative_to(ROOT)), 'trace_start_offset': tail.start,
               'trace_end_offset': trace.stat().st_size, 'trace_parse_errors': tail.parse_errors,
               'generation': generation, 'initial_ax_position': initial_position, 'initial_ax_inventory': initial_inventory,
               'phases': phases, 'all_outcomes_retained': True,
               'cache_conditions_verified': all(not s['faults'] for s in samples) and tail.parse_errors == 0,
               'target_permutation': {'formula': '(37*i)%100 for i=0..99', 'order': order,
                                      'phases': ['miss', 'memory', 'disk']},
               'method': 'Real native mouse movement and hover/service/display traces, paused AX slider checked after every sample; no cache clearing, source mutation, seek, or direct decoder call.',
               'visible_observer_sha256': digest(owned(args.visible_observer)) if observer else None,
               'visible_measurement_scope': 'Before pointer warp/event post to callback receipt of actual display-space pixels matching independently settled image and time/state templates; no overhead subtraction.' if observer else None,
               'preview_latency_scope': 'display.elapsed_ms measures mouse-event processing to NSImage assignment callback; compositor visibility and pointer-command dispatch are not timed.',
               'loading_latency_scope': 'Upper-bound proxy from immediately preceding mouse-move trace to hover trace, which follows time/loading label assignment. Trace overhead is included; compositor presentation is not timed.',
               'cache_pressure_condition': '150 unique raw 320x180 previews; fixture must yield this output size for repeated-permutation disk cascade to qualify.',
               'scope_limits': ['Existing OS file cache conditions are uncontrolled.', 'First native-image correctness is calibrated separately by the owner.', 'Faulted/missing latencies prevent qualification; p95 of available latencies alone is diagnostic.'],
               'runner_sha256': digest(Path(__file__)), 'pointer_sha256': digest(pointer)}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    tail.handle.close()
    print(json.dumps(phases, indent=2))
    if not summary['cache_conditions_verified']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
