# Master feature build reproduction — current evidence

Base `2e358f3098c2f2b7621d1dc568de8b61ad786322`; feature sources are uncommitted and independently owned. Prototype0001/0002rev3/0003 were exactly reversed from the candidate before feature work; experimental0004 was already absent. Final prototype source/patch/core/lib/helper/plugin/test receipts are preserved under ignored `work/story005-scout/prototype-final-preserved`; historical prototype apps remain APFS clones. Baseline source/app and installed preview are unchanged. Candidate output is reused for storage; it is not a second pristine master build.

## Latest completed package and remaining gates

The official existing-output feature app build042325Z passes152.4s and ad-hoc signature validation, maintaining1GiB reserve (minimum1258991616bytes). Actual native timeline/context/service/UI production files compile; this is not physical interaction proof. `feature-original-app-manifest.json` records997 original package file hashes/symlinks, original plist, system/bundle-only selected dynamic linkage and identical helper TEXT sections before/after signing. The packaged helper directly decodes two actual MP4/MKV frames from `/private/tmp` with only system PATH (corrected smoke042732Z); harness-only first-attempt type-field failure042712Z remains preserved.

Normal H1 local matrix passes77checks,32framepixel/time parity matches, and actual customAVIO1200packet parity plus size/restore/read failures pass; see `helper-flat-normal-provenance.json` and `helper-flat-custom-io-runtime.json`. Conservative admitted format scope and untested cold/stalled/larger-layout cases remain separate. The final registered actual-slider hover target042037Z passes6methods; context7 and cache/service-edge5 normal focused runs remain qualified. A final once-only integrated native suite is now justified after repaired original failures, but has not launched because current availability again falls below reserve. No unnecessary complete suite repetition occurred.

Final distribution-only addition registers the public admission generator (SHA92be89ff835bfdb8eaddac8cef634e2a9d58aa69b750d035b1979db563add3a4) in EXTRA_DIST; bin/timeline-preview/Makefile.am SHA b8127423a839e158c689327916f6abe9976738ae9025c39e5f63928390a50b4d. This post-package list change does not alter app code. Source package owner has been notified of the final list/source freeze. Full distcheck, independent clean checkout/patch-only build, actual bundle move, native candidate identity isolation, physical pointer/playback/accessibility and olderOS/Intel gates remain explicit.

`feature-build-space-plan.md` records measured footprints and concrete start thresholds:1.5GiB for the final native suite,3.5GiB for helper-disabled minimal distcheck,5GiB for independent clean patched-FFmpeg/official-prebuilt-other-input app reproduction. Full all-contrib source reproduction is a distinct unmeasured stronger gate, provisionally8GiB. No cleanup, metadata mutation, relocation or further runtime is authorized while below1GiB.

## Conventional dependency and helper build

The source patch is `contrib/src/ffmpeg/matroska-track-number.patch`, selected through normal `contrib/src/ffmpeg/rules.mak` APPLY and an explicit patch prerequisite. No private archive/member substitution is used. The exact9.0 source and normal GSM/LAME/OpenJPEG dependencies were copied from prior official-download caches and independently checked against pinned SHA512SUMS (`feature-contrib-source-archives.json`). The targeted source build uses the same selected contrib prefix as the app.

From a configured macOS source/contrib build directory, the actual normal target is:

```sh
# Environment follows extras/package/macosx/env.build.sh:
# native host architecture, SDK, vlcSetSymbolEnvironment and
# vlcSetContribEnvironment "$MINIMAL_OSX_VERSION".
make -C build/contrib/contrib-aarch64-apple-darwin19 -j4 .ffmpeg
```

