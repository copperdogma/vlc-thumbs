#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Generate a new, bounded directory of synthetic VLC preview diagnostics.

Python 3.8+ standard library; external FFmpeg/ffprobe with libx264 are required.
No video, font, network input, VLC library, or machine-specific path is used.
"""
import argparse
from contextlib import nullcontext
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

LIMIT = 300 * 1024 * 1024
RESERVE = 1024 ** 3
DURATION = 12
RATE = 24


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--output', type=Path, default=Path('work/story005-fixtures'))
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Refusing existing output directory; select a new --output')
    out = args.output.resolve()
    for key in ('ffmpeg', 'ffprobe'):
        executable = shutil.which(getattr(args, key))
        if executable is None:
            parser.error('Executable not found: ' + key)
        setattr(args, key, str(Path(executable).resolve()))
    # Validate tools before allocating any output. No implicit binary sibling paths.
    versions = {}
    for tool, executable in [('ffmpeg', args.ffmpeg), ('ffprobe', args.ffprobe)]:
        versions[tool] = subprocess.check_output(
            [executable, '-version'], text=True, timeout=15)
    out.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(out.parent).free < RESERVE + LIMIT:
        parser.error('Need 300 MiB allowance plus 1 GiB free reserve')
    try:
        out.mkdir(exist_ok=False)
    except FileExistsError:
        parser.error('Refusing existing output directory; select a new --output')
    commands = []

    def check_space():
        size = sum(path.stat().st_size for path in out.iterdir() if path.is_file())
        if size > LIMIT or shutil.disk_usage(out).free < RESERVE + LIMIT:
            raise RuntimeError('300 MiB output bound / 1 GiB reserve reached')
        return size

    def run(tool, argv, stdout_name=None):
        check_space()
        executable = args.ffmpeg if tool == 'ffmpeg' else args.ffprobe
        # Commands run inside the new directory and record portable relative names.
        commands.append({'tool': tool, 'argv': argv, 'stdout': stdout_name})
        with (out / stdout_name).open('xb') if stdout_name else nullcontext(subprocess.DEVNULL) as target:
            with (out / 'tool-stderr.log').open('ab') as errors:
                process = subprocess.Popen([executable] + argv, cwd=out,
                                           stdout=target, stderr=errors)
                started = time.monotonic()
                try:
                    while process.poll() is None:
                        check_space()
                        if time.monotonic() - started > 120:
                            raise RuntimeError('Tool exceeded 120-second command limit')
                        time.sleep(0.1)
                    check_space()
                    if process.returncode:
                        raise RuntimeError('%s failed; inspect tool-stderr.log' % tool)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()

    base = ['-nostdin', '-hide_banner', '-loglevel', 'error', '-n']
    encoder = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
               '-pix_fmt', 'yuv420p', '-threads', '2', '-g', '48',
               '-keyint_min', '48', '-sc_threshold', '0']
    source = ['-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=24:duration=12']
    tone = ['-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=12']
    fixtures = []

    def media(name, argv, description):
        # FFmpeg's file limit adds a per-output cap; monitor enforces aggregate bound.
        run('ffmpeg', base + argv + ['-fs', str(32 * 1024 * 1024), name])
        fixtures.append({'name': name, 'description': description})

    media('standard.mp4', source + tone + encoder + ['-c:a', 'alac', '-movflags', '+faststart'],
          '12 s testsrc2 320x180 24 fps; generated 440 Hz ALAC tone')
    media('standard.mkv', ['-i', 'standard.mp4', '-map', '0', '-c', 'copy'],
          'Same encoded video/audio as standard.mp4, Matroska container')
    long_encoder = encoder[:-6] + ['-g', '240', '-keyint_min', '240',
                                  '-sc_threshold', '0', '-bf', '3', '-b_strategy', '0']
    media('long-gop.mp4', source + long_encoder,
          '12 s testsrc2; ten-second GOP and three B-frames (verify actual frame map)')
    media('vfr.mkv', source + ['-vf', "select='if(lt(t,6),not(mod(n,2)),not(mod(n,3)))'",
                             '-fps_mode', 'vfr'] + encoder,
          '12 fps then 8 fps; selected original testsrc2 frames, variable PTS spacing')
    media('positive-start.mkv', ['-i', 'long-gop.mp4', '-c', 'copy', '-output_ts_offset', '5'],
          'Video PTS begins at +5 s; original pixels retained')
    media('edit-offset.mp4', ['-itsoffset', '2', '-i', 'long-gop.mp4'] + tone +
          ['-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'alac', '-use_editlist', '1'],
          'Video begins at +2 s; audio/container near zero (12 s audio, 14 s extent)')
    media('rotation.mp4', ['-display_rotation', '90', '-i', 'long-gop.mp4', '-c', 'copy'],
          '90-degree display matrix; encoded samples retain landscape geometry')
    media('sar.mp4', source + ['-vf', 'setsar=2/1'] + encoder,
          '320x180 coded samples, 2:1 SAR; intended display aspect 32:9')
    colors = []
    for color in ['red', 'blue']:
        colors += ['-f', 'lavfi', '-i', 'color=c=%s:size=320x180:rate=24:duration=12' % color]
    media('two-tracks.mkv', colors + ['-map', '0:v', '-map', '1:v'] + encoder +
          ['-metadata:s:v:0', 'title=synthetic-red', '-metadata:s:v:1', 'title=synthetic-blue',
           '-disposition:v:0', 'default', '-disposition:v:1', '0'],
          'Video ordinal 0 red/default; ordinal 1 blue. Ordinals are not VLC ES IDs')

    for record in fixtures:
        name = record['name']
        run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', name],
            name + '.probe.json')
        metadata = json.loads((out / (name + '.probe.json')).read_text())
        run('ffprobe', ['-v', 'error', '-select_streams', 'v', '-show_frames',
                       '-show_entries', 'frame=stream_index,pts,pts_time,best_effort_timestamp,best_effort_timestamp_time,duration_time,key_frame,pict_type',
                       '-of', 'json', name], name + '.frames.json')
        frame_map = json.loads((out / (name + '.frames.json')).read_text())['frames']
        record.update(bytes=(out / name).stat().st_size, sha256=sha256(out / name),
                      probe=name + '.probe.json', frames=name + '.frames.json', streams=[])
        for stream in metadata['streams']:
            if stream['codec_type'] != 'video':
                continue
            index = stream['index']
            frames = [frame for frame in frame_map if frame['stream_index'] == index]
            if not frames:
                raise RuntimeError('Missing decoded frames for %s stream %s' % (name, index))
            expected_count = 120 if name == 'vfr.mkv' else 288
            if len(frames) != expected_count:
                raise RuntimeError('Incomplete fixture: ' + name)
            prefix = name + '.v' + str(index)
            run('ffmpeg', base + ['-copyts', '-noautorotate', '-i', name, '-map', '0:' + str(index),
                                 '-an', '-fps_mode', 'passthrough', '-pix_fmt', 'rgba',
                                 '-c:v', 'rawvideo', '-f', 'framehash', '-hash', 'sha256', prefix + '.framehash'])
            previews = []
            for number in [0, len(frames) // 2, len(frames) - 1]:
                image = prefix + '.frame%03d.png' % number
                run('ffmpeg', base + ['-i', name, '-map', '0:' + str(index), '-an',
                                     '-vf', 'select=eq(n\\,%d),scale=w=trunc(min(320\\,180*dar)):h=trunc(min(180\\,320/dar)),setsar=1' % number,
                                     '-frames:v', '1', '-fps_mode', 'passthrough', image])
                previews.append({'decoded_frame_index': number, 'pts_time': frames[number].get('pts_time'),
                                 'name': image, 'sha256': sha256(out / image)})
            record['streams'].append({'index': index, 'frame_count': len(frames),
                                      'first_pts': frames[0].get('pts_time'),
                                      'last_pts': frames[-1].get('pts_time'),
                                      'keyframe_pts': [f.get('pts_time') for f in frames if f['key_frame']],
                                      'coded_rgba_framehash': prefix + '.framehash', 'display_examples': previews})
        print(name, record['bytes'], flush=True)

    # Check fixture properties from FFprobe, not merely command intent.
    by_name = {record['name']: record for record in fixtures}
    for name, expected in [('positive-start.mkv', 5), ('edit-offset.mp4', 2)]:
        if abs(float(by_name[name]['streams'][0]['first_pts']) - expected) > 0.05:
            raise RuntimeError('Requested positive video start not present: ' + name)
    rotation = json.loads((out / 'rotation.mp4.probe.json').read_text())['streams'][0]
    if not any(abs(side.get('rotation', 0)) == 90 for side in rotation.get('side_data_list', [])):
        raise RuntimeError('Rotation matrix missing')
    sar = json.loads((out / 'sar.mp4.probe.json').read_text())['streams'][0]
    if sar['sample_aspect_ratio'] != '2:1':
        raise RuntimeError('2:1 SAR missing')
    long_frames = json.loads((out / 'long-gop.mp4.frames.json').read_text())['frames']
    if [f['pts_time'] for f in long_frames if f['key_frame']] != ['0.000000', '10.000000']:
        raise RuntimeError('Ten-second GOP missing')
    if not any(frame['pict_type'] == 'B' for frame in long_frames):
        raise RuntimeError('B-frames missing')
    inventory = [{'name': path.name, 'bytes': path.stat().st_size, 'sha256': sha256(path)}
                 for path in sorted(out.iterdir()) if path.is_file()]
    manifest = {'schema_version': 1, 'generator_sha256': sha256(Path(__file__)),
                'duration_seconds': DURATION, 'nominal_frame_rate': RATE,
                'tools': versions, 'commands': commands, 'fixtures': fixtures, 'files': inventory,
                'bounds': {'max_output_bytes': LIMIT, 'min_free_reserve_bytes': RESERVE,
                           'max_command_seconds': 120},
                'oracle': 'FFprobe demux/decode PTS and FFmpeg coded RGBA SHA256; independent of VLC. '
                          'FFmpeg shares the generation toolchain: this is not an independent FFmpeg correctness proof. '
                          'Display PNGs apply autorotation and SAR; scaler/color differences prohibit exact cross-decoder hash acceptance.'}
    with (out / 'manifest.json').open('x') as target:
        json.dump(manifest, target, indent=2)
        target.write('\n')
    print('Total output bytes:', check_space())


if __name__ == '__main__':
    main()
