#!/usr/bin/env python3
"""Eight/arm diagnostic: preposition800ms before unchanged move/down/up probe.

This isolates changed-hover presentation from a click while preserving the
strong per-frame ownership/pixel/timestamp guards. Not p95 qualification and
not a replacement for the original simultaneous move-and-click observations.
"""
import hashlib
from pathlib import Path
import sys
import time

import baseline_control_trial as trial
import playback_benchmark as playback

SOURCE = Path(__file__).resolve()
_original_capture = trial.Arm.capture
_original_fingerprints = trial.fingerprints


def capture(self, label, side, *args, **kwargs):
    self.args.state['scope'] = __doc__.strip()
    self.args.state['diagnostic_preposition_ms'] = 800
    begin = time.monotonic()
    point = trial.POINTS[side]
    playback.command(self.args.pointer, ['move', self.process.pid, *point])
    posted = time.monotonic()
    time.sleep(.8)
    self.actions.add({'kind': 'diagnostic_preposition', 'arm': self.name,
                      'capture_label': label, 'point': point,
                      'begin_uptime_s': begin, 'posted_uptime_s': posted,
                      'ready_uptime_s': time.monotonic(),
                      'scope': 'Pointer preposition only; not proof of preview settled state'})
    return _original_capture(self, label, side, *args, **kwargs)


def fingerprints(args):
    result = _original_fingerprints(args)
    result['test:prepositioned_control_diagnostic.py'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    return result


if __name__ == '__main__':
    if any(x in sys.argv for x in ['--samples', '--observer-diagnostic']):
        raise SystemExit('This bounded diagnostic fixes8samples/arm and per-frame ownership')
    sys.argv += ['--samples', '8']
    trial.Arm.capture = capture
    trial.fingerprints = fingerprints
    raise SystemExit(trial.main())
