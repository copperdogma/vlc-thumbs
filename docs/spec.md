# VLC timeline enhancements — Spec v0

Constraint map derived from the preserved intake and pinned-source investigation.
VLC 3.0.24 has a working isolated arm64 development build on the current host.
Story 002 has demonstrated four-surface keyframe hover, sampled actual-reader
behavior and matched playback on its original presentation path. Cam approved
150 ms RAM/disk and 200 ms initial-caption MVP limits after reviewing the 100 ms
shortfall; those are retained historical thresholds and re-scores do not rewrite
original failures. Historical precise-performance proposal: root prospectively selected a 20% p95 regression
allowance for ordinary-control response against matched unmodified VLC on 2026-10-05. A valid
percentile comparison needs at least 100 responses per arm. Baseline temporal
blocks with more than 20% median variation make that comparison inconclusive;
variation does not enlarge the allowance. The confirmed 022512 helper
adds bounded AVC multi-track Matroska correspondence. Its MP4 visible cohort
missed the historical absolute limits, with no matched unmodified-VLC baseline
and no regression attribution. The historical ordinary-control baseline pilot validated setup only; its paired attempt was invalid. The subsequent accepted practical protocol uses 20 valid responses per arm and baseline median +20%, with current evidence recorded under Story 004; it does not qualify the older precise p95 gate.
Bookmarks remain planned. ADR-001 accepts storage
lifetimes, ADR-002 selects the preview route, and ADR-003 accepts persistent preparation and sampled thumbnail freshness. No product AI inference is required. Detailed options/source seams:
[implementation synthesis](research/timeline-implementation-plan.md).

## spec:1 - VLC integration and delivery

Serves `ideal:req:annotations`, `ideal:req:previews`, `ideal:req:playback-quality`.
Need: VLC's actual macOS timeline. Initial scope compromise: macOS, local
seekable videos and development delivery; other platforms/public packaging
are deferred (ecosystem/human scope). Pinned GUI source supplies concrete seams;
no native timeline hook was identified in stable Lua. Recommended route is a
small reproducible GUI patch plus feature-owned files on VLC 3.0.24, selected at
Story 002's integration ADR gate. No permanent fork commitment is made.

Main/detached windows use a common VLCSlider path; fullscreen has a separate
NSSlider panel. Native Cocoa and custom fullscreen require distinct runtime
checks. Baseline video has been observed in fullscreen and detached modes;
actual main/detached/native/custom fullscreen hover is visibly demonstrated.
Main seek/volume/focus and the expanded 32-point hover region have recorded
checks. Actual-reader hover has stable sampled captions/focus on all four
surfaces; the inherited VoiceOver slider increment does not seek, reproduced
on the pristine baseline. Final-review changes require focused native proof. Both feature stories must
prove all four surfaces. Evolution: prefer upstream-supported hooks when they
can deliver the same interaction, and retire patch maintenance when possible.

Current-host arm64 build succeeds in attempt 009 after source-built dependencies
and architecture/toolchain repairs. Native generated MPEG-4 playback/pause/seek
works; H.264 native/detached display also observed. At attempt009, workspace was ~5.7 GiB and app
161 MiB; these are historical sizes. Auto-updates disabled; older-OS/Intel/all-format compatibility and full
clean rebuild are unqualified. Reproduce via [build runbook](runbooks/build-vlc-macos.md).
Pin source, patches, source-library hashes/config, bundle identity and signing.

Disk is a current-host resource constraint, not an assumed 30 GiB requirement.
Initial source was 163 MiB; the monitored build never hit its 1 GiB free-space
stop reserve. Cam authorized attempted building and owned-artifact cleanup on
insufficient space. Recheck free space and reuse incremental builds. Relocation
must move the whole mutable tools/contrib/source/build workspace; `-C` alone
moves only part. Retain evidence and preserve pristine source/user files.
Root eval: root-timeline-experience. Stories: 001 baseline, 002/003 features.

## spec:2 - Thumbnail correspondence and responsiveness

Cam requested a conventional native on/off control on2026-10-05. Provide a
default-on “Show timeline thumbnail previews” checkbox under Preferences →
Interface, persisted through VLC config. Saved changes apply to existing
timelines, disabling hides/cancels pending work, and normal seeking/accessibility
remain available. This preference affects previews only; bookmark design remains
separate.

