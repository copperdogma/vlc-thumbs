---
id: "006"
title: "Story005 sub-story: concise, consistent upstream review package"
status: Done
priority: High
ideal_refs: [ideal:req:previews, ideal:req:evidence]
spec_refs: [spec:1, spec:5]
adr_refs: [adr-004-upstream-preview-integration]
decision_refs: [docs/decisions/adr-004-upstream-preview-integration/adr.md, docs/evidence/story-005/user-validation-20261009.md, docs/research/upstream-contribution-scout.md]
depends_on: ["002", "004"]
parent_story: "005"
category_refs: [spec:1, spec:5]
architecture_domains: [upstream-integration]
eval_refs: []
---
# Story006 — Story005 reviewer-package polish

## Goal

Finish the concrete editorial and structural preparation of Story005's upstream
contribution: consistent current commit messages, a short useful introduction,
clear patch dependencies and straightforward reproduction instructions. Reduce
review effort without weakening functionality, hiding limits or speculating about
maintainer preferences. Cam explicitly requests this child task on2026-10-09 and
asks for focused, efficient modifications without endless testing.

This is a bounded sub-story within Story005's submission preparation, not a new
product feature or a substitute for its remaining submission/review phase.
The parent remains InProgress. The child depends on the already-qualified parent
slice, not completion of parent Phase3; its graph prerequisites are002/004 to avoid
a circular dependency. No AI-capability eval ladder applies; existing native
product validation remains owned by Story005.

## Verified starting point

Current package: `patches/vlc-master/contribution-series-source10/`, thirteen
patches,72 source paths, combined tree `b7c0f24e442c35a57bb108d56b801fd05b624943`,
base `2e358f3098c2f2b7621d1dc568de8b61ad786322`. It contains approximately10,860
added lines across the serialized series, including tests/docs and overlapping
changes. Largest review units add4,695 and3,671 lines. This is a substantial
review even though our project's larger development-journal commit is not the
upstream submission.

Directly inspected problems:

- `feature-series/proposed-commit-messages.md` opens with obsolete NOT READY/stage
  labels and refers to helper77 as historical although current qualification is
  recorded. Its current README links it as submission supporting material.
- Cover, overview, prerequisite README and draft description repeat long
  qualification paragraphs and internal stage/cohort terminology.
- Eight prerequisite repairs and five feature patches span several concerns.
  P0006/7 use feature-created tests; component lists are not independently
  buildable submissions. The canonical interleaved order is documented, but
  review boundaries and why each repair accompanies the feature need a simpler
  explanation.
- Public reproduction instructions mix ordinary build/test steps with optional
  GUI identity isolation. The full uninterrupted public recipe is unexecuted;
  ordinary commands passed in stages and complete conventional distcheck passed
  separately. These are distinct facts to retain accurately.

## Acceptance Criteria

- [x] **Current subjects/messages:** Provide thirteen concise draft subjects and
  messages in canonical order, each explaining its problem, resulting behavior
  and relevant tests/dependency. Remove obsolete status headers and source-stage
  narrative from current-facing drafts. Match actual patches; retain attribution,
  notices and AI disclosure; invent no authorship/sign-off attestations.
- [x] **Short entry point:** Cover description leads with user benefit and a
  compact implementation/ownership explanation. One review map connects each
  logical concern to patches, important files/interfaces and relevant tests.
  Replace duplicated validation prose with one concise table plus links to exact
  limits. Current-facing text requires no understanding of our internal phases,
  source rounds, cohorts, safety receipts or development diary.
- [x] **Explicit dependencies and concern boundaries:** Separate feature purpose
  from prerequisite purpose in the review map. For every prerequisite, state the
  concrete defect/reason for inclusion, actual dependency and qualified scope.
  Distinguish logical review groups from independently applicable/buildable
  stacks. Assess whether an inexpensive packaging/test-only adjustment can remove
  a concrete dependency; make it only if beneficial and narrowly provable.
  Otherwise preserve canonical order and explain the constraint plainly. No
  requirement to split every repair into a separate MR or shrink code to an
  arbitrary line count.
