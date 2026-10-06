---
id: "005"
title: "Open-source contribution (Story 002b)"
status: Pending
priority: High
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity, ideal:req:evidence]
spec_refs: [spec:1, spec:2, spec:4, spec:5]
adr_refs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services, adr-003-persistent-thumbnail-preparation]
decision_refs: [docs/research/upstream-contribution-scout.md, docs/decisions/adr-001-media-metadata-storage/adr.md, docs/decisions/adr-002-native-thumbnail-services/adr.md, docs/decisions/adr-003-persistent-thumbnail-preparation/adr.md, docs/evidence/story-004/current-acceptance-ledger.md, docs/runbooks/build-vlc-macos.md]
depends_on: ["002", "004"]
category_refs: [spec:1, spec:2, spec:4, spec:5]
architecture_domains: [upstream-integration, native-timeline, thumbnail-decoding, thumbnail-cache]
eval_refs: [story-002-preview-capability, story-004-responsive-preview-capability]
---
# Story 005 — Open-source contribution (Story 002b)

**Status:** Pending — ready for Phase 1 investigation. **Priority:** High.
**Depends on:** completed Stories 002 and 004. **Precedes:** Story 003 bookmarks.

Cam calls this **Story 002b**: contribute thumbnails before building bookmarks.
The tracker uses its next numeric ID, 005, without renumbering existing stories.
This is one story with three phases. The initial planning scout is evidence for
its first gate, not a completed contribution audit.

## Goal

Offer VLC a useful native macOS timeline-preview contribution that fits its
current architecture, conventions and maintenance expectations. Own the research,
refactoring, tests, documentation and review follow-through so maintainers can
evaluate a focused, well-supported change. Be willing to replace local
implementation choices to achieve that fit. Learn upstream patterns before
implementing bookmarks, then carry those patterns forward.

Scope includes Stories 002 and 004: native hover, honest frame/time correspondence,
preferences, responsive preparation and safe reusable caching. A coherent series
of smaller merge requests is welcome; do not silently drop the NAS fixes or rely
on unpublished private machinery. Acceptance is a maintainer decision.

## Eval Ladder Context

The local thumbnail stories are Done on qualified build 001728. Their ledger
records bounded native/NAS, cache, control and playback evidence plus inherited
reader checks and remaining limitations. Those results do not qualify a port.
This story adds upstream integration, independent reproduction and external review
as a distinct validation boundary. Re-run affected preview capability checks on
the selected upstream baseline and candidate. The integrated root stays deferred
until bookmarks exist; a successful MR cannot pass that root.

## Acceptance Criteria

### Phase 1 — Investigate and choose an upstream approach

- [ ] **Contribution map:** Record dated primary sources for the canonical repo,
  target branch, submission route, code/style/ownership conventions, commit and
  patch structure, licenses, supported builds, tests/CI, localization,
  accessibility and any explicit AI-assisted contribution policy. Distinguish
  written rules from conventions inferred from accepted macOS changes. Missing
  policy or inaccessible review history stays unknown.
- [ ] **Architecture and product fit:** Pin the target; check existing timeline
  issues/MRs, native controls, core thumbnail/preparser and media-library services.
  Compare reuse, a small extension and retaining our helper through a minimal
  local proof. Resolve track/time/transform, lifecycle, caching and preparation
  contracts. Identify separate FFmpeg work if needed. Produce a gap matrix with
  source, current behavior, proposed change and verification for each material gap.
- [ ] **Reviewable plan:** Record an upstream-integration ADR and concrete patch
  or MR-series plan, including removals and tests. Resolve major architecture
  uncertainty before broad porting. Where direction from maintainers is needed,
  present a concise problem, useful example and focused design question through
  their documented channel. Record feedback; do not assume interest or approval.

### Phase 2 — Improve, integrate and prove the contribution

- [ ] **Native fit:** Use the selected branch's APIs, build system, naming,
  Objective-C/C style, memory/thread ownership, logging, settings, localized
  strings and accessibility patterns. Preserve normal controls and playback.
  Remove parallel decoder/cache machinery where native services meet the contract;
  justify any remaining extension/dependency. Update ADR/spec decisions explicitly.
- [ ] **Independent reproduction:** A clean checkout of the upstream base plus
  our submission builds through documented upstream commands without the ignored
  local workspace or host-specific scripts. Include build integration, legal
  fixture generation and license/attribution records. Check the actual upstream
  OS/architecture matrix through available local builds and CI; report unavailable
  coverage. Every dependency is available to maintainers.
