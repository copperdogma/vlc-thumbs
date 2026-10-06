#!/usr/bin/env python3
"""Apply the timeline integration only to the pinned, mutable VLC checkout."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PIN = '6de05adcbaf2e8b85fe86aad4169393098628119'
SOURCE = ROOT / 'work/build/vlc-source'
PATCH = ROOT / 'patches/vlc-3.0.24/0001-native-timeline-previews.patch'


def owned_path(path):
    """Reject symlink escapes, including an entire symlinked work directory."""
    path = pathlib.Path(path)
    if path.resolve() != path.absolute() or not path.is_relative_to(ROOT / 'work/build'):
        raise RuntimeError('Build path must remain inside the owned work/build tree: ' + str(path))
    return path


def git(*args, check=True):
    return subprocess.run(['git', '-C', str(SOURCE), *args], check=check,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def inspect():
    owned_path(SOURCE)
    if git('rev-parse', 'HEAD').stdout.strip() != PIN:
        raise RuntimeError('Mutable VLC checkout does not match the qualified source pin')
    changed = git('apply', '--numstat', str(PATCH)).stdout.splitlines()
    if not changed:
        raise RuntimeError('Timeline patch is empty')
    for line in changed:
        name = line.split('\t', 2)[-1]
        if not name.startswith('modules/gui/macosx/') or '..' in pathlib.PurePosixPath(name).parts:
            raise RuntimeError('Patch may modify only the macOS UI module: ' + name)
        owned_path(SOURCE / name)
    files = sorted((ROOT / 'src/macosx').glob('*'))
    if not files:
        raise RuntimeError('Canonical native sources are missing')
    for path in files:
        if path.is_symlink() or not path.is_file() or path.suffix not in ('.h', '.m'):
            raise RuntimeError('Unexpected native source entry: ' + str(path))
        owned_path(SOURCE / 'modules/gui/macosx' / path.name)
    forward = git('apply', '--check', str(PATCH), check=False)
    reverse = git('apply', '--reverse', '--check', str(PATCH), check=False)
    if forward.returncode == 0:
        status = 'ready-to-apply'
    elif reverse.returncode == 0:
        status = 'already-applied'
    else:
        raise RuntimeError('Patch is neither cleanly applicable nor already applied; preserve local edits and inspect:\n' + forward.stderr)
    return status, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only pin, path and patch checks')
    args = parser.parse_args()
    status, files = inspect()
    if not args.check:
        if status == 'ready-to-apply':
            git('apply', str(PATCH))
        for path in files:
            shutil.copyfile(path, SOURCE / 'modules/gui/macosx' / path.name)
    print(json.dumps({'source_pin': PIN, 'patch_status': status, 'check_only': args.check,
                      'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in [PATCH, *files]}}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
