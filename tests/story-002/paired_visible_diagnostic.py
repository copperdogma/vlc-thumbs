#!/usr/bin/env python3
"""Bounded AB/BA observer-load experiment, never percentile qualification.

Owns one development VLC process. Generates prior-generation heavy-observer
sRGB templates, ordinarily reopens, and prewarms every scored target in RAM.
Twenty target pairs alternate heavy/buffered order. Each starts from the same
RAM-resident calibration160 caption and requires exact image/time/keyframe,
paused-zero state, AX Position, focus and geometry preservation. All attempts,
including errors, are retained. No product mutation or installed VLC control.

The buffered arm measures500ms with pre/post scene guards. It cannot prove
per-frame ownership equivalence or qualify a product latency budget. Comparison
is diagnostic: pairing isolates observer work imperfectly because live AppKit,
WindowServer, OS scheduling and capture callbacks remain nondeterministic.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import re
import socket
import stat
import subprocess
import time

import continuous_hover_trial as continuous
from continuous_hover_trial import Trial, WORK, ORDER, finite, json_write, metadata_record
import native_hover_benchmark as hover
import playback_benchmark as playback
from native_hover_trial import bundle_digest


class PairedTrial(Trial):
    arm = 'heavy'
    sequence = 0

    def capture(self, record, bucket, **kwargs):
        self.sequence += 1
        record['name'] = f'{self.sequence:03}-{self.arm}-{record["name"]}'
        record['observer_arm'] = self.arm
        self.args.probe = self.args.heavy_probe if self.arm == 'heavy' else self.args.buffered_probe
        result = super().capture(record, bucket, **kwargs)
        costs = [row['callback_work_ms'] for row in result[0] if 'callback_work_ms' in row]
        if self.arm == 'buffered' and not costs:
            raise RuntimeError('Buffered observer omitted callback-work diagnostics')
        if costs:
            record['callback_work_ms'] = {'count': len(costs), 'maximum': max(costs),
                                          'median': hover.percentile(costs, .5), 'p95_diagnostic_only': hover.percentile(costs, .95)}
        return result

    def focus_guard(self):
        observed = json.loads(self.pointer('focus'))
        if not observed.get('app_active'):
            raise RuntimeError('Owned development VLC inactive before/after scored capture')
        expected = self.state.get('reference_focus')
        if expected is None:
            self.state['reference_focus'] = observed
        elif observed != expected:
            raise RuntimeError('Focus or window geometry changed: ' + str(observed))
        return observed

    def reset_caption(self):
        before = len(self.events())
        self.pointer('move', *self.point(160))
        evidence = self.trace_request(before, 160, 'memory')
        # Native assignment is a setup condition, not the scored visible event.
        # Independently settled reference160 exists; wait for rendering stability.
        time.sleep(.15)
        self.actions.add({'kind': 'same_RAM_calibration_separator', 'trace': evidence})


def summarize_pairs(records):
    pairs = []
    for i in sorted({r['pair_index'] for r in records if 'pair_index' in r}):
        group = [r for r in records if r.get('pair_index') == i]
        row = {'index': i, 'attempt_count': len(group), 'all_attempts_correct': len(group) == 2 and not any(r['faults'] for r in group)}
        by_arm = {r.get('observer_arm'): r for r in group}
        if row['all_attempts_correct'] and all(a in by_arm and 'visible' in by_arm[a] for a in ['heavy', 'buffered']):
            row['bucket'] = group[0]['bucket']
            row['order'] = [r['observer_arm'] for r in group]
            for metric in ['image_and_time_visible_ms', 'time_visible_ms']:
                row[metric] = {a: by_arm[a]['visible'][metric] for a in ['heavy', 'buffered']}
                row[metric]['heavy_minus_buffered'] = row[metric]['heavy'] - row[metric]['buffered']
        pairs.append(row)
    correct = [p for p in pairs if p['all_attempts_correct'] and 'image_and_time_visible_ms' in p]
    summary = {'pairs': pairs, 'complete_correct_pairs': len(correct), 'no_qualification_claim': True}
    # Diagnostic medians, retaining all raw pairs. Never omit a bad pair silently.
    if len(correct) == len(pairs) and pairs:
        for metric in ['image_and_time_visible_ms', 'time_visible_ms']:
            values = [p[metric]['heavy_minus_buffered'] for p in correct]
            summary[metric + '_paired_delta_median_ms'] = hover.percentile(values, .5)
            summary[metric + '_pairs_improved_at_least_one_60Hz_interval'] = sum(v >= 1000 / 60 for v in values)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ['app', 'media', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--media-json', type=Path)
    parser.add_argument('--pairs', type=int, default=20, help='1..20; below20 is applicability only')
    parser.add_argument('--heavy-probe', type=Path, default=WORK / 'validation/story002/continuous-visible-capture-probe')
    parser.add_argument('--buffered-probe', type=Path, default=WORK / 'validation/story002/buffered-visible-capture-probe')
    parser.add_argument('--pointer', type=Path, default=WORK / 'validation/story002/native-pointer')
    args = parser.parse_args()
    try:
        for name in ['app', 'media', 'output', 'heavy_probe', 'buffered_probe', 'pointer']:
            setattr(args, name, hover.owned(getattr(args, name)))
        if args.output.exists() or args.output.is_symlink() or not 1 <= args.pairs <= 20:
            raise ValueError('Fresh output and1..20 pairs required')
        if args.media.parent != WORK / 'fixtures/story-002' or args.media.name not in ['standard-cache-pressure.mp4', 'standard-cache-pressure.mkv']:
            raise ValueError('Only generated standard-cache-pressure MP4/MKV allowed')
        if not args.app.is_dir() or not args.media.is_file() or not all(p.is_file() and os.access(p, os.X_OK) for p in [args.pointer, args.heavy_probe, args.buffered_probe]):
            raise ValueError('Existing development app, fixture and executable probes/pointer required')
        with (args.app / 'Contents/Info.plist').open('rb') as handle:
            info = plistlib.load(handle)
        if info.get('CFBundleIdentifier') != playback.BUNDLE_ID:
            raise ValueError('Isolated development bundle required')
        executable = hover.owned(args.app / 'Contents/MacOS' / info.get('CFBundleExecutable', 'VLC'))
        plugin = hover.owned(args.app / 'Contents/MacOS/plugins/libmacosx_plugin.dylib')
        if any(str(executable) in line for line in subprocess.check_output(['ps', '-axo', 'command='], text=True).splitlines()):
            raise ValueError('Requested app already running; existing processes never stopped')
        source_sha = playback.digest(args.media)
        metadata = None
        candidates = [hover.owned(args.media_json)] if args.media_json else [WORK / 'validation/story002/cache-pressure-regeneration-1931.json', WORK / 'validation/story002/cache-pressure-fixtures.json']
        for candidate in candidates:
            if not candidate.is_file():
                continue
            try:
                metadata = metadata_record(candidate, args.media, source_sha)
                args.media_json = candidate
                break
            except ValueError:
                continue
        if metadata is None:
            raise ValueError('Current fixture SHA must match generated-fixture metadata')
        metadata_duration = float(metadata.get('probe', {}).get('format', {}).get('duration', metadata.get('duration_seconds', 0)))
        if args.duration is None:
            args.duration = metadata_duration
        if not finite(args.duration) or not 80.25 < args.duration <= 91 or metadata_duration and abs(metadata_duration - args.duration) > .05:
            raise ValueError('Verified fixture duration required, covering80.1s and <=91s')
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.probe = args.heavy_probe
    args.output.mkdir(parents=True)
    actions, attempts, rc_log = [playback.Log(args.output / name) for name in ['actions.jsonl', 'attempts.jsonl', 'rc.jsonl']]
    state = {'schema_version': 1, 'diagnostic_only': True, 'qualification_eligible': False, 'guard_equivalence_proven': False,
             'scope': 'Main-window20 paired prewarmed-RAM heavy/buffered ScreenCaptureKit observer-load experiment',
             'limits': ['Buffered ownership is pre/post only; transient changes unobserved', 'System-generated pointer and WindowServer display_time; not physical scanout',
                        'Uncontrolled OS/cache/scheduling effects', 'No overhead subtraction or product threshold changes'],
             'app': str(args.app), 'media': str(args.media), 'duration_seconds': args.duration, 'requested_pairs': args.pairs,
             'target_buckets': ORDER[:args.pairs], 'attempts': [], 'started': playback.stamp(),
             'source_sha256_before': source_sha, 'module_sha256_before': playback.digest(plugin),
             'app_tree_sha256_before': bundle_digest(args.app, playback.digest), 'pointer_sha256_before': playback.digest(args.pointer),
             'heavy_probe_sha256_before': playback.digest(args.heavy_probe), 'buffered_probe_sha256_before': playback.digest(args.buffered_probe),
             'media_json_sha256': playback.digest(args.media_json), 'runner_sha256': playback.digest(Path(__file__)),
             'observer_source_sha256': playback.digest(Path(__file__).with_name('buffered_visible_probe.m')),
             'imported_runner_sha256': playback.digest(Path(continuous.__file__))}
    trial = PairedTrial(args, state, actions, attempts)
    stdout = stderr = None
    try:
        if trial.socket_path.exists() or trial.socket_path.is_symlink():
            raise RuntimeError('Existing socket refused')
        argv = [str(executable), '--ignore-config', f'--config={args.output / "vlcrc"}', '--intf=macosx', '--extraintf=oldrc',
                f'--rc-unix={trial.socket_path}', '--rc-fake-tty', '--stats', '--play-and-pause', '--start-time=0', '--no-media-library',
                '--no-metadata-network-access', '--macosx-control-itunes=0', '--no-macosx-mediakeys', '--no-macosx-recentitems',
                '--macosx-continue-playback=2', '--no-video-title-show', '--no-loop', '--no-repeat', '--no-random', '--verbose=2', str(args.media)]
        help_result = subprocess.run([str(executable), '--longhelp', '--advanced', '--help-verbose'], capture_output=True, text=True, timeout=10)
        (args.output / 'compiled-options.txt').write_text(help_result.stdout)
        (args.output / 'compiled-options.stderr').write_text(help_result.stderr)
        declared = set(re.findall(r'--([a-z][a-z0-9-]*)', help_result.stdout))
        missing = sorted({a[2:].split('=', 1)[0] for a in argv[1:] if a.startswith('--')} - declared)
        state['argument_validation'] = {'returncode': help_result.returncode, 'missing_options': missing}
        if help_result.returncode or missing:
            raise RuntimeError('Compiled app options invalid')
        stdout, stderr = [(args.output / name).open('xb') for name in ['app.stdout', 'app.stderr']]
        trial.process = subprocess.Popen(argv, env=dict(os.environ, VLC_TIMELINE_DIAGNOSTICS=str(trial.trace)),
                                         stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
        state.update(pid=trial.process.pid, app_command=argv)
        trial.sock = socket.socket(socket.AF_UNIX)
        deadline = time.monotonic() + 12
        while True:
            if trial.process.poll() is not None:
                raise RuntimeError('Owned app exited before RC')
            try:
                trial.sock.connect(str(trial.socket_path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() >= deadline:
                    raise RuntimeError('RC startup timeout')
                time.sleep(.1)
        trial.sock.settimeout(.2)
        trial.rc = playback.RC(trial.sock, rc_log)
        state['startup_paused'] = playback.paused_zero(trial.rc, actions, timeout=12)
        trial.pointer('activate')
        time.sleep(.4)
        trial.geometry()
        trial.reopen()
        calibration = trial.calibrate('prior-template-generation')
        trial.attempt('template', 160, existing_trace=calibration)
        for bucket in ORDER[:args.pairs]:
            trial.attempt('template', bucket)
        json_write(args.output / 'templates.json', {'templates': trial.templates, 'prior_generation_only': True})
        trial.generation = None
        prior = trial.reopen()
        trial.calibrate('fresh-RAM-generation')
        if trial.generation in prior:
            raise RuntimeError('Ordinary reopen did not create fresh generation')
        # Seed every target once, using real requests. Scored trace then must
        # explicitly say memory, even though templates warmed earlier OS caches.
        for bucket in ORDER[:args.pairs]:
            before = len(trial.events())
            trial.pointer('move', *trial.point(bucket))
            evidence = trial.trace_request(before, bucket, 'miss')
            actions.add({'kind': 'RAM-prewarm', 'bucket': bucket, 'trace': evidence})
        state['initial_rc'] = trial.observe_paused()
        _, inventory = playback.slider_rect(args.pointer, trial.process.pid)
        positions = [float(line.split(' value ')[1].split(' title ')[0]) for line in inventory.splitlines() if line.endswith('title Position') and ' value ' in line]
        if len(positions) != 1:
            raise RuntimeError('One AX Position required')
        state['initial_ax_position'] = positions[0]
        trial.focus_guard()
        for i, bucket in enumerate(ORDER[:args.pairs]):
            for arm in (['heavy', 'buffered'] if i % 2 == 0 else ['buffered', 'heavy']):
                trial.reset_caption()
                focus_before = trial.focus_guard()
                trial.arm = arm
                before_count = len(state['attempts'])
                try:
                    trial.attempt('memory', bucket, trial.templates['160'])
                finally:
                    # Trial retains the attempt even on exceptions.
                    if len(state['attempts']) > before_count:
                        record = state['attempts'][-1]
                        record.update(pair_index=i, observer_arm=arm, focus_before=focus_before)
                        try:
                            record['focus_after'] = trial.focus_guard()
                        except Exception as error:
                            record['faults'].append(str(error))
                            raise
                        # Retain enriched attempt without rewriting append-only log.
                        actions.add({'kind': 'paired-attempt-completed', 'attempt': record})
        state['final_rc'] = trial.observe_paused()
        state['completed_collection'] = True
    except Exception as error:
        state.update(completed_collection=False, collection_error=str(error))
        actions.add({'kind': 'collection_error', 'error': str(error)})
    finally:
        if trial.rc:
            try:
                trial.rc.send(['quit'])
            except OSError:
                pass
            trial.rc.stop.set()
            trial.rc.sock.close()
            trial.rc.thread.join(timeout=2)
        elif trial.sock:
            trial.sock.close()
        playback.terminate(trial.process)
        if trial.process and trial.socket_path.exists() and stat.S_ISSOCK(trial.socket_path.lstat().st_mode):
            trial.socket_path.unlink()
        for handle in [stdout, stderr]:
            if handle:
                handle.close()
        for field, path in [('source', args.media), ('module', plugin), ('pointer', args.pointer), ('heavy_probe', args.heavy_probe), ('buffered_probe', args.buffered_probe)]:
            state[field + '_sha256_after'] = playback.digest(path)
            state[field + '_unchanged'] = state[field + '_sha256_after'] == state[field + '_sha256_before']
        state['app_tree_sha256_after'] = bundle_digest(args.app, playback.digest)
        state['app_unchanged'] = state['app_tree_sha256_after'] == state['app_tree_sha256_before']
        state['pair_summary'] = summarize_pairs(state['attempts'])
        integrity = all(state[k + '_unchanged'] for k in ['source', 'module', 'pointer', 'heavy_probe', 'buffered_probe', 'app'])
        state['diagnostic_collection_passed'] = bool(state.get('completed_collection') and integrity and state['pair_summary']['complete_correct_pairs'] == args.pairs)
        state['all_attempts_retained'] = True
        state['qualified'] = False
        state['finished'] = playback.stamp()
        json_write(args.output / 'summary.json', state)
        for log in [actions, attempts, rc_log]:
            log.file.close()
        print(json.dumps({'summary': str(args.output / 'summary.json'), 'diagnostic_collection_passed': state['diagnostic_collection_passed'],
                          'qualified': False, 'error': state.get('collection_error')}), flush=True)
    return 0 if state['diagnostic_collection_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
