# Master feature port — root-owned implementation plan

Selected 2026-10-05 under Cam's authorization to finish Story005 phases1/2 with
SOL 6.1 medium builders. This is an implementation choice, not VideoLAN acceptance.
Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Preserve the qualified3.0
app/source and pristine master baseline. No commits, contact or submission.

## Decision and measured reason

Use a macOS-only installed helper built against selected FFmpeg9 contrib,
retaining the bounded decoder/fingerprint isolation and service/cache/scheduler
contracts. Extend master's existing hover panel and current player controller.
Do not depend on experimental core patches0001–0004 for this feature. Preserve
their evidence separately. Native reuse exposed a larger correlated movie-time
and presentation-eligibility prerequisite; the retained-helper discriminator
already supplies known-frame, rotation/SAR, persistent-request and reordered
selected-track proof with independent pixel references.

Use the normal contrib source patch list to expose representable positive
Matroska TrackNumber in AVStream.id. Independent source review finds VLC's
avformat demux uses stream index for its ES IDs, with no direct AVStream.id
consumer in its playback/mux paths. Test the affected FFmpeg ID selectors and
stream groups and forced-avformat playback. This is simpler to reproduce than a
second private FFmpeg build or host-specific archive surgery. A separate
FFmpeg-ready patch and dependency rationale belong in the eventual package;
acceptance and submission order remain maintainer decisions.

The source-backed MOV-origin concern was not a demonstrated failure: exact
helper captures preserve origin0, actual2s and duration14s for the initial-gap
fixture, matching its independent moviePTS2 reference. No speculative correction
is authorized. Keep this regression and record an actual counterexample before
changing origin policy. Baseline native pixel/clock observations are separate,
non-atomic evidence; the helper must report its actual movie sample, not copy a
baseline clock bias. Sparse keyframe distance remains permitted and visible.

## Frozen cross-owner contract

- Immutable context dictionary on main: `generation` (session UUID plus monotonic
  generation), `url` (owned file URL), `duration` (positive microseconds),
  `eligible`, `videoStableID` (copied certified stable string), `videoInputID`
  (nonnegative int), `videoCount` (1..128), `sourceEpoch` (owned input-lifecycle
  counter). No borrowed pointer escapes. Read URI,
  duration, capabilities and exactly one selected video in one player lock.
  Invalid/unknown/multiple selection is ineligible. No filesystem work under lock.
- Current-media notification invalidates even for the same URI. Track-list,
  selection, length, capability and stop events refresh a coherent snapshot;
  presentation generation rejects delayed callbacks. Pointer movement cannot
  renew the context's15s provisional-source deadline.
  Advance sourceEpoch synchronously in player-locked source/input lifecycle
  callbacks before queuing main notifications; the atomic getter copies it and
  context generation compares it. A same-URI reopen must qualify anew even if
  a pointer event precedes its queued main notification. Do not substitute an
  input-item address that can be reused.
- New helper protocol4: required `--video-input-id` and `--video-count`, local
  file, dimensions and worker/one-shot mode. Keep bounded request lines and
  JSON-header/RGBA payload framing. Replies include `video_input_id`,
  `video_count`, `mapping` (`single` or `matroska-track-number-flat-v1`) and actual
  `video_track_number` (positive Matroska identity or -1), alongside actual/request
  time, dimensions, source and operation counters. These are not player clocks.
- For flat Matroska, require positive unique TrackNumbers and exact requested
  input-ID match; retain the qualified AVC multi-video restriction and count
  guard. For one other video, count equality establishes the sole-stream mapping.
  Other multi-video mappings fail closed; they were never generally qualified.
  Do not parse opaque ES string IDs or use menu order as identity. Parent validates
  reply identity/count/mapping before accepting pixels. Explicit failure never
  falls back to another track.
  H1 requires explicit flat admission before using the new mapping string. A
  bounded opt-in FFmpeg existing-EBML-parser scan is selected for a prototype:
  inspect all finite top-level elements independently of SeekHead, reject ordered
  editions and hard/medium links, unknown-size Clusters, incomplete parse or
  restoration/budget failure. Use isolated512-byte AVIO buffering, at most8MiB
  physical admission reads,20k seeks and100k structural nodes within the existing
  operation deadline. Preserve original AVIO buffer/cursor ownership. Final
  acceptance depends on exact parser/fault tests and representative NAS cost;
  fail-closed alone does not qualify responsiveness. See the gate design evidence.
- Cache namespace changes to `v5:keyframe-master-id1:transform1:flat-mkv1`, including source
  policy/identity, stableID, numericID and count. Header protocol4 and new namespace
  cannot reuse old protocol3/ordinal images. Keep32MiB/256MiB,512samples/2048aliases,
 255targets, finite retries/demand retention, atomic safe cache files, sampled
  hash caveat and fresh-open qualification. Labels/bookmarks remain unrelated.
- Public helper name `vlc-timeline-preview`, installed in `pkglibexecdir` and
  copied/signed beside the app executable. No host executable/PATH dependency.
  Existing code is refactored for surrounding style; omit prototype path-based
  trace/event-monitor hooks. Retain useful internal counters and normal logging.