- [ ] **Strong verification:** Relevant upstream tests/CI and meaningful new
  regressions pass; independent review has no unresolved material findings.
  Verify actual native hover and ordinary controls on each supported control
  surface, preference lifecycle, keyboard/VoiceOver, context races, selected-track/
  PTS/rotation correspondence, restart/freshness/corruption/eviction, worker failures
  and local/slow-NAS behavior. Use reproducible legal fixtures. Compare matched
  pre-change/candidate controls, playback and resources with a prospectively
  documented practical protocol. Retain the baseline-median +20% ordinary-control
  allowance unless explicitly revised with cause. Report new preview delay
  separately; disclose overhead, failures and uncertainty. Freshly qualify changed
  paths and justify any inherited evidence.
- [ ] **Maintainer-ready package:** Focused commits, useful messages and correct
  attribution; no unrelated cleanup, local methodology scaffolding, app binaries,
  private media/paths/NAS addresses. Provide motivation, architecture/tradeoffs,
  a small shareable demonstration, build/test commands and results, limitations
  and a patch-series map. Reproduction must not require reading our development
  diary. Verify licensing and any required author/sign-off claims; never invent
  attestations. Review the exact public diff before submission.

### Phase 3 — Submit and shepherd

- [ ] **Submission:** Open the contribution through VLC's official process against
  the chosen target. Record public URL(s), base/head revisions, dependencies and
  readiness status. Check CI/discussion on the submitted revision. A draft for
  design feedback is clearly labeled and does not satisfy ready-for-review gates.
- [ ] **Follow-through and disposition:** Track each actionable reviewer/CI request
  to a change, evidence or reasoned response. Fix issues, rerun affected checks,
  keep the branch current and summarize revisions. Follow project norms for commit
  updates and follow-up cadence; avoid noisy nudges. Record merged commits or an
  explicit decline/alternative route. An open MR or silence remains pending. If
  declined or waiting indefinitely on direction, bring Cam a concrete recommendation;
  do not silently mark success or begin bookmarks. Record conventions and accepted
  architecture for Story 003. Non-merge closure requires Cam's decision on scope
  and sequencing.

## Out of Scope

Bookmarks, new history/privacy features, public binary releases, a guaranteed
merge, unrelated VLC cleanup and a permanent fork commitment. Preserve the working
local preview app and original media during upstream experiments.

## Approach Evaluation

| Approach | Benefit | Required evidence |
|---|---|---|
| Current development branch with existing core thumbnail services | Maintained APIs and potentially less custom machinery | Actual frame time, selected track, lifecycle, caching/preparation and NAS proof |
| Small extension to an existing core service | Shared capability and less macOS-only maintenance | Demonstrated API gap, appropriate ownership, cross-platform impact/tests and direction for a material API change |
| Narrow helper or stable-branch contribution | Reuses locally proven code | Upstream branch/architecture fit, failure of simpler reuse options against concrete requirements and independent dependency/build proof |

The local 3.0.24 ADRs explain the current app, not an obligation to impose that
architecture upstream. Current development source has relevant thumbnail and hover
infrastructure; existence is not behavioral equivalence or a performance result.
Choose from proof and maintainer guidance, not sunk cost.

**Simplification baseline:** Reuse VLC's deterministic facilities first. Product
AI inference/model benchmarking is irrelevant. The discriminating experiment is a
minimal native timeline request through the upstream service with known-frame
local and slow-storage fixtures, checked against our correctness/lifecycle contract.

## Tasks

1. **Investigate:** Audit official guidance and representative accepted macOS
   patches; pin the target. Check related work and contributor account/identity
   requirements. Compare our source, prototype minimal service reuse and record
   the ADR, gap matrix and commit plan. Inspect current CI/build definitions.
2. **Improve:** Check disk headroom and use an isolated upstream checkout. Port
   the smallest complete native experience, remove superseded paths, add native
   regression coverage and reproduce the build independently. Run targeted upstream
   checks and relevant native proof. Review correctness, resource bounds,
   maintainability, licenses, localization and accessibility; fix material findings.
3. **Submit and shepherd:** Prepare the exact public commits and MR description,
   submit through the confirmed route, attach review links, track feedback/CI,
   implement and verify revisions, record disposition and bookmark handoff. Set a
   concrete follow-up cadence when an actual review exists; no empty monitor now.

