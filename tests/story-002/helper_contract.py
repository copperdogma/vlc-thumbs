#!/usr/bin/env python3
"""Behavioral helper qualification. Does not qualify native UI or cache latency."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
MAX_REPLY = 4096 + 320 * 180 * 4 + 1


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def call(helper, path, target, ordinal=0, timeout=6, video_count=1):
    argv = [str(helper), '--input', str(path), '--time-us', str(round(target * 1e6)),
            '--video-ordinal', str(ordinal), '--video-count', str(video_count), '--max-width', '320', '--max-height', '180']
    started = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    buffers = [bytearray(), bytearray()]
    overflow = []
    def read(stream, buffer, limit):
        while True:
            b = stream.read(4096)
            if not b:
                break
            if len(buffer) + len(b) > limit:
                overflow.append(True)
                p.kill()
                break
            buffer.extend(b)
    readers = [threading.Thread(target=read, args=(p.stdout, buffers[0], MAX_REPLY)),
               threading.Thread(target=read, args=(p.stderr, buffers[1], 65536))]
    for r in readers:
        r.start()
    rss_kib, cpu, timed_out = 0, 0., False
    while p.poll() is None:
        if time.monotonic() - started > timeout:
            timed_out = True
            p.kill()
            break
        sample = subprocess.run(['/bin/ps', '-o', 'rss=,%cpu=', '-p', str(p.pid)], capture_output=True, text=True)
        values = sample.stdout.split()
        if len(values) == 2:
            rss_kib = max(rss_kib, int(values[0]))
            cpu = max(cpu, float(values[1]))
        time.sleep(.01)
    p.wait()
    for r in readers:
        r.join(timeout=1)
    elapsed = (time.monotonic() - started) * 1000
    if timed_out:
        raise AssertionError('External 6-second process deadline exceeded')
    if overflow:
        raise AssertionError('Protocol output bound exceeded')
    raw = bytes(buffers[0])
    line, separator, payload = raw.partition(b'\n')
    assert separator and len(line) <= 4096, 'Missing/bounded JSON header'
    header = json.loads(line)
    assert header.get('version') == 2 and type(header.get('ok')) is bool
    if header['ok']:
        assert p.returncode == 0
        assert header['channels'] == 4
        assert type(header['width']) is int and 1 <= header['width'] <= 320
        assert type(header['height']) is int and 1 <= header['height'] <= 180
        assert header['payload_bytes'] == len(payload) == header['width'] * header['height'] * 4
        assert header['requested_us'] == round(target * 1e6)
        assert header['video_ordinal'] == ordinal
        assert header.get('sampling') == 'keyframe'
        assert type(header['actual_us']) is int and header['actual_us'] >= 0
        assert rss_kib <= 512 * 1024
    else:
        assert p.returncode != 0 and not payload and isinstance(header.get('error'), str)
    return {'header': header, 'elapsed_ms': elapsed, 'peak_sampled_rss_kib': rss_kib,
            'peak_sampled_cpu_percent': cpu, 'payload_sha256': hashlib.sha256(payload).hexdigest()}, payload


FRAME_MAP_CACHE = {}


def timeline_origin(record):
    # Native VLC flat-Matroska timecodes retain the initial positive gap.
    if record['probe']['format'].get('format_name') == 'matroska,webm':
        return 0.0
    return float(record['probe']['format'].get('start_time', 0))


def expected_frame(fixtures, record, target, ordinal, actual):
    streams = [s for s in record['probe']['streams'] if s['codec_type'] == 'video']
    stream_index = streams[ordinal]['index']
    map_path = fixtures / (record['name'] + '.frames.json')
    if map_path not in FRAME_MAP_CACHE:
        FRAME_MAP_CACHE[map_path] = json.loads(map_path.read_text())['frames']
    frames = FRAME_MAP_CACHE[map_path]
    frames = [f for f in frames if f['stream_index'] == stream_index]
    origin = timeline_origin(record)
    candidates = [(i, float(f['best_effort_timestamp_time']) - origin)
                  for i, f in enumerate(frames) if f.get('key_frame') == 1]
    assert candidates, 'Independent map must contain actual keyframes'
    index, normalized = min(candidates, key=lambda f: abs(f[1] - actual))
    assert abs(normalized - actual) <= .002, 'Reply is not an independently verified keyframe'
    # Seek indexes/codecs can return an earlier qualified keyframe. Do not decode
    # forward through a sparse GOP merely to satisfy an arbitrary pointer delta.
    if any(t <= target + .002 for _, t in candidates):
        assert actual <= target + .002, 'Future keyframe returned despite preceding keyframe'
    else:
        assert abs(actual - min(t for _, t in candidates)) <= .002, 'Initial gap must use first qualified keyframe'
    return index, normalized, streams[ordinal]


def reference(ffmpeg, path, index, ordinal, w, h, stream):
    # Select independent ffprobe frame ordinal; no helper-reported PTS used here.
    matrix = stream.get('color_space')
    if matrix in (None, 'unknown', 'unspecified'):
        matrix = 'bt709' if stream['height'] >= 720 else 'bt601'
    # Explicit project SDR fallback; host CLI defaults differ on unspecified HD.
    argv = [ffmpeg, '-nostdin', '-v', 'error', '-i', str(path), '-map', f'0:v:{ordinal}',
            '-vf', f'select=eq(n\\,{index}),scale={w}:{h}:flags=bilinear:in_color_matrix={matrix}', '-frames:v', '1',
            '-threads', '2', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-']
    result = subprocess.run(argv, capture_output=True, check=True, timeout=30)
    assert len(result.stdout) == w * h * 4, 'Independent reference frame size'
    return result.stdout, argv


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--helper', type=Path, required=True)
    ap.add_argument('--fixtures', type=Path, default=ROOT / 'work/fixtures/story-002')
    ap.add_argument('--output', type=Path, default=ROOT / 'work/validation/story002/helper-keyframe-results.json')
    ap.add_argument('--ffmpeg', default='/usr/local/bin/ffmpeg')
    ap.add_argument('--samples', type=int, default=100)
    args = ap.parse_args()
    assert args.samples >= 100, 'Qualification requires >=100 samples per standard fixture'
    fixtures, helper = args.fixtures.resolve(), args.helper.resolve()
    manifest = json.loads((fixtures / 'generation.json').read_text())
    records = {r['name']: r for r in manifest['fixtures']}
    results = {'scope': 'Protocol v2 keyframe MVP helper: decode/IPC/reference/resource/latency; UI/cache/playback untested',
               'sampling': 'keyframe', 'pointer_delta_is_failure': False,
               'host': os.uname()._asdict() if hasattr(os.uname(), '_asdict') else list(os.uname()),
               'helper': str(helper), 'helper_sha256': sha(helper),
               'generation_sha256': sha(fixtures / 'generation.json'),
               'conditions': 'Sequential uncached process launches, generated media recently written/read; OS filesystem cache warm/uncontrolled. No global cache flush. Timing includes Python sampling overhead; excludes GUI/service/presentation.',
               'correctness': [], 'benchmarks': [], 'failures': []}
    def save():
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + '\n')
    hashes = {name: sha(fixtures/name) for name in records}
    cases = [('standard.mp4', 12.125, 0), ('standard.mkv', 12.125, 0),
             ('long-gop.mp4', 9.125, 0), ('vfr.mkv', 8.25, 0), ('nonzero.mkv', 6.125, 0),
             ('nonzero.mkv', 0., 0), ('nonzero.mkv', 11.125, 0), ('nonzero.mkv', 16.125, 0),
             ('edit-offset.mp4', 5.125, 0), ('rotation.mp4', 4.125, 0), ('sar.mp4', 3.125, 0),
             ('two-tracks.mkv', 4., 0), ('two-tracks.mkv', 4., 1),
             ('short-4k.mp4', 1.25, 0), ('five-minute.mp4', 244.25, 0),
             ('standard.mp4', 0., 0), ('standard.mp4', 60., 0), ('edit-offset.mp4', 0., 0)]
    for name, target, ordinal in cases:
        case = {'fixture': name, 'target_s': target, 'ordinal': ordinal}
        try:
            measured, payload = call(helper, fixtures/name, target, ordinal, video_count=2 if name == 'two-tracks.mkv' else 1)
            case.update(measured)
            assert measured['header']['ok'], measured['header']
            actual = measured['header']['actual_us'] / 1e6
            if name == 'nonzero.mkv':
                assert measured['header']['timeline_origin_us'] == 0
                assert actual == (15.0 if target >= 15 else 5.0), 'Native MKV timeline keyframe correspondence'
            index, normalized, stream = expected_frame(fixtures, records[name], target, ordinal, actual)
            case['independent_frame_index'] = index
            case['independent_normalized_s'] = normalized
            case['pointer_delta_s'] = actual - target
            # Selected frame must match an independent actual-keyframe map entry.
            assert abs(measured['header']['actual_us'] / 1e6 - normalized) <= .002
            width, height = measured['header']['width'], measured['header']['height']
            sar = stream.get('sample_aspect_ratio', '1:1').split(':')
            ratio = stream['width'] / stream['height'] * (int(sar[0]) / int(sar[1]) if len(sar) == 2 and int(sar[1]) else 1)
            rotation = next((s.get('rotation', 0) for s in stream.get('side_data_list', []) if 'rotation' in s), 0)
            if abs(rotation) % 180 == 90:
                ratio = 1 / ratio
            assert abs(width / height - ratio) < .04, 'Display aspect / rotation mismatch'
            pixels, argv = reference(args.ffmpeg, fixtures/name, index, ordinal, width, height, stream)
            # Independent builds may differ in color-conversion rounding; alpha excluded.
            error = sum(abs(a-b) for i, (a, b) in enumerate(zip(payload, pixels)) if i % 4 != 3) / (width*height*3)
            case['reference_mean_absolute_rgb_error'] = error
            case['reference_command'] = argv
            assert error <= 8., f'Reference pixels differ: {error:.3f}'
            case['pass'] = True
        except Exception as e:
            case.update({'pass': False, 'failure': str(e)})
            results['failures'].append(case.copy())
        results['correctness'].append(case)
        save()
        print(name, target, case['pass'], case.get('failure', ''), flush=True)
    for name, ordinal in [('audio-only.m4a', 0), ('corrupt.mp4', 0), ('truncated.mp4', 0),
                          ('hdr-tagged.mp4', 0), ('two-tracks.mkv', 2), ('missing.mp4', 0), ('.', 0)]:
        case = {'fixture': name, 'ordinal': ordinal, 'expected': 'error'}
        try:
            measured, _ = call(helper, fixtures/name, 1., ordinal, video_count=2 if name == 'two-tracks.mkv' else 1)
            case.update(measured)
            assert not measured['header']['ok'], 'Expected explicit failure'
            case['pass'] = True
        except Exception as e:
            case.update({'pass': False, 'failure': str(e)})
            results['failures'].append(case.copy())
        results['correctness'].append(case)
        save()
    mp4, mkv = results['correctness'][:2]
    results['same_stream_rgba_equal'] = mp4.get('payload_sha256') == mkv.get('payload_sha256') and mp4.get('pass') and mkv.get('pass')
    if not results['same_stream_rgba_equal']:
        results['failures'].append({'failure': 'Same-stream MP4/MKV RGBA mismatch'})
    for name in ('standard.mp4', 'standard.mkv'):
        samples, failures = [], []
        for i in range(args.samples):
            target = ((i * 37) % 119) * .5
            try:
                measured, _ = call(helper, fixtures/name, target)
                assert measured['header']['ok'], measured['header']
                actual = measured['header']['actual_us'] / 1e6
                index, normalized, _ = expected_frame(fixtures, records[name], target, 0, actual)
                measured.update({'target_s': target, 'pointer_delta_s': actual-target,
                                 'independent_keyframe_index': index, 'independent_normalized_s': normalized})
                samples.append(measured)
            except Exception as e:
                failures.append({'i': i, 'target': target, 'error': str(e)})
        times = sorted(s['elapsed_ms'] for s in samples)
        bench = {'fixture': name, 'attempted': args.samples, 'success': len(samples), 'failures': failures,
                 'samples': samples, 'first_benchmark_process_ms': samples[0]['elapsed_ms'] if samples else None,
                 'p50_ms': times[math.ceil(len(times)*.5)-1] if times else None,
                 'p95_ms': times[math.ceil(len(times)*.95)-1] if times else None,
                 'max_ms': max(times) if times else None,
                 'max_absolute_pointer_delta_s': max((abs(s['pointer_delta_s']) for s in samples), default=None),
                 'max_sampled_rss_kib': max((s['peak_sampled_rss_kib'] for s in samples), default=0)}
        bench['helper_latency_target_pass'] = not failures and bench['p95_ms'] <= 1000
        results['benchmarks'].append(bench)
        if not bench['helper_latency_target_pass']:
            results['failures'].append({'failure': 'Helper standard latency condition failed', 'fixture': name})
        save()
        print(name, 'benchmark p95', bench['p95_ms'], 'errors', len(failures), flush=True)
    results['source_hashes_unchanged'] = all(sha(fixtures/name) == value for name, value in hashes.items())
    density = []
    for name in ('standard.mp4', 'standard.mkv', 'long-gop.mp4', 'five-minute.mp4'):
        record = records[name]
        stream_index = next(s['index'] for s in record['probe']['streams'] if s['codec_type'] == 'video')
        frames = json.loads((fixtures / (name + '.frames.json')).read_text())['frames']
        origin = timeline_origin(record)
        keys = [float(f['best_effort_timestamp_time'])-origin for f in frames
                if f['stream_index'] == stream_index and f.get('key_frame') == 1]
        density.append({'fixture': name, 'keyframes_s': keys, 'keyframe_count': len(keys),
                        'max_interval_s': max((b-a for a,b in zip(keys,keys[1:])), default=None)})
    results['independent_keyframe_density'] = density
    results['helper_hash_unchanged'] = sha(helper) == results['helper_sha256']
    if not results['helper_hash_unchanged']:
        results['failures'].append({'failure': 'Helper binary changed during attempt'})
    results['first_helper_request_ms'] = results['correctness'][0].get('elapsed_ms')
    if not results['source_hashes_unchanged']:
        results['failures'].append({'failure': 'Generated source changed'})
    results['pass'] = not results['failures']
    save()
    raise SystemExit(0 if results['pass'] else 1)


if __name__ == '__main__':
    main()