- [x] **Simple reproduction:** Put the ordinary pinned-base apply/build/check/
  distcheck route first. Move optional GUI isolation and host-specific details
  into a separate section. Every command must map to the actual build contract
  and preserved evidence. Distinguish commands already executed, the unexecuted
  uninterrupted sequence, optional skips and unavailable coverage without making
  maintainers decode trial histories. No ignored local harness may be required
  by the public build route.
- [x] **Evidence-led standards assessment:** Check changed submission materials
  against existing dated primary guidance and actual source conventions. Cite
  any concrete unmet written requirement. Unknown reviewer tastes, predicted
  objections and lack of endorsement are not defects or completion blockers.
  Existing related work may be linked as context, with no inferred preference or
  compulsory architecture negotiation. Do not promise upstream acceptance.
- [x] **Preservation and closure:** Default scope changes documentation and
  manifests only. Preserve all thirteen patch bytes, source-tree identity,
  fixture/demo provenance, qualified app and behavioral limits. Any actual
  patch/dependency change needs an explicit delta and affected-consumer check,
  not inherited whole-tree claims. Record a concise validation report and update
  parent links/current status; keep historical snapshots and raw receipts intact.

## Tasks

- [x] Rewrite the current cover, description and thirteen draft commit messages.
- [x] Explain prerequisite defects, review groups and actual dependencies.
- [x] Put ordinary reproduction first and optional GUI isolation in an appendix.
- [x] Consolidate validation facts and preserve useful limits.
- [x] Refresh manifest artifact hashes; check unchanged patches/source identity,
  links, shell syntax/equivalence and generated records once.
- [x] Record focused validation, close this child and update the parent handoff.

## Plan

Two SOL6.1 medium writers own disjoint document groups. Root owns manifests,
acceptance judgment and closure. The first writes cover/description/messages/
prerequisite map; the second writes overview/reproduction/limitations. Root updates
hash bookkeeping only after both groups finish, then performs one integrated
artifact check. The selected ADR004 mechanism is unchanged. No fixture coverage
or eval-ladder movement; this is submission documentation, not product behavior.
No new approval dependency: Cam explicitly approved execution of this story.

Default patch order is retained. P0006 depends on the feature context-test source;
P0007 depends on feature-created macOS regression/build scaffolding. Extracting
that scaffolding would create another changed qualification boundary for limited
presentation benefit. A clear map is the efficient correction; separately
buildable prerequisite stacks are not claimed.

## Execution plan and stop conditions

1. Read the current package and dated standards record once; make a short list
   of concrete inconsistencies, redundant sections and real dependencies.
2. Rewrite messages, cover/overview, review map and reproduction sections in one
   coordinated pass. Use existing project patterns and ADR004; retain the
   selected helper architecture. Prefer a clear map over unnecessary patch
   rearrangement.
3. Apply at most one narrow dependency-packaging improvement if analysis proves
   an actual benefit. Otherwise document the existing coupling and proceed.
   Do not redesign product architecture merely to anticipate a reviewer taste.
4. Run one focused validation pass. Fix concrete findings, then recheck only the
   affected documents/commands/artifacts. Allow one corrective editorial round;
   if a new material runtime issue appears, record and route it explicitly rather
   than expanding this task into an open-ended diagnostic loop.
5. Stop once the criteria are met and remaining limits are stated clearly. Report
   the changes and why they reduce review work. No upstream contact/submission,
   new app installation or architecture expansion belongs to this child task.

## Proportional validation

- For docs/manifests: inspect every changed current-facing claim/link and its
  evidence, verify patch/demo hashes and exact application order/tree pins, check
  manifest consistency and run `make methodology-compile validate` plus scoped
  whitespace checks. Preserve meaningful raw unified-diff/log whitespace.
- Reuse applicable full normal checks, helper77, conventional distcheck,
  native/playback and reader evidence; editing prose is not grounds to repeat
  them. No VoiceOver onboarding, hover marathon, performance cohort, exhaustive
  platform campaign or test-framework addition.
- For changed shell instructions: check syntax, environment assumptions and
  equivalence to the executed commands. Run a single affected command smoke only
  where needed to resolve a concrete discrepancy. Retain the uninterrupted-route
  coverage limit unless actually executed; do not manufacture a new full-build
  quota merely to simplify the wording.
