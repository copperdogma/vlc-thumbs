# Story004 correction validation — candidate001728

## Findings first

The original validation found two runtime defects: wrong-track images when VLC/libav count mappings disagree, and RAM-hot payload loss during background quota pruning. Both have reproduced failing baselines and corrected regression passes. A stronger newer-background pressure case rejected the intermediate mtime-only fix; the final cache uses bounded demand priority while retaining the hard quota. Additional review found incompatible legacy test commands, now explicitly retired with current replacements documented. No remaining material code findings were reported by scoped independent and Codex reviews.

**Grade B (86/100). Close now.** The declared story scope is implemented and validated; no remaining material findings or implementation gaps. Evidence limits below remain explicit.

## Scope and decision fit

All local tracked and untracked changes were inventoried and reviewed during the original validation. This correction pass inspected the changed helper/protocol, cache API/implementation/contracts, service mapping namespace/regression, retired commands and reconciled documentation; unchanged files retain that prior review. Commands: `git status --short`, `git diff --stat`, `git diff`, `git ls-files --others --exclude-standard`; inventories are retained under ignored `work/validation/story004/validation-final-*`. ADR001 storage lifetimes, ADR002 private libav route and ADR003 sampled freshness remain applicable. Ideal stays implementation-free. No external library/code was added.

Final build provenance is [001728](app-build-correction-001728.json). Its source hashes match current inputs; deep strict signature and exact staged component parity pass. [Local contracts](local-contracts-correction-001728.json) record3410/3410cache checks and40/40service checks, mapping namespace invalidation, current packaged mismatch tests, and eight unchanged Mach-O TEXT sections. [NAS](native-nas-correction-001728.json) records10/10matching physical-pointer images after fresh launch, cached target reuse without decoder reads, intact source samples and frozen inputs. The prior235648 malformed-track UI shows blue playback with honest unavailable preview; its helper/controller/context/UI source hashes are unchanged in001728. Its four-surface/CLIoff/main-pointer proof is likewise inherited for unchanged adapters; final NAS integration exercises the changed cache. This is proportional evidence reuse, not a fresh whole-interface claim.

## Verification limits

Current-session cached thumbnails bridge source checks; fresh reopen still qualifies metadata plus sampled hashing. Unsampled changes can escape detection. Cold NAS misses may take seconds or timeout and recover; the27.9s intermediate attempt remains recorded. The unsigned unchanged helper fault suite passes; packaged injected-blocked-read qualification remains inconclusive despite code-section parity. Native assignment timing is not compositor latency. Reader focus and Save/Cancel/restart preference proof are explicitly inherited for unchanged UI/preference paths; fresh actual-reader startup was inconclusive. Upstream tests remain historical for unchanged core/TLS/dependency code. No universal/p95 latency, causal stall attribution, forced NAS disconnect, exhaustive formats, public distribution or bookmark/root proof is claimed.

## Learning review

RESULT: no-candidate
Reason: The correction reinforced already-covered findings-first, baseline reproduction, bounded research and current-candidate validation rules; the concrete defects belong in product regressions.
Evidence checked: original validate report, correction baselines, cache/helper/service tests, scoped review ledger and applicable AGENTS/validate guidance.

## Story Validation

All10acceptance criteria are **Met** in the [current ledger](current-acceptance-ledger.md), including safe reuse, truthful native UI and resource retention reopened by validation. All12implementation tasks are complete. Architecture/quality/functionality/performance/testing/docs gradeB; improvements remain broader media coverage and stronger reader/compositor/causal attribution outside this declared scope. No score claims the full North Star or bookmarks.

Final20-per-arm control comparison is valid:37.612ms baseline/37.635ms feature,+0.062%,within prospective+20%. Three matched60s playback pairs pass audio/drop checks with130–138background jobs; costs and limits in [playback](playback-correction-001728.json). Exact qualified components installed, deep signature passed, normal-profile pointer image inspected ([delivery](local-preview-update-001728.json)). No further tests warranted without new code/failure.

Workflow gates: `/build-story` complete; `/validate` complete; `/mark-story-done` close-out applied under Cam's approved correction plan. All applicable tenets verified; dependency002Done; ADR003 remains accepted. **Remaining Story Gaps: none within declared scope.** Close-out bookkeeping completed separately and not counted as implementation quality. Root awaits003. No commit/push/publication authorized or performed.
