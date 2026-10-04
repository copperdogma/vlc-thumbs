---
name: create-eval
description: Scaffold a new eval, place it in the eval ladder, and link it to the relevant story, spec compromise, and methodology category
user-invocable: true
---

# /create-eval [eval-id or short description]

Local variant: read `docs/evals/README.md` first. Our registry, contracts,
attempts, and golden metadata use the paths declared there; upstream backend
or PromptFoo examples are illustrative, not installed runtime. Deferred contracts
have no executable runner or measured score. Do not create a fake runner or
record a missing engine as a failed model attempt.


> Alignment check: Before choosing an approach, verify it aligns with
> `docs/ideal.md`, `docs/methodology/state.yaml`,
> `docs/methodology/graph.json`, and relevant decision records in
> `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`,
> respect its limitation type and evolution path. If none apply, say so
> explicitly.

Create a **new eval scaffold**. This is the day-to-day companion to
`/setup-methodology` and the front door for adding new evals after the baseline
package already exists. If the repo is missing the baseline eval/golden package
entirely, run `/setup-methodology` first.

Use `/create-eval` to set up the eval. Use `/improve-eval` to iterate on an
existing eval, rerun it, or classify failures.

## Workspace Assumptions

Use the repo-equivalent paths if `init-project` or `/setup-methodology` adapted
this package to a different layout.

- Registry: `docs/evals/registry.yaml`
- Eval docs/protocol: `docs/evals/README.md`
- Attempt template: `docs/evals/attempt-template.md`
- Promptfoo runbook: `docs/runbooks/promptfoo.md`
- Eval implementations: `packages/backend/src/ai/evals/`
- Prompt files: `packages/backend/src/ai/prompts/`
- Golden fixtures: `tests/fixtures/golden/`

## Steps

1. **Read context first**:
   - `docs/ideal.md`
   - relevant `spec:N` sections plus `docs/methodology/state.yaml` / `docs/methodology/graph.json` for owning category and compromise state
   - any linked ADRs
   - `docs/evals/README.md`
   - `docs/runbooks/promptfoo.md` if the eval is prompt-based

2. **Place the eval in the ladder**:
   - `root-ideal` — the one-step perfect path from natural complete input/assets
     to the ideal output
   - `child` — isolates a measured failure mode from a parent/root eval
   - `compromise-detection` — proves a spec compromise can be deleted or
     simplified
   - `quality-runtime` / `quality-capability` — ordinary quality, latency, or
     cost evidence for an implemented surface
   - If it is a child eval, record the parent eval and the specific failure mode
     it isolates. Do not create orphan child evals with no parent failure.

3. **Classify the eval**:
   - Choose registry `type`: `quality` or `compromise`
   - Derive the eval class from that type + context:
     - `quality-runtime` — model/cost/latency trade-off
     - `quality-capability` — observable feature quality gate
     - `compromise-detection` — deletion gate for a spec compromise

4. **Choose the runner**:
   - `promptfoo` for prompt/model comparisons and rubric-scored outputs
   - `custom` TypeScript script for runtime/contract/system-level checks
   - Reuse existing layouts in `packages/backend/src/ai/evals/` before inventing a new one

5. **Scaffold the eval entry**:
   - Add a full registry entry in `docs/evals/registry.yaml`
   - Use the repo's actual registry schema. In Ultima IV Web that means `type:
     quality|compromise`; do not invent a separate `eval_class` field unless
     the target repo already stores one.
   - Include command, config/script path, target metric, and any methodology state/graph + spec linkage notes
   - Include ladder placement notes: root/parent/child, parent eval, and
     measured failure mode when applicable
   - If the eval is a compromise gate, make the linked compromise explicit

6. **Scaffold the implementation files**:
   - Create the eval config or script stub in `packages/backend/src/ai/evals/`
   - Point to prompt files, scorers, or golden fixtures in the existing layout
   - Reuse existing prompt or scoring helpers when possible

7. **Link the eval to the methodology graph**:
   - Story or story draft that owns the work
   - Relevant `spec:N` or compromise ID
   - Relevant methodology category / phase
   - Any fixture or golden IDs the eval depends on

8. **Verify the scaffold**:
   - Paths referenced in the registry exist
   - Runner choice matches the actual task
   - Ladder placement is explicit enough that `/triage` can decide whether to
     rerun a parent eval, create a child eval, or recommend implementation work
   - The eval can be handed off cleanly to `/improve-eval`

## Guardrails

- Do not run `/improve-eval` logic here; this skill scaffolds, it does not do
  the optimization loop.
- Do not create an eval with no story/spec/state anchor.
- Do not create a child eval without a parent/root eval and a measured failure
  mode, unless the output explicitly says the first task is to measure that
  parent failure.
- Do not invent a second eval layout when the current registry /
  `packages/backend/src/ai/evals/` / `tests/fixtures/golden/` structure already fits.
- Do not leave the registry entry partial; a new eval is not created until the
  registry has a real entry.
