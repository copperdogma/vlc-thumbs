#!/usr/bin/env python3
"""Four/arm diagnostic with existing feature trace and one3s owned-PID sample.

Instrumentation changes scheduling; these values never qualify p95 or serve
as the production comparison. The frozen player and control observer remain.
"""
import hashlib
from pathlib import Path
import subprocess
import sys

import baseline_control_trial as trial

SOURCE = Path(__file__).resolve()
_original_popen = subprocess.Popen
_original_capture = trial.Arm.capture
_original_fingerprints = trial.fingerprints
_profile = None
_handles = []
_profile_path = None


def popen(argv, *args, **kwargs):
    if isinstance(argv, (list, tuple)) and argv and str(argv[0]) == str(trial.WORK/'build/vlc-arm64/VLC.app/Contents/MacOS/VLC') and any(str(x).startswith('--rc-unix=') for x in argv):
        env = dict(kwargs.get('env') or {})
        config = next(str(x).split('=',1)[1] for x in argv if str(x).startswith('--config='))
        trace = Path(config).parent/'timeline-phase.jsonl'
        trace.touch(mode=0o600,exist_ok=False)
        env['VLC_TIMELINE_DIAGNOSTICS'] = str(trace)
        kwargs['env'] = env
    return _original_popen(argv, *args, **kwargs)


def capture(self, label, side, *args, **kwargs):
    global _profile, _profile_path
    self.args.state['scope'] = __doc__.strip()
    if self.name == 'feature' and '-click-' in label and _profile is None:
        _profile_path = self.out/'main-thread-sample.txt'
        for name in ['sample.stdout','sample.stderr']:
            _handles.append((self.out/name).open('xb'))
        _profile = _original_popen(['sample',str(self.process.pid),'3','1','-file',str(_profile_path)],stdout=_handles[0],stderr=_handles[1])
        self.actions.add({'kind':'profile_started','owned_pid':self.process.pid,'profiler_pid':_profile.pid,'path':str(_profile_path),'scope':'Diagnostic only; observer/profiler/trace affect scheduling'})
    return _original_capture(self,label,side,*args,**kwargs)


def fingerprints(args):
    r = _original_fingerprints(args)
    r['test:control_phase_diagnostic.py'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    return r


if __name__ == '__main__':
    if any(x.startswith('--samples') or x=='--observer-diagnostic' for x in sys.argv):
        raise SystemExit('This bounded diagnostic fixes4samples/arm and per-frame ownership')
    sys.argv += ['--samples','4']
    trial.Arm.capture = capture
    trial.fingerprints = fingerprints
    subprocess.Popen = popen
    try:
        code = trial.main()
    finally:
        if _profile:
            try: _profile.wait(timeout=15)
            except subprocess.TimeoutExpired:
                _profile.terminate()
                _profile.wait(timeout=3)
        for h in _handles: h.close()
        if _profile: print({'profile_returncode':_profile.returncode,'sample_exists':_profile_path.is_file(),'sample_bytes':_profile_path.stat().st_size if _profile_path.is_file() else 0})
    raise SystemExit(code)
