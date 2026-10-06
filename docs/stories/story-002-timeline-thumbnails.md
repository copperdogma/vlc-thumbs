---
id: "002"
title: "Thumbnail previews on the macOS timeline"
status: Done
priority: High
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity, ideal:req:evidence]
spec_refs: [spec:1, spec:2, spec:4, spec:5]
adr_refs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services]
decision_refs: [docs/decisions/adr-002-native-thumbnail-services/adr.md, docs/decisions/adr-001-media-metadata-storage/adr.md, docs/research/timeline-implementation-plan.md, docs/runbooks/build-vlc-macos.md]
depends_on: ["001"]
category_refs: [spec:1, spec:2, spec:4]
architecture_domains: [native-timeline, thumbnail-decoding, disposable-cache]
eval_refs: [root-timeline-experience, story-002-preview-capability]
---
# Story 002 — Thumbnail previews on the macOS timeline

**Status:** Done — native preview preference follow-up validated and locally installed. **Priority:** High. **Depends on:** 001.
Cam authorized finishing Story 002 on 2026-10-04. The written feature plan is
approved by that request. Pinned native build/decoder substrate exists;
implementation now follows ADR-002 and the acceptance gates below.

## Goal

Hover over VLC's actual macOS timeline and see a recognizable nearby keyframe, while video playback continues untouched. Deliver the complete native
interaction, bounded background extraction and disposable cache in an isolated
app, on main, detached, native-fullscreen and custom-fullscreen controls.

## Eval Ladder Context

Root: `root-timeline-experience`, deferred and never attempted because
bookmarks are not implemented. This story's preview capability checks use its
ACs and the root contract's threshold/fixture tables. Automated helper/service
contracts and physical native interaction attempts exist. Cam approved
150/200 ms absolute limits for historical scoring on 2026-10-04. On2026-10-05
Cam approved a shared-load-aware course correction after reporting two other
AI threads continuously use the machine. The earlier root-selected zero-added-
allowance rule and100-sample p95 plan are historical. Cam subsequently clarified
that an actual baseline/post performance comparison remains mandatory, while
precision requirements should be practical. The current predeclared plan uses
20 responses per arm, actual visible-response medians and a20% allowance against
preserved baseline; ranges and block variability are reported. Precise tail and
causal-stall characterization may remain unqualified, but an invalid ordinary-
control comparison does not complete this requirement. See the
[required pragmatic comparison plan](../research/story-002-pragmatic-before-after-plan.md).
Preview delay has no vanilla denominator and is descriptive, without an
invented threshold. Re-scoring is separate from the retained measurements. Diagnostic extraction probes
alone do not measure UI, playback impact, cache or broad format support.
Candidate-specific results and open gates are recorded in the
[current acceptance ledger](../evidence/story-002/current-acceptance-ledger.md).
Root becomes runnable only when Story 003 also works.

## Acceptance Criteria

- [x] **Preference:** Native basic Interface preferences expose an enabled-by-default preview checkbox; Save applies it to existing timelines, Cancel leaves it unchanged, and the choice persists after restart. Off hides/cancels preview work and restores normal timeline controls.

- [x] **Native experience:** Hover shows time plus image above the actual track;
  geometry follows the drawn track at window sizes/scales and endpoints. No
  playback seek, pause, sound or focus change occurs merely from hover. Main,
  detached, native and custom fullscreen each have recorded interaction proof.
- [x] **Correspondence:** Required fixtures pass normalized frame/time mapping,
  including MP4 and MKV, long GOP, VFR, nonzero start/edit offsets, rotation and
  aspect ratio. The image is independently verified as a keyframe from the
  selected track; show actual frame time separately from pointer time and record
  distance/density. Cam accepts keyframe gaps for the MVP; extra decoded samples
  can follow if trials find them too coarse. Missing/ambiguous timestamps or unsupported presentation
  show unavailable; they never produce a guessed or stale successful preview.
- [x] **Responsiveness:** Obtain a usable measured before/after native ordinary-
  control comparison on matched preserved baseline and feature apps. Use20
  responses per arm in four AB,BA,BA,AB blocks, report median/range/block
  variability and all errors, with root-selected20% median allowance. Preserve
  actual independent pixel-render evidence and display timestamps; AX value
  alone is not visible response. No exact equality or precision p95 guarantee
  is required. The comparison itself remains mandatory for closure; precise
  tail latency/causal attribution may remain explicitly deferred. Follow the
  [corrected plan](../research/story-002-pragmatic-before-after-plan.md).
- [x] **Bounded work:** One decoder worker, one active + one replaceable pending
  request, finite timeout/restart policy, <=32 MiB decoded cache and <=256 MiB disk
  cache. Measure worker memory/CPU and enforce selected caps. Request bursts,
  leave/hide, track change, stop, media replacement and rapid switching never
  allow a stale result to attach to another request/media or grow a work backlog.
  Test same-size/preserved-mtime replacement on reopen and during in-flight
  extraction. No cross-open cache reuse without the ADR's verified freshness
  contract; the conservative default treats those entries as misses.
- [x] **Fault handling:** Unsupported/audio-only/nonseekable/unknown-duration
  sources, corrupt cache, unwritable/full cache, worker crash/hang and malformed
  reply fail locally and recoverably. Playback continues; no infinite restart
  loop or label-store access. Local files cannot cause helper network fetches.
- [x] **Playback/control integrity:** Preserve normal drag/click/wheel/keyboard
  seeking, volume, focus and controls reveal/hide. Meet the <=1 percentage-point
  dropped-frame increase for each matched playback pair and verify audio
  continuity. Fix demonstrated feature-induced interruptions or stalls; disclose
  unattributed repeat observations in both arms as deferred precision
  characterization rather than asserting absence of stalls. Verify source video
  SHA-256 before/after. Existing slider accessibility remains usable; decorative
  previews do not steal focus or repeatedly announce on mouse movement.
- [x] **Reproducible app:** Patch/source/build recipe tracked outside ignored
  work; applies to pristine pin. Helper resolves from the bundle and runs arm64
  without host PATH/non-system dylib leakage. Bundle/cache signing remains valid.
  Exact linked source/config/license provenance recorded; public release deferred.

## Out of Scope

Bookmark implementation, entire-video precompute, remote/live/DRM sources,
all-codec equivalence with VLC, subtitles or user video effects baked into
images, universal/Intel/other-platform packaging, notarization/distribution and
changing installed VLC. Unsupported cases must be explicit. Root completion is
not claimed by this story alone.

## Approach Evaluation

| Candidate | Benefit | Evidence / selection test |
|---|---|---|
| Private helper linked to existing contrib libav libraries | One engine, independent decode, per-frame timestamps, process isolation | Preferred candidate: 15 tiny-fixture requests passed; real resolution/PTS/IPC/cancellation gate still required |
| AVFoundation only or with fallback | Native async/transform API | MP4 passes, same-stream MKV fails; two engines add qualification/maintenance |
| Independent public LibVLC player | VLC demux/decoder breadth | Callback frames lack PTS, snapshot async and input clock is not frame identity; must solve that before adoption |
| Bundled FFmpeg CLI | Familiar extraction workflow | Can work, but requires its own packaging/protocol and no benefit established over verified libraries |

**Simplification baseline:** Deterministic local UI/decoding; an LLM call cannot
provide continuous native pointer interaction or decode exact video frames.
AI-only/hybrid inference adds no product capability. No paid model measurement
required. Reuse pinned VLC sliders/input lifecycle and existing contribs;
AVFoundation probing is evidence, not a second shipped engine.

Select the route with the initial fixture/cancellation/packaging spike, record
an integration/decoder ADR, and update the plan before broader implementation.
ADR-002 selects this route; Cam subsequently chose keyframe-first sampling. ADR-001 already requires
separate disposable cache storage. See the synthesis for alternative costs.

## Tasks

- [x] Recheck disk headroom; preserve/reuse the working build and pristine pin.
  Record candidate base revision and existing build repairs separately from
  feature patches; do not rebuild all dependencies without evidence of need.
- [x] Establish the checked-in patch/source layout and reproducible apply/build
  command; add generated fixture manifest/recipe and a diagnostic attempt format.
- [x] Run the first technical gate: production-shaped seek/decode on required
  formats/time origins, bounded worker IPC/cancel and bundle launch; select route
  and record its ADR. Treat probe source as a sketch, including missing codec
  EAGAIN/EOF handling, not a ready implementation.
- [x] Implement read-only media context/generation and timeline geometry adapter;
  observe input and duration/track changes. Map selected video track deliberately.
- [x] Implement helper: normalized PTS selection, aspect/rotation/color policy,
  protocol/resource bounds, file-only access, timeout and clean shutdown.
- [x] Implement latest-demand scheduling and memory/disk LRU caches, versioned
  freshness keys, atomic writes, invalidation and confined cache cleanup. Select
  the explicit cache freshness contract in the decoder ADR; default to a fresh
  media-open namespace and metadata guards, with cross-open reuse requiring
  freshly verified content identity. Document continuous external mutation limits.
- [x] Implement one hover presentation with time/loading/image/unavailable;
  wire separate windowed and fullscreen sliders without global slider changes.
  Reserve composition for Story 003's labels without implementing their store.
- [x] Obtain native fullscreen panel/pointer evidence early; selected-window
  captures from feasibility did not expose the floating panel. Use a functioning
  pointer driver or recorded human exercise; do not replace hover proof with
  direct method calls or AX value assignment.
- [x] Add meaningful automated tests for geometry, timestamp normalization,
  generation/cancel races, cache ownership and malformed helper responses.
- [x] Run required fixture and failure cases, actual native UI/keyboard checks,
  paired playback/resource benchmark and video hashes. Capture images and
  actual frame PTS/time, not only successful return codes.
- [x] Inspect patch application, incremental build, bundle signing/dependencies;
  record commands, failures and supported scope in evidence. Update eval registry
  when a runnable contract/attempt exists; keep integrated root deferred.
- [x] Update relevant spec/state/runbooks, remove redundant prototypes/paths,
  regenerate views, run `make validate` and `git diff --check`, then `/validate`
  and `/mark-story-done`. Commit/push only on request.

## Architectural Fit

Owning areas: native timeline adapters, isolated preview service and disposable
cache. Spec:1/spec:2 have the declared previewMVP substrate; spec:4 remains partial for bookmarks/integrated-root behavior. At the 2026-10-05 MVP closeout, 132643 functional acceptance was supported; subsequent native preference and Story 004 work are recorded below and in the current ledgers. There is no imported game coverage matrix or web driver to run.
The root fixture table is the local coverage contract.

Verified seams: `VLCSlider.m` 137 lines; `VLCSliderCell.m` 354;
`VLCControlsBarCommon.m` 459; `VLCFSPanelController.m` 564;
`VLCInputManager.m` 766; `Makefile.am` 826. These are pinned upstream counts.
Keep heavy new logic in feature files, thin lifecycle/UI integration in existing
controllers, and a shared adapter reused by Story 003. Do not cast internal
`libvlc_int_t` to public `libvlc_instance_t` or seek the playing input.

Proposed contracts: context snapshot `{generation, URL, duration, seekable,
videoTrack}`; request/reply with generation/request ID, selected stream,
requested/actual microseconds, dimensions, transform/version and result/error.
Cache freshness is not annotation identity and cannot authorize durable restores.

## Files to Modify

Tracked additions, finalized by the technical gate:

- `patches/vlc-3.0.24/` plus `src/macosx/` and `src/thumbnail-helper/`: reviewable
  integration patches and owned source; no vendored whole checkout.
- `scripts/`: apply/build/probe/fixture commands with isolated toolchain paths.
- Target upstream `VLCSlider`/cell or a timeline-only subclass, controls common,
  fullscreen controller and their XIBs; input manager for lifecycle/duration;
  `modules/gui/macosx/Makefile.am` and macOS bundle-copy/signing recipe for helper.
- Proposed `VLCTimelineContext`, `VLCTimelineInteractionController`,
  `VLCThumbnailService`, `VLCThumbnailCache` and helper source files.
- `tests/` for deterministic contracts; `tests/fixtures/golden/` manifests with
  generated media ignored. `docs/evidence/story-002/` for measured attempts.
- Spec/state, eval registry/root contract, build runbook and decoder ADR.

## Redundancy / Removal Targets

Do not ship both experimental extractors or keep two tooltip/geometry systems.
Retain historical probe evidence; remove temporary production stubs once helper
integration replaces them. No removal of VLC's ordinary playback controls.

## Project Tenets

- [x] Preserve source videos, installed VLC and real user data.
- [x] Pin source/dependency/fixture provenance and report untested scope.
- [x] Measure before claiming responsiveness or simplifying decode behavior.
- [x] Keep UI, decode, cache and durable notes independently owned.
- [x] Inspect native interaction and rendered frames; compile success is insufficient.

