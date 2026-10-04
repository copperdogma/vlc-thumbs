---
name: triage-architecture
description: Audit a bounded architecture domain for cleanup pressure and record the next structural move
user-invocable: true
---

# /triage-architecture [domain-id]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md`, `docs/methodology/state.yaml`, and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Canonical architecture-audit leaf skill. Direct invocation is allowed, and
`/triage architecture` routes here.

## Lane Packet Mode

When full-sweep `/triage` asks for a lane packet, return up to three neutral
architecture candidates or stop conditions. Do not choose the repo-wide winner,
and do not let direct-mode "pick one domain" behavior leak into a single final
lane decision. For each candidate include candidate name, lane type, Ideal/spec
value, coverage value when relevant, domain evidence, eval/golden evidence when
relevant, why now, suggested action shape, whether it is story-worthy or
audit/no-op, validation/stop condition, blockers, and reasons not now.

Direct invocation may still pick one architecture domain and return one
recommended architecture action. In lane-packet mode, keep any due-ness scoring
as private evidence or label it as non-final lane evidence. Do not populate
`### Recommended Action` with an architecture winner; use that field only to
hand the packet back to main `/triage` or to say there is no architecture-lane
action. Put actionable options under `### Lane Packet` as neutral candidates or
stop conditions.

## What This Skill Produces

A short advisory report:

- domain health
- structural cleanup signal
- direct mode: one recommended next architecture action
- full-sweep lane-packet mode: neutral architecture candidates or stop
  conditions

This skill is read-only unless the user explicitly asks to update the audit
state.

## Read First

1. `docs/ideal.md`
2. `docs/spec.md`
3. `tests/fixtures/formats/_coverage-matrix.json`
4. `docs/evals/registry.yaml` when the domain affects eval/golden truth
5. `docs/methodology/state.yaml`
6. `docs/methodology/graph.json`
7. `docs/runbooks/triage.md`, plus `docs/runbooks/triage-architecture.md`
   if that architecture-specific runbook exists
8. relevant ADRs and recent story files for the direct-mode domain or
   lane-packet candidates

## Steps

1. Resolve the domain
   - in lane-packet mode, inspect `architecture_audits` broadly enough to
     return up to three neutral domain candidates or stop conditions; do not
     pick a single most-due domain
   - in direct mode, if no domain is supplied, inspect `architecture_audits` in
     `docs/methodology/state.yaml` and pick the most due domain
   - in direct mode, if a domain is supplied, verify it exists in state

2. Read the domain state for the direct-mode domain or lane-packet candidates
   - last audit date
   - recent story refs
   - open findings
   - manual priority
   - notes

3. Inspect recent evidence
   - story files in `recent_story_refs`
   - recent validation or work-log drift signals
   - relevant ADR/spec slices
   - coverage rows, eval/golden evidence, or artifact manifests when the domain
     can affect traceability, source fidelity, no-downsample guarantees, or
     Builder-ready handoff

4. Judge whether an audit is due
   - high manual priority
   - open findings
   - overdue cadence
   - obvious repeated drift
   - concrete Ideal/spec risk to coverage truth, eval/golden confidence,
     traceability, source fidelity, no-downsample guarantees, or Builder-ready
     handoff

5. Decide one output
   - in direct mode: no action, fold into existing story, create follow-up
     story, or escalate to ADR/discussion
   - in lane-packet mode: neutral candidates or stop conditions for main
     `/triage` to compare across lanes

## Report Format

```markdown
## Triage Architecture

### Domain
- `{domain-id}` — {short summary}

### Due Signals
- {signal or "None"}

### Findings
- {bounded structural issue or "No actionable drift found"}

### Recommended Action
- {direct mode: one next architecture action; lane-packet mode: return packet to main `/triage` or no architecture-lane action}

### Lane Packet
- {neutral architecture candidate + lane type + Ideal/spec/coverage value + evidence + why now + action shape + story-worthiness/audit scope + validation/stop condition + blockers + reasons not now}
```

## Guardrails

- Read-only by default
- Keep direct-mode audits bounded to one domain unless the evidence clearly
  spans two
- In lane-packet mode, summarize candidate domain evidence without running a
  full architecture audit for each domain
- Prefer delete / merge / re-home over new abstraction
- If no action is the honest answer, say so explicitly
