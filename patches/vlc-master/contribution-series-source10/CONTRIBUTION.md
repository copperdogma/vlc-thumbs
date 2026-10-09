# Native macOS timeline keyframe previews

Hovering VLC's timeline shows an image and its actual **Keyframe** time so users
can inspect a scene before seeking. Pointer time remains the seek target.
Previews default on, have an Interface preference, and fall back to ordinary time
hover for unsupported media or failures. Bookmarks are outside this contribution.

The existing player supplies selected-video identity and an input epoch. A
service owns scheduling, stale-result cancellation and bounded caches. Retained
private helpers built through FFmpeg contrib perform metadata/decode work outside
the UI thread and player lock, preserving tested movie-time/track correspondence
without changing normal demuxing.

## Apply and review

Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Combined tree: `b7c0f24e442c35a57bb108d56b801fd05b624943`.
Feature midpoint: `cce7f9917b8dc4d5432e7f83b2c840f8c3c5027b`.

Apply all thirteen entries in [contribution-series](contribution-series) once:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

**P** means `blocker-prerequisites/`; **F** means `feature-series/`.
Start with the [review map and reproduction route](feature-series/README.md).
The [prerequisite map](blocker-prerequisites/README.md) explains each accompanying
repair. P0006 extends F0004's controller test; P0007 uses registration modified by
F0003/F0004. These are logical review groups, not independently qualified stacks.
Reordering needs new application and affected-consumer proof.

The [manifest](contribution-manifest.json) pins patches and intermediate trees:
72 combined paths, 59 feature paths, six overlaps. [Thirteen draft messages](feature-series/proposed-commit-messages.md)
follow the canonical order.

## Validation and limits

| Area | Result and qualification boundary |
|---|---|
| Build/tests | Normal build/full registered `make check` and 77 helper matrix checks pass. Nested counts overlap; zero targeted cast warnings is not universal warning-free proof. |
| Distribution | Complete conventional `make distcheck` passes through cleanup; optional skips remain. Read-only archive preflight forwarded ordinary test-driver argv/status. |
| Reproduction | Public commands passed in stages; the uninterrupted public sequence, including fresh outer distcheck, is unexecuted. |
| Package | Signatures, 398 loadables and two-fixture helper relocation pass. Source-only proposal. |
| Native UI | Main/custom-fullscreen hover and returned-main preview persistence observed. Ordinary controls fade; cause and broader lifecycle remain unknown. |
| Reader/seek | Narrow ordinary-main reader proof inherited. Preview-visible/fullscreen reader, accurate exposed position and precision seeking remain unqualified. |
| Playback/resources | Three matched 60 s pairs: zero native video/audio losses, continuous captured audio. Mean CPU overhead+1.47–2.29 percentage points; sampled maximum app+worker RSS+97.6–100.6 MiB. System-mixed audio/shared-host sampling limits apply. |
| Shutdown/platforms | Narrow ordinary Quit observations; historical crash cause unresolved. Intel/older macOS/external CI unavailable. |

[Detailed limits](feature-series/LIMITATIONS.md) preserve measurements, exclusions
and failures. Regular local/NAS files qualify; URLs and unsupported track/timeline
mappings fall back to time hover. Freshness uses sampled SHA256, which can miss
unsampled changes. Caches are 32 MiB RAM/256 MiB disk; provisional images expire
within 15 s. [Historical screenshots](feature-series/demonstration/README.md) illustrate
earlier rendering, not current-tree proof.

## Reproduce and credit

Use the [ordinary build/test route](feature-series/README.md); optional GUI
isolation is separate. The patched helper/test READMEs describe contrib setup and
synthetic fixtures. No private harness is required.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance. Retain GPL/LGPL and third-party notices; no assignment or sign-off
is asserted. No binaries/private media included. Upstream submission and acceptance
remain separate.