Actual local driver `work/story005-scout/build-feature-contrib.sh` sources the pinned official script in its documented `none` mode, then explicitly invokes its base/symbol/contrib setup. It isolates pkg-config to the selected prefix, uses native SDK27/arm64 and4jobs, and invokes ordinary `.ffmpeg`. Receipt `candidate-build-20261006T032530Z.json` succeeds116.3s; the initial driver-mode error is preserved at032509Z. This is source reproduction of FFmpeg plus its declared dependencies on top of existing exact prebuilt contrib for the remaining packages, not a claimed all-contrib clean build.

For a new source-only public build, the upstream entry point is:

```sh
extras/package/macosx/build.sh -a aarch64 -c -x -j4 -C build
```

This command expresses the normal complete-source recipe but has not been executed for every remaining dependency here. Do not substitute the old unmodified prebuilt FFmpeg and infer the metadata patch is present. Full clean public reproduction remains a gate.

The helper is an ordinary macOS-desktop installed `pkglibexec_PROGRAMS` target, `vlc-timeline-preview`, with an equivalent gated Meson executable. Configure uses checked static pkg-config dependencies on avformat63.1.100/avcodec63.1.100/avutil61.1.100/swscale10.1.100; normal Automake flags provide target compiler/architecture. The helper has no VLC-core link dependency. `bin/timeline-preview/test.py --helper BUILT_TARGET` is registered as `make -C bin check-timeline-preview` and a Meson test, with optional generated fixtures for broader checks. Current basic checks require Python3.9 or newer; helper runtime requires no Python/PATH executable lookup.

Actual official bootstrap/configure + helper target/check recipe is captured by032941Z. The first bootstrap exposed conditional `pkglibexec_PROGRAMS +=` use without a definition for every build condition (032904Z). Build-list normalization initializes the variable once and appends cache/preparser/helper targets; no player/core behavior changes. Thirteen registered basic checks pass. `feature-helper-build-manifest.json` records helperSHA2566d90de5bded764f4471d7c70db86fe62da1df72685493d7e93720ab418880483,20,235,368bytes,arm64,minOS11.0,SDK27.0 and system-only dynamic references. Full normal helper focused checks separately pass39 (`helper-protocol4-normal-*.json`). H1 ordered-edition admission remains pending and is not qualified by those checks.

## Runtime and native targets

Clean-pin core/lib/preparser/serializer were incrementally rebuilt to remove prototype ABIs. Merged FFmpeg configuration is enabled, so forced `avformat` resides in `libavcodec_plugin.dylib`. Existing generated avcodec/swscale `.la` link targets and dylibs were preserved under `work/story005-scout/pre-feature-plugin-relink`; their generated link targets were then invalidated for a normal relink against new archives. `feature-runtime-build-manifest.json` captures coherent libraries, helper and plugins (033221Z). Neither source reset nor broad cleanup was used.

Native production timeline files are registered in `modules/gui/macosx/Makefile.am`. Service/cache/scheduler/hover tests plus portable C fault helper are registered in the existing native XCTest bundle. Context uses an isolated focused bundle with injected class stubs, avoiding collisions with real service objects; its build rpaths point to the owned candidate core. The test fixture target is `modules/vlc-thumbnail-test-helper`, injected through `VLC_MACOSX_TEST_HELPER_PATH`, not a Python/runtime-PATH dependency. Meson does not currently build the full native macOS GUI upstream (`meson_options.txt` lists that TODO); the new helper Meson target is not a claim of full GUI Meson support.

Registered native first pass033257Z executes262 methods: original253 plus cache1/scheduler1/service3/hover4. It catches3 cache malformed-header scalar exceptions; all other methods pass. Cache owner repairs raw `video_count` type validation before integer conversion. A narrowed normal cache rerun033616Z passes1 method/0 failures16s; the failed attempt is preserved. Context initial normal target033512Z passes6 methods; final reviewed reentrancy target034218Z passes7 methods. Final narrowed cache and four service-edge methods034344Z pass5 methods/0 failures (17.827s), including bounded partial writes and channel-overflow rejection. Do not aggregate these as an unchanged full-suite clean result. Official full-app attempt033704Z was cancelled cleanly before new timeline/UI source compilation; its source-freeze hold/cancellation receipt is retained. New actual-slider focused target is registered but its normal run remains pending. H1 remains pending.

