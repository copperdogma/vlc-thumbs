---
name: golden-verify-reset
description: Reset the golden verification checklist to force re-verification of all T1 fixtures.
user-invocable: true
---

# /golden-verify-reset [--all | fixture-id]

Local variant: read `docs/evals/README.md` first. Our registry, contracts,
attempts, and golden metadata use the paths declared there; upstream backend
or PromptFoo examples are illustrative, not installed runtime. Deferred contracts
have no executable runner or measured score. Do not create a fake runner or
record a missing engine as a failed model attempt.


> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Reset golden fixture verification status to force re-verification.

**Why:** After schema changes, model upgrades, or when you want to double-check
previous verifications with fresh eyes. Useful before an overnight `/golden-verify`
run to force a complete re-check.

**Usage:**
```
/golden-verify-reset              # reset all CLEAN fixtures to PENDING
/golden-verify-reset LC-001       # reset one specific fixture
/golden-verify-reset --all        # reset everything including PASS entries
```

## What It Does

1. Read `tests/fixtures/golden/_verification-checklist.md`
2. Reset statuses:
   - Default: `CLEAN (pass N)` → `PENDING — reset for re-verification`
   - `--all`: also resets `PASS N (issues found: X)` entries
   - `fixture-id`: resets only that entry
3. Preserve audit trail — set Last Pass Notes to `Reset YYYY-MM-DD. Previous: {old status}`
4. Report how many fixtures were reset

## Example

Before:
```
| 1 | LC-001-childhood-summer-lake | CLEAN (pass 1) | All good. |
```

After:
```
| 1 | LC-001-childhood-summer-lake | PENDING — reset for re-verification | Reset 2026-03-01. Previous: CLEAN (pass 1) |
```

## Guardrails

- Only modifies `_verification-checklist.md` — never touches golden output files
- Previous status is always preserved in Last Pass Notes for auditability
