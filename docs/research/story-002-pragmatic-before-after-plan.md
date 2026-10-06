# Story 002 required pragmatic before/after comparison

2026-10-05: Cam clarified that an actual baseline/post-change performance
comparison is still required. The earlier interpretation that the comparison
could be optional for closure was too broad. Story 002 is reopened; its existing
functional evidence and three matched playback pairs remain valid.

## Required experiment

Reuse the existing preserved baseline and unchanged signed feature132643,
generated90-second MP4, fixed main-window geometry, owned process cleanup and
frozen-v4 pixel/timestamp observer. Use its existing phase mode so accessibility
queries occur only before/after capture, rather than burden every frame with AX
work. Ownership/routing, per-frame foreground/window bounds, independent pixel
knob identity and actual WindowServer display timestamps remain checked. This
is an approximate knob-render response metric, not completed-seek latency or
equivalent precision/per-frame AX qualification. No new observer framework.

Collect four predetermined AB,BA,BA,AB blocks, five alternating clicks per arm
per block:20 actual responses per arm. Use the existing3000ms observation bound
to avoid making a900ms capture deadline the product target. Templates and seeds
use the same phase mode. Preserve all slow observations; stop on the first
invalid/censored dependent capture, never score an incomplete collection as a
passing comparison or substitute AX-only response for visible response.

Root prospectively selects a practical median ordinary-control allowance of20%
relative to the measured baseline. Report counts, median, min/max, four block
medians and raw samples. This intentionally replaces the elaborate100-sample
p95 gate for Story002 completion after Cam asked for a less-specific comparison.
Twenty samples do not support a precision p95 claim. Shared-host temporal
variation is reported, not added to the allowance or used to discard otherwise
valid samples. If the feature median exceeds the allowance, investigate the
feature path before considering closure; a noisy result does not prove cause.
Precise tail latency/causal stall characterization can remain deferred, but
the usable baseline/post-change comparison itself is mandatory.

Historical phase-mode diagnostics on an older candidate showed meaningful
feature overhead, so this current experiment is allowed to fail. Do not assume
removing per-frame AX is a product fix. Reuse functional/helper/service evidence
through unchanged-source provenance; fix any demonstrated product regression
with proportional build/native checks. No exact equality, zero resource growth,
new global load-control system, user-process termination or benchmark retry loop.

Primary timing reference: [Apple displayTime](https://developer.apple.com/documentation/screencapturekit/scstreamframeinfo/displaytime)
defines the WindowServer frame display time; use it rather than callback arrival.
Existing frame/pixel contracts and prior method controls are retained in their
scoped records. Root owns GUI actions. Hourly loop-review remains required for
extended work. No commits, pushes or public distribution are authorized.

The first phase cohort stopped at readiness after three baseline responses due
to an absent per-PID AppKit instance, despite the correct frontmostPID. It stays
invalid. A bounded prospective acquisition correction uses the validated
frontmost instance directly and retains all later guards. Four nativepositive
captures plus independently recorded foregrounddeparture and exactownedtarget
termination negatives passed; qualification/source/binaryhashes live in
`docs/evidence/story-002/control-frontmost-acquisition-qualification.json`.
The fresh complete cohort uses this variant in both arms; no older pooling.

Completed2026-10-05: fresh cohort002 supplies20 actual responses per arm with
zero faults and identical qualified observer contracts. Medianbaseline343.047ms,
feature330.741ms (observed−3.587%, within prospective20% allowance). Full ranges,
block variability, raw values and independent audit are recorded in
`docs/evidence/story-002/pragmatic-before-after-validation.md`. Both ownedapps
exit0 cleanly and product132643 remains unchanged. This completes the required
practical comparison, not a precisionp95 or causal-speedup qualification.
