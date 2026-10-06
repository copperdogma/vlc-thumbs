# Setup / refresh

Greenfield intake authored VLC-specific Ideal/spec before importing the skill
package. Cam's setup request already authorized that import. The v0 product
interpretation remains open to refinement; no new permission gate is inferred.
Missing source examples (`docs/prompts/ideal-app.md`, source ADR-021) were not
fabricated. The Board Game Ingester bundled modes/checklist were available.

Canonical setup skill: `.agents/skills/setup-methodology/SKILL.md`.
Use its sparse no-code path. Work from `docs/setup-checklist.md`, preserve raw
intake, and align Ideal/spec/state/graph, story and root eval. Include absent
runtime, audit, UI, codebase and golden lanes with reasons/triggers.

Copy exact source skills with support files; record selected paths and hashes.
Use `docs/runbooks/skills.md` for domain overrides and routing. Unchanged shared core
contracts remain byte-identical; deliberate local adaptations retain original
provenance and record their adopted source and current hashes. Optional imported skills do not require provider
setup or model evaluation. Compatibility links expose canonical skills.

Run `make methodology-compile`, `make skills-sync`, `make validate`, and direct
facts JSON. Review whitespace and generated graph currency. Product validation
must later supply pinned VLC/build/media and actual macOS interaction evidence.
No heavy evals or agent loops are needed to prove absent code.

No ports are allocated or reserved for this project. Native app work needs no
web launcher. If a web/API runtime appears, obtain Conductor allocation before
binding. Dependency/Codex setup hook is deferred until a real build needs it;
source/lockfiles/user data must not be rewritten by a hydration hook.

## Research rule refresh — 2026-10-04

Preserve the portable research rule in `AGENTS.md`, including lean kickoff.
Keep planning and mid-implementation research hooks in `/build-story` and the
unexplained-failure hook in `/validate`. Refresh `/loop-verify` coordinator
checkpoints and `/loop-review` strategy comparison without adding a schedule,
expanding budgets, weakening proof or changing owner reuse boundaries.
The local `/loop-verify` strict reset contract remains authoritative: material
fixes reset the original scope within existing convergence and budget limits.
Do not import another verifier phase model implicitly from setup examples.
See `docs/research-before-reinvention.md` for adopted source and check scope.

## Agent staffing and event waits — 2026-10-06

Preserve the short common policy in `AGENTS.md` and focused leaf decisions in
installed skills. Strategic `/loop-review` resolves the strongest eligible model
and highest supported effort at runtime, records requested versus verified served
identity, and dispatches one bounded read-only reviewer when needed. Respect fork
schemas, scope, privacy, budgets, deadlines, clean stops and chat authorization.
Routine workers use the cheapest capable configuration only when overhead is
justified, with bounded packets, artifact access and native completion or
message-aware waits. Preserve tiny-lane coverage, existing delegation authority,
plan gates, one Git owner and proportional checks. Never alter frozen evaluation
subjects, prompts or judges through staffing policy; enforce aggregate paid-work
caps before concurrent dispatch. Retain sparse/no-code exceptions and local
verification/reset contracts; do not install absent evaluation leaves just for
this policy. See `docs/agent-staffing-and-event-waits.md` for the adoption receipt.
