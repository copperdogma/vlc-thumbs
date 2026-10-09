---
id: "005"
title: "Open-source contribution (Story 002b)"
status: In Progress
priority: High
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity, ideal:req:evidence]
spec_refs: [spec:1, spec:2, spec:4, spec:5]
adr_refs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services, adr-003-persistent-thumbnail-preparation, adr-004-upstream-preview-integration]
decision_refs: [docs/decisions/adr-004-upstream-preview-integration/adr.md, docs/research/upstream-contribution-scout.md, docs/decisions/adr-001-media-metadata-storage/adr.md, docs/decisions/adr-002-native-thumbnail-services/adr.md, docs/decisions/adr-003-persistent-thumbnail-preparation/adr.md, docs/evidence/story-004/current-acceptance-ledger.md, docs/runbooks/build-vlc-macos.md]
depends_on: ["002", "004"]
category_refs: [spec:1, spec:2, spec:4, spec:5]
architecture_domains: [upstream-integration, native-timeline, thumbnail-decoding, thumbnail-cache]
eval_refs: [story-002-preview-capability, story-004-responsive-preview-capability]
---
# Story 005 — Open-source contribution (Story 002b)

**Status:** In Progress — Phases1/2 complete at the disclosed bounded scope in [current source10 verification](../evidence/story-005/current-source10-final-verification.md). Final reviewer package checker PASS; halt ready for owner review before submission. Platform and preview-visible reader coverage remain unmeasured; shutdown cause remains owner-deferred. Phase3 remains untouched. **Priority:** High.
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

- [x] **Contribution map:** Record dated primary sources for the canonical repo,
  target branch, submission route, code/style/ownership conventions, commit and
  patch structure, licenses, supported builds, tests/CI, localization,
  accessibility and any explicit AI-assisted contribution policy. Distinguish
  written rules from conventions inferred from accepted macOS changes. Missing
  policy or inaccessible review history stays unknown.
- [x] **Architecture and product fit:** Pin the target; check existing timeline
  issues/MRs, native controls, core thumbnail/preparser and media-library services.
  Compare reuse, a small extension and retaining our helper through a minimal
  local proof. Resolve track/time/transform, lifecycle, caching and preparation
  contracts. Identify separate FFmpeg work if needed. Produce a gap matrix with
  source, current behavior, proposed change and verification for each material gap.
- [x] **Reviewable plan:** Record an upstream-integration ADR and concrete patch
  or MR-series plan, including removals and tests. Resolve major architecture
  uncertainty before broad porting. Where direction from maintainers is needed,
  present a concise problem, useful example and focused design question through
  their documented channel. Record feedback; do not assume interest or approval.

### Phase 2 — Improve, integrate and prove the contribution

- [x] **Native fit:** Use the selected branch's APIs, build system, naming,
  Objective-C/C style, memory/thread ownership, logging, settings, localized
  strings and accessibility patterns. Preserve normal controls and playback.
  Remove parallel decoder/cache machinery where native services meet the contract;
  justify any remaining extension/dependency. Update ADR/spec decisions explicitly.
- [x] **Independent reproduction:** A clean checkout of the upstream base plus
  our submission builds through documented upstream commands without the ignored
  local workspace or host-specific scripts. Include build integration, legal
  fixture generation and license/attribution records. Check the actual upstream
  OS/architecture matrix through available local builds and CI; report unavailable
  coverage. Every dependency is available to maintainers.
- [x] **Strong verification:** Relevant upstream tests/CI and meaningful new
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
- [x] **Maintainer-ready package:** Focused commits, useful messages and correct
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

1. [x] **Investigate:** Audit official guidance and representative accepted macOS
   patches; pin the target. Check related work and contributor account/identity
   requirements. Compare our source, prototype minimal service reuse and record
   the ADR, gap matrix and commit plan. Inspect current CI/build definitions.
2. [x] **Improve:** Check disk headroom and use an isolated upstream checkout. Port
   the smallest complete native experience, remove superseded paths, add native
   regression coverage and reproduce the build independently. Run targeted upstream
   checks and relevant native proof. Review correctness, resource bounds,
   maintainability, licenses, localization and accessibility; fix material findings.
3. [ ] **Submit and shepherd:** Prepare the exact public commits and MR description,
   submit through the confirmed route, attach review links, track feedback/CI,
   implement and verify revisions, record disposition and bookmark handoff. Set a
   concrete follow-up cadence when an actual review exists; no empty monitor now.

Update research, ADRs, spec, evidence and current state as facts change. Run
`make methodology-compile` and `make validate` for local docs; they do not replace
VLC tests. Update eval records when ported capability results exist. No imported
Python/AI/coverage infrastructure is needed for this native project.

## Workflow Gates

- [x] Phase 1: contribution map, target pin, gap matrix, minimal reuse proof and
  integration ADR/patch plan; unresolved maintainer decisions explicit.
- [x] Phase 2: independent build, native/automated proof, independent code review
  and exact public package meet the readiness checklist at the disclosed bounded
  scope in [current source10 verification](../evidence/story-005/current-source10-final-verification.md).
- [ ] Phase 3: submission/review have an honest disposition; bookmark handoff is
  recorded, with Cam deciding any non-merge path.
- [x] Fresh `/validate` completed at disclosed bounded scope: [owner test delivery validation](../evidence/story-005/user-validation-20261009.md), grade B. No confirmed material current product defect; stale documentation and historical package routing corrected.
- [ ] `/mark-story-done` records whole-story completion after phase3 disposition, without equating local tests or submission to upstream acceptance.

## Current readiness and retained limitations

Phases1/2 are locally complete at the disclosed bounded scope in
[current source10 verification](../evidence/story-005/current-source10-final-verification.md).
Whole-story completion remains pending Phase3. Fresh `/validate` is complete at disclosed scope; see the owner test delivery validation.

### Historical submission-checklist correction

The following earlier assessment and raw failures are preserved; current source10
verification supersedes their readiness conclusions.

Phase1 remains complete. Phase2 is reopened for the reviewer-improvement candidate and the corrected submission-standard assessment. The official VLC Sending Patches checklist requires error-free `make check` and complete `make distcheck` when files are added. Preserved failures do not meet those requirements; no maintainer waiver or green CI is known. The contribution is prepared for maintainer review with an incomplete submission checklist, not ready to submit. The prior validation conclusion is superseded while its raw evidence remains preserved. Phase3 remains unauthorized and unchecked.

Controls20/arm pass (+3.464%, within20%). Six matched60s playback intervals retain zero paired lost-picture change and complete digital-audio coverage. The133ms candidate screenPTSgap is an observation hole, without demonstrated feature-attributable stall; no uninterrupted-video claim. Independent288 counted native tests (one optional-volume skip), helper77 and separate ENOSPC proof pass. Distcheck remains80pass/5skip/7fail, with bounded attribution, not a green whole build. Unavailable architectures/OS and actual VoiceOver activation remain explicit.

Candidate007 actual hover on four surfaces, media/track/rotation, preference/restart, source failure/replacement and ordinary controls combine with finite002 physical main/custom gestures and custom continued playback. Unchanged shared actions justify ordinary-control inheritance. Main strict seek completion, detached precision/drag and actual reader navigation remain unqualified; no new exhaustive gesture matrix is claimed. See [native closeout](../evidence/story-005/native-edge-closeout-002.md).

### Shutdown finding

One of six performance parents exited-11 during SIGTERM shutdown; five exited0. The exact crash remains preserved (SHA2566ba3b2bb4ed11761c66fc1e9d8a55610127210abca301c7c59ccbed14bd83b08). Static UPnP worker/pool offsets align but runtime image identity and exact causality are unproved. Absence of owned processes does not establish clean exit.

Independent source review proves an unchanged upstream GetMediaSource owned-reference leak: the GUI wrapper adds a hold without releasing the original owned result, preventing normal services-discovery destruction. A complete baseline verbose trace confirms UPnP services activation without its close, while renderer discovery closes and later cleanup proceeds. This corroborates an activated pre-existing lifetime hazard and supports carrying it as a baseline limitation outside this focused patch. It does not fix or conclusively exonerate the candidate crash. Sampler, short publicAPI host, LLDB and fresh-vmmap protocols remain inconclusive; no live-worker/UUID/quiescence proof is claimed. See [sanitized attribution](../evidence/story-005/shutdown-baseline-attribution.md).

Approved cleanup was limited to12 exact targets. Preserve the1GiB reserve and original media. No more runtime, cleanup, commit, push, contact, submission or bookmarks are authorized by this handoff.

## Plan

2026-10-08 scoped correction001: root-reviewed controller-owned bottom-bar/per-view-coordinate correction, exact pre-edit backup and source-extracted AppKit check only, within fresh00:29:21–00:59:21Z release. Full build requires>=5GiB; diagnostic implementation/native qualification remain held. No story completion or Phase2 readiness claim. See [evidence](../evidence/story-005/autohide-correction001.md).

**Current implementation:** the completed comparison selected ADR004's retained
helper route. The [frozen master port plan](../evidence/story-005/feature-port-plan.md)
supersedes the earlier conditional experiment steps below, fixing native/context/
protocol/cache/dependency ownership and exact tests. Prototype core patches were
preserved then reversed exactly from the integration source, which returned to the
clean pin before builders began the feature. Existing outputs are not automatically
evidence for the new source; all changed components require fresh build receipts.

### Current authorization and staged technical gate

**Historical execution gate, 2026-10-09T00:47Z (superseded by current source10 verification):** Evening continuation after disk relief; exclusive computer use authorized from2026-10-09T00:30Z with no end specified. Prior usage and per-check bounds retained; Phase2 OPEN. Performance006 failed capture completion; one corrected private observer qualification007 then failed pre-t0 with155 complete screen frames and zero audio bytes. Route STOP, no benchmark verdict or further runtime released. Reader foreground proof remains absent, actual VoiceOver OFF, human foreground question pending. No production source/public/install/cleanup/contact/submission/commit/push changes. Qualification007 is a capture-tool setup failure, not measured silence or a VLC performance regression. Current playback and preview-visible reader proof remain mandatory; no Phase2 acceptance change. See [terminal record](../evidence/story-005/evening-continuation-20261008.md).

**Historical diagnostic021 capture and wrapper milestone, 2026-10-08:** Diagnostic021 run002 SETUP FAILED/zero captures; run003 CAPTURED_ROOT_REVIEW_REQUIRED:33 captures/three unique images spanning44.2069s show controls+preview, but Documents permission prompt confounds the result and actual AX fullscreen-button return differs from historical Escape. No fade-fix, acceptance or ordinary-Quit claim. Independent visual/trace receipt2cfa5260… and terminal audit0033b89da… preserve source72/apps/prior evidence. Reviewer-wrapper successor static checker PASS:29 artifacts/13 patches/two PNGs unchanged, introductory prose4423→2462 words (44.3% shorter), aggregate`cb17ba51b172f9b9bfc1a283d4f4e01a3b7b6ef4e24d9f1205e03d46c1a91249`; remains NOTREADY/Phase2 OPEN. Audio-only metadata isolation+compile released, no runtime or seed; reader/new022 preparation held. Goal ACTIVE/open, prior usage preserved;07:33 hourly review recorded/next08:33Z, hard stop13:19:04Z. No acceptance/source/public-package/install/cleanup/contact/submission/commit/push changes.

**Historical diagnostic007 initial closeout, 2026-10-08:** Diagnostic007/021 derivative build PASS; actual runtime FAILED before hover on the120s root-bridge expiry (126.426538s terminal), zero moves/captures and no returned-main or ordinary-Quit proof. Distinct unintended CUA relaunch PID36853/helper36862 opens default state and stalls; SIGTERM does not stop them, then root sends exact-owned SIGKILL and both are absent. This is no product crash or ordinary-Quit claim. Independent terminal audit verifies prior four apps/36 namespaces/source72/qualified021 app exact and original trial PIDs28561/28579/29246 absent; prior failed receipts/logs remain unchanged. See `work/story005-autonomous-diagnostic021-plan007/terminal-independent-audit001.json` (SHA`b79c33afbbf84ad4af1ff0bec534c6e148496fb35882f1d79d62c5e5debb9e0e`). Self-contained owned-PID successor is PREPARATION ONLY, no new runtime released. Audio/performance route remains TERMINAL/no retry; reader unqualified. Goal ACTIVE/Phase2 OPEN, prior usage preserved, hard stop13:19:04Z/next review07:33Z; no acceptance/install/cleanup/contact/submission/commit/push changes.

**Historical diagnostic006 closeout, 2026-10-08:** Diagnostic006 derivative build PASS:11 commands, strict baseline35-section/UUID equality,997 files/10 links/398 loadables, two translation units/dependencies/signatures/observer verified without weakening the gate. ONE autonomous runtime fails BEFORE hover: PID91946 SIGABRT−6 during ONE CUA fullscreen-button action; stderr NSInvalidArgumentException `-[VLCWindow videoViewController]` traces S005Diag→showControls→hasBecomeFullscreen. The diagnostic unchecked cast causes this abort; it is distinct from historical shutdown004 and establishes no product019/source10 crash. Zero pointer moves/captures, no returned-main or normal-Quit proof. Root terminal-preservation001 verifies all three old apps/30 namespaces/020 app exact; read-only terminal audit confirms parent91946 absent and current executable-resolved scan finds no VLC/vlc-preparser/vlc-timeline-preview processes. No pre-crash helper identities were retained, so individual owned-helper absence cannot be retrospectively qualified; no universal absence claim. Original006 and earlier002 target/003 OSO-UUID/004 include-compile/005 SDK-guard failures remain immutable. Build worker prepares007 with class guard/new021 identity ONLY; root review required before build/runtime. Audio/performance route remains TERMINAL/no retry; reader unqualified. Goal ACTIVE/Phase2 OPEN, prior usage preserved; seven-hour stop13:19:04Z,06:33 review performed06:32:39Z/next07:33Z. No acceptance/product/public-package/install/cleanup/contact/submission/commit/push changes.

**Historical execution gate, 2026-10-08T06:19:04Z:** Cam explicitly grants exclusive computer use for seven hours,06:19:04–13:19:04Z; prior goal usage is preserved, goal ACTIVE/Phase2 OPEN and blocked audit reset. Root corrects the earlier human-availability prerequisite for ONE instrumented autonomous returned-main020 diagnostic: established native pointer warp+post+persistent query and the retained physical negative support this bounded method. New plan002 is PREPARATION ONLY pending root review before build/runtime; old held001 expired at06:15:55Z and remains preserved. No source fix, fade-cause or readiness claim. Audio-ACK route remains TERMINAL/independent SETUP FAIL requiring systemic audit, with no private-harness repair/retry; cohort002 remains zero eligible arms/no audio or performance verdict. Reader remains unqualified. Source10, prior apps/evidence, public13/stage015 and checked NOTREADY reviewer snapshot remain preserved. Next hourly review06:33Z; no acceptance changes/install/cleanup/contact/submission/commit/push. Authorization: `work/story005-seven-hour-20261008-061904/authorization.json`.

**Historical execution gate before the seven-hour release, 2026-10-08:** Audio-ACK diagnostic independently FAILED SETUP: baseline app_activeTRUE thenFALSE with unchanged geometry; observer never launches, no ACK/channel evidence/t0/measurement. Caller/cohort exit0 is inherited false success from empty AssertionError text tested by `if failure`, not PASS; no repair/retry. BaselineSIGTERM0, preparser15534/cohort15520 absent,100 pins/apps/source72/current019 namespace preserved. Audio route TERMINAL/systemic audit needed; no more private-harness/tool-repair/runtime release. Cohort002164-video/0B-audio/zero-arm/no-verdict and diagnostic-only startup readiness remain unchanged. Returned-main fade unresolved/reader unqualified. Checked local reviewer snapshot NOTREADY:29 artifacts/13 patches/two historical PNGs exact, aggregate539e266…, checker0/fresh identity/source-public-stage015 preserved. Diagnostic app HELD pending human availability/root review, latest admission05:50:55Z/stop06:15:55Z; no human answer inferred. Phase2/goal OPEN/no acceptance changes/submission/contact/install/cleanup/commit/push.

**Historical execution snapshot, 2026-10-08:** Fresh performance comparison SETUP FAIL before media/visible baseline binding, zero collected arms/no performance verdict. ONE019 custom-fullscreen hover PASS33.164s/root41 frames/human stationary hold; returned-main NEGATIVE across43 frames: preview/seek bar persist15.686s but ordinary button row/title fade in40–42 despite human stationary confirmation. Cause unknown/no fix. Trial78337 exits0 via SIGTERM cleanup, sampled helpers absent; source/app/media exact, no ordinary-Quit claim for this trial. ONE reader attempt stops before activation/media/VoiceOver enable on observer identity guard PID66309, zero captures/no reader proof; root observes actual VoiceOver OFF in System Settings/no settings changes. Distinct baseline-only read-only diagnostic terminal3.559s/one coherent active/nonhidden presentation snapshot/readiness observed, no media/activation request/scoring and no playback PASS; original setup failure remains unexplained. Baseline comparison OPEN/zero arms; root prepares one fresh matched cohort after a material readiness discriminator, no performance claim or further human checks released. Earlier paused-main019/ordinary-Quit and staged-public fragment proofs remain scoped; full public recipe UNEXECUTED. Phase2/goal OPEN, no source fix/new GUI; next review05:33Z/overall stop06:15:55Z/no submission/contact/install/cleanup/commit/push.

**Historical execution snapshot, 2026-10-08T04:53Z:** Root reviews three fresh source10 Performance1/2/3 metadata isolations PASS6.158s:997 files/10 internal links,398 sections+UUIDs and397 whole-file bytes, nine commands/deep-strict signatures, owned PID/PPID/PGID absence. Source019/baseline012/source72/prior preferences preserved; minimum free approximately8.65GB, no GUI. Provenance SHA`234f95379ee70f04e7d9f8b0adf2247825e3463ab781e76bcba7249e1a1c7dfd`. Fresh matched playback/resource comparison REQUIRED because clock/GL/lifetime changes affect applicability; root accepts only narrow old20/arm paused healthy shared-action inheritance. Runtime/pointer compilation HELD for root review; fullscreen/reader held pending human availability, with a fresh readiness question sent around04:42Z. Reader protocol diff review complete, system baselineNULL/no settings reads or actions. Earlier staged public-host PASS and original failures remain preserved; full public recipe UNEXECUTED. Phase2/goal OPEN, next review05:33Z/overall stop06:15:55Z; no submission/contact/install/cleanup/commit/push.

