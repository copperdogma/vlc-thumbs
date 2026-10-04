# Imported skills and VLC applicability

Installed union: 29 Board Game Ingester names plus four Ultima-only skills,
33 total. Board Game Ingester is the default source for overlapping packages;
Ultima's generic `init-project` replaces the board-game-specific intake skill.
Ultima adds `create-eval`, `golden-create`, `golden-verify`, `golden-verify-reset`.
All selected skill files and bundled helpers are exact copies. The source
manifest records every file's original path/hash. Portable compiler/facts scripts
from Ultima have locally recorded project-name/status-scope adaptations.

`AGENTS.md`, this runbook, and other VLC-local runbooks govern domain-specific
commands and meaning. Imported references to games, scans, formats coverage,
Builder output, elderly users, engine recovery, source-project ADRs, backend
Python, `driver.py`, output schemas, or existing model credentials are examples
or absent source infrastructure, not VLC facts. Do not create them to placate a
skill. Do not copy source tests/evidence or claim their results for VLC.

| Imported guidance | VLC local equivalent |
|---|---|
| Raw scans / original game intake | Pinned VideoLAN source/build and legal video fixture provenance |
| Asset fidelity / golden output | Known frame/time correspondence, annotations, unchanged video bytes |
| Coverage matrix / source stages | `state.yaml` categories; fixture/build matrix deferred until real inputs |
| Browser inspection | Native macOS UI inspection for VLC; browser only for a real future browser UI |
| Source-project commands | Actual commands in this project's Makefile; build/UI commands added when verified |
| Source schemas / model baseline | Concrete VLC candidate contracts; deterministic behavior is not an LLM product task |
| Central tenets | Local media integrity, correct timestamp/identity, playback quality, inspectable evidence |
| Prior project ADRs | Local `docs/decisions/`; no decision exists yet |
| Scout index / docs/scout paths | `docs/research/scout.md` and `docs/research/` |

Active workflow package: init/setup, triage and leaves, create/build/validate/
close story, align/ADR/ideation, eval creation/improvement, scout and bounded
review. `/create-story` bundled template is an exact source template; replace
all placeholders and source-domain requirements with the local equivalents
above when authoring a VLC story.

Golden helpers, visual-inspect-loop, codebase/architecture audits, model discovery,
format-gap-analysis and learning/review helpers are installed but run only when
their substrate/problem applies. Model discovery and format-gap-analysis have no
current VLC lane. `/create-cross-cli-skill` is for a future skill-authoring task.
`/finish-and-push` needs an actual user commit/push request.

Inventory used a bounded Luna agent for mechanical comparison; main agent owned
selection and local meaning. Its preference for Ultima's shared tree was considered;
Board Game Ingester was chosen as the requested primary donor, with exact copies
and local overrides to prevent either source domain from governing VLC.
