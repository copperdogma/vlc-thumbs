# Public source package inventory — Story 005

Read-only package review on 2026-10-05/06. Candidate:
`work/upstream/vlc-master-story005-candidate`, HEAD/base
`2e358f3098c2f2b7621d1dc568de8b61ad786322`; pristine comparison:
`work/upstream/vlc-master-story005`. This is a live, uncommitted builder tree;
the exact final public diff must be reviewed again after integration. No product
source, installed app, media, author configuration or remote was changed by this
review. Source-package readiness is incomplete; this does not certify binaries,
native behavior, upstream acceptance, Intel or older macOS coverage.

## Source and attribution

| Files/source | Observed license and provenance | Public-package requirement |
|---|---|---|
| `bin/timeline-preview/timeline-preview.c` | GPL-2.0-or-later; retained from wrapper `src/thumbnail-helper/thumbnail-helper.c`, then adapted to protocol4/FFmpeg9. Both retain generic `Copyright (C) 2026 VLC timeline enhancements contributors.` | Record retained-source provenance and actual contributor attribution. The collective placeholder is not evidence of the human copyright holder. Root must resolve the final header/commit author truth without inventing attestations. |
| `modules/gui/macosx/timeline/VLCThumbnail{Cache,Scheduler,Service,Worker}.{h,m}` | GPL-2.0-or-later SPDX; port of same wrapper `src/macosx/` components | Preserve license and record retained/adapted source ownership; surrounding upstream macOS files use full GPL notices with copyright/author lines. SPDX alone supplies license intent but not individual attribution. |
| `timeline/VLCTimelineContext.{h,m}`, `VLCTimelineContextTests.m`, `VLCTimelineContextTestSupport.m` | GPL-2.0-or-later SPDX; new master context seam/tests | Same truthful attribution review; test support is isolated test-only code and must remain outside application sources. |
| `modules/gui/macosx/tests/VLCThumbnail{Cache,Scheduler,Service}Test.m`, `VLCThumbnailTestHelper.c`, `VLCTimelineHoverTest.m`, `bin/timeline-preview/test.py` | GPL-2.0-or-later SPDX; wrapper-derived contract tests and new identity/fault/UI seams | Retain notices and tests in dist inputs. No private media needed by cache/context/mock-worker tests. |
| Existing slider/player/Main/preferences/window sources | Existing VLC GPL2-or-later full headers remain, e.g. slider credits Marvin Scholz and VLC authors/VideoLAN | Preserve existing authors. New changes do not justify replacing prior copyright or assigning all work to one author. |
| `contrib/src/ffmpeg/matroska-track-number.patch` | 406-byte raw diff against FFmpeg9 `libavformat/matroskadec.c`; that source retains FFmpeg Project copyright and LGPL2.1-or-later notice | Create a separate reviewable FFmpeg dependency change with motivation, semantics, regression and truthful author identity. Raw patch currently has no From/Subject/body, authorship or tests. Do not describe it as ready for FFmpeg submission. |
| Wrapper fixture generators and direct dependency probes listed below | LGPL-2.1-or-later SPDX; standalone mathematical patterns/standard-library container manipulation | Preserve their licenses when copying. A GPL application/helper does not require stripping the compatible LGPL source notices from independent tools. |

VLC's source tree supplies `COPYING` (GPLv2) and `COPYING.LIB`. The pinned
macOS style is concrete source evidence, not a discovered mandatory full-header
policy. Configured Cam Marsollier name/email is an available author identity;
configuration alone does not establish copyright ownership, DCO agreement or
sign-off. Do not manufacture a Signed-off-by or other attestation.

## Helper dependency closure

`feature-contrib-build-manifest.json` records normal contrib FFmpeg9 source build
and static pkg-config closure. Its very large `config` and host-specific flags
are local receipts, not public guide material. Normal recipes and checksum files
in upstream `contrib/src/` make sources available without private archive surgery.

