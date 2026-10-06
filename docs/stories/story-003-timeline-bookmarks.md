---
id: "003"
title: "Persistent short labels on the macOS timeline"
status: Pending
priority: High
ideal_refs: [ideal:req:annotations, ideal:req:persistence, ideal:req:navigation, ideal:req:media-integrity, ideal:req:playback-quality, ideal:req:evidence]
spec_refs: [spec:1, spec:3, spec:4, spec:5]
adr_refs: [adr-001-media-metadata-storage]
decision_refs: [docs/decisions/adr-001-media-metadata-storage/adr.md, docs/research/timeline-implementation-plan.md, docs/runbooks/media-metadata.md]
depends_on: ["001"]
category_refs: [spec:3, spec:4]
architecture_domains: [native-timeline, media-identity, durable-annotations]
eval_refs: [root-timeline-experience]
---
# Story 003 — Persistent short labels on the macOS timeline

**Status:** Pending. **Priority:** High. **Depends on:** 001.
Recommended after 002 to reuse its timeline adapter. There is no decoder/cache
runtime dependency: this story can prove bookmark behavior independently. If
started first, create the same shared adapter and let 002 reuse it; do not build
a second UI system. Planning is authorized; implementation has not started.

## Goal

Right-click any point on VLC's actual macOS timeline, enter a brief label, and
find that label at the same moment after quitting and reopening the same video.
Labels are normally **one to three words**. Show their markers and compact labels
when controls appear; hover to read, click to seek, and edit/delete in place.
Deliver durable storage, correct media association and all four native surfaces.

## Eval Ladder Context

Root: `root-timeline-experience`, deferred, never attempted. This story's planned
bookmark capability check comprises the ACs and root fixture/retention matrix;
no child runner exists yet. System SQLite arm64 link and single-process
transaction/revision behavior have been probed; product schema, identity hashing,
restart and UI are unimplemented. Run bookmark proof even if previews are
unavailable. Run the full integrated root once both stories work; independent
store or screenshot success cannot pass it.

## Acceptance Criteria

- [ ] **Compact native interaction:** Right-click captures pointed time, not the
  later playhead. Small single-line editor supports Enter save/Escape cancel,
  Unicode/punctuation, trimming and nonempty validation. No hard three-word
  validator. Main, detached, native and custom fullscreen each support add,
  hover, click-to-seek, edit/delete and ordinary controls reveal/hide.
- [ ] **Visible and accessible:** Ticks and brief labels appear with controls;
  hover exposes full label. Dense/coincident labels remain reachable through
  clustering/selection, never arbitrary selection or silent loss. Keyboard
  add-at-playhead and label list/menu expose seek/edit/delete. Preserve slider
  accessibility role, key handling, focus and ordinary left-drag/wheel actions.
- [ ] **Correct time/navigation:** Persist integer microseconds and stable IDs;
  resize/scaling never changes saved time. Marker seeks meet <=0.5 s arrival
  error on required fixtures while preserving playing/paused state. A successful
  seek request alone is not arrival proof. Endpoints, duration changes and
  unknown/nonseekable input have explicit bounded behavior.
- [ ] **Durable writes:** Acknowledged create/edit/delete survives full app quit,
  relaunch and reopening; repeats after force termination following commit.
  Failure before commit preserves previous data/draft. Interrupted transactions,
  retry, two-instance writes/conflicts, read-only/full store, invalid records,
  corruption and newer schemas never silently overwrite or recreate a catalog.
- [ ] **Media identity:** Same unchanged canonical local file restores labels;
  duplicate basename, different content at same path (including same-size and
  preserved-mtime replacement) do not inherit them. Direct/symlink target opens
  agree; retargeted/broken symlink does not. Special path characters work.
  Copies/moves/renames to another canonical path do not auto-reconnect in v1;
  old labels are retained. Read-only video folders work without adjacent writes.
- [ ] **Race isolation:** Switching/stopping during hash/load/editor/save clears
  old visuals immediately. Stale completions cannot attach or write a new
  video's context. Every edit/save targets its captured identity/revision/time.
  Input-clear and new-input notifications are handled idempotently.
- [ ] **Independent lifetime:** Labels survive >30-entry resume turnover, clear
  recent history, recent-items disabled, and thumbnail eviction/deletion/corruption.
  No automatic missing-file/age eviction. Cache operations cannot open the store
  for writes. Original video hashes and installed VLC/user state remain intact.
