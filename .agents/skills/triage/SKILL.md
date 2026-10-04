---
name: triage
description: Orchestrate Board Game Ingester triage from Ideal/spec/coverage facts and neutral lane packets, then recommend the best next action
user-invocable: true
---

# /triage [stories|inbox|evals|architecture|health] [sub-arg]

> Alignment check: Before choosing an approach, verify it aligns with
> `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
> `docs/methodology/graph.json`, `tests/fixtures/formats/_coverage-matrix.json`,
> and relevant decision records in `docs/decisions/`. If none apply, say so
> explicitly.

`/triage` is the meta-skill. It does not own backlog, inbox, eval,
architecture, or health logic itself. In full-sweep mode it starts from the
Ideal/spec/state/graph/coverage frame, gathers neutral lane packets, shows the
top three cross-domain candidates, then synthesizes one recommended next
action.

Board Game Ingester's north star is raw scans in, Builder-ready assets out,
with no silent losses. Triage should prioritize source fidelity, no
downsampling, traceability, coverage/eval/golden evidence, and Builder-ready
handoff over convenient backlog motion.

## Worker Model Sizing

When full-sweep triage launches neutral lane packets with subagents, size each worker model and reasoning level to lane risk. Use cheaper or lower-reasoning workers for factual scans and mechanical packet gathering; keep stronger workers for semantic contracts, security, eval correctness, cross-repo decisions, or high-cost misses. Record any explicit override rationale in the triage report.

## Routing

| Invocation | Behavior |
|---|---|
| `/triage` | Full-sweep orchestrator mode |
| `/triage stories` | Delegate to `/triage-stories` |
| `/triage stories 009` | Delegate to `/triage-stories 009` |
| `/triage inbox` | Delegate to `/triage-inbox` |
| `/triage inbox scan` | Delegate to `/triage-inbox scan` |
| `/triage evals` | Delegate to `/triage-evals` |
| `/triage evals scan-crop-detection` | Delegate to `/triage-evals scan-crop-detection` |
| `/triage architecture` | Delegate to `/triage-architecture` |
| `/triage architecture asset_pipeline` | Delegate to `/triage-architecture asset_pipeline` |
| `/triage health` | Delegate to `/triage-health scan` |
| `/triage health scan` | Delegate to `/triage-health scan` |

When a scope is provided, hand off completely to the leaf skill. Do not
maintain duplicate logic here.

## Leaf Skills

- `/triage-stories` — backlog prioritization, readiness, dependency bottlenecks
- `/triage-inbox` — inbox scan or processing
- `/triage-evals` — eval health, rerun candidates, compromise deletion signals
- `/triage-architecture` — bounded structural simplification / cleanup lane
- `/triage-health` — read-only freshness packet across coverage, codebase
  improvement, eval/model/golden, methodology/tooling, architecture-audit, and
  dependency/provider health
- `/codebase-improvement-scout` — report-first codebase hygiene follow-up when triage recommends it
- `/discover-models` — provider/model freshness follow-up when triage recommends it

When full-sweep `/triage` asks a leaf for input, request a compact lane packet
instead of a final repo-wide decision. Each packet should provide up to three
neutral candidates with candidate name, lane type, Ideal/spec value, evidence,
why now, action shape, story-worthiness or eval/audit/health scope,
validation/stop condition, blockers, and reasons not now.

The main `/triage` thread owns cross-domain ranking. Do not preselect one
"largest gap" so narrowly that leaf lanes ignore stronger evidence in their own
domains.

## Full-Sweep Mode

When invoked with no scope:

1. **Read the shared frame**
   - `docs/ideal.md`
   - `docs/spec.md`
   - `docs/methodology/state.yaml`
   - `docs/methodology/graph.json`
   - `tests/fixtures/formats/_coverage-matrix.json`
   - `docs/stories.md` only as a generated index into authored story files
     under `docs/stories/`, plus `docs/build-map.md` if present
   - recent `git log --oneline -20`
   - relevant ADRs under `docs/decisions/`

2. **Start neutral lane evidence, then run the fact collector directly**
   - Unscoped `/triage` is a contracted fan-out command. Treat the user's
     invocation of unscoped `/triage` as explicit authorization to use the
     runtime's subagent/delegation tool for neutral lane packets when it is
     available and safe for the current checkout.
   - Immediately launch scoped neutral packet requests for:
     - `/triage-stories`
     - `/triage-inbox scan`
     - `/triage-evals`
     - `/triage-architecture`
     - `/triage-health scan`
   - In the main thread, run:

     ```bash
     python3 scripts/triage_facts.py --json
     ```

   - Use the facts for branch/dirty state, skill-surface link or optional-alias drift,
     story/eval recommendations, stale eval scores from repo score history,
     coverage-matrix status, inbox counts, architecture-audit cadence,
     codebase-improvement freshness, lane presence, and recent churn.
   - Treat an absent codebase-improvement report as health freshness evidence,
     not as a required-file failure.
   - If subagents/delegation are unavailable, unsafe for the current checkout,
     or the user explicitly asks not to use them, still run the fact collector
     here, then query the same neutral packet contracts sequentially later and
     state that fallback in the response.

3. **Open candidate gaps without picking a winner yet**
   - State 2-4 plausible unmet Ideal promises or overscaffolded compromises.
   - Map each to spec section(s), methodology category, phase, coverage row if
     relevant, and evidence.
   - Do not pick the final winner before lane packets report.

4. **Run actionability and eval-ladder gates**
   - Last meaningful action, date, proof artifact, and what materially changed.
   - For AI capability or image-stage work, identify the root/parent/child eval
     placement and inspect eval/golden score history before recommending
     implementation backlog.
   - Blocked stories and exhausted eval retries remain health flags unless
     current evidence satisfies the unblock/retry condition.

5. **Apply phase pressure**
   - `converge` -> delete/simplify/collapse residue when honestly possible.
   - `climb` -> improve capability, widen proof, add measured substrate.
   - `hold` -> make existing substrate cheaper, simpler, or easier to operate
     when stronger lines are not actionable.

6. **Collect lane packets and calibrate against the Ideal**
   - Keep `scripts/triage_facts.py` as a direct main-thread fact source, not a
     delegated lane and not a substitute for leaf judgment.
   - Add a compact `Vs Ideal` read: literal north-star distance, current-tech
     progress, and whether the line of travel is improving, mixed, stalled, or
     blocked.

7. **Build the top-three shortlist**
   Each item must include:
   - original lane packet candidate name
   - recommendation
   - lane type
   - Ideal/spec value
   - evidence
   - why now
   - action shape
   - story-worthiness or lane scope
   - validation or stop condition
   - blockers
   - reasons not now
   - why it ranked above or below the other two

8. **Synthesize one final recommendation**
   Rank the problem first, then choose the vehicle that best advances it:
   continue/expand/reopen/consolidate a story, create a story, run an eval,
   run architecture work, run health/tooling work, or no-op.

   Before recommending `create a story`, challenge that choice against the last
   2-4 stories on the same problem line. If the runtime seam, fixture/eval
   boundary, emitted artifact contract, and operator-facing outcome are the
   same, prefer continuing, expanding, reopening, or consolidating over creating
   a tiny story fragment.
   When a new story is still the right vehicle, do not default to a few-minute
   slice. If adjacent work shares the same fixture, eval, artifact contract, or
   operator-facing proof boundary, expand the boundary toward roughly one
   focused AI hour of implementation plus validation, or longer when that is
   the smallest coherent milestone. Treat that as a sizing heuristic, not a
   quota; keep tiny stories only for genuine high-risk unknowns, blockers, or
   indivisible proof boundaries.

9. **Return a short report**

```markdown
## Triage

