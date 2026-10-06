# Required pragmatic before/after validation — 2026-10-05

The required comparison is complete on unchanged preserved baseline and signed
feature 132643. This corrects the premature functional-only closure: baseline/post
performance comparison is mandatory, while precision p95 and causal-stall
characterization may remain deferred.

## Findings and measured scope

No material collection defect found in the bounded runner/acquisition review.
The complete cohort has 20 valid actual visible-control responses per arm, all
52 template/seed/scored sessions use the same qualified prospective acquisition
variant and phase AX mode, all capture fault arrays are empty, frozen inputs
match before/after, and both owned processes exited 0 with no cleanup errors.
No slow observation was discarded or pooled with failed cohorts. Root checked
these conditions against raw session records and the qualified probe/source
hashes. An independent agent recomputed every earliest matching frame timestamp and
median from raw records, verified ordering/counts/guards/cleanup, and matched
live source/app fingerprints against the unchanged 132643 manifest. No material
findings; its scoped closure assessment is recorded in the story work log.

| Approximate input-to-visible-knob response | Preserved baseline | Feature 132643 |
| --- | --- | --- |
| Valid scored responses | 20 | 20 |
| Median | 343.047 ms | 330.741 ms |
| Minimum–maximum | 279.568–487.320 ms | 233.484–420.992 ms |
| Block 0 median, baseline then feature | 349.647 ms | 319.641 ms |
| Block 1 median, feature then baseline | 333.535 ms | 304.034 ms |
| Block 2 median, feature then baseline | 369.773 ms | 362.590 ms |
| Block 3 median, baseline then feature | 326.413 ms | 326.847 ms |

Feature pooled median is 3.587% below baseline, within the prospectively chosen
baseline +20% median allowance (411.657 ms). This supports comparable ordinary
control response in this run, not a causal speedup or general performance
guarantee. Baseline block medians vary 326.413–369.773 ms; feature 304.034–362.590 ms.
The host remains shared with other work. No samples are removed or allowance
expanded because of that variability. Twenty observations do not qualify p95.

The endpoint is actual pixel-identified native knob render using WindowServer
frame display timestamps minus tagged physical input time. Phase AX checks
occur pre/post capture, with exact retained instance/executable, fresh foreground,
CG window/crop and routed input guards. It does not measure completed video seek,
hover thumbnail latency, or equivalent per-frame AX precision. Vanilla VLC has
no hover-thumbnail denominator. The unchanged helper/cache/native feature
proof remains separately linked in the acceptance review.

## Existing playback baseline/post comparison

Three matched 60-second pairs remain valid: feature-minus-baseline dropped-frame
fractions are −1.964, +0.783 and −5.905 percentage points. Every pair meets the existing
<=1 percentage point increase allowance. All six runs have zero detected interior
digital-audio below-threshold intervals and zero lost buffers; detection limits
remain. Repeated video ROI observations occur in both arms and remain unattributed,
so no universal no-stall claim follows. Reported costs are roughly +2 percentage
points app CPU and +20–40 MiB sampled app RSS, not zero overhead or harmlessness.
See [matched playback evidence](playback-cadence-16ms-current-summary.json).

## Failure preservation and provenance

The first pragmatic cohort stopped after three scored baseline responses because
a readiness per-PID AppKit lookup returned nil despite the correct frontmost PID.
It remains invalid, unpooled and unrescored. The prospective narrow correction
acquires the validated frontmost NSRunningApplication once, retains it and keeps
all later guards. Readiness self equality is acquisition fact, not independent
corroboration. Four baseline positive captures plus independently corroborated
foreground departure and owned target termination negatives passed. See
[qualification](control-frontmost-acquisition-qualification.json).

[Machine-readable result](ordinary-control-pragmatic-before-after.json) retains
all 40 raw scored values, eight blocks, frozen hashes, cleanup checks and absolute
ignored raw-artifact paths. Earlier 900 ms/100 sample cohorts remain invalid and
are not rescored. Product apps did not change during this comparison; the only
executable change is the scoped observer readiness acquisition correction.

## Closure assessment

All seven Story 002 criteria are now supported for the declared functional MVP
scope, including the required usable ordinary-control before/after comparison.
Helper/service/native/reader/resource evidence remains applicable through the
[acceptance review](shared-load-acceptance-review.md) and
[delivery manifest](mvp-delivery-manifest.json). Upstream suite retains51 pass,
1 skip,1 baseline-reproduced TLS failure,0 errors; it is not a fully green suite or
native feature proof. Broad media/MKV timing, exact diagnostic classification,
precise tail/causal attribution, public packaging and integrated bookmarks/root
remain explicit limits. No commit/push/public distribution was performed.