- If patch order or test ownership actually changes: one static apply/tree
  comparison and the smallest build/test covering the affected intermediate
  consumer. Broaden only for an evidenced runtime/build dependency change.
- Review test purpose/maintainability at touched boundaries; remove redundant
  tests only when their unique failure coverage is demonstrably retained. Add no
  implementation-mirroring tests or tests for wording changes.

## Files to modify

Primary: current package `CONTRIBUTION.md`, `feature-series/README.md`,
`feature-series/proposed-commit-messages.md`,
`feature-series/contribution-description-draft.md`, `feature-series/LIMITATIONS.md`,
`blocker-prerequisites/README.md`, the linked demonstration README and affected
manifests only. Demonstration images and capture provenance stay byte-exact.

Supporting: `patches/vlc-master/README.md`, parent Story005, this story,
`docs/plan.md`, `docs/methodology/state.yaml`, generated graph/index and one concise
new validation record under `docs/evidence/story-006/`. Existing source/build/test
files are outside default scope; touch only for the narrowly justified dependency
adjustment described above. Do not rewrite historical package directories.

## Architectural Fit and removal targets

ADR004's selected native hover/current-player owner, retained helper, cache and
normal contrib/build integration remain unchanged. This advances spec:5 and the
Ideal's inspectable evidence by making the selected contribution understandable.
It neither changes media/storage contracts nor introduces a new ADR decision.
Remove stale current-stage labels, duplicated validation paragraphs and mandatory
reading of historical transcripts. Keep meaningful limitations accessible.

## Workflow Gates

- [x] Build complete: bounded packaging modifications and dependency map finished.
- [x] Validation complete: one focused pass and affected corrective checks recorded.
- [x] Story marked done via `/mark-story-done`: child criteria met; parent still
  owns actual upstream submission and review disposition.

## Blocker Summary

None for the default documentation scope; current package and evidence exist.
Inaccessible live wiki pages or unknown reviewer preferences do not block use of
available dated primary guidance. A newly found concrete written-rule violation
or required source change must be recorded with evidence and its smallest fix;
never silently weaken a mandatory acceptance gate.

## Work log

20261009 — Created at Cam's request after candid package reassessment. User rules
out speculative reviewer-preference objections and requests focused modifications
without endless tests. Status Pending: concrete substrate and bounded criteria
exist; implementation has not started. No product change, contact or submission.

20261009 — User explicitly sets Story006 as goal and authorizes execution. Explore confirms current29 artifacts/13 patches, stale messages and repetition; ADR004/spec:1/5 alignment retained. Root pins baseline artifacts and splits disjoint docs to two SOL6.1 medium writers. Product/patch/app bytes remain outside edit scope; ordinary recipe must use current feature-enabled flags, not historical lean disable-macosx recipe. No runtime qualification loop.

20261009 — Small coherent editorial delta: the linked demonstration README carried the same obsolete NOT READY stage banners. Root removes those banners, retains screenshot scope/provenance and the existing generation command unchanged. Root also corrects the review-map distribution entry from include/Makefile.am to the three actual modules source lists. No patch/product/test change.

20261009 — Build and focused validation complete; /mark-story-done closes child006. Seven reviewer Markdown files and three manifests changed;29 artifacts/13 unchanged patches, two images, provenance and source identities preserved. Central table,13 messages, prerequisite defects/dependencies and ordinary-first reproduction are current. Four Bash syntax blocks/38 links/artifact hash checks pass; optional GUI block exact and enabled flag equivalence demonstrated. Root corrective pass fixes source-list map and cover length. See docs/evidence/story-006/validation.md. Existing product evidence reused; no new tests/runtime. Whole Story005 remains InProgress for submission/review. Landing state: local changes; recommend finish-and-push as the next request.

20261009 — Cam invokes validate, fixes and finish-and-push after the brief app smoke. Findings-first root and independent documentation reviews find no material defect. Fresh artifact/hash/link/syntax/flag/methodology checks pass; scoped smoke playback/pause/seek/resume and normal Quit pass, hover not reverified. Closeout authorization wording updated; no code/patch change or runtime campaign. Child stays Done; land project repository only, parent Phase3 still pending.
