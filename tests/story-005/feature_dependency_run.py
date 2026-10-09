#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Capture direct ID/selectors/packet results; optional exact baseline parity.

No playback claim: this observes libavformat before video decoding. Malformed
controls are recorded separately from valid-input regressions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--probe', type=Path, required=True)
    ap.add_argument('--fixtures', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--baseline', type=Path)
    ap.add_argument('--expect-modified', action='store_true')
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((args.fixtures / 'manifest.json').read_text())
    report = {'probe': str(args.probe.resolve()), 'probe_sha256': sha(args.probe),
              'fixture_manifest_sha256': sha(args.fixtures / 'manifest.json'),
              'selectors': ['#0', '#7', 'i:7', '#31', 'i:31', '#47', '#63', '#2147483647'],
              'cases': [], 'pass': True}
    for case in manifest['cases']:
        path = args.fixtures / case['file']
        assert sha(path) == case['sha256']
        command = [str(args.probe.resolve()), str(path.resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        name = path.stem
        (args.output / (name + '.jsonl')).write_text(result.stdout)
        (args.output / (name + '.log')).write_text(result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        streams = [r for r in rows if 'selectors' in r]
        packets = [r for r in rows if 'packet' in r]
        measured = {'file': case['file'], 'validity': case['validity'], 'command': command,
                    'exit': result.returncode, 'streams': streams,
                    'packets': len(packets), 'groups': [r for r in rows if 'group' in r]}
        valid = case['validity'].startswith('valid')
        if valid:
            measured['valid_demux_eof'] = result.returncode == 0 and len(streams) == 5
            report['pass'] &= measured['valid_demux_eof']
            if args.expect_modified:
                numbers = list(case['track_numbers'])
                if case['reversed_entries']:
                    numbers.reverse()
                expected = [n if 0 < n <= 2147483647 else -1 for n in numbers] + [0]
                measured['expected_ids'] = expected
                measured['ids_match'] = [r['id'] for r in streams] == expected
                measured['selectors_match'] = all(r['selectors'] == [int(r['id'] == int(s.split(':')[-1].lstrip('#'))) for s in report['selectors']] for r in streams)
                report['pass'] &= measured['ids_match'] and measured['selectors_match']
            if args.baseline:
                old = [json.loads(line) for line in (args.baseline / (name + '.jsonl')).read_text().splitlines()]
                old_packets = [r for r in old if 'packet' in r]
                old_streams = [{k:v for k,v in r.items() if k not in ('id','selectors')} for r in old if 'selectors' in r]
                measured['packets_equal'] = old_packets == packets
                measured['stream_properties_equal'] = old_streams == [{k:v for k,v in r.items() if k not in ('id','selectors')} for r in streams]
                report['pass'] &= measured['packets_equal'] and measured['stream_properties_equal']
        else:
            measured['scope'] = 'Malformed input observation; no valid-input parity assertion.'
        report['cases'].append(measured)
    (args.output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'cases': len(report['cases']), 'output': str(args.output)}))
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
