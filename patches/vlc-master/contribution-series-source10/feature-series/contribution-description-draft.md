# Proposed contribution description

**READY for bounded pre-submission review of Phases1/2; no submission.** The whole story remains InProgress; Phase3 is not authorized.

This contribution adds keyframe previews to VLC's native macOS timeline so users
can inspect a scene before seeking. The hover panel shows the image and
its keyframe time; pointer time remains the seek target. Previews default
on, have an Interface preference, and fall back to ordinary time hover for
unsupported media or failures. Bookmarks are outside this series.

The player context supplies selected-video identity and an input epoch. A service
owns scheduling, stale-result cancellation and 32 MiB RAM/256 MiB disk caches.
Serial metadata and decode queues use retained private worker processes built
through the existing FFmpeg contrib rules. Workers isolate movie-time sampling without changing normal demuxing.
The retained helper follows measured movie-time and retained-session requirements.
A future core thumbnail extension is an alternative for maintainers to consider;
no endorsement is assumed.

Only regular local files, including mounted NAS files, qualify. Flat Matroska requires exact, unique TrackNumber mapping; bounded admission rejects
unsupported timelines. Fresh reopen requalifies metadata plus sampled SHA256,
which cannot detect every unsampled change. Provisional images share a 15-second
deadline that pointer activity cannot renew.

The combined tree passes normal build/full registered `make check` and all
77 helper matrix checks. Compilation retains `-Wbad-function-cast` with zero
warnings in that targeted class. Complete conventional `make distcheck` passes through final cleanup. Recorded optional skips remain; nested native counts overlap registered suites. Normal/isolated packages, signatures and all 398 loadables pass qualification; two-fixture helper relocation passes.

Paused main/fullscreen hover passes narrowly. Returned-main thumbnail/seekbar persistence is observed; ordinary title/buttons fade. Upstream ordinary fade occurrence is inherited, while current fade cause and broader preview lifecycle remain unknown. Earlier actual main Position-to-Pause/Play reader navigation retains its narrow inherited scope. Current preview-visible/fullscreen VoiceOver is unmeasured; latest practical navigation was inconclusive, with no established defect. Autonomous reader setup stopped. Three current matched60s AB/BA/AB pairs pass bounded playback/preparation/audio/drop/resource qualification. All native frame/audio loss counters are zero; candidate-minus-baseline sampled mean CPU is+1.47/+2.20/+2.29 percentage points and combined sampled maximum RSS is+100.3/+100.6/+97.6MiB. Recorder overhead is measured separately. Complete pair1 was retained across a human-permission pause; the interrupted second pair was excluded and its failed cohort remains failed. System-mixed AAC/PCM continuity, variable-rate capture observations and sampled resources retain their limits; no per-app callback or universal smoothness claim follows. Accurate exposed position, precision seeking, broader reader
coverage, intermittent shutdown causality and unavailable Intel/older-macOS/CI
coverage remain disclosed in [limitations](LIMITATIONS.md). Public normal-build/check
commands passed in stages; the full public recipe, including outer distcheck,
remains unexecuted. The [review map](README.md) and
[historical screenshots](demonstration/README.md) provide context; screenshots
illustrate earlier builds and do not qualify current native behavior.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance under retained GPL/LGPL and third-party notices. Credit asserts no
sole ownership, assignment, waiver or sign-off. Maintainer acceptance and patch
boundaries remain open.