Serves `ideal:req:previews`, `ideal:req:playback-quality`.
Need: a recognizable nearby image to help locate the general area, without seeking playback. Decode cost,
keyframe spacing, timestamps and geometry are physics/ecosystem limitations.
Cam selected a keyframe-first MVP on 2026-10-04: demand-driven asynchronous
keyframe images, aspect-fit 320×180,
half-second buckets, explicit loading/unavailable, latest-request cancellation
and 32 MiB memory/256 MiB disk caches. Limits/timing are targets, not measurements.
Selected-track identity, aspect/rotation and time origins must agree with VLC;
subtitles/user filters are not baked into previews in initial scope. Unsupported
presentation cannot be silently approximated. For the tested AVC multi-video
Matroska path, a private FFmpeg 8.1.2 libavformat build carries Matroska
`TrackNumber` through stream metadata; the helper sorts positive unique values
and checks their count against VLC's expected video-track count. This mapping
passes original/reversed red-blue fixture checks. Count mismatch, invalid
identity, more than 128 streams, and unsupported mapping return unavailable.
Multiple programs and other codec/container combinations remain unsupported or
unqualified; do not infer support from local menu ordinals.

Preferred candidate: private arm64 helper linked to the already built FFmpeg
8.1.2 libraries. Its tiny fixture probe passed 15 seek/decode requests, including
same-stream MP4/MKV with identical RGB hashes. AVFoundation passed MP4 but failed
that MKV; public LibVLC callback timing needs additional frame-identity work.
These are diagnostic findings, not broad performance/format qualification. The
022512 build uses private libavformat archive SHA-256
`93d8acfd4368bb6e0ea9e82a3b8cc5c0a27d1624cb6859bc4e8534c04d035d34`; only its
`matroskadec.o` differs from the original across 539 verified archive members.
Pinned VLC source and linked VLC libraries remain unchanged. Never use the
playing input for extraction or require the host FFmpeg executable.
Source/config/license review precedes any public distribution.

The pointer time and actual preview-frame time are distinct; show both when
they differ. Keyframe gaps are acceptable in the MVP. Record sampled time
distance and keyframe density; additional decoded samples are a future option
if trying the product shows gaps are too coarse. This supersedes the agent
proposed <=0.5 s preview correspondence gate, before the keyframe runs.
[Root contract](evals/root-timeline-experience.md) preserves the 2026-10-04
absolute 150/150/200/1000 ms limits as historical thresholds, with playback,
resource and failure checks. Historical, separately deferred precise ordinary-control qualification uses a
matched pre-change VLC baseline and the prospectively approved 20% p95 allowance;
it requires at least 100 valid responses per arm. If matched baseline blocks
vary by more than 20% in median response, or measurement ownership/setup fails,
the comparison is inconclusive, never a pass. Do not increase the allowance to
absorb noise. Functional MVP acceptance is separate from this precise latency
qualification. An inconclusive shared-host comparison and unattributed repeats
in both arms are disclosed as nonblocking performance characterization for the
MVP; they do not support claims of “no stalls” or a performance pass. Reproducible
feature-attributable stalls remain defects. CPU/RSS playback resources use
matched baseline/candidate deltas; enforce declared worker/cache bounds and
playback-integrity gates. Historical Story 002 costs were about +2 percentage points
CPU and +20–40 MiB RSS; current Story 004 measurements report the app and helper costs separately in its acceptance ledger; repeated-ROI evidence does not attribute every stall.
Vanilla VLC has no thumbnail baseline, so report ordinary response and the new
thumbnail's delay separately as descriptive evidence.
The 2026-10-05 MP4 cohort missed prior absolute limits but has no matched vanilla
baseline and no regression attribution. Bound worker/backlog,
reject stale media/request generations, forbid helper network fetches, and
handle missing/ambiguous PTS honestly. ADR-001 puts images in a feature-owned
Caches directory; corrupt/evicted images regenerate without touching labels.
Cache freshness must be explicit: conservative initial proposal namespaces
entries by media-open generation with file-state guards; cross-open reuse needs
fresh content verification, otherwise decode as a miss. Continuous external
rewriting is outside unchanged-file scope. Test preserved-mtime/size replacement;
metadata-only reuse cannot silently weaken the stated freshness contract.
Evolution: reduce sampling or decoder/cache complexity when measured simpler
behavior meets targets. Root remains deferred; Story 002 owns preview proof.

