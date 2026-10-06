# Story 002 resumed working objective — 2026-10-05

Cam approved the preceding recommendation to retain demonstrated functionality, use a practical explicit regression allowance that accounts for measured variability, and reserve a short quiet-machine window for precise performance claims. Cam reports two other AI threads continually use the machine. Exclusive mouse/keyboard ownership remains authorized; exclusive compute resources are not assumed.

## Objective and goal-tracker limitation

Finish Story 002's native keyframe-thumbnail MVP using current-candidate functional, correspondence, bounded-work, fault, playback/control, accessibility and reproducible-build evidence. Preserve exact historical outcomes and disclose precision-performance limits. Use loop-review after each hour of extended work. The earlier goal API reported a blocked tracker with no resume/objective-edit operation. Cam subsequently deleted that goal and explicitly requested a new one; on 2026-10-05 at 08:50:42 Edmonton, create_goal succeeded with an active updated objective matching this plan. The historical API limitation is resolved by Cam's action, not by falsely completing or replacing unfinished work.

## Revised acceptance contract

Ordinary-control precise qualification uses an explicitly declared 20% p95 regression allowance relative to matched unmodified VLC, chosen before further measurements. This is a pragmatic MVP tolerance, not a measured perceptual threshold. Never add background variability to that allowance to make it larger. At least 100 valid responses per arm are needed for a percentile comparison. Report temporal block variation and uncertainty separately: for the four predetermined 25-response baseline blocks (runner rounds0..3), calculate V=(max(block medians)-min(block medians))/min(block medians); if V exceeds 0.20, or measurement setup/ownership/pixel identity fails, call the comparison inconclusive, never pass or product regression. This median screen is not a confidence bound on p95. A completed stable run can establish only the declared threshold outcome for its observed cohort, not a precise causal estimate or general-host guarantee. A future quiet-window comparison should include repeated baseline cohorts and uncertainty estimates; the current shared-host experiment cannot claim exclusive load or causality.

MVP completion requires functional correctness and the existing bounded resource/playback gates, not a precise zero-regression claim under uncontrolled load. Keep no hover-induced seeks/pauses/audio interruptions, valid images/timestamps, no stale generations, accessible native controls, required surface interactions, <=1 percentage-point paired dropped-frame increase, finite worker/cache/backlog/timeouts and source preservation. Actual reproducible feature-attributable stalls remain defects to fix. Repeat observations present in both baseline and candidate without attribution are disclosed as unresolved performance characterization; absence of attribution is not evidence of no stalls. Broader format/platform/public packaging remain deferred.

Vanilla VLC has no thumbnails; new thumbnail delay remains separately descriptive. Existing absolute failures and invalid comparisons are not rescored as passes. Historical zero-allowance policy is superseded prospectively only. CPU/RSS costs remain reported, with declared worker/cache limits required. The prior plan treated an inconclusive comparison as a nonblocking follow-up; Cam's later clarification supersedes that for the actual ordinary-control baseline/post comparison, which is required for Story 002 completion. Precise tail-latency/causal-stall qualification remains deferred. The eval registry distinguishes functional evidence from performance qualification.

## Bounded execution and exit

1. Reconcile the story/eval/spec/state/ledger with this authorized policy and enumerate candidate-applicable evidence. Keep the build 132643 frozen unless a concrete product defect appears.
2. Run at most one existing frozen-v4 100-per-arm comparison with20% allowance on the shared machine, recording background-load context. No new observer version, global cache flush, user-process termination or automatic retries. Stop this lane on its first invalid result or after15minutes; preserve the whole attempt without partial percentile salvage. Evaluate baseline temporal variability only if the entire collection is valid.
3. Use proportional current evidence inheritance where helper/service inputs are byte-identical. Review remaining functional gaps and fix/test actual defects rather than redevelop measurement tooling.
4. Validate current acceptance with a findings-first review, regenerate methodology records and close through mark-story-done only if the revised functional gates are met. Clearly record any deferred precision-performance claims. No commit/push or new automation is authorized.

Primary noise guidance: [LLVM benchmarking tips](https://llvm.org/docs/Benchmarking.html) recommends repeated measurements and reducing other running processes; noise reduction alone does not eliminate measurement bias. macOS-specific causes of earlier failures remain unknown.


## Superseding user clarification — 2026-10-05

Cam clarified that an actual baseline/post performance comparison remains
required for Story 002 completion. This supersedes the earlier statement above
that an inconclusive comparison could be deferred for MVP closure. At reopening, the former
Done disposition was withdrawn and Story 002 was In Progress. Preserve the existing
functional evidence and three valid matched playback pairs. Use the current
[pragmatic before/after plan](story-002-pragmatic-before-after-plan.md): 20
actual ordinary-control responses per arm across four counterbalanced AB, BA, BA, AB
blocks; existing phase-mode observer; 3000 ms observation bound; actual pixel-
render response median; prospective allowance of baseline median +20%. Report
medians, ranges, block medians, raw samples and variability. This does not
support a precision-p95 claim. Precise tail/causal characterization remains
deferred. Historical failures and invalid attempts remain unchanged.


## Completed pragmatic comparison — 2026-10-05

The user-required comparison is complete and audited. Twenty valid actual visible
knob-render responses were captured per arm across blocks ordered AB, BA, BA, AB.
Baseline median 343.047 ms (range 279.568–487.320); feature median 330.741 ms
(range 233.484–420.992), delta −3.587%, within prospective baseline median
+20%. See [validation](../evidence/story-002/pragmatic-before-after-validation.md)
and [raw results](../evidence/story-002/ordinary-control-pragmatic-before-after.json).
This is an approximate shared-host observation, not causal speedup, p95,
completed-seek latency or a general-host guarantee. The earlier functional-only
closure was withdrawn at reopening; the required comparison now supports Story
002 Done for its declared functional MVP scope. Preserve the invalid and failed
historical attempts. Precise tail/causal-stall characterization remains deferred;
three valid matched playback pairs remain accepted.
