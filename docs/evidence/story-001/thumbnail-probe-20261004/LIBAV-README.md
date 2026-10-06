# Direct contrib libav thumbnail feasibility probe

2026-10-04 UTC, macOS27.0/26A428. Planning evidence only. This follow-up tests a
single private helper using existing pinned VLC contrib libraries; no upstream,
plugin, installed-app or user-store edits.

`run-libav.py` obtains only the existing contrib .pc dependencies with isolated
PKG_CONFIG_LIBDIR and invokes xcrun clang. Its exact argv/results live in
libav-commands.json. It compiles arm64, minimum macOS11.0, SDK27.0, links static
libavformat/libavcodec/libavutil/libswscale, dead-strips and removes debug symbols.
Helper size17,199,704bytes (~16.4MiB), no non-system dynamic dependencies.
Together with the previous probe the directory remains below30MB.

Runtime/installed/source version all FFmpeg8.1.2. .pc versions:
libavformat62.12.102,libavcodec62.28.102,libavutil60.26.102,libswscale9.5.102.
Contrib archive is FFmpeg8.1.2 from VLC3.0.24's pinned contrib rules and checksums.
libav-build-provenance.json records configure flags, .pc files, media hashes.
config.h flags: GPL0,VERSION3=0,NONFREE=0,VIDEOTOOLBOX=0.
Runtime avcodec_license reports LGPL2.1 or later.

Dependency link flags additionally pull zlib,gsm,mp3lame,openjpeg,math,pthreads,
AudioToolbox,CoreFoundation,CoreVideo,CoreMedia. Current otool dependencies contain
only libSystem and these Apple frameworks: other contrib libraries are static.
Original contrib configuration requests deployment10.7, but arm64 helper has
actual LC_BUILD_VERSION minimum11.0; this is not an older-OS compatibility test.

Probe opens/parses file, selects video stream, opens software decoder with one
thread; seeks backward to a keyframe using av_seek_frame, flushes the decoder,
decodes forward, accepts first frame whose best_effort_timestamp>=target, scales
to320x180 RGB via swscale and hashes pixels. It exposes timestamp and timebase.
Five sequential out-of-order targets include one repeat. This tiny source is an
availability probe; it lacks production EAGAIN/error/recovery, aspect/rotation,
color-management, arbitrary stream-start semantics, resource/time/cancellation,
IPC and application-bundle contracts. Do not promote it directly to production.

| Fixture | Open ms | Seek/decode/scale per request ms | Actual seconds |
| --- | --- | --- | --- |
| H.264 MP4 | 2.351 | 2.597,5.138,1.922,3.357,1.814 | 0.5,7.25,2.333333,6.75,2.333333 |
| Same-stream H.264 MKV | 0.733 | 2.382,4.656,1.819,4.007,1.772 | 0.5,7.25,2.333,6.75,2.333 |
| MPEG-4 smoke | 0.611 | 0.781,0.585,0.560,0.654,0.430 | 0.5,2.25,1.333333,1.75,1.333333 |

All15 requests successfully sought, decoded and scaled180rows. Requested2.3s
chooses the first frame at/after target, unlike the AV probe's preceding frame;
that is an explicit probe policy, not a decoder error. At each tested target,
MP4 and MKV RGB MD5 hashes are identical despite different timebases; repeated
targets repeat the same RGB hash. All media hashes still match previous records.

FFmpeg AVFrame.best_effort_timestamp (installed libavutil/frame.h:693-698) is
estimated using heuristics and expressed in stream timebase; it is not a promise
that malformed/missing-timestamp inputs have trustworthy source timing. Installed
avformat.h:2295-2309 describes keyframe seek; avcodec_flush_buffers resets decoder
state. Missing/ambiguous PTS and VLC-vs-stream time-origin disagreement need
explicit failure/qualification tests.

Planning judgment: prefer one private arm64 helper using these already pinned
contrib libraries for the first thumbnail story. It has per-frame timestamps,
passes the concrete MP4+MKV fixture pair and avoids both public LibVLC linking/
frame-PTS ambiguity and AVFoundation+fallback duplication. A persistent worker
could reuse open/decoder state and support cancellation by termination; the
actual IPC and scheduling design remains implementation work. CONFIG_VIDEOTOOLBOX0
means these measurements are software decode of very small fixtures; 4K/long-GOP
and playback competition remain unqualified.

Private-development helper packaging is straightforward from this inventory,
not proven as a shipped app. Resolve helper through the app bundle, compile it
from the same contrib build, include it in bundle signing, verify isolation and
termination, and record exact source/dependency configuration. Static linking
adds license/source/relink obligations if distributed; LGPL baseline and disabled
GPL/nonfree flags do not by themselves prove all dependency distribution terms.
Inspect matching FFmpeg and gsm/LAME/OpenJPEG/zlib licenses and preserve source/
patches/build recipes before any public packaging decision. No distribution done.

Fresh process/library open timing is not cold-disk latency, no PNG/IPC/native-UI
cost is included and there are no percentile, playback or broad-format claims.
