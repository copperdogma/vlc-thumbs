# Native macOS timeline keyframe previews

**READY for bounded pre-submission review of Phases1/2; no submission.** The whole story remains InProgress; Phase3 is not authorized. Hovering
VLC's timeline shows an image and its actual **Keyframe** time, helping users
inspect a scene before seeking. Pointer time remains the seek target. An
Interface preference disables previews; unsupported media retains ordinary time
hover. Bookmarks are outside this contribution.

## Apply and review

Base commit: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Combined tree: `b7c0f24e442c35a57bb108d56b801fd05b624943`.
Feature midpoint: `cce7f9917b8dc4d5432e7f83b2c840f8c3c5027b`.

Apply all thirteen entries in [contribution-series](contribution-series) once
from the pinned source root. **P** denotes `blocker-prerequisites/`; **F** denotes
`feature-series/`. The exact order is:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

P0006–7 depend on feature-created
regression tests; the prerequisite component cannot be applied contiguously
first. No independent whole-prerequisite build is qualified. The
[manifest](contribution-manifest.json) records every patch and intermediate tree,
72 combined paths, and 59 feature paths with six prerequisite overlaps.

Start with the [feature overview](feature-series/README.md). F0000 covers source
distribution; F0001–2 cover FFmpeg contrib and the private helper/build boundary;
F0003 covers cache/scheduler/worker ownership; F0004 covers player context, native
hover and preferences. [Prerequisites](blocker-prerequisites/README.md) address
build/distribution, clock/TLS/GL, ownership, termination and control hit testing.
Maintainer agreement on submission boundaries and FFmpeg ownership remains open.

## Validation and limits

The exact combined tree passes the normal build and complete registered
`make check`. The rebuilt helper passes all 77 matrix checks and retains
`-Wbad-function-cast` with zero warnings in that targeted class; broader warning
classes are unqualified.

Complete conventional `make distcheck` passes through final cleanup. Recorded optional skips remain; nested native counts overlap registered suites.

Normal/isolated packages, signatures and all 398 loadables pass qualification; two-fixture helper relocation passes.

Paused main-window and fullscreen hover pass across24.7 and33.2 sampled seconds. Returned-main thumbnail/seekbar persistence is observed; ordinary title/buttons fade. Upstream ordinary fade occurrence is inherited, while current fade cause and broader preview lifecycle remain unknown. Earlier actual main Position-to-Pause/Play reader navigation retains its narrow inherited scope. Current preview-visible/fullscreen VoiceOver is unmeasured; latest practical navigation was inconclusive, with no established defect. Autonomous reader setup stopped.

Accurate exposed media position, precision seeking and other fullscreen and reader
coverage remain unqualified. Intermittent shutdown causality remains unresolved;
bounded Quit observations establish neither crash frequency nor a causal fix.
Three current matched60s AB/BA/AB pairs pass bounded playback/preparation/audio/drop/resource qualification. All native frame/audio loss counters are zero; candidate-minus-baseline sampled mean CPU is+1.47/+2.20/+2.29 percentage points and combined sampled maximum RSS is+100.3/+100.6/+97.6MiB. Recorder overhead is measured separately. Complete pair1 was retained across a human-permission pause; the interrupted second pair was excluded and its failed cohort remains failed. System-mixed AAC/PCM continuity, variable-rate capture observations and sampled resources retain their limits; no per-app callback or universal smoothness claim follows. Intel, older macOS and CI execution are unavailable.

Regular local files, including mounted NAS files, qualify; URLs do not. Selected
video mapping and bounded flat-Matroska admission fail closed for unsupported
cases. Freshness uses metadata plus sampled SHA256; unsampled changes may escape
detection. See [limitations](feature-series/LIMITATIONS.md) for exact scope.
[Historical screenshots](feature-series/demonstration/README.md) illustrate earlier
rendering and do not qualify this tree's native behavior.

## Reproduce and credit

Follow the [build/test and GUI host instructions](feature-series/README.md) after
applying the aggregate series. The patched source's `bin/timeline-preview/README.md`
and `bin/timeline-preview/tests/README.md` describe contrib setup and fixtures.
Public normal-build/check commands passed in stages; the full public recipe,
including outer distcheck, remains **unexecuted**. Archive checks used a read-only
preflight forwarding unchanged argv/status to the ordinary upstream test driver.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance. Retain VLC GPL/LGPL and third-party notices; credit asserts no sole
ownership, assignment, waiver or sign-off. No binaries or private media are
included. Maintainer acceptance remains separate.
