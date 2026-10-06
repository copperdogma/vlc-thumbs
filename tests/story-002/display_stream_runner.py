"""Supplement an owned VLC window stream with a bounded actual display crop.

The parent owns media playback and active-interval selection. This observer
never activates an application or sends pointer/input events.
"""
import json
from pathlib import Path
import subprocess
import threading
import time


def collect(observer, pointer, pid, window, screen_file, stop, result, out, seconds, process_ids):
    from playback_benchmark import command, digest, stamp, terminate
    capture = None
    stderr_handle = None
    try:
        frames = []
        for line in screen_file.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get('kind') == 'frame' and 'roi_pixels' in row:
                frames.append(row)
        if not frames:
            raise RuntimeError('No window-stream reference frame before actual display capture')
        frame = frames[0]
        px, py, pw, ph = frame['roi_pixels']; bw, bh = frame['buffer_size']; bounds = window['bounds']
        rect = [bounds['X'] + px / bw * bounds['Width'], bounds['Y'] + py / bh * bounds['Height'],
                pw / bw * bounds['Width'], ph / bh * bounds['Height']]
        out.mkdir()
        argv = [str(observer), '--pid', str(pid), '--window-id', str(window['id']),
                '--output', str(out), '--duration', str(seconds + 5), '--fps', '60',
                '--roi', '0,0,1,1', '--display-rect', ','.join(map(str, rect))]
        result.update(rect_screen_points=rect, window=window, observer_sha256=digest(observer),
                      reference_window_frame=frame, command=argv, errors=[], focus_checks=[],
                      scope='Actual display sourceRect matching burned-counter ROI; screen pixels only, no audio/microphone/whole-desktop archive. No automatic attribution.')
        stderr_handle = (out / 'observer.stderr').open('x')
        capture = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=stderr_handle, text=True)
        process_ids.append(capture.pid)
        result['observer_pid'] = capture.pid
        lines = []
        ready_signal = threading.Event()
        def read_ready():
            lines.append(capture.stdout.readline()); ready_signal.set()
        reader = threading.Thread(target=read_ready, daemon=True); reader.start()
        if not ready_signal.wait(10) or not lines or not lines[0]:
            raise RuntimeError('Display stream did not provide ready within10s')
        ready = json.loads(lines[0])
        if ready.get('event') != 'ready' or ready.get('pid') != pid:
            raise RuntimeError('Unexpected actual display stream ready record')
        result['capture_ready'] = ready
        while capture.poll() is None and not stop.wait(.25):
            focus = json.loads(command(pointer, ['focus', pid]))
            windows = json.loads(command(pointer, ['inspect', pid]))
            current = next((w for w in windows if w['id'] == window['id']), None)
            result['focus_checks'].append({'at': stamp(), 'focus': focus, 'window_bounds': current['bounds'] if current else None})
            if not focus.get('app_active') or not current or current['bounds'] != bounds:
                raise RuntimeError('Actual display observer lost active owned application or fixed geometry')
        capture.wait(timeout=20)
        (out / 'observer.stdout').write_text(lines[0] + capture.stdout.read())
        result['exit_code'] = capture.returncode
        if capture.returncode:
            raise RuntimeError('Actual display stream exited unsuccessfully')
        if not (out / 'summary.json').is_file():
            raise RuntimeError('Actual display stream did not finalize summary')
        result['finished'] = stamp()
    except Exception as error:
        result.setdefault('errors', []).append(str(error)); stop.set()
    finally:
        terminate(capture)
        if stderr_handle:
            stderr_handle.close()
