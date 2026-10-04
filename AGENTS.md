# VLC timeline enhancements — Agent Instructions

Read this file at the start of each session. This is an independent project;
the neighboring Ultima IV and Board Game Ingester repositories are read-only
workflow sources, not VLC product references.

## Mission and truth

Enhance VLC's actual macOS timeline with hover thumbnails and persistent
annotated bookmarks. Read `docs/idea-intake.md`, `docs/ideal.md`, `docs/spec.md`,
`docs/methodology/state.yaml`, generated `docs/methodology/graph.json`, and
`docs/plan.md` for planning. Before implementation, read the active story and
its Ideal/spec/state slice. Raw intake is preserved; prior assistant claims are
unverified until supported by current primary documentation or pinned source.

## Working rules

- User instructions and existing authorization outrank imported skill guidance.
  Cam requested skill import and project setup; no additional import permission
  is required. Ideal/spec are v0 drafts, not a claimed user-approved final vision.
- Delegate bounded inventories/checks/research to cheaper models when useful;
  use stronger models for integration, persistence and behavioral judgments.
  Main agent owns conclusions. No compulsory repeated agent loop for sparse setup.
- Verify current VideoLAN documentation and pin source revision/build before
  interface changes. Inspect macOS normal/fullscreen controls; do not infer their
  API from Qt/Linux examples or assume Lua can alter the native scrub bar.
- VLC is an upstream open-source project to extend. Reusing its licensed source
  is appropriate here; Ultima's independent-engine-recovery restriction is unrelated.
- Preserve videos. Work on copies in ignored `work/`; do not change installed
  VLC, real annotation stores or source projects during experiments.
- Keep caching, media identity, annotations and UI boundaries inspectable.
  No extraction engine, storage schema, or maintained fork is selected yet.
- Record source/build provenance, hypotheses, actual measurements, failures and
  tested scope. Compile or screenshot success alone is not functional proof.
- Include actual macOS UI interaction validation for user-facing stories and
  restart/media-identity proof for persistence changes. Preserve playback and
  accessible controls. Browser verification applies only if a browser UI exists.
- Keep imported core skills exact where shared. Use local runbooks below for
  domain terms, commands, fixtures and priorities. Do not execute source-repo
  commands, paid calls or model discovery solely because a skill mentions them.
- Do not commit, push, publish, create remote repositories, change other projects,
  or schedule automation without the user's request. Verify licenses before
  distributing source, dependencies or media. Keep private media and secrets ignored.

## Methodology and skills

`.agents/skills/` is canonical; `skills`, `.claude/skills` and `.cursor/skills`
are compatibility symlinks. See `docs/runbooks/skills.md` for selection and
local applicability. All 33 requested skills are installed; optional lanes stay
dormant until there is relevant substrate. Source hashes live in
`docs/evidence/workflow-skill-sources.json`.

- `/init-project` preserves intake and authors Ideal/spec; `/setup-methodology`
  is the only full-package setup/refresh entrypoint.
- `/triage` starts from Ideal/spec/state/graph, gathers neutral facts/packets,
  compares candidates and recommends one next action. Absent runtime evidence
  is an explicit deferral, not a broken-proof emergency.
- `/create-story`, `/build-story`, `/validate`, `/mark-story-done` own story flow.
  Keep optional sidecars bounded and implementation delegation behind the
  applicable plan gate; existing user approval remains valid.
- `/create-eval`, `/improve-eval`, golden helpers own behavioral contracts and
  measured attempts. `/align`, ADR helpers and `/ideation` support decisions.
- `/loop-verify` is budgeted by default; strict repeated proof needs a material
  reason. `/finish-and-push` does not expand authorization.
- `/scout` records current primary findings under `docs/research/`; deferred
  ideas go in `docs/inbox.md`.

## Current stage and commands

Local setup only. No VLC source/build, product code, video golden, product runner,
benchmark, or accepted architecture exists. Story 001 is Draft feasibility.
Root eval is deferred. Native app work has no web port; no Conductor range is
allocated. Defer web launcher/dependency setup hooks until real tooling needs them.

`docs/methodology/state.yaml`, story files and eval registry are writable truth.
Graph and `docs/stories.md` are generated; never edit them manually.

```
make methodology-compile
make validate
node scripts/triage-facts.mjs --json
```

`make validate` checks graph currency, skill wiring/source hashes and local
workflow references. It is not VLC functionality, performance or licensing proof.

## Research and strategy checkpoints

When a nontrivial obstacle makes the next step uncertain, inspect enough
local evidence to name the general problem class, then check established
approaches before inventing a workaround. Reuse applicable prior research;
otherwise consult a few primary sources, retaining the constraints that
affect applicability. Stop once you can choose an approach and a small local
test. Prefer the simplest permitted technique that fits; explain material
departures. If attempts keep failing, revisit the diagnosis and assumptions
before adding retries or special cases. Record reusable sources, the
decision, local evidence, and uncertainty in existing project notes. Obvious
fixes need no research ceremony. Preserve project reuse boundaries and
acceptance criteria.

In long-running work, use `/loop-review` to periodically challenge the
approach against the intended outcome and established alternatives, even
when local metrics improve. Preserve a requested cadence; otherwise use
roughly 30 minutes of active work or three substantive rounds, whichever
comes first, as a tunable default within the authorized run. `/loop-verify`
keeps its round checks and earlier stop rules. Reuse applicable source
comparisons, carry cadence across interruptions, and charge research to the
existing budget. This does not create a schedule or extend work past a stop.