- [ ] **Measured responsiveness:** Identity verification runs off-main with bounded
  memory/cancellation and leaves playback responsive. Measure fresh full SHA-256
  cost on short and large fixtures before accepting identity architecture; no
  success claim for unmeasured large-file responsiveness. Once identity is ready,
  restore <=100 ms p95 and commit acknowledgement <=200 ms p95 for 1,000 labels
  per media on the declared local fixture/store. Show pending/failure honestly.
- [ ] **Reproducible and integrated:** Source/patches, schema, fixtures and test
  commands tracked; arm64 isolated app builds and signs. After 002, shared hover
  composes image/time/label and both services pass root together on all surfaces.

## Out of Scope

Paragraph notes, tags/colors, automatic move/rename/cross-path matching, sync,
cloud/uploads, export/import, importing VLC bookmark options, catalog repair UI,
forensic secure deletion, remote/live/DRM media and public release. Do not write
into video files or their folders. No reset-all control is needed for this story.

## Approach Evaluation

| Candidate | Benefit | Cost / proof |
|---|---|---|
| SQLite in Application Support | Transactions, locking, versioning; platform arm64 link verified | Preferred provisional store; schema/fault/concurrency/restart must be built and tested |
| Versioned JSON with locked atomic replacement | Small and inspectable | Must implement cross-process locking, reload/merge/conflict and interrupted-write recovery correctly |
| Existing resume preferences or input bookmark serialization | Existing code access | Wrong retention/escaping/persistence proof; rejected as durable source of truth by ADR-001 |
| Canonical URL + full SHA-256 + size, verified each open | Strong replacement distinction, including preserved metadata | Preferred correctness baseline; reads the whole file and delays labels; measure cost first |
| Canonical URL + metadata/fingerprint or cached digest | Fast unchanged-file lookup | Cannot guarantee detection of every same-fingerprint byte change; any weaker contract requires an explicit ADR/spec decision |

**Simplification baseline:** Native event handling and transactional local state
require deterministic code. AI-only/hybrid inference contributes no capability;
no model calls or model benchmark are needed. Reuse VLC input notifications,
URI access, integer seek, DATA/CACHE roots and Story 002's UI seams. An
`NSURLFileResourceIdentifierKey` alone is not restart-persistent identity.

The first gate measures strict hashing and confirms the selected storage schema.
Record a media-identity/store ADR before broader implementation, including the
loading compromise; ADR-001's accepted storage lifetimes stay unchanged. Do not
silently optimize by trusting metadata or by hashing only part of the file.

## Tasks

- [ ] Recheck disk headroom and isolated app/store roots; coordinate shared UI
  files with 002. Existing build and SQLite library are verified prerequisites.
- [ ] Establish legal fixture identity cases and measure cancellable full-file
  hashing on short/large media with paired playback baseline. Record size,
  storage, cache state, elapsed/CPU/memory and label-availability cost; accept
  or revise the identity proposal explicitly before implementing the store.
- [ ] Record identity/schema/concurrency/migration ADR; define versioned schema,
  validation, SQLite connection settings, bounded busy handling and durable-ack
  semantics. Capture returned pragmas, not merely issued SQL.
- [ ] Implement read-only canonical URL/content identity with before/after file
  checks and path revalidation; generation-guard hash/load completion. Do not
  hash on position ticks. Missing/changing input fails closed and preserves data.
- [ ] Implement serial store, parameterized transactions, revision conflict
  checks, idempotent retry, activation reload, schema/corruption protection and
  shutdown drain. Support injected test roots and IO errors.
- [ ] Implement annotation coordinator with immutable marker snapshots and
  captured editor context; handle input switch/clear/duration changes explicitly.
- [ ] Implement compact editor and timeline context menu, labels/markers,
  overlap chooser, hover composition, precise seek, keyboard menu/list and AX
  actions. Reuse/create the shared timeline-only geometry adapter.
- [ ] Wire windowed/detached and separate fullscreen panel adapters. Validate
  real pointer/context/keyboard behavior in native and custom fullscreen early;
  selected-window capture alone did not expose the floating panel in feasibility.
- [ ] Add meaningful tests for schema/identity/races, two-process contention and
  optimistic conflicts, interrupted writes, corrupt/newer schema, retry and
  cache/store confinement. Simulate full disk; never fill the host disk.
- [ ] Run native end-to-end restart/seek/edit/delete and complete retention/
  identity matrix; verify source hashes. Check failures visibly preserve draft
  and committed data. Record a force-quit-after-ack trial separately from clean quit.
