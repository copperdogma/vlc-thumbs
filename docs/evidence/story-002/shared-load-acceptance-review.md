# Story 002 acceptance review under shared host load

Reviewed 2026-10-05 against signed build
[132643](app-build-controller-16ms-experiment-132643.json), controller SHA-256
`47b31fa472d778e0c48b304b6c07cf6e7f7a7a62cade31f42943093f4d093690`.
This is an evidence/source review, with no new runtime or GUI tests and no
story-status change. The root agent owns final closure validation.

## Findings and acceptance decision

The candidate-applicable evidence supports the native keyframe-thumbnail MVP's
functional acceptance under Cam's revised
[working plan](../../research/story-002-shared-load-completion-plan.md).
Precise ordinary-control performance and causal video-stall qualification
remain **unqualified**. Functional completion must not be represented as a
performance pass, a claim of zero stalls, or integrated-root completion.
Bookmarks and the integrated root remain deferred.

No demonstrated functional defect requiring a new implementation or broad
test matrix was established by this audit. Retain actual reproducible
feature-attributable defects as mandatory fixes. An inconclusive observer
attempt does not establish harmlessness, and high host load does not explain
its failure by itself. The failed input-response observation below remains
preserved; a missing response independently reproduced in valid ordinary use
would require investigation even after MVP closure.

## Seven acceptance criteria

| Criterion | Candidate-applicable evidence and judgment | Limits to preserve |
| --- | --- | --- |
| Native experience | [Current applicability](cadence-16ms-current-applicability.json) records current main, detached, native-fullscreen and prepared custom-fullscreen physical hover/clear/reentry. Main/native endpoint captions and detached stationary-pointer resize are observed; paused position and source integrity are preserved. This supplies required native surfaces in the declared visible-controls scope. | Detached host ID changes during resize; geometry follows the observed resulting controls. The earlier custom no-host attempt remains unexplained. The successful alpha-ready first entry is not a universal entry-reliability claim. |
| Correspondence | [Helper qualification](helper-tracknumber-results.json) passes 25 correctness/error cases and 200 standard MP4/MKV requests, independently checking pixels/keyframe times. Cases include long GOP, VFR, nonzero starts, edit offsets, rotation, SAR, 4K and long media. [Matroska mapping](matroska-track-mapped-contract.json) and [native selected-track menus](native-selected-track-results.json) cover original/reversed red-blue AVC tracks. Current MKV generation checks show requested times near 45.0185/81.469515 s with actual keyframes at 44/80 s. Unchanged decoding/context seams justify inheritance. | Keyframe gaps are approved MVP behavior, with actual time separate from pointer time. Broad codecs, negative Matroska origins and ordered editions remain unqualified. Multi-program unavailable UI passed; its native service diagnostic was `malformed-reply`, while direct helper output was `ambiguous_track_mapping`. Do not claim exact diagnostic classification. |
| Responsiveness | The [single shared-load comparison](ordinary-control-shared-load-20pct-inconclusive.json) is invalid and supplies no p95, threshold result or causal regression attribution. Under the revised authorized scope, this is a nonblocking precision-performance follow-up; ordinary controls have separate current functional click/drag/wheel/keyboard/volume evidence. Thumbnail delay remains descriptive because vanilla VLC has no thumbnail denominator. | Preserve historical absolute failures and invalid attempts; do not rescore them as passes. No preview-latency improvement or general response guarantee follows from functional completion. |
| Bounded work | Current service/context/geometry/helper inputs match 022512 and 072539. [Count/cache contracts](service-track-count-cache-contract.json) pass 25 non-latency checks, including mismatch cache isolation, in-flight file change, burst cancellation, cache ownership/quota and memory LRU. [Prior standard service run](service-tracknumber-results.json) covers 600 settled requests. Current [same-process burst](cadence-16ms-single-process-burst-applicability.json) supplies controller-specific pending-hide/cancellation proof below one 16 ms cadence, with no subsequent old display before MKV switch. | Require one active decoder plus one replaceable pending request, 32 MiB decoded cache, 256 MiB disk cache and finite cancellation/recovery. The helper enforces 512 MiB sampled RSS/physical-footprint, 128 MiB individual allocation, 320 MiB decoder-buffer accounting and a five-second deadline; the 10 ms watchdog can briefly overshoot and sampling is not an instantaneous hard RSS cap. Do not turn app RSS deltas into a zero-growth rule. |
| Fault handling | The unchanged helper/service contracts cover explicit unsupported inputs, malformed/oversized/crashed/hung helper recovery, missing helper, local-only launch, corrupt/refused cache and shutdown. [Actual permission/ENOSPC and replacement probes](cache-fault-results.json) complement the count/cache run's simulated IO refusal. [Native program-unavailable behavior](native-program-unavailable-results.json) supplies a visible unsupported-path observation with pause/source intact. The native controller clears unsuccessful replies rather than fabricating a successful image. | Preserve test-layer boundaries: service delivery proves neither pointer routing nor playback by itself. Unsupported mapping stays unavailable; broader presentations are not silently qualified. The count/cache report alone did not induce true ENOSPC. |
| Playback/control integrity | Current [three-pair analysis](../../../work/validation/story002/playback-cadence-16ms-001/analysis.json) has six eligible 60 s collections with matched fixture, observer/geometry and diagnostics-disabled conditions. Individual dropped-picture-rate increases are -1.9642, +0.7834 and -5.9052 percentage points, each within the existing 1 pp limit. All six source hashes remain unchanged, all have zero interior digital-audio gaps and 80 successful pointer moves; helper processes were sampled in feature runs. Current main click, drag, wheel, keyboard seek and volume checks passed. Historical actual-reader observations plus source-invariant inheritance and fresh main reader checks support accessibility, as detailed below. | ROI repeats occur in both arms without attribution; retain them as unresolved characterization under the revised policy. Whole-second RC values cannot exclude tiny seeks or establish precise stall absence; source review and paused native observations supplement that boundary. CPU/RSS costs remain approximately +2 percentage points and +20–40 MiB. Reader samples do not establish continuous speech silence or repair VLC's inherited VoiceOver increment behavior. |
| Reproducible app | [132643 manifest](app-build-controller-16ms-experiment-132643.json) pins VLC source `6de05adcbaf2e8b85fe86aad4169393098628119`, owned source/build inputs, arm64 helper dependencies, bundle outputs and successful strict signing verification. The private libavformat archive/provenance is recorded; source/apply/build recipes are tracked outside ignored work. Helper bundle resolution and source isolation remain unchanged. | Clean dependency rebuild, notarization, distribution, Intel/other-platform packaging and broad media support remain deferred. Development delivery does not qualify a public release. |

