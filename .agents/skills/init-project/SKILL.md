---
name: init-project
description: Seed a new AI-coded project by interviewing for the idea, authoring the Ideal and v0 spec first, then importing the appropriate methodology package and skills
user-invocable: true
---

# /init-project [new-idea|from-existing] [source-repo-path] [target-repo-path]

Use this as the **seed skill** for starting a new project from a blank folder or
lightly scaffolded repo. It is intentionally opinionated:

> **Get `docs/ideal.md` right first.**

Do not run `/setup-methodology greenfield`, create a story backlog, choose a
stack, or import a broad skill surface before the project has a real
`docs/ideal.md` and a v0 `docs/spec.md` derived from it. Without those, a repo
can only contain generic process furniture.

`setup-methodology` remains the canonical full-package installer. In a new
greenfield project, it is downstream of the Ideal/spec intake.

## Alignment References

Before acting, read the source repo's nearest equivalents of:

- `docs/methodology-ideal-spec-compromise.md`
- `docs/prompts/ideal-app.md`
- `docs/decisions/adr-021-execution-ideal-build-constraints/adr.md`, if present
- `.agents/skills/setup-methodology/SKILL.md`
- `.agents/skills/setup-methodology/templates/setup-checklist.md`
- `.agents/skills/setup-methodology/references/modes.md`

If one is missing, say so and continue from the rules in this skill. Do not
invent a different setup model.

## Modes

### `new-idea`

Use when the target folder is empty or only contains a bare repo and the user is
bringing an idea. This is the default mode.

### `from-existing`

Use when the target already has meaningful code, docs, prototypes, or imported
notes. Read what exists first, preserve provenance, then reconstruct the
implicit Ideal/spec through conversation.

## The Three Intake Roles

During idea intake, the AI has three simultaneous roles:

1. **Teacher / thinking partner** — Help the user understand what they are
   trying to create and what `docs/ideal.md` is for. Explain the Ideal briefly
   when needed: it is the no-limits north star, written as a concrete,
   implementation-free experience that can filter every future feature.
2. **Recorder** — Preserve everything useful: raw phrasing, half-formed ideas,
   examples, contradictions, rejected directions, preferences, non-goals, and
   hard constraints. Do not prematurely compress the user's thinking into a
   polished Ideal. Material that does not belong in the Ideal may still belong
   in the spec, preferences, stories, eval seeds, or open questions.
3. **Sorter / challenger** — Separate product ideal, execution ideal,
   vision-level preferences, spec compromises, and compromise-level
   preferences. If the user states a "requirement" that conflicts with the
   emerging Ideal, pause and dig in. The tension is signal: the Ideal may be
   missing something, the requirement may be a today's-world compromise, or the
   idea may need to be rejected or reframed.

## Continuous Triage Rule

Every new idea the user mentions at any point in this flow must be triaged
against the current `docs/ideal.md`, `docs/spec.md`, and raw intake. Do not
assume late ideas belong only in the spec or raw capture because the Ideal has
already been drafted.

For each new idea, decide whether it:

- changes or enriches the Product Ideal
- changes or enriches the Execution Ideal
- adds a vision-level preference
- adds or changes a durable requirement
- belongs as a spec compromise or compromise-level preference
- contradicts the current Ideal/spec and needs discussion
- is a story/eval seed, non-goal, or open question

If the idea affects the Ideal, update the Ideal. If it affects the spec, update
the spec. If it creates tension, pause and ask a targeted question. Keep
documents cohesive; do not append ideas in the order the user happened to say
them unless that order is conceptually right.

## Flow

### 1. Orient

- Confirm the target directory and whether it is empty, a bare repo, or an
  existing project.
- Confirm the source repo/path that contains the methodology package to reuse.
- Check `git status --short` if the target is already a git repo.
- Read before overwriting any existing project files.

If this seed skill is the only copied asset, use the source repo by path for
references until the full package is imported.

### 2. Preserve Raw Intake

Create or update:

```text
docs/idea-intake.md
```

For existing projects, put imported historical artifacts under
`docs/legacy_intake/` and keep `docs/idea-intake.md` as the live synthesis
trail.

Capture the user's original words, your questions, their answers, decisions,
open uncertainties, examples, non-goals, hard constraints, candidate Ideal
material, candidate spec compromises, preferences, and apparent contradictions.
Do not delete raw intake once distilled.

