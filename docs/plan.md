# Implementation plan

The deep dive is recorded in [timeline implementation planning](research/timeline-implementation-plan.md).
The Ideal remains the implementation-free North Star. The source/build route,
proposed architecture, tests and compromises live in that synthesis, the spec
and the feature and contribution stories.

1. **Story 001 — feasibility (Done):** pinned source, working isolated arm64
   app, native control map, diagnostic decoder/SQLite probes and concrete proof
   plan. The baseline build works; feature proof belongs to the following stories.
2. **[Story 002 — thumbnails](stories/story-002-timeline-thumbnails.md):** native
   hover/time/image on all four control surfaces; independent decoder helper,
   cancellation and bounded disposable cache. Prefer existing contrib FFmpeg
   libraries: the measured MP4/MKV pair works, unlike AVFoundation-only MKV.
   Done for the bounded MVP and the basic preference follow-up. Current signed
   build 155231 adds a default-on “Show timeline thumbnail previews” checkbox in
   Interface > Playback behaviour. Native checks covered off/save and hide,
   cancel, restart persistence, on/save and actual display, explicit CLI-off
   precedence, and normal seek/Position tooltip/volume preservation. See the
   [native preference record](evidence/story-002/native-preview-preference-final.json)
   and [build manifest](evidence/story-002/app-build-preview-preference-final-155231.json).
   The Story002 20-per-arm ordinary-control comparison measured baseline median
   222.039 ms (range 158.141–617.109) and feature median 236.531 ms (range
   113.493–526.612), +6.527%, within the prospective baseline-median +20%
   allowance. See the [comparison record](evidence/story-002/ordinary-control-preview-preference-final.json).
   This approximate shared-host knob-render result is not a causal speedup, p95,
   completed-seek latency or a general-host guarantee. The earlier 132643
   evidence remains dated and scoped; the three matched playback pairs and
   reader/helper/service proof are inherited unchanged. No fresh four-surface
   preference toggle or reader rerun is claimed. Precise tail/causal-stall
   characterization remains deferred. Historical failures stay preserved.
   Bookmarks, broad compatibility and public packaging remain separate.
3. **[Story 004 — responsive reusable thumbnails](stories/story-004-responsive-reusable-thumbnails.md)
   (Done, corrected001728):** reusable worker, progressive midpoint/largest-gap coverage,
   hover-centered priority and bounded cross-open cache are implemented and
   qualified on001728 after correcting count-mismatch wrong-track reuse and background eviction of RAM-hot disk images. Current-session RAM images bridge NAS validation with
   Checking source; fresh reopen requires metadata and sampled SHA256 under
   ADR-003. Current four surfaces, NAS, settings,20/arm ordinary controls and
   three active-preparation playback pairs pass their scoped checks. The local
   preview app is updated; [acceptance ledger](evidence/story-004/current-acceptance-ledger.md)
   retains resource costs, inherited reader proof and unqualified broader claims.
4. **[Story 002b / 005 — open-source contribution](stories/story-005-open-source-contribution.md)
   (Pending, next):** investigate VLC's current contribution process, conventions
   and existing thumbnail architecture; improve/port and independently qualify
   a focused contribution; then submit through the official process and shepherd
   review. The [initial scout](research/upstream-contribution-scout.md) finds
   current development infrastructure worth testing before retaining our helper.
   Phase 1 must settle the target and architecture before broad implementation.
   Cam requested this before bookmarks. This turn creates the plan only;
   upstream acceptance and the full investigation remain unproven.
5. **[Story 003 — bookmarks](stories/story-003-timeline-bookmarks.md):** compact
   one-to-three-word labels, visible markers, hover, add/edit/delete/seek and
   independent durable storage. Reuse 002's timeline context/presentation.
   First measure full-file identity verification and record the identity/store
   ADR. SQLite is the leading store candidate; replacement safety and hash cost
   must be reconciled explicitly before broad implementation.
6. Run each story's capability proof; after previews and bookmarks work, run the integrated root with
   restart, identity, retention, playback and accessibility checks on main,
   detached, native-fullscreen and custom-fullscreen controls.

The stories retain distinct image/caching versus durable-write/identity contracts.
All use a real pinned baseline; 003 now waits for 002b/005's contribution outcome
or Cam's explicit sequencing change, so its design follows learned upstream
conventions. Notes do not depend on a working decoder. Keep all format,
fullscreen, error handling and native UI work inside the owning feature story.
Do not split them into backend-only tasks that leave the interaction unfinished.

Cam authorized finishing Story 002, including implementation and validation.
This work follows the required pragmatic comparison plan in
`research/story-002-pragmatic-before-after-plan.md`. The earlier optional-
comparison goal was completed prematurely; a corrected active goal was created
at2026-10-05 15:05:13UTC to finish the required before/after comparison. Prior
goal/API and closure records remain historical, not current blockers or proof.
ADR-001 accepts storage lifetimes; ADR-002 selects the preview implementation.
Story 003 identity/schema choices remain proposals awaiting its technical gate.
Upstream contribution is now the next priority, before bookmarks. Full public
binary packaging, portability across moves/devices, colors and tags remain
deferred. Reuse the existing build where applicable, recheck free
space before heavier work, and preserve the prior low-disk guard. No other
project or installed VLC is modified. No commit/push in this planning step.
