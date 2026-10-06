# NAS thumbnail latency investigation — 2026-10-05

Cam reported a black Loading preview followed by Preview unavailable after
roughly five to ten seconds on a large MP4 on an SMB volume over Wi-Fi. This
pass is diagnosis and design discussion, not an implementation decision.
The general problem is interactive random access to remote media, aggravated
by repeated initialization and cancellation of in-flight work.

Follow-up: Cam requested [Story 004](../stories/story-004-responsive-reusable-thumbnails.md)
on the same day, adopting hover-centered priority, finishing bounded active
work, earliest-missing preparation when not hovering, and persistent cache reuse
as planned behavior. The story owns acceptance and the identity/lifecycle ADR
gate; no product implementation is implied by this investigation.

## Observed scope

The supplied file is 9,064,004,044 bytes (8.442 GiB), H.264, 1920×1036, about
108 minutes, on a mounted `smbfs` volume. Its name/path and diagnostic outputs
stay in ignored `work/validation/nas-preview-20261005/`. No media was written,
copied wholesale, or uploaded. No app or product source was changed.

The installed helper hash is
`cbbd6784deb18501eddccf4d695dbd7b39c3ef27b14374fa34209d638d6b836f`, matching
build 155231. Current helper, service, and controller sources match that build's
manifest. A direct invocation of the installed helper at 1493 seconds succeeded
in 0.465 seconds, returning one 320×172 keyframe at 1488.570411 seconds.

Instrumentation-only copies of the helper were compiled under ignored work
using the same source/library build command, with stage/read counters added.
The five-second deadline and extraction algorithm were retained. These are
helper probes, not native UI latency observations or cold-cache benchmarks.
OS/NAS cache state and competing host/network activity were uncontrolled.

| Target | Process wall time | Outcome |
| --- | --- | --- |
| 1493s, installed helper | 0.465s | Success |
| 1493s, stage instrumentation | 6.828s | Explicit `timeout` error |
| 3200s, stage instrumentation | 3.266s | Success, actual 3199.905033s |
| 6000s, stage instrumentation | 1.382s | Success, actual 5998.409078s |
| 4600s, read instrumentation | 4.134s | Success, actual 4596.425167s |

For the 4600s probe, instrumented helper stages occupied 3.652 seconds, of which
3.522 seconds were inside `read()` calls. Scaling occupied 1.209ms. The helper
read 11,999,229 bytes through 305 read calls and processed 163 selected-video
packets, including three key-marked packets, before returning its first decoded
frame. These are bytes returned by file reads, not measured network traffic;
kernel caching can satisfy reads. The remaining process wall time is outside
the instrumented stage interval and is not attributed.

Container opening alone read 6,524,178 bytes. A bounded top-level MP4 atom walk
found `ftyp`, then a 9,057,545,370-byte `mdat`, then a 6,458,642-byte `moov` at the
end of the file. This explains substantial index/header work on opening; the
mere presence of a tail `moov` does not establish that moving it would solve
preview latency. The probe does not scan the whole 9GB file.

The timeout probe completed container opening/stream discovery/seeking, then
expired before returning a keyframe. The successful read-timed probe establishes
file reads as the dominant measured cost for that request. It does not isolate
Wi-Fi, SMB server, client cache, or host scheduling as separate causes. The
original native UI incident has no captured trace, so its exact failure remains
unattributed; the same extraction path demonstrably can time out on this file.

## Current implementation

- **Keyframes still need decoding.** They are compressed video frames, not
  pre-rendered small images. The helper backward-seeks, sets
  `AVDISCARD_NONKEY`, decodes a source-sized frame, and scales to fit 320×180.
  Skipping decoding of other frames does not skip every intervening read or
  guarantee immediate decoder output; the packet counts above demonstrate this.
- **Demand only.** Hover triggers extraction. No background generation,
  prewarming, neighboring-keyframe prefetch, or whole-timeline index is built.
- **Repeated initialization.** Each cache miss launches a new helper and opens
  the file, parses container data, discovers streams, creates a decoder, seeks,
  reads/decodes, scales, and exits. The playback input remains independent.
- **Cancellation amplification.** Each delivered mouse move schedules a refresh
  that resets `_demand`/`_generation` and cancels the current request. The 16 ms
  timer coalesces a burst, but the later same-bucket guard cannot preserve an
  already-running request after that reset. Even movement within the same
  half-second bucket can restart work. A stationary pointer does not do this.
