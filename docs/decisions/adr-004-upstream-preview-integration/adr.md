---
status: ACCEPTED
date: 2026-10-05
story_refs: ["005"]
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity, ideal:req:evidence]
spec_refs: [spec:1, spec:2, spec:4, spec:5]
related_adrs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services, adr-003-persistent-thumbnail-preparation]
---
# ADR-004 — Upstream preview integration

## Selected implementation decision — 2026-10-05

Accepted as the root's technical implementation choice within Cam's delegated
phases1/2 request, not as VideoLAN acceptance or completed feature proof. Follow
the [frozen feature port plan](../../evidence/story-005/feature-port-plan.md):
retain the isolated FFmpeg9 helper and bounded service/cache/preparation behavior,
integrate through ordinary build/package rules, and extend master's existing
hover panel/current player. Expose Matroska TrackNumber through a minimal normal
contrib source patch, with focused affected-consumer regression coverage. Do not
ship the diagnostic archive-replacement recipe or depend on core prototypes.

H1 additionally requires conservative flat-presentation admission. The separate
opt-in FFmpeg EBML-parser patch scans the complete physical Segment within fixed
read/seek/node/deadline bounds, preserving original buffered I/O state. It rejects
ordered editions, hard/medium links, SegmentFamily, unknown-size nested elements,
multiple documents/Segments and incomplete or over-budget scans. These exclusions
are explicit; SegmentFamily is conservatively rejected, not asserted to prove a
virtual timeline. New mapping/cache policy excludes earlier uncertified images.
Normal source builds,77 helper/admission checks and custom-AVIO parity/fault
checks pass. Two bounded warm NAS comparisons preserve all36 paired pixel/time
results, with observed ready times23–86ms on the current helper. This supports
the chosen gate for those layouts; cold/stalled/larger-source cost is unqualified.
Native consumer and full feature qualification remain required.

The [helper discriminator](../../evidence/story-005/helper9-discriminator.md)
provides actual compile, moviePTS/pixel, transform, retained-open and reordered
track evidence. Root visually inspected the paired generated images. Native reuse
instead revealed a larger movie-time/eligibility prerequisite. Source review finds
no direct VLC playback AVStream.id consumer that necessitates another private
dependency variant; FFmpeg ID selection/stream groups still require tests.
The supposed helper origin-collapse finding was withdrawn after exact raw records
and independent references refuted it. No repair was made from that inference.

No current maintainer endorsement is assumed. Existing !7493/#29393 are disclosed
with the measured reuse gaps and contribution rationale. This design can be
reviewed as a source proposal; essential future feedback may still change it.
All native, NAS, cache/restart, playback, clean reproduction and public-diff gates
remain required before ready-to-submit. Earlier investigation below is retained
as decision history and does not override this selected plan.

## Context and Ideal alignment

Story005/002b must prepare a contribution maintainers can evaluate independently.
Immediate, accurate previews and undisturbed playback remain the Ideal. The
qualified3.0.24 implementation is evidence about one branch, not an obligation
to retain a private decoder, IPC protocol or cache upstream. Bookmarks and durable
identity remain separate. Cam authorizes phases1/2 now, ending before submission.

Canonical master and its official mirror both resolve to
`2e358f3098c2f2b7621d1dc568de8b61ad786322` on this audit. Its preparser offers
asynchronous thumbnail requests and process isolation; the native slider already
shows hover time. These are useful primitives, not a demonstrated complete service.

