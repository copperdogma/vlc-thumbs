# Story004 current implementation and delivery — 2026-10-05

Qualified222506 is installed locally. [Acceptance ledger](current-acceptance-ledger.md)
maps current source/contracts, four native surfaces, NAS restart/pending images,
settings/controls, playback/resource trials and delivery provenance. Earlier
snapshots below are historical attempts, not current blockers or scores.

## Historical pre-resumption snapshot

# Story 004 local implementation status — 2026-10-05

Historical pre-resumption snapshot below. Freshness is now accepted and Movies/
desktop available; later213341 progress and remaining gates are recorded in
[NAS validation progress](nas-validation-progress.md). The linked local-contract
results have been refreshed to that helper/source revision.

The persistent helper, finite progressive/hover scheduler, bounded reusable cache
and asynchronous service are implemented in the isolated candidate. The installed
VLC Timeline Preview app remains Story 002 build155231. Story 004 is In Progress.

[Local contract results](local-contract-results.json) record tested source hashes,
helper provenance and actual test results. Helper v2/v3 samples match on seven
generated fixtures; malformed requests, idle reuse, mutation and independent
blocked read/open/stat deadlines pass. Cache contracts pass 2,835 checks; scheduler
contracts pass; service contracts pass 29 checks, including cached presentation
bypassing active decoding, actual-keyframe cache reuse, restart, bounded latest
intent, canceled contexts and clearing current cached presentation after mutation.
The real-helper Cocoa smoke passes with one worker across misses and disk reuse
without a decoder launch after reopening.

Review led to separating coordinator/cache presentation from decoding, guarded
metadata subprocesses, demand-only cache eviction and notifying the current hover
when any request invalidates media. Background preparation stops at cache capacity
instead of evicting/regenerating its own finite plan. Failure records are capped.

The signed development build manifest is
`work/validation/story002/app-build-20261005T180959.584821Z.json`.
It is a build result, not native feature acceptance. Local AB/BA helper diagnostic
results are retained under `work/validation/story004/local-helper-comparison-final`:
all four targets succeeded per arm/block, but first candidate startup was 183.6 ms
versus 8.1 ms on the later candidate block. This variability prevents a universal
speedup claim. No native or NAS speedup is inferred from it.

Required qualification remains: cache freshness product choice, native four-surface
presentation/preference, NAS before/after and practical controls/playback/resource
comparison. CUA verified the desktop locked. The native control attempt failed
activation before valid observations; it is setup-invalid. Movies is not mounted,
so the NAS helper attempt is also setup-invalid. All attempts are retained under
ignored work. The existing +20% baseline-median control allowance is unchanged.

ADR-003's sampled freshness proposal is not enabled without explicit acceptance.
Full-file verification remains the default, so a large remote file can still spend
its identity deadline reading bytes; this candidate is not ready for daily delivery.
No video, installed ordinary VLC, bookmark store or source neighbor was changed.

A follow-up unified nearby-image distance across the service and panel: half the
finite coarse interval, bounded to 2–60 seconds. The 29th service check verifies
that shared policy. Final180959 candidate built and signed; native remains untested.
