---
name: golden-create
description: Create a golden reference output from input data — research the format, process inputs, produce expected output files.
user-invocable: true
---

# /golden-create [fixture-id | input-path]

Local variant: read `docs/evals/README.md` first. Our registry, contracts,
attempts, and golden metadata use the paths declared there; upstream backend
or PromptFoo examples are illustrative, not installed runtime. Deferred contracts
have no executable runner or measured score. Do not create a fake runner or
record a missing engine as a failed model attempt.


> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Create a golden reference test fixture from input data. The output doesn't need to
be perfect — `/golden-verify` catches issues on subsequent passes.

**Usage:**
```
/golden-create RA-003                           # inbox item or existing T2
/golden-create ~/recordings/grandma-interview/  # any input path
/golden-create                                  # scan inbox, pick first item
```

## Prerequisites

The golden workspace must exist at `tests/fixtures/golden/` with at least a
`README.md` format spec. If it doesn't, tell the user to run
`/setup-methodology` first.

## Where Things Live

- **Format spec:** `tests/fixtures/golden/README.md` — canonical schema reference
- **Verification protocol:** `tests/fixtures/golden/_verify-golden-outputs.md` — write with this in mind
- **Existing T1 fixtures:** Browse any `"tier": "T1"` fixture for a concrete example
- **Inbox:** `tests/fixtures/golden/_inbox/`
- **Validator:** `npx tsx tests/fixtures/golden/validate-golden.ts {FIXTURE-ID}`
- **Checklist:** `tests/fixtures/golden/_verification-checklist.md`
- **Coverage matrix:** `tests/fixtures/golden/_coverage-matrix.json`

## Workflow

1. **Research the format fresh.** Read README.md and one existing T1 fixture every time.
   Don't assume you know the schema from prior context — it may have changed.

2. **Find the input.** Check the given path, inbox, or existing fixture directory.
   If nothing exists, tell the user where to drop inputs.

3. **Read the input completely.** Build a thorough mental model of every entity,
   relationship, and claim before writing anything. This step determines output quality.

4. **Write the golden output** — `expected-entities.json`, `expected-questions.json`,
   `metadata.json`, `notes.md`. Set up the fixture directory if needed (move from
   inbox, name files per convention in README.md).

5. **Validate.** Run the validator until it passes clean:
   ```
   npx tsx tests/fixtures/golden/validate-golden.ts {FIXTURE-ID}
   ```

6. **Move the inbox item.** If the source came from `_inbox/`, move it to the new
   fixture directory now that processing is complete. This prevents other agents
   from re-processing it. If the fixture directory already has a matching source
   file, delete the inbox copy instead.

7. **Update tracking.** Add a PENDING entry to `_verification-checklist.md`. Update
   `_coverage-matrix.json` with the new fixture, `verification_status: "pending"`.

6. **Report** what was created, entity counts, anything interesting, and that
   verification is pending.

## Principles That Matter

These are what the verifier will reject you for violating:

- **sourceExcerpts must be real.** Actual quotes or close paraphrases from the input.
  If you can't find a quote for a claim, either the claim shouldn't exist or you
  missed something in the input.
- **Confidence can't exceed the input.** `stated` only for things explicitly said.
  `inferred` for logical deductions. Don't upgrade certainty.
- **Preserve ambiguity.** Guessing wrong is worse than flagging uncertainty. Use
  `unresolved_identities` for genuinely ambiguous references.
- **Don't aim for perfection.** A good-faith 90% golden is more valuable than no
  golden. `/golden-verify` exists for the last 10%.
