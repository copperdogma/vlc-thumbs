# Story 002 generated helper qualification

Generate project-owned synthetic media with:

```sh
python3 scripts/generate-thumbnail-fixtures.py
python3 tests/story-002/helper_contract.py --helper /absolute/path/to/vlc-thumbnail-helper
```

The generator requires host research FFmpeg/ffprobe at `/usr/local/bin/`.
They are not product dependencies. Full command arrays, generation configuration,
media hashes, stream metadata and independent presentation-frame maps live in
ignored `work/fixtures/story-002/`. `manifest.json` freezes a compact generation
receipt; no media is tracked. Generation stops at a 300 MiB directory bound or
before consuming the 1 GiB free-space reserve. Visuals/audio are lavfi synthetics;
the font is local Arial. No private or downloaded media is used.

Standard fixtures are 60 s H.264 1080p24 with burned frame/time numbers and a
generated ALAC tone; MP4 and MKV remux identical encoded streams. ALAC avoids an
AAC priming shift that otherwise changed MKV's normalized frame origin. Diagnostic
fixtures cover B-frames/long GOP, VFR, container +5 s start, MP4 delayed video/edit
list, true display-matrix rotation, 2:1 sample aspect ratio and separate red/blue
video tracks. Stress fixtures are three-second 4K and five-minute low-resolution
long GOP. The latter is deliberately not a 1080p playback stress substitute.

The helper runner validates bounded argv/JSON/RGBA replies, explicit errors,
keyframe identity, display aspect and rotation, independent pixels and unchanged
media. Cam's approved keyframe MVP requires protocol v2 and `sampling: "keyframe"`.
Pointer-to-image delta is reported without the former 0.5-second exact-frame
requirement. FFprobe supplies an independent decoded frame map including
`key_frame`; host FFmpeg extracts the verified actual keyframe ordinal. A reported
timestamp alone cannot pass. Mean
absolute RGB difference <=8 allows separate-libav color/scaling rounding; exact
same-stream MP4/MKV RGBA equality remains required. This tolerance does not
replace native visible-frame inspection. Each standard fixture receives >=100
sequential settled requests in permuted target order, with every error counted.
It records sampled process RSS/CPU, timing, first request and success percentiles.

For unspecified SDR color matrices, the independent reference explicitly uses
BT.709 at encoded heights >=720 and BT.601 below that, matching the declared
project policy. Host FFmpeg's implicit matrix differs on these synthetic HD
streams; using implicit conversion initially produced RGB differences of 8.7–9.1.
The explicit reference leaves the pixel tolerance unchanged and must still be
checked against VLC's visible presentation. A PQ/BT.2020-tagged synthetic clip
tests unsupported-presentation rejection; it is not an HDR quality reference.
Other error probes cover missing/nonregular files and truncated headers. An
initial edit-list gap may use the first qualified keyframe with its true time;
the runner verifies this against the independent map. Otherwise the helper must
use a preceding qualified keyframe rather than search forward through a sparse
GOP. Density is recorded for standard, long-GOP and five-minute fixtures; every
settled benchmark request includes its actual pointer delta.

Output is `work/validation/story002/helper-keyframe-results.json`. Historical
`helper-results-v3.json` preserves the earlier exact-frame strategy proof and is
not the keyframe MVP result. Timing includes Python
process/resource sampling and excludes GUI events, service/cache work and actual
presentation. Recent generation/reference reads make OS storage caches warm or
uncontrolled; no global cache flush occurs. Sampled RSS/CPU can miss short peaks;
the helper must separately enforce its allocation/resource limits. This runner
does not qualify cache latency, native hover surfaces, playback competition,
accessibility, cancellation races, malformed-worker injection or root completion.


## Native visible latency

`native_hover_trial.py` and service traces report event-to-image assignment.
That boundary does not prove that a new image has reached the display. Use the
continuous actual-display runner for the visible latency gate:

```sh
python3 tests/story-002/continuous_hover_trial.py \
  --app work/build/vlc-arm64/VLC.app \
  --media work/fixtures/story-002/standard-cache-pressure.mp4 \
  --duration 90.037333 \
  --output work/validation/story002/continuous-hover-fresh-attempt
```

The app must be stopped, the output directory must be new, and the generated
fixture must match its metadata SHA. Repeat separately for MKV using its verified
container duration. The runner owns only the development app it starts. Leave
other apps and the pointer idle: every scored frame requires active owned VLC,
correct parent/panel geometry and an unchanged source/app. A failed guard stops
the run and retains all attempts; a stopped setup is not a latency result.

The observer first produces independent sRGB image/caption templates in a prior
media generation. Ordinary playback/stop/reopen establishes a fresh cache
namespace. Each demand starts a ready continuous ScreenCaptureKit stream before
native pointer injection. Completion is the first complete frame with matching
image, pointer caption and independently checked actual-keyframe caption whose
WindowServer display time and presentation PTS are at or after input. Native
assignment and capture callback receipt remain separate diagnostics. This proves
the observed WindowServer presentation, rather than physical screen scanout.