| Linked component | Source/license evidence inspected | Qualification |
|---|---|---|
| FFmpeg9.0: avformat, avcodec, avutil, swscale | `contrib/src/ffmpeg/rules.mak`, `SHA512SUMS`; extracted `ffmpeg/LICENSE.md`, `COPYING.LGPLv2.1`, `libavformat/matroskadec.c`; archive checksum in `feature-contrib-source-archives.json` | LGPL2.1-or-later selected configuration; `!CONFIG_GPL=yes`, `!CONFIG_NONFREE=yes`, `!CONFIG_VERSION3=yes` in generated config.mak denote disabled options. Normal source-built patched libraries recorded; no private member replacement. |
| GSM1.0-pl22 | Existing contrib recipe/checksum; extracted `gsm/COPYRIGHT` | Permissive notice-preservation license, Jutta Degener/Carsten Bormann. Source archive receipt exists. |
| LAME3.100 | Existing contrib recipe/checksum; extracted `lame/LICENSE`, `COPYING` | Library GPL/LGPLv2 terms; source archive receipt exists. Selected normal recipe enables libmp3lame. |
| OpenJPEG2.5.4 | Existing contrib recipe/checksum; extracted `openjpeg/LICENSE` | BSD2-clause notices; source archive receipt exists. Do not claim unused thirdparty directories are linked merely because they are in the archive. |
| zlib1.3.2 | Existing `contrib/src/zlib/rules.mak`, `SHA512SUMS`; installed `include/zlib.h` notice and `lib/pkgconfig/zlib.pc` version/license; `libz.a` hash in manifest | Public source availability is established by recipe. Extracted zlib source/build tree and a zlib archive acquisition receipt are absent from this feature manifest's four-tarball receipt. Do not describe the entire linked closure as independently rebuilt from source. Retained official prebuilt acquisition has its separate baseline receipt. |
| Apple frameworks/system tools | Static flags list AudioToolbox, VideoToolbox, CoreFoundation, CoreMedia, CoreVideo, CoreServices, pthread/libm; source uses Mach/CommonCrypto | Use documented Xcode/macOS SDK prerequisites. These are system platform dependencies, not libraries to copy into the source patch. |

FFmpeg's [official legal guidance](https://ffmpeg.org/legal.html) distinguishes
LGPL default code from optional GPL/nonfree configuration and corresponding-source
obligations. This source contribution should carry the existing contrib recipe
and precise patch; it need not ship compiled tools or media. Any future binary
distribution would need an additional exact dependency/source/notice compliance
review. No binary distribution is authorized here. VideoLAN legal-page fetch
returned HTTP418 during this check; pinned source notices and existing scout
evidence remain the license evidence. Compatibility here is a source-license
inventory, not a patent opinion or comprehensive legal certification.

## Portable test inputs and material gaps

Candidate `bin/timeline-preview/test.py` accepts `--fixtures`, `--trim-fixtures`
and `--identity-fixtures`. The candidate currently has no fixture generator or
fixture generation/test guide. Its `Makefile.am` registers only the basic
helper-only checks; fixture matrices are optional caller-driven checks. Thus
passing that make target does not mean identity/PTS/rotation/trim regressions ran.

Suitable existing sources to copy/adapt, rather than publishing local runners:

- `tests/story-005/generate_fixtures.py`: Python3.8+ stdlib plus FFmpeg/ffprobe;
  FFmpeg needs lavfi testsrc2/color/sine, libx264, ALAC, PNG, framehash and fps_mode.
  No network, fonts or imported assets. Explicit output/tool arguments work
  standalone; replace the wrapper-specific default `work/story005-fixtures` in
  a public guide with an explicit scratch destination. `FIXTURES.md` documents
  mathematical-source provenance, bounds and oracle limitations.
- `tests/story-005/mp4_generate_fixtures.py`: stdlib plus FFmpeg/ffprobe;
  explicit fresh output required; testsrc2 and synthetic edit-list/CTTS controls.
  Include the exact subset consumed by helper tests, preserving generation and
  hashes rather than importing the rejected MP4 playback patch.
- `tests/story-005/feature_dependency_fixtures.py`: stdlib plus FFmpeg/libx264;
  writes known TrackNumbers and malformed identity controls using synthetic
  color streams. No mkvmerge dependency or imported assets.
- `tests/story-005/feature_dependency_probe.c` and
  `feature_dependency_run.py`: direct libavformat ID/selectors/packet comparison,
  including baseline parity. Provide standard compiler/pkg-config commands and
  explicit baseline/candidate executables. Do not import private build runners.

The helper contrib configuration disables filters and does not enable libx264;
it cannot generate this fixture set itself. A separate externally installed
FFmpeg CLI with these features is an explicit test-only requirement, available
to upstream maintainers but not supplied by the normal helper dependency build.
Record the tested CLI version/configuration and generated manifest hashes.
Generating and decoding with FFmpeg does not independently certify FFmpeg;
direct VLC behavior and visual/time correspondence remain separate gates.

## Minimal self-contained public layout

Proposed layout, owned by root/builders rather than created by this review:

```text
contrib/src/ffmpeg/matroska-track-number.patch
contrib/src/ffmpeg/rules.mak                 # patch application through normal contrib
bin/timeline-preview/
  timeline-preview.c  PROTOCOL.md  Makefile.am  test.py
  README.md                                # motivation/build/tests/limits/attribution
  fixtures/
    generate.py  generate-mp4.py  generate-matroska.py
    README.md                              # tools, fresh-output recipes, oracle/bounds
  tests/
    avformat-identity.c  compare-identity.py # or separate FFmpeg regression package
modules/gui/macosx/timeline/                 # product classes + isolated context seam
modules/gui/macosx/tests/                    # registered XCTest + fault helper
```

