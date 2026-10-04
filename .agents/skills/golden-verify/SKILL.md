---
name: golden-verify
description: Orchestrate golden fixture verification — launch parallel subagents, record results, loop until everything is CLEAN.
user-invocable: true
---

# /golden-verify [fixture-id]

Local variant: read `docs/evals/README.md` first. Our registry, contracts,
attempts, and golden metadata use the paths declared there; upstream backend
or PromptFoo examples are illustrative, not installed runtime. Deferred contracts
have no executable runner or measured score. Do not create a fake runner or
record a missing engine as a failed model attempt.


> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Orchestrate verification of all golden reference test fixtures. This is a pure
orchestrator — it never reads fixture content. It reads the checklist, launches
subagents to do the work, records their verdicts, and loops.

Because the orchestrator stays lean (no fixture content in context), it can run
for hours processing dozens of fixtures.

**Usage:**
```
/golden-verify                  # run until everything is CLEAN
/golden-verify LC-042           # verify one specific fixture
```

**With ralph-wiggum:**
```
/ralph-loop /golden-verify --completion-promise 'All golden fixtures are verified CLEAN'
```

## The Loop

Repeat until there's no work left:

### 1. Check inbox

Scan `tests/fixtures/golden/_inbox/` for new input directories. For each one,
launch a high-capability subagent to run `/golden-create`.

### 2. Find work

Read `tests/fixtures/golden/_verification-checklist.md`. Also scan for T2 fixtures
that could be promoted (have input but no `expected-entities.json`).

Work items:
- **Promotable T2s** — need `/golden-create`
- **PENDING** — need first verification pass
- **PASS N** (had issues last time) — need another clean pass

If nothing needs work, report done and stop.
Ralph-wiggum signal: `<promise>All golden fixtures are verified CLEAN</promise>`

### 3. Launch subagents

Use your judgment on parallelism — usually one fixture per subagent. Default to a high-capability worker for semantic golden verification; use cheaper or lower-reasoning workers only for mechanical inbox scans, compatibility-link or optional-alias checks, or validator-only follow-up where fixture judgment is not required. Record explicit model/reasoning overrides in the batch notes.

**Tooling check:** Before launching, identify the project's execution pattern (e.g., `npx tsx`, `.venv/bin/python`) and include it in the instructions so subagents don't fail silently with the wrong interpreter.

**For T2 promotions:**
> Run `/golden-create` for fixture `{FIXTURE-ID}`.

**For T1 verifications:**
> Adversarially verify golden fixture `{FIXTURE-ID}`. Your job is to find bugs,
> not confirm correctness.
>
> The verification protocol is at `tests/fixtures/golden/_verify-golden-outputs.md`
> and the format spec is at `tests/fixtures/golden/README.md`. Read the INPUT
> first — build your own mental model before looking at the golden output, then
> compare ruthlessly. Fix any issues directly in the files.
>
> Run the validator after edits:
> `npx tsx tests/fixtures/golden/validate-golden.ts {FIXTURE-ID}`
>
> Report: VERDICT (CLEAN or FIXED), what you changed if anything, validator result.

### 4. Update checklist and loop

Collect all verdicts. Update `_verification-checklist.md` yourself (not the
subagents — one writer avoids conflicts):
- CLEAN → `CLEAN (pass N)`
- FIXED → `PASS N (issues found: X)` with notes
- New golden → add row as `PENDING`

Report batch results, then loop back to step 1.

## Guardrails

- **Never read fixture content.** Subagents do the work. You stay lean.
- **Do not underpower semantic golden verification.** Most fixture verification needs high-capability judgment; downshift only for mechanical or validator-only work, and say why.
- **Don't verify what you just created.** New goldens get PENDING status; a
  different subagent verifies them next iteration. This is how we get context
  isolation — the verifier has zero memory of how the golden was written.
- **You own the checklist.** Subagents report; you write. One writer, no conflicts.