## Explicit inheritance reasoning

The 022512, 072539 and 132643 manifests have identical service, context,
geometry and helper source hashes. Their signed bundled helper output is
identical: `cbbd6784deb18501eddccf4d695dbd7b39c3ef27b14374fa34209d638d6b836f`.
The decoder/archive inputs match. The controller changes canvas placement and
refresh scheduling; it still uses the same context and selected-track/count
service contract. This supports reuse of correspondence, helper bounds,
cache/fault/replacement and selected-track mapping proof in their recorded
scopes. Historical native timing or playback results are not inherited as
current measurements: the current six-run playback cohort supplies its own
candidate-specific evidence.

For reader behavior, the preserved 012354 controller source at
`work/validation/story002/presentation-draw-experiment/VLCTimelineInteractionController-before.m`
matches that manifest's `8f29688434a60fa3510178bf5bd898e16e64a7571a762b160515a1e800eeb937`
hash. Comparing it with 132643 shows unchanged panel `canBecomeKeyWindow` and
`canBecomeMainWindow` returning NO, AX subtree exclusion, mouse-event
transparency, slider accessibility label/action ownership and fullscreen
collection/parent behavior. Adding a canvas/card and timer does not introduce a
new accessible or focus-owning preview window. The
[restored reader proof](voiceover-restored-remaining-surfaces.json), its linked
main/custom observations and fresh current main-window 12-sample reader/control
check therefore support proportional inheritance. Current four-surface physical
interactions supplement the changed presentation path. This is explicitly
inherited evidence plus focused confirmation, not a newly run four-surface
reader test; no blanket rerun is justified solely by the canvas/timer change.

The prepared custom-fullscreen check sampled owned-window alpha=1 three times
before first hover and observed preview, leave and reentry. That is sufficient
for the declared fully-visible-controls interaction. An earlier no-host result
during entry/fade does not establish a reproduced product defect after full
visibility. Keep its unknown cause rather than explaining it retroactively.
If eligible fully visible controls plus delivered mouse movement reproducibly
fail to show preview, treat that as functional work rather than deferred timing.

## Precision-performance outcome

The prospectively declared rule is `candidate p95 / baseline p95 <= 1.20` on
at least 100 valid responses per arm. The four predetermined baseline blocks
have 25 responses each; the screen is
`V=(max(block medians)-min(block medians))/min(block medians)`, with `V>0.20`
inconclusive. This median screen is not p95 confidence, and variability never
enlarges the allowance. Repeated baseline cohorts and uncertainty estimates
belong to a future short quiet-window precision comparison.

The sole new frozen-v4 attempt stopped at 25 baseline / 48 feature observations.
The expected new knob was missing: one complete frame retained x=950 while AX
changed from approximately 5585.997 to 6651.446; input routing and ownership
passed. Integrity stayed unchanged and no inputs changed. The complete cohort
is invalid: no partial percentile, block-variation result, performance pass or
regression attribution is salvaged. This is the final bounded attempt, not a
reason for a new observer or automatic retry.

Recorded one-minute whole-host load ranged 12.1743–18.9370; summed process CPU
ranged 610.1–965.4%, reflecting percentages summed across multiple cores. Those
samples include VLC and test apparatus, are not machine utilization percentages,
and do not attribute failure to Cam's AI threads. Shared load is context, not a
proved cause. The missing-knob observation remains available for a later
independent reproduction if necessary.

Before marking Done, root must reconcile story/spec/state/ledger/registry with
these seven judgments, link the current playback cohort, retain all historical
failures and explicitly keep precision latency/causal-stall qualification
unqualified. Functional completion must not conceal an independently reproduced
defect or imply completion of Story 003 or the integrated root.