**Historical execution snapshot, 2026-10-08T04:40Z:** The retained public normal-host remaining literal check PASS in221.952973s/supervisor0: registered6/30(29pass1optional skip)/25/94 and GUI smoke1/1, originalTRSPASS/noFAIL-ERROR. Published fragment commands now complete across interrupted stages, not one uninterrupted full public recipe; full recipe UNEXECUTED. Prior plan001/002 failures remain failed and immutable; changed text/stubs/stub_helper does not establish code equivalence or product defect. Actual retained binary/fullInfo/plist/flags/four production hashes and original-baseline source/normal018/tools preservation exact; PGID35729 absent, minimum free7,424,864,256B. Source10 normal/full77/dist/package/isolation/relocation and ONE paused-main019 physical hover/ordinary quit remain qualified within recorded scopes. Phase2/goal OPEN; fullscreen/reader/return-main held pending human availability and root review. Next review05:33Z/overall stop06:15:55Z; prior usage preserved, no submission/contact/install/cleanup/commit/push.

**Historical execution snapshot, 2026-10-08T04:16Z:** ONE paused main-window physical hover PASS: Cam confirms stationary hold/no click-drag and controls/seek bar/thumbnail stayed visible; root verifies all42 capture hashes/all12 unique images, selected17–41 spans24.719132s. Pointer02:55/Keyframe02:54 burn-in174.000/4176 remains stable while mainpaused01.083/26 and RCtime1 stay unchanged; cursor glyph later hides. ONE CUA Command-Q exits0/noSIGTERM, parent26665 and sampled helpers26689/27427 absent. Source/app/media/preserved inputs exact. Preserve failed018 preactivation observer identity and failed019110s qualification guard; distinct retained019 qualification PASS3.194s. Stage01529-artifact checker PASS; public-host attempt fails during configure after41.344s on allocation-observer lstat of a deleted conftest*.o.tmp. No fragment make/relink/check/GUI executes; fragment/full recipe UNEXECUTED. Preservation exact/ownedPGID19506 absent; GUI lease released, not a native runtime release. Fullscreen/return-main proposal held pending human availability and root review; no retry. Phase2/goal OPEN pending final readiness assessment; no historical cause/fullscreen/reader/seek-accuracy claim. Original native900s window ends04:17:29Z, next loop review04:33Z, overall stop06:15:55Z. No submission/contact/install/cleanup/commit/push.

**Historical execution snapshot, 2026-10-08T04:00Z:** Source10 full normal/helper77/complete conventional distcheck PASS. Original package018 validator failure remains preserved; distinct independent normal-package and isolated018 all398/signature/resource qualification PASS, followed by two-fixture relocated-helper PASS. Native018 read-only preflight PASS; runtimeFALSE/human availability UNANSWERED. Old017/stage14/public13/history exact; no physical hover/fade-fix or Phase2 completion claim. Goal/Phase2 OPEN within the existing three-hour continuation ending06:15:55Z, prior usage preserved. Next hourly loop review04:33Z. No submission/contact/install/cleanup/commit/push. See [source10 qualification](../evidence/story-005/source10-qualification001.md).

**Historical execution snapshot, 2026-10-08T03:35Z:** Cam explicitly grants three additional hours ending06:15:55Z; prior eight-hour/45minute usage remains preserved. Root scouts/plans/coordinates and SOL6.1-medium agents build. Source10 applies only three named-double helper temporaries on source9's autohide correction. Fresh fullnormal and helper77 pass; root-reviewed thirteen-patch composition matches72 current source files. Complete conventionaldistcheck is running; package018/helper relocation and physical mainhover remain pending. Source9/017 and all prior evidence are preserved; source9 qualification does not qualify the changed helper. Human availability is unanswered and is distinct from time authorization. Keep Phase2/goal incomplete. Same5GiB full-build admission/1GiB physical reserve; no install/cleanup/contact/submission/commit/push. Hourly03:33 review complete, next04:33Z if active. See current readiness ledger and blocker-resolution loop.

**Historical eight-hour execution gate:** Cam explicitly resumes the loop including all previously named blockers and requests an active goal. Root scouts/plans/coordinates; SOL6.1medium agents build. Start2026-10-07T02:01:51Z; maximum8h, hourlyloop-review03:01:51Z. Prior halt/no-more-diagnostics superseded for fullmakecheck/distcheck, actualshutdownfault, freshcurrentapp/native/reader and attainableplatform qualification. Preserve revision11/installedapps/originalmedia and1GiBfloor; no contact/submission/commit/push/additionalcleanup. Concreteboundedplans in [blocker-resolution loop](../evidence/story-005/blocker-resolution-loop.md); mandatory requirements remain unchanged.

**Historical evidence, 2026-10-07T06:54Z:** Coherent freeze8 covers72 paths with clean fresh source confirmation. Full normal009 build/check and complete conventional010 distcheck pass, including final cleanup; fresh016 normal app packaging/all398 loadables/helper relocation pass. Native001 AX setup and002 activation stop before media/Quit. Owned SIGTERM cleanup exits0, but loaded normal Quit is unqualified. Root desktop inventory confirms Mac locked; manual unlock requested. Keep strong-verification/maintainer-ready package unchecked, public11 unchanged and promotion held. Historical crash causality, reader/current native and Intel/olderOS gaps remain; no submission/contact/commit/push/installed change. See current readiness ledger and blocker-resolution loop.

**Previous execution snapshot, 01:41 (superseded by resume below):** resource hold cleared after the approved cleanup and
explicit resume. Phase1 is complete. The independent feature app artifact, helper
77/custom-AVIO checks, portable warm NAS comparison, and final registered suite
(288 counted tests, one optional skip, zero failures) pass within their scopes.
Actual ENOSPC passed separately. The separately reviewed source-header manifest
prerequisite fixes archive compilation. Distcheck then fails7 of92 runtime tests;
bounded attribution and source-guide/package reconciliation are complete. Preserve
that result; no runtime repair or weaker test gate is inferred. Existing
product sources remain unchanged. Native proof is partial and held by the
Mac lock, with manual unlock, alternate hover-input permission and final attribution
still pending. Keep the1GiB reserve; no further cleanup is authorized.

Cam now requests completion of tasks/phases 1 and 2 and an explicit halt when the
contribution is ready to submit. Root owns scouting, planning and integration
judgment; SOL 6.1 medium agents own actual building. This supersedes the prior
story-creation-only restriction. No upstream contact, submission, push, public
binary release, bookmark implementation or change to the installed preview app
is part of this run. No author/sign-off attestation will be invented.