- **Caching exists, with limits.** Successful small RGBA results enter 32 MiB
  memory and 256 MiB local disk caches. Keys contain canonical URL, stat fingerprint,
  media-open generation, track/count and half-second requested time. Different
  buckets can independently decode the same keyframe. A new media-open
  generation prevents cross-open reuse, including after restarting the app.
  File-state checks also occur on cache hits; there is no full-video content hash.
- **Five-second failure policy.** Both helper and service enforce a five-second
  limit. The service collapses nonzero helper exits and several underlying errors
  into `decode-unavailable`; the UI presents Preview unavailable and a blank
  image. An expired request does not establish an absent/unsupported keyframe.
  Failures are not cached as successful thumbnails. No automatic stationary retry
  follows a failed completion.

Source pointers: `src/macosx/VLCThumbnailService.m` (fingerprint/cache keys,
process lifecycle and deadlines), `VLCTimelineContext.m` (fresh generation),
`VLCTimelineInteractionController.m` (refresh/cancellation/presentation),
`VLCTimelineGeometry.h` (500 ms buckets), and
`src/thumbnail-helper/thumbnail-helper.c` (read/decode/scale/guards).

## Established patterns and applicability

1. [FFmpeg demuxing API](https://ffmpeg.org/doxygen/8.0/group__lavf__decoding.html)
   distinguishes opening headers, stream discovery that reads/decodes packets,
   packet reads and seeking. Our stage probe demonstrates those costs locally.
   [Format options](https://ffmpeg.org/ffmpeg-formats.html#Format-Options) describe
   probe/analysis controls; those values are not a total file-I/O budget.
2. [mpv thumbfast source](https://github.com/po5/thumbfast/blob/master/thumbfast.lua)
   retains a separate worker, sends later seeks through IPC, coalesces updates on
   a 50 ms timer, supports keyframe seeking and optional worker startup on load.
   Its network-stream support defaults off; that flag is not proof of detecting
   mounted SMB paths. Transfer candidate: preserve independent playback and a
   bounded worker while reusing open container/decoder state between requests.
3. [IINA generation](https://github.com/iina/iina/blob/develop/iina/PlayerCore.swift)
   builds thumbnails in the background, exposes incremental progress and reads
   cached results. It checks mounted remote volumes behind a preference.
   [IINA cache](https://github.com/iina/iina/blob/develop/iina/ThumbnailCache.swift)
   validates version, file size and modification date. Transfer candidate:
   persistent small-image coverage plus incremental availability. Its metadata
   identity policy is weaker than our preserved-size/mtime replacement contract;
   adopting that policy would require an explicit decision.
4. [Plex preview thumbnails](https://support.plex.tv/articles/202197528-video-preview-thumbnails/)
   illustrates precomputed whole-video indexes, with substantial up-front CPU,
   time and storage cost. This is an alternative, not evidence that aggressive
   precomputation during wireless playback is beneficial.

Primary-source snapshots/hashes are retained in the ignored diagnostic directory.
External design patterns are not local performance proof.

## Recommended direction for discussion

Start by retaining one bounded helper per active media/track and reusing its
container/index/decoder. Separate invalidating an obsolete presentation from
destroying useful decoding work. Coalesce targets, preserve same-sample work,
and never display a completion under a different media/track/time label.
Retain watchdog/restart behavior for genuinely stuck workers.

Cache by actual sample/keyframe with target-to-sample lookup so nearby requests
reuse an existing image with its truthful timestamp. Add cross-open reuse only
with an explicit freshness/identity policy; avoid solving cache identity by
requiring a full 9GB NAS read before showing anything.

Then evaluate a small coarse set prepared after opening, with hover demand taking
priority and gradual nearby refinement. Rate-limit preparation and back off when
it competes with playback. A sparse representative image with its actual sample
time can bridge a miss. Do not present an old image as if it were the new target.

Preserve error reasons and distinguish a slow source/timeout from unsupported
media. A longer bounded startup allowance may help network access, but merely
raising every hover timeout does not address repeated initialization, wasted
reads or canceled work. Smaller output dimensions are low priority given the
measured 1 ms scaling cost. Investigate decoder buffering/unnecessary packet reads
before assuming every current read is intrinsic to keyframe extraction.

Proof before adoption: same-file before/after with retained failed attempts,
fresh/repeated targets, pointer movement and stationary demand, reopen/cache
replacement correctness, actual UI display, and playback under background work.
Separate local SSD and mounted SMB observations, retain variable-host ranges,
and preserve the previously agreed practical baseline comparison. NAS behavior
was outside the earlier bounded Story 002 acceptance; this report adds a concrete
daily-use gap without rewriting historical local-fixture passes.

## Progressive coverage proposal — 2026-10-05

Cam subsequently proposed middle-first generation, then quarter points, then
eighth points, to avoid leaving most of a video blank while a chronological pass
fills its beginning. This is breadth-first interval subdivision: complete the
coarse level before subdividing further. A depth-first walk would recreate the
undesired concentration in one portion of the timeline. This is a proposed
refinement to Story 004's original chronological no-hover fallback, not a shipped
change or a measured NAS improvement.

Bounded primary-source comparison:

- [IINA at 0b975d58, generation loop](https://github.com/iina/iina/blob/0b975d58bb5b313f55938315c09dd5c01c67c61a/iina/FFmpegController.m#L202-L219)
  divides duration into equal intervals, then iterates indices from zero upward.
  Its background generation is chronological; evenly spaced final positions do
  not imply evenly spread early availability.
- [mpv_thumbnail_script fork at 6b6e1a27, job order](https://github.com/marzzzello/mpv_thumbnail_script/blob/6b6e1a279fb13387221ed8fb4d50aa560ed10f7e/src/thumbnailer_shared.lua#L374-L393)
  halves a power-of-two stride to produce increasingly dense coverage. It is a
  close precedent, not exactly Cam's duration-based midpoint sequence: for 64
  samples its indices begin 64, 32, 16, 48, 8, 24, 40; for 100 they begin 64, 32,
  96, 16, 48, 80. The initial stride is strictly larger than the count, so the
  first sample is count-dependent.
  [Dispatch](https://github.com/marzzzello/mpv_thumbnail_script/blob/6b6e1a279fb13387221ed8fb4d50aa560ed10f7e/src/thumbnailer_shared.lua#L482-L499)
  distributes the fixed order among workers; completion order can vary. The
  inspected path chooses the closest completed image for display and does not
  reprioritize the job list around hover. Treat this as a design exemplar, not
  an endorsement of dependency maintenance or performance.
- [Thumbfast](https://github.com/po5/thumbfast/blob/master/thumbfast.lua) retains
  its worker and services requested seeks; its optional early startup does not
  implement this whole-timeline subdivision strategy.

A small independent ordering simulation reproduced the fork's loop, checked
unique complete coverage for counts 1, 2, 3, 17, 64, 100, and verified Cam's first
seven normalized targets as 50, 25, 75, 12.5, 37.5, 62.5, 87.5 percent. With exact
samples and equal per-image cost, worst distance to one of those seven samples is
12.5% of duration, versus 94% for the first seven points on a chronological
1%-spacing grid. This establishes only the coverage geometry: real keyframe
positions, extraction cost, concurrency and NAS caching were not modeled. Result
snapshots stay in ignored
`work/validation/nas-preview-20261005/coverage-order-simulation.json`.

Recommendation for the next design decision: replace chronological background
fill with duration-based breadth-first subdivision when empty, generalized to
largest remaining gaps when a valid cache or hover results already exist. Keep
the latest demanded hover ahead of background work after bounded active work
finishes. Nearby refinement should not monopolize all background work while
large uncovered regions remain; evaluate a small deterministic allocation of
background turns to global gaps. No new algorithm is needed simply for novelty.

Account for actual returned keyframe times and deduplicate repeated samples;
missing/failed intervals need finite retries and cannot cause endless bisection.
Stop at the agreed finite density/budget. Preserve the persistent cache and actual
sample-time labels from Story 004. On NAS storage, broad subdivision may incur
more expensive seeks than chronological extraction; it improves early spatial
coverage, not necessarily total generation time. Measure usable coverage against
wall time and bytes read while playback runs, comparing the existing ordering,
pure subdivision and hover-plus-gap refinement before selecting final weights.