### Responsive reusable previews — Story 004, 2026-10-05

Cam requested [Story 004](stories/story-004-responsive-reusable-thumbnails.md)
after the [large SMB-file investigation](research/nas-thumbnail-latency.md).
This behavior is implemented and qualified on corrected001728, installed in the requested
local preview app. See [acceptance ledger](evidence/story-004/current-acceptance-ledger.md).
Reuse a bounded worker and successful thumbnails across requests and app restarts;
prepare a finite sparse set proactively. With no hover, use midpoint/quarter/finer subdivision for an empty cache and
fill largest remaining gaps when samples exist. With hover, finish valid bounded active work,
serve the latest hovered target next, then expand to missing samples on both
sides by distance. Pointer movement reprioritizes pending work; it must not keep
destroying useful extraction. Media/track changes, disable/close and watchdog
expiry remain interruption boundaries. Hide on hover exit while preparation
returns to largest-gap coverage. Background work yields to playback.

Persist small images and completed coverage incrementally under feature-owned
Caches. Normal close/quit must not invalidate them. Quota eviction, explicit
clearing, corruption, changed media and incompatible cache versions may require
regeneration. Deduplicate nearby requests that map to the same keyframe and show
its actual time. Keep a useful nearby image while preparing an updated sample
when its identity/time are clear; distinguish slow access from unsupported media.
Bound queue, preparation, retries and retention to prevent eviction/refill churn.

ADR-001's lifetime split remains. ADR-003 revises ADR-002's process/cancellation and cross-open identity assumptions
with a tested freshness contract. Metadata or partial fingerprints do not prove
complete content equality; no silent weakening of replacement safety or unmeasured
full-file NAS hash on the interactive path. Reuse established player mechanisms
as evidence-backed options, adapting them where local behavior warrants it.
ADR-003 accepts metadata plus a fresh SHA-256 fingerprint of 16 evenly spaced
64 KiB ranges including head/tail (at most 1 MiB; smaller files hash fully).
Device/inode, size, nanosecond mtime/ctime and selected track/transform/version
remain part of identity, guarded before and after reads. Disposable thumbnails
may reuse under this practical contract. Already-qualified local cache hits
receive a final guarded pathname metadata observation before presentation,
without reopening the video or introducing a metadata reuse window. Within a
qualified current session, already-loaded RAM samples may appear provisionally
with Checking source while validation runs. This can briefly show the earlier
source until a change/error is detected; it is not a fresh verified hit. Clear
on failure or a15s presentation deadline that pointer movement cannot renew;
block further provisional display until verification recovers. Context changes
clear immediately and reopened media must freshly qualify before reuse.
Cam delegated this presentation decision after the measured NAS metadata delay.
Changes confined to unsampled bytes
with every metadata field preserved can evade it; this is not whole-file equality
and does not define durable bookmark identity. Cam delegated the choice on
2026-10-05; full-file hashing was rejected for mandatory NAS cache lookup cost.

The story defines fresh restart, scheduler, local/SMB and native UI proof and
retains the practical baseline-median +20% ordinary-control comparison policy.

## spec:3 - Annotation persistence and media identity

Serves `ideal:req:annotations`, `ideal:req:persistence`, `ideal:req:navigation`,
`ideal:req:media-integrity`.
Need: correct durable short labels without modifying media. One to three words
is a design preference; compact single-line entry, no hard word-count validator.
Labels and videos remain local by default. Verify unchanged video hashes.

Accepted [ADR-001](decisions/adr-001-media-metadata-storage/adr.md) separates
Application Support labels, Caches thumbnails and small preferences. VLC's
resume preferences are decoded-URI→seconds records capped at 30 entries and
cleared with recent history. Reuse input/lifecycle access, not that retention.
Labels must survive history clearing/turnover, recent-items disabled and cache
cleanup. Do not write beside videos or directly edit a preferences plist.

Initial scope compromise: the same unchanged canonical local file; no automatic
move/rename/copy/cross-device reconnection (ecosystem/human scope). Different
bytes at the same path must not silently inherit notes. Proposed correctness
baseline: canonical encoded URL + fresh full SHA-256 + size, verified off-main
on each open with file-change guards. This may delay label availability on large
videos; show verifying state and keep playback independent. Measure that cost
first in Story 003. Metadata-only/cached-digest identity is an alternative with
a weaker undetectable-replacement guarantee; any change requires an explicit
ADR/spec decision before implementation, not a silent optimization.