### Candidate Gaps
- {candidate gap + spec/category/phase/coverage}

### Vs Ideal
- Literal north-star: {distance from raw scans -> Builder-ready assets}
- Current-tech read: {present-day progress}
- Direction: {getting closer | mixed | stalled | blocked} - {why}

### Top Three
1. {original lane packet candidate name}: {recommendation}
   - Lane type: {story | inbox | eval | architecture | health}
   - Ideal/spec value: {refs + value}
   - Evidence: {files/facts}
   - Why now: {trigger}
   - Action shape: {continue story | expand story | create story | eval | audit | health | no-op}
   - Story-worthiness / scope: {AI-sized story | expand existing story | eval-only | audit-only | health-only | no-op}
   - Stop condition: {validation/proof}
   - Blockers: {if any}
   - Reasons not now: {if any}
   - Rank rationale: {why here}
2. {same fields}
3. {same fields}

### Final Recommendation
- {one next action}

### Handoff
Reply yes to proceed with: {exact next command or concrete action}.
```

## Guardrails

- Full-sweep mode is read-only.
- Surface the top three recommendations before the final recommendation.
- Do not pick the final winner before neutral lane evidence can surface
  stronger domain-specific candidates.
- Do not hide the lower-ranked top-three candidates.
- Do not fragment work into tiny stories when a coherent story line already
  owns the same fixture/eval/artifact boundary.
- Treat roughly one focused AI hour of implementation plus validation as a
  sizing calibration for new stories when adjacent work can be bundled
  honestly; it is not a quota and should not pad indivisible risk probes.
- Do not recommend implementation when a parent eval failure is still too vague
  to classify.
- Do not recommend build work for AI/image stages before naming the current
  eval/golden proof boundary.
- Do not claim asset correctness from non-crashing logs; proof must include
  artifact, manifest, or eval evidence.
- Do not route planning fixes through generated `docs/stories.md`; update the
  authored story, state, eval, coverage, ADR, or AGENTS surface instead.
- Do not recommend work that violates source fidelity, no-downsample,
  traceability, reversible transform, or Builder-ready handoff tenets.
- Do not recommend "no action" unless every plausible phase-aligned move is
  blocked, exhausted, or lacks a bounded falsifiable next step.
