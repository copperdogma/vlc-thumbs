# Story 001 — source and host preflight, 2026-10-03

Setup checked in as `fdf25f274ed98ff2706226b4bdd1aa42c08590b5` on local main.
Remote is absent; push awaits user destination. Story work starts on
`codex/story-001-feasibility`. No product implementation patch made.

## Source acquisition and identity

Commands executed:

```sh
git ls-remote https://code.videolan.org/videolan/vlc.git refs/heads/3.0.x refs/tags/3.0.24 'refs/tags/3.0.24^{}'
git clone --depth 1 --branch 3.0.24 https://code.videolan.org/videolan/vlc.git work/upstream/vlc-3.0.24
git -C work/upstream/vlc-3.0.24 rev-parse HEAD
git -C work/upstream/vlc-3.0.24 status --porcelain
```

Clone succeeds, HEAD `6de05adcbaf2e8b85fe86aad4169393098628119`, pristine status.
[Official release directory](https://download.videolan.org/pub/videolan/vlc/3.0.24/)
contains the matching source release. Inspected file hashes in source-manifest.json.
The source checkout is ignored; no upstream source is staged for this project.

## Host observed

- arm64; macOS 27.0 build 26A428.
- Xcode selected at `/Applications/Xcode.app/Contents/Developer`.
- Apple clang 21.0.0, clang-2100.3.34.2; SDK 27.0.
- Python 3.14.3; CMake 4.0.1; Ninja 1.12.1; pkg-config 2.5.1.
- Git, clang, make, CMake, Ninja, pkg-config, FFmpeg and gh found.
- autoconf/automake/meson not found in current PATH. The upstream macOS script
  has a separate tools-bootstrap stage, so this alone does not prove a blocker.

Command executed:

```sh
bash work/upstream/vlc-3.0.24/extras/package/macosx/build.sh -h
```

Help prints supported arch/build-directory/contrib options and exits 1 by its
explicit help branch. This is CLI inspection, not a failed compile. No build,
configure, dependency install or VLC launch has run. SDK/tool compatibility and
prebuilt contrib availability remain unqualified.

## Source obligations observed

The inspected native slider files carry GPL version 2-or-later notices. The
LibVLC public header carries an LGPL notice; upstream provides COPYING and
COPYING.LIB. Preserve relevant notices when modifying/copying code. This is an
inventory of source notices, not a completed redistribution/dependency-license
audit. There is no distribution artifact or licensing decision in this pass.

## Retrieval caveats

Web fetch of the main source-download page returned HTTP 418; the wiki macOS
compile page timed out. Official Git transport and the official release listing
worked. Build guidance therefore comes from the pinned upstream build.sh rather
than an assumed accessible wiki. Development branch comparison was checked by
`git ls-remote ... refs/heads/master` at SHA
`da266629fdffc4bee4560d9c818efd16217efeda`; it is a different version/architecture.