## Scope, warnings and guard

- Native host is macOS27/Xcode27/SDK27 arm64. Normal helper object floor is11.0. Official environment nominal minimum is10.13; arm64 clamps to11.0. Existing clean-pin ObjC core objects `dirs`/`netconf` retain minOS27 warnings when linked at11.0. Generated `OBJC` lacks the deployment/sysroot suffix that generated `CC` has. This is recorded as olderOS unqualified, not fixed by changing upstream core/build semantics in this lane. Intel, olderOS execution and clean cross-matrix CI are unqualified.
- Fresh FFmpeg configuration reports CONFIG_GPL=0,CONFIG_GPLV3=0,CONFIG_NONFREE=0. The helper is GPL-2.0-or-later; static closure includes GSM/LAME/OpenJPEG/zlib and Apple frameworks. Exact source/configuration/patch/dependency inventories and corresponding-source obligations remain required before distributing binaries; default contrib recipe license selection alone is insufficient.
- Warnings include legacy dependency Autoconf macros, SDK/deployment issues above, clang limited-range argument and helper double-to-int cast warnings. Failed driver/bootstrap/test logs are retained. No concealed source-version substitution or repeated blind build attempts.
- Owned build monitor enforces1GiB free reserve, stops its process tree/groups on reserve failure, and bounds XCTest attempts at180s. Child builds/tests use a small environment whitelist plus explicit recipe overrides to avoid inherited credential dumps. Original projects/apps, baseline and installed preview are not cleanup targets.
- Dependency lane proofs cover direct ID selectors/packet parity and actual forced-avformat captures. DOVI stream-group execution, Matroska ordered editions/linked segments, native four-surface interaction, reader/pointer, preferences/context races, NAS/freshness and20-control/three active-playback pairs remain their explicit gates. App compile/signature success cannot establish those behaviors or package/readiness claims.

## Configuration review repairs and current hold

B1/B2/B3 approved source fixes are captured in `feature-build-review-repair-receipt.json`: Meson static dependencies receive the original feature option as `required` and all `.found()` results gate the helper, preserving the `auto` default; minimal `distcheck` explicitly disables the helper; explicit Autoconf helper enable plus disabled VLC errors consistently; tests report a clear Python3.9 prerequisite. Public maintainer/fixture/dependency-probe inputs are distributed normally. No current Meson installation is available, and its option matrix has not been executed. Generated Autotools checks will be rerun after storage clearance; a lean helper-disabled distcheck would not replace feature-enabled proof.

The H1 parser-owned flat-timeline patch is selected conventionally after TrackNumber via `rules.mak`, with an explicit prerequisite. Current patch SHA256 is `abd605f770de85f739929c5d333bd45e8d35075b2b69720cfaecbdc0d278450e`; prior normal FFmpeg/helper results predate H1 and do not qualify the new mapping. Build work is paused at the parent-directed storage hold, with a1GiB absolute reserve. `feature-owned-storage-reclaim-proposal.json` records exact duplicate archive/staging candidates; no deletion is authorized or performed by that proposal.

H1 normal source-contrib rebuild035202Z succeeds104.3s with minimumfree1680285696bytes; normal helper bootstrap/configure/rebuild035359Z succeeds46.2s and13basicchecks. Exact receipts are `feature-h1-contrib-build-manifest.json` and `feature-h1-helper-build-manifest.json`; helper SHA256 `b2b5e5d13bf6d3e92f9e23193ec516d86b1f54547783fb5c53ce2fbbf6dadf73`. These establish conventional build integration, not H1 admission/I/O/playback behavior. Subsequent focusedhover build preflight refuses when external disk availability drops to785128KiB, below1GiB; no test subprocess launches. `feature-build-disk-preflight-stop.json` preserves this hold.