## Workflow Gates

- [x] Substrate inspected and implementation plan/technical ADR recorded.
- [x] Applicable implementation authorization recorded.
- [x] Build complete: implementation finished, required checks run, summary shared.
- [x] Validation complete or explicitly skipped by user.
- [x] Story marked done via /mark-story-done.

## Blocker Summary

No current completion blocker remains in the declared MVP scope. The required
pragmatic ordinary-control comparison is complete and independently audited:
20 responses per arm on the final preference build155231, baseline median222.039ms versus feature236.531ms, within
the prospective20% allowance. Three matched playback pairs and functional proof
remain applicable. Precise tail latency and causal-stall attribution remain
unqualified; no general performance guarantee is claimed.

## Blocker Evidence

The [current validation](../evidence/story-002/preview-preference-validation.md)
and [numeric result](../evidence/story-002/ordinary-control-preview-preference-final.json)
retain medians, ranges, block variability and all40 scored observations. All52
raw session contracts, owned clean exits and unchanged product fingerprints
were audited. Previous invalid cohorts and premature closure remain historical,
unpooled and unrescored.

## Unblock Condition

Satisfied by the complete actual baseline/post comparison, applicable functional
and matched-playback evidence, and findings-first independent audit. Any later
independently reproducible feature defect remains a defect; shared load does
not explain it away.

## Plan

Story002 is complete through validation and mark-story-done for the declared
native/keyframe/local-media MVP. The required practical comparison is distinct
from deferred precision characterization. Story003 bookmarks and integrated
root remain separate. No commit/push/public distribution is authorized.

## Work Log

20261004 — Created at Cam's request after deep source/build/decoder investigation.
Distinct story justified by the image/caching/correspondence contract; durable
labels have a separate write/restart/identity contract in 003. Build baseline
and libav probe verified; no feature code implemented. Main owns planning;
bounded lower-cost inventory and stronger persistence review informed synthesis.

20261004-0706 — Started at Cam's explicit request to set a goal and finish 002.
Existing full feature plan approved; use loop-review hourly if work continues.
ADR-002 selects timeline-only adapters, existing-contrib helper (one process per
uncached demand initially), session-scoped cache and bounded latest-demand work.
Source/build substrate rechecked; 6.4 GiB free. Main owns GUI/service/integration;
bounded delegation permitted by project instructions with disjoint file owners.
First useful milestone: visible preview in native app, then all surfaces/tests.

20261004-0730 — Cam clarified MVP intent: nearby keyframes give a sense of the
general area; exact frames at every timeline point are unnecessary. Replace the
agent-proposed half-second preview correspondence gate before keyframe scoring.
Retain the North Star Ideal. Show actual preview time and keep optional denser
decoding as future refinement based on use. Prior precise-decoder measurements
remain historical evidence, not the revised MVP result.

20261004-0733 — Keyframe-v2 helper passes 22 cases and 200 requests, independently
checking keyframe flags/PTS/pixels. Candidate app compiled, bundled and signing
verified through tracked runner; patch checks clean on pristine pin. Native hover
is still unqualified while Mac locked; no completion/root claim. Reports in
docs/evidence/story-002. Service/cache fault/latency checks continue separately.

20261004-0742 — Bundled helper runs with empty PATH and signing remains valid.
Added actual chmod/ENOSPC tests on a verified owned 20 MiB disk image; previews
survive both failures and disk persistence recovers. Test image detached.
Same-size/ns-mtime-preserving atomic replacement rejects an in-flight reply and
forces a reopened cache miss. Inputs/media unchanged; reports archived.
Native UI is still unavailable: Computer Use rechecked the locked Mac at 07:37.
No UI/playback completion claim; manual unlock request remains pending.

20261004-0743 — Blocked audit: the locked Mac prevented required native checks
on three consecutive goal turns (initial interaction attempt, cache-fault
continuation, and this recheck). Decoder/service/fault/bundle evidence passes;
remaining completion depends on actual pointer/fullscreen/control/playback
validation. No independent implementation work remains justified before that
end-to-end demonstration. Mark goal/story Blocked pending manual unlock, not
Done; preserve the full objective and all remaining acceptance gates.

20261004-1504 — Cam unlocked the Mac and explicitly requested continuation.
Native app/AX access verified; goal/story resumed. Loop-review: aligned but
at risk until the user-facing result is demonstrated. Decoder/cache work is
qualified in its own scope; prioritize a visible native hover over expanding
backend checks. Actual slider pointer event reaches adapter, but preview hides
within100ms; add bounded visibility diagnostics and resolve before other surfaces.
Use LaunchServices open -n for registered app launch; direct Popen plus immediate
Sky access caused a second blank instance, which was closed. Next hourly review
16:04 UTC during active work. No added scope or approval needed.

20261004-1523 — Resumed native validation opened generated standard.mp4 through
NSOpenPanel and paused playback at 00:07. Both adapters initialize with attached
windows. The Mac locked again before the first instrumented hover, so native
preview behavior remains unproved. Added opt-in event-versus-persistent-pointer
coordinates and slider visibility/tracking diagnostics; rebuilt successfully
(app-build-20261004T152137.038094Z). No inferred tracking fix or UI success.
Manual unlock requested; continue with actual pointer evidence before further
architecture changes. Preview child panels are excluded by the tool's selected
parent-window screenshot, so absence from that screenshot alone is inconclusive.

20261004-1524 — Fresh blocked audit after manual resume: the Mac locked again
during the user-triggered continuation and remained locked on both automatic
goal continuations. Instrumented candidate is built and running, but actual
hover/popup, fullscreen, track selection and playback validation cannot proceed
without desktop access. No further speculative implementation or redundant
backend testing is justified before observing native pointer behavior. Mark
Blocked pending unlock, preserving all Story 002 requirements.

20261004-1618 — Cam is at the unlocked computer and explicitly resumes.
Native OpenPanel verified accessible. Hourly loop-review: aligned but at risk
until visible preview proof; preserve all acceptance gates and prioritize
event-versus-persistent-pointer observation before further tracking changes.
Next review due 17:18 UTC during continued work.

20261004-1624 — Bounded primary AppKit research and local pass-through monitor
resolve the automation ambiguity: tool event {733,7} is inside the slider while
persistent pointer {1076.875,271.47265625} is outside. Tracking area attached
and fully visible. Physical movement elsewhere matches coordinates. Tool
clicks cannot prove sustained hover; human baseline requested asynchronously.
Research and next experiment: docs/research/native-hover-input-validation.md.

20261004-1629 — Actual main-window controls: click sought to 00:12; drag
sought to 00:35; vertical wheel changed position to the end (coarse tool scroll,
not a hover). Command+Option+Right sought paused media from 00:22 to 00:32.
AX volume set 50% and restored 100%; Position remains an AX slider and the
window stays focused. Horizontal scroll is ignored by upstream deltaY logic.
Command+Right is next-item, not a seek binding; menu cancellation verified
via its explicit AX Cancel action. These observations cover ordinary controls
only; no hover-dependent playback/focus guarantee claimed yet.

20261004-1631 — Blocked audit after resumed real-pointer request: current app
is live/unlocked but Sky has no sustained hover operation; three consecutive
goal turns still have zero actual entries/displays. Current build/diagnostics
archived and ordinary controls checked. No further speculative tracking change
or repeated backend checks is justified before real hover. Mark Blocked on
physical-pointer baseline or explicit alternative automation request.

20261004-1648 — Cam hovered; app crashed in CFRelease/VLCSliderCell dealloc.
The controller copied the resource-owning cell twice across actual movements;
upstream has no copyWithZone override for its display link. Bounded NSCopying
research and pinned source review support removing the copy rather than
patching upstream ownership for a geometry query. Read live bar/knob bounds
without changing playback value. Cam explicitly permits alternative computer
interactions; use actual persistent pointer movement for regression/UI proof.

20261004-1700 — Main and custom-fullscreen previews visibly demonstrated after
copy removal, with real pointer events and composite captures. 9000 guarded
geometry queries and 20 entry/exit moves pass; paused position stays 00:08.
Cam confirms it looks good and requests taller hover. Select 32pt total height
based on Apple macOS 28pt recommendation; parent tracking expands only hover,
leaves slider actions/drawing/AX untouched, and clamps within controls bounds.
Rebuilt candidate; above/below/leave/resize validation next.

20261004-1719 — Main 32pt above/below/leave passes with paused time 00:15.
Custom fullscreen visibly passes expanded target after panel reveal completes;
native-fullscreen launch also displays a preview, paused time 00:07 unchanged.
Detached window produces previews above/below and hides outside, but full
controls visibility/resize/focus checks remain. Native-pointer AX presses target
only isolated PID/window, with unique match required. Keep foreground app in a
live exec session: background Popen children vanish after command completion,
then Sky transparently launches a default instance. This was test lifecycle,
not evidence of a native-fullscreen feature crash. Current live detached PID48344.

Cam finds ordinary keyframes more than adequate. A valid synthetic 24s H264
with exactly one initial keyframe proves sparse coverage: requests throughout
return actual time 0. Record a future maximum-gap supplementary-image policy;
no threshold or fallback is implemented. Source video stays unchanged.

Hourly loop-review at 17:18 UTC: aligned and progressing. User-visible preview
now works, so preserve keyframe MVP and finish native/presentation/playback
proof. Defer sparse fallback design rather than expand decoder qualification
before current story is proven. Next course check 18:18 UTC if still active.
SCK observer compiled, first standalone run aborts in WindowServer initialization;
bounded primary AppKit research supports explicit NSApplication.shared before
capture. Rebuilt observer pending live retry. Goal tool now reports active.

20261004-1758 — Detached baseline drawing defect isolated to VLCVoutView filling outside its bounds on modern AppKit. Apple guidance supports intersecting the fill with self.bounds; actual rebuilt wide/resized controls/previews now visibly pass. Failed layer experiments removed. Candidate manifest: app-build-20261004T173718.293740Z.json.

Recovered about 1.2 GiB by deleting only compiled intermediate objects/archives under the owned contrib build tree, preserving installed dependencies/source/fixtures/apps. Manifest: intermediate-cleanup-20261004.json. Cam previously authorized reclaiming owned build artifacts if space is low.

Before scored disk-LRU runs, declare a 90-second stream-copy loop derivative of standard MP4/MKV. One hundred half-second buckets in the 60-second source cannot exceed 32 MiB RAM. The derivative supplies 150 distinct buckets with identical codec/resolution/encoded frames; burned labels restart at 60s while presentation timestamps continue. This is solely the cache-pressure fixture; playback pairs retain the 60s source. Provenance: cache-pressure-fixtures.json; pair size about 219 MiB.

First full baseline played through, but the observer did not finish within seven seconds after the active trial ended. Collection failed; no playback pass inferred. Increased observer finish grace to bounded twenty seconds with explicit timestamps, keeping active playback sixty seconds. Fresh baseline retry running.

20261004-1812 — All six paired60s collections finish cleanly after20s observer grace. Before-Utility increases .556/.500/3.111pp: third fails unchanged one-point gate. Audio tone calibrated independently at440Hz/-21.07dBFS; no interior audio silence/PTS gaps in six trials. Video repeat candidates exist in both arms and require attribution; no full playback pass. Source hashes unchanged. New research thumbnail-playback-priority.md records Apple Utility QoS guidance and predeclared experiment. Utility queue/helper candidate built/signed manifest180947; fresh production-path pair running with developer tracing disabled in both arms. Scheduling and tracing changes jointly tested, not separately causal.

Native MP4 attempt001 retains350outcomes: memory/disk phase p95 assignment25.94/7.64 ms, but one miss was unexpectedly RAM because startup pointer had warmed it. Uncached condition fails qualification; do not hide sample. Fix test lifecycle using ordinary media reopen after pointer moves outside, verifying new generation/no prior scored-bank demands. Native timing scope is mouse-event to image assignment with loading proxy, separately checked against actual visible screenshot. Utility-version native trials next.

20261004-1823 — Hourly loop-review18:18: aligned/progressing, closeout at risk. Current Utility production-path dropped-frame increases .137/−2.100/−8.078pp; audio continuous, sources unchanged. Pair2 differs by one logical pixel in window/track width; report this confound, do not erase prior third-pair failure. Screen recorder gaps and baseline repeat intervals leave strict stall assessment open.

Native MP4003 after ordinary fresh reopen has350fault-free outcomes:100miss/100RAM/50pressure-seed/100disk. p95 native event-to-image assignment129.75/8.36/9.24 ms for miss/RAM/disk; loading proxy2.80/2.69/3.32 ms. Visible calibration shows expected80s keyframe from looped source (burned20s). MKV trial running. Wrapper002 failed because pinned oldrc rejects playlist commands while paused; source check justified resuming off-track before stop/add, then establishing fresh paused0. Failed001/002 retained. No user media/app/store mutation. Next review19:18 if needed.