A full run uses100 misses,100 RAM hits,50 pressure seeds and100 disk hits; every
fault is retained. `--count` below100 is a method pilot without disk pressure and
cannot qualify percentile budgets. No global OS-cache flush is performed;
reference generation leaves storage caches warm or uncontrolled. The current
fixture is the generated90s derivative with independently verified keyframes.
These main-window runs do not replace fullscreen, playback or reader checks.

## Bounded observer diagnostic

```sh
python3 tests/story-002/paired_visible_diagnostic.py \
  --app work/build/vlc-arm64/VLC.app \
  --media work/fixtures/story-002/standard-cache-pressure.mp4 \
  --duration 90.037333 --pairs 20 \
  --output work/validation/story002/paired-visible-fresh-attempt
```

Use `--pairs 20` (separate argument). This compares alternating heavy/buffered
observers on the same20 prewarmed RAM targets. The buffered callback copies into
32 prefaulted slots and performs image analysis after capture stops. Its scene
ownership guards are before/after, so this comparison is diagnostic only and
cannot replace the per-frame-qualified observer. Retain all pairs and errors;
never subtract observer overhead from product latency or use a subset to claim
acceptance. Sequential runs with different product builds are provisional
experiments, not randomized product comparisons.

Upstream `make check` is separate regression coverage. Its current baseline TLS
failure, skip and complete results are recorded in
`docs/evidence/story-002/upstream-tests.json`; it does not exercise native hover.


Cam-approved MVP targets (2026-10-04): memory/disk visible previews150ms p95,
initial pointer-time/loading200ms p95, uncached image1s p95. Original100ms
cohorts remain unchanged; mvp-threshold-rescore.json records explicit revised
contract assessment. This is re-scoring retained observations, not a new run.


Program-local video ordinal regression (generated owned MPEG-TS only):

```sh
python3 tests/story-002/multi_program_contract.py \
  --helper work/build/thumbnail-helper/thumbnail-helper \
  --output work/validation/story002/program-contract-NEW
```

The output directory must be new and below `work/`. One program with two video
tracks must retain independent red/blue ordinals; two programs must reject both
requests with `ambiguous_track_mapping` and no pixel payload. This boundary is
explicit unavailable, not broad MPEG-TS support qualification.


Reordered Matroska track ambiguity regression:

```sh
python3 tests/story-002/matroska_track_contract.py \
  --helper work/build/thumbnail-helper/thumbnail-helper \
  --output work/validation/story002/matroska-track-NEW
```

Historical result: the earlier helper rejected all multi-video Matroska input,
including the convenient TrackEntry order. The confirmed 022512 candidate
supersedes that result only for the tested AVC multi-video MKV path: its private
libavformat build exposes Matroska `TrackNumber`, and the helper sorts positive
unique values and checks their count against VLC's expected video-track count.
Original/reversed red-blue cases and a count mismatch pass five checks
([current evidence](../../docs/evidence/story-002/matroska-track-mapped-contract.json)).
Multiple programs, WebM, other codecs, and broader presentation equivalence remain
unavailable or unqualified. The older regression above remains useful for its
historical helper and must not be cited as current blanket-Matroska behavior.


Fixture generation requires a new output directory. Reuse the pinned existing
fixture set for evidence reproduction; create a fresh `--output` for deliberate
regeneration instead of overwriting it. Source-preservation regression:

```sh
python3 tests/story-002/fixture_preservation_contract.py \
  --output work/validation/story002/fixture-preservation-NEW
```

This uses generated sentinels only and proves linked media, linked sidecars and
hardlinked media are rejected before an encoder is invoked.

## Required pragmatic before/after comparison

`pragmatic_control_trial.py` preserves the exact executed bounded recipe for
cohort002:20 responses per arm, blocks AB, BA, BA, AB, phaseAX at3000ms and
actual pixel-render median comparison with a prospective20% allowance. It
requires the qualified `control-response-probe-v4-frontmost`, exact isolated
baseline/feature paths and generated MP4 in ignoredwork. Its frozen outputpath
must be fresh; change that path prospectively for a new run, preserve a runner
hash, and never pool older cohorts. Root owns GUI actions. It launches/cleans
only owned apps; no installedVLC or private media. Before marking a result
valid, completion audit must independently check raw session acquisition/phase
guards, all timestamps, unchanged fingerprints and both cleanup outcomes.

Current results and exact executedrecipe hashes are in
`docs/evidence/story-002/ordinary-control-pragmatic-before-after.json`; the scoped
interpretation is `docs/evidence/story-002/pragmatic-before-after-validation.md`.
This supplies an approximate actual before/after comparison, not p95 or
completed-seek timing. The earlier precision observer attempts remain historical.
