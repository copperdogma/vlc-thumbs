# Pinned upstream macOS baseline reproduction

Qualified local substrate: unchanged VLC master
`2e358f3098c2f2b7621d1dc568de8b61ad786322`, arm64 macOS27/Xcode27 SDK27,
clang21.0.0. Official app build passed; native GUI proof is a separate boundary.
Full receipts and app hashes: `baseline-build-manifest.json`.

## Exact prerequisites and dependency choice

- Native Python3.14.3 at `/opt/homebrew/opt/python@3.14/bin/python3.14`.
- Host pkgconf2.5.1 at `/usr/local/bin/pkg-config`; matching pkg.m4 under
  `/usr/local/share/aclocal`, checksum in bootstrap diagnosis. This host tool is
  Intel/Rosetta; actual compiler/output architecture is arm64.
- Xcode clang/make/SDK and Apple Metal Toolchain27A266a, installed through the
  documented `xcodebuild -downloadComponent MetalToolchain` prerequisite.
- Upstream tools bootstrap/build chooses its pinned packages. M4/gettext mirror
  repairs retain exact versions and pass upstream SHA512SUMS. See download
  decision and verification receipts; no product-source patch was applied.
- Exact official prebuilt contrib archive uses CI19 triplet and recipe revision
  `15b71e3fa6d49ed2845dfb1324760984eae6101c`. Derive it with
  `extras/ci/get-contrib-sha.sh macos-arm64` in sufficient source history;
  a one-commit shallow clone gives a misleading key. Recorded200-commit deepening
  sufficed locally without changing HEAD. This is official prebuilt dependency
  reproduction, not a completed source-contrib rebuild.

## Official build command and environment

From the project root, with a pinned isolated upstream source and new owned output:

```bash
vlc_task_source="$PWD/work/upstream/vlc-master-story005"
vlc_task_output="$PWD/work/story005-master-baseline"
export VLC_PATH="/opt/homebrew/opt/python@3.14/bin:/usr/local/bin"
export ACLOCAL_PATH=/usr/local/share/aclocal
export PKG_CONFIG_PATH=
export PKG_CONFIG_LIBDIR=/nonexistent/story005-pkgconfig-isolation
export VLC_FORCE_KERNELVERSION=19
export VLC_PREBUILT_CONTRIBS_URL=https://artifacts.videolan.org/vlc/macos-arm64/vlc-contrib-aarch64-apple-darwin19-15b71e3fa6d49ed2845dfb1324760984eae6101c.tar.zst
export NCURSES_LIBS="-L$vlc_task_output/contrib/aarch64-apple-darwin19/lib -lncursesw"
bash "$vlc_task_source/extras/package/macosx/build.sh" \
  -a aarch64 -x -j 4 -C "$vlc_task_output"
```

ACLOCAL_PATH exposes third-party pkg-config macros while owned-I macro paths keep
priority. NCURSES_LIBS is a documented configure override removing an absent
SDK26.2 path embedded by the prebuilt artifact; ncurses remains enabled. The
artifact's chromaprint.pc also retains an SDK26.2 framework-search path, but did
not fail this build. No source or contrib metadata was edited.

If repairing an already failed bootstrap, run the official `bootstrap` explicitly
with owned tools first in PATH and that ACLOCAL_PATH; partial generated configure
otherwise makes build.sh skip bootstrap. If changing configure environment in an
existing build, preserve/rename the owned generated output Makefile so official
build.sh regenerates it. Exact attempts are retained, including interruptions.

The disposable monitor in `work/story005-scout/baseline-build-monitor.py` records
commands/pin/input hashes/elapsed time/minimum free space. It stops the build
process group below1GiB free and never deletes anything. Do not reuse the old
Story001 monitor, which targets preserved work/build.

## Pinned upstream CI checks

After successful app build, explicitly export SDKROOT for direct compiler calls:

```bash
export PATH="$vlc_task_source/extras/tools/build/bin:$VLC_PATH:/usr/bin:/bin:/usr/sbin:/sbin"
export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
export VLC_TEST_TIMEOUT=60
make -C "$vlc_task_output" -j4 check TESTS=
make -C "$vlc_task_output/modules" -j4 check-macosx
```

Results: check targets compile successfully (`TESTS=` executes zero tests), then
macOS XCTest executes253tests with0failures. Deep/strict app signature verification
passes. Dynamic dependencies inspected for395app Mach-O paths contain no
absolute user/Homebrew/library references. This does not establish redistribution
compliance, older-OS support, Intel local execution, preview correctness, native
control behavior or playback performance.

Candidate builds use their own source/output/extracted contrib prefix/object files;
the unchanged baseline tools can be prefixed to VLC_PATH and the exact archive
copied into the new output for independent official extraction. Candidate receipts
add diff hashes and every approved product/test input, including untracked test.
