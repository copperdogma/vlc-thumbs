# macOS timeline hover previews

**Prepared for maintainer review; submission checklist incomplete.** Nothing has
been submitted. The candidate has an unresolved shutdown SIGSEGV; conventional
`make check`/`make distcheck` are non-green. Actual VoiceOver navigation and
Intel/older-macOS execution remain unqualified. See [limitations](LIMITATIONS.md).

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

| Part | Revision-11 size | What to review |
|---|---:|---|
| 0000: source-header distribution | 4,732 bytes; 3 paths; +18/−9 | Five existing headers in Automake lists; no runtime changes |
| 0001: contrib identity/admission | 13,511 bytes; 3 paths; +285/−1 | FFmpeg TrackNumber and bounded opt-in Matroska scan |
| 0002: helper/build/tests | 187,618 bytes; 20 paths; +3668/−6 | Protocol4 worker, normal FFmpeg9 contrib, packaging, portable fixtures |
| 0003: native service foundation | 214,638 bytes; 14 paths; +4598/−1 | Cache, scheduler, worker, service and their tests; no production activation |
| 0004: native context/hover activation | 94,739 bytes; 21 paths; +1468/−41 | Player epochs/context, hover panel, preferences, activation and focused tests |

This map totals 59 unique paths and 515,238 patch bytes. The two native build
lists occur in both parts 3/4. Parts 2/3 depend on part 1; part 4 activates part 3
and uses part 2. These are review units, not independent releases. FFmpeg
dependency ownership and its eventual submission route are not agreed.

Revision 10 had four patches totaling 510,405 bytes; its largest native patch
added 6,021 lines. Revision 11 separates the service foundation (+4,598 lines)
from context/activation (+1,468), about a 23.6% reduction in the largest native
review unit. Intermediate foundation compile/link and its 265-execution suite passed
with one optional skip, using freshly built native objects and verified reused
core/contrib/runtime inputs. This is no from-scratch whole-core/contrib proof.

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
the recorded failures and partial install/cleanup results do not satisfy it.

**Revision 11 qualification:** exact five-patch application reproduces source tree
`f8f7d0fdb46c1ae25ba94049143d12ecb7daf96c`. Normal helper/module builds and headless
tests passed: 77 helper checks and 284 unique native executions (283 passes,
one optional ENOSPC skip). The service reentrancy regression passes with the fix
and fails against an isolated original-service object. Helper success checks now
reject error-only replies; duplicate hover execution and copied geometry coverage
were removed without deleting distinct behavior contracts. A final two-line test
aggregation correction preserves the three unique registered bundles.

These changes have no new packaged-app or GUI qualification. Screenshots and
native/NAS/playback measurements below [limitations](LIMITATIONS.md) are historical
through revision 10; the changed helper/service have current headless qualification
only. Original failed setup attempts and make-check/distcheck/shutdown/reader/
platform limits remain. Prepared for maintainer review; submission checklist incomplete.
