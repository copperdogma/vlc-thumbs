# Story005 verification protocol — prospective

Recorded before feature implementation or candidate measurement. Target baseline
is canonical master2e358f3098c2f2b7621d1dc568de8b61ad786322; record actual source,
configure/dependencies, app components and candidate diff hash for each acquisition.
The existing3.0 evidence remains scoped history, not a master baseline.

## Architecture discriminator

1. Build unchanged source, run relevant preparser tests and macOS XCTest, record
   exact compiled/run/skipped counts and logs. A successful compile alone is not
   application or API correctness proof.
2. Use `tests/story-005/generate_fixtures.py` outputs and independent FFmpeg frame
   timestamps/keyframe maps. Run fast and precise prep on standard MP4/MKV,
   long GOP/Bframes, VFR, positive-start/edit-offset, rotation and SAR; compare
   actual callback date, returned pixels/display geometry and requested target.
3. Enumerate stable video IDs from pinned playback; request red, blue and an
   invalid ID with ordinal fallback disabled. Compare internal/external prep.
   Record invalid-ID timeout/unavailable separately from wrong successful image.
4. Exercise repeated uncached requests locally and against available slow storage.
   Record open/read counts when instrumentable, actual time gaps, source warmth,
   request/callback/export boundaries and failures. Three repeats initially
   discriminate mechanism; they are not a p95/causal performance estimate.
5. Independently bounded cancellation test: ignored SIGTERM/hung worker, callback
   deadline, process reap and ability to service a subsequent request are separate
   observations. No unattended fault process may remain after the test.

Choose the small native route only if these facts support it. Existing source
shows missing selected-track option transport and SIGTERM-only termination;
reproduce before changing core. Repeated input opens are known, their unacceptable
NAS cost is not yet demonstrated. Broader core/session work needs a revised exact
plan rather than silently widening this experiment.

## Candidate capability and regressions

- Native main, detached, native fullscreen and custom fullscreen: actual pointer
  enters/exits/rapid movement, correct time/image, hide/cancel/context switches,
  seek by click/drag/wheel/keyboard, volume and fullscreen fades. Map actual master
  control instances first; do not infer classes from old3.0 resources.
- Preference: disable during work, save, reopen/restart, reenable, explicit CLI
  precedence, ordinary time tooltip/control preservation. Use isolated profile
  and stores; preserve the installed daily preview app and user originals.
- Keyboard/VoiceOver: inspect accessible title/role/value, focus stability and
  control activation on actual surfaces. Reproduce baseline defects before
  attributing them to the contribution. An unsuccessful reader launch is unknown.
- Context/track/time/transform: replay the legal discriminating fixtures and
  adversarial stale callback/media/track cases. Missing/unsupported identity or
  presentation must be unavailable rather than wrong-success.
- Cache/restart: limits, atomic interruption/corruption/digest/shape, eviction and
  bounded demand retention, generation separation, sampled source replacement,
  symlink change, independent process reopen, fixed provisional15s deadline,
  source failure/disable/close clear. Retain the unsampled-byte limitation.
- Worker and preparation: one active/latest demand, finite plan and retries,
  hover priority/global fairness, cancellation, crash/hang, low disk/permission
  failures and recovery; report unsupported platforms/formats explicitly.

## Practical matched comparison

Preserve baseline-median+20% ordinary-control allowance. Acquire20valid responses
per arm under the same fixture/window/display/input protocol; retain all attempts,
exclusions and reasons. Alternate matched baseline/candidate blocks, use the same
observer boundary, and report medians/ranges plus exclusions. Large baseline drift
or ownership/observer failure is inconclusive, not permission to enlarge allowance.
New preview delay is descriptive and separate from vanilla ordinary response.

Acquisition compatibility note, 2026-10-06: the older Story004 control wrapper
imports Story002 code with a fixed bundle ID, window/slider/crop geometry,
light-style knob classifier and media-at-launch/paused-zero setup. Its measured
boundary is visible knob feedback, not completed seeking. The old preview probe
also depends on diagnostic events absent from the master contribution. Do not
run those wrappers unchanged or substitute missing traces with inferred events.
Reuse their actual-display timestamps and exact-process ownership guards only
after validating the current isolated IDs, visible geometry and response
classifier against both master apps. Use the proven empty-window readiness
sequence. Record a prospective adapter/protocol addendum before scored collection;
keep the20% allowance, balanced arms and retained exclusions. The baseline's
paused-seek/resume defect is a separate limitation, not latency evidence or a
reason to silently change the observed response boundary. Cam subsequently authorized screen and mouse use (2026-10-06); the existing
bounded native pointer harness may now be used. Source preparation and observer
adaptation remain within authorized verification work.

Use at least three matched60second playback pairs, with candidate preparation
actually active. Record playing state, audio continuity, dropped-picture deltas,
app/worker CPU/RSS and source hashes. Preserve baseline/candidate ordering and
shared-host confounds. Existing allowed dropped-picture increase is1percentage
point. Screen repeats alone do not identify causal stalls. Choose enough legal
media duration/work to avoid measuring an already-completed preparation queue.

## Reproduction and handoff

Clean upstream checkout plus only proposed patches must build with documented
upstream commands. Exact contrib-key history matters: a shallow clone that hides
prior relevant changes must be deepened before deriving the prebuilt artifact.
Run required upstream tests and `make distcheck` for added/moved/removed files;
report unavailable Intel/older-OS/remote CI coverage explicitly. Independent review
must clear material findings. Public package includes source/fixture recipe,
licenses/attribution, a small legal demonstration, test commands/results and
limitations; excludes local methodology, binaries, private paths/media/NAS details.
No external contact or submission in the current run; final source author and any
attestation must be real and verified. Phase2 readiness cannot stand in for phase3
maintainer acceptance or the bookmark-dependent integrated root.
