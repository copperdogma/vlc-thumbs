#!/usr/bin/env python3
"""Generate owned Story 002 media; host FFmpeg is a research dependency only."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 300 * 1024 * 1024
RESERVE = 1024 ** 3


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ffmpeg', default='/usr/local/bin/ffmpeg')
    ap.add_argument('--output', type=Path, default=ROOT / 'work/fixtures/story-002')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'work'):
        ap.error('Generated media must be in this project ignored work directory')
    # Never regenerate over existing entries: a linked fixture or sidecar can
    # otherwise redirect FFmpeg/Python writes into source media outside work/.
    # A new directory also preserves the provenance of earlier fixture sets.
    try:
        out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        ap.error('Fixture output must be a new directory; choose a fresh --output')
    commands, records = [], []
    ffprobe = str(Path(args.ffmpeg).with_name('ffprobe'))
    version = subprocess.check_output([args.ffmpeg, '-version'], text=True)
    def check_space():
        size = sum(p.stat().st_size for p in out.glob('*') if p.is_file())
        if size > LIMIT or shutil.disk_usage(out).free < RESERVE + LIMIT:
            raise RuntimeError('300 MiB fixture bound / 1 GiB free reserve reached')
    def run(name, command, description):
        check_space()
        path = out / name
        argv = [args.ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-n'] + command + [str(path)]
        subprocess.run(argv, check=True, timeout=240)
        check_space()
        commands.append(argv)
        probe = subprocess.check_output([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])
        metadata = json.loads(probe)
        records.append({'name': name, 'description': description, 'bytes': path.stat().st_size,
                        'sha256': digest(path), 'probe': metadata})
        print(name, path.stat().st_size, flush=True)
    font = '/System/Library/Fonts/Supplemental/Arial.ttf'
    label = f"drawtext=fontfile='{font}':text='frame %{{n}} time %{{pts\\:hms}}':fontsize=36:fontcolor=white:box=1:boxcolor=black:x=20:y=20"
    def source(duration=8, size='640x360', rate=24):
        return ['-f', 'lavfi', '-i', f'testsrc2=size={size}:rate={rate}:duration={duration}']
    enc = ['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '27', '-pix_fmt', 'yuv420p', '-threads', '2']
    run('standard.mp4', source(60, '1920x1080') + ['-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=60',
        '-vf', label] + enc + ['-g', '48', '-c:a', 'alac', '-movflags', '+faststart'], '60 s 1080p24 with burned frame/time and generated ALAC tone (no AAC priming shift on remux)')
    run('standard.mkv', ['-i', str(out/'standard.mp4'), '-map', '0', '-c', 'copy'], 'Same video/audio bitstreams as standard.mp4')
    run('long-gop.mp4', source(12) + ['-vf', label] + enc + ['-g', '240', '-bf', '3'], '12 s, ten-second GOP, three B-frames')
    run('vfr.mkv', source(12) + ['-vf', label + ",select='if(lt(t,6),not(mod(n,2)),not(mod(n,3)))'", '-fps_mode', 'vfr'] + enc, 'VFR: 12 fps then 8 fps; original burned source frame numbers')
    run('nonzero.mkv', ['-i', str(out/'long-gop.mp4'), '-c', 'copy', '-output_ts_offset', '5'], 'Container and video start at +5 seconds')
    run('edit-offset.mp4', ['-itsoffset', '2', '-i', str(out/'long-gop.mp4'), '-f', 'lavfi', '-i', 'sine=frequency=880:duration=14', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-use_editlist', '1'], 'Video starts at +2 s while audio/container start near zero; initial video gap')
    run('rotation.mp4', ['-display_rotation', '90', '-i', str(out/'long-gop.mp4'), '-c', 'copy'], '90-degree display matrix, landscape encoded samples')
    run('sar.mp4', source() + ['-vf', label + ',setsar=2/1'] + enc, '640x360 encoded pixels, 2:1 SAR, 32:9 display aspect')
    run('two-tracks.mkv', ['-f', 'lavfi', '-i', 'color=c=red:size=640x360:rate=24:duration=8', '-f', 'lavfi', '-i', 'color=c=blue:size=640x360:rate=24:duration=8', '-map', '0:v', '-map', '1:v'] + enc, 'Video ordinal 0 red, ordinal 1 blue')
    run('audio-only.m4a', ['-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', '-c:a', 'aac'], 'No video stream')
    run('hdr-tagged.mp4', source(2, '320x180', 12) + enc + ['-color_trc', 'smpte2084', '-color_primaries', 'bt2020', '-colorspace', 'bt2020nc'], 'Synthetic ordinary samples tagged PQ/BT2020 to verify explicit unsupported-presentation rejection; not an HDR quality golden')
    run('short-4k.mp4', source(3, '3840x2160', 12) + ['-vf', label] + enc + ['-g', '24'], 'Three-second 4K diagnostic stress')
    run('five-minute.mp4', source(300, '320x180', 12) + ['-vf', label] + enc + ['-g', '600', '-bf', '3'], 'Five-minute low-resolution fifty-second GOP stress; not standard latency')
    corrupt = out / 'corrupt.mp4'
    with corrupt.open('xb') as f:
        f.write(b'Story 002 intentionally corrupt synthetic video\x00' * 8)
    records.append({'name': corrupt.name, 'description': 'Invalid synthetic bytes', 'bytes': corrupt.stat().st_size, 'sha256': digest(corrupt)})
    truncated = out / 'truncated.mp4'
    with (out / 'standard.mp4').open('rb') as f:
        with truncated.open('xb') as target:
            target.write(f.read(512))
    records.append({'name': truncated.name, 'description': 'First 512 bytes of owned standard.mp4; incomplete MP4 header', 'bytes': truncated.stat().st_size, 'sha256': digest(truncated)})
    # Frame map is independent of helper reporting. Keep verbose map in ignored work.
    for record in records:
        if record['name'] in ('corrupt.mp4', 'audio-only.m4a', 'truncated.mp4'):
            continue
        frames = subprocess.check_output([ffprobe, '-v', 'error', '-select_streams', 'v', '-show_frames', '-show_entries', 'frame=stream_index,best_effort_timestamp_time,pkt_duration_time,key_frame,pict_type', '-of', 'json', str(out / record['name'])])
        with (out / (record['name'] + '.frames.json')).open('xb') as target:
            target.write(frames)
    metadata = {'generator': str(Path(__file__).relative_to(ROOT)), 'ffmpeg_version': version,
                'commands': commands, 'total_media_bytes': sum(r['bytes'] for r in records), 'fixtures': records}
    with (out / 'generation.json').open('x') as target:
        target.write(json.dumps(metadata, indent=2) + '\n')
    print('Generated bytes:', metadata['total_media_bytes'])


if __name__ == '__main__':
    main()
