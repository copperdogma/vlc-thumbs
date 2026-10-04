---
id: "001"
status: Draft
priority: High
ideal_refs:
  - ideal:req:previews
  - ideal:req:annotations
  - ideal:req:persistence
  - ideal:req:playback-quality
  - ideal:req:evidence
spec_refs:
  - spec:1
  - spec:2
  - spec:3
  - spec:4
adr_refs: []
depends_on: []
eval_refs:
  - root-timeline-experience
---
# Story 001 — VLC macOS timeline feasibility

## Goal

Find the smallest maintainable path to both requested interactions on VLC's
actual macOS timeline. Establish pinned source/build/UI evidence before choosing
an integration architecture. This is a feasibility proposal, not permission to
modify the installed VLC or a claim that a native fork is necessary.

## Acceptance Criteria

- [ ] Verify current primary VLC extension/module documentation and source licensing; distinguish observations from intake suggestions.
- [ ] Pin source revision/version and macOS/architecture/toolchain. Explain choice versus the intake's unverified 3.0.24 suggestion.
- [ ] Map normal and fullscreen seek controls, time/position geometry, hover/right-click events, marker drawing and playback/decoder boundaries to source paths/symbols.
- [ ] Compare existing upstream capability, Lua extension, native module and UI patch against BOTH interactions, including separate-window mismatch.
- [ ] Establish a reproducible isolated build/launch path or record the exact failed command, blocker and next route. Do not replace installed VLC.
- [ ] Define legal known-video fixture acquisition/generation, root test capture method and proposed measurable preview/seek/latency/playback thresholds.
- [ ] Record a route recommendation, expected maintenance cost, unresolved API/storage questions and next integrated vertical slice. Update spec/state and compile graph.

## Out of Scope

Shipping either feature, distributing VLC, creating a remote, signing/notarizing,
modifying real media/notes, changing installed VLC, choosing annotation schema
without identity analysis, Windows/Linux support, colors/tags, paid AI calls.

## Approach Evaluation

Existing upstream behavior is the first baseline. A Lua extension is attractive
if it can manipulate the required native surface; a native module or UI patch
may provide control at greater build/maintenance cost. A companion window changes
the requested experience and needs a deliberate product decision. No route is
qualified yet. Use current primary docs plus source inspection, then a minimal
isolated experiment where inspection cannot resolve the hook.

AI can assist research and implementation; a single model response cannot itself
provide native event handling or durable player state. The product is a
behavioral native UI feature, not a prompt-comparison task. No model capability
failure is asserted to justify code.

## Eval Ladder Context

Parent outcome: `root-timeline-experience`, deferred and never attempted.
This story establishes substrate and an honest test path; it does not pass the
root. No child deletion eval or measured parent failure exists. A fixture/build
probe here may become a capability check once its command and expected outcome
are real. Do not mark compile success as end-to-end proof.

## System Context / Integration Impact

Today this repository has workflow docs/scripts only. VLC supplies media identity,
input state, seek controls and playback outside this checkout; none has been
inspected here. Preview extraction must not seek the playing input. Annotation
identity must survive cache churn and app restart. UI markers share timeline
geometry with normal dragging and control reveal/hide. Source inspection must
identify which normal/fullscreen surfaces share or duplicate this behavior.

## Decision Inventory / Open Questions

- Version/build target: stable VLC release versus development source. Recommend
  a supported macOS baseline after verifying build feasibility; no release pinned.
- Integration: existing feature/extension/module/UI patch. Recommend the least
  invasive route that meets the actual timeline contract, based on evidence.
- Preview extraction: VLC decode path versus an external helper. Compare
  isolation, licensing, deployment and performance before selecting.
- Identity/storage: same-file scope first; keep replacement detection and durable
  notes separate from disposable thumbnails. Move/rename portability undecided.
- Delivery: isolated local build first; packaging/upstream plans follow proof.

## Tasks

- [ ] Read official docs and pin relevant source under ignored work/input with provenance.
- [ ] Inventory macOS seek UI classes/events and native extension/module boundaries.
- [ ] Record route matrix with exact supporting source pointers and unknowns.
- [ ] Verify local build prerequisites and establish isolated build/launch instructions.
- [ ] Plan fixture and root scenario with measurable thresholds and UI evidence.
- [ ] Write feasibility synthesis in docs/research, measured build attempts in docs/evidence, and any resulting ADR proposal.
- [ ] Refine the implementation plan/story boundary with the evidence; update spec/state and graph.
- [ ] Run make validate and scope-appropriate build checks; no product pass from setup checks.

## Architectural Fit

Owning area: future VLC macOS UI integration and timeline services. State spec:1
through spec:4 are missing/climb. No local source, schema or runtime proves
build-readiness. No applicable local ADR found in docs/decisions. Source-project
ADRs, fixtures and game rules do not constrain this project.

## Files to Modify

- docs/research/scout.md — index primary research and feasibility findings.
- docs/research/ — source/UI/route synthesis with citations and applicability.
- docs/evidence/ — exact isolated build/probe attempts and results.
- docs/spec.md and docs/methodology/state.yaml — qualify constraints and substrate.
- docs/evals/root-timeline-experience.md — measurable thresholds/capture plan.
- scripts/ — only verified build/probe helpers required by the selected route.

## Redundancy / Removal Targets

No product implementation exists to remove. Replace unverified candidate text
with qualified facts while preserving original intake and failed experiments.

## Project Tenets / UI Verification

- [ ] Preserve input media and real user state.
- [ ] Pin provenance; keep hypotheses separate from observed facts.
- [ ] Inspect actual native UI evidence and normal/fullscreen coverage.
- [ ] Preserve playback, seeking, keyboard and accessibility behavior.
- [ ] Keep changes scoped and conclusions proportional to measured evidence.

## Workflow Gates

- [ ] Substrate inspected and written plan exists.
- [ ] Applicable plan approval/authorization recorded before implementation.
- [ ] Feasibility work complete with honest build/UI evidence.
- [ ] Validation complete or explicitly skipped by user.
- [ ] Story marked done via /mark-story-done.

## Plan

Not yet built. Start with primary source/UI investigation; refine a concrete
experiment plan once source/build boundaries are known. Setup authorization
covers project scaffolding; no product implementation plan is claimed approved.

## Work Log

20261003 — Setup: preserved the overview and drafted this feasibility boundary.
Source/build/UI substrate is unverified; status Draft. No product work executed.
