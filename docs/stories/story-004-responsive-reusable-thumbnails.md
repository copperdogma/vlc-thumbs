---
id: "004"
title: "Responsive previews with background preparation and reusable caching"
status: Done
priority: High
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity, ideal:req:evidence]
spec_refs: [spec:1, spec:2, spec:4, spec:5]
adr_refs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services, adr-003-persistent-thumbnail-preparation]
decision_refs: [docs/decisions/adr-003-persistent-thumbnail-preparation/adr.md, docs/decisions/adr-001-media-metadata-storage/adr.md, docs/decisions/adr-002-native-thumbnail-services/adr.md, docs/research/nas-thumbnail-latency.md, docs/research/story-002-pragmatic-before-after-plan.md, docs/runbooks/build-story.md, docs/runbooks/media-metadata.md]
depends_on: ["002"]
category_refs: [spec:2, spec:4]
architecture_domains: [native-timeline, thumbnail-scheduling, media-identity, thumbnail-cache]
eval_refs: [root-timeline-experience, story-004-responsive-preview-capability]
---
# Story 004 — Responsive previews with background preparation and reusable caching

**Status:** Done. **Priority:** High. **Depends on:** 002.
Cam authorized implementation and a goal to finish the story on 2026-10-05. Existing native UI,
helper, cache, tests and build supply the substrate. Worker protocol and cache
identity decisions are the first technical gate, not assumed completed work.

## Goal

Make exploring large local and mounted-network videos useful: prepare sparse
keyframe previews in the background, prioritize the current hover and surrounding
moments, reuse completed work, and keep useful thumbnails across closing and
reopening VLC. Show truthful nearby images and understandable waiting/failure
states on the actual macOS timeline while preserving playback. Keyframes remain
the preferred samples; generating every frame or every half-second is unnecessary.

## Eval Ladder Context

The integrated `root-timeline-experience` remains deferred until bookmarks exist.
Story 002's bounded local-fixture capability and ordinary-control comparison
passed; those results do not establish large-file NAS responsiveness. The
[2026-10-05 NAS investigation](../research/nas-thumbnail-latency.md) observed a
helper timeout on an 8.44 GiB H.264 SMB file and, in another request, 3.522 seconds
inside reads versus 1.209 ms scaling. The original UI incident was not logged;
these are diagnostic helper measurements, not native presentation measurements.

This story's proof combines deterministic scheduler/cache/fault contracts,
actual native hover, and matched before/after trials on local storage and SMB.
Preserve build155231 as the pre-change feature baseline; unmodified VLC remains
the control/playback baseline. Register a scoped capability eval when its runner
exists; do not invent a score from these planning notes. Rerun affected preview
and eventual integrated-root contracts after implementation.

## Acceptance Criteria

- [x] **Proactive sparse coverage:** When an eligible video opens with previews
  enabled, preparation starts after media context is ready using midpoint,
  quarter and finer breadth-first coverage when empty. With existing samples,
  fill the largest remaining gaps, skipping valid cache/in-flight entries. Record a
  finite duration-aware coverage plan and rate/budget limits before scoring.
  Demonstrate eventual planned coverage under available resources; completion
  does not mean every keyframe or every existing half-second bucket. Reopening
  resumes gaps in the plan rather than regenerating completed samples.
- [x] **Hover-centered priority:** Let the single bounded active extraction
  finish on ordinary pointer movement; preserve its result in the correct cache.
  The latest uncached hovered target runs next, then missing samples in increasing
  distance on either side of the current hover. Use a deterministic tie rule
  that visits both sides. Recenter pending priorities when the pointer moves;
  intermediate targets cannot create an unbounded backlog. Same-sample movement
  shares in-flight/completed work. On hover exit, hide the panel immediately,
  finish valid active work and return to largest-gap coarse coverage.
- [x] **Reusable worker and bounded interruption:** Reuse open file/container
  state across successful uncached targets; opening/probing is not repeated per
  hover. At most one extraction is active, with bounded pending intents and
  off-main work. Preserve finite startup/request/stuck-worker deadlines and
  crash recovery. Stop/close, media or selected-track change, invalidated identity,
  disable preference/CLI override, and shutdown cancel obsolete work and clear
  its queue. A stalled job may be terminated; ordinary pointer movement alone
  must not repeatedly kill/reopen the worker.
