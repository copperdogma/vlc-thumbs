#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Generate synthetic Matroska identity controls in a fresh directory.

Requires FFmpeg with libx264. No imported media. Rewrites EBML lengths and block
track VINTs; drops optional seek/cue tables and CRCs rather than leave stale ones.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zlib


def vint(data, at, ident=False):
    lead = data[at]
    if not lead:
        raise ValueError('zero VINT marker')
    width = 1
    while not lead & (1 << (8 - width)):
        width += 1
    raw = int.from_bytes(data[at:at + width], 'big')
    return (raw if ident else raw & ((1 << (7 * width)) - 1)), width


def encode_vint(value):
    for width in range(1, 9):
        if value < (1 << (7 * width)) - 1:
            return ((1 << (7 * width)) | value).to_bytes(width, 'big')
    raise ValueError('VINT overflow')


def elements(data):
    at = 0
    while at < len(data):
        ident, a = vint(data, at, True)
        size, b = vint(data, at + a)
        begin = at + a + b
        end = begin + size
        if size == (1 << (7 * b)) - 1:
            end = len(data)  # generated Segment may have unknown size
        if end > len(data):
            raise ValueError('element exceeds parent')
        yield ident, data[begin:end]
        at = end


def element(ident, body):
    return ident.to_bytes((ident.bit_length() + 7) // 8, 'big') + encode_vint(len(body)) + body


MASTERS = {0x18538067, 0x1549A966, 0x1654AE6B, 0xAE, 0xE0, 0xE1,
           0x1F43B675, 0xA0, 0x1941A469, 0x61A7, 0x1254C367, 0x7373,
           0x63C0, 0x67C8}
DROP = {0xBF, 0x114D9B74, 0x1C53BB6B, 0xA7, 0xAB}


def rewrite(data, mapping, reverse=False):
    pieces = []
    for ident, body in elements(data):
        if ident in DROP:
            continue
        if ident == 0xD7:
            number = mapping[int.from_bytes(body, 'big')]
            body = number.to_bytes(max(1, (number.bit_length() + 7) // 8), 'big')
        elif ident in (0xA3, 0xA1):
            old, width = vint(body, 0)
            body = encode_vint(mapping[old]) + body[width:]
        elif ident in MASTERS:
            body = rewrite(body, mapping, reverse)
        if ident == 0x1654AE6B and reverse:
            entries = list(elements(body))
            if any(i != 0xAE for i, _ in entries):
                raise ValueError('unexpected Tracks child')
            body = b''.join(element(i, b) for i, b in reversed(entries))
        pieces.append(element(ident, body))
    return b''.join(pieces)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--ffmpeg', default='ffmpeg')
    args = ap.parse_args()
    if args.output.exists():
        ap.error('output must be new')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.output.parent).free < 1024 ** 3 + 16 * 1024 ** 2:
        ap.error('1 GiB reserve required')
    args.output.mkdir()
    out = args.output.resolve()
    (out / 'subtitle.srt').write_text('1\n00:00:00,000 --> 00:00:01,500\nSynthetic identity control\n')
    def chunk(name, body):
        return struct.pack('>I', len(body)) + name + body + struct.pack('>I', zlib.crc32(name + body))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress((b'\x00' + bytes([255, 0, 0]) * 2) * 2)) + chunk(b'IEND', b'')
    (out / 'cover.png').write_bytes(png)
    command = [args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin',
               '-f', 'lavfi', '-i', 'color=c=red:s=64x48:r=12:d=2',
               '-f', 'lavfi', '-i', 'color=c=blue:s=64x48:r=12:d=2',
               '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
               '-i', 'subtitle.srt', '-map', '0:v', '-map', '1:v', '-map', '2:a', '-map', '3:s',
               '-c:v', 'libx264', '-threads:v', '1', '-pix_fmt', 'yuv420p', '-g', '12',
               '-c:a', 'aac', '-c:s', 'srt', '-attach', 'cover.png',
               '-metadata:s:t', 'mimetype=image/png', '-metadata:s:t', 'filename=cover.png', 'seed.mkv']
    run = subprocess.run(command, cwd=out, capture_output=True, text=True, timeout=30)
    (out / 'ffmpeg.log').write_text(run.stderr)
    run.check_returncode()
    seed = (out / 'seed.mkv').read_bytes()
    if len(seed) > 16 * 1024 ** 2:
        raise RuntimeError('fixture bound exceeded')
    cases = [('nonconsecutive', [7, 31, 47, 63], False, 'valid'),
             ('reordered', [7, 31, 47, 63], True, 'valid'),
             ('int-max', [7, 2147483647, 47, 63], False, 'valid'),
             ('too-large', [7, 2147483648, 47, 63], False, 'valid-unrepresentable-int'),
             ('duplicate', [7, 7, 47, 63], False, 'malformed-duplicate-number'),
             ('zero', [7, 0, 47, 63], False, 'malformed-zero-number')]
    records = []
    for name, numbers, reverse, validity in cases:
        path = out / (name + '.mkv')
        path.write_bytes(rewrite(seed, dict(zip(range(1, 5), numbers)), reverse))
        records.append({'file': path.name, 'track_numbers': numbers,
                        'reversed_entries': reverse, 'validity': validity,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {'generator': str(Path(__file__).resolve()), 'command': command,
                'tool_version': subprocess.check_output([args.ffmpeg, '-version'], text=True, timeout=5),
                'legal': 'Generated colors, sine wave, text subtitle and 2x2 PNG; no external media.',
                'ebml_policy': 'Reencode lengths and block TrackNumber VINTs; omit optional indexes and CRCs.',
                'cases': records}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'cases': len(records), 'output': str(out)}))


if __name__ == '__main__':
    main()
