#!/usr/bin/env python3
"""Generated track-count ambiguity regression; no private media or GUI claims."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, default=ROOT/'work/build/thumbnail-helper/thumbnail-helper')
    parser.add_argument('--output', type=Path, default=ROOT/'work/validation/story004/track-count-contract.json')
    parser.add_argument('--native-vlc', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {'helper_sha256': hashlib.sha256(args.helper.read_bytes()).hexdigest(), 'checks': [],
              'scope': 'Generated MP4 mismatch plus single-video MP4/Matroska count safety; v2/v3. Optional native demux qualification, not physical-pointer proof.'}
    with tempfile.TemporaryDirectory(prefix='track-count-', dir=ROOT/'work/validation/story004') as directory:
        folder = Path(directory)
        multi, single, mkv = folder/'multi.mp4', folder/'single.mp4', folder/'single.mkv'
        subprocess.run(['/usr/local/bin/ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'color=c=red:s=640x360:r=24:d=2', '-f', 'lavfi', '-i', 'color=c=blue:s=640x360:r=24:d=2',
                        '-map', '0:v', '-map', '1:v', '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '2',
                        '-pix_fmt', 'yuv420p', str(multi)], check=True)
        subprocess.run(['/usr/local/bin/ffmpeg', '-v', 'error', '-y', '-i', str(multi), '-map', '0:v:1', '-c', 'copy', str(single)], check=True)
        subprocess.run(['/usr/local/bin/ffmpeg', '-v', 'error', '-y', '-i', str(single), '-c', 'copy', str(mkv)], check=True)
        # Unknown video media header causes VLC's MP4 demux to omit the first
        # track while libav still recognizes its encoded video samples.
        raw = bytearray(multi.read_bytes())
        header = raw.index(b'vmhd')
        raw[header:header+4] = b'zzzz'
        # Ensure the remaining blue video track is enabled for native playback.
        tracks = [i for i in range(len(raw)) if raw[i:i+4] == b'tkhd']
        assert len(tracks) == 2
        raw[tracks[1]+7] |= 1
        multi.write_bytes(raw)
        if args.native_vlc:
            run = subprocess.run([str(args.native_vlc), '--intf=dummy', '--ignore-config', '--no-audio',
                                  '--vout=dummy', '--no-video-title-show', '--play-and-exit', '-vv', str(multi)],
                                 capture_output=True, timeout=20)
            log = run.stderr.decode(errors='replace')
            observations = [line for line in log.splitlines() if any(token in line for token in
                            ['ignoring track[', 'adding track[', 'using video decoder module'])]
            native_ok = run.returncode == 0 and 'ignoring track[Id 0x1]' in log and 'adding track[Id 0x2] video (enable)' in log and 'using video decoder module' in log
            result['checks'].append({'name': 'native omits first track and decodes second', 'pass': native_ok, 'observations': observations})
        for path, count, expected in [(multi, 1, False), (single, 2, False), (mkv, 2, False),
                                      (single, 1, True), (mkv, 1, True)]:
            for version in [2, 3]:
                base = [str(args.helper), '--input', str(path), '--video-ordinal', '0', '--video-count', str(count), '--max-width', '320', '--max-height', '180']
                argv = [base[0], '--worker', *base[1:]] if version == 3 else [*base, '--time-us', '1000000']
                run = subprocess.run(argv, input=b'1 1000000\n' if version == 3 else None, capture_output=True, timeout=18)
                pieces = run.stdout.split(b'\n', 2)
                first = json.loads(pieces[0])
                response = json.loads(pieces[1]) if version == 3 and first.get('ok') else first
                pixels = pieces[2] if version == 3 and first.get('ok') else (pieces[1] if len(pieces)>1 else b'')
                if expected:
                    passed = response.get('ok') is True and len(pixels) >= 4 and pixels[2] > 200 and pixels[0] < 20 and run.returncode == 0
                else:
                    passed = response.get('ok') is False and response.get('error') == 'ambiguous_track_mapping' and response.get('payload_bytes', 0) == 0 and not pixels
                result['checks'].append({'name': f'{path.name} count={count} v{version}', 'pass': passed,
                                         'response': response, 'first_pixel_rgba': list(pixels[:4]), 'exit_code': run.returncode})
    result['pass'] = all(check['pass'] for check in result['checks'])
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(result['checks']), 'output': str(args.output)}))
    raise SystemExit(0 if result['pass'] else 1)


if __name__ == '__main__':
    main()
