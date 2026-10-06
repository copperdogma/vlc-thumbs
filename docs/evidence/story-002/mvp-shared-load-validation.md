# Story 002 functional MVP validation — 2026-10-05


> **Interim disposition history:** The prior functional-MVP Done
> recommendation was withdrawn at reopening. Cam clarified that an actual baseline/post
> ordinary-control comparison is required for Story 002 completion. The story
> is In Progress. Existing functional evidence and three valid matched playback
> pairs remain accepted. The required comparison uses 20 actual responses per
> arm, four counterbalanced blocks ordered AB, BA, BA, AB, phase-mode 3000 ms observation,
> actual pixel-render response medians, and a prospective baseline median +20%
> allowance. Report ranges, block medians and variability; do not claim precision
> p95. Precise tail/causal characterization remains deferred. See the [current
> plan](../../research/story-002-pragmatic-before-after-plan.md). The original
> closure evidence and conclusions below are preserved as historical record.


## Final completion after required comparison — 2026-10-05

The required pragmatic comparison is now complete and independently audited.
Baseline median was 343.047 ms (range 279.568–487.320); feature median was
330.741 ms (range 233.484–420.992), delta −3.587%, within the prospective
baseline median +20% allowance. The 20-per-arm cohort has 52 phase/acquisition
raw sessions independently recomputed, zero capture faults, unchanged
fingerprints and clean owned-process exits. See [comparison validation](pragmatic-before-after-validation.md)
and [machine-readable result](ordinary-control-pragmatic-before-after.json).
This approximate shared-host pixel-identified knob-render measure is not causal
speedup, p95, completed-seek latency or a general-host guarantee. The earlier
functional-only Done disposition was withdrawn at reopening; Story 002 is now
Done for the declared functional MVP scope based on the completed gate. Existing
functional evidence and three matched playback pairs remain valid. Precise tail
and causal-stall characterization remain deferred. Historical invalid attempts
and failures remain preserved.

## Findings first

No demonstrated functional defect remains under the user-approved shared-load
MVP scope. Strong [acceptance review](shared-load-acceptance-review.md) maps all
seven criteria to candidate-applicable proof and describes inheritance explicitly.
The signed controller 132643 is unchanged; no runtime code was changed during
this policy/closeout pass. Precise latency and causal-stall qualification remain
unqualified. An independently reproducible feature-caused defect remains a
required fix even after MVP closure.

Cam approved the practical-tolerance/noise-aware direction, then explicitly
deleted the obsolete blocked goal and requested a new updated goal. Root created
that active goal successfully and selected a prospective 20% ordinary-control
p95 allowance before further collection. The updated goal explicitly permits
inconclusive precision characterization to remain deferred; this is not a
performance-pass claim. The [working objective](../../research/story-002-shared-load-completion-plan.md)
records the exact policy, temporal variability screen, scope and stop rule.

## Requirement scorecard

Overall grade:B — functional MVP complete in the declared native/local-media
scope, with explicit performance/compatibility limits. Seven of seven revised
functional acceptance criteria are supported. Precision qualification is deferred,
not included as a passing score.

| Criterion | Grade | Evidence |
| --- | --- | --- |
| Native experience | B | Current physical main/detached/native/full-visible-custom hover, endpoint, resize and clearing observations; earlier custom no-host failure preserved. |
| Correspondence | B | Unchanged helper/context inputs, independent fixture keyframe/pixel/time contracts, selected AVC MKV track menus and fresh MP4-to-MKV display/generation observations. |
| Responsiveness | B for functional scope | Current native controls usable and preview work asynchronously scheduled; exact performance remains unqualified under the adopted nonblocking deferral. |
| Bounded work | B | One active decoder and one replaceable pending request,32 MiB decoded cache/256 MiB disk cache, finite timeout/resource watchdog, service cancellation and fresh sub16ms pending-hide proof. Sampling is not an instantaneous RSS ceiling. |
| Fault handling | B | Unchanged malformed/crash/hang/unsupported/cache-fault contracts, native unavailable response and scoped permission/ENOSPC probes; diagnostic classification limitation retained. |
| Playback/control integrity | B | Current three paired playback runs each meet<=1pp dropped-frame increase, digital audio continuity/source hashes preserved; current native controls/mainreader plus source-invariant four-surface reader inheritance. Unattributed repeats remain disclosed. |
| Reproducible app | B | Pinned source/patch/build manifest, arm64 private helper and strict signing verification; clean rebuild/notarization/public release remain out of scope. |

The [acceptance review](shared-load-acceptance-review.md) provides source hashes,
original evidence links, tested cases and each limitation behind this table.
Historic four-surface reader results are reused through unchanged AX/focus
ownership, supplemented by current main-reader and all current physical surface
checks; this is not a fresh four-surface reader run. Helper/service/context/
geometry provenance supports reuse of their unchanged tests. No blanket rerun
is needed for documentation-only closeout.

## New bounded comparison

One frozen-v4 comparison with prospective 20% allowance stopped invalid at25
baseline/48 feature responses. A captured frame retained the old knob despite
changed AX value and valid routed ownership. App/fixture/tooling hashes stayed
unchanged. [Archived outcome](ordinary-control-shared-load-20pct-inconclusive.json)
preserves the complete failure and variable host-load context. No partial
percentile, baseline-variation assessment or performance effect is salvaged;
load does not establish the cause. The measurement lane is stopped, with no
new observer or automatic retry. A future short quiet-window characterization
remains in the inbox, alongside separately descriptive thumbnail delay.

## Proportional validation and reuse

Root freshly ran patch-application check, app-build preflight, strict deep bundle
signing verification and diff whitespace check; all passed. Final methodology compile and validation passed after status reconciliation;
143 evidence JSON records parsed and the current story checklist is complete. Existing configured VLC
suite is51pass,1skip,1 baseline-reproducedTLSfailure, not an all-green suite or
nativeGUI proof; unchanged core/TLS binaries justify retaining that known
baseline result. This pass does not redistribute binaries or modify installed
VLC, private videos, real annotation stores or source projects.

The full implementation and untracked source were covered by preceding source/
contract reviews; the new strong review verifies current manifest inheritance
and all revised acceptance boundaries. Additional codex-review was not run for
this docs/evidence-only pass because the candidate runtime source is unchanged
and focused strong review already addresses the acceptance/inheritance risk.
No live workflow learning was promoted; the user correction is retained in
research/working-plan records rather than silently changing imported skills.

## Historical functional-only closure recommendation — withdrawn 2026-10-05

Close now under the explicitly revised functional MVP scope, after final generated
record checks. Record Story 002 Done separately from precise-performance-unqualified
and integrated-root-deferred. No bookmark capability or public binary release
is implied. Goal completion follows actual story/status reconciliation and
validation; no commit/push is authorized.


Historical functional-only final disposition, withdrawn at reopening: Story 002 Done before the required comparison. All seven
revised criteria are supported; precise performance remains unqualified/deferred.
Generated story index and methodology graph reflect closure. No commit, push
or binary distribution occurred.
