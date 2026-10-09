#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Bounded acquisition from an isolated helper; records observations, not acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--helper', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--reordered', type=Path, help='Owned legal fixture with reversed Matroska TrackEntries')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
args.helper = args.helper.resolve(strict=True)
args.output.mkdir(exist_ok=False, parents=True)
report = {'helper': str(args.helper), 'helper_sha256': hashlib.sha256(args.helper.read_bytes()).hexdigest(),
          'cases': []}

def members(group):
    result = subprocess.run(['ps', '-axo', 'pid=,pgid=,stat='], capture_output=True,
                            text=True, check=True, timeout=2)
    return [{'pid': int(f[0]), 'group': int(f[1]), 'state': f[2]}
            for line in result.stdout.splitlines() if len(f := line.split()) >= 3
            and int(f[1]) == group]

def acquire(name, source, times, ordinal=0, count=1, fingerprint=False):
    if shutil.disk_usage(args.output).free < 1024 ** 3:
        raise RuntimeError('Less than 1 GiB free')
    command = [str(args.helper)]
    if fingerprint:
        command += ['--fingerprint', 'sampled', '--input', str(source.resolve())]
    else:
        command += ['--worker', '--input', str(source.resolve()),
                    '--video-ordinal', str(ordinal), '--video-count', str(count),
                    '--max-width', '320', '--max-height', '180']
    case = {'name': name, 'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'command': command, 'times_us': times}
    report['cases'].append(case)
    payload = ''.join('%d %d\n' % (i + 1, value) for i, value in enumerate(times)).encode()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    start = time.monotonic()
    try:
        output, errors = process.communicate(payload, timeout=25)
        case['returncode'] = process.returncode
        case['timeout'] = False
    except subprocess.TimeoutExpired:
        case['timeout'] = True
        os.killpg(process.pid, signal.SIGKILL)
        output, errors = process.communicate(timeout=2)
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=2)
        case['final_members'] = members(process.pid)
        case['elapsed_seconds'] = time.monotonic() - start
    (args.output / (name + '.stdout.bin')).write_bytes(output)
    (args.output / (name + '.stderr.log')).write_bytes(errors)
    replies = []
    while output:
        header, separator, rest = output.partition(b'\n')
        assert separator and len(header) <= 4096
        reply = json.loads(header)
        size = reply.get('payload_bytes', 0)
        assert 0 <= size <= 320 * 180 * 4 and len(rest) >= size
        if size:
            pixels = rest[:size]
            pixel_path = args.output / ('%s-%d.rgba' % (name, reply['id']))
            pixel_path.write_bytes(pixels)
            reply['rgba_path'] = str(pixel_path)
            reply['rgba_sha256'] = hashlib.sha256(pixels).hexdigest()
        replies.append(reply)
        output = rest[size:]
    case['replies'] = replies
    (args.output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')

fixtures = root / 'work/story005-fixtures'
for name, times in [('standard.mp4', [125000, 4125000, 125000]),
                    ('long-gop.mp4', [9125000, 10125000, 125000]),
                    ('edit-offset.mp4', [4125000, 10125000, 2125000]),
                    ('positive-start.mkv', [6125000, 11125000, 5125000]),
                    ('rotation.mp4', [4125000, 10125000, 125000]),
                    ('sar.mp4', [125000, 4125000, 125000])]:
    acquire(name, fixtures / name, times)
mp4 = root / 'work/story005-mp4-fixtures001'
for name in ['nonkeyframe-trim.mp4', 'negative-ctts.mp4', 'negative-ctts-trim.mp4']:
    acquire(name, mp4 / name, [0, 125000, 4125000, 0])
for ordinal in [0, 1]:
    acquire('two-tracks-%d' % ordinal, fixtures / 'two-tracks.mkv', [125000, 4125000], ordinal, 2)
if args.reordered:
    for ordinal in [0, 1]:
        acquire('reordered-tracks-%d' % ordinal, args.reordered, [125000, 4125000, 125000], ordinal, 2)
    acquire('reordered-count-mismatch', args.reordered, [125000], 0, 1)
acquire('sampled-fingerprint', fixtures / 'standard.mp4', [], fingerprint=True)
print(json.dumps({'output': str(args.output), 'cases': len(report['cases'])}))