### 3. Interview for the Ideal

The interview should feel like a project-shaping conversation, not a form. Ask
one or a few focused questions at a time, then synthesize back what you heard.
Teach just enough methodology as you go so the user can participate well.

Use the "magic exists" frame:

- If there were no limitations, what would happen?
- What does the user provide, if anything?
- What do they get back?
- What disappears because magic handles it?
- What should the user never have to configure, manage, remember, or decide?
- What would make the product feel wrong, creepy, tedious, dishonest, or
  off-mission?
- What qualities should survive even if every implementation compromise is
  eliminated?
- What is the minimum floor below which the product solves nobody's problem?

For a library or module, push toward the ideal of non-existence: the consuming
system handles the work in one step and the user never thinks about the module.
For an application, push toward the simplest perfect interaction.

The Ideal also seeds the root eval. Ask: if the user gave the natural complete
input or asset set, what perfect output should the system produce in one step?
Preserve at least one golden seed for that full path when possible. If current
AI cannot do it, that failure is not a reason to skip the eval; it is the reason
to decompose into child evals and compromises.

Do not start from technology, screens, data models, or task lists. Those belong
in the spec or stories after the Ideal exists.

### 4. Sort Before Drafting

### Ideation Option Expansion

Use `/ideation` during idea intake or before drafting `docs/ideal.md` when the
possibility space is thin, all proposed product directions are same-shaped, or
Cam explicitly wants broader options. The ideation packet may run in a bounded
subagent when the user has explicitly authorized delegation, but `/init-project`
keeps the interview, raw intake, Ideal/spec synthesis, and final document
edits.

Before drafting `docs/ideal.md`, classify the intake. Keep the raw notes intact,
but make a working synthesis with these buckets:

- Product Ideal
- Execution Ideal
- Vision-Level Preferences
- Requirements
- Root Eval / Golden Seeds
- Spec Compromises
- Compromise-Level Preferences
- Open Questions / Tensions

When in doubt, do not silently decide. Reflect the tension back to the user and
ask a targeted question. A conflict is often the best path to the true Ideal.

### 5. Write and Review `docs/ideal.md`

Draft `docs/ideal.md` before `docs/spec.md`.

Required sections:

- Product Ideal
- Execution Ideal
- Vision-Level Preferences
- Requirements
- Minimum Viable Floor
- Quality Bar / root eval and golden seeds when useful

Quality rules:

- The Ideal is a vivid narrative, not a mission statement.
- It is concrete enough to answer design questions.
- It is implementation-free enough that no architecture, UI layout, provider,
  workflow, or data model is implied unless it reflects genuine user intent.
- Every sentence should help decide whether a future feature fits.
- Vision-level preferences are permanent qualities, not implementation tactics.
- Requirements describe capabilities that survive every implementation.
- Root eval seeds describe the perfect one-step input/output path, not the
  current decomposed implementation.

Review the draft with the user. Ask what feels wrong, missing, too small, too
technical, or too generic. Iterate until the user says it is directionally
right. During review, any new idea the user adds must go through the continuous
triage rule above before you decide whether it belongs in the Ideal, spec, raw
intake, or open questions. Do not call the Ideal final forever; call it good
enough to seed the first spec.

### 6. Write and Review `docs/spec.md`

Only after the Ideal is directionally accepted, draft a v0 spec.

The spec is the compromise map, not the Ideal repeated as requirements. For
each major area, record:

- product need
- build/technical need when applicable
- the Ideal this compromise serves
- the current compromise
- the limitation forcing it
- limitation type: AI capability, ecosystem, legal, physics, or human
- compromise-level preferences
- detection or evolution path
- what gets deleted, simplified, or transformed when the limitation changes
- parent eval or root Ideal eval the compromise exists under, when applicable

Use roughly 8-10 categories only when the project is complex enough. A small
tool can have fewer. Choose categories from the project, not from the source
repo.

The v0 spec may include open questions and "unknown until researched" markers,
but it must not fake certainty. If there is not enough information to write a
real compromise, ask another question or mark the area explicitly incomplete.

Review whether the spec correctly represents what today's reality forces. Do
not proceed to full package import if the spec has no real project shape.