20261004-1852 — Final MKV native trial001 completed350fault-free outcomes; p95 event-to-image assignment143.78/7.58/8.31 ms for miss/RAM/disk, loading proxy4.30/2.57/3.13 ms. Selected-track native menu proof switches redTrack1 to blueTrack2, generation changes and actual video/preview match. Main-window final candidate click/drag/wheel/keyboard seeking, AX volume and focus checks preserve paused state.

Reclaimed445MiB from five exact owned regenerable artifacts with hashes recorded in regenerable-cleanup-20261004.json, retaining fixtures/source/installed dependencies/apps/evidence. Free space after cleanup about1GiB.

Fullscreen disappearing controls were reproduced on pristine baseline; explicit activation/settling plus persistent movement reveals them. Final candidate custom fullscreen now visibly passes32pt above/below/leave, fade after moving outside and reveal, and actual click seek while paused. No product fade workaround. Owned-panel captures fullscreen-final/ exclude unrelated overlays. Native-fullscreen/detached final matrix and strict playback stall assessment remain open.

20261004-1854 — Final candidate native-fullscreen mode passes above/below/leave at fresh AX track925..942, unchanged paused13s, four-second fade outside/reveal, actual click seek43s. Detached final candidate passes wide and resized960x608 controls/previews: above/below/left/right/leave preserve paused23s; native click seeks44s. Focus stays own video window; captured owned windows exclude unrelated overlays. All four current surfaces have actual visible32pt hit-area proof.

20261004-1907 — Geometry-controlled pair2 attempt004 finished both arms; exact recorded window/track sizes match. Selected production cohort changes now+.1366/−1.1521/−8.0783pp, all below unchanged1pp limit. Historical geometry-confounded003 and failedbefore-Utility002 remain preserved. Strict stall attribution remains unqualified.

Read-only review found fullscreen setupControls restores the generic tooltip after the adapter clears it. Move adapter construction immediately after setupControls, preserving translated AX overrides. Exclude decorative preview panel accessibility element/children/navigation children; real slider remains accessible. Rebuilt/signed manifest190039. New actual main hover AX tree has no preview text/image descendants and retains Position/volume sliders; focus remains main video. No actual VoiceOver speech test claimed. Earlier350-demand measurements and cohorts apply to180947, before these bounded UI changes.

A five-second Animation Hitches applicability capture reached its recording time limit but did not finish serialization; shell briefly reported ENOSPC. Terminated only owned xctrace PID89515 after bounded shutdown attempts; output is an incomplete40KiB trace, no performance conclusion. Disk availability varied from259MiB to1.5 GiB. Incremental build preflight now estimates128MiB reserve plus four copies of current GUI/helper sizes, instead of an arbitrary1GiB requirement; actual small rebuild succeeded. Fresh/dependency builds still need separate sizing.

First native switching diagnostic is unqualified: opening the small two-track clip resized the main window, invalidating recorded hover coordinates, and paused oldrc state made final add ambiguous. Preserve lifetime-actions.json/screenshots as diagnostics. Next test must derive fresh AX geometry after each verified media transition and qualify an actually in-flight demand, then close a detached window during work. No stale-delivery pass inferred from this attempt.

20261004-1918 — Native lifetime attempt002 corrects setup with fresh AX geometry and verified ordinary input state. Actual demand on standard is in-flight at A→B switch; no old-generation display occurs after the new B hover. B is visibly red, then stop/reopen A shows its own36s keyframe while paused0. First attempt afterEOFstop could not establish paused0 and remains diagnostic. Final detached-close proof records in-flight demand before actualAXclose, context invalidation, no completion display, no preview/video window, and surviving app.

Fullscreen tooltip removal on modern AppKit also removed the only exposed slider name: translated legacyoverride labels were empty. Copy the existing translated tooltip into accessibilityLabel only when no label exists, then remove tooltip. Rebuilt/signed191250. Actual custom-fullscreen AX description nowPosition; two-second stationary track hover has preview/control/video windows only, no duplicate tooltip. Decorative preview text/images remain absent from AXnavigation andfocusstaysvideo.

Native helper permission fault: temporarily remove execution permission from only the owned bundled helper, restore in finally. Actual fullscreen UI showsPreview unavailable; playback advances13→14→16s with no pause except explicit testcontrols. Restoring mode makes nextcoldhover display48s keyframe. HelperSHA/mode unchangedaftertest. FullsystemVoiceOver speech and strict visible latency still not claimed. Hourlyreview19:18running; next20:18ifextended.

Hourlyloopreview19:18: aligned/close, featureworknotbottleneck. Preserve literalvisiblelatency and attributable-stall gates; proposed bounded standardon-screenpixelobserver pilot. Existing snapshotAPIpilot10 warmed callbacks12–15 ms onunchanging ownedVLCregion provesadequate rawcaptureoverhead, nothoverlatency. Proceedtest-onlyinput+ownedpopupcapturecalibration, then100settleddemands ifvalid. Do notinterpret documentinganunqualifiedgate as completingit. Nextreview20:18.

20261004-1941 — Visible measurement pilot advances beyond NSImage assignment. Final191250 native-fullscreen real-pointer capture observes old panel coordinates, then new actual display-space pixels at the new location. Cold main-window hover pilot independently inspected loading.png: pointer00:35 plus Loading… present at68.565 ms callback receipt measured from before cursor placement/event post. SCScreenshotManager captures owned popup only; imageROI8,9,320,180 excludes translucent footer. White glyph masks permit time/state comparison without pretending footer RGB is stable. Pilot scope only; not a percentile score. Test-only template preparation will occur in a prior media generation; ordinary off-track stop/reopen preserves actual miss conditions. No product feature change or gate relaxation. Previous question-only goal turn supplied no new completion evidence; current pilot supplies decision-changing evidence and supports next bounded collection.

20261004-1952 — Display-stall pilot001 stopped screen-space collection at its active-app guard; the launched VLC had not become active. Existing window-stream playback collection completed8s but supplies no display-space comparison. Preserve it as setup diagnostic. Existing production cohorts have many real helper descendants, so this is not evidence that extraction was absent; their active screen state was unrecorded. Playback runner now explicitly activates the owned app before observation and records verified focus, preserving hover as non-activating. A fresh eight-second pilot002 is running the same window stream plus five100-capture display-space batches at its mirrored burned-counterROI. No strict-stall conclusion yet.

20261004-2014 — Visible observer integration attempts001–004 remain failures, not percentile proof: first lost active-app state; second calibration deadlines left too few settled samples; third one-point geometry drift rejected all300 scored requests; fourth completed350 traces but22/300 snapshot API faults and three time-mask ambiguities prevent qualification. Controlledgeometry/earlypreflight now avoids drifting references. A40-request cold/RAM applicability pilot with live main runloop produced zero errors; old semaphore wait blocked the calling AppKit main thread, while the async screenshot API does not guarantee a background completion queue. This is a supported hypothesis, not fullyisolated causality. Read-onlycapture API now warms on preceding owned popup before inputt0; no pointer/decoder/cacherequest occurs duringinstrumentwarmup. Nearest-template comparison rejects oldtime/state glyphs even when both captions lie within a tolerance; thresholdswere notrelaxed. Attempt005 is running100miss/100RAM/50pressure/100disk against100 independently settled glyph/image references from a prior generation. Source/candidateunchanged.

Actual-display stall pilot002 captured525 snapshots with no errors alongside8seconds of native window stream; no>=100 ms windowrepeat occurred, so attribution remains unqualified. Firstpilotstoppedatactive-app guard. ContinuousSCKdisplaycrop support is now compiledtest-only from primarySDKsourceRect/displayfilter APIs, toavoidper-screenshot nondeterministicdelivery andmeasureactualcounterpixels at60fps. Cropmustlieinsideactiveownedwindow/onedisplay; noaudio/microphone/whole-desktopcapture inthismode. Exactoldobserverbinary/source retainedinwindow-capture-before-display-mode. Noqualifiedlongcohortyet.

20261004-2023 — Attempt005 failed qualification: 7/100 cold,21/100 RAM,87/100 disk faults; pressure50/50 completed. Warmup faults before pointer input disrupted the cache ordering, so later cache mismatches cannot establish a product regression. No passing-subset percentile accepted. Hourly20:18 review finds observer reliability is the immediate obstacle; one persistent-process40-demand applicability pilot is the next bounded experiment. If any API fault or semantic ambiguity remains, stop snapshot cohort repeats and qualify continuous display-crop capture. Four native surfaces including fullscreen fade/reveal remain demonstrated; VoiceOver speech, literal visible p95 and strict stall attribution stay open. Next review21:18 UTC.

20261004 — Persistent snapshot applicability pilot001 stopped after21 of40 demands. Twenty cold targets had zero API faults and independently matching image/time/ready pixels with actual miss traces. First RAM target0 followed bucket3: both legitimately use the same0s keyframe image/state, while pointer captions differ (00:00 vs00:01). The image-only observer stopped on its first matching image before the pointer caption updated: captured time is27 bits from target0 and0 from previous3. Actual trace was a memory hit. This is an observer stopping-condition defect, not a demonstrated stale-preview defect. No additional snapshot cohort retry: preserve raw records and move to continuous display-crop applicability as the20:18 review prescribed. Owned observer/app stopped; fixture hashes unchanged. Methodology validation and diff whitespace check pass.

20261004-2038 — Actual-display nine-second applicability capture tracks moving counter/pause/resume with continuous frame timestamps and no errors. Dual-process window/display capture then failed at shutdown: diagnostic002 preserves delegate SCStreamError -3805 application-connection interruption followed by -3808 already-stopped. Primary SDK offers a display filter including only the owned application. Single-stream owned-display/audio pilot001 passes8s:453 active frames, no>=100 ms repeat/timestamp/callback gaps, continuous interior generated audio, errors[]. This avoids separate observer lifetimes and captures only owned VLC audio/crop; no microphone/unrelated-app pixels. Three matched60s pairs are now running sequentially with identical settings, fixed geometry and recurring active-app/window checks. Firstbaseline is complete; no cohort verdict until allpairs are inspected.

20261004-2055 — Three matched actual-display+owned-audio60s pairs qualify playback for prior191250 candidate on declared standard MP4/main-window scope:0/0/0pp drop-rate increases, no interior audio interruption or timestamp/callback gaps. Only repeat0.25–0.267s at EOF in botharms; independent source duration60s plus eachapp stderr EOF/pausing and firstpostintervalpause prove terminalprovenance. Real helper sampled31/37/31 times in feature, zero baseline;80 realpointer moves/arm;56 focus/geometrychecks/arm; sourcehashunchanged. Strong read-only review supports bounded nofeatureattributablestall claim. Baseline moduleUUID8689B67E-4781-3602-9EBA-AF5882A9A13C independentlymatches Story 001 GUI startup sample122 andbuild signinglog2495; exactoriginalSHAwasnotinthatoldmanifest. Full broad-media guarantee is notclaimed. New Matroska fix candidate requires appropriate requalification.

Native time-origin checks001/002 revealed true positive-offsetMKV error, including wrong keyframe selection at11.125s. PinnedVLC/native seek6→source1.25 and16→source11.25 establish rawMatroska timeline. Helper noworigin0 for flatMatroska/WebM; preserves initial5s gap, rejectsnegative start, otherformats unchanged. Cachepolicy prefix revised. Expanded25 correctness/error cases and200standardrequests pass independentkeyflag/time/pixels, p95 MP4/MKV32.52/43.04 ms. Current signed205111 candidate builds; actualnativehover11s showsframe0+Keyframe0:05, ordinaryseek11 shows source6.208s. MP4editgap remains Keyframe0:02 atpointer0 andnativefirstimageat2s. Bothcontainers service26checks pass including100requests/cachetier; nofaults. VoiceOver/literalvisiblelatency and finalcandidateplayback remain open.


### 2026-10-04 21:07 UTC — actual-display latency method pilot

A single continuous sRGB display crop now matches an independently prepared
prior-generation image and pointer caption with no capture errors. The runner
reuses the established oldrc resume/confirmed-stop/reopen sequence; stop/add
while paused had silently reused the media cache. The corrected pilot proved a
new generation and a real miss (131.52 ms service assignment). This does not
qualify p95. The capture observer now rejects pre-input presentation timestamps
and incomplete frames when selecting measured completion. Full actual-display
cache-tier cohorts and VoiceOver remain open. The current 20:51 candidate is
being rerun through the working three-pair actual-display playback method.


### 2026-10-04 21:15 UTC — current candidate playback gate