1. **Pin and baseline (S):** inspect canonical GitLab metadata and current source,
   using the official GitHub mirror for the isolated checkout at
   `work/upstream/vlc-master-story005`. Both currently resolve master to
   `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Record contribution conventions,
   accepted examples and competing work in `docs/research/upstream-contribution-scout.md`.
   Run the unchanged upstream macOS build into a new ignored output with a disk
   reserve. Builder owns this checkout's generated tools/contrib/build artifacts
   and `docs/evidence/story-005/baseline-*`; preserved 3.0 workspaces are read-only.
   Done means exact provenance, build outcome and baseline test availability.
2. **Discriminating proof (M):** compare native preparser callbacks, selected ES
   identity, picture PTS/orientation, per-request input lifetime and cache ownership
   against the existing feature contract. Root freezes a small experiment before
   assigning a builder; no broad port until this selects an honest architecture.
   Candidate seams are `include/vlc_preparser.h`, `src/preparser/`,
   `test/src/preparser/thumbnail.c`, macOS `VLCPlaybackProgressSlider`,
   `VLCPlayerController` and `VLCLibraryImageCache`. Record failures as evidence;
   no old3.0 runtime result qualifies master.
3. **Integration decision (M):** write the gap matrix, upstream ADR and exact
   disjoint patch ownership after the experiment. Open MR !7493 already proposes
   macOS hover previews and issue #29393 describes shared preview infrastructure;
   inspect both before choosing complementary work. If a material maintainer
   decision is essential and cannot be resolved from published direction, record
   the concrete question and bring that blocker to Cam without contacting upstream.
4. **Implement and qualify (L, conditional on technical gate):** SOL builders
   integrate the selected complete behavior and portable regressions. Root reviews
   correctness and exact public diff, coordinates independent review and fresh
   native surfaces/preferences/track/time/transform/NAS/restart proof, and preserves
   the prospective baseline-median +20% ordinary-control comparison. Record measured
   preview delays and resource overhead separately. A clean reproduction plus
   contribution package is required before declaring submission readiness.

**Historical discriminator, 21:06 (superseded by ADR004 selection):** stop experimental 0004; do not expand into general
MP4 repair. Finish the already-bounded selected-track tests. Compare the story's
retained-helper option using isolated FFmpeg 9 source/contrib: compile the existing
helper, minimally adapt APIs if necessary, verify known frame/time/rotation/SAR,
trim and signed-CTTS behavior, persistent forward/backward requests, sampled
freshness and reordered selected-track identity against master. Keep playback
libraries and qualified source untouched; private dependency changes must have
reproducible source/configuration and license evidence. Cap scratch growth and
preserve the 1 GiB reserve. This is the explicitly planned alternative proof, not
a selected architecture or an authorization to weaken readiness. Root owns its
decision; SOL 6.1 medium agents build and independently inspect source semantics.

The work closes the Ideal preview/evidence/playback gaps through maintainable
upstream integration. It respects spec:1's native macOS/local-media scope,
spec:2's keyframe-first and sampled-freshness compromises, ADR-001 storage lifetime,
and ADR-002/003 behavioral contracts while allowing replacement mechanisms. The
root remains deferred pending bookmarks. Product AI evaluation and the imported
format coverage matrix are inapplicable; use native VLC tests and legal fixtures.

Structural risks are the large private helper, host-specific build/dependency
paths, callback ownership, shared-core blast radius and parallel upstream work.
Delete redundant helper/cache paths only from the proposed upstream package once
replacement behavior is proved; preserve qualified local source/evidence. Local
methodology files never enter the VLC patch. Build metadata or documentation checks
do not substitute for native proof. The next detailed port plan remains conditional
on the research/prototype gate rather than a commitment to an unverified design.

## Work Log

### 2026-10-08 — Diagnostic006 build pass and pre-hover abort

Diagnostic-only build passes strict baseline gate; runtime aborts in the unchecked diagnostic cast during fullscreen entry before any hover measurement. Source10/product019 crash behavior and historical004 causality are not established. Original006 preserved;007 class-guard/new021 preparation awaits root review. See current gate and source10 qualification for scope; next review07:33Z/hard stop13:19:04Z.

### 2026-10-08T06:19:04Z — Explicit seven-hour autonomous continuation

Exclusive computer authorization permits preparation of ONE instrumented returned-main020 diagnostic using established persistent native pointer input; root reviews before build/runtime. Old held001 and all failed audio/reader/performance evidence remain unchanged. No result or acceptance claim; goal/Phase2 OPEN, prior usage preserved, next review06:33Z/hard stop13:19:04Z. See the current execution gate and authorization receipt.

2026-10-08T00:53:03Z — Cam resumes the goal after another project frees space; fresh available space6.4GiB clears5GiB build admission. This continuation ends01:53:03Z and does not reset prior clocks or goal usage. Root reviews/co-ordinates SOL6.1 medium builders: normal017 from the one-file correction, fresh source9, actual controller compilation/linking, complete package/loadable/signature/helper provenance, then one single-instance physical main-hover check with capture armed before entry. Existing016/R8/revision13 and all apps/media/history are preserved; new fullcheck/distcheck remain pending. Product-first proof changes the tested implementation; no causal attribution to the earlier fade is assumed. Instrumentation remains a separate reviewed fallback after a negative result, not an upfront product change. Continuous1GiB reserve; no cleanup/install/contact/submission/commit/push. Plans: `work/story005-autohide-build017-plan001/PLAN.md` and `work/story005-autohide-native017-plan001/`.

### 2026-10-07 — Physical hover comparison001 closeout

ONE unchanged016 paused300s before-hover arm only; strict sameURI pause4/time1 brackets pass. Cam reports working transient hover and whole playback-controls/seekbar fade; eight independent PNGs missed the transient, so steady-hover proof is unqualified rather than a proven no-hover failure. Companion empty Home65651/CUA selection and focus ambiguity qualify the human observation; no static product defect or earlier playing-case explanation. No fullscreen/returned-main/VoiceOver/replay. Human ONE Command-Q exits owned48713 zero/noSIGTERM, parent/sampledpreparser/helper absent. Later actual trigger receipt independently reconciles retained raw missing-at-closeout-receipt failure. Root separately closes companion65651 once without post-exit AX query; readonlyps reports no remaining VLC executables, prior CUA auto-relaunch probable not proven. Source72/app016/fixture/1000 historical files exact;1GiBfloor retained. Revision13 unchanged, no new patch cycle; Phase2 qualification unchanged. Docs-only closeout, nothing further released. [Report](../evidence/story-005/physical-hover-compare001.md).

2026-10-07T22:46Z — Cam authorizes final focused UI gaps and maintainer package closeout, stopping before submission. Ideal playback/evidence and spec1/4/5/ADR004 align; no new architecture or AI eval. Root reviews exact existing-tool native and outgoingpackage plans; SOL6.1medium owns preparations/building, root nativeUI/judgment.60min ceiling23:46:45Z,1GiBfloor, no rebuild/newdiagnostic/sourcefix, preserve existing apps/media/profiles/history/public11. Unknown004 useraccepteddeferred. Planned narrow nativeproof: customfullscreen return→mainhover, actualreader leavePosition/reachordinarycontrol while previewvisible. Finalpackage exactsource/dependency/license/attribution/privatepath review; no upstreamcontact/commit/push/install/cleanup.

2026-10-07T22:32Z — Cam approves the proposed small baseline/candidate seek and normal-Quit comparisons, and accepts deferring deeper intermittent shutdown work absent a concrete discriminator. Aligns with Ideal playback-quality/evidence, spec1/4/5 and ADR004; no architecture/source change or AI eval applies. Root owns scouting/plan/UI/judgment, SOL6.1medium prepares compact existing-tool plan before runtime. Maximum45min through23:17:09Z, at most3 trials/arm alternating, first pair main paused exposedpercentage versus actualtime and two settled native seeks. Baseline equivalence must be disclosed; no failure-rate or causality inference from a small clean cohort. Continuous1GiBfloor/no build, preserve VO OFF/apps/media/profiles/source/history/public11. No cleanup/contact/submission/commit/push/install.

### 2026-10-07 — Small main seek and normal-Quit comparison

Cam approved the bounded comparison and accepts deferring004 causality. Two actual trials only: baseline012 and separately reviewed candidate016. Stable pausedmovie/AXpercentage correspondence, ordinaryPlay, two nativeCUA midpoint actions perarm and>5s decoded/core advancement pass. Both expose stalecontrols afterCUA actions; inheriteddragflag explanation remains a hypothesis. Baseline normalCommandQ exits-11/noSIGTERM with exactUUID015 ResizeNotify/logging pattern, distinct from004conditionwait. Cohort ends; separately reviewed candidate1 normalCommandQ exits0/noSIGTERM. Parent/sampledpreparser absent; all72source bytes/modes/bothapp/history pins/resourcefloors exact. No productfix, build, instrumentation, publicpromotion or further runtime; VoiceOver OFF. Scope/geometry/eventdelivery/latency/platform/package limitations remain explicit. [Comparison report](../evidence/story-005/seek-quit-comparison001.md).

### 2026-10-07 — Reader002 scoped physical VoiceOver validation

**Scoped reader002 closeout, 2026-10-07 (separate reader-only authorization after the 20:43Z loop ended):** Cam’s physical VoiceOver input on unchanged candidate016 demonstrates main-window Position navigation, leaving Position for Pause, and ordinary pause/Play. The paused spoken 5.5% matches exposed slider value 0.05534079456701875; it does **not** match burned-in 38.417 seconds of the 7200-second fixture, and does not qualify progress accuracy or precise seeking. Two paused images retain 38.417/frame922 and typed pause; physical Play produces human-witnessed whole, easily understandable 1.3/1.4/1.5% announcements, advancing images 109.000/frame2616→207.167/frame4972, and typed play. Root’s one Command-Q exits0 without SIGTERM; owned parent and sampled preparser/helper are absent, with no matching new crash report at inventory. Source72 bytes/modes, app016 manifest, fixture and 703 historical files remain exact. VoiceOver is OFF, welcome checkbox1 restored, scripting0 unchanged, and the reader process is absent. Visible-preview navigation, fullscreen reader behavior, seek precision and a streaming-announcement fix remain unqualified. Historical shutdown004 remains unresolved; Phase2 and the original goal remain open/blocked, public11 unchanged, and this is not ready-to-submit proof. Earlier assessments below are preserved history.

[Final receipt](../../work/story005-native016-reader002/final-receipt.json) · [Settings restoration](../../work/story005-native016-reader002/root-reader-settings-restored.json).

20261006-1727 — Actual2320 fixed-region calibration8cases pass: botharms setup/right/left, strict1792×912 region/600000CLI, independent570/350 and oldcenter, taggedrouting/frameclocks, emptynegative and unfocusedrefusal. Occlusionstage fails expectedrefusal because actualAXhit remainscandidate-owned; no occluder was established, so preserve failedfixture without claiming guardbypass orocclusionpass. Stop33.876s; all owned/sampledapps/preparsers absent. Remaining originallyplanned absenttargetrefusal completed once against actualretired28609 afterfreshpsabsence: expliciterror/nonzero,zero posted/routed,absenceafter. Receiptf08af15f, no apprelaunch/replay. Nine scopedcases qualify, notfull10casepass. Independentreview supports foreground/unoccluded visible-controls20/arm cohort with unchanged paused-rendered-knob metric, classifier/phaseAX/routing/clocks/+20% criterion and explicit occlusion/defaultfade/seekcompletion limits. Builder preparescompactfrozenc.acquire wrapper only, no further calibration replay.

20261006-1727 — Applied reviewed isolatedprocesspath correction exactly3ddae9a5; newadapterfreeze514c01f7 changes onlydevelopmentplaybacksource, preserves68e6/source/nativebinaries/publicseries. ExplicitProcessSnapshotError rawidentity evidence persistsbeforecleanup;14identity+6persistencemockedchecks andindependentreviewclear. Fresh1740 caller133aae98/pland9fbe1b5/19pins closesapply. Actual1740 baselinecentral6s PASS: t0within0.428s ofobserverbegin,145movingROIhashes/600RMSwindowsnonebelow−60, video decode/display+145 and audio/play+71, zero reportedloss/gap/captureerrors; rootvisuallyinspected actualbaselinePNG confirmsROIinsideknownmovingvideo. Candidate011 startup/play passes but actualAXbarwidth594 vs prospective548.5 triggersgeometrySTOP beforecandidatecapture/cachebins. Total17.414s, owned31536/32264 and sampled31538/32278/32338 absent. No comparison/score/retry;011consumedpreserved. Read-onlygeometry/state sourceaudit precedes any successor. No production/publicpatch/nativebinary change.

20261006-1720 — Actual2316 visible-controls calibration establishes baseline setup/right/left (independent570/350 and old570 precheck) under the exact shared600000ms CLI. First candidateinitial saved PNG is1840×912 instead of required1792×912 despite ownedCG/AX896×456 geometry: root inspected a visible correct01:09/Keyframe01:08 preview extending48 rasterpixels left of mainwindow. Stop17.9395s; no candidate response/remainingcases/scores/retry. All owned apps and sampled preparser/helper identities absent (19626/19628/20019/20021/20166). Preserve receiptaffe19d3/originals. Bounded capture-extent diagnosis compares platform -l selectedwindow/childunion with exact physicaldisplay -R ownedrect; no resizing/cropping originals or classifier relaxation. Builder prepares a minimal source-backed fixed-region successor only.

20261006-1719 — Actual1730 shortplayback setup stops3.952s before observer on frozenprocess_snapshot exactapp-path comparison, after baseline startup/play/geometry/savedvideoPNG. Baseline12231/preparser12233 absent;011 remains unlaunched and cache absent; no8s/centralinterval/audio/cache/score proof. Read-only existingVLC PID comparison reproduces Darwin nonfinalcomm truncation to15chars; -ww doesnotfixthatcolumn, while finalcomm and SDKlibproc proc_pidpath returnfullpaths. Original1730psraw was notretained, so mechanism is applicable/reproduced, not contemporaneous exactcause. Isolated collector fix uses numeric/UID/start fields with argvlast and authoritative libproc exactpaths, retains only target/directchild diagnostics, and tests failclosed identity/selection behavior. Root requests explicit failure-evidence persistence beforecleanup and newfreeze; no frozen/public source or runtime retry yet.

20261006-1717 — Three-round strategiccheckpoint: aligned but repeated transient-control capture setup is a local-minimum risk. Actual2311 baseline-right independently passes center570/evaluate336.945ms unscored; postread strictpaused/source/time/AXPosition unchanged. Following leftpre capture1.344s later has no controls, so STOP after11.283s; noleftobserver/candidate/remainingcases/scores. Owned89586/preparser89588 absent. Preserve runtime-receipt9492efde and originals. Reuse primary pinned source comparison: mouse-hide-timeout is milliseconds/default1000, macOS converts integerseconds min1, no explicit max, gates controls/titlebar/cursor hiding without changing seek/play actions or directworker/cache settings. Choose identical prospective600000ms visibility configuration covering entire<=600s control cohort, replacing reveal choreography. Keep180/3000observer, independentPNG/routing/clocks/20responses/median+20% unchanged; disclose visible-controls scope and possible prolonged hover-presentation eligibility. Defaultfade remains separate. Builder prepares compact fresh successor only. Nextstrategiccheckpoint1747 or three substantive rounds, whichever first.

20261006-1717 — Root and independentreview clear frozen shortplayback1730 driver79c7b9bb/plan3b39af5a,15offlinechecks/19pins and actualfresh runtime/socket/011cache. Release ONE unscored baseline012→candidate0118s capture/central6s applicability to sole nativeowner. Actualaudio/frame/timebase coverage, exactsource/counters, coldUID-safe cache/worker/protocol4/opaquev5key consistency and inside-bin growth required. Source/contextID is not independently recomputed; same6s cadence baseline. Active85s/cleanup35s budget has an explicit expected-descendant assumption; caller120s bound required. NoPause/seek/hover/retry or scoredcohort. Root will inspect actualsavedvideoPNG/ROI afterrun, not claim modelvisualgate inside selfcontainedrun. Controlbuilder offline/disjoint, no concurrentUI.

20261006-1714 — Root and independentreview clear fresh2311 control successor: driver4766a81c/plan3d77d6f2,45 mocked checks, exact pinned components/fresh paths. Observer180frames/3000ms now matches frozen scored settings;12s probe/600s outer unchanged. Post-observer move-only reveal and single independentPNG are bracketed by exact strictpaused source/time/sixcounters and finite AXPosition equality; earlier JSONL/t0/taggedrouting/displayTime/PTS remain the only timing evidence. Source confirms move-only path cannot click/seek; actual visibility still requires proof. Fresh root nativeinventory41/noerrors. Root releases picture_orientation_build as soleUI/runtimeowner for one check; native_baseline remains disjoint offlineplaybackpreparation, no concurrent launch. Stop first failure, preserve raw/cleanup, no automaticretry or scoring.

20261006-1708 — Bounded transientUI source pass recommends a post-observer no-click reveal/park before the independent screenshot. Pinned controller autohide/show/mouseOnControls and video mouseMoved notification support the remedy; exact1725 cause remains unproven. Preserve original2000ms observer/event/t0/frames and classify independent postcenter only, with strictpaused/source/time/AXposition bracketing to show no additional seek. A disjoint SOL builder prepares this ignored successor only; nativeowner separately prepares8s audio/cache pilot. No concurrent UI, retries, classifier change or new scored result. Research recorded in upstream-contribution-scout. Existing007 native preference/source/reopen proofs will be inherited; actual reader navigation and minimal surface edges remain future closeout work.

20261006-1707 — Actual1725 finite calibration stops at first critical baseline seed check in8.328385s: independent post screenshot has no classified knob. Baseline012 PID58127 startup/prebind/play/singlepause/typedpause/finalstrictpause pass. Raw observer contains exact tagged move/down/up routing, two AX phases,114 post frames and completion;20 live complete frames classify center570/570.1 at391–1174ms, but full-window screenshot starts2481ms after input and lacks visible controls (root visually inspected). This is capture/time-separation disagreement, not proof absent slider feedback or a product regression. No c.evaluate qualification, candidate/left/negative/refusal/score/retry. Owned app and sampled derivedpreparser58136 exit/absence confirmed. Preserved final-case-inventory/raw-probe-summary/PNG/classifier/JSONL under actual1725 output. Root requests bounded source-backed transientUI timing diagnosis before any control successor, and prepares a disjoint8s audio/cache applicability plan only. No new runtime release.

20261006-1706 — Root and independent reviewer clear the frozen1725 control calibration plan (driver76512aff, planad82c6b8,14 pinned inputs) after29 offline checks. Only ignored successor plan changes: reviewed typed startup/guard, typed pause diagnostics retaining one requestedplay3 pending or pause4 ready plus at most one listenerpause3, and optional sampled descendant census. Final68e6 strict validators, observer/pointer/apps/fixture, exact geometry/crops/independent PNG centers/event-frame timing and finite10 cases remain unchanged. Root releases one600s bounded live calibration with original10s startup/pause and12s probe bounds, fresh paths,1GiB guard, first-failure stop and owned cleanup. No scoring, retries or parallel UI. Actual result pending; module import cannot acquire runtime. Next strategic checkpoint1735/three substantive rounds remains.

20261006-1704 — Resumption loop-review: aligned but measurement setup remains the delivery risk. The completed1005 run provides actual owned startup/strict-barrier proof in3.119s, replacing the earlier failed setup assumptions. Reuse the existing source-backed comparison of multiplexed CLI notifications versus structured request IDs and AX proxies: typed requested/listener tuples are disjoint, preserve all raw data, and retain the unchanged final strict validator. StructuredHTTP adds interface/build setup and AX alone can be stale, so neither is justified for this successful narrow gate. Do not grow a general harness framework. Next deliverable is one finite control calibration with independent rendered knob centers and routed event/frame clocks, followed by a separate short audio/cache playback calibration; only then release prospective scored cohorts. No retries or proxy successes count. Next strategic check by1735 Edmonton or three substantive rounds, whichever comes first; the locked dependency wait did not count as active iteration. No scope/permission change.

20261006-1703 — Integrated1005 actual setup check passes: owned candidate007 PID51247 exits0 and fresh ps confirms absence; total3.118984s. Seven prebind attempts retain unavailable socket/window stages before strict identity/emptyRC/CG/AX success. Eight startup replies preserve two STARTED pending and five play3/time0 pending replies before play3/time1 ready with decoded24/displayed25/audio24/played24/loss0. Readiness1.434854s after admission is descriptive setup evidence only. ONE unchanged68e6 strict barrier confirms exact source URI, requestedplay3 and all six counters. No pointer/pause/observer/modelhandoff/otherapp/retry/scoring. Existing unproven794/42789 untouched. Actual receipts live under work/story005-typed-readiness-20261006-1005. Root inspected exit/startup-ready/barrier-success; independent review pending. Native owner prepares fresh control calibration plan only; playback scout read-only and disjoint.

20261006-1702 — User explicitly resumes. Fresh root read-only native inventory returns41 apps and no native errors, satisfying the manual-unlock prerequisite. Re-read AGENTS/build-story, active blocker/plan/state, Ideal/spec and ADR004. Existing approved plan still closes preview/playback/evidence gaps and preserves sampled freshness and source-only delivery limitations. Root releases exactly one reviewed integrated1005 setup-only candidate007 check to the existing SOL6.1 medium native owner, with hash/fresh-path/resource preflights, original120s cap, raw evidence and owned cleanup. No pointer/pause/observer/other app/retry/scored result authorized in this release. Phase1 complete, phase2 open, phase3 untouched; no commit/push/contact/cleanup.

20261006-1007 — Secondgoalturn for the renewedMaclock: priorgoalturn madeconcreteprogress (diagnosticguard/parity/capfixes andtruthupdates), notmerewait. Freshread-onlynativeinventory stillreportslocked/manualunlockrequired. Authorizedremainingofflinefinishingnowcomplete: finalguard2243f072 resetsstructuredrejectionsuccess=False forfinalpersist/proofwrite faults;29parity+6cap+9finalwrite=44mockedchecks, AST andfocusedindependentreviewclear. Freshintegrated1005 launcherdf6a3110/plan23af46ab pinsguard2243/predicate7f2498/collector91e473/unchanged68e6finalvalidator;10offlineclosurechecks pass andactualruntime/socketroots areindependentlyverifiedUNCREATED. Oldguards/preflights/failedruntime preserved. No public/sourcechange ornativeacquisition. NextauthorizedruntimeisONEreviewedself-contained007-only120s typedreadiness applicability afterfreshaccessible desktop evidence; noinput/observer/scores andnoautomaticretry. Allcalibratedcontrol/playback/fullphase2/readiness gates remainopen. Noadditionalmeaningfulofflinework identified; manualunlockisrequired. Goaltoolremainsactive because currentrenewedlockaudit has reachedtwo, notthree, consecutivegoalturns. Ifnextgoalturn revalidates same lock andno newprogress ispossible, setgoalblocked ratherthancontinuingstatusloops. Nevermarkcomplete orpause.

20261006-1001 — Finalfocusedofflineguardreview clears priorcap/structuredfailure findings atfea07d51/preflight20c072e7; all35mockedchecks/hashes match, strictcriteria/successreturnkeys preserved. No native/runtime/integrationclearance. Diagnosticcaveat documented: finalpersistence failure canleave attempt.success=True while PrebindError/persistence_unavailable rejects; only successfulfunctionreturn/exactproof qualifiesprebind, neverthatdiagnosticflagalone. No actualIO fault runtime isclaimed. Verifierends; no extraiteration ornewacquisition whilelocked. Methodologycompile/validate/gitdiffcheckpass on currentblockedtruth. Finalhandoff remainsmanualMacunlock; phase2/nativecontrol/playback andready-to-submit gates remainopen. No commit/push/submission/contact.

20261006-0959 — Offline guard limits correction complete, finalfocusedreviewpending: successorfea07d51 preserves strictoldprebind criteria/successshape, records everyavailable attempted-stage rawprefix/identity/stamp beforestructuredfailure, and returns persistence_unavailable onunsafeoutput/cap/IO withoutoutsidewrite orbudgetbypass. Eachpersist enforces projectedaggregate-oldOwnSize+serializedSize<=32MiB;128KiB is accurately retainedprefix only, notcapturememory.29parity/evidence +6boundarychecks=35PASS andASTpass. Priorrevisions/guard/typedplan/failedreceipts preserved; no realprocess/socket/native/UIruntime. Lastfreshdesktoprecheck stilllocked;manualunlockrequestpending. Story/state nowBlocked andvisiblecurrentplanholdsprelaunch. No source/publicpatches/metrics/gatecompletion changed. Goaltoolblockedthreshold has notyet reached threeconsecutivegoalturns for thisrenewedlock; do not falselycomplete/pause/recreate it. Resumeonlywhenactualdesktopaccess returns, preserving userauthorization andpreparedreviewednextgate.

20261006-0952 — Current-state checkpoint/renewed external hold: typedreadiness draft passes16offlinechecks and independentreview; live0945 stopped8.550s at strictAXempty prebind beforeadmission, child24629 exit0/absent. Originalrejectedguardraw was lost, so exactpastfailurecause remainsunknown. Root thenrefreshed CUA documentation and performed read-onlygetState whiledesktopquiet; nativeinventory explicitlyreports Maclocked/automaticunlockfailed. No apps launched/input byroot. Usermanualunlockrequest ispending; screen/mouse/creditauthorization persists and isnotbeingre-requested. ALLnative/runtime/observer work held. Oneboundedoffline diagnostic-only guard successor preservesrejectedCG/AX/RC/liveidentity/stamps withunchangedstrictcriteria; nativebuilderownsignoredfiles. Existingbuilds/source/demo/publicpatches preserved. Goal remainsactive whilemeaningfulofflineworkcontinues; readinessgatesremainunchecked. Nextstrategiccheckpoint10:20 or threesubstantiverounds afteractualresumption; externalwait createsnoautorun/schedule.

20261006-0943 — Three-round strategyreview: self-containedorchestration succeeded; streamclassification is now the evidencedsetup obstacle. Firstcontrols pilot stopped1.474s with actualsingleURI/requestedunknown4294967295 +unsolicitedplay2. Noinput/observer/candidate/score; exactownedbaseline6655 exits0/absent. Compare standardtyped/correlatedmessageclassification (JSON-RPC source is generalmechanism, VLCcontract is pinnedCLI) with AXadvancement readiness or a structuredlocalAPI. Root/native/independentreviewer inspect exactlistener/snapshot disjointpairs/locking beforechoosing; no broadduplicateallowance orfinalvalidatorchange. This is a useful diagnosed failure, but no nativeperformance gate has advanced. Keep objectiveandcriteria, preferonecause-targetedlocalcheck, andavoid furtherwholepilot launches untilsetupclassification is proved. Existingself-contained120s/10s bounds remain available; no newclone/productpatch/remotecontact. Next09:50 checkpoint retained or threesubstantiverounds sooner.

20261006-0939 — Controls pilot source review: use bounded conditionreadiness for the asynchronous Pause toggle too, preserving exactURI/currenttime/sixcounters and strictPause4 validator. One command sendsPause once; validPLAYING is pending untilPause4 withinprospective10s, allrawretained. Conditionalocclusion can reuse ownedbaseline AXraise onlyifactualcandidateforeground remains and frozenobserver rejects its AXhit againstexactbaselinePID withzeroinput; otherwise preserveunattempted. No userapp/newobserver/geometryretry. Reviewinstructions were firstqueued to acompletednativeworker withoutstarting aturn; followup_task nowexplicitly triggers revision. No app runtimeelapsed during this deliverygap. Revisedhashes/offlineevidence required beforeone rootrelease.

20261006-0931 — Self-contained acquisition applicability passes: exact007 child49842 singlelaunch/prebind/admission/readiness/strictbarrier/cleanup completed1.760181s, exit0/absent. Three retained pendingreplies (STARTED twice, then validPLAYING withzero counters) progress toready at0.628288s afteradmission: play3/time0, video decoded5/display4/audio15/played15/loss0. One unchanged68e6 strictbarrier then passes exactURI/state3/sixcounterparse. Allraw/base64 bytes and liveidentity brackets preserved. This timing is setupobservation, notpreview/control performance. No inputs/observers/scores. Applying self-containedconditionbasedsetup to nextcontrolpilot eliminates unnecessary model/CUA gates; native builder prepares onlyfreshignoredpilotdriver/plan forreview, preserving10minouter andfinitecases/criteria. Rootwillindependentlyview actualframes andrequirecalibrationevidence beforescores.

20261006-0928 — Three-round loop review/course correction: aligned outcome, orchestration now demonstrably ineffective. The0924 startup experiment passed actualowned prebind/CUA but contextcompaction consumed120s before admissionmarker; exact12908 timestampedcleanup elapsed120.044s, exit0/absent, zero startupreplies. No product/readiness result follows. Manual model/CUA handoff between launch and admission is unnecessary for a no-input test and makes agent latency part of a finite experiment. Established alternative is a self-contained bounded acquisition process with deterministic stages and final receipts, keeping external observers/nativeownership rather than injecting production tracing. Reuse proven actualchild/RCempty/CG/AX/executable guard, then immediateadmission→reviewed10s conditioncollector→unchanged strictbarrier→cleanup inside one command. NoCUAbind is needed for this narrower no-inputreadiness check; priorbindings and actualnativefunctional proof remain separate. Keep120s bound and allcriteria/sourcehashes, no newclone or hiddenretry. Builder prepares onlylauncher orchestration; rootreviews beforeone release. Nextusefuldeliverable remains actualreadinessreply then renderedcontrolresponse, not moremanualsetupcycles. Next strategicdeadline09:50 retained or threesubstantiverounds sooner.

20261006-0920 — Strategy checkpoint carried at09:19 after source-backed diagnosis: useful uncertainty improved. Diagnostic-only successor68e6cd3d preserves strictvalidate_rc and exactfailurebytes;16offlinecases and independentreview clear. Candidate-only experiment19.761s/120s now proves immediateSTARTED reply with correctURI, unknown4294967295/no time/zero counters; no duplicateframing occurs in this sample. Original0918 reply remains lost. Choose standard bounded condition-based readiness over immediateassumption or fittedsleep: requestedPLAYING3/currenttime/nonzero decoding precede unchanged strictmeasurementbarrier. Listener PLAYING2 is a different source contract, not accepted by requestedstatevalidator. Native builder prepares one120s applicability experiment with prospective10s startupbound and allpendingreceipts, offlinefailclosedchecks, then rootreviews beforelaunch. Still no nativeperformance metric or gatecompletion. Keep nextusefuldeliverable one renderedcontrolresponse afterready, not further framework expansion. No productionpatches/newclone/thresholdchanges; next strategicdeadline09:50 or threesubstantiverounds.

20261006-0912 — Three-round strategy checkpoint: aligned but test-setup overhead still dominates, with no scored native result. Timestamped baseline visibility now passes; next controls cohort established baseline play3/Pause4/counters/visible geometry but failed candidate strict RC before observers. Raw failed reply was lost by exception-first barrier API, and one dependent reveal move ran before inspecting the failed result; both are test-harness problems to correct, not product or performance findings. Both owned apps exited cleanly211.640s/600s. Compare established request/response capture with blind parser relaxation or repeating fullpilot: preserve raw bounded transport evidence before validation, enforce sequential fail-fast orchestration, then one candidate-only raw state/source/counter discriminator. Existing pinnedCLI/source-backed successful functional RC requests and Unix stream semantics remain the relevant comparison; precise actual rejection stays unknown. Builder may add diagnostic retention only, with offline same-criteria tests and independent review. No criteria relaxation, source/product change, new appclone or further fullpilot is justified until this tiny transport observation succeeds. Useful nextdeliverable is one diagnosed actual reply, then one rendered control response; metrics and broadnegative cases remain explicitly open. Next cadence09:20 remains, or three substantive rounds sooner.

20261006-0904 — Small readiness experiment resolves the immediate precondition: baseline012 exact21111/source/state3/time1→3→5 and live identity bracketed queries at admission+1.007/+3.010/+5.013s; normal owned main window and AX timeline are present. Root viewed actual frame1.917/frame46. Controls naturally faded, so pixels do not qualify knob readiness. Experiment completed29.031s/120s, timestamped cleanup exit0/psabsent. Earlier untimestamped empty-query cause stays unknown. Root releases one fresh controls-only finite calibration cohort,10min from firstlaunch, unchanged observers/thresholds, baseline012/candidate007; owned move reveals controls, ordinaryplay→actualPause4 and independent centers precede one seed/positive perarm and savednegative/guardrefusals. No resume of seeked sessions or scoring. Separate fresh playing/audio/cache qualification follows only after this control pilot.008–011 remain unused.

20261006-0900 — Resumption loop review (08:50 checkpoint was missed across interruption): aligned but calibration remains the bottleneck. Original0828 pilot reached actual owned empty-window readiness, exact-path CUA binding and legal media admission for both arms; interruption consumed its600s bound. Both proven-owned children exited0 and are absent; launcher source enforces the original bound, but exit receipts lack timestamps proving the precise cleanup time. No pause barrier, observer, routed input or score ran; all unattempted cases remain explicit. Do not reset the timer or call startup proof performance proof. Native owner now diagnoses existing logs/query semantics read-only before one smallest cause-discriminating experiment. Reuse established native readiness/coordinate research and ScreenCaptureKit complete-frame timestamps: RC-only or service timing cannot replace actual visible control feedback, while direct source instrumentation would alter the artifact. A smaller one-arm window-readiness experiment is preferable to repeating the whole pilot before its precondition works. No source/observer threshold changes, additional app clones or unrelated repairs are justified. Fresh008–010 scored namespaces remain unused. Next strategy review09:20 (retain cadence) or three substantive rounds; frequent commentary continues. Goal tool now reports active after user continuation, with objective unchanged.

20261006-0820 — Current-state loop review: aligned but setup reliability at risk.
The first calibration ran no observers/media/input and stopped at CUA timeout.
Root's raw stderr/source pass establishes invalid unprefixed video-autoresize
launcher flag before binding; child failure was not propagated. CUA auto-launch
semantics and later no-option006 PID42789 timing fit, but ownership remains
unproven and untouched. Reuse the successful functional launcher and exact pinned
macosx-video-autoresize option, with alive/socket/empty-window preconditions and
child-exit propagation. Fresh baseline012 preserves existing006. Compare the
established exact-PID launcher/ready barrier with blindly retrying CUA or random
identity variants: verified preconditions address the observed cause directly.
One corrected finite pilot follows reviewed preflight; unchanged frozen observers
and acceptance criteria remain. No drift/geometry/input claim comes from failed
setup. Native follow-up passed preferences/CLI/source-failure/replacement and
wheel/volume/Space across four surfaces; drag remains coordinate/setup-inconclusive.
Source-backed coordinate review recommends one paired playing main drag after
performancepilot, using qualified logical coordinates and actual down/drag/up.
No core pause/seek or broad upstream cleanup patch is inferred. Next review08:50
or three substantive rounds. Keep normal progress updates frequent while operators
wait; preserve every failed case and all fresh scored namespaces.

20261006-0748 — Loop review after structural, baseline attribution, reader and
observer-review rounds: aligned, with qualification overhead now the principal
risk. Useful progress is actual four-surface rendering, source/track/rotation
replacement, reader activation and baseline attribution of all three remaining
assertion signatures (clock/TLS/OpenGL); cause/configuration limits remain. Keep
the existing external-observer approach: source-backed ScreenCaptureKit display
timestamps and matched intervals measure actual feedback, whereas RC-only timing
would lose that boundary and production tracing would change the feature artifact.
Independent review found missing RC source/exact-state validation and out-of-window
preparation boundary bins; builder must resolve these before any scored trial.

Do not chase unrelated upstream install/distclean or full reader navigation fixes.
A finite15-minute native follow-up closes current preference/CLI/freshness/practical
control gaps while observer fixes/compile finish offline, then hands UI exclusively
to a small calibrated pilot. Stop scored collection if the pilot fails rather than
adding special cases. Retain reader's actual detached keyboard/keywindow focus
stability and baseline-equivalent pointer-following outline as limited proof, not
spoken-label or full reader-navigation acceptance. Legal demonstration uses exact
clean synthetic screenshots with corrected actual-used fixture provenance; unused
12s session inventory cannot label admitted300s media. Next checkpoint08:18 or
three substantive rounds, whichever first. Existing scope/authorization preserved.

20261006-0744 — Native owner quiet handoff: exact owned app/worker sessions
exited, unproven794 untouched, VoiceOver restored off and Settings closed. One
standard untouched-baseline OpenGL test reproduces archive GL_INVALID_OPERATION
at filters.c134 (TRS FAIL/native134/driver0,0.942s); no overrides/rebuild, own group
reaped. Normal-vs-minimal config limits and cause uncertainty remain. Graphics
released for reviewed performance calibration after offline compile/review. Actual
VoiceOver starts through documented Settings route, but full spoken/navigation/
control activation remains unqualified; per-arm hover AX focus stability observed.
No global reader/speech settings remain changed. Exact native functional receipts
are pending coordinator review.

20261006-0738 — Structural distribution experiment terminal at first failed
stage. Redistributed archive and required5headers/12helper files pass. Install/
uninstall and DESTDIR command exits are zero with clean uninstall residuals, but
inspection finds failed destination `cd` in unchanged parallel install-data-local,
followed by `mv` in the build tree; do not claim correct executable installation.
Empty installcheck has no functional installed suite. distcleancheck fails with
`bin/vlc` and extra-only `libvlc_vtutils.la` left. Pinned make-rule/source comparisons
and Automake docs identify existing ordering/cleanup declaration issues, without
changing source or suppressing tests.232.4s/644MiB extra allocation; original seven
runtime failures and all diagnostic/source/archive bookends preserved. Continue
required native/performance proof; avoid turning unrelated upstream repairs into
a new iteration loop. See structural-distribution-001.json for exact scope.

20261006-0731 — Current-state loop review after resumed isolation, real hover and
observer-planning rounds: aligned and progressing, with performance observation
the main remaining technical risk. Actual four-surface preview, media/track
replacement and rotation now establish useful behavior beyond compile/test counts.
Continue this native acquisition to keyboard/reader, preference and restart/freshness
proof before handing the desktop to calibrated matched trials. Do not rerun passing
helper/contracts or chase an unrelated whole-upstream green distcheck. Reuse the
source-backed Automake structural-vs-runtime distinction and Apple's complete-frame
/displayTime observer contract recorded in master-trial-adapter-plan.md. A materially
different alternative is production trace instrumentation or RC-only timings; the
former changes the tested artifact and the latter lacks actual displayed-feedback
evidence. Existing external ScreenCaptureKit capture plus a small positive/negative
classifier pilot preserves the required boundary with less product change. New
observer sources take explicit identities; no legacy3.0 bundle constants.

For active preparation, use a separate prospective background-only cohort with
pointer outside the timeline and bounded cache alias-growth snapshots matched in
both arms. Require proactive completions in every10s bin and near both ends, plus
exact owned worker identity. This supports sampled preparation across the interval,
not continuous decoder occupancy; exclude early-finished cohorts. Architecture
review challenges this seam before scored acquisition. The separately bounded
structural-distribution experiment preserves failed make-check and its binaries
before install/uninstall/redist/distclean checks. Next strategic checkpoint around
08:02 Edmonton or three substantive rounds, whichever first. Existing authorization
covers these steps; no submission, contact, commits or broad source cleanup.

20261006-0727 — Human-input hold resolved: Cam accepts the open-source/credit
recommendation and explicitly authorizes screen and mouse use. Existing GPL/LGPL
terms and third-party notices remain; contributor credit is not an assignment,
exclusive ownership claim or invented sign-off. The Mac is accessible. Resume
phase2 under existing scope. Candidate007 is a metadata-only isolated clone with
source-equivalent loadable sections (receipt `isolated-candidate007.json`). Actual
display composites show correct image/time on all four timeline surfaces, and
MP4→MKV and red→blue selected-track switches replace old images. Root independently
viewed main-display-composite.png: pointer02:29, Keyframe02:28 and burned148.000
seconds while main playback is51.625 seconds. Panel-only capture omissions are a
capture artifact, not a product rendering failure. Native owner retains exclusive
UI; observer adapters build offline. Remaining native/reader/restart/performance
proof and failed distcheck disposition remain open. The app goal tool still shows
the earlier blocked status and cannot be resumed by update_goal; do not claim it
active or complete. Repository status is In Progress. No submission or contact.

20261006-0149 — Blocked audit: the same manual-unlock, alternate hover-input and
human-attribution holds persist for the third consecutive goal turn. The preceding
continuation made no substantive progress; rechecking status was not a verified
wait. All worker lanes are terminal, the distcheck receipt is terminal-failed,
and live public manifest SHAeecec3b9 matches the final59-file confirmation. No
human answer has supplied the missing input or authorization. Offline build,
bounded failure attribution, review and preservation work is complete for the
current frozen source. No further useful independent action closes the required
native or attribution gates. Mark story and goal Blocked, not complete; keep the
full phases1/2 objective and all unmet criteria. Resume only after the named
inputs change. No repeated build/test or UI-lock workaround is scheduled.

20261006-0148 — Final headless closeout: revision9 public tree
48a6b53f29d7f99ea410ba0e9d7085f7d9673acb exactly reproduces59 files; only the helper
README payload changed from revision8. The other three patches are byte-identical.
Independent source confirmation matches every public hash, exact staged path set
and pinned HEAD with no unrelated unstaged tracked dirt.99 generated translation
paths matched their preserved receipt, then their verified generated-only inverse
restored original bytes; no generic cleanup was used. Failed archives/logs remain.
Latest review009 and wrapper prose now distinguish historical freezes from current
results. `make methodology-compile`, `make validate` and `git diff --check` pass.
No further build/test run is needed for this docs-only change. Phase2 and the goal
remain incomplete; native unlock/input permission/attribution answers and the
distribution runtime gate remain open. No submission, contact, commit or install.

20261006-0145 — Loop-review after the header prerequisite, runtime-failure
diagnosis and baseline attribution rounds: aligned, with actual native proof held
and distribution runtime qualification still open. The revision8 archive contains
all five headers byte-exactly and compiles/links.072705Z then fails at make check:
92 counted,80 pass,5 skip,7 fail,437.5s and6.40GiB minimum free. Installation,
uninstallation and distclean were not reached. No test was suppressed or weakened.
The broad missing-header inventory prevented another speculative source repair;
Windows remains outside the current graph and untouched.

Bounded independent diagnosis finds15 failing-test/implementation files unchanged
from the pin. Missing BMP/converter errors fit upstream's disabled avcodec/swscale
minimal profile. Clock/TLS/OpenGL causes were not established from those logs.
Two existing untouched-baseline selectors then reproduce the exact clock drift_72
and TLS acceptance assertions, each under two seconds, no rebuild or host change.
Full baseline and minimal distcheck configurations differ; this is scoped baseline
failure evidence, not a matched whole-build comparison. Certificate expiry is
excluded; selected TLS backend and OpenGL causes remain unproven. Root inspected
the074008Z receipt, native exit134 and recorded FAIL (the Automake driver's own0
exit must not be mistaken for a test pass). Owned groups are gone.

Reused and refreshed the official Automake distribution-contract comparison in
the runtime triage note: a VPATH compile cannot stand in for its subsequent test,
install and cleanup stages. A fuller dependency profile is an established way to
satisfy tests requiring codecs/converters, but it would be a different profile
and would not settle the baseline clock/TLS or OpenGL causes. Would choose the
bounded attribution runs again; would not repeatedly rebuild or repair unrelated
upstream tests while the actual product gate needs an unlocked Mac. The meaningful
next product proof remains native hover, surfaces, reader, restart and matched
controls/playback under the existing prospective protocol. No allowance or
readiness criterion changes, no prototype core code reintroduced.

Finish only the source-guide/package reconciliation and generated-translation
preservation now. The guide records actual independent artifact versus failed
outer launcher,288 counted/one skip/zero failures, exact failed distcheck and
host prerequisites. Its final changes are documentation only; unchanged app and
test evidence is reused. Preserve public patch/tree correspondence and failed
archives. All final attribution, manual unlock and alternate hover-input answers
remain pending. No contact/submission/commit or daily-app replacement. Next review
by0215 local or three substantive rounds only if active work resumes; this does
not create work to fill the human-input hold.

20261006-0127 — Distribution prerequisite follow-through:072024Z verifies all
four Apple header bytes in the actual archive, then fails selected media-library
compilation on the previously inventoried LazyPreparser.h omission. Root inspected
the error, source include and exact one-line SOURCES addition. Its independent
review is clear. Expand only the separate leading prerequisite to five unchanged
headers across three Makefiles; no Windows repair, runtime/flag/condition change
or feature-patch change. Revision8 exactly applies59 files at
treec545256d9ca20aed8e75a57f9fdb76091ddecf9d. This remains the same conventional
archive-completeness mechanism, not a new product lane. Preserve the failed archive
and run the same guarded check; report a different material failure before repair.
Source guide reconciliation waits until that job ends. Native and attribution
holds remain. The0120 strategic review and0152 deadline remain in force.

20261006-0120 — Loop-review after three substantive rounds, before the retained
0122 checkpoint: aligned, with the final
source archive gate progressing and the actual user-facing proof held by the Mac
lock. Since0052, conventional distcheck exposed three distinct prerequisites:
GNU sed syntax in upstream's distribution hook, Git discovering this wrapper
repository above the extracted read-only archive, and omitted existing Apple
headers. Scoped GNU sed4.10 through VLC_PATH and GIT_CEILING_DIRECTORIES resolve
the first two without changing VLC source. Their bounded smokes pass; failure
receipts and generated translation deltas remain preserved. The subsequent run
reaches actual Apple compilation and fails on missing channel_layout.h.

Root inspected the exact diff and independent review: list channel_layout.h,
avaudiosession_common.h, VLCDrawable.h and vlc_pip_controller.h beside existing
consumers in only the two Apple output Makefile.am files. Header bytes, runtime
code, conditions and flags are unchanged. This is a small required packaging
delta within phase2. SOL6.1 medium build/package owners prepare a separate leading
0000 patch, preserving the existing three feature diffs. The public inventory
becomes58 files. Other inventory omissions in medialibrary and Windows remain
outside scope; a new material failure requires a fresh decision before repair.

Would continue this bounded archive check: the standard Automake distribution
approach directly tests the source package a contributor will consume, unlike a
Git checkout build that already passed but cannot expose missing archive inputs.
Reused the primary Automake and Git comparisons in the linked distcheck research
notes. Copying headers into an extracted archive or weakening its read-only
checks would defeat that mechanism. The smallest useful next proof is byte-exact
archive membership for all four headers, followed by the same guarded distcheck.
No new full app or registered-suite run is warranted for source-list-only edits.

Keep source/public guide reconciliation finite after that result. Do not invent
additional headless tests to occupy the native hold; passing contracts cannot
replace visible hover, reader, restart or matched controls/playback. Correction
to0052 process wording: only explicitly tracked native launch PIDs were stopped;
later PID794/801 ownership is unproven and neither was touched. No UI input while
locked. No change to goal, readiness criteria, submission boundary or pending
human questions. Next review by0152 local or three substantive rounds, whichever
comes first; dependency waiting does not extend active work.

20261006-0052 — Loop-review after the quiet-suite diagnosis/correction and native
acquisition rounds: aligned and progressing; native completion is now held by
the Mac lock. The final independent registered suite passes on public revision6
tree1a567b8705d3f744afc2b873458a5e8af02f7a7b:269 main cases (one optional-volume
skip),7 context and12 hover, zero failures. Root inspected064748Z receipt/log,
including the actual real-controller test after the earlier integration class.
Actual ENOSPC already passed separately. The preceding focused two-selector run
also passes. The independent artifact, helper77 and custom-AVIO proof remains
applicable; both later source deltas only change tests. No app rebuild is needed
for them. Lean upstream distcheck is running with macOS UI/helper disabled,
separately from the feature-enabled app/test proof.

The fixed-sleep failure recurred under quiet owned build conditions. Reuse the
Apple completion-expectation comparison: a bounded condition tests completion
without mistaking a chosen sleep for a product deadline. The pipe prefill test
also assumed fixed capacity;32 local probes did not reproduce its failure.
Published Apple XNU allows capacity growth under changing shared pipe pressure,
a compatible explanation rather than proven causation. A bounded256KiB no-reader
fixture exceeds the documented64KiB Darwin buffer cap, and independent workers
plus joined cancellation prevent later epoch assertions cascading. Independent
review clears this test-only repair; production IPC deadlines are unchanged.

Actual candidate evidence advances saved0→restart0 and saved1→restart1, ordinary
wheel/core seeks, native fullscreen enter/exit and disk preparation. Initial
cache absence was the test's unique cache-domain symlink, intentionally refused
by SafeAncestors. Preserve that link/target, create the same owned domain as a
real directory, then observe7samples/7targets and a later8th payload. Root CUA
inspection corroborates actual public-fixture playback/window identity, not a
visible preview. The next same-URI reopen stops before media admission because
CUA reports Maclocked; all owned GUI/helper processes are now stopped. See the
native acquisition ledger for each surface and failed/unqualified attempt.

Would continue this approach: meaningful source/test failures are closed and
the remaining product evidence needs the actual interactive Mac. Established
headless contract tests are complementary; substituting them for physical hover
or reader proof would not satisfy the story. Complete only the pending distcheck
and source-package evidence while waiting for manual unlock, the existing
alternate-input question and final attribution facts. Do not expand tests or
restart passing lanes to fill that wait. No scope, allowance or authorization
changes. Next strategic review by0122 local or three substantive rounds, whichever
comes first; this does not extend work past a real human-input hold.

20261006-0030 — Loop-review: aligned and progressing, with native proof and final
reproduction still at risk. Since0003, the actual-slider duration correction
passes12 registered tests and a counterfactual old mapping fails; the corrected
app packages/signs and preserves997 files/10 symlinks through relocation and
isolation. Independent remote source plus the public55-file tree builds its own
tools, patched FFmpeg and app; fresh normal helper77 and custom-AVIO parity/fault
checks pass. The independent app's final build/sign log completes, but its outer
launcher exits1 after the builder modified an executing shell script. Preserve
that failed orchestration receipt and direct artifact verification separately;
subsequent launchers are written completely and frozen before execution.

The latest full suite is not green:269 main tests include one optional-volume
skip and two failures, while context7/hover12 pass. One fixture leaks four process
environment variables into the later real-controller test. Reusing Apple class
setup/teardown and POSIX process-environment guidance in
`docs/research/story-005-test-environment-isolation.md`, select owner save/restore
over a separate test process: the existing serial fixture already has synchronous
LibVLC teardown, so restoring its state fixes the demonstrated cause with less
build machinery. The56th public file is test-only; independent review clears
bytes/unset-state ownership, allocation/setup failure and idempotent cleanup.
The other failure is a fixed2.5s wait with6 jobs done and the7th active, not a60s
preparation timeout. Apple expectation guidance and the existing condition-based
quiescence test provide the alternative synchronization mechanism, documented in
`service-port-async-failure-diagnosis.md`; first run one quiet full suite after the
environment repair. If the fixed wait fails again, change only synchronization
to the existing bounded completion predicate, not production deadlines.

Would choose the retained helper and current native integration again given the
source-backed ADR004 comparison: core reuse still lacks the demonstrated time/
eligibility contract, and another decoder redesign would not close the present
native evidence gap. Finish the independent suite/distcheck and actual candidate
experience instead of increasing test inventory or rebuilding unchanged app code
for test-only deltas. Candidate functional UI is released; matched performance
waits for all build activity to stop. Baseline main/detached/native/custom surfaces,
playing seeks and ordinary pause/resume work; paused-seek/resume and stale bar
labels reproduce without the contribution and remain explicit limitations.

Human attribution and alternate hover-only input permission remain unanswered.
Use permitted CUA actions for independent native work; elapsed time is not either
answer. No scope/acceptance reduction, commits, upstream contact or daily-app
replacement. Continue within the existing authorized goal. Next strategic check
by0100 local or three substantive rounds, whichever comes first.

20261006-0003 — Loop-review: aligned and progressing, with one necessary feature
correction exposed by native baseline use. Since the23:48 review, independent
tools and normal patched contrib build pass, all four baseline control surfaces
were actually reached, playing seeks and pause/resume without a seek work, and
four focused cache/service fault tests pass. Literal ENOSPC reached errno28 on a
verified20MiB owned HFS volume; RAM fallback, seed reopen and disk recovery pass,
then the captured device was detached. Atomic publication ordering is inherited
from the identical Story004 persistence sequence apart from manifest4→5; no
literal killed-writer or power-loss claim is made. The real-controller race test
compiled but aborted at a missing configuration registration assertion; its
owner is diagnosing test initialization before one repair, not changing product
configuration to satisfy the harness.

Baseline paused-seek/resume stop and stale time controls reproduce with the new
portable fixture and verified CUA actions. A media switch updates title/video/
queue to12seconds while the bar retains the old300second timeline. The feature
still uses that bar duration after refreshing its atomic context: stale10s versus
current20s at50% can send a valid-but-wrong5s request. This source-derived defect
must be repaired, independent of whether the baseline clock/drag issue is fixed.
Root selects the fresh context duration for both hover pointer caption and preview
request/endpoint clamp; mixed duration sources and strict equality suppression
are rejected because normal item/live duration differences may be legitimate.
Keep ordinary seek/core behavior untouched and test shorter/longer stale bars and
duration changes at completion. Candidate is stopped before rebuilding. Its only
native result so far is a visible empty window and the default enabled preference.

We would retain ADR004's helper route: the source-backed native/preparser movie-time
and eligibility gaps are unchanged. The meaningful verification alternative is to
qualify unaffected controls and record reproduced baseline defects, rather than
expand into a general master clock repair. This does not excuse wrong feature
pixels or duration mapping. Finish this coherent correction, final source freeze,
independent reproduction/distcheck and candidate native/restart/performance proof;
do not add another broad test inventory once these named boundaries close.

Disk capacity dropped externally from20.2GiB to5.8GiB during the independent build;
fresh app stage started above its5GiB threshold and remains under continuous1GiB
guard. No further cleanup is authorized. A7200second stream-copy fixture recipe
is prepared for255-target/60second active-preparation proof; actual generation
awaits a separate small capacity preflight. Real pointer hover needs an alternate
input method absent from CUA; Cam has been asked for explicit harness permission
under the tool's instructions. Human attribution is also pending. Other work
continues. Next strategic checkpoint00:33 or three substantive rounds.

20261005-2348 — Loop-review and resumed execution: aligned and progressing, with
native qualification now the main uncertainty. This performs the overdue23:03
check after storage cleanup/resume; retain the next scheduled00:03 checkpoint
or three substantive rounds rather than shifting cadence. Approved12-target
cleanup observed1.72GiB recovery with protected source/config/app hashes preserved.
Fresh resume capacity26.2GiB clears the resource blocker. Final registered normal
suite passes277 tests, zero failures, and same-bundle relocation plus isolated
candidate signing preserve loadable sections/997otherfiles. Fresh official remote
checkout plus3public patches reproduces54files/treedc28a08a. Its tools build first
failed because the manual guide omitted SDKROOT and the host CMake runs via
Rosetta; documented SDKROOT/CMAKE_APPLE_SILICON_PROCESSOR repair is being tested.
SDK27.0 versus prior26.2 is recorded, not hidden.

The selected helper still closes actual sample-time/selected-track/NAS reuse gaps;
ADR004's recent source-backed comparison to native core/preparser remains relevant
and its movie-time/eligibility prerequisite is unchanged. We would choose this
route again. Returning to core would not resolve baseline AppKit/playback setup
or independent build requirements. The meaningful alternative for verification
is ordinary playing startup with event-based readiness, rather than another
paused-start coordinate replay. Pinned doc/clock.md describes audio as nominal
master; baseline play action simply toggles player state. The fresh-domain
discriminator's main/detached midpoint hover/seek succeeds, but both sliders are
already0.99675846 at the first post-Play snapshot,16.176seconds after the seek
snapshot. The second click is not confirmedPause. No causal clock diagnosis or
feature regression is asserted. Next bounded test uses the new public300s fixture,
timestamps/RCstate/rate/time, ordinary initial playback then verified AX pause,
midpoint seek and resume; stop on another jump before fullscreen/performance.

New portable long fixture and NAS repeat remove the unrecovered old seed recipe
from required proof:36requests/18pairedactual-time andpixel results agree with
oneopen/worker, warm NASready19.9–37.1ms prior/19.7–46.3ms current. Oldlayout stays
supplementary. Independent audit distinguishes277coverage from remaining race/
fault boundaries. Authorize narrow queued15s expiry, stable service quiescence
and actual retiredPID checks in existing test files; assess real-player epoch
proof before implementation. Avoid redundant broad reruns and speculative
production hooks. Actual UI/restart/matched playback, clean reproduction/distcheck,
legal demonstration and human attribution remain gating. No ready-to-submit claim.

20261005-2239 — Draft package and resource handoff: final3patch series applies to
the pin and exactly matches54 frozen files, tree65a741e6f10b60cf42bbf4a8eac81c07d5a8db63;
manifest0101f4cfbb40288c3e5bcae72918600cbfdd9c7210474e5df36be8fb6af602ac.
Exact license/header/private-data review passes within its declared scope; missing
human author/holder-credit facts are requested, not invented. Public README keeps
AI-assistance provenance explicit. Clean reproduction/native acceptance remain
open. The larger NAS fixture's exact remux is retained but its seed generation
command/version could not be recovered in a bounded trace. Keep the measured
result supplementary; after headroom returns, create a fresh public five-minute
synthetic seed with recorded tool/recipe, measure its actual remux structure and
repeat that bounded comparison. Do not equate older differently hashed seeds.

Cam has been asked for5GiB available based on measured source/output/tools plus
1GiB reserve; this is not a request to delete the inventory. All runtime is held,
and small source-package work is complete. The launcher preflight repair's mocked
low-space branch proves zero Popen/profile/symlink/log writes. Learning-review
hook considered because of the earlier false timestamp inference and this shell
sequencing failure; the immediate concrete correction and retained evidence are
recorded without modifying memory or shared workflow skills. Story stays Blocked
at phase2; no ready-to-submit, commit, install or external contact claim.

20261005-2232 — Loop-review checkpoint (three substantive rounds since resume):
aligned and progressing, but phase2 is resource-blocked. The77-case local gate,
36 paired warm-NAS responses and complete packaged app materially improve the
contribution's usefulness; another narrow matrix cannot substitute for the
remaining native experience and independent clean reproduction. Reused the
current ADR004/source-backed comparison with native core/multiposition preview:
its movie-time/eligibility gap still requires broader design, so returning to
that mechanism now would not remove either the disk constraint or native proof.
Continue the selected helper proposal and preserve its conservative exclusions.

Smallest next decisive experiment remains fresh-domain detached baseline setup,
then candidate four-surface proof, followed by matched controls/playback and
independent build/distcheck. Source-series/attribution review can finish without
runtime; do not spend the hold repeatedly rerunning passed intermediate tests.
Keep the1GiB floor. Ask for sufficient fresh headroom once the build owner records
an estimate; there is no permission to delete protected work or modify other
projects. This is the due22:33 strategic check performed one minute early, not
a change of cadence. Next check23:03 local or three substantive rounds; exclude
verified resource waits. No goal change, submission, installed-app replacement
or weakened acceptance criterion.

20261005-2230 — Phase1 investigation/plan gate complete: root reconciled the
current gap matrix with ADR004, final helper/runtime evidence and the coherent
three-part source-series plan. No upstream endorsement or contact is implied.
Phase2 remains open. Normal H1 helper passes77 checks, all32 prior image replies
retain exact pixels/time, and custom I/O fault/packet proof is recorded. Two warm
NAS layouts complete72 requests with36 exact paired image/time results and one
open per helper. These are bounded warm observations, not universal latency.
The official feature app compiles/packages/signs successfully; isolated packaged
helper proof passes from an unrelated working directory. Final full XCTest,
actual candidate native controls, restart/cache/playback comparison, clean
reproduction/distcheck and final attribution remain unqualified.

Disk again fell below reserve to about831MiB; runtime/build lanes are held while
small source/provenance work finishes. The baseline launcher exposed a shell
sequencing error after a failed preflight: an old-domain owned process briefly
started then its continuous guard stopped it before media/UI acquisition. The
builder must make pre-Popen checking fail closed and validate the low-space path.
No installed app/private media was touched, and no cleanup was authorized.
Next native discriminator is a fresh owned bundle domain, after root's bounded
AppKit restoration research and exact baseline deadlock sample inspection.
Preserve the next22:33 strategic checkpoint; resource waiting is not active
iteration. Public source series refresh adds the final admission guide/dist list.

20261005-2219 — Resume and loop-review checkpoint: the previous continued goal
turns made no progress under a verified disk blocker, and the goal was marked
blocked after the third occurrence. Cam now explicitly requested continuation.
Initial fresh df showed689MiB, so only small source-package work proceeded.
At22:19, Foundation capacity, df, statvfs and shutil readings reflected newly
recovered space; statvfs/shutil agreed on2,084,753,408bytes (about1.94GiB).
The guard metric and1GiB reserve are unchanged. A single read-only CUA inventory
also succeeded without a lock error; this is availability, not native behavior.

The overdue2203 strategic checkpoint is audited now, retaining the original
deadline across resource waiting. The route remains aligned: source-reviewed
normal dependency/helper builds and actual buffered-I/O parity/fault evidence
justify the full bounded admission/parity/cost experiment. The alternative native
preparser route still has the evidenced movie-time/eligibility prerequisite; no
new observation justifies reopening it or replacing the feature with a smaller
proof. Continue the selected port, use existing fixtures/artifacts, and avoid
another large checkout/build. Next checkpoint2233 or three substantive rounds.

SOL6.1 medium lanes resumed H1 admission/parity, the remaining actual native hover
test, owned baseline UI setup and small public source-series preparation.
The draft three-part series applies cleanly to the pin and exactly reproduces
54 frozen source files;432,964 patch bytes and2,016,661 peak temporary/artifact
bytes stayed within the20MiB cap. Generated Python caches are excluded. The
combined native patch keeps startup/build/tests/UI dependencies coherent without
temporary stubs. This is exact source correspondence, not clean-build or native
qualification. Final results, attribution, reproduction/distcheck and public-diff
review remain mandatory. No commit, cleanup, install or external contact occurs.

20261005-2157 — Early strategy checkpoint and resource hold: normal FFmpeg9
TrackNumber and opt-in flat-admission dependency builds succeeded; actual helper
binary b2b5e5d13bf6d3e92f9e23193ec516d86b1f54547783fb5c53ce2fbbf6dadf73
passes13 basic registered checks. The actual normal-libavformat custom-AVIO probe
preserves all1200 packet payloads with admission on/off and rejects unsupported
size, restore failure and mid-scan read failure. Sanitizers cover the probe,
not an asserted fully instrumented dependency build. The38-case admission matrix,
39-case helper pixel/PTS parity and representative local/NAS costs remain pending.

Context preference/shutdown reentrancy, hover snapshot reentrancy, malformed cache
counts, context type/completeness and channel overflow are repaired and cleared
by independent review. Parent command writes now have one bounded write/read
deadline; this is fault hardening, not a reproduced normal-protocol hang.
Registered focused context7 and cache/service-edge5 tests pass; actual headless
slider6 methods/32 assertions pass, with the old ordering failing its new check.
The earlier complete262-method native run preserves its three repaired cache
failures; no new complete final-suite pass is claimed. Public fixture generators,
dependency probes and guide now run without wrapper imports; current39 helper
checks and direct dependency comparisons pass on the prior normal helper/library
freeze. B1–B3 build configuration repairs are source-reviewed; Meson is unavailable.

Independent H1 review found and cleared concatenated-Segment and size-query cursor
restoration gaps. Reuse of the existing EBML parser remains the selected mechanism;
the native-parser alternative still lacks an exposed presentation eligibility
contract. No new architecture pivot is warranted before the pending bounded runtime
comparison. This is aligned progress with resource/UI execution blockers, not
contribution readiness. Preserve all previous acceptance thresholds.

Disk then fell below1GiB and finally to190MiB after owned build completion. All
new build/test/NAS acquisition launches were held; no owned process remains and
no file was deleted. Cam's separately authorized read-only storage review found
a duplicate211180KiB contrib archive and regenerable183564KiB staging directory;
the inventory distinguishes APFS accounting and protected evidence. The cleanup
request explicitly prohibited deletion, so no cleanup is inferred from the goal.
Requested restored headroom through the asynchronous input tool; existing Mac
unlock question remains pending. Goal is unfinished, with no submission/contact,
commit, installed-app replacement or bookmark work.

Learning-review hook considered because the run exposed a relayed interpretation
mistaken for measurement: retain exact artifact/hash evidence before diagnosing
another agent's result. Existing records already preserve the correction; no
memory or live workflow change is authorized or made. Next strategic checkpoint
remains2203/three substantive rounds; dependency/resource waiting does not count
as active iteration, and a stale deadline should be audited on resumption.

20261005-2134 — Loop-review checkpoint (due2133): aligned and progressing, with
native proof still dependent on Mac unlock. The normal FFmpeg9 contrib source
recipe now builds the installed helper; registered source tests and new native
seams run against the actual candidate. This improves public reproducibility,
but does not yet deliver a qualified app. Independent review exposed context/UI
notification reentrancy and an unenforced flat-Matroska boundary; the first full
native test run exposed malformed cache scalar handling. These are concrete
integration findings to repair, not reasons to reduce acceptance criteria.

Would choose the retained-helper approach again on current evidence. The
mechanistically different native-preparser alternative is covered by the recent
source-backed comparison and failed trimmed movie-time/eligibility discriminator;
reopening general core timing work would increase scope without resolving the
present contribution sooner. Reuse that comparison, preserve its prototype
results separately, and finish one complete helper-based app before considering
another architecture. For Matroska, reuse its established EBML parser rather
than inventing a second container parser; primary specification permits late
chapters and linked segments, so a flag-only metadata check is insufficient.
The bounded next comparison is an explicit eligibility guard with flat/ordered/
linked and incomplete-input fixtures, measured within existing worker bounds.

Continue already-authorized SOL6.1 medium integration and independent review.
Next useful deliverable is an isolated app built through normal commands with
material findings fixed, exact tests and a self-contained public source inventory.
Do not promote readiness without physical native/NAS/playback gates. No additional
permission or external handoff is needed for this course; no submission/contact,
commit or installed-app replacement occurs. Next checkpoint2203 or three
substantive rounds, retaining the cadence from2133 rather than resumption time.

20261005-2125 — Architecture selection and align review: the retained helper builds
against actual FFmpeg9; independent frame/time references, rotation/SAR and
reordered red/blue TrackNumber checks support a complete port route without the
larger preparser movie-time/eligibility prerequisite. Root inspected the paired
contact sheet. The alleged helper origin-collapse defect was an unverified relayed
interpretation; exact captures refuted it (origin0, actual2s, duration14s), so the
reports were explicitly corrected and no speculative code repair occurred.

Root selects normal contrib TrackNumber source patch plus focused affected-consumer
tests, avoiding a second private dependency recipe. Independent source review finds
no direct AVStream.id use by VLC avformat playback, while FFmpeg ID selectors and
stream groups need regression coverage. The frozen plan assigns disjoint SOL6.1
medium helper/build/context/service/UI lanes and preserves all behavior/readiness
requirements. Same-URI reopen receives a synchronous sourceEpoch so queued main
notifications cannot briefly reuse an earlier open's qualification.

Align advisory read Ideal/spec/state/graph/story/ADRs/registry and AGENTS. No Ideal
change or new acceptance threshold is needed. Existing 3.0 records remain scoped
history; no imported requirements/format matrix exists here. Apply plan/spec/state/
AGENTS updates under the authorized build workflow, then regenerate the graph.
Do not change old eval results; new master feature results need their own exact
candidate evidence before any readiness promotion. Contribution acceptance and
native proof remain open; Mac unlock request is pending. Next strategic checkpoint
remains2133 or three substantive rounds, not reset by the new implementation phase.

20261005-2106 — Loop-review checkpoint (due2103/three substantive rounds): aligned
but architecture remains at risk. The review began2101 during final track/runtime
diagnosis and is recorded now; next checkpoint2133 or three substantive rounds.
Process termination and orientation have useful bounded evidence; track rev2 now
passes the registered thumbnail test and eight real URI requests, selecting red
and blue in both execution modes and rejecting an invalid ID. External raw-file
tests exposed an existing enum validator excluding RGBA/ARGB; independent review
and both actual registered tests clear the narrow rev3 correction. Eight real
file requests also reproduce exact red/blue parity and reject invalid IDs.
Explicit-track private item
copy still omits opaque input data, so the general API is not submission-ready.

The MP4 experiment hit its declared trimmed-preroll failure and was reversed
exactly from the integration candidate, with its plugin/results preserved. Native
image conversion now demonstrates correct rotation without another product patch.
Those facts improve uncertainty, not the requested end-user capability. Native
UI proof is separately awaiting Cam's Mac unlock; the qualified app is unchanged.

Would repeat the native-reuse discriminator: it exposed real correctness gaps
before a broad UI port. Would not continue polishing unrelated core defects as a
proxy for full contribution readiness. Reused current primary-source comparison
with the retained FFmpeg mechanism and !7493/#29393. The alternative is explicitly
in the story and Cam delegated integration judgment; requesting new permission
merely to test it would invent a gate. Root assigns SOL6.1 medium builders a
bounded FFmpeg9 compile/frame/time/transform/identity/freshness comparison. Success
would justify the concrete master port plan, while failure can still force a
material core-design decision. No dropped acceptance criteria, contact, commits
or fork/public-binary commitment. The current ledger preserves every unmet gate.

20261005-1950 — Activated under Cam's explicit request to finish phases1/2, using
SOL6.1 medium builders and root-owned research/planning, stopping before upstream
submission. Created an active goal. Read Ideal/spec/state/generated graph, intake,
Story005 and ADR001–003; existing local contracts align with the Ideal. Required
sections exist; converted tasks to checkboxes. Current target checkout is a clean
mirror of canonical master2e358f3. Read-only sidecars inventoried local contracts
and build substrate. About12GiB was free; old build monitor is unsafe to reuse
unchanged because it deletes preserved work/build below its reserve. New build
must own its output and stop without touching old artifacts. Public API search
found open macOS preview MR!7493 (unresolved discussions) and shared-design
issue#29393; these are material new planning inputs, not evidence of acceptance.
No product code or installed app has changed. Next: inspect that direction and
qualify the unchanged upstream build before a bounded reuse experiment.

20261005 — Created from Cam's three-phase request. Inspected completed local
feature, ADRs, source footprint and generated graph; performed an initial upstream
planning scout and placed contribution before bookmarks. No upstream build/port
proof claimed.

20261005 — Planning validation: generated story index/graph includes unique ID005
and Story003's sequencing dependency; `make methodology-compile`, `make validate`
and `git diff --check` passed. Planning files only; no runtime validation claimed.

20261005-2009 — Loop-review checkpoint after contribution/source/build planning
rounds: aligned and progressing, with architecture and clean native build still
at risk. Actual progress is a canonical master pin, documented current contribution
rules, visible competing-work/ownership facts, portable9-media synthetic fixture
package, and a bounded internal/external preparser diagnostic. None is feature
readiness. The independent source review identifies narrower gaps than a new
preview engine: external requests lose selected-track item options; SIGTERM-only
process termination has an unbounded wait. PTS/format do cross external JSON, so
the disabled timestamp test alone is not proof of bad timestamps. Reuse the
published#29393/!7493 comparison and pinned source rather than invent another
architecture. Continue the unchanged build and discriminate core reuse first;
only measured repeated-open/NAS failure warrants retained-session API work.
No change to scope or acceptance, no maintainer-interest assumption. Next strategic
check by2039 local or three substantive implementation/experiment rounds, whichever
comes first; dependency waits alone are not an iteration loop.

20261005-2009 — Fixture/build setup evidence: SOL fixture builder produced9small
legal media files with independently decoded frame/time maps and30PNG examples
(total5.23MB), without external media or fonts. Root inspected rotation101x180,
SAR320x90 and blue second-track output. This qualifies fixture properties, not VLC.
The initial shallow clone made upstream's history-derived contrib key equal HEAD;
bounded deepen200 lets the unchanged official script derive15b71e3 and locate the
exact official macos-arm64 archive. Builder is using that upstream recipe under
reserve, retaining earlier failed/download/source-fetch logs. Source HEAD stays
2e358f3; no product code changes. `make validate` and whitespace check passed for
local planning/tooling, not VLC functionality. Native probe compilation pending.

20261005-2023 — First master runtime result: the bounded process discriminator
compiled with warnings as errors against unchanged arm64 libvlccore. Normal
termination completed; SIGTERM-resistant termination remained blocked at the
eight-second outer watchdog. Dedicated process groups were cleaned and verified
empty. This establishes a narrow process-API defect, not full preparser recovery.
Root compared POSIX and Microsoft termination contracts and requested an
independent minimal-fix review. Native source mapping confirms all four video
surfaces share the master progress slider; custom fullscreen reparents it, and
the old fullscreen XIB is not a live controller. The official build needed
documented ACLOCAL_PATH, Metal toolchain and NCURSES_LIBS environment repairs;
tracked upstream source remains unchanged. Thumbnail runtime proof and the full
architecture decision remain pending. Evidence and exact build commands are in
docs/evidence/story-005; no public patch or feature qualification yet.

20261005-2024 — Concrete first patch plan within the authorized phases: create an
isolated candidate checkout at the same master pin. SOL builder owns
`src/posix/process.c`, `include/vlc_process.h`, a new POSIX process regression and
its `test/Makefile.am` registration. Change the forced-kill operation to SIGKILL,
clarify existing semantics and preserve normal non-forced shutdown. A self-child
that ignores SIGTERM has its own alarm fallback, so the unmodified baseline fails
the expected-SIGKILL assertion without hanging. Verify default/forced shutdown,
I/O unblock, repeated kill and reap, with an outer bounded test group. Produce a
focused uncommitted patch under `patches/vlc-master/`; no author/sign-off claims.
Root retains integration and review. The change is independent of the broader
preview mechanism; no retained-session API or full port is authorized by this
technical decision alone. Main integration proceeds under Cam's phase1/2 request
only after the remaining discriminator supports its exact plan.

20261005-2033 — Loop-review checkpoint after three substantive rounds: aligned
but architecture is at risk. Unchanged master builds, all check targets compile,
and253 native XCTest cases pass; this is upstream substrate, not new feature
proof. The first isolated forced-termination patch passes its actual registered
candidate-core regression and independent source review. The132-request reuse
matrix now demonstrates three additional gaps: external chosen-track transport,
MP4 B-frame/edit-list sample dates, and lost picture orientation. Root inspected
the landscape output stamped4.000 and the correct rotated portrait reference;
callback time4.083334 is not acceptable evidence of actual frame time.

Would choose the native-reuse experiment again: it discovered concrete defects
before broad UI work. Reuse the current source-backed comparison with a retained
private decoder and with upstream#29393/!7493; no new engine is justified yet.
The small source-warm NAS comparison shows133–238ms core requests versus about4ms
retained-helper operations after separate startup; incompatible timing boundaries
and tiny source scope prevent a general performance conclusion. Preserve the
existing practical controls criterion and measure eventual caching/preparation.

Continue the small lifecycle patch and isolate PTS/format causes, prioritizing a
source-correct fix with regressions over guessed offsets. A constructor probe
already shows all eight input orientations reset to normal; MP4 timeline mapping
needs a bounded independent diagnosis. Do not broaden into a native UI port until
track/time/transform have a coherent correction plan. Sampled freshness has no
equivalent upstream service: compare a bounded native I/O slot with an identity-only
helper, preserving the fixed presentation deadline and stalled-resource cap.
No change to user goal or readiness criteria. Next review by2103 local or three
substantive correction/experiment rounds, whichever occurs first.

20261005-2034 — Next bounded correction plan: two disjoint SOL medium builders
will prepare isolated patches for the proven track and orientation defects.
Track ownership is `vlc_thumbnailer_arg`, preparser request ownership and JSON
transport, stack initializers and existing thumbnail/file regressions. A nullable
canonical ID preserves default behavior; explicit IDs are deep-copied, singular,
strictly selected on the private input, and never fall back to the default track.
Matched worker/core provenance remains required; inspect fail-closed handling of
missing selection transport. No arbitrary item-option serialization or shared
playback-item mutation.

Orientation ownership is the common picture allocation/clone boundary and the
existing image regression. Preserve the input orientation through setup while
retaining established plane allocation/crop behavior; verify all eight transforms,
cloning, and a real rotated thumbnail export. A buffer-only fix is insufficient
because avcodec clones the picture later. Review affected constructor callers and
existing conversion behavior. Neither patch may modify the baseline or the
in-flight candidate source. These small prerequisite proofs do not authorize a
guessed MP4 time correction, cache redesign or broad UI port. Root reviews before
the build owner applies the patches to the integration candidate.

20261005-2040 — MP4 scratch plan after first/later-GOP discrimination and primary
history review: SOL builder may remove only the seek-start-DTS condition from
edit-time subtraction in an independent source checkout. Keep signed preroll,
existing empty-edit handling and all other demux behavior. Produce an explicitly
experimental patch, then root review before integration. Qualify packet DTS/PTS/
PCR and real image times against independent media maps, including first/later
GOP, leading empty edit, positive non-keyframe trim, multiple-edit transitions,
negative-CTTS and unchanged controls. Stop on clock failure, shown preroll or an
unaffected regression; no compensating constants. This is a bounded reuse
experiment, not a claim that a common-demux fix or the preview architecture is
ready. Current orientation patch has independent source review with no material
findings and is being integrated for registered/image export tests.

20261006-1732 — loop-review: aligned but setup iteration had become the main
risk to phase2 completion. Since17:17, fixed-region capture established eight
scoped native cases; the separate absent-target acquisition adds a ninth. The
occlusion fixture did not actually occlude and remains unqualified. Reuse the
source-backed screencapture rectangle comparison and native visibility timeout
research: fixed display rectangles plus existing identical visibility settings
fit this foreground visible-controls measurement better than repeated reveal
choreography or attached-window capture. Freeze those mechanisms and proceed
with the existing20/arm prospective cohort after the narrow persistence/cleanup
repair; do not add another calibration loop or count setup samples as scores.

The corrected process collector enabled an actual baseline8s/central6s playback
capture with moving video and digital audio. Candidate011 stopped on a coherent
queue-layout width mismatch before observation, so no matched result exists.
The established alternative is ordinary Play Queue collapse on both arms, using
the pinned native action rather than guessed saved-state defaults. Fresh013 is
prepared without launch. One matched short pilot will distinguish stable shared
video projection and active preparation before any60s scores. Preserve fixed
source, capture, cache and timing criteria. Next strategic checkpoint after
three substantive rounds or18:02 active-work time; no scope expansion, cleanup,
submission or contact.

20261006-1734 — Root released one prospective controls cohort to the SOL6.1
medium native builder after independent scoring/scope review and a narrow
cleanup correction. Driver14706ed15e46e2e476751f83769dfca2f7cd3cbd21c4cfb8b2b2a9419dca802b,
planeedeac1e418ab9688a00e5e2f3a2e7d567edc7dfb5940ac95ba5861443520b41.
Three synthetic persistence-failure cases establish that owned retirement is
attempted and errors retained even when summary writes fail. Existing frozen
acquire/scorer/order/allowance unchanged. Sole UI ownership;555s active/45s
cleanup reserve/600s caller bound, first failure and no replacement. Playback
1750 successor independently clear but remains unlaunched pending controls
cleanup. Phase2 performance acceptance remains unqualified until actual results.

20261006-1736 — Remaining native closeout bounded by architecture sidecar:
retain007 four-surface rendering, preference/reopen/source-change proof. After
performance, acquire one matched main-playing drag (delivered physical input,
actual seek/continued play, candidate preview hidden during drag). Candidate
detached/custom edges need one click/drag, leave/hide, ordinary fade/reveal,
return/main hover without stranded panel; baseline discriminator only if needed.
Actual reader main navigation/activation uses existing Settings startup plus
Apple Item Chooser/default-action commands. Preserve spoken identity/cursor and
actual state transition separately from key-window/AX focus. Prior detached
outline evidence does not establish those outcomes. Apple primary sources:
https://support.apple.com/guide/voiceover/item-chooser-vo2724/mac and
https://support.apple.com/en-ae/guide/voiceover/vo4be8816d70/mac. No exhaustive
accessibility claim, new threshold or rerun of qualified rendering matrix.

20261006-1738 — Prospective control cohort PASS:48 valid attempts/20 scored
per arm; baseline141.765354ms versus candidate146.676000ms median (+3.463925%,
within20%). All raw48/order/median arithmetic independently checked by root.
No retries/exclusions, fixture unchanged, owned apps/preparsers absent after
cleanup, no cleanup/persistence errors,176.449s elapsed. Visible-controls paused
rendered feedback scope only, with default fade/occlusion/completed seek and
preview delay explicitly separate. One1750 matched short playback pilot released
after native ownership handoff; all further score gates remain pending.

20261006-1739 —1750 short playback pilot stopped on first setup prerequisite,
before queue action/capture/observer. Actual video-mode AX tree has no library
`Toggle Play Queue`; it has one depth3 AXCheckBox described `list view`,value1
and visible queue. Owned baseline49715/preparser49717 retired;013 remains unused.
General problem: native accessibility labels depend on presentation state.
Root and architecture sidecar traced actual video XIB575 NSListViewTemplate
button→togglePlayQueue:, controller709→same split controller120 collapse action.
Earlier library-toolbar selector was inapplicable. Prepare a narrow selector-only
successor requiring unique actual checkbox/state/queue corroboration, one press
if open, none if closed, settled poststate and matched projection. No alternate
label/defaults/coordinatefallback; preserve1750 failure and all timing/cache
criteria. This is a setup applicability correction, not playback evidence.

20261006-1742 — loop-review after controls/1750/1760 rounds: aligned, but
process-enumeration setup remains at risk of displacing actual playback proof.
Control20/arm is now qualified; actual matched projection is established by
1760 PNGs, and baseline central6s observation is valid. Candidate failed on
extra child54982 path0/ESRCH, with raw app/preparser/retained-worker path successes
before it. General class is process lifetime races, not decoder failure.
Established alternative to whole-snapshot retries is bounded lifecycle-aware
enumeration: Apple XNU PIDPATHINFO cannot return a live path for an exited/zombie
process, while BSD-info/ps can still report its zombie state. Reuse strict app
and retained-worker identity brackets, but record unknown short-lived extra
children explicitly instead of pretending all enumerated children stay live.

Research sources: Apple XNU bsd/kern/proc_info.c2046–2061, libsyscall/wrappers/
libproc/libproc.c249–266, local SDK errno ESRCH3/SZOMB5 and Apple waitpid manual.
Builder prepares isolated narrow correction plus owned unreaped/reaped child
applicability test and rejection matrix. Only one selected lifecycle check for
extra-child0/ESRCH may confirm absence or sameidentityZ; live/reused/permission/
malformed/retainedworker failures stay failures. No executable inference from
truncated names, counted unknown resources, whole-snapshot retry, score change
or production change. Root/independent review before applying. Preserve1760/013;
fresh014 avoids cache reuse. Next checkpoint three substantive rounds or18:12
active-work time. No additional calibration polish beyond this material race.

20261006-1747 — Reviewed lifecycle correction applied with explicit candidate
retained-worker PID pin before interval snapshots. Development adapter source
f9edcf12dd5d5691016ebfe9df3416a43bd199dc9c83696ebc32b0a1dfe7d16f;
successor freeze8081470ba9ba3d09ffd0cd4dec24640a7d7da47c198edd34ade137b6bf3f70b4
preserves old source/freeze. Root checked full diff: reviewed collector plus
minimal caller pin, and one exact014 allowlist addition. All25 pins match;21
offline checks pass. One1770 fresh014 short pilot released, same8s/central6s
capture,85active/35cleanup/120caller, first failure/no automatic retry.
No production/public source, scoring or cache policy changed.

20261006-1748 —1770 both short-pilot arms qualify setup, not performance:
central6s/8s capture; moving ROI152/153 hashes,600/600 RMS windows above−60dBFS,
video144/audio70 counter advances and zero loss. Candidate targets12→16→22→27
with unchangedworker65379 and matching actual sourceID1/count1/single/track−1,
inside-bin deadlines and payload integrity pass. App/preparser/worker cleanup
confirmed,29.216s elapsed. Root inspected both exact display PNGs: matching video
projection/letterbox/controls, actualbar866; fixed ROI contains identical narrow
left letterbox plus moving source content. No ROI/criterion change. Audio callback
delivery gaps449.8ms baseline,518.5/787.7ms candidate retained, with no reported
audio PTS discontinuities/silence/screen gaps; do not claim causal VLC stalls or
a performance pass.013/014 caches preserved. Prepare original3×60s paired
background-only comparison AB/BA/AB using reserved fresh008–010; no more pilot
calibration. Actual functional drag uses documented CUA App.drag; inherited
registered hide-during-drag remains separate from unobserved held-state pixels.

20261006-1755 — Strategic checkpoint: aligned and now progressing end to end.
The lifecycle-aware collector's owned-child applicability and fresh014 short
pilot removed the last observed setup blocker. Reuse the recent source-backed
process-lifetime technique and native collapsed-queue projection comparison;
manual visual inspection alone cannot provide the fixed60s clock/audio/cache
witnesses, while a newly redesigned observer would discard the qualified pilot.
Choose unchanged p.trial directly with a small serial six-run wrapper, preserving
all gates and observer limits. Root/independent review clear final driver
e3b64e0d6764008dc4e43573fa42a7890f15990183a354a9b446ca7619fab0fe,
plan2c34214c1f3b2442f6d3eecb3630cf04403983943f49907db90a221bd20df629,
caller98fe3c641d744aff861d2a22caca1bb3c9f68afd4064bc9d564b41553ba1f240.
Preliminary caller copied stale pilot keys; final closure fixes them before launch
and records exact-path/hash/key checks. All33 pins/19offline checks pass.

Root released ONE AB/BA/AB matched60s cohort using012 and fresh008–010;65s capture,
620active/100cleanup/720caller,1GiB floor, source/worker/cache inside-bin guards,
no input/hover and no replacement. Collection is unscored until root paired
review of audio/PTS/drop+1percentagepoint/resources/observer limits and PNGs.
Stop on first failure; do not retune from collected results. Functional edge
packet is prepared offline. Next review after3substantive rounds or18:25 active
time; wait/collection does not authorize extra work or submission.

20261006-1757 —1800 cohort stops on baseline empty-window prebind before media,
input, observer or candidate. Alive exactbaseline79229 has UID-owned RC socket,
empty queue/requestedstop5/volume100; visible-owned CG enumeration remains[]
within8s. Cause unproven. Root native inventory41apps/noerrors shows desktop
accessible, not a lock attribution. Owned79229/preparser79231 absent after
cleanup; allfive remaining arms unattempted,008–010 untouched. Preserve raw
prebind attempts/inventory, not performance samples. Investigate standard
background native-app activation before unchangedwindowreadiness, not longer
waits/guardrelaxation or CUA autolaunch. SourceVLCMain.m358/366 creates/orders
mainwindow at launch;467 handles reopen. SDKNSRunningApplication notes default
activation brings main/key windows forward. Existing exactdomain/path/PID utility
activation is a candidate setup action, not evidence of visible readiness itself.

20261006-1759 — Narrow1801 successor released once after root review. Existing
exact-PID/path activation request is allowed at most once only after the typed
prebind NoVisibleOwnedWindow failure has already proved empty stopped RC/socket
ownership. Strict native app identity is bracketed before/after, no worker before
admission, and original8s deadline is checked after activation and successful
prebind. Guard2243/remaining pipeline unchanged; request Boolean is not readiness.
SDK activation behavior/sourceVLCMain researched; cause of1800 stays unproven.
Finaldriver6197e34e7006174f9ba0058d72b96d3b7b34cd2ba5f8dfb8fb58fd4c777cf28b,
plan7a0f8d3928d50ad3ed96b2f99b2924d773520e071db582effd0d9ee1833b6e90,
callera5f50bee7752b1ad93c16f47d2b79c4863dd8f1a84c8347d006e05b9ab83e4b9.
Fresh output/transport/socket paths and008–010 caches, same six-run order and
65/60s capture/inside-bin guards/720s caller;14offline closure checks. No extra
calibration, scoring change, failed-run replacement or source modification.

20261006-1808 —1801 six matched central60s arms collected in456.010s, fixed
AB/BA/AB order/no replacements. Allpaired lost-picture rates0%→0% (0pp change),
allaudio-buffer losses0 and digitalaudioRMS/PTScoverscentral60 withoutlowaudio
intervals/PTSdiscontinuity. Allthreecandidate workers addaliases in allsixbins.
Independent read-onlyanalysisda32ad3ecdab90d37fe914845791cac38d992271d586b45c505850b14715df60
retains sampledCPU/RSS/observerlimits. Root does NOT accept a cleanplayback or
submission-readiness claim: P1candidate has133.332ms screenPTSgap; more critically
P3candidate5678 exits−11(SIGSEGV) duringquit, versusfiveexit0. All sampled owned
parents/preparsers/workers absent, but absence is not cleanexit. Originalanalysis
only requirednon-null childexit; separate interpretation correction preserves
that limitation without rewriting results. Nativeowner investigates exactowned
crashreport/stack read-only; no retry/sourcepatch yet. Independent functional
edgepacket released to soleUIowner aftercleanup, with explicitexitcode checks
and firstfailurestop; currentphase2 remains InProgress/readinessheld.

20261006-1810 — Revision10 source-guide-only package closure passes root exactdiff
comparison and independent review. Final59-file treecc0ec69e8be5ba2e60ccae6ea095b471b500a6ff;
0002b2661e2a585ed4f543c97ba0f50ce401637dbc1b8404fe85572cf866a8f6875e;
manifest86d3cd4b8105d684952bb613b191ffabacce7b5bb8b84a4bff83dbcba4b23fe3.
READMEc0a75f2f508066ee4d82daa7f10253c0fa2c498c3d956e0022efdce55cce428f
replaces obsolete Maclocked prose with stableverification instructions. Actual
one-hunk diff equals approved proposal; fresh pinnedbaseapply reconstructs exact
tree/modes/blobs, candidate/reproduction59hashes match. Revision9 preserved;
0000/0001/0003/images/runtime unchanged. Wrapper13artifact/privacy/link/source
check passes,4271930B; final metrics/reader/readiness updates remain pending.
Source-guide proof does not clear shutdown/screen evidence holds.

20261006-1811 — loop-review after startup correction/fullcohort/crash-discovery:
aligned but readiness is at risk from a real shutdown failure, not a missing
metric. Controlsqualify; six60s intervals provide0pp drops/digitalaudio evidence
within capture limits. Do not repeat them to erase the SIGSEGV or133msPTSgap.
Faultstack concurrently shows dlclose/pluginUnmap/moduleEndBank and conditionwait
returningthroughunknownaddress. StaticUPnP WorkerThread/gMiniServerThreadPool
offsets strongly align, but usedImages lacksdefinitiveUPnPmapping; no named
thumbnailframe is notfeatureexoneration.

Compare continuingfeaturepatching with established orderly-thread-quiescence
before dynamicunload. PinnedUPnPwrapper destructor callsUpnpFinish, discovery
closesjoinownsearchthread, libupnp1.14.31 stops timer/server/pools; detached
worker logicalcounts do not independently prove OSthreadreturn beforeunload.
VLC pluginUnmap requires nofuturepluginuse. These primarysources justify a
small attributiontest, not a speculativefix: threefiniteuntouchedbaseline
normalplay/quitcycles, actualprequitmodulemap/briefthreadsamples, stoponmatching
repro orbound. Threecleanquitsremaininconclusive. Keepmodule/defaultselection,
noUPnPdisable/unloadpolicychange/performance retake. Prepareoffline, then serial
nativehandoff afterindependentedges. Existingphysicalinteractionproof remains
necessary; revisedstablepublicsourceguide is verified withoutnewruntimeclaims.
Nextcheckpoint3substantiverounds or30active minutes; preserve allfailuretruth.


### 2026-10-06 18:29 Edmonton — bounded shutdown attribution release

Root reviewed the frozen attribution driver, plan and caller; released one maximum-three-cycle unmodified baseline012 acquisition to the sole native owner. Same actual owned Popen SIGTERM shutdown as1801, default UPnP, legal7200s fixture,76s lifetime, pre-quit loaded-image ranges/UUID and1s thread sample. First setup failure or nonzero exit stops remaining cycles; three clean exits remain inconclusive. Diagnostics perturb the process and cannot supply a performance score. Outer330s/active280s/cleanup50s and1GiB floor retained. Candidate crash and original numerical results remain unchanged. Offline existing-pointer drag insertion reviewed; compilation/packet preparation authorized, runtime held until serial handoff. No new input framework or CUA coordinate variants.


### 2026-10-06 18:31 Edmonton — attribution diagnostic stopped; native handoff

Frozen shutdown attribution001 stopped in cycle1 when /usr/bin/sample exceeded its5s bound. vmmap and strict source/process identity were acquired; no completed planned cycle or crash attribution is claimed. Exact baseline10615 exit0 and sampledpreparser10624 absence are retained; cycles2/3 unattempted. No retry or sampler repair released. Root handed sole UI ownership to the reviewed002 existing-CG-pointer edge packet, with baseline main drag first, no gesture retries, actual strict source/target plus5s continued-video gate, exit0/absence between phases and finite reader restoration reserve. Crash readiness hold remains.


### 2026-10-06 18:33 Edmonton — loop-review: preserve observations, avoid proxy repetition

Aligned but at risk: completed numerical performance and native features are useful, while two new failures belong to diagnostic/setup evidence. The sampler timeout gives no completed baseline cycle. CGdrag physically reaches burned03:18/frame4752; later strict play3/time210 supports continued playback, but the immediate RC response was not persisted before its failed target assertion. Root inspected actualPNG and retains both observed behavior and frozen-gate incompleteness. No baseline retake. Independent remaining002 cases released within the original global deadline, correcting only persist-before-assert ordering.

The established alternative is direct reproduction of module shutdown/quiescence using existing headless VLC service-discovery entry points, preserving wrapper release/UpnpFinish/module unload. This can positively identify a pre-existing mechanism; clean runs still cannot exonerate the candidate. Bounded read-only applicability is delegated before any execution. Reuse pinned UPnP shutdown/history research rather than repairing the sampler or guessing dependency fixes. The133ms screenPTSgap is an observation hole with no demonstrated feature-attributable >100ms stall; retain digitalaudio/drop findings but no uninterrupted-video/no-stalls claim. Actual shutdownSIGSEGV remains material. Next strategy check after three substantive decisions or roughly30 active minutes; waits do not count.


### 2026-10-06 18:35 Edmonton — source-backed unscored seek observation correction

Candidate main CGdrag reaches visible03:20/frame4800 but immediately saved oldrc play3/time32 remains preseek; cleanexit26420/preparser26422absence. The immediate gate fails and5s gate is unexecuted; no main retake. Pinned oldrc/player/timer/input callbacks establish asynchronous currenttime versus requestedseek. Root approves bounded3s/200ms explicit condition waiting only for unused surface cases, preserving every reply and original strict identity/source/state/target tolerances; singlegesture/noresend then5s core+burned-video advance. Reader continues independently within the original900s whole/360s reader bounds. This qualifies eventual convergence only, never a numeric seek-latency result. Research source anchors and decision are recorded in upstream-contribution-scout.


### 2026-10-06 18:38 Edmonton — unused native cases and supported shutdown substrate

Reader baseline SettingsOFF→ON did not yield an actual running VoiceOver process/chooser. No VO-Space action invented and no candidate startup retry. ActualOFF restoration and baseline31283exit0/observedchild absence retained. Treat actual reader navigation as unavailable, with existing AX/source evidence separately scoped. Detached candidate36533 physicalvideo is clipped before any seek input; root inspectedPNG, and setup refusal/strictplay/source/exit0 are preserved without feature attribution. Independent custom case continues within original deadline. One ordinary detached-window resize may test the unused source prerequisite later, with no gesture resend or vout patch.

Headless substrate audit rejects unsupported assumptions: --services-discovery has no pinned-master consumer, and UpnpInit2/Finish are local plugin symbols. The existing publicLibVLC discoverer test supplies a supported new/start/stop/destroy/release lifecycle. SOL builder compiled an ignored signal-flag-only host against actual packaged baseline libs; root reviewed source/caller/modulemapping/positive-only interpretation and90s bound. Execution awaits nativeUIquiet; no repeated clean-run ladder or dependency workaround.


### 2026-10-06 18:45 Edmonton — finite native closeout and direct API result

002 closes with sixexit0/all13sampledidentitiesabsent. Customclick/drag+5s/reparent passes; instantmainRC and detachedAXprojection assertions remain incomplete/uncalibrated, not feature defects. Independent source/control review supports scoped common-control inheritance and earlier007four-surfacehover; no repeatedgesture matrix added. ActualVoiceOver startup is unavailable onbaseline/OFFrestored, noreaderpass. See native-edge-closeout-002.md for exact limits.

PublicAPI UPnP host50305 starts/maps/stops/destroys/releases actualbaseline libraries and exits0/absent. Intended5s hold misses because nativeCLOCK_MONOTONIC differs from Pythonmonotonic by~7.47s; actualstart-to-stop1.376911s. Preserve protocol deviation; no crash reproduction or exoneration, no clockrepair/cleanrunrepeat. Next bounded strategy review considers existing debugger inspection of thread quiescence immediately before module unload instead of more clean proxies. OriginalcandidateSIGSEGV remains the sole material runtime readiness finding; screenPTSgap remains noncausal observation limit.


### 2026-10-06 18:47 Edmonton — strategy checkpoint: direct quiescence inspection

Aligned but at risk of diagnostic activity displacing submission readiness. Useful gains: combined nativeordinarycontrol proof is closed at documented scope; no new featurecontrol finding remains. The unchangedpublicAPIhost demonstrates supportedUPnPlifecycle but its clean short exit cannot explain GUIshutdown. No further sampler/clockrepair/cleanproxy runs selected. Established alternative: debugger read-only inspection at the identifiedUPnP plugin's pre-dlclose boundary, inspecting actualmoduleidentity and allthreadstacks rather than hoping for a randomfault. OfflineDWARF/symbolinventory establishes substrate; builder prepares one bounded packet only, while sourceinventory checks GUI-reference teardown difference. Positive liveWorkerThread-at-unmap violates pinnedbank.c no-longer-used precondition, but originalfaultcausalattribution and lastloaderreference remain separate. Missingidentity/permissions/breakpoint/deadline stops inconclusive; no targetfunctioncalls/productioninstrumentation/permissionchanges. Nextreview after acquisition or three substantive decisions, with originalgoal and no-submission stop unchanged.


### 2026-10-06 18:51 Edmonton — concrete untouched-GUI ownership defect

SOL source audit and root directread verify GetMediaSourceownedref→wrapperHold→singledeallocRelease imbalance in pinneduntouchedmacOSprovider. ProviderDelete does not drain discoveries; interface/provider teardown precedes modulebankunload. EmptyGUI LANdatasource initialization occurs before anyprivate media. This materially changes diagnosticframing: publicAPIhost's explicitdestroy bypasses the suspectedGUIleak, so no moreproxy repetitions. OfflineLLDBpacket redirected to exactbaseline012emptyGUI, identifiedUPnPunmap/allthreadstacks under one120souter/90sactive/30scleanup bound. Read-onlydebugvariables must establish actualpluginidentity; no targetfunctioncalls, registerguess, permissionschange or fallbackloop. No runtime released until concretepacketreview. Originalfaultattribution stillopen; sourcebug alone does not prove PID5678cause.


### 2026-10-06 18:53 Edmonton — direct GUI debugger discriminator released

Root read entire frozen SBinspector/caller/plan and released ONE acquisition to SOL process-review owner as soleVLCruntime actor. Exactbaseline012emptyGUI, freshignoredconfig/userdata, no input/media, actualUPnPmapping≤20s then5s ownPythonclock andONEpassed-throughSIGTERM. At vlc_dlclose require actualcore/EndBankstack/handleargument and currentDWARFUnmapplugin or EndBanklib matching exactUPnPpath; ambiguity/optimizationfailure/permission/API/deadline stops. Retain actualmoduleUUID/ranges/allthreadPC/backtraces/WorkerThreadreturncontinuations and optionalFinishresolution/count.90sactive/108souterwait+12scleanup,1GiBfloor/64MiBcap; no inferiorfunctioncalls/registerguess/permissionchanges/fallbackloop. OwnedinferiorKill onlyforSTOPcleanup isdistinctfromcleanexit; knownPID freshabsenceverification required. Publicsource/patches/runtimecodeunchanged.


### 2026-10-06 18:57 Edmonton — debugger unavailable; existing lifecycle trace alternative

ONE LLDB acquisition stops inconclusive at108.084s caller timeout insideSBTarget.Launch; no innerresult/moduleidentity/stacks/Finishcounts exist. Owned55775inferior/55756LLDB gone; ownorphan55776debugserver required separatelyreverifiedSIGTERMcleanup. Wholeclosure130.218s exceeds120s target and is disclosed; no permissionchanges/input/relaunch. Closure18838a2d2bcea3dc546323656e83d4fc0bd407eb9ad2ef15d584dcd84a5204bc retained.

Strategycheckpoint: sourceownershipfinding materiallyimproves diagnosis, but new debugger mechanics are not the outcome. Stopdebugger/sample/clockrepair and cleanproxy repetitions. Existing module_unneed verbose lifecycle logging offers a different established observation mechanism on the actualGUIpath. Boundedapplicability asks whether actualUPnPinit/mapping plus missingCloseSD/removal acrossnormalshutdown, together with the provenownedrefimbalance/coreunmapordering, can demonstrate existinglifetimefailure without implyingexactoriginalcrashcausality. No runtime released yet. Rootmustcheck logging-completeness/absence limits beforedecision; no inferredpass from silence. Originalsource/runtimepackageunchanged, goalactive/phase2open.


### 2026-10-06 19:07 Edmonton — root readiness judgment

Independent architecture review verifies all eight ownership/UPnP/cleanup files unchanged and the baseline trace activation/teardown facts. Root accepts the concrete upstream owned-reference defect plus activated-path corroboration as a documented baseline limitation, without inferring exact original crash causality. Stop diagnostic-tool repairs and runtime repetitions. Ordinary-control preservation is qualified by combined actual native and unchanged shared-action evidence; actual VoiceOver remains unavailable. Final wrapper reconciliation and proportional validation are the remaining mechanical handoff work. Story stays InProgress because phase3 is untouched.

### 2026-10-06 19:09 Edmonton — final validation and authorized halt

Final13 public artifacts/checker/source-proof receipt hashes independently rechecked by root; all match. SOL6.1 medium final semantic review finds no material current-truth contradiction. Source revision10/four patches/two PNGs unchanged; direct wrapper privacy/provenance/links/cap checks pass. Fresh methodology compile/check and33-skill wiring pass. Full makevalidate hangs at scaffoldGitroot query; Gitstatus/version and previouswhitespace hang, so no fresh whole-checkout diff/untracked/whitespace or fullvalidate pass is asserted. Prior exact59-file apply/source and independentcode/build/test reviews remain applicable. Root requested termination only of exact owned blocked verification processes; uninterruptible Git may retain pending termination, not native runtime. Phases1/2 complete with disclosed limits; goalcomplete and halt before phase3. No commit/push/contact/submission or bookmarks.


### 2026-10-06 19:21 Edmonton — requested separate installed preview

Cam asks for an installed final candidate and change/review explanation. SOL6.1 medium build owner installs a metadata-only APFS clone as ~/Applications/VLC Timeline Upstream Preview.app, version4.0.0-dev, unique org.videolan.vlc.story005.upstreampreview domain.997file/10symlink/398code-section and strict signature checks pass; only intended Info.plist/main signature bytes differ. Both existing user3.0.24 preview and system VLC full before/after manifests unchanged. Fresh settings/cache/userdata domain remains absent; no launch, default-handler registration or user-profile modification. Root verifies receipt hash/path/identity/version. See installed-upstream-preview.json. Public source/patch series unchanged and nothing submitted; whole story staysInProgress forphase3. User may open the separate app to check familiar local/NAS hover, media/track switches, fullscreen/control behavior and quit/reopen, with known shutdowncrash/disclosed qualification limits retained.


### 2026-10-06 19:32 Edmonton — authorized bounded reviewer-improvement loop

Cam requests up to8hours of streamlining, standards/reviewer burden/bug audit and testquality reduction, using loopverify/hourlyloopreview. Root records exactUTCdeadline09:32:48Z and hourlyanchoredcadence; firstfreshSOL6.1medium parallelpass isfind-only with disjointshards and separatebaseline snapshot. CurrentGitstatusworks,17.12GiBfree. Earlierhalt superseded onlyfor thislocalreview/improvement task; no submission/contact/commit/push/installedappoverwrite. Readideation for boundedreviewerbrainstorm. Previousqualifiedrev10 preserved; neverinherit changedruntimeproof.

20261006-2000 — Reviewer-improvement loop ends early after local convergence. SOL6.1medium builders fix terminal-completion reentrancy and helper false-positive checks; remove dead parser state/buffers, duplicate hover execution, copied nonproduction geometry coverage and redundant Automake result entries. Five-part revision11 splits nativefoundation/activation with actual intermediate normal compile/link/265tests1skip; final284unique283pass1skip and helper77pass. Fresh full59path source and15artifact package review find no material local issue. Exacttreef8f7d0fdb46c1ae25ba94049143d12ecb7daf96c; installedapps unchanged. Standards correction keepsphase2 open; no mandatory-check waiver/newGUI/crashfix claim. Nothing submitted/committed/pushed. Finalvalidation owns current handoff; revision10 evidence remains historical.

20261006-2001 — Cam requests another loop explicitly adding previously reported blockers and an active goal. Createdgoal; rootreopens boundedscouting for distribution/test configuration and defects, actualshutdown/lifetime evidence, currentisolatedapp/native/reader proof, and locallyattainableplatform checks.8hhardstop10:01:51Z/hourly03:01:51Z. Prior59path/fivepatch revision11 cleanreview retained as baseline, not wholephase2 completion. FourSOL6.1medium find-onlyscouts released, builds/UI awaitrootconcreteplan. No furtherpermission needed for in-scope follow-through.

20261006-2023 — Expanded blocker loop: normal incremental build passes; unreached full test-directory traversal94/94 incl clock/TLS/GL/provider ownership passes, helper77 passes. Full normal top-level check remains failed at one existing service fixed-sleep assertion (284unique:282pass/1skip/1fail). Fresh67-path source review clean; accepts causal-barrier/bounded-completion repair in existing test only, exact original runtime cause unproved. Revision11 publicpackage preserved; plan feature12 plus separate five baseline prerequisites. Conditional private shutdown marker build prepared without GUI/live-source/installed-app changes. See blocker-resolution-loop.md for freeze/receipts/ownership and next fresh full review. Phase2 remains open, goal active, no submission/contact/commit/push.


20261006-2120 — Expanded blocker loop final67pathround4source review isclean. Accepted schedulerstatepartition correction and compactexistingtestchanges have original4assertioncounterfactual/focusedpasses. Normal015package/sign/source/helperrelocationcorrespondencepass; no currentnativeGUI/reader/playback proof becauseMaclocked. Correctcomplete-metadata registeredsmoke004passes8.371s; fullnormalcheck005passesonce175.118s withnative284=283pass/1optionalskip,testdir94/94 andallofficialregisteredchecks, includingtopGUI. Earlierfailedstacks/evidencepreserved; originalSIGTERMcausalityunresolved. RootreleasesONEcompletefreshconfigured006distcheck withmechanicalnestedprelaunchguard forwardingoriginaldriver. Feature12/fivepatches plussixbaselineprerequisites combinedtree4ff3c806956c25da360d89a1281331064eea849f remainstaged; public11preservedunchanged. Nextstrategyreview04:01:51Z/hardstop10:01:51Z. Phase2open/no submission/contact/commit/push/installedchange/cleanup.


20261007-1935Z — Cam's18:56Z yes reopens three bounded lanes within20:43:12Z. SOL6.1medium builders complete one timing correction/trial, one private SDK observer/control/trial, and one ignored-stage wrapper text/hash cycle; root reviews and owns CUA. Custom002 qualifies actual hover/pause/resume/main-return;240s composite deadline leaves returned-main hover and normal Quit unqualified. Waitobserve001 exact016 actualCommandQ0/noSIGTERM captures five pre-unmap callintervals, allcompletionunknown; historical004 crash remains unresolved. Ignored28-artifact/12-patch stage passes both existing checkers with shorter readable unexecuted hostrecipe, source72/app/patch/public11 exact. VoiceOver deferred untilCam canhelp. No producttest additions/sourcechanges/publicpromotion/contact/submission/commit/push/install/cleanup. Phase2 checkbox staysopen; final narrow diagnostic adjudication/currentreadinessledger own closeout.


### 2026-10-07 22:56Z — final focused UI trial stopped after negative rendered hover

One unchanged016 trial establishes actual custom-fullscreen entry and return to the original main window with typed playback continuing. The one existing native hover probe passes routing/ownership/capture, but root's rendered full-window image shows no thumbnail or Keyframe caption after return; cause unknown. No retry or source fix follows. Reader-with-preview remains unattempted: human availability unanswered, VoiceOver never enabled. Root ONE Command-Q exits0 without SIGTERM; parent absent, descendant scope limited to no safely derived identities. Source72/app/fixture/899 history files exact; resource floor passes. Historical004 remains user-accepted deferred. Phase2 stays open, public11 preserved and nothing submitted. See [focused closeout](../evidence/story-005/final-ui-closeout001.md) and its final receipt for the separate native-routing, rendered-product and shutdown conclusions.

- 2026-10-07 final package closeout: SOL6.1 medium prepared local revision13 after root plan and diff review. Exact 28-artifact source/application/privacy/identity checks pass unchanged; twelve patches and both images preserved. Current UI negative hover and narrow clean Quit are disclosed. Phase2 remains open; no contact/submission/commit/push. See `patches/vlc-master/contribution-series-revision13/CONTRIBUTION.md`.


20261008-0033Z — Root-reviewed autohide correction changes current candidate controller only; other71 R8 source bytes/all72 modes exact and affected pre-edit backup preserved. Actual-method AppKit probe compiles and11 cases pass, five old failures reproduce then pass corrected. First failed pipe-capture run preserved; identical-binary direct-file completion supports plumbing hypothesis without causal proof. Historical R8/full009/010/apps016/revision13/public11 preserved but do not qualify changed source. Native/observed-fade cause and Phase2 remain open. Fresh30min release00:29:21–00:59:21Z only; full build held>=5GiB vs~1.6GiB. Diagnostic plan only; no runtime/build/instrumentation/cleanup/contact/commit/push/install. See autohide-correction001 evidence.


20261008-0053Z — Fresh bounded continuation ends01:53:03Z with no prior-budget reset. Root-reviewed normal017 adapters preserve source9 (72paths/one controller change), old016 and exact APFS prebuild package/install copies. ONE normal package attempt stops25.718s at conservative1GiB volume-free-drop guard: owned make39653 SIGTERM exit−15, drop1,287,598,080B/min4,590,829,568B. Actual controller compile/plugin link logs are partial observations only; normal build partly updated/macos-install incomplete, no packagepass/017app/isolation/relocation/native. Poststopfree~3.0GB, no exactPID/PPID/PGID39653, filesystem-consumption attribution unknown. Bounded Python/Apple research recorded; no alternatebudget implemented, no retry/buildbelow5GiB/guardchange. Historical009010/revision13 remain source8 evidence. Goalactive/incomplete/Phase2open; root separate prerequisite preparation has no publicpromotion, human/resourcequestionspending. No runtime/source/cleanup/install/contact/submission/commit/push. See [attempt report](../evidence/story-005/autohide-build017-attempt001.md).

20261007-2008 — resource resume: Cam explicitly requests continuation after other storage work. Fresh free7.7GiB clears5GiB admission. Root releases bounded preparation for normal017 checkpoint-aware successor; runtime/build execution remains behind root review. Previous01:53Z window expired; new02:08:17–02:48:17Z continuation consumes remaining eight-hour goal accounting without reset. Source9/static72 composition and retained-object dependency evidence reused, not runtime readiness. Normal package, fullsource9 gates and one physical mainhover remain the critical path; no wrapper-only substitute, no shutdown004 reopening, no installed/public/contact/commit/push/cleanup change. See current readiness ledger and continuation receipt.

20261008-0237Z — Corrected source9 normal017 official package PASS/signature/fullInfo/all398; exact corrected checkpoint object/plugin reused. Fresh fullnormalcheck PASS registered compat6/core29+1skip/modules25/integration94/topsmoke; nested284native=283pass1skip, not additive. Source72/headers989/appmanifest exact. Originalisolate fails840s reserve and remains failed. Root-reviewed distinctread-only retained017 qualification passes7.248s with fresh398section/hash and796rawUUID evidence pins, whole-source/old016/prebuild preservation and identity/security boundaries; separate helperrelocation passes2.284s/twofixture headers+pixels. Source9distcheck NOT LAUNCHED strictadmission2.127slate; nooverride. No native017/observedfade-fix proof; humanavailabilityunanswered/fullnativeadmissioncutoffpassed. Phase2/goal incomplete, historical004useraccepteddeferred, no furtherbuild/runtime thiscontinuation. Preserve public13/history/apps/media; no cleanup/install/contact/submission/commit/push. See [successor report](../evidence/story-005/autohide-build017-successor001.md).

20261008-0241Z — Automatic continuation retains02:48:17Z stop/no clock reset. Remaining useful static proof: ownedbare/index/object13patch composition PASS12.971s/2.86MB; finalsource9treea568215775ffa7ddd6bbad393d466d79ae72e131 from pinnedbase2e358f30. Root independently checks72entire source bytes/modes/GitblobIDs/exact changedpathset and31preserved patch/public13/index inputs. New intermediate/fulltree IDs recorded for futurestage014; no public promotion/commit/source/build/native changes. Source9fullnormal/app/helper green; complete distcheck/current physicalhover still pending; Phase2/goal incomplete.

20261007-2051 — Cam explicitly approves additional45minutes,02:51:50–03:36:50Z. Prior8hgoalusage/failedisolation/refuseddistadmission retained, noreset. RootcoordinatesSOL6.1medium for complete source9distcheck and onecorrected017 physicalmainhover ifhumanavailable; humanavailabilitypending. Reuse exactgreen normal/package/independent017/helper/staticfulltree proof; no source/install/contact/submission/commit/push/cleanup. Goalactive/Phase2open. Authorization under work/story005-extra45-20261008-025150/.

20261007-2104 — Explicit extra45minute continuation: source9 fresh configure55.819s plus ONE complete conventionaldistcheck611.170s PASS through finaldistcleancheck/archivebanner; no guard/manualcleanup/testoverride. Root verifies source72/PO111/app017 andactualreceipts/loghashes; registered6/30(29pass1skip)/25/93+topGUI and284nested(283pass1skip), notadditive. Corrected017 read-onlypreflightPASS/runtimeFALSE/humanavailabilitypending; fullnativeadmissionstrictbefore03:21:50Z, hardstop03:36:50Z/prior8husagepreserved. Ignoredstage014wrapperPASS/concisedocsupdatepending;3avoidablefeaturehelperwarningscleanupunapplied/source9frozen. Phase2/goalOPEN; no install/cleanup/contact/submission/commit/push. See docs/evidence/story-005/source9-distcheck-extension001.md.

20261007-2112 — Ignoredstage014 concise29artifact wrapper checker003PASS/584wordcover; all13patches/2PNG/public13/source72 exact, fullunexecutedrecipe retained and canonicalaggregateapplication corrected. Privatewarningprobe002 removes3warnings but varianttext differs32bytes; no actualproductpatch/helper/nativeexecution or behavioral-equivalence claim. Humanavailability remains pending for preflighted017; Phase2OPEN, stop03:36:50Z/nativeadmissionstrictbefore03:21:50Z unchanged.

20261007-2115 — Camexplicitlygrants3h03:15:55–06:15:55Z; prior8h+45minusagepreserved. Rootreleases SOL6.1medium exact3temphelperwarningcleanup/source10freeze/preservation; freshhelper77/fullnormal/dist/package/currentapp qualification tofollowrootreview. Source9/017/stage14/public13/historypreserved, native017heldoncandidatechange; no actualavailabilityinferred. Phase2/goalOPEN; no install/cleanup/contact/submission/commit/push. Authorization work/story005-three-hour-20261008-031555/authorization.json.


### 2026-10-08T03:35Z — source10 warning cleanup and affected gates

Within Cam's explicit three-hour window, SOL6.1-medium builders applied only the three approved helper temporaries and preserved source9/app017/history. Fresh fullnormal and full77 pass against exact new helper; targeted Wbad-function-cast warnings are zero with diagnostic enabled. Independent changed-slice review is no-issue; actual13patch source10 composition matches72 bytes/modes/blobs/exactchangedpaths. First helper run's globaldelta guard stop remains failed/inconclusive; evidence-backed scoped-TMPDIR successor preserves floor/assertions and passes. Complete conventionaldistcheck runs once; package018 and human-assisted mainhover remain pending. No new product tests, submission/contact/install/cleanup/commit/push. Goal/Phase2 remain incomplete; stop06:15:55Z.


2026-10-09 practical closeout: Cam grants full desktop until stop and requests ending reader setup churn. One current019 episode displays paused preview/AXPosition and exits ordinarily0; source72 preserved. Reader cursor stays on macOS WindowSharingSessionButton, so reader navigation is INCONCLUSIVE, not a demonstrated feature regression. Independent requirement audit removes Utility-navigation and particular input-route prerequisites as private process gates while retaining actual preview-visible accessibility coverage and current matched playback/audio/drop/resources as missing Strong-verification evidence. Preserve006/007 zero-arm failures; no measurement waiver, green Phase2, submission or source change. Concise reviewer handoff preparation records these limits.

2026-10-09 reader inheritance correction: independent source comparison, rechecked by root, binds human reader002 to source-round8 and finds70/72 current paths identical. Later control-hit geometry/outlet and helper named-double casts do not change slider accessibility, ordinary actions or nonactivating preview panel. Clock/GL/lifetime changes were already tested by the human reader episode. Inherit actual main Position/Pause/return spoken5.5%/Play proof; no further Utility or autonomous reader protocol required. Preview-visible, precise-seek and all-surface reader coverage remain unmeasured limits. Receipt work/story005-practical-reader001/root-reader-inheritance-review.json. Current matched playback remains open.

20261009 — Root closes Phases1/2 at the disclosed bounded scope: three matched playback pairs PASS, ordinary main reader evidence legitimately inherited after source comparison, final29-artifact/13-patch reviewer package checker PASS. Full local build/helper77/distcheck/native and preservation evidence stand. Platform/preview-visible reader coverage, interrupted public-recipe execution and owner-deferred shutdown cause remain explicitly disclosed in current-source10-final-verification.md. Whole story remains InProgress; Phase3 untouched. No submission/contact/install/commit/push.

20261009 — Owner reports fresh qualified test app looks good and invokes finish-and-push for this project repository. Exact final29-artifact/13-patch reviewer copy promoted byte-exact to patches/vlc-master/contribution-series-source10; local acceptance recorded and inbox/changelog updated. Reuse current source72/build/native/playback and fresh gradeB validation; whole Story005 remains open for Phase3, no VLC contact/submission.
