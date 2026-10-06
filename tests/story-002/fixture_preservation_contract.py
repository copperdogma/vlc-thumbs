#!/usr/bin/env python3
"""Existing linked fixtures and sidecars must be rejected before encoder launch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT/'work')
    out.mkdir(parents=True, exist_ok=False)
    original = out/'synthetic-original.bin'
    original.write_bytes(b'Generated source preservation sentinel\n'*100)
    before = digest(original)
    marker = out/'encoder-was-called'
    encoder = out/'fake-ffmpeg'
    encoder.write_text('#!/usr/bin/env python3\nfrom pathlib import Path\nPath('+repr(str(marker))+').write_text("called")\n')
    encoder.chmod(0o700)
    checks = []
    for name, leaf, hard in [('linked-media', 'standard.mp4', False),
                             ('linked-sidecar', 'generation.json', False),
                             ('hardlinked-media', 'corrupt.mp4', True)]:
        directory = out/name
        directory.mkdir()
        target = directory/leaf
        if hard:
            os.link(original, target)
        else:
            target.symlink_to(original)
        run = subprocess.run([sys.executable, str(ROOT/'scripts/generate-thumbnail-fixtures.py'),
                              '--ffmpeg', str(encoder), '--output', str(directory)],
                             capture_output=True, text=True, timeout=5)
        passed = (run.returncode != 0 and 'must be a new directory' in run.stderr
                  and not marker.exists() and digest(original) == before)
        checks.append({'case': name, 'pass': passed, 'exit': run.returncode,
                       'stderr': run.stderr, 'original_sha256_after': digest(original),
                       'encoder_called': marker.exists()})
    result = {'scope': 'Only generated sentinel media; reject existing output before encoder/Python writes',
              'generator_sha256': digest(ROOT/'scripts/generate-thumbnail-fixtures.py'),
              'original_sha256': before, 'checks': checks, 'pass': all(c['pass'] for c in checks)}
    (out/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(checks)}))
    raise SystemExit(0 if result['pass'] else 1)

if __name__ == '__main__':
    main()
