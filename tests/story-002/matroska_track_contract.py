#!/usr/bin/env python3
"""TrackNumber mapping preserves selected colors across reversed TrackEntries."""
import argparse
import json
from pathlib import Path
from helper_contract import call, sha

ROOT = Path(__file__).resolve().parents[2]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--helper', type=Path, required=True)
    ap.add_argument('--source', type=Path, default=ROOT / 'work/fixtures/story-002/two-tracks.mkv')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / 'work')
    out.mkdir(parents=True, exist_ok=False)
    result = {'scope': 'Owned AVC multi-video Matroska identity/order regression and count mismatch rejection; not general codec qualification',
              'helper_sha256': sha(args.helper), 'source_sha256': sha(args.source), 'checks': [], 'pass': False}
    try:
        assert args.source.stat().st_size < 20 * 1024**2
        data = bytearray(args.source.read_bytes())
        def vint(at, ident=False):
            assert 0 <= at < len(data) and data[at]
            size = 1
            while not data[at] & (1 << (8-size)):
                size += 1
                assert size <= 8
            assert at + size <= len(data)
            value = int.from_bytes(data[at:at+size], 'big')
            return (value if ident else value & ((1 << (7*size))-1)), size
        def elements(start, end):
            while start < end:
                ident, n = vint(start, True)
                size, m = vint(start+n)
                body = start+n+m
                assert body+size <= end
                yield ident, start, body, body+size
                start = body+size
        changed = False
        for ident, _, start, end in elements(0, len(data)):
            if ident != 0x18538067:
                continue
            for ident, _, start, end in elements(start, end):
                if ident != 0x1654ae6b:
                    continue
                entries = list(elements(start, end))
                tracks = [bytes(data[a:b]) for ident, a, _, b in entries if ident == 0xae]
                assert len(tracks) == 2
                others = []
                for ident, a, body, b in entries:
                    if ident == 0xae:
                        continue
                    # Void replaces the old checksum without changing offsets.
                    if ident == 0xbf:
                        assert b-a == 6
                        others.append(b'\xec\x84\x00\x00\x00\x00')
                    else:
                        others.append(bytes(data[a:b]))
                replacement = b''.join(others + list(reversed(tracks)))
                assert len(replacement) == end-start
                data[start:end] = replacement
                changed = True
        assert changed
        reversed_media = out / 'reversed-tracks.mkv'
        reversed_media.write_bytes(data)
        result['reordered_sha256'] = sha(reversed_media)
        ordinal_hashes = {}
        for media in (args.source, reversed_media):
            for ordinal in (0, 1):
                measured, payload = call(args.helper.resolve(), media.resolve(), 4., ordinal, video_count=2)
                assert measured['header']['ok']
                assert measured['header']['video_track_number'] == ordinal + 1
                rgb = list(payload[:3])
                assert (rgb[0] > 200 and rgb[2] < 30) if ordinal == 0 else (rgb[2] > 200 and rgb[0] < 30), rgb
                if ordinal in ordinal_hashes:
                    assert ordinal_hashes[ordinal] == measured['payload_sha256']
                ordinal_hashes[ordinal] = measured['payload_sha256']
                measured['first_rgb'] = rgb
                result['checks'].append({'media': str(media), 'ordinal': ordinal, 'pass': True, **measured})
        mismatch, pixels = call(args.helper.resolve(), reversed_media, 4., 0, video_count=1)
        assert mismatch['header'] == {'version': 2, 'ok': False, 'error': 'ambiguous_track_mapping'} and not pixels
        result['checks'].append({'case': 'native-count-mismatch', 'pass': True, **mismatch})
        assert sha(args.source) == result['source_sha256']
        assert sha(args.helper) == result['helper_sha256']
        result['pass'] = True
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        (out/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(result['checks']), 'error': result.get('error')}))
    raise SystemExit(0 if result['pass'] else 1)

if __name__ == '__main__':
    main()
