# Playback resource contract correction — 2026-10-05

An hourly closeout review found that the root evaluation had extended Cam's
ordinary-control baseline rule to CPU/RSS playback resources without support.
The zero-added-allowance choice applies to ordinary-control response only.

For playback resources, capture matched baseline and feature values and report
the CPU/RSS deltas. Acceptance remains tied to the already declared limits:
one active decode plus one replaceable pending request, a 32 MiB decoded-image
LRU, a 256 MiB disk cache, and the proposed 512 MiB worker RSS ceiling with
bounded allocations and a five-second unresponsive-worker termination. No
additional zero-delta requirement is introduced.

The current reported cost is approximately +2 percentage points CPU and
+20–40 MiB RSS. These values must remain visible in the comparison; they do not
establish harmlessness or a global pass. Playback acceptance still requires no
hover-induced seek, pause, or audio interruption, no feature-attributable stall
over 100 ms, and a dropped-frame-rate increase no greater than one percentage
point. The current repeated-ROI evidence does not attribute every observed
stall, so those criteria remain open rather than waived.

This correction leaves ordinary-control qualification unchanged: the target is
the matched unmodified-VLC baseline with zero added allowance, and that
comparison remains unqualified. Vanilla VLC has no thumbnail denominator, so
thumbnail delay remains separately reported and descriptive.

Decision context: the [13:48 completion course review](../../research/story-002-completion-course-review.md)
retains the adopted baseline-zero ordinary-control allowance and requires
remaining gaps to stay open when unsupported. This correction narrows that
ordinary-response decision to its intended scope; the earlier
[13:09 loop review](../../../work/validation/story002/loop-review-20261005T1309.md)
records the same ordinary-control choice. The [root contract](../../evals/root-timeline-experience.md)
and [current acceptance ledger](current-acceptance-ledger.md) carry the
reconciled wording.
