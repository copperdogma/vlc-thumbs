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
  ADR-001 accepts durable Application Support labels and separate Caches
  thumbnails. ADR-002 selects a private existing-contrib libav helper with keyframe-first
  MVP sampling. Annotation schema/identity and a maintained fork remain undecided.
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

Stories001 and002 are Done within their declared scopes. Story004 corrections are Done on001728: track-count guard and bounded demand retention pass. Story003 short
bookmarks remains planned; integrated root and public distribution are deferred.
VLC3.0.24 is pinned. Corrected candidate001728 is installed at Cam's requested local preview
app; previous app is preserved under ignored work. Persistent private worker,
finite progressive/hover preparation and32MiBRAM/256MiBdisk cache are implemented.
ADR003 accepts metadata plus sampled SHA256 freshness, with its unsampled-change
limitation. Current-session RAM images may show Checking source provisionally;
shared15s expiry cannot be renewed by pointer movement. Fresh reopen qualifies
before reuse; source failure/change clears provisional images.

See docs/evidence/story-004/current-acceptance-ledger.md for current source/build,
3410cache/40service contracts, final NAS/restart and explicitly inherited unchanged native four surfaces/MP4/MKV/preferences,
20/arm control comparison and three active-preparation playback pairs. Control
medians37.612/37.635ms meet baseline+20%; audio/drop checks pass while sampled
CPU/RSS overhead is reported. Reader-focus proof is explicitly inherited from
unchanged accessibility behavior; latest actual-reader startup was inconclusive.
No universal/p95 latency, causal-stall attribution, exhaustive formats, forced
NAS reconnect or public packaging is qualified. Bookmarks need separate durable
identity/schema decisions. No new commit/push authorization is implied.

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