Update research, ADRs, spec, evidence and current state as facts change. Run
`make methodology-compile` and `make validate` for local docs; they do not replace
VLC tests. Update eval records when ported capability results exist. No imported
Python/AI/coverage infrastructure is needed for this native project.

## Workflow Gates

- [ ] Phase 1: contribution map, target pin, gap matrix, minimal reuse proof and
  integration ADR/patch plan; unresolved maintainer decisions explicit.
- [ ] Phase 2: independent build, native/automated proof, independent code review
  and exact public package meet the readiness checklist.
- [ ] Phase 3: submission/review have an honest disposition; bookmark handoff is
  recorded, with Cam deciding any non-merge path.
- [ ] `/validate` completed on final scope; `/mark-story-done` records completion
  without equating local tests or submission to upstream acceptance.

## Blocker Summary

N/A. Investigation is actionable. Target/API acceptance, account permissions and
CI availability are gates to verify, not assumed facts or established blockers.

## Blocker Evidence

N/A.

## Unblock Condition

N/A.

## Architectural Fit

- **Owners:** upstream native macOS interface and thumbnail facilities; a core/API
  owner where a demonstrated gap requires shared change.
- **Methodology:** spec:1/spec:5 lead; spec:2/spec:4 preserve the preview contract.
  Local feature substrate exists; upstream readiness is unproven. Pending means
  Phase 1 is actionable, not that a port is already buildable.
- **Contracts:** actual sample time, media/track isolation, bounded background work,
  disposable cache ownership and private original media. Replacing ADR-002/003
  mechanisms needs an explicit decision. Durable label identity stays separate.
- **Size review:** current helper 783 lines, service 461, interaction controller
  368, cache 259, worker 193, scheduler 183. Review the large helper's ownership
  and readability; these are observations, not upstream line limits. Inventory
  destination sizes and style at the pinned target before editing.

## Files to Modify

Exact upstream paths follow the target audit. Known local inputs/likely changes:

- `src/macosx/VLCThumbnail{Service,Worker,Cache,Scheduler}.{h,m}` — adapt or retire
  against upstream service/cache ownership.
- `src/macosx/VLCTimeline{Context,InteractionController}.{h,m}` and geometry header
  — integrate current native controls and context.
- `src/thumbnail-helper/thumbnail-helper.c` and `PROTOCOL.md` — potential removal
  from the upstream package, or justified integration if retained.
- `patches/vlc-3.0.24/0001-native-timeline-previews.patch` (242 lines) and private
  FFmpeg Matroska patch — historical inputs, not presumed upstream deliverables.
- Upstream build lists, resources/localization, preferences and tests — enumerate
  exact paths during Phase 1, including core paths only where needed.
- Local test/fixture scripts, research, ADRs, evals and build runbooks — retain
  portable reproduction without copying the whole project into the VLC MR.

## Redundancy / Removal Targets

Private helper/IPC/metadata-check and custom cache paths if upstream facilities
meet their requirements; host-only build repairs, debug hooks and duplicate
compatibility code from the contribution. Preserve qualified source/evidence in
history. Do not remove correctness guards merely to shrink the diff.

## Notes

A new story is warranted: ownership/success changes from a locally qualified app
to an upstream contribution with independent reproduction and external review.
Stories 002/004 retain their completed scoped evidence. Cam explicitly requested
investigation, improvement, submission and shepherding before bookmarks. Acceptance
cannot be promised on VLC's behalf.

## Plan

Start with the [initial scout](../research/upstream-contribution-scout.md). Complete
Phase 1 and its minimal proof, then record concrete target-file changes and commit
boundaries at the ADR gate. Cam clarified that the current request is scout and
story planning only. No implementation, maintainer contact or upstream submission
occurred during creation. Story003 waits for this contribution's disposition or
Cam's explicit sequencing change.

## Work Log

20261005 — Created from Cam's three-phase request. Inspected completed local
feature, ADRs, source footprint and generated graph; performed an initial upstream
planning scout and placed contribution before bookmarks. No upstream build/port
proof claimed.

20261005 — Planning validation: generated story index/graph includes unique ID005
and Story003's sequencing dependency; `make methodology-compile`, `make validate`
and `git diff --check` passed. Planning files only; no runtime validation claimed.
