# Standalone AVFoundation thumbnail planning probe

2026-10-04 UTC. Planning evidence only; no VLC feature/plugin edits.

This directory is an archival copy of the ignored `work/probes/thumbnail-plan`
experiment. Run scripts derive the repository root from that original layout;
do not execute them inside docs/evidence. To repeat without overwriting evidence,
copy probe.m, libav-probe.c, run.py and run-libav.py to a fresh
`work/probes/<new-name>/` directory, run run.py there, then run-libav.py against
the existing contrib prefix. The original absolute command logs/hashes remain
unchanged. Binaries/media and most output PNGs remain ignored; this archive
retains one representative H.264 PNG plus source/results/provenance.

Host: macOS 27.0 (26A428). Probe: arm64, built with xcrun clang and Apple
Foundation/AVFoundation/CoreMedia/CoreGraphics/ImageIO/CoreServices frameworks.
VLC baseline: 3.0.24 at 6de05adcbaf2e8b85fe86aad4169393098628119.

`run.py` contains exact generation/compile/invocation commands; `commands.json`
records arguments, exit status, stdout/stderr and wall times. Outputs occupy
approximately 1.1 MB. Sum of measured command execution time was 14.18 seconds.
The script intentionally refuses to overwrite existing generated media.

Fixtures:
- Generated 8-second, 24 fps, 320x180 H.264 MP4, readable burned-in frame/time;
  libx264 veryfast/CRF22, GOP48, YUV420P, silent.
- MKV created from that MP4 with the same encoded H.264 stream (`-c copy`).
- Existing build-smoke.mp4: 3-second, 12 fps, MPEG-4 synthetic fixture.

Probe uses one fresh AVURLAsset/AVAssetImageGenerator per process/media and
sequential asynchronous single requests through the batch Objective-C API.
Maximum320x180; appliesPreferredTrackTransform=YES; before/after tolerance0.05s.
No product cache exists. Callback latency is measured before PNG encoding;
first open-to-callback latency also includes asset/generator initialization.
Each request has a5-second timeout; none timed out.

| Fixture | Requested seconds, in order | Actual seconds | Request latency ms |
| --- | --- | --- | --- |
| H.264 MP4 | 0.5,7.25,2.3,6.75,2.3 | 0.5,7.25,2.291667,6.75,2.291667 | 179.57,53.35,26.22,36.41,26.73 |
| H.264 MKV | 0.5,7.25,2.3,6.75,2.3 | all failed | 4.15,0.09,0.06,0.06,0.05 |
| MPEG-4 MP4 | 0.5,2.25,1.3,1.75,1.3 | 0.5,2.25,1.25,1.75,1.25 | 288.21,28.52,23.25,29.28,22.96 |

H.264 first open-to-callback197.24ms; MPEG-4 first304.49ms.
All ten successful images are320x180. MKV failures were
AVFoundationErrorDomain/-11828, Cannot Open. This is one measured MKV case,
not a universal container/codec claim.

Visual inspection of all five H.264 output PNGs confirmed burned-in labels:
frame12/t00:00:00.500, frame174/t00:00:07.250, frame55/t00:00:02.292,
frame162/t00:00:06.750, frame55/t00:00:02.292. The repeated target depicts
identical frame/time. Returned API timestamps match these rendered labels
within their display rounding. MPEG-4 smoke lacks readable burned-in labels;
its results demonstrate successful extraction/API time only.

Limits: first-request/fresh-generator timing is not cold disk or cold OS timing:
generated files had just been written/read by FFmpeg. Subsequent requests reuse
the generator but are not feature-cache hits. Five requests per fixture do not
establish percentiles, duration/format breadth, cancellation, resource bounds,
playback impact or native timeline/fullscreen interaction. Host FFmpeg8.0 is
x86_64 GPL/version3 and research-only; it is not an arm64 packaged helper.
No installed VLC, real annotation store or source project was changed.

`sha256.json` records media/probe/result hashes. `integrity-check.json` rechecks
these after extraction. Existing build-smoke hash matches the original fixture
record (bc71b544440458feb68f0ba880428468dc3601021ed4b13ed8a5d48a171f10b3).
