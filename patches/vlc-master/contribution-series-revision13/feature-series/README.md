# macOS timeline hover previews

The exact combined source passes normal 009 `make check` and complete conventional 010
`make distcheck`. Current native evidence is scoped; historical shutdown 004 causality is
user-accepted deferred, and stale/inaccurate exposed progress plus broader reader/platform
coverage remain disclosed in [limitations](LIMITATIONS.md). Nothing has been submitted;
[CONTRIBUTION.md](../CONTRIBUTION.md) records executed commands and the separate, unexecuted
short host recipe.

## Behavior and support boundary

Hovering VLC's native macOS timeline adds an image and its actual **Keyframe**
time; the pointer time remains the seek target. The feature defaults on and has
an Interface preference. Failure or disabling it retains ordinary time hover.
Main, native-fullscreen, custom-fullscreen and detached controls share the owner.

Only regular local files qualify, including mounted NAS files. Exactly one video
must be selected. A sole video maps directly; multi-video flat AVC Matroska needs
an exact unique representable TrackNumber. Unsupported mappings fail closed.
The opt-in bounded Matroska scan rejects ordered/linked timelines, unknown-size
nested elements, invalid bounds and exhausted budgets; ordinary demux defaults
remain unchanged. This deliberately excludes some playable files.

Thumbnail identity includes source policy, selected video and transform version.
RAM/disk caches are 32 MiB/256 MiB. Fresh reopen requalifies metadata plus sampled
SHA256; unsampled changes can escape detection. Current-session RAM images may
show **Checking source** within one 15-second deadline that pointer activity
cannot extend. Change, source failure or expiry clears provisional images.
Annotations/bookmarks are outside this series.

## Review order

Base: VLC master `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
The [manifest](manifest.json) pins source files, modes, blobs and patch hashes.
The five raw `git apply` diffs have no invented authorship or attestation headers.

| Part | Source revision-12 size | What to review |
|---|---:|---|
| 0000: source-header distribution | 4,732 bytes; 3 paths; +18/−9 | Existing headers in distribution lists |
| 0001: contrib identity/admission | 13,511 bytes; 3 paths; +285/−1 | FFmpeg identity and bounded Matroska admission |
| 0002: helper/build/tests | 187,618 bytes; 20 paths; +3668/−6 | Private normal-contrib helper, protocol/build/package/tests |
| 0003: native service foundation | 220,377 bytes; 14 paths; +4695/−1 | Cache/scheduler/worker/service with focused tests |
| 0004: native context/hover activation | 94,739 bytes; 21 paths; +1468/−41 | Player context, native hover, preferences and focused tests |

This feature component has 59 unique source paths and 520,977 patch bytes.
Revision 12 changes only part 0003: covered-target scheduler reconciliation and
three foundation source/test files. The other four patches are exact revision 11
bytes. Separate baseline install/clock/TLS/GL/ownership/timer repairs belong to
the sibling prerequisite series; current full-gate evidence requires that combined
tree. Parts are review units, not independent releases. Maintainer boundaries
and FFmpeg ownership remain unagreed.

For a short first read: inspect this page, the ownership sketch below and
[LIMITATIONS.md](LIMITATIONS.md); then read parts 1→2→3→4 at the seams named above.
Part 0 is a separate distribution prerequisite. The [description](contribution-description-draft.md),
[commit-message drafts](proposed-commit-messages.md) and [screenshots](demonstration/README.md)
are supporting material. No private receipts are needed to read the package.

```text
main thread: player/context → hover owner → service scheduling/presentation
                                                    ↑ completion + epoch check
service serial utility queue: cache + source-verification state
             ├─ metadata serial utility queue → identity worker process
             └─ decode serial utility queue   → preview worker process
                                                    └─ private FFmpeg libraries
