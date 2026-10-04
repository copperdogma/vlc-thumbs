---
name: triage-health
description: Return read-only Board Game Ingester health and freshness candidates for triage orchestration
user-invocable: true
---

# /triage-health [scan]

Use this as a read-only lane for Board Game Ingester triage health and
freshness. It feeds full-sweep `/triage`; it does not make the final
cross-domain decision.

## Contract

`/triage-health` is always read-only. It may recommend follow-up commands such
as `/codebase-improvement-scout`, `/triage-evals`, `/triage-architecture`,
`/discover-models`, coverage-matrix upkeep, or methodology wrapper sync, but it
must not run heavy provider calls, broad codebase scouts, architecture audits,
dependency changes, or implementation work during ordinary triage.

The health lane is advisory. Do not label any health candidate as the final
triage winner, and do not let hygiene freshness automatically outrank larger
Ideal/spec/coverage asset-pipeline or eval gaps. Return evidence and stop
conditions so main `/triage` can compare it with the other lane packets.
For each candidate or stop condition, include candidate name, lane type,
Ideal/spec value, evidence, why now, action shape, validation/stop condition,
blockers, and reasons not now.

Direct standalone invocation may identify the strongest health-lane follow-up,
but still label it as a health-lane recommendation rather than a repo-wide
triage winner. Full-sweep lane-packet mode stays neutral and returns candidates
or stop conditions for main `/triage` to rank.

Architecture, UI, and harness debt may be surfaced as health evidence when it
creates concrete Ideal/spec risk to traceability, no-downsampling proof,
eval/golden confidence, coverage truth, or Builder-ready handoff. Keep that
evidence advisory for main `/triage` to prioritize.

## Evidence To Read

1. Read the shared frame:
   - `docs/ideal.md`
   - `docs/spec.md`
   - `docs/methodology/state.yaml`
   - `docs/methodology/graph.json`
   - `tests/fixtures/formats/_coverage-matrix.json`
2. Run:

   ```bash
   python3 scripts/triage_facts.py --json
   ```

   Use its eval freshness facts as the default stale-score read. They derive
   the latest measurement from explicit `latestScore`/`latest_score` when
   present, otherwise from the most recent dated `scores` entry; empty `scores`
   means no measured score.

3. Inspect existing health surfaces only:
   - latest `docs/reports/codebase-improvement/*.md`
   - `docs/evals/registry.yaml`
   - benchmark results under `benchmarks/results/`
   - `docs/methodology/state.yaml` architecture-audit domains
   - `.agents/skills`, compatibility links, optional command aliases, and `scripts/sync-agent-skills.sh --check`
   - dependency/provider notes when relevant

## Candidate Areas

Return up to three health candidates:

- **Coverage freshness** — coverage rows still `has-fixture`/`untested`,
  missing score sources, or coverage claims that no longer match graph/eval evidence.
- **Codebase improvement freshness** — broad hygiene scan age, source churn
  since the last scan, unresolved scan recommendations, or absence of a broad report.
- **Eval/model/golden freshness** — stale scores, ready retry triggers, missing
  root/parent/child eval proof, or golden fixture debt. Respect registry score
  history rather than treating every eval without `latestScore` as stale.
- **Methodology/tooling health** — skill-surface link or optional-alias drift, generated graph or stories
  index drift, missing active facts, setup checklist drift, skill-sync
  problems, or harness/tooling residue that blocks eval/golden truth.
- **Architecture-audit health** — due domains from `architecture_audits`, open
  findings, repeated drift, stale recent-story references, or architecture/UI
  debt with concrete Ideal/spec risk.
- **Dependency/provider health** — existing evidence of package/provider drift
  that could make the next asset/eval story misleading.

Use the candidate-area name as the lane type unless a more specific type is
clear from the evidence.

## Output

```markdown
## Triage Health

### Health Candidates
1. {candidate name}
   - Ideal/spec value: {north-star or spec value}
   - Lane type: {coverage freshness | codebase improvement freshness | eval/model/golden freshness | methodology/tooling health | architecture-audit health | architecture/UI/harness debt | dependency/provider health | stop condition}
   - Evidence: {files/facts}
   - Why now: {trigger}
   - Suggested action shape: {follow-up command or no-op}
   - Validation/stop condition: {what would make it done}
   - Blockers: {if any}
   - Reasons not now: {if any}

### Lane Packet
- {neutral health candidate name + Ideal/spec/coverage value + lane type + evidence + why now + action shape + validation/stop condition + blockers + reasons not now}
```

## Guardrails

- Stay read-only.
- Do not run `/codebase-improvement-scout`, `/discover-models`,
  `/triage-architecture`, provider-backed evals, golden builds, dependency
  upgrades, or implementation work during health triage.
- Do not let health work automatically outrank a larger Ideal/spec/coverage
  asset-pipeline or eval gap; return evidence so `/triage` can rank it.
