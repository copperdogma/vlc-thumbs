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
Use `docs/runbooks/skills.md` for domain overrides and routing. Shared core
contracts remain byte-identical. Optional imported skills do not require provider
setup or model evaluation. Compatibility links expose canonical skills.

Run `make methodology-compile`, `make skills-sync`, `make validate`, and direct
facts JSON. Review whitespace and generated graph currency. Product validation
must later supply pinned VLC/build/media and actual macOS interaction evidence.
No heavy evals or agent loops are needed to prove absent code.

No ports are allocated or reserved for this project. Native app work needs no
web launcher. If a web/API runtime appears, obtain Conductor allocation before
binding. Dependency/Codex setup hook is deferred until a real build needs it;
source/lockfiles/user data must not be rewritten by a hydration hook.