- [x] **Useful persistent cache:** On the same unchanged file and selected track,
  retained thumbnails are served after media close/reopen and full app restart
  without decoding those cached samples again. Persist successful samples and
  coverage incrementally so partial preparation also survives normal quit;
  interrupted writes leave earlier valid entries usable. Store small images
  locally in the feature Caches subtree. Closing/quit is not an eviction event.
  Retain until bounded eviction, explicit cache clearing, invalidation, corruption
  or incompatible format/version; thumbnails remain regenerable, not permanent
  user records. Reuse actual keyframes across nearby target lookups, with truthful
  sample timestamps. Test different requested targets sharing one sample.
- [x] **Safe reuse and ownership:** Before enabling cross-open hits, record the
  identity/freshness ADR described below and make the corresponding spec decision
  explicit. Verify unchanged reopen, file replacement including preserved
  size/mtime, symlink retargeting, track changes, changed transforms/protocol,
  mutation while decoding, and corrupt cache/manifest cases against that contract.
  Runtime request generations reject stale presentation; they must not make
  every saved image unreachable next launch. Thumbnails and preparation never
  modify video files, adjacent NAS folders, ordinary VLC settings or annotations.
- [x] **Truthful native presentation:** On main, detached, native fullscreen and
  custom fullscreen timelines, show a matching cached nearby sample promptly
  when permitted by the declared distance policy, retaining its actual time
  separately from the hover target. A result for an obsolete hover may be cached
  but cannot masquerade as the newest time. Switching media/track never shows
  the old context. A useful same-context image may bridge a pending request;
  otherwise show an honest preparing/slow-source state, not an unlabeled black
  image presented as a successful preview. Preserve controls and accessibility.
- [x] **Recoverable errors:** Distinguish timeout/slow source, disconnected or
  changed file, unsupported media/track and worker/protocol failure in diagnostics
  and appropriate user-facing states. Canceled work is not a decode failure.
  A transient failure does not permanently mark a coverage hole complete or
  unavailable: bounded retry/backoff can recover with a stationary hover or after
  NAS reconnection. An unreachable sample cannot starve the remainder or cause
  an automatic retry loop. Unsupported media does not receive endless retries.
- [x] **Bounded resources and useful retention:** Declare sampling density,
  pending-queue bound, worker deadlines, I/O pacing, memory/disk limits and cache
  retention before collection. Start from the existing 32 MiB RAM/256 MiB disk
  budgets and decoder allocation/RSS safeguards; justify any change with evidence.
  Persistent-worker lifetime must not invalidate the old one-process CPU/deadline
  assumptions. Preparation yields to playback pressure. Test long durations,
  full/read-only caches, eviction and more candidates than fit: preparation must
  not endlessly evict/regenerate its own samples or flush useful recent hover
  images just to fill a background grid. Disabling previews stops proactive work.
- [x] **Measured improvement with practical controls:** Capture pre-change and
  candidate results with the same declared pointer patterns and media, including
  initial preparation, stationary misses, rapid sweeps, jumps, repeat visits and
  reopen. Predeclare the comparison before running it; preserve all attempts,
  failures, queue waits, bytes read, open counts and displayed-sample timing.
  Demonstrate reduced repeated initialization/read waste and improved usable
  preview delivery on the reported class of NAS input; source inspection alone
  cannot pass. Use at least 20 valid ordinary-control responses per arm and the
  agreed baseline-median +20% allowance under variable host load; invalid
  acquisition is inconclusive. Compare matched playback with preparation and
  hover active using the existing dropped-frame/audio checks, reporting CPU/RSS
  costs and unresolved attribution. Do not promise universal NAS or p95 latency.
- [x] **Delivery and regression proof:** Build/sign the isolated arm64 app, run
  applicable existing helper/track/time/cache regressions plus new protocol,
  scheduler and restart cases, and inspect actual UI behavior. Keep settings
  Save/Cancel/restart/off behavior and ordinary seek/volume/reader focus intact.
  Offer/update the local preview app within then-current user authorization and
  record exact build provenance. No public packaging or publication is implied.

