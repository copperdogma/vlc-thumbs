# VLC macOS development build

Qualified local result: VLC 3.0.24 commit
`6de05adcbaf2e8b85fe86aad4169393098628119`, arm64, Xcode 27/SDK 27 on macOS 27.
Attempt 009 completed after recorded compatibility repairs. It played a generated
silent MPEG-4 fixture in the native UI; pause and click-to-seek worked. This is
a development baseline, not feature completion or release qualification.

## Workspace and prerequisites

Pristine pinned source: `work/upstream/vlc-3.0.24`. All mutable source/tools,
contribs and output live in ignored `work/build/`. Never build in the pristine
checkout or replace /Applications/VLC.app. Current successful footprint is about
5.7 GiB including intermediate files; VLC.app is 161 MiB. A universal 30 GiB
requirement was never established. Monitor actual free space during retries.

Host tools used: Xcode clang/make/SDK; /usr/local pkg-config and its pkg.m4,
GNU shell utilities; native /usr/bin/python3 3.9.6. Intel build tools may run
through Rosetta, but native Python is required for honest Meson CPU detection.
Exclude Intel /usr/local libraries from dependency discovery.

## Reproduce repairs on a fresh disposable source copy

Run from the project root. These commands describe the working route; a clean
rebuild has not been rerun. Follow the disk guard below during expensive commands.

```sh
vlc_task_root="$PWD"
vlc_task_source="$vlc_task_root/work/build/vlc-source"
vlc_task_output="$vlc_task_root/work/build/vlc-arm64"
git clone --shared "$vlc_task_root/work/upstream/vlc-3.0.24" "$vlc_task_source"
git -C "$vlc_task_source" apply "$vlc_task_root/docs/evidence/story-001/build-attempt-008/contrib-isolation.patch"
mkdir -p "$vlc_task_source/extras/tools/build/bin"
ln -sf /usr/bin/python3 "$vlc_task_source/extras/tools/build/bin/python3"
export PATH="$vlc_task_source/extras/tools/build/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd "$vlc_task_source/extras/tools"
./bootstrap
make -j4
cd "$vlc_task_root"
```

After tools finish, move `extras/tools/build/bin/ninja` to `ninja.real` and
place this executable wrapper at the original Ninja path. Do this only once;
retain the real executable. Explicit jobs disable Ninja 1.13's jobserver client,
which caused pipe errors with Apple's GNU Make 3.81.

```sh
#!/bin/sh
exec "$(dirname "$0")/ninja.real" -j4 "$@"
```

Build with these exact environment settings and options:

```sh
export VLC_PATH=/usr/local/bin
export PKG_CONFIG_LIBDIR="$vlc_task_source/contrib/aarch64-apple-darwin27/lib/pkgconfig"
export PKG_CONFIG_PATH=
export ACLOCAL_PATH=/usr/local/share/aclocal
export VLC_CONFIGURE_ARGS=--disable-sparkle
bash "$vlc_task_source/extras/package/macosx/build.sh" -a aarch64 -c -j 4 -C "$vlc_task_output"
```

The triplet above is this measured macOS host, not a substitute for another
host's triplet. `-c` builds libraries from source; it avoids the missing default
prebuilt archive. Sparkle auto-update is disabled. The script's old deployment
minimum produces libc++ warnings; this build is qualified only on the current
host. Modern minimum/older-OS support requires a separate build decision.

For an existing repaired workspace, run only the build command with these
settings. If dependency .pc files change, remove only generated
`work/build/vlc-arm64/Makefile` before rerunning to force VLC configure. Do not
wipe compiled objects unnecessarily. Architecture repairs must also invalidate
affected contrib stamps and installed .a/.pc files (attempt 006 manifest;
FreeType's stamp is `.freetype2`, not `.freetype`).

## Disk guard used in recorded attempts

Every two seconds, sample project-volume free space. Every 30 seconds, record
workspace size, elapsed time and minimum sampled free space. Stop the build's
process group below 1 GiB free. On that stop, terminate descendants before
removing only the owned disposable `work/build/`; keep pristine source and
logs. Ordinary errors retain artifacts for incremental retries. Exact monitor
used in the final attempt: `docs/evidence/story-001/build-attempt-009/disk-monitored-build.py`.
It writes the attempt 009 evidence paths; create a new evidence directory/change
those paths for a new attempt rather than overwriting previous evidence.

## Isolated launch and evidence

Output: `work/build/vlc-arm64/VLC.app`. Before GUI launch, change only its generated
Info.plist CFBundleIdentifier to `org.videolan.vlc-thumbs.development` and its
CFBundleName/DisplayName to `VLC Timeline Development`. Core darwin directory
selection and NSUserDefaults then use this separate domain. Set development-only
VLCFirstRun=true and VLCPreferencesVersion=4 to skip the early metadata modal.
Disable metadata-network-access, recent-items, media-key handling and control of
other media players; use an explicit ignored config path. Exact GUI command is
in attempt 009/gui-smoke.json. Do not use real videos or real annotation stores.

After plist changes, ad hoc sign the whole app deeply. Regenerate plugins.dat
with build `bin/vlc-cache-gen` against the app's Contents/MacOS/plugins; sign
plugins.dat, then re-sign only the outer app and verify deeply/strictly. Deep
signing plugins again after cache generation changes mtimes and stales the cache.
A subsequent `make VLC.app` can restore upstream identifier/settings, so repeat
isolation before GUI use. Do not use the development build as a file association.

Evidence: attempt 009 README, verification.json, version output, source-download
hashes, native GUI screenshots and accessibility observations. Audio/fullscreen,
other formats, thumbnail/annotation behavior and packaging are unqualified.

## Incremental feature candidate (Stories 002 and 004)

Requires the already qualified arm64 baseline/tools/contrib workspace. Stop only
the development app before replacing its binaries. These commands validate owned
paths/source pin and do not download dependencies or touch installed VLC.

```bash
python3 scripts/apply-vlc-patches.py --check
python3 scripts/build-timeline-app.py --check
python3 scripts/build-timeline-app.py
bash tests/story-004/test-service.sh
bash tests/story-004/test-cache.sh
bash tests/story-004/test-scheduler.sh
python3 tests/story-004/helper_worker_contract.py
python3 tests/story-004/track_count_contract.py
```

The feature minimum is macOS 11 for current arm64 scope. The runner builds the
macOS module and helper, copies them into the isolated bundle, deep-signs modules,
regenerates the plugin cache, signs the cache and then signs the outer app without
re-signing modules again. Exact commands/hashes/manifests go to ignored
work/validation/story002. Existing toolchain repairs belong to baseline provenance;
the feature patch includes only native GUI seams. App/helper compilation alone
is not native hover, playback or fullscreen validation.

Story 002's old one-shot service/cache-fault runners are explicitly retired with an actionable exit rather than compiling against incompatible persistent-v3 service APIs. Their old source/latency/physical ENOSPC evidence remains historical. Current protocol parity and service/cache contracts own changed-code proof; actual native hover and playback remain separate. See `tests/story-004/README.md`.