### 7. Run Cohesion Validation Passes

Before asking to import the full methodology package, run at least two document
quality passes over `docs/idea-intake.md`, `docs/ideal.md`, and `docs/spec.md`.
These are synthesis passes, not proofreading passes.

Pass 1: **Coverage and placement**

- Re-read the raw intake and verify every meaningful idea is represented in the
  right place: Ideal, spec, preference, story/eval seed, non-goal, or open
  question.
- Check late-arriving ideas especially carefully; they often reveal missing
  Ideal material.
- Confirm spec compromises point back to the Ideal they serve.
- Confirm AI-capability compromises point back to the root eval or parent eval
  whose measured failure forces the decomposition.

Pass 2: **Cohesion and contradiction**

- Find contradictions inside the Ideal, inside the spec, and between the two.
- Look for requirements or preferences that fight the magic-world Ideal.
- Merge duplicate ideas and replace chronological lists with integrated
  sections that read like a designed system.
- Suggest improvements to make the Ideal more concrete, more no-limits, or less
  solution-shaped.
- Suggest improvements to make the spec more honest about limitations,
  preferences, and detection/evolution paths.
- Suggest improvements when the eval ladder is missing: root eval, parent eval,
  measured failure mode, child eval, or implementation story.

Bring unresolved tensions back to the user before proceeding. The outcome should
be cohesive documents that synthesize what the user meant, not archives that
repeat what the user said in order.

### 8. Ask Before Full Methodology Import

After `docs/ideal.md` and `docs/spec.md` exist and have been reviewed, ask:

> Should I now import the full methodology package and appropriate skills from
> `{source_repo}` into this project?

If the user says yes, import and adapt the package. Prefer package groups over
blind file copying:

- agent instructions and cross-CLI skill wiring
- setup-methodology runbook, checklist, and compiler/check scripts
- state/graph surfaces aligned to the new spec categories
- story, ADR, eval, and golden-reference scaffolding
- recurring triage/alignment/eval/story skills that fit the new project

Only import optional lanes when the new Ideal/spec justify them. For example,
UI-scout belongs only in projects with a real UI product-truth surface; model
discovery belongs only when provider choice matters.

After import, run `/setup-methodology greenfield` or its local equivalent to
normalize the package against the already-authored Ideal/spec. Setup may refine
and align; it must not replace the intake-backed Ideal with a generic template.

### 9. Verify

Use repo-native checks after import. For RoboRally-style packages, start with:

```bash
./scripts/sync-agent-skills.sh
./scripts/sync-agent-skills.sh --check
git diff --check
```

If the imported package includes methodology compiler/check scripts, run those.
If it includes app code, typechecks, tests, or formatting, run the checks that
match the files generated or changed.

## Artifact Expectations

Before full package import:

```text
docs/
  idea-intake.md
  ideal.md
  spec.md
```

After full package import, the exact tree depends on the project. A typical
methodology repo includes:

```text
AGENTS.md
docs/
  idea-intake.md
  ideal.md
  spec.md
  methodology/
    state.yaml
    graph.json
  setup-checklist.md
  stories.md
  inbox.md
  decisions/
  evals/
  runbooks/
tests/fixtures/golden/      # or repo-equivalent golden workspace
.agents/skills/
scripts/sync-agent-skills.sh
```

## Failure Modes

- **No project idea yet:** Stop after creating an intake placeholder. Ask the
  user to explain the idea. Do not install the full package as if setup were
  complete.
- **Ideal draft is generic:** Keep interviewing. A generic Ideal creates a
  generic product.
- **Ideal draft is solution-shaped:** Move implementation detail into the spec
  or later stories.
- **Spec is just a feature list:** Rewrite it as compromises forced by named
  limitations.
- **Skill selection happens too early:** Install only this seed skill until the
  Ideal/spec reveal which package surfaces are appropriate.
- **Source repo assumptions leak:** Replace source-domain names, paths, tech
  assumptions, eval categories, and runbooks with target-project equivalents.

## Notes

- `init-project` is allowed to be copied alone into an empty folder.
- The execution ideal from ADR-021 matters here: even perfect AI builds through
  conversation and iteration because the user discovers what they want by
  reacting to drafts. Treat the interview and revision loop as part of the
  ideal process, not overhead.