```

The service owns both worker controllers; filesystem/fingerprint/decode work
runs away from the UI thread/player lock. Worker protocol IO has deadlines;
stalled kernel IO/process reap has no hard timing guarantee. **Review question:**
is this retained private-helper boundary acceptable, or should a future native
preparser contract first supply explicit movie time and presentation lifetime?
Native preparser feasibility is unresolved, not disproved.

## Apply and review tests

From the pinned VLC source root, replace `/path/to/feature-series` below:

```sh
for patch in 0000-source-header-distribution.patch 0001-contrib-matroska-identity-and-admission.patch 0002-timeline-helper-build-package-and-tests.patch 0003-macosx-thumbnail-service-cache-worker.patch 0004-macosx-timeline-context-and-hover.patch; do
  git apply "/path/to/feature-series/$patch"
done
```

After applying, `bin/timeline-preview/README.md` is the full normal-contrib build
recipe; `bin/timeline-preview/tests/README.md` covers synthetic media, direct
identity/AVIO probes and guarded ENOSPC. These are paths in the patched VLC tree.
Use its native arm64 host/tool setup before running these existing targets from
the configured build directory:

```sh
make -C bin check-timeline-preview
make -C modules check-macosx
make -C modules check-timeline-cache check-timeline-service-edges
make -C modules check-timeline-context check-timeline-hover-reentrancy
make -C modules check-timeline-player-context
```

Expect successful target exits and XCTest zero failures; the owned-volume ENOSPC
case normally skips without its explicit guard. The helper target alone omits
fixture matrices. For the full matrix, generate fresh `media`, `identity` and
`admission` directories using the three generator commands in the source guides,
then run from the source root with Python3.9+ and FFmpeg/ffprobe test encoders:

```sh
fixture_root=$(mktemp -d)
helper=/path/to/build/bin/vlc-timeline-preview
python3 bin/timeline-preview/tests/generate_fixtures.py --output "$fixture_root/media" --ffmpeg ffmpeg --ffprobe ffprobe
python3 bin/timeline-preview/tests/generate_dependency_fixtures.py --output "$fixture_root/identity" --ffmpeg ffmpeg
python3 bin/timeline-preview/tests/generate_admission_fixtures.py --output "$fixture_root/admission" --ffmpeg ffmpeg --ffprobe ffprobe
python3 bin/timeline-preview/test.py --helper "$helper" \
  --fixtures "$fixture_root/media" --trim-fixtures "$fixture_root/media" \
  --identity-fixtures "$fixture_root/identity" \
  --admission-fixtures "$fixture_root/admission" > "$fixture_root/results.json"
```

Expect JSON `pass: true`, a counted checks list and exit 0; preserve fixture/tool
and helper hashes. Headless tests do not qualify pointer behavior, reader output,
NAS cold/stall behavior or matched playback cost. The source guide also gives the
exact conventional `make -C "$vlc_output" -j4 distcheck` command and required
GNU-sed/environment/flags. [VideoLAN's submission guide](https://wiki.videolan.org/Sending_Patches_VLC/)
requires error-free `make check` and complete `make distcheck` for added files;
current combined normal 009 and complete 010 meet those two gate requirements; deferred shutdown 004 causality and scoped native/reader/platform limits remain disclosed.

**Revision 12 staged source:** five-patch replay exactly reproduces
`94a7f24d29860562783da076bdb512d39756c41f`. The three changed foundation files have focused
headless proof: scheduler regression and finite service quiescence pass; the
original scheduler class fails four covered-state assertions. The existing
supersession case now waits for causal setup and bounded successful completion.
Closed33/17/22-path confirmation covers all 72 current source files. Normal009
complete registered check and complete conventional 010 distcheck pass on the
combined tree; native284 unique cases report 283 pass/one optional skip, lifetime 5/5
and registered helper basic13/13 pass. These nested layers overlap. Full helper 77
was not rerun by 009/010. Historical screenshots/NAS/playback retain their own pins.
Historical004 cause remains user-accepted deferred; narrow reader and seek/Quit
comparison outcomes are stated above. Customroundtrip002 remains partial, without
returned-main hover or complete roundtrip qualification.

See the canonical [macOS GUI test-host recipe](../CONTRIBUTION.md) for complete
normal metadata, fresh namespaces, target-only identity embedding and ordinary
normal check/fresh outer distcheck. It is newly documented and unexecuted;
actual010 used a private read-only preflight forwarding the original test driver.
No equivalent public-recipe execution or ready-to-submit status is claimed.
