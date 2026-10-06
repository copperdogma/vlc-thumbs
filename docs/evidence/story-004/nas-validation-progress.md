# Current NAS qualification — final222506

Two current actual-pointer10/10 cohorts and the requested installed daily app show
useful images on the reported8.44GiB wireless SMB movie. [Current cohort](native-nas-provisional-222506.json),
[supplemental pending/restart proof](native-nas-pending-visual-222506.json),
[delivery](local-preview-update-222506.json) and [acceptance ledger](current-acceptance-ledger.md)
record exact scope. RAM provisional images appear0.38–3.70ms while guarded
verification can take1.68s. Fresh reopen verifies sampled content before disk reuse.
Uncontrolled warmth and prior different timeout budgets prohibit causal speedup
claims. Source/sample guards pass. Older progress below remains dated history.

## Historical progress

# NAS validation progress — 2026-10-05

Cam delegated freshness choice. ADR-003 now accepts metadata plus at most 1 MiB
of fresh sampled SHA-256 for disposable thumbnails, with its unsampled-change
limitation explicit in spec. Candidate213341 enables that policy and adds guarded
worker teardown. Movies was absent on first recheck, then reconnected by Cam;
the real input is readable. All prior invalid attempts remain retained.

[Helper comparison](nas-helper-diagnostic-001.json) preserves AB/BA observations
against frozen build155231 on the four predeclared targets. Baseline block0
returned two previews and timed out twice; candidate block0 returned four, with
its first frame taking 8.446 s and later frames 32–56 ms. Warm block1 returned all
four per arm. All six successful paired images and actual timestamps match.
Sampled verification read exactly 1 MiB in 16 reads, taking 875 ms in that attempt.
Source cache warmth is uncontrolled, and candidate15s versus baseline5s budgets
explain part of first-block usability. No universal/native speedup is claimed.

Candidate block0 EOF cleanup exceeded the runner's3s exit wait and was killed.
Inspection found cleanup entered from idle without rearming the watchdog. The
worker-only fix preserves v2's whole-request deadline and starts an independent
15s teardown budget. Injected17s blocked-close proof terminated at15.012s after a
complete successful response, with no trailing output/payload corruption. See
`work/validation/story004/helper-teardown-contract.json`.

The first real service test overlapped native playback/background preparation.
All requested images and RAM/disk hits succeeded, but one slow request caused a
worker restart, failing its single-worker assertion. This remains a failed
contention observation, not erased or a playback attribution result. Raw evidence:
`work/validation/story004/nas-service-smoke-sampled-001.json`.

After closing the diagnostic native candidate, the isolated service test passed:

| Target seconds | Source | Delivery ms |
|---:|---|---:|
|1493|miss|265.1|
|3200|miss|164.3|
|6000|miss|177.2|
|4600|miss|111.5|
|1493 again|RAM|62.6|
|1493 reopened|disk|579.9|

One worker served uncached targets; reopening used a new service/context generation
and no decoder launch. Raw evidence:
`work/validation/story004/nas-service-smoke-sampled-002.json`.
These are service delivery measurements with warm source/OS caches, not native
panel presentation or guarantees. They do not replace control/playback comparison.

[Native preferences](native-preference-sampled-212257.json) record CUA Save-off,
Cancel, full restart retaining off, restore-on, actual pointer seek with Position
and volume preserved, local video and NAS playback readiness. CUA click/drag
attempts did not produce hover previews. Its exposed API lacks mouse move; Cam explicitly authorized the existing native mouse-event runner in the subsequent yes.
Four-surface hover, CLI precedence, native cache restart, matched20-per-arm controls
and dropped-frame/audio/resource comparisons remain required. Story004 stays
In Progress; the user's installed daily app remains build155231.

Current213341 native main-window settled/repeat/rapid-latest/taller-target reentry checks pass in two independent app launches; screenshots inspected. Requested samples on restart have zero decoder reads after proactive cache loading (RAM tier). Fresh frozen20-per-arm ordinary controls pass: baseline41.382ms median, candidate40.680ms, delta -1.695%, within baseline+20%; this is approximate knob-render evidence, not a causal speedup. First cohort invalid due to owner changing shared runner during collection; retained, not pooled. See native-main-sampled-213341.json and ordinary-control-sampled-213341.json. Fullscreen/detached and matched playback/NAS visible proof remain open.