## Out of Scope

Bookmarks/annotation identity or schema, exact-frame refinement unless separately
justified, every-keyframe precomputation, HTTP/live/DRM streaming, NAS server
software/transcoding, downloads of whole private videos, cloud uploads, moving
`moov` atoms or otherwise rewriting media, automatic cross-path move/copy matching,
unlimited cache storage, and public binary distribution. Mounted SMB regular
files are in scope despite arriving through `file:` URLs.

## Approach Evaluation

| Candidate | Benefit | Cost / discriminating proof |
| --- | --- | --- |
| Persistent private libav worker plus priority scheduler | Reuses installed dependencies, container/index/decoder state and isolation; leading candidate | Version IPC/lifecycle, enforce per-request bounds, measure repeated reads and actual NAS display |
| Persistent worker with incrementally cached coarse coverage | Immediate reuse near interest plus useful images elsewhere and on later opens; leading combined direction | Bound preparation/eviction, avoid playback contention; prove priority transitions and restart hits |
| Breadth-first midpoint subdivision, then largest remaining cache gaps | Cam's follow-up proposal gives early coverage across the whole duration; combines with hover priority | Selected under Cam's implementation request; account for existing samples, keyframe duplication, seek cost and finite density; compare coverage per elapsed time |
| Reused container/index with separately isolated decode jobs | Can retain index work while isolating individual decode failures | More ownership/data handoff; compare complexity and I/O with a persistent decoder before choosing |
| Batch whole-timeline preparation before useful hover | Simple scan order and eventual complete index | Delays initial use and may spend bandwidth on unseen areas; unsuitable as a prerequisite to hover |
| Keep per-hover processes and only extend timeouts/reduce dimensions | Small patch and possible temporary relief | Does not meet reuse or scheduling requirements; measured scaling is already about 1 ms |
| Full-file content hash before each cache hit | Strong content identity | Reads entire large NAS file before benefiting from cache; measure as correctness/cost baseline |
| Stable path/file identity, metadata and bounded content checks | Fast candidate lookup and likely practical reuse | Partial checks cannot prove every byte unchanged; requires explicit freshness contract and replacement tests |

**Simplification baseline:** This is deterministic scheduling, file access,
decoding and local state. A single LLM call cannot replace those operations;
AI-only/hybrid calls add no required capability. No paid model benchmark applies.