The signed 20:51 candidate completed three new matched 60 s baseline/feature
pairs through the single owned-display plus VLC-audio capture method. Every run
retained 80 physical hover inputs, 56 active/geometry guards, zero lost frames,
no capture errors, no interior audio interruption or timestamp/callback gaps,
and unchanged source SHA. Dropped-frame-rate increase was 0 pp in each pair.
Counter-image repeats occurred only after 59.7 s at EOF in both arms; all six
app stderr logs show EOF/pausing at EOF. The observed counter/audio scope has no
feature-attributable stall above 100 ms. Report
playback-owned-display-origin-fixed.json preserves the candidate manifest and
all pair outcomes. No broader media/format/fullscreen playback or per-hover
visible-latency claim follows. Actual VoiceOver applicability is next.

### 2026-10-04 21:18 UTC — bounded observer checks

VoiceOver started through its first-run Quickstart UI, but its last-phrase
scripting and caption shortcut did not produce usable speech evidence. Reader
Quit and development-app cleanup restored the previously off state. The initial
wrapper's cleanup timeout is retained; no speech behavior is qualified.

The continuous actual-display runner prepared stable references for the three
pilot buckets, then failed before scoring because it required a repeated RC
pause-state event. Pinned oldrc's paused status branch prints a fresh “Type
'pause' to continue.” marker instead (oldrc.c:1194). Require that fresh marker,
terminal status response and a fresh statistics snapshot without seeking or
repairing pause state. The next three-demand method pilot tests this correction.
The 21:18 hourly review runs read-only alongside this bounded check.


### 2026-10-04 21:22 UTC — hourly review and observer phase correction

The 21:18 read-only loop review judged the goal aligned and progressing, with
closeout at risk from observer complexity. Keep the current product candidate
frozen; no further playback cohorts unless it changes. Bound visible-observer
applicability to a clean small trial before the declared MP4/MKV cohorts, and
stop full-cohort retries on another instrumentation failure. Obtain actual
VoiceOver evidence through a bounded caption/reader session; keep that gate open
if no speech evidence exists.

Pilot002 now scored three misses and one RAM demand, then stopped before
collecting any frames for the next RAM demand. The raw callback order proves a
readiness callback overwrote the newly reset measurement-finished flag. Separate
readiness state and serialize measurement arming before input; retain old source
and failed records. One three-demand confirmation follows, then freeze the
observer for full cohorts if clean. No product or threshold changes.


### 2026-10-04 21:29 UTC — first complete literal-visible cohort

After the phase-race repair, pilot003 passed all three misses and three RAM
demands with no capture/cache/caption/ownership errors. Froze the observer and
ran the full MP4 derivative cohort: 102 stable prior-generation references, 100
misses, 100 RAM hits, 50 pressure seeds, 100 disk hits, and unchanged app/media
source. Every scored demand had correct displayed image, pointer caption, actual
keyframe caption and cache provenance; no errors/timeouts or omitted samples.

Measured actual WindowServer p95 image+time was 190.57 ms miss, 125.89 ms RAM,
126.32 ms disk. Pointer caption p95 was 125.58/125.89/126.32 ms. Miss-image and
disk-image budgets pass, but the 100 ms RAM and pointer-caption budgets fail.
This is a complete measured failure, not an unqualified or passing subset.
Archive continuous-hover-mp4-results.json. Run MKV once with the same observer,
and investigate the input/presentation delay with a bounded read-only timing
review before changing product or instrumentation. No threshold change.


### 2026-10-04 21:51 UTC — second complete visible cohort and bounded reader session

The frozen continuous observer completed MKV with 102 prior-generation
references and all 350 demands (including pressure seeds) without correctness,
ownership, cache-provenance or capture errors. Scored image+time p95 is
217.06 ms miss, 142.63 ms RAM and 143.47 ms disk; pointer caption p95 is
167.06/142.63/143.47 ms. RAM and pointer-caption targets fail; miss/disk image
budgets pass. Both complete cohorts are retained; no threshold change or
successful-subset claim.

Read-only timing review identifies both event delivery and post-assignment
presentation delay. The observer also performs two WindowServer queries and
pixel/mask analysis per frame. Its contribution is unproven. Next experiment is
a bounded paired RAM diagnostic with buffered callbacks; no full-cohort retry
until an experiment changes the decision. The product remains frozen.

Actual VoiceOver captions announce Position/slider and spoken 5/10 percent
after accessible increments. The slider value changes but actual paused video
frame/time does not, so seeking is NOT qualified. Pinned main/fullscreen seek
handlers filter input event types and are unchanged by the feature; this points
to an inherited limitation, but a baseline reader reproduction is still needed.
Twenty physical hovers retain active app and slider focus. Caption pixel hashes
have two distinct values: “10%” and “10%, Position, slider”; this is sampled
caption evidence, not proof of no announcements. Four-surface reader behavior
remains open. The bounded session ended with the previously off reader stopped,
welcome-dialog preference restored to 1, AppleScript control left disabled,
Utility quit, and the owned development player stopped. Raw evidence is in
work/validation/story002/voiceover-caption-session-001.


### Upstream regression suite — 2026-10-04 21:53 UTC

Cam asked whether VLC's own suite had been run. No earlier run evidence was
found. Ran the configured VLC 3.0.24 make check, then top-level check-am after
recursion stopped at TLS: **51 pass, 1 skip, 1 fail, 0 errors**. test_url skips
a URL-host capability returning ENOSYS. test_modules_tls fails its trusted-
certificate handshake assertion at tls.c:182. The same unmodified test with
saved baseline core/libVLC and TLS plugins fails identically; dyld load logs
verify baseline loading, and all four libraries/plugins match feature SHA256
hashes. This is inherited from the local baseline. The exact TLS-backend/trust
cause remains open, and default make check remains red. No test was excluded
to claim a green run. Disabled checkall extras and macOS UI behavior are not
covered. The development app's macOS module hash is unchanged. See
docs/evidence/story-002/upstream-tests.json and per-directory archived logs.


### 2026-10-04 21:58 UTC — reader seek baseline reproduced

Actual VoiceOver on the saved pre-thumbnail baseline announces Position and
then 5%/10% after two native accessible increments. AX value changes to500/1000,
but the actual burned frame remains1/source0.042s and player time00:00 after
each. The baseline app was active. Baseline GUI module SHA matches its saved
manifest; this reproduces the current candidate's inherited accessible-slider
seek limitation. Do not claim VoiceOver seeking passes or expand Story 002 into
general VLC accessibility repair. Ordinary keyboard seek proof is separate.
Restored reader off, welcome-dialog preference1, AppleScript control disabled,
quit Utility and stopped only the owned baseline player. Evidence: voiceover-
baseline-comparison.json plus raw owned window/caption captures. Feature hover
announcement/focus preservation still needs stable real-reader proof.


### 2026-10-04 22:04 UTC — real-reader hover and observer pilot

Actual VoiceOver announces “0.2%, Position, slider” after using Apple's
documented VO-Shift-F5 pointer-to-reader command. Main-window20 and custom-
fullscreen10 physical hovers retain exactly one visible owned preview panel
moving through10/5 x positions, unchanged numeric slider values, unchanged
keyboard focus roles and active player. Each mode's before+hover caption pixel
hashes are identical (21/11 samples); no repeated announcement observed in
these samples. This is not continuous speech/audio capture. The original main
setup used an obsolete track Y after video start resized the window; retain it
as excluded setup and use freshly inspected AX geometry for scored proof.
Detached/native-fullscreen actual-reader proof remains open. Reader restored
off, welcome-dialog1, AppleScript control0, Utility quit, owned app stopped.
See voiceover-hover-partial.json.

The buffered same-ScreenCaptureKit observer uses32 prefaulted pixel slots and
metadata copies during callbacks, processes masks/hashes only after a fixed
500 ms capture, and checks owned active scene before/after. This is diagnostic
only because transient per-frame ownership is unobserved. The2-pair AB/BA
applicability run passes exact image/time/keyframe/cache/geometry/focus and
paused-state checks with no faults. Heavy/buffered visible responses are
126.58/35.17 ms and114.89/109.11 ms. These two mixed pairs prove applicability,
not a performance result. Proceed once to the planned20-pair diagnostic.
No product change, budget relaxation or qualification claim.


### 2026-10-04 22:07 UTC — observer hypothesis rejected; drawing experiment

The20-pair comparison completes cleanly but buffered collection is slower
overall: paired median heavy-minus-buffered-19.51 ms, only5/20 image pairs
improve by one60Hz interval. Both arms retain about70ms median post-assignment
delay. Preserve diagnostic report and stop observer tuning. A bounded product
experiment will request AppKit displayIfNeeded on the small dirty hover panel
after state/image updates, preserving assignment traces and recording draw
duration separately. Research points to normal event-loop deferred drawing,
not a proven root cause. Compare20 RAM pairs; revert without material gain.
All thresholds and decoder/cache policies retained. Original GUI source and205111 manifests/measurements are retained; the development app is rebuilt for the experiment. Prior playback/UI qualification applies to205111, not this drawing candidate.


### 2026-10-04 22:12 UTC — drawing gain; service scheduling experiment

The drawing-only experiment has no faults and reduces heavy observer median
110.02→67.52 ms/post-assignment71.77→37.31 ms, with tiny draw-call cost.
Heavy p95125.39 ms still misses100ms; buffered result is mixed. Keep the
change provisionally, with no qualification claim. Saved drawing-only app as
work/build/VLCDrawExperiment.app. Research classifies pointer-awaited cache
work as User Initiated QoS; next experiment changes only the service serial
queue priority. Expensive helper remains Utility. Re-run service contracts
and one20-pair diagnostic before broader latency/playback qualification.


### 2026-10-04 22:19 UTC — service contracts and desktop contention

Current221228 interactive-cache-QoS candidate passes26 service contracts per
MP4/MKV, including100 demands per miss/RAM/disk tier. Archived current inputs
and candidate manifest separately; these are service results, not native latency.
The planned20-pair diagnostic stopped during prior-generation template setup
when the target app became inactive. The unchanged app/source and failed attempt
are retained; no scored RAM pairs exist. Current foreground observation is Chrome.
Requested an idle desktop interval before another native run. No benchmark
threshold or scene guard is weakened. Hourly22:18 read-only review is running.


### 2026-10-04 22:20 UTC — hourly course check

Read-only hourly review finds aligned progress with closeout at risk from serial
performance tuning. Finish the QoS diagnostic when desktop exclusivity permits.
If heavy-observer p95 reaches100ms with correct results, freeze and run complete
MP4/MKV cohorts. Otherwise use existing timestamps for one bounded tail-stage
attribution and at most one further documented product experiment before another
strategic reassessment. Do not resume observer tuning, weaken thresholds or run
playback qualification on a candidate already known to fail the latency gate.
Remaining actual-reader surfaces and fresh playback belong to the selected final
candidate. This course fits existing authorization; no goal/scope change.


### 2026-10-04 22:24 UTC — unchanged-helper applicability audit

Verified current helper source/build-script and every linked static dependency
hash against the22:12 experiment manifest. The unsigned helper binary also
matches the helper used by the retained25-case/200-request origin-fixed proof.
That proof is applicable to the current unchanged helper. Standard MP4/MKV
sampled RSS peaks are21696/27728KiB; short-lived CPU sampling is incomplete and
zero samples do not mean zero CPU. Source retains512MiB RSS/footprint watchdog
at10ms,128 MiB individual AV allocations,320 MiB live frame buffers, one decoder
thread,5s wall deadline and5CPU-second RLIMIT. Brief watchdog overshoot remains
explicit. No decoder rerun is needed solely for GUI/service QoS changes. This
reuse does not qualify current native presentation or playback. Recorded in
helper-reuse-221228.json. Desktop-idle request remains unanswered; no UI runner
is live and no scored QoS pairs exist.


### 2026-10-04 22:25 UTC — blocked audit

The same desktop-exclusivity dependency persists for the third consecutive goal
turn. The prior turns completed service/provenance/review work; there is now no
independent required work that changes the next native-validation decision. No
owned runner/player is live according to current process inspection. The request
for an idle interval remains unanswered; elapsed time is not permission. Goal
status is blocked pending that reply, while Story 002 remains In Progress and
its full latency, final-candidate playback, four-surface UI/reader and closeout
requirements remain intact. No threshold, scope or completion criterion changes.


### 2026-10-04 23:56 UTC — resumed desktop interval and course review

Cam's go-ahead resumes the goal. Fresh input/GUI hashes match221228. QoS attempts
002/003 stop in template setup when VLC loses foreground; geometry guards remain
valid, current frontmost reads show ChatGPT, and zero scored pairs exist. Both
failed setups are archived. Ask whether this was user input or autonomous focus
switching; no further repeated cohorts until that cause is understood. Hourly
23:53 review preserves the QoS decision gate and recommends one timestamp-based
comparison/at most one evidence-led product experiment if latency fails. No
performance result, threshold dilution or playback transfer is claimed.


