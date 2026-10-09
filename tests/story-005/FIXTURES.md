# Portable synthetic preview fixtures

`generate_fixtures.py` is a standalone Python 3.8+ standard-library program.
Supply FFmpeg and ffprobe on PATH, or pass `--ffmpeg` and `--ffprobe` separately.
FFmpeg must provide lavfi testsrc2/color/sine, libx264, ALAC, PNG, framehash and
`-fps_mode`. The local qualification records the exact tested tool versions;
other versions need regeneration and a new manifest. No VLC build is required.

```sh
python3 tests/story-005/generate_fixtures.py --output work/story005-fixtures
```

Run from the repository root to use that default ignored destination. From a
standalone copied script, choose an explicit fresh scratch directory. An existing
directory is rejected, including an empty directory or symlink. There is no
cleanup/overwrite option. Failed runs retain their artifacts and tool log for
inspection; choose another directory for a retry. Generation never changes media
outside its newly created output directory. Output is limited to 300 MiB, with
an additional 1 GiB disk reserve. Commands have a 120-second deadline; aggregate
size/free space is checked every 100 ms while they run and between commands.
Each encoded output additionally has FFmpeg's 32 MiB cap. Polling can overshoot a
threshold during one interval; this is a conservative working bound, not an OS
quota. A truncated cap-limited encode is not a successful complete fixture set.

| Fixture | Diagnostic purpose |
| --- | --- |
| `standard.mp4`, `standard.mkv` | 12 s 320×180 24 fps testsrc2, generated ALAC tone; remuxed identical encoded streams |
| `long-gop.mp4` | Ten-second GOP, fixed three B-frames; actual keyframes and presentation order recorded |
| `vfr.mkv` | Selected source frames: 12 fps for first six seconds, then 8 fps |
| `positive-start.mkv` | First video PTS +5 s; container timeline origin differs from zero |
| `edit-offset.mp4` | First video PTS +2 s and audio near zero; MP4 edit-list origin and initial gap |
| `rotation.mp4` | Display matrix rotates 90°; encoded landscape pixels preserved |
| `sar.mp4` | 2:1 sample aspect ratio, intended 32:9 display aspect |
| `two-tracks.mkv` | Red default video and blue second video, explicit titles and dispositions |

All inputs are lavfi mathematical patterns or remuxes of those generated outputs.
There are no downloaded videos, subtitles, fonts, private media or external assets.
This generator uses no drawtext or font files. Red/blue distinguish selected tracks;
testsrc2's moving asymmetric patterns distinguish frames and display transforms.
A solid-color track proves selection but cannot identify which frame was returned.

The new directory contains `manifest.json`, per-file FFprobe stream/format JSON,
all-frame PTS/keyframe/picture-type JSON, and per-video-stream RGBA framehash files.
Framehash commands disable autorotation, preserve timestamps (`-copyts`) and
request passthrough frame cadence. These SHA256 hashes describe decoded coded
samples, with time bases in each framehash header. Presentation timestamps and
keyframe maps come from FFprobe and must be compared in the recorded time base,
not assumed to equal elapsed time since container open. A container's duration
can include the positive offset. The manifest records exact tool version output,
portable argv (relative to the output directory), media and artifact SHA256 hashes,
frame counts, first/last video PTS and keyframe PTS. It excludes its own hash.

Three PNG examples per video stream use the first, middle and last decoded frame
indices, apply FFmpeg autorotation and fit display aspect inside 320×180. Their
frame indices and source PTS are explicit. To investigate an arbitrary probe
result, decode its candidate frame index with the same recorded PNG command;
choose a separate new output file. Positive-start/edit-offset sources intentionally
reuse long-GOP pixels, so correspondence can be checked against both timelines.
Do not infer VLC's ES string ID from FFprobe index, menu ordinal or Matroska
TrackNumber; obtain it through the pinned VLC enumeration/source contract.

The oracle is FFprobe/FFmpeg, independent of the VLC preparser caller and VLC
picture timestamps. Because generation and reference decode share FFmpeg, it
does not independently certify FFmpeg itself. RGBA hashes identify exact reference
frames; VLC colorspace conversion/scaling may differ, so cross-decoder hash
mismatch alone is not a fidelity defect. Match visible patterns, source time and
geometry, then document any numerical pixel comparison and tolerance. Generation
is fixture provenance, not a VLC correctness/performance or native-UI pass.
Codec/container coverage is intentionally small; no HDR, corrupt-file, exhaustive
format, slow-storage or live-network behavior is qualified by this set.

The generator source declares LGPL-2.1-or-later, matching the neighboring probe's
source license. Generated mathematical patterns contain no third-party assets;
this source/asset inventory is not a legal opinion on codec patents or FFmpeg
binary redistribution. Record the actual FFmpeg build's license separately if
redistributing its binary; source packaging does not need to ship tools/media.

Technique references: [FFmpeg stream mapping, timestamps, streamcopy and metadata](https://ffmpeg.org/ffmpeg.html),
[FFprobe stream/frame fields](https://ffmpeg.org/ffprobe.html),
[FFmpeg testsrc2, color, sine, select, scale and setsar filters](https://ffmpeg.org/ffmpeg-filters.html),
[FFmpeg framehash output](https://ffmpeg.org/ffmpeg-formats.html#framehash).
The choice is a small synthetic source plus an external decoder oracle, with
actual local timestamp/transform properties checked after generation.