The new material finding is existing parallel work: [macOS MR!7493](https://code.videolan.org/videolan/vlc/-/merge_requests/7493)
is open with unresolved discussions. [Core design issue#29393](https://code.videolan.org/videolan/vlc/-/work_items/29393)
describes multiple preview sources and shared lifecycle APIs. The linked
[medialibrary meeting](https://code.videolan.org/videolan/medialibrary/-/issues/493)
discusses generation cost, configuration and initially explicit generation.
Those are published direction and experiments, not a current merged API or a
blanket rejection of our local desktop behavior. Public review-note endpoints
returned401; the reasons for!7493's unresolved discussion remain unknown.

## Options

| Option | Benefit | Cost / discriminator |
|---|---|---|
| Native preparser plus small macOS adapter | Reuses maintained decoder, identity and native controls | Prove actual PTS, chosen ES, transforms and repeated-open/NAS cost; current requests destroy their input after one picture |
| Small core thumbnail extension plus macOS consumer | Shared behavior; can avoid a private FFmpeg patch | Define bounded retained-session or multiposition contract, cross-platform tests and relationship to existing preview design; not automatically a small delta |
| Build on existing!7493 | Respects prior contribution and possibly reduces duplicate UI work | Old base/API, unresolved review, in-memory URI/position cache; no demonstrated track/freshness/NAS contract |
| Retain isolated helper, integrate it properly on master | Existing behavior and bounded local tests | Separate decoder/build/license/track-mapping maintenance; weakest alignment if core can meet the contract |
| Prepare a focused design/proof contribution first | Resolves ownership and avoids a competing large patch | Does not satisfy phase2 feature readiness; requires explicit sequencing decision if maintainer direction is a prerequisite |

A stable-release feature patch is not the default: current official contribution
guidance directs new work to master and maintenance branches to backports.

## Contracts that cannot disappear during simplification

- Original media stays unchanged. Local source inspection and thumbnail work must
  not block the main thread or introduce arbitrary secondary network requests.
- One bounded active extraction, latest hover intent, finite background preparation,
  cancellation on media/track/disable/close, typed failures and finite watchdogs.
- Selected video identity must correspond across playback/extraction. Stable
  `vlc_es_id` strings are promising; ordinal equality is insufficient.
- Actual frame time and pointer time remain distinguishable; dimensions, SAR,
  orientation and qualified color reflect the decoded picture. Unsupported cases
  return unavailable rather than plausible wrong images.
- Cache limits and lifecycle remain32MiB RAM/256MiB disk, with demand retention,
  atomic/corruption-safe disposable storage and explicit source qualification.
  ADR003's sampled hash limitation remains visible; labels never inherit it.
- Current-session provisional images have one15s source-check deadline. New opens
  qualify before reuse. Generation guards cover all asynchronous results.
- Ordinary controls, accessibility and playback receive fresh branch-native proof;
  predeclared ordinary-control median allowance stays baseline+20%.

## Bounded experiment and baseline

First build unchanged master using its macOS build script and CI's Darwin19
triplet. Keep generated artifacts separate from the preserved3.0 builds. Record
all source/dependency/build evidence and stop at1GiB free without deleting prior
artifacts. The upstream GUI XCTest and preparser tests establish substrate only.

A standalone caller then requests known synthetic frames through the unchanged
preparser, logs callback status, actual picture date, orientation/SAR, requested
time and elapsed time, and exports bounded pixels for inspection. Compare fast
and precise seeks, chosen tracks, repeated positions and slow storage. Check
cancellation/lifetime failures. Use actual results to choose the next extension;
source inspection alone cannot supply the runtime result.

Current baseline and prototype results are maintained in the
[readiness ledger](../../evidence/story-005/current-readiness-ledger.md). The
unchanged arm64 app builds and ran 253 XCTest cases; no master preview feature is
qualified. The existing thumbnail test's picture-date assertion is disabled
(`test/src/preparser/thumbnail.c:93`), making actual PTS an explicit experiment,
not grounds to assume the API is broken. `ThumbnailerRun` creates/stops/closes an
input for every request (`src/preparser/internal.c:503–575`), so worker-process
reuse alone cannot establish retained-demux responsiveness.

## Decisions

- **Settled for investigation:** master pin above, official GitLab submission route,
  source-only contribution scope, legal synthetic proof and preserved local app.
- **Unsettled:** decoder/session/cache owner, relationship to!7493/#29393 and exact
  patch series. No broad port until the experiment and published direction support
  a coherent plan. A material shared-core prerequisite or required maintainer
  decision must be surfaced rather than hidden in the macOS adapter.
- No upstream contact occurs in this run. Draft any necessary question locally.
  An unanswered essential architecture question prevents readiness; it cannot be
  relabeled as an accepted assumption.

## Dependencies and affected surfaces

Story005; spec:1/2/4/5; ADR001–003; current acceptance ledger; upstream contribution
scout; forthcoming master build/probe evidence. Source seams: native progress
slider and controls, player selected-track callbacks, preparser/internal/external
implementations, existing image cache, macOS XCTest and preparser tests. Changes
to shared core require cross-platform ownership and testing beyond the native UI.

## Historical integration checklist — selected-plan stage

This records the earlier selected-plan stage. Current implementation and bounded
Phases1/2 qualification are recorded in
[current source10 verification](../../evidence/story-005/current-source10-final-verification.md);
unchecked items below preserve that earlier state.

- [x] Select the technical mechanism from measured proof; maintainer acceptance remains external.
- [ ] Record exact patch files, dependencies, attribution and removal boundaries.
- [x] Update spec/state/story/runbooks and regenerate graph after selection.
- [ ] Verify current native surfaces, cache/restart/NAS, controls and playback.
- [ ] Independently reproduce and review exact public diff before readiness.

## Work log

20261005-1959 — Researching: compared current core/macOS source with ADR002/003,
found existing!7493 and#29393, and began unchanged baseline build plus bounded
preparser experiment. No architecture acceptance or upstream feature proof.

## Narrow contract review — 2026-10-05

Independent source review does not treat missing `vlc_previews` or open!7493 as
a technical blocker by themselves. Two narrower issues are evidenced: external
requests serialize URI and thumbnail arguments without item options, so the
internal `video-track-id` route is lost; POSIX termination sends SIGTERM then
waits without an escalation deadline. Conversely, external JSON preserves picture
date and full video format, including orientation/SAR. Strict internal track
selection returns before default fallback when an explicit string ID does not
match, provided ordinal fallback is disabled (`video-track=-1`).

The callback does not identify its decoded ES. A focused selected-ID field and
strict input selection, plus process-lifecycle proof/correction, are candidate
patch boundaries. Repeated input opens remain a measured-performance question;
retained-session API design is deferred until that test fails. This is a proposed
small series, not a selected or runtime-qualified architecture. See the prospective
[verification protocol](../../evidence/story-005/verification-plan.md).

## First runtime discriminator and correction direction

The [unchanged-core process probe](../../evidence/story-005/process-probe-runtime-20261006.json)
reproduced the POSIX termination problem against the pinned arm64 library. The
normal child was reaped; a child with a SIGTERM handler remained in
`vlc_process_Terminate(true)` through the eight-second outer deadline. The
independent launcher killed only its dedicated process group and verified no
surviving members. This is process-API proof; preparser callback recovery remains
untested.

The general problem is forced termination whose signal permits refusal.
[POSIX signal definitions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/signal.h.html)
distinguish SIGTERM from uncatchable SIGKILL. The pinned API documents
`kill_process=true` as forced termination, and its Windows implementation already
uses unconditional `TerminateProcess`. Microsoft's
[contract](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess)
still requires waiting for pending I/O to complete or cancel. Therefore neither
platform supports a universal hard real-time exit claim.

The candidate correction is to align the existing POSIX forced-kill operation
with its documented semantics, preserving normal `Terminate(false)` shutdown,
rather than introduce a new timeout API. Review callers and regression needs
before editing. This small fix does not select the full preview architecture.

## Current native control map

Pinned master uses `VLCMainVideoViewController` and
`VLCMainVideoViewControlsBar.timeSlider` for embedded, detached, native-fullscreen
and custom-fullscreen video. Custom fullscreen reparents the same view into a
borderless window; the packaged old `VLCFullScreenPanel.xib` has no corresponding
live controller implementation. Extend the existing
`VLCPlaybackProgressSlider` time-hover panel rather than port the old independent
fullscreen controller or install a competing popup.

The new service must observe current media, track list/selection, capabilities
and duration through `VLCPlayerController`. Copy the stable ES string ID while
holding the player lock; its exposed metadata pointer is borrowed. Fullscreen
reparenting and controls fading must cancel/hide presentation even without fresh
pointer events. `getThumbnailer()` currently enables only thumbnail-to-files,
so a picture-returning adapter must deliberately configure its own service or
extend the existing instance. These are source findings awaiting native proof.

## Reuse proof and bounded core corrections

The [132-request matrix and 24-request follow-up](../../evidence/story-005/preparser-probe-results.md)
demonstrate external selected-track loss, rotation loss and a seek-dependent MP4
timestamp discrepancy. Standard MP4/MKV, VFR, positive-start MKV and SAR checks
provide useful counterexamples; the failure is not universal. Root inspected the
rotation outputs. An eight-orientation allocation/clone probe proves metadata is
reset in `picture_Setup` by `video_format_Setup`. A focused constructor correction
and existing image-test extension are prepared in an isolated worktree, pending
integration and real export proof.

The selected-track prototype adds an optional owned ID to thumbnail arguments,
private-input strict selection and dedicated IPC transport. An acknowledgment
in the response lets explicit requests fail closed when a worker omits or
mismatches the selected-ID contract. This is acknowledgment of applied request
semantics, not an independently observed decoded ES ID. Default requests retain
their existing behavior; no arbitrary item options are transported.

MP4 correction remains an experiment. Source/history identifies the condition
that skips edit media-time subtraction when the seek-start DTS precedes that
time. [The 2021 change](https://github.com/videolan/vlc/commit/7acbebf3eca9b01eeb5b5cdd200ed0771fc3f947)
explicitly sought to avoid negative offsets; it also shifts the later PTS. The
later-GOP discriminator returns matching times, whereas first-GOP output is
83.334ms late. The bounded experiment removed that condition, improving ordinary
positive-edit packet/picture correspondence, but failed its declared stop gate:
a non-keyframe trim returned an out-of-edit negative picture date and could not
export an image. The exact experimental patch was removed from the integration
candidate. See the [results](../../evidence/story-005/mp4-candidate-results.md) and
[movie-time contract gap](../../evidence/story-005/movie-time-contract-gap.md).
No constant timestamp subtraction or UI workaround is acceptable.
The common demux impact requires stronger regression coverage before inclusion
in a submission series. This does not add general MP4 support to the feature scope.

Source-warm NAS core requests on the generated12MB file took133–238ms. Retained
helper requests were about4ms after separately measured28ms startup; boundaries
and cache warmth differ. This identifies a repeated-open cost, without proving a
new retained-session API necessary. Final caching/preparation and matched playback
must decide its product impact.

## Strategy checkpoint — retained-helper comparison

The native reuse discriminator was worthwhile: a small macOS adapter cannot yet
promise correlated movie time and edit eligibility. Continuing the one-line MP4
experiment into general demux/decoder/timing repair would materially expand that
plan. The core work is deferred while the story's already-listed retained-helper
alternative receives its missing local proof.

The alternative changes the mechanism: an isolated retained FFmpeg decoder maps
its own movie timeline and owns source qualification, while current VLC native
controls supply playback context. It must prove correspondence with master's
selected tracks and movie position, and must build from public source without
private ignored machinery. Current master selects FFmpeg 9; the old 8.1.2 private
TrackNumber modification and build scripts cannot simply be shipped unchanged.

Root authorizes only the bounded helper 9 compile/fixture/identity experiment in
the current plan. A successful result would justify a concrete port decision and
patch plan, not establish maintainer acceptance. Existing !7493/#29393 remain
architecture inputs; absence of their future API is not itself a blocker. The
complete feature, NAS/freshness safeguards and independent reproduction remain
required. Native interaction proof separately awaits Mac unlock.
