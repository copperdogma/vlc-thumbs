#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Build only an isolated copied helper against a supplied VLC contrib prefix."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--prefix', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--private-avformat', type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
if shutil.disk_usage(args.output).free < 1024 ** 3:
    parser.error('Less than 1 GiB free')
environment = dict(os.environ, PKG_CONFIG_LIBDIR=str(args.prefix / 'lib/pkgconfig'),
                   PKG_CONFIG_PATH='')
flags_command = ['pkg-config', '--static', '--cflags', '--libs',
                 'libavformat', 'libavcodec', 'libavutil', 'libswscale']
flags = shlex.split(subprocess.check_output(flags_command, env=environment,
                                          text=True, timeout=15))
if args.private_avformat:
    assert flags.count('-lavformat') == 1
    flags = [str(args.private_avformat.resolve()) if flag == '-lavformat' else flag
             for flag in flags]
command = ['xcrun', 'clang', '-arch', 'arm64', '-mmacosx-version-min=10.13',
           '-std=c11', '-Os', '-Wall', '-Wextra', '-Werror',
           '-Wl,-dead_strip', '-Wl,-S', str(args.source.resolve()),
           '-o', str((args.output / 'thumbnail-helper').resolve()), *flags]
result = subprocess.run(command, env=environment, capture_output=True, text=True,
                        timeout=60)
(args.output / 'build.log').write_text(result.stdout + result.stderr)
inputs = [args.source, Path(__file__)]
inputs += sorted((args.prefix / 'lib').glob('libav*.a'))
inputs += [args.prefix / 'lib/libswscale.a']
if args.private_avformat:
    inputs.append(args.private_avformat)
report = {'command': command, 'pkg_config_command': flags_command,
          'prefix': str(args.prefix.resolve()), 'status': result.returncode,
          'sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in inputs}}
binary = args.output / 'thumbnail-helper'
if result.returncode == 0:
    report['binary_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
    report['file'] = subprocess.check_output(['file', str(binary)], text=True)
    report['linkage'] = subprocess.check_output(['otool', '-L', str(binary)], text=True)
    report['bytes'] = binary.stat().st_size
(args.output / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': result.returncode, 'output': str(args.output),
                  'binary_sha256': report.get('binary_sha256')}))
raise SystemExit(result.returncode)
