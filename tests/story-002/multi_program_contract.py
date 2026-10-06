#!/usr/bin/env python3
"""Prove program-local ordinal ambiguity is unavailable, not a guessed image."""
import argparse
import json
from pathlib import Path
import subprocess
from helper_contract import call, sha

ROOT = Path(__file__).resolve().parents[2]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--helper', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--ffmpeg', default='/usr/local/bin/ffmpeg')
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / 'work'), 'Generated fixtures must stay in owned work/'
    out.mkdir(parents=True, exist_ok=False)
    result = {'scope': 'Generated MPEG-TS program/ordinal regression; not broad TS qualification',
              'helper_sha256': sha(args.helper), 'fixtures': [], 'checks': [], 'pass': False}
    try:
        for multiple in (False, True):
            media = out / ('multiple.ts' if multiple else 'single.ts')
            argv = [args.ffmpeg, '-nostdin', '-v', 'error', '-f', 'lavfi', '-i',
                    'color=c=red:s=640x360:r=12:d=4', '-f', 'lavfi', '-i',
                    'color=c=blue:s=640x360:r=12:d=4', '-map', '0:v', '-map', '1:v',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-g', '1', '-threads', '2']
            argv += (['-program', 'program_num=1:st=0', '-program', 'program_num=2:st=1']
                     if multiple else ['-program', 'program_num=1:st=0:st=1'])
            argv += ['-f', 'mpegts', str(media)]
            subprocess.run(argv, check=True, capture_output=True, timeout=30)
            assert media.stat().st_size < 20 * 1024**2
            digest = sha(media)
            result['fixtures'].append({'path': str(media), 'sha256': digest, 'argv': argv})
            for ordinal in (0, 1):
                measured, pixels = call(args.helper.resolve(), media, 1.5, ordinal)
                header = measured['header']
                if multiple:
                    assert header == {'version': 2, 'ok': False, 'error': 'ambiguous_track_mapping'}
                    assert not pixels
                else:
                    assert header['ok']
                    rgb = list(pixels[len(pixels)//8*4:len(pixels)//8*4+3])
                    assert (rgb[0] > 200 and rgb[2] < 30) if ordinal == 0 else (rgb[2] > 200 and rgb[0] < 30), rgb
                    measured['center_rgb'] = rgb
                result['checks'].append({'multiple_programs': multiple, 'ordinal': ordinal,
                                         'pass': True, **measured})
            assert sha(media) == digest
        assert sha(args.helper) == result['helper_sha256']
        result['pass'] = True
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(result['checks']), 'error': result.get('error')}))
    raise SystemExit(0 if result['pass'] else 1)

if __name__ == '__main__':
    main()
