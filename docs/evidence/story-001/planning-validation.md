# Feasibility and two-story planning validation

2026-10-04. Scope: Story 001 research/build/probes and requested implementation
planning. Feature implementation is absent and is not scored as completed.
Main applies `/validate` and `/mark-story-done`; no commit/push is part of this
turn. Existing build evidence is reused because no feature/build-source change
has occurred since attempt 009; only its recorded contrib isolation patch is
present in the mutable source diff. Pristine upstream remains clean.

## Findings first

Bounded independent review found two material planning ambiguities, both fixed:

1. Thumbnail cache freshness was underspecified. The synthesis/spec/story now
   require an explicit decoder-ADR contract and replacement tests. Conservative
   proposal: media-open namespace with file-state guards; cross-open reuse needs
   fresh content verification, otherwise decode as a miss. Continuous external
   mutation limits are explicit; durable annotation identity remains separate.
2. Latency trials mixed settled demand with intentional cancellation. The root
   contract now separates settled non-superseded latency trials from burst
   cancellation/backlog/stale-result tests, with errors/timeouts explicitly
   failing a condition rather than disappearing from success percentiles.

No remaining material planning defect found in the inspected scope. Residual
limits: neither feature exists; floating fullscreen panel pointer interaction,
large-file hashing, production IPC/cache/schema, real-resolution performance,
broader formats and public packaging are unqualified. These are feature-story
requirements, not hidden feasibility passes. Recommendations remain proposals;
only ADR-001 storage lifetimes are accepted.

Independent reviewer used a bounded cheaper-model document pass; stronger
persistence research informed identity/write semantics. Main verified findings
and owns recommendations. No repeated review loop or speculative work added.

## Story 001 requirement ledger

| Original requirement | Result and applicable evidence |
|---|---|
| Primary extension/module/source licensing investigation | Met: pinned source inventory, Lua/native/UI route table, COPYING/module notices and explicit distribution limits |
| Pin release/source and host/build | Met: source-manifest/preflight, attempt-009 command/verification, source checksums and build runbook; host-only qualification |
| Map normal/fullscreen geometry/events/drawing/decoder boundaries | Met: pinned paths/symbols and four-surface table in synthesis; source map plus runtime observations/capture limitation |
| Compare existing/Lua/module/UI patch against both features | Met: initial research route matrix and synthesis; small native GUI patch recommended without claiming impossible alternatives |
| Reproducible isolated build/launch or precise failure | Met: nine recorded attempts culminate in arm64 development app, runbook, namespace and signing; clean rebuild not repeated |
| Legal fixture, capture plan and measurable proposed targets | Met: generated known-frame MP4/MKV recipes/hashes, planned fuller matrix, explicit frame/seek/latency/playback/resource targets and capture limits |
| Recommendation, maintenance/open questions and next integrated slice | Met: synthesis plus Stories 002/003, patch maintenance scope, decoder and identity/store ADR gates, shared UI/root integration |

All eight feasibility tasks and five tenets are satisfied within their research
scope. Native panel/keyboard/feature behavior is required in 002/003; Story 001
does not claim shipping it. Build/plan authorization is recorded in intake and
the original work log. ADR-001 remains accepted; its schema/identity/cache/runtime
items remain open. No weakening of the original feature shipping exclusions.

Planning request: two complete feature stories, compact 1–3-word label design,
alternatives, verified seams, tasks/files, measurable ACs, errors, scope and
workflow gates are present. Both initial Pending states rely on actual native
source/build/decoder/platform-library substrate, not on a completed enhancement.
Recommended order is 002 then 003; store behavior does not depend on decoding.
No prototype or matrix is misrepresented as a product golden/eval pass.

## Validation performed

- Inspected `git status --short`, `git diff --stat`, affected `git diff` and
  `git ls-files --others --exclude-standard`; untracked ADR/build/probe/planning
  artifacts included. Historical build logs/results retained, not rewritten.
- `make methodology-compile` and `make validate`: graph, 33 canonical skill
  source hashes/wiring and local scaffold checks pass. `git diff --check` passes.
- Local Markdown targets resolve; Story 001 evidence JSON files parse; new
  stories have distinct IDs and no imported template placeholders.
- `git diff --exit-code -- docs/ideal.md` passes: North Star unchanged.
- Strict deep app signature verification passes; pristine source status clean.
  Existing attempt-009 arm64/dependency audit reused; full rebuild unnecessary
  for this documentation/probe planning delta.
- Rechecked libav result set: 3 fixtures × 5 requests succeed; paired MP4/MKV
  RGB hashes equal. Source media SHA-256 values still match original manifests.
  AVFoundation failure and timing limitations retained. SQLite output confirms
  platform link/basic transaction/revision checks only.
- Native detached/fullscreen captures inspected. Ordinary baseline seek proof
  reused from attempt 009; fullscreen floating panel interaction remains unproven.
- No product root run, no model/provider calls, no installed VLC/user-store
  edits, no source-project mutations. Diagnostic binaries/media remain ignored.

`codex review` was not used: current feature-planning delta is documentation
and bounded research evidence, with no production behavior patch. Probe programs
were compiled/executed for the narrow claims they support, not adopted as
production code. Learning-review considered: these are local planning/proof
clarifications; no separate durable workflow-learning candidate or skill edit.

## Disposition

**Grade B: feasibility and planning requirements met, residual technical limits
explicit. Close now — Story 001 only.** Seven of seven original ACs met; eight
tasks and five tenets complete. Remaining closeout bookkeeping is status/gates,
generated records and changelog. No remaining Story 001 implementation gap.
Stories 002/003 remain unstarted, root deferred. Next product work is Story 002's
technical/plan gate. Landing request, if desired, is `/finish-and-push`; it is
not invoked by this planning task.