- Objective-C seam names: player `-timelinePreviewSnapshot` returns the owned
  dictionary without generation; `VLCTimelineContext` adds generation and exposes
  `+sharedContext`, `-snapshot`, `-refresh`, `-invalidate`, notification
  `VLCTimelineContextChanged`. It starts after player initialization in VLCMain
  and invalidates/shuts service down during app termination. Service retains
  `+sharedService`, `-initWithHelperPath:cacheRoot:`, `-prepareContext:enabled:`,
  `-cancelRequest:`, `-cancel`, `-shutdown`, internal `-metrics`, and replaces the
  old ordinal request with `-requestForContext:time:completion:` returning a
  request token. Completion is `(NSImage *, NSDictionary *)` on main. Worker
  uses `-requestURL:videoInputID:videoCount:time:` plus existing fingerprint,
  invalidation and metrics methods. Root approves any change to these seams.
  `-invalidate` on context is terminal: stop/remove observers before publishing
  an ineligible context; internal source-refresh invalidation uses a private
  reusable method. Commit context state before synchronous callbacks/notifications
  so a reentrant snapshot read cannot recurse or resurrect shutdown work.
- Existing slider owns pointer time, expanded centered hover target, preview
  image and actual keyframe/status caption. Reuse its one nonactivating panel;
  preserve seek/scroll/keyboard and accessibility ownership. Hide/cancel on
  fade, disable, drag, window reparent/removal, inactive app and context changes.
  Preserve saved/CLI preference precedence and localize complete user strings.
  Acquire a potentially refreshing snapshot before establishing new hover state;
  refresh before checking callback serial/state. Keep pointer caption time at the
  endpoint but clamp preview request time to duration-1 microsecond, respecting
  the service's half-open media interval without inventing a frame timestamp.

## Disjoint builder ownership

| Owner | Files and responsibility | Done evidence |
|---|---|---|
| Helper builder | `bin/timeline-preview/` C source/protocol, FFmpeg patch source file | Protocol4, identity/resource/network bounds, fresh fixture and malformed/failure proof |
| Build owner | configure, Autotools/Meson lists, contrib rules, package/sign files, reproduction | Normal verified-source dependency build, relocatable signed package, target checks/dist inputs; no host archive replacement |
| Context builder | dedicated snapshot method in VLCPlayerController; `timeline/VLCTimelineContext.*`, VLCMain startup/shutdown and context tests | Owned atomic snapshot, no borrowed ES pointer; coherent lifecycle/generation/selection tests |
| Service builder | `timeline/VLCThumbnail{Service,Worker,Cache,Scheduler}.*`, associated XCTest source | Protocol/namespace adaptation, bounds/lifecycle/cache/freshness regressions using injected test paths |
| UI builder | progress slider, controls fade hook, preferences/macOS option/XIB, localization list and UI-related tests | One panel and tracking owner, localized state/preference lifecycle, baseline control semantics preserved |
| Review/fixture lanes | independent reviews and legal dependency/fixture regressions | Material findings resolved; exact source/binary/fixture receipts; no qualification by compilation alone |

Builders share only the frozen interfaces above. Build owner alone edits build
lists and integration source application. Root resolves any proposed contract
change. Use the existing isolated candidate source/output after exact reversal of
prototype patches and preservation of their bounded artifacts; do not duplicate
another multi-gigabyte build. Stop at1GiB free, never delete preserved originals.

## Validation and public series

First compile the helper and pure/native test seams, then integrate the app. Run
new helper identity/PTS/transform/fault tests, source-fingerprint/service/cache
contracts and registered macOS tests. Port existing legal fixture recipes with
explicit tool requirements and compact generated media provenance. The public
package must reproduce without this wrapper repository, diary or ignored tools.

Native qualification follows the unchanged [protocol](verification-plan.md):
four surfaces, pointer/keyboard/reader, preferences/context races, NAS/fresh-open/
source mutation/corruption/eviction,20valid controls per arm at median+20%, and
three60s active-preparation playback pairs. UI access has recovered; reliable
baseline lifecycle setup and current candidate qualification remain open. ARM host proof cannot establish
Intel/olderOS coverage. Record unavailable CI/build matrix coverage explicitly.

Selected draft review series: (0) existing source-header distribution prerequisite;
(1) FFmpeg TrackNumber and flat-admission prerequisites
with focused regressions; (2) bounded helper, normal build/package integration and
portable fixtures/guide; (3) integrated native context/service/cache/hover/preferences
and regression coverage. The third part stays coherent because startup, build
lists, shared contracts and tests depend on the complete native slice; splitting
that feature part further would require temporary integration stubs. The separate
leading prerequisite lists four unchanged Apple headers beside their consumers in
`modules/audio_output/Makefile.am` and `modules/video_output/Makefile.am`, plus
`LazyPreparser.h` in `modules/misc/Makefile.am`. Actual archive compilation exposed
both failures; independent source review clears the three-file metadata-only fix.
The earlier archive inventory had identified the media-library omission, and the
next compile proved it is required by the selected build graph. The unrelated
Windows header remains out of scope. This changes no runtime code, condition or flag.
The existing three feature patches remain byte-identical to revision 6. Exact source application is
verified in the draft feature-series manifest, but runtime readiness is separate. Independent review, licensing/source inventory, clean reproduction and exact
public diff are mandatory before readiness. No claim of ready-to-submit until
those and the native gates are satisfied.