### 2026-10-04 18:06 MDT — focus diagnostic and QoS decision

Cam could not identify the cause of foreground loss. A bounded unscored42s
activation-monitor session retains owned VLC active in all samples, including
native thumbnail movements; the next activation is after owned-player cleanup.
This establishes local setup applicability, not the cause of earlier failures.
Guarded QoS attempt004 then completes all20 pairs with correct images/time/cache,
no faults and unchanged source/app. Heavy median126.06/p95183.73 ms and buffered
median90.64/p95177.06 ms do not show a useful gain or meet the100ms bar. These are
diagnostics, not percentile qualification. Retain the complete result and restore
service Utility QoS from the saved source; drawing remains provisional. Rebuild
started with manifest20261005T000626.431477Z. Tail attribution again shows most
latency after image assignment; one bounded primary-source presentation review
will choose the remaining experiment or profiling step before further rebuilds.
No observer tuning, threshold change or old playback qualification transfer.


### 2026-10-04 18:11 MDT — ordering applicability correction

Transition-only ordering's first setup detects an owned336x224 panel atCGlevel0,
not required3. Trace showsparentChangedtrue butlevelChangedfalse: the decision
was computed beforeaddChildWindow, which adopts the parent's level during
attachment. Preserve failed setup and move level comparison after attachment;
no threshold or observerguard changes. Corrected000958 build's2-pairpilot passes
firstreveal/reopen and all4 scored captures with correctimages/captions/focus.
This is applicabilityonly; diagnostic20paircomparison follows once. Newmode
transitionstacking stillneedsqualification ifretained.


### 2026-10-04 18:14 MDT — ordering comparison and profiling cutoff

Corrected transition-only ordering completes20 correct pairs with no faults.
Heavy median59.38/p95110.49 ms, buffered median110.07/p95193.11 ms; heavy improves
somewhat versus the earlier sequential drawing run but still misses100ms and
mixed observer arms do not establish a clear causal gain. Preserve allresults,
revert this experiment per bounded course and rebuild drawing-only/Utility
candidate001302. Source before experiment is restored exactly. No further
speculative ordering/layer tweaks. One unscored owned main-thread sample during
native hovers investigates blocking/presentation phases. The first profiling
wrapper failed before app launch because copied monitor executable permissions
were not preserved; retainedattempt001, fresh002 usescopy2. No product fault or
latency measurement follows from that setup failure.


### 2026-10-04 18:23 MDT — profiling outcome and remaining qualification

Ordinary20s main-thread sample is valid and mostlyeventwait, not a sustained
feature-drawing block. It does not reproduce the captured timing environment.
Captured-profile003 has correctownedPID and a correcttwo-pair method trial but
an emptycallgraphdespite sample exit0, so phase attribution remains unproven.
Earlier001/002 PID lookup selected the short-lived help process; retained all
failures and corrected ownership. Do not equate tool exit0 with evidence or
continue blind retries. The next profiling setup needs explicit target lifetime
and observed stacks before choosing another production change. Actualforeground
remainsstable in successfulsessions; earlierdesktopcontention is historical.
Story 002 remainsInProgress with all latency/currentplayback/remainingreader and
closeout gates intact. No extra user diagnosis or source mutation is required.


### 2026-10-04 19:09 MDT — acceptance block and locked desktop

Hourly 01:02 UTC review redirects work from serial performance experiments to
independent current-candidate acceptance. Freeze 001302 drawing-only/Utility
source; no profiler retries or speculative production changes in this block.
Fresh hashes match every manifest input and all five bundled outputs. Compared
with 205111, only the interaction-controller input differs, so unchanged
helper/service proof is reusable while native presentation/playback is not.
Created current-acceptance-ledger.md covering all seven ACs and precise gaps.
Mac remains locked at 19:07 MDT; no dependent UI runner is active and an unlock
request is pending. Complete reader surfaces, proportional four-surface controls
and three matched playback pairs once available, then determine the remaining
latency gap without silently changing targets. Story remains In Progress.


### 2026-10-04 19:14 MDT — current actual-reader four-surface proof

Cam unlocked the Mac. Started bounded owned caffeinate assertion; no persistent
sleep/security setting change. Current 001302 actual VoiceOver pointer-to-slider
navigation plus ten physical hover movements per main/detached/native/custom
surface preserve app activation, focus and slider state. One owned preview panel
appears in each sample; all eleven decoded caption frames per surface have the
same pixel hash. Initial detached pointer was covered by the reader caption
pane; retain excluded setup and move outside its known bounds before scoring.
This is sampled caption/focus proof, not continuous speech or reader-increment
seeking. Restore reader off, welcome-dialog1, AppleScript-control0, Utility quit.
Host passed=false is lifecycle-only, no behavior verdict; evidence summary
voiceover-current-four-surfaces.json owns guarded sample conclusions. Current
three matched actual-display/owned-audio playback pairs started in a fresh
directory, without reader enabled. No old playback qualification transfer.


### 2026-10-04 19:25 MDT — provisional drawing rejected; source restored

The drawing-only001302 playback cohort retains three complete matched pairs
with a replacement third pair: dropped-rate deltas-0.1413/+0.5650/+0.2120pp,
continuous audio and unchanged source, but three interior feature counter
repeats117–133 ms in pairs1/2. Third pair is clean. Original third-feature attempt
fails owned-app identity guard mid-run; no new crash report, RC still responds,
app cleanly exits during cleanup. Retain incomplete attempt; no weakened guard.
Stream callbacks remain regular through the pair1 repeat, with idle samples
between complete frames. This is a real observed unchanged display interval,
not proof of feature causality. Primary variance/frame-status research recorded.
Reject provisional drawing optimization conservatively because it neither
qualified100ms latency nor playback; do not label it a proven causal regression.
Restore original controller snapshot verified against205111 input hash, rebuild
012354 and verify every recorded production input equals205111. GUI artifact
hash differs after rebuild, so fresh playback remains required. Signed bundle
build passes. Begin three fresh paired playback runs with middle pair order
reversed to reduce fixed-order drift. No observer/threshold change. Current
candidate is original presentation/Utility, not001302. Rejected source/evidence
retained, reader evidence states its candidate identity explicitly.


### 2026-10-04 19:41 MDT — restored candidate acceptance inventory complete

Current012354 three fresh matched60s playback pairs complete with80 pointer
moves and55focus guards each, no capture/timestamp gaps, continuous owned-app
audio and intact source. Dropped-rate deltas0/-0.0708/-0.1416pp meet1pp limit.
Pairs1/2 have onlyEOF repeats; pair3 baseline has150/125 ms interior repeats and
feature108ms. No observed feature excess, but individual causes unresolved;
retain every interval and do not claim zero pauses or prove causal absence.
Actual reader detached/native now pass ten movements/eleven identical caption
frames each on restored rebuild; original main/custom proof applies to identical
original inputs. Reader/settings restored. Current physical click→53s,
CGdrag→29s, isolated wheel42→45s and keyboard45→55s while paused all work;
volume256→243. Above/below expanded target and both endpoints display one panel,
leave displays none, slider state unchanged. Exclude ineffective Sky drag and
combined wheel/keyboard snapshot; guarded native events and isolated snapshots
own conclusions. Whole-process time probes supplement short-lived CPU samples:
MP4/MKV user+system approximately0.01s each, RSS23.8/27.2MB, two representative
demands only. Bounded caps/broader resource evidence remain separate.

Current ledger records six capability criteria supported in declared scope.
Only frozen100ms RAM/initial-caption responsiveness targets remain unmet by
complete cohorts on identical restored source. Proposed MVP contract150ms RAM
and200ms initial time/loading (disk150ms, uncached image1s retained) is documented
for Cam's decision and has not been applied. Keep Story 002 InProgress; final
validation/closure awaits numeric disposition. No new percentile claim, no
silent requirement relaxation, no commit/push. Loop-review's acceptance-first
course is fulfilled; no speculative profiler or source tuning added.


### 2026-10-04 20:02 MDT — approved MVP contract and final review corrections

Cam explicitly approved changing the acceptance criteria to RAM150ms and
initial-caption200ms; disk150ms, uncached1s and playback/control limits stay
unchanged. The historical complete MP4/MKV reports and failed100ms outcomes
are retained byte-for-byte; a separate retrospective re-score passes all six
100-demand phases with zero faults. This is not a new measurement.

Final findings-first CLI review accepted four P2s: program-local VLC ordinals
cannot be used as file-global ordinals on multi-program sources; inactive
tracking could reopen the panel; first feature preflight required an absent
helper; and stationary-pointer resize could retain the old time. Current
015734 rebuild conservatively rejects multi-program ambiguity, guards active
presentation, uses a32MiB absent-helper estimate and refreshes active geometry.
Fresh helper25cases+200requests, service23contracts and generated single/multiple
program four-case regression pass. Preflight with temporarily absent owned
helper passes and restores it; built bundle signs/verifies. Final third CLI
review remains in progress. Current native regression attempt stopped at
activation on a locked desktop; preserve its unsuccessful attempt and request
unlock. No preview/resize/background pass inferred from that attempt.

Hourly loop-review confirms acceptance-first course and proportional unchanged
path reuse; no more speculative presentation/performance tuning. Stable-geometry
cohorts/playback and sampled reader evidence have explicit applicability,
not identical-current-input claims. Record focused changed-path native proof
before final validation/Done. No commit/push or bookmark implementation.


### 2026-10-04 20:05 MDT — track-order ambiguity fixed

The third review found a fifth P2: VLC adds Matroska tracks in TrackNumber-sorted
map order; public libavformat retains TrackEntry order without exposing that
identity. A reversed-entry fixture reproduces wrong ordinal images. Preserve
the ambiguity clause by returning unavailable for multiple Matroska/WebM video
streams, including convenient original ordering, rather than pretending it is a
verified identity. Single-video MP4/MKV successful sampling paths are unchanged.
Research/source evidence and bounded regression are checked in; current020311
build/signing and fresh helper25cases/200requests pass. Original and reversed
Matroska fixtures both reject bothordinals with no pixels; single-program TS
independent red/blue tracks remain tested separately. Historical selected-track
success claims are not transferred to this changed compatibility boundary.
Final native proof still awaits unlock; fourth CLIreview is running. This
implements the existing explicit-unavailable rule, with no guessed mapping,
new decoder/parser/dependency route or changed latency/playback requirement.


### 2026-10-04 20:09 MDT — fixture preservation boundary corrected

The fourth broad review found a sixth P2 in tooling: FFmpeg-y and Python writes
could follow an existing fixture/sidecar link outside the output directory.
Require a new output directory before any encoder invocation, use FFmpeg-n
and exclusive Python writes. Existing fixture bytes/provenance stay untouched;
no app/runtime source changes, rebuild or performance rerun required. Three
synthetic sentinel cases (symlink media, symlink sidecar, hardlink media) reject
before encoder launch and preserve source hashes. Final review targets only
this corrected tooling scope; earlier broad reviews and accepted findings
remain inspectable. UI remains pending desktop unlock, no native pass claimed.


### 2026-10-04 20:10 MDT — affected-scope review clean; native proof pending

Final targeted fixture-preservation review finds no concrete regression and
independently repeats all three sentinel tests. Six accepted P2s are fixed;
findings/evidence are retained, including the initial review's missed findings.
Methodology compile/validate and diff whitespace checks pass. Temporary owned
wake assertion is terminated, failed UI host has exited, reader settings were
untouched and generated sources remain intact. No native guard/resize/unavailable
pass is inferred while locked. Continue with the focused final native block
when unlocked, then validate/close against current020311; no more speculative
latency tuning or unsupported identical-current-source transfer.

### 2026-10-04 — unlocked desktop and final correspondence checks

Auto-lock is now disabled by the owner. Physical background/reactivation and stationary-pointer resize regressions passed on candidate 020311; AppKit-generated mouse events during resize are retained, and the cursor coordinates stayed fixed. The helper-private Matroska TrackNumber mapping restores the required AVC two-track case without mutating VLC playback dependencies. Five original/reversed/count-mismatch helper checks, the fresh 25-case/200-request decoder matrix, and 600 service requests passed. Candidate 022512 built and signed successfully. A further 25-check service run passed, including native-count forwarding and preventing incorrect-count cache reuse. The first fresh current MP4 native cohort stopped during template setup after confirmed foreground loss: zero scored attempts, no percentile claim. Exclusive idle desktop confirmation remains pending for complete MP4/MKV cohorts and selected-track UI proof. Story remains In Progress.

### 2026-10-05 — baseline-only ordinary response and final native correspondence

