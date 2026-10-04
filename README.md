# VLC timeline enhancements

A new macOS VLC project for hover thumbnail previews and persistent annotated
bookmarks on the actual playback timeline. Right-click a position to annotate it;
markers and hover text return when the same video is reopened. Videos stay untouched.

Start with [Ideal](docs/ideal.md), [Spec](docs/spec.md), preserved
[intake](docs/idea-intake.md), [plan](docs/plan.md), and
[Story 001](docs/stories/story-001-vlc-macos-feasibility.md).

Status: workflow setup only; feasibility and implementation have not begun.
No VLC version or integration architecture is selected. This folder is an
independent local Git repository nested under Ultima IV Web; no remote/commit
was created. Moving it later is possible; compatibility links are relative.

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

No native app build, web runtime, reserved port allocation, dependency hydration
hook or product eval runner exists yet. Story 001 determines the source/build
and fixture route. A future web/API helper must use Conductor port allocation;
this setup does not modify Conductor.
