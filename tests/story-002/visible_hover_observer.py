#!/usr/bin/env python3
"""Bounded visible-screen observer for Story 002 native hover trials.

The caller owns application launch, media state, cache setup, and invocation
order. This helper only asks the compiled visible-capture-probe to move to a
timeline bucket, retain its raw JSONL, and compare visible pixels.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
DEFAULT_PROBE = WORK / 'validation/story002/visible-capture-probe'
TIME_MASK_RE = re.compile(r'^[0-9a-fA-F]{540}$')
STATE_MASK_RE = re.compile(r'^[0-9a-fA-F]{1055}$')
IMAGE_HASH_RE = re.compile(r'^[0-9a-fA-F]{16}$')


class VisibleHoverError(RuntimeError):
    """The requested visible hover observation could not be established."""


def _owned(path: Path, *, must_exist: bool = False) -> Path:
    path = Path(path).absolute()
    resolved = path.resolve(strict=must_exist)
    if resolved != path or not resolved.is_relative_to(WORK) or resolved == WORK:
        raise ValueError(f'Path must stay beneath {WORK} without symlinks: {path}')
    return resolved


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _rows(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    with path.open(encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise VisibleHoverError(f'{path.name}:{line_number}: malformed probe JSON: {exc}') from exc
            if not isinstance(row, dict):
                raise VisibleHoverError(f'{path.name}:{line_number}: probe row is not an object')
            result.append(row)
    return result


def _hamming(left: str, right: str) -> int:
    if len(left) != len(right):
        return 1 << 30
    return sum((int(a, 16) ^ int(b, 16)).bit_count() for a, b in zip(left, right))


def _read_loading_mask(path: Path) -> str:
    source = _owned(path, must_exist=True)
    raw = source.read_text(encoding='utf-8').strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = raw
    if isinstance(value, dict):
        value = value.get('state_mask_hex')
    if not isinstance(value, str) or not STATE_MASK_RE.fullmatch(value):
        raise ValueError(f'Loading-state mask must be 1055 hexadecimal characters in {source}')
    return value.lower()


class VisibleHoverObserver:
    """Observe visible previews using an existing, workspace-owned probe.

    ``rect`` is the global AX timeline rectangle ``(x, y, width, height)``;
    ``duration`` is the media duration in seconds. Every path written by this
    helper stays beneath the repository's ignored ``work/`` directory.
    """

    def __init__(self, pid: int, rect: Iterable[float], duration: float,
                 probe: Path = DEFAULT_PROBE, loading_mask: Path | None = None,
                 templates: Path | None = None):
        self.pid = int(pid)
        self.rect = tuple(float(n) for n in rect)
        self.duration = float(duration)
        self.probe = _owned(Path(probe), must_exist=True)
        if not self.probe.is_file() or not self.probe.stat().st_mode & 0o111:
            raise ValueError(f'Probe must be an executable existing file: {self.probe}')
        if self.pid <= 0 or len(self.rect) != 4 or not all(map(math.isfinite, self.rect)):
            raise ValueError('A positive PID and finite x,y,width,height timeline rectangle are required')
        if self.rect[2] <= 14 or self.rect[3] <= 0 or not math.isfinite(self.duration) or self.duration <= 74.6:
            raise ValueError('Timeline width/height and media duration do not cover the 150 calibration buckets')
        self.probe_sha256 = _digest(self.probe)
        self.loading_mask = _read_loading_mask(loading_mask) if loading_mask else None
        self.templates_path = _owned(Path(templates)) if templates else None
        self._out: Path | None = None
        self._templates: dict[str, Any] | None = None
        self._commands_path: Path | None = None
        self._previous_bucket: int | None = None

    def _check_probe(self) -> None:
        if _digest(self.probe) != self.probe_sha256:
            raise VisibleHoverError('The existing visible-capture-probe binary changed during this observer run')

    def _prepare_output(self, out: Path) -> Path:
        path = _owned(Path(out))
        path.mkdir(parents=True, exist_ok=True)
        if not path.is_dir():
            raise ValueError(f'Output must be a directory: {path}')
        self._out = path
        self._commands_path = path / 'probe-commands.jsonl'
        reserved = [self._commands_path, path / 'templates.json', path / 'calibration-failures.json']
        reserved.extend(path / f'calibration-bucket-{bucket:03d}.jsonl' for bucket in range(100))
        collisions = [item for item in reserved if item.exists()]
        if collisions:
            raise ValueError(f'Refusing to overwrite existing observer output: {collisions[0]}')
        return path

    def _invoke(self, argv: list[str], output_file: Path) -> tuple[int, str, str, float, bool]:
        self._check_probe()
        command = [str(self.probe), *argv]
        began = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=3, check=False)
            returncode, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            returncode = None
            stdout = exc.stdout.decode(errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
            stderr = exc.stderr.decode(errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
        elapsed = time.monotonic() - began
        entry = {
            'argv': command,
            'output_jsonl': str(output_file),
            'returncode': returncode,
            'timed_out': timed_out,
            'timeout_seconds': 3,
            'elapsed_seconds': elapsed,
            'stdout': stdout,
            'stderr': stderr,
        }
        assert self._commands_path is not None
        with self._commands_path.open('a', encoding='utf-8') as log:
            log.write(json.dumps(entry, allow_nan=False, sort_keys=True) + '\n')
            log.flush()
        return returncode if returncode is not None else 124, stdout, stderr, elapsed, timed_out

    def _point(self, bucket: int) -> tuple[float, float, float]:
        x, y, width, height = self.rect
        seconds = 0.5 * bucket + 0.1
        left, right = x + 7, x + width - 7
        return left + seconds / self.duration * (right - left), y + height / 2, seconds

    @staticmethod
    def _validate_row(row: dict[str, Any], context: str) -> tuple[str, str, str, int, int]:
        if row.get('error') not in (None, ''):
            raise VisibleHoverError(f'{context}: probe row error: {row["error"]}')
        data = row.get('result')
        if not isinstance(data, dict):
            raise VisibleHoverError(f'{context}: missing result object')
        scale = data.get('scale_from_336_points')
        width, height = data.get('pixel_width'), data.get('pixel_height')
        if scale not in (1, 1.0, 2, 2.0) or (width, height) != (336 * int(scale), 224 * int(scale)):
            raise VisibleHoverError(f'{context}: unexpected panel dimensions/scale {width}x{height} scale={scale}')
        if data.get('image_roi_points') != [8, 9, 320, 180]:
            raise VisibleHoverError(f'{context}: expected opaque image ROI 8,9,320,180')
        image_hash = data.get('image_sample_hash_fnv1a64')
        time_mask, state_mask = data.get('time_mask_hex'), data.get('state_mask_hex')
        time_glyphs, state_glyphs = data.get('time_glyph_count'), data.get('state_glyph_count')
        if not isinstance(image_hash, str) or not IMAGE_HASH_RE.fullmatch(image_hash):
            raise VisibleHoverError(f'{context}: invalid opaque image ROI hash')
        if not isinstance(time_mask, str) or not TIME_MASK_RE.fullmatch(time_mask):
            raise VisibleHoverError(f'{context}: invalid time glyph mask')
        if not isinstance(state_mask, str) or not STATE_MASK_RE.fullmatch(state_mask):
            raise VisibleHoverError(f'{context}: invalid state glyph mask')
        if not isinstance(time_glyphs, int) or time_glyphs < 0 or not isinstance(state_glyphs, int) or state_glyphs < 0:
            raise VisibleHoverError(f'{context}: invalid time/state glyph count')
        return image_hash.lower(), time_mask.lower(), state_mask.lower(), time_glyphs, state_glyphs

    def prepare(self, out: Path) -> Path:
        """Capture 100 scored-bank points and write stable per-bucket templates.

        Raw probe rows are retained in ``calibration-bucket-NNN.jsonl``. This
        method intentionally completes all 150 invocations before reporting
        validation errors so partial evidence is preserved.
        """
        output = self._prepare_output(out)
        with self._commands_path.open('x', encoding='utf-8') as log:  # noqa: SIM115
            pass
        raw_by_bucket: dict[int, list[dict[str, Any]]] = {}
        failures: list[str] = []
        for bucket in range(100):
            x, y, seconds = self._point(bucket)
            raw_path = output / f'calibration-bucket-{bucket:03d}.jsonl'
            argv = ['--pid', str(self.pid), '--point', f'{x:.6f},{y:.6f}', '--settle-ms', '1500',
                    '--count', '100', '--output', str(raw_path)]
            rc, stdout, stderr, elapsed, timed_out = self._invoke(argv, raw_path)
            try:
                rows = _rows(raw_path) if raw_path.is_file() else []
            except VisibleHoverError as exc:
                rows = []
                failures.append(f'bucket {bucket}: {exc}')
            raw_by_bucket[bucket] = rows
            if rc != 0:
                failures.append(f'bucket {bucket}: probe return code {rc}' + (' (3s timeout)' if timed_out else ''))
            if not rows:
                failures.append(f'bucket {bucket}: no JSONL rows (elapsed {elapsed:.3f}s)')
            if stdout.strip() or stderr.strip():
                failures.append(f'bucket {bucket}: unexpected probe stdout/stderr; retained in probe-commands.jsonl')
            if rc == 2:
                failures.append('Calibration stopped after ownership/active-app precondition failure; remaining buckets unattempted.')
                break

        templates: dict[str, Any] = {}
        for bucket, rows in raw_by_bucket.items():
            if len(rows) < 3:
                failures.append(f'bucket {bucket}: fewer than three screenshots')
                continue
            parsed: list[tuple[str, str, str, int, int]] = []
            for index, row in enumerate(rows):
                try:
                    parsed.append(self._validate_row(row, f'bucket {bucket} row {index}'))
                except VisibleHoverError as exc:
                    failures.append(str(exc))
            if len(parsed) != len(rows):
                continue
            recent = parsed[-3:]
            if any(sample[:3] != recent[-1][:3] for sample in recent[:-1]):
                failures.append(f'bucket {bucket}: final three image/time/state samples are not stable')
                continue
            image_hash, time_mask, state_mask, time_glyphs, state_glyphs = recent[-1]
            if self.loading_mask and _hamming(state_mask, self.loading_mask) <= 43:
                failures.append(f'bucket {bucket}: final stable state is still Loading, not a ready thumbnail')
                continue
            if time_glyphs <= 0 or state_glyphs <= 0:
                failures.append(f'bucket {bucket}: stable final time/state glyph region is empty')
                continue
            templates[str(bucket)] = {
                'bucket': bucket,
                'target_seconds': 0.5 * bucket + 0.1,
                'opaque_image_hash': image_hash,
                'time_mask_hex': time_mask,
                'time_glyph_count': time_glyphs,
                'state_mask_hex': state_mask,
                'state_glyph_count': state_glyphs,
                'stable_final_samples': 3,
                'raw_jsonl': raw_by_bucket[bucket] and f'calibration-bucket-{bucket:03d}.jsonl',
            }
        if len(templates) != 100:
            failures.append(f'only {len(templates)}/100 buckets produced a stable template')
        if failures:
            self._write_failure_manifest(output, failures, raw_by_bucket)
            raise VisibleHoverError('Visible calibration failed; all available rows are retained in '
                                    f'{output}. First issue: {failures[0]}')
        manifest = {
            'schema_version': 1,
            'kind': 'visible_hover_templates',
            'pid': self.pid,
            'timeline_rect': list(self.rect),
            'media_duration_seconds': self.duration,
            'probe_path': str(self.probe),
            'probe_sha256': self.probe_sha256,
            'calibration': {'buckets': 100, 'formula_seconds': '0.5 * bucket + 0.1',
                            'settle_ms': 1500, 'capture_count_cap': 100,
                            'stable_final_samples_required': 3, 'retained_all_rows': True},
            'templates': templates,
        }
        template_path = output / 'templates.json'
        with template_path.open('x', encoding='utf-8') as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write('\n')
        self._templates = manifest
        self.templates_path = template_path
        return template_path

    @staticmethod
    def _write_failure_manifest(output: Path, failures: list[str], rows: dict[int, list[dict[str, Any]]]) -> None:
        path = output / 'calibration-failures.json'
        summary = {'schema_version': 1, 'kind': 'visible_hover_calibration_failures',
                   'failures': failures, 'buckets_with_rows': sum(bool(value) for value in rows.values()),
                   'row_counts': {str(key): len(value) for key, value in rows.items()},
                   'all_available_rows_retained': True}
        with path.open('x', encoding='utf-8') as handle:
            json.dump(summary, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write('\n')

    def _load_templates(self, out: Path) -> dict[str, Any]:
        if self._templates is not None:
            return self._templates
        path = self.templates_path or _owned(Path(out) / 'templates.json', must_exist=True)
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data.get('kind') != 'visible_hover_templates' or data.get('probe_sha256') != self.probe_sha256 or
                data.get('pid') != self.pid or tuple(data.get('timeline_rect', ())) != self.rect or
                data.get('media_duration_seconds') != self.duration):
            raise VisibleHoverError('Template manifest kind or exact probe fingerprint does not match this observer')
        self._templates = data
        return data

    def collect(self, bucket: int, out: Path, require_distinct: bool = True) -> dict[str, Any]:
        """Collect one scored bucket until its calibrated opaque image appears."""
        if not isinstance(bucket, int) or isinstance(bucket, bool) or not 0 <= bucket < 150:
            raise ValueError('Scored bucket must be an integer in [0,150)')
        output = _owned(Path(out))
        output.mkdir(parents=True, exist_ok=False)
        self._out = output
        self._commands_path = output / 'probe-commands.jsonl'
        if not self._commands_path.exists():
            self._commands_path.touch(mode=0o600, exist_ok=False)
        templates = self._load_templates(output)
        template = templates['templates'].get(str(bucket))
        if not isinstance(template, dict):
            raise VisibleHoverError(f'No calibrated template for bucket {bucket}')
        x, y, seconds = self._point(bucket)
        raw_path = output / f'visible-bucket-{bucket:03d}.jsonl'
        if raw_path.exists():
            raise ValueError(f'Refusing to overwrite visible capture rows: {raw_path}')
        argv = ['--pid', str(self.pid), '--point', f'{x:.6f},{y:.6f}', '--expected-hash',
                template['opaque_image_hash'], '--count', '100', '--output', str(raw_path)]
        rc, stdout, stderr, elapsed, timed_out = self._invoke(argv, raw_path)
        rows = _rows(raw_path) if raw_path.is_file() else []
        result: dict[str, Any] = {
            'bucket': bucket,
            'target_seconds': seconds,
            'raw_jsonl': str(raw_path),
            'probe_returncode': rc,
            'probe_timed_out': timed_out,
            'probe_elapsed_seconds': elapsed,
            'probe_stdout': stdout,
            'probe_stderr': stderr,
            'rows': rows,
            'first_matching_image': None,
            'first_matching_time': None,
            'first_matching_state': None,
            'image_visible_ms': None,
            'time_and_state_visible_ms': None,
            'previous_bucket': self._previous_bucket,
            'previous_time_ambiguous': None,
            'errors': [],
            'faults': [],
        }
        if rc != 0:
            result['errors'].append(f'probe-returncode-{rc}')
        if stdout.strip() or stderr.strip():
            result['errors'].append('unexpected-probe-stdout-or-stderr')
        ready_state = template['state_mask_hex']
        previous = templates['templates'].get(str(self._previous_bucket)) if self._previous_bucket is not None else None
        for index, row in enumerate(rows):
            if row.get('error') not in (None, ''):
                result['errors'].append(f'row-{index}-error:{row["error"]}')
                continue
            observed = row.get('result')
            if not isinstance(observed, dict):
                result['errors'].append(f'row-{index}-missing-result')
                continue
            receipt = row.get('input_to_callback_ms')
            if not isinstance(receipt, (int, float)) or not math.isfinite(receipt) or receipt < 0:
                result['errors'].append(f'row-{index}-invalid-callback-receipt')
                continue
            if result['first_matching_image'] is None and observed.get('image_sample_hash_fnv1a64') == template['opaque_image_hash']:
                result['first_matching_image'] = {'row_index': index, 'input_to_callback_ms': receipt}
            observed_time = observed.get('time_mask_hex')
            time_distance = _hamming(observed_time, template['time_mask_hex']) if isinstance(observed_time, str) else 1 << 30
            previous_time_distance = _hamming(observed_time, previous['time_mask_hex']) if previous and isinstance(observed_time, str) else 1 << 30
            time_match = time_distance <= 22 and (not require_distinct or time_distance < previous_time_distance)
            if result['first_matching_time'] is None and time_match:
                result['first_matching_time'] = {'row_index': index, 'input_to_callback_ms': receipt,
                                                 'hamming': time_distance,
                                                 'time_mask_hex': observed_time}
            observed_state = observed.get('state_mask_hex')
            state_match = False
            if isinstance(observed_state, str):
                distances = [(label, _hamming(observed_state, mask)) for label, mask in
                             [('ready', ready_state), *([('loading', self.loading_mask)] if self.loading_mask else [])]]
                label, distance = min(distances, key=lambda pair: pair[1])
                previous_state_distance = _hamming(observed_state, previous['state_mask_hex']) if previous else 1 << 30
                state_match = distance <= 43 and distance < previous_state_distance
                if result['first_matching_state'] is None and state_match:
                    result['first_matching_state'] = {'row_index': index, 'input_to_callback_ms': receipt,
                                                      'state': label, 'hamming': distance}
            if result['time_and_state_visible_ms'] is None and time_match and state_match:
                result['time_and_state_visible_ms'] = receipt
        previous = templates['templates'].get(str(self._previous_bucket)) if self._previous_bucket is not None else None
        if require_distinct and result['first_matching_time'] is not None and isinstance(previous, dict):
            distance = _hamming(result['first_matching_time']['time_mask_hex'], previous['time_mask_hex'])
            result['previous_time_hamming'] = distance
            result['previous_time_ambiguous'] = distance <= result['first_matching_time']['hamming']
            if result['previous_time_ambiguous']:
                result['errors'].append('time-mask-ambiguous-with-previous-scored-template')
        elif self._previous_bucket is not None:
            result['previous_time_ambiguous'] = None
        if result['first_matching_image'] is None:
            result['errors'].append('calibrated-image-not-observed')
        if result['first_matching_time'] is None:
            result['errors'].append('calibrated-time-mask-not-observed')
        if result['first_matching_state'] is None:
            result['errors'].append('ready-or-loading-state-mask-not-observed')
        if result['first_matching_image'] is not None:
            result['image_visible_ms'] = result['first_matching_image']['input_to_callback_ms']
        if result['time_and_state_visible_ms'] is None:
            result['errors'].append('time-and-state-not-visible-in-same-capture')
        # Keep a separate caller-facing fault list while retaining the detailed
        # validation field for standalone inspection.
        result['faults'] = list(dict.fromkeys(result['errors']))
        result['all_rows_retained'] = True
        result['qualified'] = not result['faults']
        summary_path = output / f'visible-bucket-{bucket:03d}-summary.json'
        with summary_path.open('x', encoding='utf-8') as handle:
            json.dump({key: value for key, value in result.items() if key != 'rows'},
                      handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write('\n')
        self._previous_bucket = bucket
        return result


Observer = VisibleHoverObserver