Cam confirmed baseline or baseline plus an explicit allowance as the response
policy. Root selects the measured baseline itself, with zero added ordinary-
control allowance; no positive percentage is inferred. The complete 022512 MP4
run preserved 350 demands with zero faults; historical-limit p95 values were
666.165 ms miss, 648.142 ms RAM and 722.136 ms disk. Those are historical
absolute failures, not demonstrated regressions. A matched ordinary-response
baseline comparison is still being prepared; the aggregate ablation recorded
below does not replace it. No performance code has changed.

Both original and reversed AVC Matroska files have actual native-menu selection
proof: Track 1 red and Track 2 blue, correct TrackNumbers and keyframe-zero
captions. The reversed fixture remained paused at zero after hover, and both
sources were preserved. The multi-program TS displays Preview unavailable,
remains paused at zero and preserves its source; direct installed-helper output
is `ambiguous_track_mapping`. The native service diagnostic instead says
`malformed-reply`, so exact diagnostic classification is unproven. See
[`native-selected-track-results.json`](../evidence/story-002/native-selected-track-results.json)
and
[`native-program-unavailable-results.json`](../evidence/story-002/native-program-unavailable-results.json).

A bounded generic display observer captures the same seek-bar knob/track crop
in unmodified and feature apps. The 8-per-arm pilot validated setup but is not
qualification; a 25-baseline/22-feature attempt ended invalid when the settled
knob failed its expected physical-point guard. Neither establishes p95 or
regression ([pilot](../evidence/story-002/ordinary-control-baseline-pilot.json),
[incomplete attempt](../evidence/story-002/ordinary-control-baseline-incomplete.json)).
Ordinary controls use the matched baseline with zero added allowance. Thumbnail
delay has no vanilla denominator and remains descriptive. The frozen 177 MiB
022512 app snapshot was preserved before any possible tuning.

### 2026-10-05 03:33 UTC — baseline policy and bounded measurement gate

Cam explicitly confirmed the target should be baseline, or baseline plus an
explicit percentage at worst. The active ordinary-control target chooses the
baseline itself with zero added allowance. There is no pending percentage
selection required for that option. New preview wait remains separately
reported because vanilla VLC has no preview denominator.

The shared light-style knob metric passes five bounded pixel exercises and
native pilot003: eight clicks per app, correct expected positions, no ownership
or pause faults, all recorded inputs unchanged. Root inspected the original
reference crops. It is a setup pilot, not percentile qualification. The first
full cohort stopped after25 baseline and22feature scored clicks when the next
feature click retained the old knob during900ms; posted input does not establish
application receipt. The complete raw failed attempt and fingerprints remain,
with no p95/regression verdict. Evidence: ordinary-control-baseline-pilot.json
and ordinary-control-baseline-incomplete.json.

Early loop-review at03:29 identifies observer/input reliability as the immediate
bottleneck. One bounded diagnostic is authorized within the existing story:
32clicks total across both apps and per-frame/pre-post AX observer modes, a
predeclared3second observation window for both, tagged exact-PID passive input
receipt, pre/post AX value and independent visible knob position. It is
measurement attribution only, not permission to relax the baseline target or
transfer reduced ownership guards into qualification. A further unexplained
input/ownership failure stops full-cohort retries pending its resolution.
Product source/build022512 remains frozen. Next hourly review due04:29UTC.

Current native selected-track original/reversed checks pass4/4 and unsupported
multi-program unavailable presentation passes1/1, with source/pause preserved;
internal error-label discrepancy is retained. Methodology compile, scaffold,
skill wiring and whitespace checks pass after the baseline-policy doc update.
Story 002 remains In Progress; no commit or push performed.

### 2026-10-05 — rejected panel-order experiment; 022512 restored

The signed 035125 experiment changed only the source controller's repeated-
panel-order guard; helper output stayed byte-identical and service, context,
geometry and helper inputs were unchanged. The valid 32-sample observer
diagnostic completed with zero faults. Per-frame medians were 250.17 ms baseline
and 382.47 ms feature, an added 132.30 ms versus the previous 132.71 ms; phase
medians were 242.4 and 362.89 ms. It showed no material relative gain and is
not p95 qualification ([rejected diagnostic](../evidence/story-002/window-ordering-rejected-diagnostic.json)).
Independent source review found no guard defect; the experiment was rejected
because it measured no material gain. Root removed the guard, restored the
exact 022512 app from its preserved snapshot, and verified the controller input
hash plus every prior manifest output hash. The 035125 app and manifest remain
historical artifacts; the guard is not retained. Current runtime is 022512.
The baseline-only ordinary-response comparison remains unqualified, the
thumbnail delay remains descriptive, and Story 002 remains In Progress.

### 2026-10-05 — phase-setup diagnostic did not score

The later phase-only AX setup attempt stopped before scoring any clicks because
its templates failed before the first `-click-` label. In the feature right
template, the passive exact-PID tap recorded the nonce-tagged move/down/up
sequence and AXSlider changed from 5585.997 to 6651.446, but 14 complete frames
through the 900 ms observation bound all showed the knob at 950 pt. Baseline
left/right templates showed the knob at 950 / 1090 pt. This records an accessibility
value change without a corresponding visible knob update in the observed
feature frames; it does not establish ignored input, a blocked app, or a latency
regression. All fingerprints remained unchanged, both owned apps exited 0, and
no profiler started because setup failed before the first scored-click label.
The archived [phase-setup report](../evidence/story-002/ordinary-control-phase-setup-failure.json)
retains the raw result. Instrumented landmarks are listed in the
[response-contention note](../research/native-response-contention.md); they are
not a qualified timing sample. No rerun is requested. The ordinary response
target remains the matched unmodified-VLC baseline with zero added allowance,
thumbnail delay remains descriptive, and Story 002 stays In Progress.

### 2026-10-05 04:22 UTC — independent capture and aggregate ablation queued

The bounded independent screenshot attempt did not reproduce the earlier
missing draw: feature right reached knob position1090 after418.4809 ms, and the
fresh crop visibly showed1090, agreeing with the original stream. Wrapper
finalization failed because it called `cleanup` instead of `close`; root
verified the exact owned PID and argv, quit that app, and confirmed its socket
and process were gone. Screenshot timing metadata was lost, so this cannot prove
that the screenshot and stream were temporally aligned or establish capture
freshness. Preserve the unqualified
[report](../evidence/story-002/ordinary-control-independent-capture-diagnostic.json);
do not rerun it.

The 04:22 hourly review finds the investigation aligned but at a measurement
local minimum. One eight-per-arm aggregate preview-work ablation is being
prepared, with preview enabled and environment-gated bypass on the same
diagnostic app, geometry, fixture and observer. The baseline arm remains
unchanged. Bypass preserves tracking while skipping metadata/context work, panel
presentation and decoder demand together; this cannot isolate those components
from one another. The temporary [042439 app manifest](../evidence/story-002/app-build-preview-ablation-042439.json)
is diagnostic-only, leaves the helper unchanged, and does not qualify p95 or
represent a shipping change.
Source was restored to f6d8889, prior 022512 outputs were verified exact, and
at this historical point the runtime remained 022512; later reversible builds
are recorded in the current closeout section. At this review point the
experiment was still being prepared; its later result is recorded below. No observer refinement or
new full cohort was queued. Story 002 remains In Progress.

### 2026-10-05 — aggregate preview-work ablation completed

The [diagnostic report](../evidence/story-002/ordinary-control-preview-ablation-diagnostic.json)
records eight scored responses per arm on the same 042439 diagnostic app,
geometry, fixture and observer; only the environment flag differed. All 16
responses passed per-frame ownership, nonce-routed-input, held-slider AX and
visible-pixel checks, with no faults or censored attempts. Median response was
370.86554 ms with preview enabled (range 241.51–541.56 ms) and 253.77404 ms
with preview work bypassed (range 149.65–315.96 ms), a 117.0915 ms median
difference. Fresh RC snapshots after all captures remained paused at media time
50 or 59 seconds. App, observer, media and fixture fingerprints were unchanged;
both arms exited cleanly.

This supports aggregate preview-work contribution under this observer
condition. The bypass groups metadata/context work, panel presentation and
decoder demand, so it does not identify an individual cause. It is not p95
qualification or baseline-relative acceptance. The baseline-only target remains
zero added allowance; helper and shipping source are unchanged. Root restored
the exact 022512 runtime and verified every prior manifest output hash. The next
step at that time was root's read-only component-level causal decision; no fix
was selected. Later profiler findings and the bounded coalescing experiment outcome follow
below. Story 002 remains In Progress.

### 2026-10-05 — profiler options failure and full-schema preflight

The first actual-VLC Time Profiler attempt failed before recording: xctrace
returned57 because the partial options JSON lacked required data, then the
recording-start notifier timed out after15seconds. Root cleaned up the owned VLC
with exit0; source and app fingerprints were unchanged. This is not a profiler
unavailability result and provides no stacks or profiling-latency evidence. The
[failure record](../evidence/story-002/ordinary-control-profiler-options-setup-failure.json)
preserves it.

Read-only `--show-recording-options` calls exposed available options but did not
validate JSON payloads. Apple’s Xcode27 release notes describe emitting and
passing recording options as JSON. A newly generated full seven-key schema,
with Time Profiler waiting-thread capture enabled, was then accepted by a
100 ms recording attached to newly owned idle Python PID37429: xctrace returned0
and reported a saved trace; the child was terminated with status-15. The
[configuration](../evidence/story-002/profiler-full-recording-options.json),
[preflight result](../evidence/story-002/profiler-full-options-preflight.json)
and [tool stdout](../evidence/story-002/profiler-full-options-preflight.stdout)
are archived. This validates option-loader acceptance only, not actual VLC
profiling or useful stacks.

