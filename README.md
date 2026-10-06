# VLC timeline enhancements

A new macOS VLC project for hover thumbnail previews and persistent annotated
bookmarks on the actual playback timeline. Right-click a position to annotate it;
markers and hover text return when the same video is reopened. Videos stay untouched.

Start with [Ideal](docs/ideal.md), [Spec](docs/spec.md), preserved
[intake](docs/idea-intake.md), [plan](docs/plan.md), and
[Story 001](docs/stories/story-001-vlc-macos-feasibility.md).

Status: Stories002 and004 thumbnails are Done. The local signed001728 app at
`~/Applications/VLC Timeline Preview.app` prepares sparse keyframes progressively,
prioritizes the current hover and nearby positions, and retains bounded thumbnails
across reopen/restart. Current-session cached images can show “Checking source…”
while NAS validation runs; reopening first checks metadata and sampled SHA256.
The default-on checkbox remains in Interface > Playback behaviour.

Bounded native, NAS restart and practical controls/playback checks pass; unchanged
four-surface, MP4/MKV and preference/reader evidence is explicitly inherited.
Track-count mismatches now reject safely, and hovered images receive bounded
retention priority over background thumbnails. See the
[acceptance ledger](docs/evidence/story-004/current-acceptance-ledger.md) and
[local update](docs/evidence/story-004/local-preview-update-001728.json).
Shared-host measurements do not establish universal/p95 latency or causal stall
attribution. Reader focus uses explicitly inherited unchanged-interface evidence;
the latest reader startup was inconclusive. Story003 short bookmarks and the
integrated root remain planned/deferred.

This is an independent Git project nested under Ultima IV Web, with a public
[GitHub repository](https://github.com/copperdogma/vlc-thumbs). Compatibility
links are relative; neighboring projects are read-only workflow sources.

## Local workflow

Requires Node.js, Bash and Make; no npm install or paid API is needed.

```
make methodology-compile
make skills-sync
make validate
node scripts/triage-facts.mjs --json
```

The checks verify project scaffolding, not working VLC features. All 33 skills
from Board Game Ingester plus Ultima's additional skills are installed with
support files and provenance. See [skill routing](docs/runbooks/skills.md) and
[setup checklist](docs/setup-checklist.md). Shared contracts are preserved;
local instructions override examples from other products.

The [build runbook](docs/runbooks/build-vlc-macos.md) records the working native
development route. No web server or reserved port is needed; native capability runners exist.
Native code and a private decoder helper do not require Conductor allocation.