- [ ] Measure UI/commit/restore/identity/playback budgets with the declared
  fixture set; run integrated root after 002, including cache churn during
  save/load and media switches. Update registry with actual attempts/limitations.
- [ ] Remove temporary/duplicated UI or persistence paths; update spec/state,
  ADR/runbooks and evidence. Apply patches to pristine pin, build/sign/check
  dependencies, run `make validate` and `git diff --check`, then `/validate`
  and `/mark-story-done`. Commit/push only on request.

## Architectural Fit

Owning areas: `VLCMediaIdentity`, `VLCAnnotationStore`, annotation coordinator
and shared timeline presentation. State spec:3 has accepted storage ownership
but no product schema/store; spec:4 has baseline UI only. No game coverage matrix,
web server or imported Python driver applies. Root fixture table owns coverage.

Pinned `VLCInputManager.m:248` clears/attaches inputs and can send two notifications;
position updates are throttled ~100 ms, while length changes require explicit
handling. `VLCCoreInteraction.m:455` requests integer-time seeks but does not
prove arrival. `src/darwin/dirs.c:123` gives bundle-scoped DATA/CACHE roots.
Large controllers (`VLCInputManager` 766 lines, core interaction 1,312, fullscreen
564) should receive thin hooks; hashing and SQL belong in separate files.

Proposed contracts and schema are in the [synthesis](../research/timeline-implementation-plan.md).
Foreign keys, stable UUIDs, integer times and revisioned updates cross store/UI
boundaries. UI snapshots are published only for the current media generation.
A save may finish for its captured old media after switching, but cannot update
new media's markers. Scope is unchanged local files, not continuously rewritten
media. Full hashing remains a measured tradeoff, not a claim of instant restore.

## Files to Modify

- `src/macosx/`: proposed media identity, annotation store/coordinator/editor
  and shared timeline context/presentation files; keep responsibilities separate.
- `patches/vlc-3.0.24/`: input lifecycle/duration, common controls, fullscreen
  controller/XIB, application termination, menu/keyboard wiring and SQLite link.
- Existing target sources `VLCInputManager.m`, `VLCControlsBarCommon.m`,
  `VLCFSPanelController.m`, `VLCMain.m`, related XIBs and `Makefile.am`; only
  necessary touch points, not a replacement of core bookmark/resume facilities.
- `tests/`: identity/store/transaction/race contracts; generated fixture and
  isolated-store recipes. `docs/evidence/story-003/` captures actual attempts.
- Spec/state, eval registry/root contract, media-metadata runbook, schema ADR
  and any shared apply/build scripts established by 002.

## Redundancy / Removal Targets

Do not duplicate 002's geometry/hover controller or make a second durable store
in preferences/core bookmark options. Preserve existing VLC bookmarks/resume
behavior; no legacy migration without a future explicit contract.

## Project Tenets

- [ ] Preserve original media, private notes and installed VLC.
- [ ] Pin identity/schema/evidence; never claim persistence from a screenshot.
- [ ] Measure identity latency before accepting a responsiveness compromise.
- [ ] Separate durable labels from cache/history and main-thread UI work.
- [ ] Verify actual restart, failure, fullscreen and accessible navigation.

## Workflow Gates

- [ ] Substrate inspected and implementation plan/identity-store ADR recorded.
- [ ] Applicable implementation authorization recorded.
- [ ] Build complete: implementation finished, required checks run, summary shared.
- [ ] Validation complete or explicitly skipped by user.
- [ ] Story marked done via /mark-story-done.

## Blocker Summary

N/A. No proved blocker; identity latency is the first measured decision gate.

## Blocker Evidence

N/A.

## Unblock Condition

N/A.

## Plan

1. Measure full-hash latency/playback impact and select the identity/store ADR.
2. Build and fault-test identity/store/coordinator, then deliver the complete
   compact native label interaction through the shared adapter on all surfaces.
3. Prove restart, replacement, retention, accessibility and performance; after
   002 run integrated root. Validate and close only against recorded evidence.

## Work Log

20261004 — Created at Cam's request for separate thumbnail/bookmark stories.
One-to-three-word intent retained without inventing a hard word-count limit.
Pinned lifecycle, path/seek seams and platform SQLite probe reviewed. Stronger
agent reviewed durability/race semantics; main owns the proposed plan. No
feature code, schema or real annotation store created. Separate story warranted
by durable writes/identity/restart contract, independent of image-cache success.