Use established players for mechanisms, not unquestioned architectures:
[thumbfast](https://github.com/po5/thumbfast/blob/master/thumbfast.lua) retains a
worker, coalesces seeks and supports early startup;
[IINA](https://github.com/iina/iina/blob/develop/iina/PlayerCore.swift) prepares
and caches thumbnails, with explicit remote-volume treatment. Preserve our
selected-track, timestamp, privacy and playback requirements. Confirm relevant
upstream code/API and licenses before copying code. Adapt or improve these
patterns when local measurements support doing so; do not add exact-frame
refinement simply because another player does it.

### Identity and lifecycle decision gate

ADR-001's lifetime split remains accepted. ADR-002's short-lived helper,
terminate-on-new-demand and per-open cache namespace describe the shipped MVP;
this story intentionally changes those assumptions. Before implementation of
cross-open reuse, create a follow-up ADR selecting worker protocol, persistent
cache identity/invalidation, manifest/versioning and interrupted-write behavior.
Decouple durable sample keys from ephemeral presentation generations.

A full fresh content hash and cheap metadata/sampled fingerprints offer different
correctness guarantees. The current spec forbids silently weakening replacement
safety. This story does not silently accept an IINA-style metadata-only policy,
nor assume a fast algorithm can establish complete content equality without
reading content. Measure the cost, document the threat/freshness boundary and
resolve any required product tradeoff with Cam using a concrete proposal. Until
resolved, do not label persistent reuse qualified. This is a bounded technical
planning gate; existing helper/cache/UI substrate is available now.

## Tasks

- [x] Freeze build155231/source manifests and reproduce the NAS failure class
  with stage timing; include a legal redistributable long/high-bitrate fixture
  on local storage and a controlled slow-I/O fixture. Keep private NAS evidence
  and paths ignored. Recheck disk headroom before adding generated fixtures.
- [x] Define the smallest finite sampling/priority plan: progressive midpoint/largest-gap coverage
  without hover; active work finishes; newest hover then outward neighbors;
  clear exceptions for context invalidation, disable and stuck work. Record
  queue, pacing, retry, pause/backoff and eviction rules and comparison protocol.
- [x] Evaluate repeated-open and unnecessary packet-read costs; compare the
  leading worker routes using existing contrib libraries. Write the lifecycle/
  cache identity ADR and update the applicable spec contract before adopting it.
- [x] Extend helper protocol/worker lifecycle and service orchestration. Separate
  presentation cancellation from useful same-media work; reset decoder state
  correctly on seeks and retain media/track correspondence and bounded cleanup.
- [x] Implement sample lookup/deduplication, incremental persistent cache/coverage,
  atomic recovery and quota-aware retention. Reopen/cache keys must survive
  process generations and respect the accepted identity policy.
- [x] Implement the priority scheduler and resource pacing; add deterministic
  state-transition tests covering jitter, jumps, hover exit, start/end, same
  sample, existing coverage, failure/backoff, capacity churn and all invalidations.
- [x] Integrate nearby-sample/pending/failure UI and existing preview preference
  across all four native surfaces, preserving timestamp honesty and reader focus.
- [x] Exercise restart reuse and faults, helper hangs/crashes, file replacement,
  unavailable/reconnected SMB volumes, read-only/full cache and schema mismatch;
  inspect actual artifacts and confirm no video/annotation writes.
- [x] Run the predeclared same-file old/new preview comparison and practical
  ordinary-control/playback checks. Include visible UI, not only helper timings.
  Use failure classification via `/improve-eval` where needed; register the
  scoped runner/results in `docs/evals/registry.yaml` without rewriting old scores.
- [x] Build/sign, run affected Story 002 regressions and proportional upstream
  checks, then `make methodology-compile`, `make validate`, and `git diff --check`.
  Use native runners and ignored `work/validation/` artifacts; imported Python
  pipeline/driver.py and format-matrix commands do not exist in this project.
- [x] Remove superseded paths, reconcile spec/state/plan/research/eval coverage,
  and provide a validated local app when authorized.
- [x] Verify traceability, source fidelity, simple deterministic ownership,
  playback/accessibility preservation and actual visual behavior before closeout.

## Workflow Gates

- [x] `/build-story`: implementation complete, affected checks run, evidence shared.
- [x] `/validate`: acceptance reviewed against the candidate, limitations explicit.
- [x] `/mark-story-done`: statuses and generated views updated only after proof.

## Blocker Summary

No current blocker. The reproduced mapping/retention defects are corrected and
revalidated on001728 under the approved plan. Earlier failed baselines and
intermediate evidence remain historical; current closure maps to the
[ledger](../evidence/story-004/current-acceptance-ledger.md).

## Blocker Evidence

Current native NAS/four surfaces/settings/restart, practical control/playback,
local identity/quota/fault contracts and requested local delivery are qualified.
Reader focus is inherited explicitly for unchanged accessibility behavior; the
fresh startup attempt was inconclusive. No general-reader repair is claimed.

## Unblock Condition

N/A. If the identity/performance requirements prove incompatible under the
available SMB semantics, record the evidence and concrete tradeoff before
changing the contract; do not silently weaken it or claim persistence passed.

## Architectural Fit

`spec:2` and `spec:4` have partial substrate in the climb phase. Extend the
existing helper/service/context/timeline boundaries; one service should own
priority and caching for all surfaces. No second player or per-window worker.
The current sources were inspected and match the shipped build manifest.
The helper is 569 lines; isolate persistent protocol/scheduling responsibilities
where that simplifies ownership rather than growing an undifferentiated file.
No `docs/notes/`, `docs/scout/` or imported format coverage matrix exists; research
is under `docs/research/`, and native fixture coverage under `tests/story-002/`
and the eval registry. These, ADR-001/002 and the storage/build runbooks apply.

## Files to Modify

- `src/macosx/VLCThumbnailService.m` (274 lines), `.h` (20): queue/worker lifetime,
  reusable cache, typed outcomes; split focused components if justified.
- `src/macosx/VLCTimelineInteractionController.m` (346): hover intent, pending
  sample presentation, UI cancellation and preference lifecycle.
- `src/macosx/VLCTimelineContext.m` (68): stable media/track context versus
  transient presentation generations.
- `src/thumbnail-helper/thumbnail-helper.c` (569), `PROTOCOL.md` (55): reusable
  protocol, per-request guards, error/status and reusable demux/decode state.
- `scripts/build-thumbnail-helper.sh` (53), `scripts/build-timeline-app.py` (166),
  native patch if required: package new components without a host FFmpeg dependency.
- `tests/story-002/service_contract.m` (191): preserve applicable regressions;
  add focused scheduler/cache/protocol/native cases under `tests/story-004/`.
- `docs/decisions/`, `docs/spec.md`, `docs/evals/registry.yaml`,
  `docs/methodology/state.yaml`, `docs/plan.md`, test runbooks and evidence:
  record decisions, commands, scope and actual results; regenerate graph/index.

## Redundancy / Removal Targets

Per-demand process launch/open/probe, terminate-on-every-hover scheduling,
per-open-only cache keys, duplicate copies of a keyframe for nearby buckets,
unconditional image clearing on pointer movement, and error collapsing into a
single unavailable state. Remove superseded behavior after its replacement is
qualified; retain historic manifests/evidence and prevent parallel schedulers.

## Notes

Cam explicitly requested a **new story** on2026-10-05. This is a follow-up to
Story 002, not a relabeling of its earlier proof: long-lived worker ownership,
proactive scheduling and cross-open persistence change the runtime and validation
contracts. It merits one complete user-facing story; do not split it into
backend-only fragments. Story 003's durable labels remain separate.

Cam's scheduling proposal is adopted as the planning contract: finish bounded
active work, prioritize the latest hover, expand outward in both directions,
and use progressive subdivision/largest-gap coverage when there is no hover.
Cam accepted this refinement and requested implementation on 2026-10-05.
The finite sampling plan and interruption rules make that preference testable.
Persistent thumbnails are a reusable disposable cache, not permanently retained
annotations. Quota eviction or OS/user cache clearing can require regeneration.

## Plan

Cam's 2026-10-05 instruction to start implementation approves the discussed
worker, coverage and cache work. No additional plan approval is needed within
this scope. ADR-003 records the separate cache freshness product choice.

1. Freeze build155231 binary/source evidence under ignored work before changing
   inputs. Declare comparison targets/pointer patterns, bounds and invalid-run
   classification. Small generated fixtures plus existing NAS stage observations
   provide the failure baseline; preserve all later native comparison attempts.
2. Extend thumbnail-helper.c/PROTOCOL.md with reusable version-3 requests, ready
   response, per-operation watchdogs and IO metrics; retain v2 CLI correctness
   tests. Verify repeated out-of-order seeks against v2 pixels/PTS and faults.
3. Add focused scheduler and cache modules with deterministic contracts. Service
   owns one worker, latest hover and finite background coverage; runtime generations
   remain ephemeral. Identity implementation waits for the ADR freshness choice.
4. Update controller/context for proactive readiness and preference lifecycle,
   same-bucket coalescing, truthful nearby images and recoverable states. Preserve
   tracking geometry and accessible slider actions across four adapters.
5. Update build source wiring and test runners; build/sign candidate after helper,
   scheduler, cache and service contracts pass. Run local/NAS baseline/candidate
   preview and controls/playback, restart/media-change/toggle/native surface proof.
6. Remove superseded per-hover cancellation/cache paths, reconcile documentation
   and eval registry, then validate acceptance and mark Done only when proved.

Impact: helper watchdog/cleanup, decoder seek state, cache ownership/invalidation
and controller stale callbacks are the main risks. Dependency libraries and video
files stay unchanged. Keep focused responsibilities rather than one growing file.
Root remains deferred until bookmarks; scoped Story 004 contracts provide proof.
Small scope clarification: reserve background turns for broad coverage while hover
neighbors refine; finite retries/capacity prevent starvation or eviction loops.
No additional external dependency, paid calls or public packaging is planned.

## Work Log

20261005-1030 MDT — Created from Cam's approved NAS improvement direction and
hover-centered scheduling proposal. Verified existing substrate and prior ADRs;
incorporated an independent bounded scheduler/edge-case review. Status Pending;
implementation/eval results remain absent. Next: lifecycle/cache identity gate
and the practical pre-change comparison plan when implementation is requested.

20261005 — Planning validation: focused independent review found no material
gaps against Cam's scheduling, retention and reuse direction. Methodology compile,
validation, whitespace, unique-ID/generated-view and local-link checks passed.
No implementation or runtime result is claimed.

2026-10-05 — Implementation authorized; goal created. Read Ideal/spec/state/graph,
ADR-001/002 and helper/service/context/controller/build/test seams. Story closes
preview responsiveness and playback-quality gaps; deterministic work needs no
product AI compromise. Existing helper/cache/native substrate is sufficient.
ADR-003 selects worker lifecycle and progressive coverage; sampled freshness is a
concrete pending product choice. Main owner integrates persistence and behavior;
bounded low-cost sidecar inventories baseline/testing substrate. No implementation
result, freshness qualification or native regression pass yet.

2026-10-05 — Local implementation and review: persistent v3 worker retains container
state and per-operation guards; guarded stat helper covers blocked metadata calls.
Progressive/hover scheduler, bounded actual-time cache and asynchronous coordinator
are integrated. Demand eviction is allowed; background work stops at capacity.
Review fixes cover cached presentation bypassing decode and current-hover clearing
when an obsolete extraction detects file mutation. Seven-fixture helper regression,
2,835 cache checks, scheduler contracts, 28 service checks and real-helper Cocoa
smoke pass. Signed isolated candidate build180630 succeeded; installed build155231
is unchanged. See docs/evidence/story-004/local-implementation-status.md and scoped
eval story-004-responsive-preview-capability. Native control acquisition is invalid
because the Mac is locked; NAS acquisition is invalid because Movies is absent.
Freshness choice, native four-surface proof and matched playback/performance remain
required. No acceptance checkbox is passed solely from build/local-contract proof.

2026-10-05 — Goal continuation: verified desktop still locked and Movies absent.
Unified panel/service nearby-image distance using the same finite-grid interval,
with bounded 2–60 second limit. Updated stale chronological/Pending plan text.
Final local service suite passes 29 checks; signed candidate180959 builds and
methodology/whitespace checks pass. This is implementation progress, not a native
or NAS pass; cache freshness acceptance and external validation remain blocked.

2026-10-05 — Third consecutive goal-turn blocker audit: CUA again reports the Mac
locked with no native app access; /Volumes again lacks Movies; no freshness choice
has arrived. Previous turn was progress (shared bridge policy, 29 passing service
checks and final signed build), not a verified live-process wait. No build/test job
remains running. Completion remains unproven: native four-surface/preference and
restart delivery, NAS improvement, controls/playback/resource comparisons and the
freshness boundary are still required. Local contract evidence cannot substitute
for them. Further repeated local checks or invented NAS inputs would not advance
those gates. Goal is blocked pending user/external-state changes; story remains
In Progress, installed app unchanged, acceptance not weakened.

2026-10-05 — Cam delegated cache-freshness choice and made the unlocked desktop
available. Selected metadata plus sampled SHA-256 under ADR-003 and explicitly
revised spec with its unsampled-change limitation. Enabled sampled policy; full
verification no longer gates NAS thumbnail delivery. Finder's saved server URL
is used to reconnect Movies after current /Volumes inspection found it absent.
Fresh native/NAS acquisition resumes when mounted; prior invalid attempts retained.

2026-10-05 — Resumed validation: Movies reconnected; sampled candidate built, 29
service contracts pass. Actual NAS AB/BA helper diagnostics show all candidate
requests usable versus two baseline timeouts in first block, with6/6 successful
paired pixel/time matches; source warmth and changed timeout budget remain limits.
Service contention attempt failed one-worker assertion after retry but returned
all images; isolated repeat passes worker reuse, RAM and disk reopen. EOF cleanup
watchdog gap fixed and blocked-close fault proved15.012s. Native CUA preferences
Save/Cancel/restart and seek/volume pass on212257; no native hover or playback
comparison pass yet. Final213341 signed candidate includes teardown fix. See
docs/evidence/story-004/nas-validation-progress.md.

2026-10-05 — Cam authorized the existing native event runner. Two current213341 main-window actual-pointer cohorts pass settled/repeat/rapid-latest and taller-target exit/reentry, with actual-time screenshots inspected; second app launch returns requested samples without decoder reads after proactive cache loading. Fresh20-per-arm controls pass baseline+20%:41.382ms versus40.680ms medians. First cohort invalidated by owner changing a shared runner during collection; retained and excluded. Three60s matched playback pairs are collecting on fresh identities of a274MiB two-hour generated fixture, with background dispatch exposure verified inside the active interval. Hourly loop review recommends continuing native NAS/fullscreen qualification before optimization or closure.

2026-10-05 — NAS validation exposed seconds inside metadata-only checks even after removing redundant file opens. Cam delegated presentation choice; selected immediate current-session RAM image with “Checking source…” while final validation proceeds. Added asynchronous metadata continuations, coalesced RAM/cache validation, a nonrenewing15s deadline and current-context failure clearing/suppression. Fresh opens still require metadata plus sampled hashing; no TTL or stale validated hit. Current222506 build passes39service contracts,2841cache checks and scheduler proof; real helper completes7-target proactive plan in2.448s and reloads coverage with0decodes. Current native NAS10/10 assignments pass: first qualified disk79.8ms from eligible hover, nine RAM provisional images0.38–3.70ms while final checks include1.45/1.68s NAS delays. Source/sample/frozen-input guards pass. Detached/native/custom fullscreen, mainMP4/MKV and CLIoff pass current functional checks; detached covered-window acquisition retained invalid and corrected with a selected-window AX raise. Ordinary-control and fresh matched-playback qualification are collecting; installed daily app unchanged.

2026-10-05 — Final acceptance review against222506:39service/2849cache checks,
seven-fixture35requestv2/v3 parity, sampled identity/blocked-I/O faults and real
proactive7-target/reopen proof pass. Current four native surfaces, mainMP4/MKV,
two NAS10/10 actual-pointer cohorts, visible Checking source and full-app disk
restart with0decoder reads pass. Save/Cancel/off restart/on/CLIoff/seek/volume
pass. Fresh20/arm controls37.925/37.492ms meet +20%; three matched60s playback
pairs with133–140background dispatches pass audio/drop checks; CPU/RSS overhead
reported. Scoped reader-focus proof is inherited because decorative nonkey panel
and original Position/actions remain; fresh actual-reader startup inconclusive.
Recovery/permissions/identity faults are isolated contracts, not forced user NAS
mount changes. Invalid attempts and instrumentation limits retained. Installed
preview app's qualified components match; deep signature and actual NAS image
inspected. No source video/ordinary VLC/annotations modified. See current ledger
for criterion mapping and the distinction from unqualified general claims.

## Central Tenet Verification and Documentation

- [x] Ideal stays implementation-free; ADR003/spec own lifecycle, freshness and compromises.
- [x] Source/video fidelity and separate disposable-cache/durable-label ownership preserved.
- [x] Deterministic bounded modules; existing licensed libav reuse, no product AI dependency.
- [x] Current local/native/control/playback artifacts inspected; scope and failures retained.
- [x] Spec/state/plan/eval/README/AGENTS and generated graph/story index reconciled.

2026-10-05 — /mark-story-done:12/12tasks and10/10acceptance criteria mapped to
current evidence; applicable tenets verified, capability eval recorded, ADR003
accepted, dependency002Done. Methodology compile/validate and whitespace pass.
Story004Done within its declared scope; root awaits003. Requested local app
updated to222506 with previous app preserved; diagnostic launch closed and normal
profile retained. No commit or push performed. Landing state: recommend
/finish-and-push as the next request when Cam wants repository landing.

## Approved correction plan — 2026-10-05

Cam approved the validate handoff plan. Reopen this same story without weakening acceptance. Prior normal-case evidence remains historical/applicable where inputs are unchanged; two adversarial reproductions override complete acceptance.

1. In `src/thumbnail-helper/thumbnail-helper.c`, reject provided native video-count mismatches before selecting any container stream. Add v2/v3 and single-video Matroska regressions. Version `VLCThumbnailService.m` mapping identity so potentially wrong cached images are unreachable.
2. In `VLCThumbnailCache.m`, make meaningful RAM use contribute to safe disk recency and protect hot images against background quota pruning; test passive enumeration and restart under pressure. Cache format need not change.
3. Reconcile stale current documentation. Rebuild/sign using the existing isolated build; run affected helper/cache/service/identity contracts and additional review, then actual selected-track/hover and quota/restart/native-control proof. Replace the local app only after qualification.
4. Revalidate and mark done only after the correction requirements pass. No commit/push or publication.

Delegate disjoint cache implementation/tests to an inherited-model worker; mechanical stale-document reconciliation to gpt-6-luna. Main owns helper/service identity, integration, builds, UI proof and final assessment. The Ideal corresponding-image/privacy/playback goals and ADRs 001–003 remain unchanged. Baselines are both reproducible failures recorded in `validate-20261005.md`; no new AI capability or fixture-format matrix applies. Root remains deferred until bookmarks.

### Work log — correction

20261005 — Reopened under explicit user approval after validation found two correctness gaps. Existing libav helper/cache substrate is sufficient. Files at risk include protocol tests, sampled identity/service restart tests and app provenance. Runtime images are disposable, so a mapping-policy namespace bump is appropriate and does not affect annotations. Cache correction must preserve safe local ownership and avoid touching metadata during passive enumeration.

20261005 — Additional Codex review found the documented Story002 v2 service/cache-fault runners no longer link against the persistent worker/cache/scheduler service. Accepted after source/link-command inspection. Folded into the existing remove-superseded-paths task: explicitly retire incompatible commands, update the active build runbook to current suites, preserve historical v2 test sources/evidence and state that no fresh physical ENOSPC mount trial is claimed. No runtime expansion or new dependencies.

20261005 — Stronger cache-pressure repro after the first correction: a cold quota filler timestamped just newer than a RAM hover still displaces its payload and breaks restart reuse (2877 checks, two failures). Retained at work/validation/story004/cache-newer-background-failure.log. General problem is background cache pollution, not NAS speed. Bounded primary research on RocksDB priority pools supports a small demand-before-background retention tier. Within the approved retention task, record a current-context hover-used set bounded by512samples, including newly decoded demand results; evict ordinary/background entries before those samples and their manifest, with nanosecond LRU inside each tier and the same hard256MiB cap. No new library or cache format. First235648 candidate measurements are retained as intermediate evidence and will not be represented as final corrected-build proof.

20261005 — Approved correction completed and revalidated on signed001728. Mapping-count guard and countguard2 namespace eliminate wrong-track legacy reuse; cache meaningful touches and bounded demand priority survive newer background pressure while enforcing hard256MiB. Same3410-check harness fails9baseline checks (two consequential setup assertions), passes all corrected checks;40service and current packaged count tests pass. Scoped independent/Codex reviews clean after explicit legacy-runner retirement. Final NAS10/10cached images after restart, final20/arm controls37.612/37.635ms(+0.062%), and three matched60s playback pairs with130–138background jobs pass. Only cache.m/.h differ from235648; four-surface/malformed-track/preference/reader proof reused proportionally with limitations explicit. Installed001728exact components/deep signature and normal-profile actual NAS54:01/54:00image inspected;222506preserved. First installed driver rejected by development-only pointer guard retained as invalid acquisition; exact-preview guarded pointer and bounded visible-window placement supplied final normal-profile proof. No source/annotation/defaults/config edits.

20261005 — /mark-story-done:12/12tasks,10/10criteria, alltenets, capability eval and dependency002verified; workflow gates complete. Story004Done under approved correction plan; no remaining same-scope implementation gaps. Root/bookmarks remain separate. No commit/push performed. Landing state: recommend /finish-and-push as the next request when Cam wants repository landing.