Register generator/guide/direct-test files in `EXTRA_DIST` and applicable Meson
distribution/build definitions. The final guide should give upstream build
commands, exact enabled options, helper-only and fixture test commands, native
XCTest commands and prospective native/control/playback protocols, plus measured
results/limits. It must not depend on this wrapper's methodology or diaries.
Keep FFmpeg regression ownership distinct if reviewers require a prerequisite
FFmpeg contribution. Root owns final patch splits; this layout is an inventory
recommendation, not a new architecture decision.

## Public exclusions and exact-diff review

Exclude wrapper `.agents/`, methodology docs/state/generated graphs, all ignored
`work/` sources/build outputs/apps/binaries, NAS/private-media evidence, raw
logs and manifests containing `/Users/cam`, `/Volumes`, network addresses or
private media names. Do not copy `helper9_{build,cases,private_avformat,score}.py`,
native-baseline orchestration or prototype preparser/process/MP4 experiments into
the product package. Preserve those as local evidence. Never include experimental
core patches0001–0004 as hidden prerequisites of the retained-helper feature.

At this snapshot, 42 modified/untracked candidate files were scanned as complete
text for `/Users/`, `/Volumes/`, `smb://`, `192.168.`, `10.0.`, `work/story`,
`VLC_THUMBNAIL_TRACE`, and `thumbnail-events`: no matches. This bounded scan does
not establish that every personal identifier/secret or unrelated source change
is absent. Final review must include tracked diff plus every untracked deliverable,
XIB/localization metadata, source headers and build/dist lists. Existing
`bin/preparser/Makefile.am` change replaces conditional assignment with `+=`;
root/build owner should retain only if required to compose the new helper target.

Python AST syntax parsing passed for the three generators, dependency runner and
candidate helper test. No fixture regeneration/build/native proof was run by
this read-only lane. Existing feature/native verification receipts remain the
responsibility of their owners.

## Frozen file receipts for this inventory

| File | SHA256 |
|---|---|
| candidate `bin/timeline-preview/timeline-preview.c` | `8b6dbe3a28c45bab10d3286e28f119aff79687121fa2ed04ffe25c6a97ce8a82` |
| candidate `bin/timeline-preview/test.py` | `199d1d30e7f72d17dec2699a627ed194b7ff83e315b263cf4370b29b048d580b` |
| candidate `bin/timeline-preview/PROTOCOL.md` | `97a9fd6748a8c58ef7db513731a42b96af41f4311cb857e185f17fcbb68c470d` |
| candidate FFmpeg TrackNumber patch | `23baeb78b81fcb51e5068feaba2ad6f8ddfedfc3eb7dd5bca3b7d56df5ce2602` |
| wrapper `generate_fixtures.py` | `154d820ef129f869b1cf60b653ea39376b04b3f4819a0af8e7bab76100dd7b89` |
| wrapper `mp4_generate_fixtures.py` | `f4fb0a7d5dc5405d6b6cd311abb3156cfa16e1b647ed65d416af6732d5273067` |
| wrapper `feature_dependency_fixtures.py` | `fe7266629643bf841c6780c903f248f922dcfb769a24e462e6e4f6517555ad49` |
| wrapper `feature_dependency_probe.c` | `c2d8128e24ee35f3b5ed40325f7b46d0ed69ed6417af23ed2dca06b16684723e` |
| wrapper `feature_dependency_run.py` | `bfe99307ef3e8ea119652a0b18d1c5cc052bd042d46725af13f7abd4eac6db4d` |

Open actions before public readiness: portable fixture/test guide and dist inputs;
truthful authorship/retained-source attribution; separate reviewable dependency
patch/regressions; accurately scoped dependency rebuild provenance; final complete
public diff review; clean independent reproduction; native gates and platform
coverage/limitations from their owners.


### Attribution addendum — 2026-10-06 resumed authorization

The unresolved-human-credit language above records the earlier review snapshot.
Cam subsequently approved contributor credit, AI-assistance disclosure and an
open-source contribution under existing VLC GPL/LGPL terms. Contributor/contact
identity is taken from current Git configuration: Cam Marsollier
<cam.marsollier@gmail.com>. Existing third-party notices and collective contributor
source notices remain. This does not assert sole copyright ownership, assignment,
waiver or Signed-off-by. No mandatory source-header rewrite was identified; any
maintainer request for holder precision remains a review question. Wrapper metadata
now expresses this distinction and passes an independent59-source/9-artifact hash
and privacy/link/identity check. Manifest SHA256 after that metadata-only update:
`6eb4c9a5ee0ec6c0238592a86a2ea3570868d47be1c27079f6a3f85b715ac987`.
Source tree and all four patches remain unchanged. Native/performance acceptance
and actual demonstration packaging remain open; nothing has been submitted.