SQLite is the provisional store candidate; system arm64 link/basic transactions
have been probed, not the product schema or restart behavior. Versioned media/
annotation records, integer microseconds, revision conflicts, durable commit
acknowledgement, schema/corruption protection and bounded background IO are the
proposed implementation. JSON remains an option with proper locking/atomic
replace/recovery. Select identity/schema in Story 003's ADR. Test restart, crash,
replacement, duplicate basenames, symlinks, read-only media, stale saves,
concurrent launches and write failures. Preserve old records on identity change.
Evolution: replace costly identity machinery when a simpler mechanism meets the
stated guarantee. Colors/tags/export/legacy import deferred. Root owns combined
proof; Story 003 owns complete bookmark capability.

## spec:4 - Interaction quality and behavioral proof

Serves `ideal:req:playback-quality`, `ideal:req:navigation`, `ideal:req:evidence`.
Need: images/short labels coexist naturally with ordinary playback controls.
Requested initial gestures: hover for preview/text; right-click a timeline
position to add; marker click to seek; context edit/delete. Show ticks and brief
labels when controls appear, clustering overlaps into a selectable compact list.
Provide keyboard add-at-playhead and label navigation/edit actions while keeping
the existing slider accessible. No paragraph authoring or separate companion
window as the primary product. These choices implement the broader Ideal.

UI geometry/input lifecycle and hover previews are implemented in the current candidate; bookmark behavior is unimplemented.
Use one context/geometry/presentation seam with thin windowed/fullscreen adapters.
Time values are microseconds, independent of pixels. Capture media/time/revision
when editing; media changes clear visuals immediately. A late completion cannot
attach to a new video. Observe duration/track changes as well as playhead ticks.

Proof compromise (ecosystem/physics): generated known-frame fixture matrix,
native pointer/keyboard/VoiceOver observation plus deterministic decoder/store
checks. The [root contract](evals/root-timeline-experience.md) specifies targets,
fixtures, repetitions, fault/retention tests and evidence. No root runner/pass
exists. The selected-window capture omits fullscreen floating panels. Real persistent-pointer events and owned-window composite captures now demonstrate hover; remaining latency/playback/accessibility gates require their own evidence. Do not replace real interaction with screenshots/AX values.
Evolution: retain small meaningful regressions and simplify instrumentation once
behavior is dependable. Each feature story owns its complete native UI proof.

## spec:5 - Project workflow and source obligations

Serves `ideal:req:evidence`, `ideal:req:media-integrity`.
Need: repeatable, reviewable source/build decisions. Methodology docs/skills/checks
are the current execution compromise (AI capability); no measured AI failure
justifies product inference or model discovery. Deletion eval deferred until a
real repeated task has a meaningful baseline; preserve evidence/review when
simplifying. Imported examples are overridden by local runbooks; source projects
stay read-only. No web port/Conductor allocation is needed for a native app and
private pipe-based helper. A future network helper would require reassessment.

Licensing is a legal constraint: verify selected source/library obligations
before distributing, preserve corresponding source/configuration/patch records,
and do not mistake a build or probe for release clearance. Public repository
already exists by Cam's request; no current permission to publish binaries or
new commits is implied. Story 001 is feasibility; 002 and 003 implement the
separate preview and durable-label outcomes. Root completion requires both.

### Story 004 correspondence/retention correction

A supplied VLC/helper video-count mismatch is ambiguous for every container; reject it before selecting an ordinal. The corrected persistent mapping namespace is `v4:keyframe-countguard2:transform1`, so prior potentially wrong-track samples are not reused. Manifest format remains v4. For the selected identity, demand-use membership covers at most512 sample records: a meaningful RAM/disk hit or an explicit store with `allowEviction:YES` promotes the sample; passive coverage/enumeration does not. Identity change or removal clears membership. Disk pruning removes background entries first, then demand/current-manifest entries as needed, while the256MiB hard cap always applies. The correction's current-source hash and baseline/candidate results are recorded in the [correction review ledger](evidence/story-004/correction-review-ledger.md).
