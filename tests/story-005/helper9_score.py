#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compare helper images with independently decoded fixture frames; no quality allowance."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--results', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
report = {'reference_decoder': subprocess.check_output(['ffmpeg', '-version'], text=True),
          'comparisons': []}
cases = json.loads(args.results.read_text())['cases']
cache = {}
for case in cases:
    source = Path(case['source'])
    if not source.with_suffix(source.suffix + '.frames.json').exists():
        continue
    metadata = json.loads(source.with_suffix(source.suffix + '.frames.json').read_text())['frames']
    for reply in case['replies']:
        if not reply.get('rgba_path'):
            continue
        stream = reply['video_ordinal']
        # All video-only fixtures have stream-index zero; two-track fixture has 0/1.
        frames = [frame for frame in metadata if frame['stream_index'] == stream]
        actual = reply['actual_us'] + reply['timeline_origin_us']
        index = min(range(len(frames)), key=lambda n: abs(float(frames[n]['pts_time']) * 1e6 - actual))
        reference_time = float(frames[index]['pts_time']) * 1e6
        key = (str(source), stream, index, reply['width'], reply['height'])
        if key not in cache:
            if shutil.disk_usage(args.output).free < 1024 ** 3:
                raise RuntimeError('Less than 1 GiB free')
            path = args.output / ('reference-%d.rgba' % len(cache))
            command = ['ffmpeg', '-v', 'error', '-i', str(source), '-map', '0:v:%d' % stream,
                       '-vf', 'select=eq(n\\,%d),scale=%d:%d:flags=bilinear:in_color_matrix=bt601:in_range=tv:out_range=pc' %
                       (index, reply['width'], reply['height']), '-frames:v', '1', '-fps_mode', 'passthrough',
                       '-pix_fmt', 'rgba', '-f', 'rawvideo', str(path)]
            result = subprocess.run(command, capture_output=True, timeout=15)
            assert result.returncode == 0, result.stderr
            cache[key] = (path, command)
        path, command = cache[key]
        helper_pixels = Path(reply['rgba_path']).read_bytes()
        reference_pixels = path.read_bytes()
        assert len(helper_pixels) == len(reference_pixels)
        differences = [abs(a - b) for i, (a, b) in enumerate(zip(helper_pixels, reference_pixels)) if i % 4 != 3]
        comparison = {'case': case['name'], 'id': reply['id'], 'actual_us': reply['actual_us'],
                      'timeline_origin_us': reply['timeline_origin_us'], 'reference_frame_index': index,
                      'reference_pts_us': reference_time, 'pts_difference_us': actual - reference_time,
                      'reference_keyframe': frames[index]['key_frame'],
                      'width': reply['width'], 'height': reply['height'],
                      'rgb_mae': sum(differences) / len(differences), 'rgb_max_difference': max(differences),
                      'helper_sha256': hashlib.sha256(helper_pixels).hexdigest(),
                      'reference_sha256': hashlib.sha256(reference_pixels).hexdigest(), 'reference_command': command}
        report['comparisons'].append(comparison)
        (args.output / 'comparisons.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'comparisons': len(report['comparisons']), 'max_rgb_mae': max(c['rgb_mae'] for c in report['comparisons'])}))