Apple’s [WWDC23 Instruments hang analysis](https://developer.apple.com/videos/play/wwdc2023/10248/)
uses inspected thread stacks to distinguish busy main-thread work from a
blocked thread. At this preflight point, one exact-PID VLC transition attempt
was pending to test for expected stack rows; the later results follow below.
Current production remains exact restored 022512, ordinary-response allowance
remains zero, and Story 002 stays In Progress.

### 2026-10-05 — profiler stacks and notification-coalescing experiment

An exact-PID Time Profiler recording produced interpretable stacks. The safe
[summary](../evidence/story-002/ordinary-control-profiler-main-stack-applicability.json)
records 1,394 exported rows, 214 main-thread rows and 213 nonempty main-thread
backtraces. One instrumented input-to-visible response took 350.357 ms. The
preview path crossed `mouseMoved` / `updatePreview`, a text-field update and
display-cycle/Core Animation commit work before an unfair-lock wait (163.286 ms
of sample weight). A separate accessibility-window-ordering path included
SkyLight transaction waiting (122.949 ms of sample weight). These are sampled
interval weights, not CPU duration or proof of continuous blocking; the single
response does not estimate latency.

A minimal-environment [clean profiler pair](../evidence/story-002/ordinary-control-clean-profiler-pair.json)
recorded one enabled response at 433.88 ms and one bypassed response at
73.69 ms. Its enabled stack includes `NSWindow _setFrameCommon` fence/backing-
store waiting beneath `updatePreview` called by `mouseMoved`. This is an
attribution lead, not a treatment effect, p95, or baseline acceptance result.
Raw trace TOCs remain private and are excluded from shared evidence.

The bounded source hypothesis is to coalesce repeated preview-window position
updates by notification name and sender, posted with `NSPostASAP`. Current
[NSNotificationQueue documentation](https://developer.apple.com/documentation/foundation/notificationqueue)
documents deferred posting and duplicate coalescing; [NSPostASAP](https://developer.apple.com/documentation/foundation/notificationqueue/postingstyle/asap)
posts at the end of the current callout or timer. Apple's archived (retired)
[Cocoa Fundamentals guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CocoaFundamentals/CommunicatingWithObjects/CommunicateWithObjects.html)
describes coalescing expensive display-server work. `NSPostWhenIdle` requires
run-loop idleness and could be deferred under sustained input (inference from
that condition), so the historical experiment used `NSPostASAP`. Its incomplete outcome is
recorded below; no improvement is retained, and no `setFrameOrigin` speedup is
demonstrated. Current production remains exact restored 022512, zero added
ordinary-response allowance remains the target, and Story 002 remains In
Progress.


### 2026-10-05 06:03 UTC — coalescing retry stopped; MKV setup failure

The 050009 NSPostASAP coalescing candidate is historical and was not retained.
The [first diagnostic](../evidence/story-002/ordinary-control-coalescing-setup-failure.json)
contained five valid samples and the [repeat](../evidence/story-002/ordinary-control-coalescing-repeat-setup-failure.json)
contained twenty; both ended with foreground ownership false and neither is a
completed response comparison. In the repeat feature phase at click000, the old
crop remained visible while passive exact-PID move/down/up was observed. At
+877 ms the collapsed app-active guard (owned-process existence, expected bundle
ID and active state) read false, then owned-process and held AX passed about
60 ms later. The cause of the guard result is unknown. This does not establish
a coalescing effect, ignored input, a foreign foreground app, a product defect,
or a latency result. Source review found no
defect; NSPostASAP does not guarantee click priority. Following the loop review,
root stopped retries on this path. The candidate manifest/source and both
incomplete reports remain archived.

Root restored the original controller and verified every previous 022512
manifest output hash. No notification queue change is retained and production
remains exact 022512. Ordinary-response acceptance still targets the matched
unmodified-VLC baseline with zero added allowance; preview delay remains
descriptive.

The stable 022512 `continuous-hover-tracknumber-mkv-001` descriptive cohort
stopped at template bucket85 after six valid templates and zero scored
requests. Its [setup report](../evidence/story-002/current-mkv-cohort-foreground-setup-failure.json)
classifies the capture target as inactive or the crop as owned by another main
window; source, app and inputs were unchanged. This is the third foreground
setup failure overall. Unlike the two preceding coalescing-run failures, this
one occurred on the stable original single-app path; its cause remains unknown. No MKV response or timing
result is available. Root paused further UI metrics pending user guidance on
an idle-desktop window or alternate checks. Story 002 remains In Progress.

### 2026-10-05 — stable-strip geometry prototype, no UI qualification

While response metrics remain paused, root built two
isolated signed prototypes: [061652](../evidence/story-002/app-build-stable-strip-prototype-061652.json)
and [061929](../evidence/story-002/app-build-stable-strip-prototype-061929.json).
Review found that the first host union, based on the knob-center inset, could
clip the gutter at the full hover-range endpoints. The corrected prototype uses
the full `VLCTimelineHoverBounds` xmin/xmax union. This was a source geometry
review, not a reproduced UI failure. The card is 336×224 inside a transparent
wide panel; a managed canvas draws background and local shadow, the card view
moves within the panel, and host-window frame updates are limited to geometry
changes. Ignored prototype sources remain in `work/validation/story002/`.

The [read-only foreground recorder preflight](../evidence/story-002/foreground-recorder-readonly-preflight.json)
ran three seconds, returned0 with two ready/final rows, and confirms startup/run-
loop applicability only. It made no activation calls and does not prove
notification delivery or captured transition behavior. After each build, root
restored canonical 022512 source/runtime and verified all bundle hashes. The
prototype produced no product change, UI proof or performance result. Before
considering retention, prove both endpoints, all four surfaces, clearing/hide,
stacking and resource use, then compare ordinary-control response against the
matched baseline. Adapt observer ownership/crop/geometry only if the prototype
first demonstrates value. Metrics remain paused; Story 002 stays In Progress.

### 2026-10-05 — bounded visual and guard applicability follow-up

On the restored original 022512 single-app path, six valid interactions passed
with stable ownership and target activation-notification delivery
([record](../evidence/story-002/ordinary-control-foreground-applicability.json)).
This validates notification applicability for that run only and does not
explain earlier setup failures.

The first prototype endpoint test moved to x=1537, one pixel beyond the actual
last accepted slider pixel x=1536. Slider AppKit bounds were x=208/width1328;
the first included pixel was x=209/local0, while AX's 1330 width included
alignment padding ([coordinate diagnostic](../evidence/story-002/stable-strip-main-coordinate-diagnostic.json)).
Treat that attempt as invalid test geometry, not a feature defect. The corrected
visual run then passed six physical pointer moves across left/middle/right
x=1536/return/leave/re-enter. Host identity and bounds stayed stable, hide and
reveal worked, media remained paused at zero, and source remained unchanged
([visual result](../evidence/story-002/stable-strip-main-visual-results.json)).
Root reviewed PNGs for the middle and right captions and clearing. Captures were
of the owned parent+child window group rather than an isolated panel, and this
prototype evidence does not establish all-surface behavior or performance.

The matched ordinary-control attempt stopped during baseline template-right
with zero scored samples ([setup failure](../evidence/story-002/stable-strip-control-comparison-setup-failure.json)).
The collapsed guard read false at 941770.821 despite crop containment and
post-owned checks being true; a separate activation receipt occurred at
941760.464, with no event observed before cleanup at 941771.310. This absence
does not prove there was no transition and does not waive the ownership guard.
It is a setup failure, not a response timing sample.

A six-interaction baseline-only guard-component diagnostic passed without
reproducing the transient guard result; its first wrapper had a post-analysis
`KeyError`, and its query-end timestamp precedes getter completion. A separate
10 ms cadence observer captured 5,996 samples (median 10.03 ms, maximum 19.84 ms)
without reproducing the guard failure
([record](../evidence/story-002/ordinary-control-guard-components-applicability.json)).
These checks do not qualify latency or identify the original cause. Root's next
bounded step is a new-instance registration/setup pilot using lifecycle
notification observation. No further repeated comparison should begin before
that pilot reports. The optional idle-desktop question remains unanswered, but
is not a blocker to existing authorized guarded diagnostics. UI performance
metrics remain paused, original 022512 is restored, and Story 002 remains In
Progress.

### 2026-10-05 07:03 UTC — NSWorkspace launch route abandoned

The bounded [launch setup attempt](../evidence/story-002/workspace-launch-pilot-setup-failure.json)
used the expected `VLCBaseline.app` URL, returned PID67263 with the expected
bundle ID, and preserved exact process argv. It failed before capturing any
interaction: RC reported `stop`, zero media time and empty counters, so a stable
paused time-zero input was not established. The cleanup adapter reported an
argv/config/socket ownership mismatch. A separate `ps` check at 07:01 found the
PID absent, but no exact process exit status was available; neither observation
establishes the launch-path cause or clean-exit status.

Root's read-only source diagnosis found `work/upstream/vlc-3.0.24/modules/gui/macosx/darwinvlc.m` lines 230–286 forwards
remaining arguments and plays, while `work/upstream/vlc-3.0.24/modules/gui/macosx/VLCMain.m` lines 472–497 filters duplicate
command-line media in `openFiles:`. Environment and working-directory
differences remain unproved. At the 07:03 stop review, no concrete defect was
established. Per the bounded rule (no more than 15 minutes for concrete diagnosis
and one fix only if a defect is demonstrated), abandon the NSWorkspace route;
do not rerun or claim a cause.

Original 022512 is restored. At the time of this entry, the other three
stable-strip surfaces remained pending. UI performance qualification remains
paused and Story 002 remains In Progress.

### 2026-10-05 — detached and fullscreen stable-strip visual applicability

The detached 061929 prototype completed six observations with stable host,
leave/hide and source integrity; playback remained paused at zero. Root reviewed
the right endpoint image and confirmed 01:30 / Keyframe 1:28. Custom fullscreen
001 and 002 both failed before the first endpoint observation because no host
was found; the actual AX fullscreen timeline rectangle was
x=641,y=918,w=445,h=17. Cause remains unknown. The [compact evidence record](../evidence/story-002/stable-strip-four-surface-visual-applicability.json)
preserves both initial failures.

Diagnostic003 seeded custom and native fullscreen at middle, then exercised
left/middle/right/return/leave/re-enter. All observations passed visible
presentation, stable-host, hide and integrity checks, with paused media time
zero. The custom host was 795×240 at (466,690), and the native host was 795×240
at (466,697). Root reviewed custom right (01:30 / keyframe 1:28) and native
return-middle (00:45 / keyframe 0:44) images and clearing. Captures include the
owned parent+child window group, not an isolated panel. An alpha=0 visibility
observation occurred during initial fullscreen reveal before the seeded run;
it does not explain the earlier no-host failures.

Together with the main-window and detached results, the 061929 prototype now
has four-surface visual-applicability evidence only. First-entry fullscreen
reliability, resize, playing-media behavior, playback/control, accessibility,
resources and performance remain unqualified. Canonical original 022512 remains
current; no prototype change or acceptance closure is claimed. The other-surface
visual checks do not resume paused performance qualification. Story 002 remains
In Progress.

### 2026-10-05 — runloop-observer setup failure

The revised observer main-loop pump and 1 ms no-op timer passed its 5-case pixel
self-test, but the run stopped at the first baseline template before the
negative attempt; it scored zero samples
([diagnostic](../evidence/story-002/ordinary-control-runloop-observer-setup-failure.json)).
At t0+0.302s the observer recorded `display_frame` index17/status1 while the
collapsed target-app guard read false, crop and AX ownership were true, and
tagged routing plus after-owned checks passed. An independent notification
collector saw target activation but no transition before cleanup; absence is
not causal proof. Review also identified unexercised harness limitations:
`frame` versus `display_frame` kind handling and a missing independent negative
interval. The negative path is not validated.

All input hashes and canonical 022512 remained unchanged. This establishes no
cause, fix or latency gain. Root's baseline-left-only split-component plus
frontmost-snapshot classification run 002 is still running; its outcome is
pending at that point. This result does not justify a performance repeat or
primary guard change. Story 002 remains In Progress.

### 2026-10-05 — frontmost-v2 contract and fresh reversible candidate

The baseline-only prospective frontmost-v2 observer passed four positive
controls with 696 callbacks, zero failures and zero legacy disagreements, plus
a five-case pixel self-test. A deliberate Finder interval produced two frames
with PID759 / `com.apple.finder`, target activation/deactivation notifications
and successful foreground actions; the negative probe exited1 as expected
([summary](../evidence/story-002/control-frontmost-v2-001-contract-applicability.json)).
This validates the new observer policy under its controls only. Frozen v1 probe
and trial files remain preserved, no previous guard failure is waived or
explained, and the primary guard was not changed. Classification run002 passed
without reproducing the earlier discrepancy; root stopped further
classification runs.

The earlier reversible development app [072539](../evidence/story-002/app-build-stable-strip-candidate-072539.json)
was built from stable-strip source hash
`4c8170c228906dfc5ec24d05e9c5c806534d10fa35a6a76f49c7a933cc4506c5`. Original
signed 022512 and controller source hash
`f6d88892c4731659340a2d96ede7a61b02f40ed2c9ddf8424ae2853c089bc4cc` remain
preserved; helper outputs match across the two manifests. The candidate is not
final. The fresh formal matched comparison stopped during baseline click010
after ten baseline observations and zero feature observations: three capture
callbacks were idle, with no complete presentation frame available to score.
Input routing and ownership checks passed. The cohort is invalid, with no
partial salvage, candidate-failure attribution or latency claim; see the
[incomplete-cohort record](../evidence/story-002/ordinary-control-frontmost-strip-001-incomplete.json).
Apple's ScreenCaptureKit guidance filters for complete frames ([status](https://developer.apple.com/documentation/screencapturekit/scframestatus/complete),
[capture flow](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos)).
Observer v3 has prospective strong review acceptance and is implemented: AX
checks run only for `SCFrameStatusComplete`; ownership/window/crop guards remain
on every callback, idle AX is null/unmeasured, and phases remain separate and
unqualified. The five-case pixel self-test and Python compile pass. Its first
qualification attempt stopped before capture geometry after the independent
collector observed Codex foreground transitions during setup. Cam later
confirmed mouse/keyboard use during those transitions, then finished; this
does not explain earlier unexplained false-guard observations. The
[setup-failure record](../evidence/story-002/ordinary-control-complete-frame-v3-setup-failure.json)
preserves this as no UI qualification and no candidate/performance evidence.
The v2 headless replay was rejected for version mismatch. Root's 13:09 review
records a 07:03→13:09 gap without an hourly-compliance claim. A clean v3 control
run passed four positive controls with zero faults and independently
corroborated the known Finder negative, which the probe rejected as expected
([controls](../evidence/story-002/ordinary-control-complete-frame-v3-controls.json)).
This is observer/control applicability only, not feature UI or performance
qualification. The first eight-per-arm method pilot on 072539 ended invalid at
four baseline / five feature observations when the requested feature knob at
x=1090 remained visually at x=950; input routing, ownership and AX value change
passed, but the pixel response was missing. No partial metric is salvaged
([record](../evidence/story-002/ordinary-control-complete-strip-pilot-setup-failure.json)).
Root then built experimental [132643](../evidence/story-002/app-build-controller-16 ms-experiment-132643.json),
controller source SHA-256
`47b31fa472d778e0c48b304b6c07cf6e7f7a7a62cade31f42943093f4d093690`. Only the
controller input differs from 072539; helper/service/archive inputs match. A
separate eight-per-arm method pilot passed without faults or input changes;
descriptive ranges were 245.5–367.4 ms baseline and 241.8–385.2 ms feature,
not p95/effect qualification ([summary](../evidence/story-002/ordinary-control-16 ms-method-pilot.json)).
The fresh formal 100-per-arm v3/900 ms/zero-allowance comparison ended invalid
at 61 valid baseline and 75 valid feature observations. Baseline action 62
failed on one idle callback where the per-PID app object was absent while the
independent foreground query still showed the expected VLC PID/bundle and the
parent crop remained contained; no pixels were available. Cause is unknown and
this does not establish product regression. No partial comparison, p95 or effect
is salvaged ([record](../evidence/story-002/ordinary-control-16 ms-formal-setup-failure.json)).
The 132643 candidate-specific [surface summary](../evidence/story-002/cadence-16 ms-surface-applicability.json)
records bounded main-window, detached and native physical-hover/clear
applicability; main/native right caption was 01:30 / Keyframe 1:28, detached
resize caption was 01:20, and the detached host ID did not survive resize.
The initial custom first-entry attempt had zero hosts at five positions, with a
host on reentry; that attempt is preserved as an incomplete historical result.
The later `cadence-16 ms-custom-ready-001` alpha-ready run now passes its bounded
custom-surface applicability scope, without resolving general first-entry
reliability ([current applicability](../evidence/story-002/cadence-16 ms-current-applicability.json)).
Both 072539 and 132643 remain reversible and unqualified. Focused controls and
reader checks now exist for 132643, but ordinary-control latency and playback
stall attribution remain open.

Detached resize004 did not find a host under the stationary pointer because
aspect correction yielded actual height743 rather than850 and moved the bar
from y1028 to y921. The pointer stayed outside the new bar, so the preview hid
as expected; this is setup geometry, not defect evidence. Four-surface visual
applicability remains separate from fullscreen first-entry reliability, resize,
playing behavior, accessibility and performance acceptance. Story 002 remains
In Progress with required gates open.

### 2026-10-05 — focused reader, controls, and MP4→MKV applicability

On experimental 132643, the prepared custom-fullscreen entry check passed after
sampling owned-window alpha before the first hover. Main, detached, native-fullscreen,
and custom-fullscreen results now provide bounded surface applicability; the
earlier custom no-host attempt remains preserved with cause unknown. Detached
resize changed host bounds, so its host ID did not survive that transition.
Focused main-window reader samples retained AXSlider focus/value across 12
caption-clear/hover records, and the selected click, drag, wheel, keyboard-seek,
and volume checks passed. This is not a four-surface reader/accessibility pass
([summary](../evidence/story-002/cadence-16 ms-current-applicability.json)).

A separate MP4-to-MKV transition check verified that rapid leave hid the MP4
preview, no old-generation preview appeared before the new file, the generation
advanced from 3 to 9, and two MKV previews matched requested times near 45.0185
and 81.469515 seconds to actual keyframes at 44 and 80 seconds. The parent host
ID remained 23201; its bounds changed on media switch, which accounts for the
raw strict `stable_host: false` summary flag. Although 32 rapid moves were
posted, only 30 events were observed and their minimum interval was 43.953 ms;
this did not test pending-timer cancellation below 16 ms. A raw diagnostics
metadata mismatch is retained in the [scoped record](../evidence/story-002/cadence-16 ms-cancel-mkv-applicability.json).
This establishes neither a full MKV response cohort nor a latency percentile.

A follow-up same-process burst addressed the missing sub-16 ms case without
changing the app, controller or observer. AppKit coalesced 33 posted moves
(32 timeline moves plus leave) into seven delivered timeline mouse-move events;
six intervals were below 16 ms. Hide followed the last delivered timeline
event by 9.134 ms, within the pending interval. No later preview appeared before the MKV switch, pause and
integrity remained intact, and the new generation displayed the two MKV frames
([record](../evidence/story-002/cadence-16 ms-single-process-burst-applicability.json)).
This is native pending-hide/cancellation applicability only, not a latency
percentile or full MKV response cohort.

The ordinary-control matched-baseline result remains unqualified, and the
current repeated-ROI evidence does not attribute every stall. CPU/RSS resource
costs are reported as matched deltas against the declared worker/cache bounds,
not as a zero-delta rule; the separate playback-integrity gates remain open.
Story 002 remains In Progress.


20261005-0842 — approved shared-load course correction and resumed objective:
Cam approved a practical explicit regression allowance, variability-aware
measurement and retention of functional proof after explaining continuous
competing AI workloads. Root prospectively selects20% ordinary-control p95
allowance, separate baseline-block variability and no noise-expanded margin.
The [authoritative plan](../research/story-002-shared-load-completion-plan.md)
records the goal-API limitation and resumed execution. The prior blocked tracker
cannot be restarted/rewritten through its exposed API; work continues under
Cam's instruction without falsely completing or replacing it. One existing-v4
comparison is permitted, with no observer redesign or retry; precision results
may remain inconclusive and explicitly deferred for MVP closure. Historical
zero-allowance and absolute results remain unchanged. Current candidate132643
is frozen; no new runtime implementation or public distribution is proposed.
Strong read-only acceptance audit found no demonstrated functional defect;
unchanged helper/service/context/geometry inputs support scoped test inheritance.
Unchanged panel focus/AX/mouse transparency plus preserved four-surface reader
observations, fresh main reader and all four current physical surfaces support
accessible-controls MVP without claiming a fresh four-surface reader rerun.
Fully visible custom controls passed first-entry scope; the earlier no-host
observation remains unknown, not erased. Native MKV images/generation/cancel
proof support functional scope; broad MKV percentile timing remains deferred.


20261005-0850 — goal restarted by explicit user instruction:
Cam deleted the obsolete blocked goal and requested a fresh goal for the updated
priorities. get_goal returned null; create_goal succeeded with active status with the
functionalStory 002MVP objective, prospective 20% baseline allowance, explicit
unqualified-performance deferral, no measurement redesign/retry and hourly
loop-review. No token budget was requested or set. The tracker now matches
the authoritative working plan; its earlier API limitation is historical.


20261005-0855 — final findings-first functional MVP validation:
The [strong acceptance review](../evidence/story-002/shared-load-acceptance-review.md)
finds seven revised functionalACs supported and no demonstrated product defect.
The [validation report](../evidence/story-002/mvp-shared-load-validation.md)
records gradeB functionalcompletion, precisionperformance unqualified, inherited
helper/service/reader scope and current native/playback proof. Root freshly
ran patch-application check, build preflight and strict deep signing verification.
The [delivery manifest](../evidence/story-002/mvp-delivery-manifest.json) verifies
every original source/input and canonical app output hash unchanged from132643;
no new runtime code or executable was produced. Historical failed/invalid
measurements remain unchanged; precise performance is not a passing score.
Only the current production helper/native path ships; AVFoundation/prototype
extractors remain ignored historical evidence, not duplicate product paths.
Final methodology regeneration/validation and mark-story-done follow.


20261005-0858 — mark-story-done: functional MVP closed under approved scope:
All seven revised acceptance criteria, implementation tasks and source/privacy/
evidence tenets are supported by [validation](../evidence/story-002/mvp-shared-load-validation.md)
and the strong [acceptance review](../evidence/story-002/shared-load-acceptance-review.md).
Methodology compilation/validation, patch/build checks, bundle signing and
whitespace checks pass. Current development delivery is unchanged132643, with
all manifest inputs/app outputs freshly verified. No new runtime code was
needed. Historical upstream suite retains51pass,1skip,1baselineTLSfailure;
it is not reported as green or GUI proof.
Precise latency/causal-stall qualification and broad MKV response distributions
remain explicitly unqualified/deferred in registry/inbox; neither failed
measurement nor high host load becomes a performance pass or cause claim.
Bookmarks/integrated root/public packaging remain separate. Learning-review
was considered: record the user correction and bounded course in research; no
live workflow/skill learning is promoted. Landing state: local uncommitted
MVP ready; finish-and-push is the next request if Cam wants to land it.


20261005-0905 — closure corrected after user clarification:
Cam clarified that baseline/post-code performance testing is still required,
but can be pragmatic and less specific. Root's prior optional-comparison
interpretation was too broad. Reopened Story002 and withdrew its closure;
functional proof and paired playback results remain applicable, not discarded.
Created a fresh active corrected goal (get_goal returnednull) requiring an
actual bounded before/after comparison. The corrected plan reuses frozen-v4
phase mode,20samples/arm, median/ranges/temporal variability and prospective20%
median allowance; there is no new observer framework or p95 claim. Historical
closeout entries remain preserved as superseded decisions.

20261005-0923 — Corrected required baseline/post comparison completed on
unchanged baseline and signedfeature132643:20 actual responses each; medians
343.047msbaseline/330.741msfeature, ranges279.568–487.320/233.484–420.992ms.
Four blocks orderedAB BA BA AB; featuremedian−3.587%, within prospectively
selected20% allowance. Blockvariability/rawsamples retained; no p95 or causal
speedup claim. Root audited all52 rawphase/acquisition sessions, zero faults,
frozenbefore/afterinputs and bothownedcleanexit0. Earlierthree-sample pragmatic
readinessfailure remainsinvalid. Narrowobserver acquisition correction passed
fourpositive/foregrounddeparture/ownedtermination controls, with qualifiedhashes.
See [current validation](../evidence/story-002/pragmatic-before-after-validation.md)
and [raw numeric summary](../evidence/story-002/ordinary-control-pragmatic-before-after.json).
Fresh patch/buildpreflight and strictdeepcodesign pass; productinputs unchanged.
Existing3matchedplaybackpairs, helper/service/native/reader evidence remain
applicable. Storycompletion awaits independentresultaudit and statusreconciliation.

20261005-0924 — Independent findings-first audit found no material defect in
collection: all52 session contracts and40 earliest matching display-time
latencies independently recomputed; AB BA BA AB order, counts, clean exits
and before/after/live fingerprints match. Product inputs/outputs match unchanged
132643. Actual approximate before/after comparison is valid within the20%median
allowance; observed−3.587% is not causal speedup or precisionp95 proof.
Mark-story-done: all7 acceptance criteria, tasks, tenets and workflow gates
complete under declared MVP scope. Earlier prematureclosure remainswithdrawn.
Final generatedviews/validation will reflect correctedcompletion; bookmarks
and precisionfollowups remain separate. No commit/push/distribution performed.

20261005-0927 — Final methodology compilation, graphcurrency, scaffold/skill
validation and gitdiff whitespace check pass after statusreconciliation. The
required actual before/after result and matchedplayback evidence are linked
from currentledger/state/registry; allcurrent gates complete. Corrected goal
can be completed. Productbuild/signature preflight remainsgreen.

20261005 — Cam requested a conventional native preference toggle and update to
the local daily-use app. Reopened this same-feature story for the bounded
follow-up; earlier validatedbuild and actualperformance evidence remain scoped
to their hashes. Plan/research: `docs/research/timeline-preview-preference.md`.
Register boolean, wire basicInterfaceXIB/controller, cancel/hide on Save, then
prove physicaloff/on/Cancel/restart behavior and update localapp. No new approval
is needed: Cam explicitly requested implementation.

20261005 — Preference follow-up completed in155231: standard default-on native
Interface checkbox, inheritedbool accessor matching upstreamstatusmenu, Save
notification cancellation/hide and originaltooltiprestoration. Independent
review found no outstandingmaterial issue after the documentedtooltip/CLI fixes.
Final004 physical main-window tests pass defaulton/offSave/Cancel/restart/onSave;
explicitCLIoff also yields zero previewwork and preserves seek/Position/volume.
Final20-per-arm currentbuild comparison is valid: baseline222.039ms versus
feature236.531ms, +6.527%, within predeclared20% allowance. All52 rawcontracts,
40 latencies, frozeninputs and cleanexit0 audited; no p95/causal claim.
Localdailyapp updated, signed, launched and newcheckboxvalue1 observed; actual
Preferenceswindow leftvisible. See `docs/evidence/story-002/preview-preference-validation.md`.
All8 criteria, tasks and gates complete; previousrecords remain dated and scoped.
No publicdistribution/commit/push.


### 2026-10-05 — status reconciliation

The earlier dated entries that say Story 002 was In Progress, native UI was
unavailable, or a given candidate was current describe their acquisition
point; they remain preserved as historical records. Story 002 is Done for its
declared thumbnail MVP and preview-preference scope. Its required practical
ordinary-control comparison is scoped to preference candidate 155231 and the
matched playback evidence remains as recorded in the Story 002 ledger. Story
004's later qualified candidate 222506 and its present reopen findings are
tracked separately in the [Story 004 acceptance ledger](../evidence/story-004/current-acceptance-ledger.md).
The integrated root remains deferred for bookmarks; Story 004 is reopened for
wrong-track count correspondence and RAM-hot sample disk retention.
