# macOS timeline contribution and baseline readiness repairs

**Prepared for maintainer review; submission checklist incomplete; no submission; current native qualification partial.** This review package has two review components:
[hover previews](feature-series/README.md) and [baseline prerequisites](blocker-prerequisites/README.md).
The intended feature remains 59 source paths/five patches. Seven separate prerequisite
units add 13 paths and overlay 5 feature paths, producing 72 unique combined paths.
The source review burden is 568,295 patch bytes (+10,849/−118): 520,977 bytes
for the feature (+10,134/−58) and 47,318 for prerequisites (+715/−60), including
tests and source documentation. Canonical application order is in [contribution-series](contribution-series):
five feature patches followed by seven prerequisites. Apply each from the pinned
VLC source root with ordinary git apply; do not apply the same patch twice.

Upstream base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Feature 12 tree: `94a7f24d29860562783da076bdb512d39756c41f`.
Combined source tree: `4ff4b5bc0ec361272b7ad0138d5e67512b952af9`.
The [aggregate manifest](contribution-manifest.json) pins exact components, patch
order, intermediate trees and all 72 source modes/blobs/hashes. Independent cached
application equals a separately constructed complete source snapshot. This is
source correspondence, not whole-build or user-facing qualification.

Feature 12 changes only three foundation files in part 0003: scheduler covered-state
reconciliation and existing scheduler/service regression coverage/synchronization.
The other four feature patches retain revision 11 bytes. Prerequisites repair
baseline install/distribution/cleanup, clock origin, TLS fixture backend, GL fallback, owned
media-source lifetime and timer teardown. These are separate maintainer concerns;
no agreement on final submission boundaries is asserted. The timer regression
uses a feature-created context test, so its packaged patch depends on the feature.

The exact 72-path freeze passes executed normal 009 complete registered check and
conventional 010 complete distcheck through final distcleancheck. Native tests report 283 pass
and one optional skip among 284 unique cases; lifetime 5/5 and helper-basic 13/13 pass. Normal 94
and archive 93 test cases preserve upstream distribution Lua-disable flags; nested totals
overlap. Full helper 77 was not rerun by 009/010. Actual 010 used a private read-only artifact
preflight forwarding unchanged argv/status to the original driver. The shorter public host
recipe remains **unexecuted**; executed build/archive proof does not establish execution of
that changed route. No public forensic guard is required. Historical failures are retained.

Historical shutdown 004 remains unexplained and user-accepted **DEFERRED**. A bounded
comparison found one unchanged-baseline normal Command-Q SIGSEGV matching the earlier 015
ResizeNotify/logging pattern, distinct from 004's condition-wait pattern. One corresponding
candidate normal Command-Q exited 0 without SIGTERM. This establishes neither 004 causality,
shutdown frequency nor candidate exoneration.

Actual human VoiceOver main Position-to-Pause navigation, stable pause and resumed advancing
video pass narrowly. Spoken/exposed 5.5% disagreed with 38.417 s/7200 s; accurate media position,
precise seek, visible-preview navigation and fullscreen reader remain unqualified. A separate
comparison qualifies ordinary Play and two actual native CUA midpoint actions per arm with
decoded 150 s and >5 s continued video. Both arms exposed stale slider/time labels after actions;
no physical drag, quarter-position or universal accessibility claim follows.

Current main hover and custom-fullscreen 180-second Keyframe hover, actual UI Pause/Resume
and return to the main window are demonstrated. Returned-main hover and normal Quit were
not reached within that roundtrip's deadline; its full roundtrip remains unqualified.
A later bounded trial entered custom fullscreen and returned to the original main window
with strict playing state. Its one native hover route and capture passed, but independent
full-region image review showed the on-bar cursor and advancing 116.042 s/frame 2785 with
no thumbnail or Keyframe caption. Returned-main hover remains unqualified; the cause is
unknown, and this single negative capture does not establish a regression. No retry or
reader trial followed; VoiceOver was never enabled. Root's one Command-Q exited 0 without
SIGTERM and the parent was absent. No matching crash was present in the bounded inventory
(delayed reporting remains possible); no universal descendant-absence claim follows.

Intel/older-macOS/CI execution remain unavailable. These limits are review disclosures;
maintainer acceptance and completion of all native qualification remain separate decisions.

Reproduce current gates using this combined tree and the feature source build
recipe; retain exact full configure flags, tool/contrib/source and binary hashes.
Any owned embedded smoke identity is target-specific build/test metadata, not a
product patch. Nested distcheck executables need their own actual identity proof;
outer identity alone does not qualify them. Keep official tests and assertions.
No app/helper binaries, logs, profiles, private paths or media are included.

The declared artifact inventory includes only this page, contribution manifest/order
and the two named component inventories. Older prototype/experimental artifacts
outside those inventories are excluded. Use an explicit allowlist when exporting.

New baseline part 7 isolates video-window callback lifetime plus compact actual-provider
wiring coverage. Its five focused old-source/fixed cases are source-level evidence only;
current normal 009 and complete 010 pass; historical 004 causality remains deferred. The
canonical 12-patch stack is the qualified application unit; part 7 is not independently
base-build qualified.

## Executed gate commands (sanitized record)

This transcript records executed argv from the normal 009/complete 010 gate plans;
`${...}` replaces only recorded absolute workspace paths. It is evidence of those
runs, not a newly executed recipe. The source freeze SHA256 is
`7cdbe597d18a01b2856e8ba00979e15d63fc8593698d3ca5346ac7437e690ec5`.
The configure script SHA256 was
`a39a19bad7d0931154d15c5c2939f1abec06d57fcab0d4c9aa91eab71ef882d1`.
The ordinary driver SHA256 was
`f5031431dfc824ee2f012950aef35530e5acf3eb412421c8050662b616deaded`.
SDK27.0, arm64, deployment target10.13 and the tool/contrib environment described
below apply. The configured normal build was reused. Normal009 ran:

```bash
make -j8 V=1
make -C "${vlc_build}/bin" -W vlc_osx_static-darwinvlc.o V=1 vlc-osx-static "${normal_identity_override}"
make -j8 check "${normal_identity_override}"
```

Complete010 configured a fresh outer build and ran:

```bash
"${vlc_source}/configure" --enable-macosx --enable-merge-ffmpeg --enable-osx-notifications --enable-flac --enable-theora --enable-shout --enable-ncurses --enable-twolame --enable-libass --enable-macosx-avfoundation --disable-xcb --disable-caca --disable-pulse --disable-vnc --with-macosx-version-min=10.13 --without-x --build=aarch64-apple-darwin19 --host=aarch64-apple-darwin19 --with-macosx-version-min=10.13 --with-macosx-sdk=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX27.0.sdk --enable-extra-checks --with-contrib=${vlc_contrib} --enable-avcodec --enable-avformat --enable-postproc --enable-swscale --enable-timeline-preview
make -j8 distcheck "DISTCHECK_CONFIGURE_FLAGS=--enable-macosx --enable-merge-ffmpeg --enable-osx-notifications --enable-flac --enable-theora --enable-shout --enable-ncurses --enable-twolame --enable-libass --enable-macosx-avfoundation --disable-xcb --disable-caca --disable-pulse --disable-vnc --with-macosx-version-min=10.13 --without-x --build=aarch64-apple-darwin19 --host=aarch64-apple-darwin19 --with-macosx-version-min=10.13 --with-macosx-sdk=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX27.0.sdk --enable-extra-checks --with-contrib=${vlc_contrib} --enable-avcodec --enable-avformat --enable-postproc --enable-swscale --enable-timeline-preview" "${distcheck_identity_override}" 'LOG_DRIVER=python3 ${private_readonly_preflight} $(SHELL) $(top_srcdir)/autotools/test-driver'
```

The two identity overrides retained generated target-only link flags and appended
`-Wl,-sectcreate,__TEXT,__info_plist,${normal_plist}` or `${distcheck_plist}`.
Fresh GUI identities/userdata and archive embedded identity were verified. The private
preflight only inspected artifacts before forwarding the original test-driver's argv
and exit status. It is disclosed here as an executed-run difference and is excluded
from outgoing inputs; substituting the ordinary driver removes that observation and
has not been executed as this shorter recipe. No TESTS/backend/assertion/global-linker
or updater-policy override was used. The public recipe below supplies the host and
identity setup for independent review without that private instrumentation.

## Reproduce the macOS GUI test host

Actual normal 009 and conventional 010 passed on combined tree `4ff4b5bc0ec361272b7ad0138d5e67512b952af9`.
Actual 010 used a private read-only artifact preflight that forwarded unchanged argv/status to the original test-driver.
The shorter public recipe below is newly documented and **unexecuted**; it makes no equivalent-execution claim.
Use the patched source's `bin/timeline-preview/README.md` for ordinary native arm64 tools/contrib/build setup.
Retain that build's exported compiler/SDK/architecture, original LDFLAGS, pkg-config isolation, ncurses, GNU sed and tool PATH.
Actual009/010 used SDK27.0 and deployment target10.13; other toolchains are separate configurations.
Set absolute `vlc_source`, `vlc_build`, `vlc_contrib` and fresh nonexistent `review_dir` paths without spaces or commas.
Use Bash, Python3 and GNU make. HOME stays unchanged; preserve generated profiles and logs after a failure.

```bash
set -e
test ! -e "$review_dir"
mkdir "$review_dir"
while IFS='=' read -r env_name env_value; do
  case "$env_name" in
    DYLD_*|VLC_PLUGIN_PATH|VLC_DATA_PATH|VLC_LIB_PATH|VLC_LIBEXEC_PATH|__CFBundleIdentifier)
      unset "$env_name" ;;
  esac
done < <(env)
prepare_gate() {
  gate=$(mktemp -d "$review_dir/gate.XXXXXXXX")
  python3 - "$vlc_build" "$gate" <<'PY'
import base64, json, os, pathlib, plistlib, sys, uuid
b, g = map(pathlib.Path, sys.argv[1:])
normal = plistlib.loads((b / 'share/macosx/Info.plist').read_bytes())
assert plistlib.loads((b / 'bin/Contents/Info.plist').read_bytes()) == normal
required_keys = (
    'CFBundleVersion', 'CFBundleShortVersionString', 'NSPrincipalClass',
    'NSMainNibFile', 'CFBundleIconFile', 'SUFeedURL', 'SUPublicDSAKeyFile',
)
for k in required_keys:
    assert normal.get(k)
assert normal['SUFeedURL'].startswith('https://') and len(base64.b64decode(normal['SUPublicEDKey'], validate=True)) == 32
r = b / 'bin/Contents/Resources'
icon = normal['CFBundleIconFile']
icon += '' if icon.endswith('.icns') else '.icns'
resources = (
    r / normal['SUPublicDSAKeyFile'],
    r / icon,
    r / 'Base.lproj' / (normal['NSMainNibFile'] + '.nib'),
    r / 'Assets.car',
    b / 'Frameworks/Sparkle.framework/Versions/Current/Sparkle',
)
for p in resources:
    assert p.is_file() and p.stat().st_size
info = dict(normal)
ident = 'org.videolan.vlc.review.' + uuid.uuid4().hex
info.update(
    CFBundleIdentifier=ident, CFBundleName=ident,
    CFBundleDisplayName=ident, CFBundleExecutable='vlc-osx-static',
)
for k in ('CFBundleDocumentTypes', 'CFBundleURLTypes', 'UTExportedTypeDeclarations', 'UTImportedTypeDeclarations'):
    info.pop(k, None)
h = pathlib.Path.home()
paths = [
    h / 'Library/Preferences' / ident,
    h / 'Library/Preferences' / (ident + '.plist'),
    h / 'Library/Caches' / ident,
    h / 'Library/Application Support' / ident,
    h / 'Library/Saved Application State' / (ident + '.savedState'),
    g / 'userdata',
]
assert all((not os.path.lexists(p) for p in paths))
(g / 'namespaces.json').write_text(json.dumps(list(map(str, paths)), indent=2))
(g / 'userdata').mkdir()
(g / 'Info.plist').write_bytes(plistlib.dumps(info))
lines = (b / 'bin/Makefile').read_text().splitlines()
i = next((i for i, x in enumerate(lines) if x.startswith('vlc_osx_static_LDFLAGS =')))
flags = lines[i].partition('=')[2].strip()
while flags.endswith('\\'):
    i += 1
    flags = flags[:-1] + ' ' + lines[i].strip()
assert '$(vlc_osx_LDFLAGS)' in flags and '-static' in flags
assert all((x in flags for x in ('../lib/.libs/', '../src/.libs/', '../Frameworks/')))
(g / 'flags').write_text(flags)
PY
  identity_override="vlc_osx_static_LDFLAGS=$(cat "$gate/flags") -Wl,-sectcreate,__TEXT,__info_plist,$gate/Info.plist"
}
make -C "$vlc_build" -j8 V=1 > "$review_dir/build.log" 2>&1
prepare_gate
make -C "$vlc_build/bin" -W vlc_osx_static-darwinvlc.o V=1 vlc-osx-static "$identity_override" > "$gate/relink.log" 2>&1
# Check embedded identity before the first GUI launch, without launching VLC.
python3 - "$vlc_build/bin/vlc-osx-static" "$gate/Info.plist" <<'PY'
import pathlib, struct, sys
d = pathlib.Path(sys.argv[1]).read_bytes()
assert struct.unpack_from('<I', d)[0] == 4277009103
o = 32
actual = None
for _ in range(struct.unpack_from('<I', d, 16)[0]):
    c, n = struct.unpack_from('<II', d, o)
    if c == 25:
        for i in range(struct.unpack_from('<I', d, o + 64)[0]):
            p = o + 72 + 80 * i
            name, seg, addr, size, pos = struct.unpack_from('<16s16sQQI', d, p)
            if (seg.rstrip(b'\x00'), name.rstrip(b'\x00')) == (b'__TEXT', b'__info_plist'):
                actual = d[pos:pos + size]
    o += n
assert actual == pathlib.Path(sys.argv[2]).read_bytes()
PY
VLC_USERDATA_PATH="$gate/userdata" make -C "$vlc_build" -j8 -W test/run_vlc.sh check "$identity_override" > "$gate/check.log" 2>&1
python3 - "$vlc_build/test/run_vlc.sh.trs" <<'PY'
import pathlib, sys
assert ':test-result: PASS' in pathlib.Path(sys.argv[1]).read_text().splitlines()
PY
prepare_gate                         # fresh distribution identity and userdata
outer="$review_dir/outer"
test ! -e "$outer"
mkdir "$outer"
python3 - "$vlc_build" "$vlc_contrib" > "$gate/configure-flags" <<'PY'
import pathlib, shlex, subprocess, sys
b = pathlib.Path(sys.argv[1])
args = shlex.split(subprocess.check_output([str(b / 'config.status'), '--config'], text=True))
flags = [a for a in args if a.startswith('--') and (not a.startswith(('--prefix=', '--srcdir=', '--with-contrib=')))]
flags.append('--with-contrib=' + str(pathlib.Path(sys.argv[2]).resolve()))
for f in ('macosx', 'merge-ffmpeg', 'extra-checks', 'avcodec', 'avformat', 'postproc', 'swscale', 'timeline-preview'):
    assert '--disable-' + f not in flags
    if '--enable-' + f not in flags:
        flags.append('--enable-' + f)
print('\n'.join(flags))
PY
configure_flags=()
while IFS= read -r flag; do configure_flags+=("$flag"); done < "$gate/configure-flags"
(
  unset GIT_DIR GIT_WORK_TREE
  export GIT_CEILING_DIRECTORIES="$outer" VLC_USERDATA_PATH="$gate/userdata"
  cd "$outer"
  "$vlc_source/configure" "${configure_flags[@]}" > "$gate/configure.log" 2>&1
  make -j8 distcheck "DISTCHECK_CONFIGURE_FLAGS=${configure_flags[*]}" "$identity_override" > "$gate/distcheck.log" 2>&1
)
```

Require zero exits, actual registered PASS receipts and complete terminal distcheck success through final distcleancheck.
The target override propagates through recursive make; this short recipe has no nested forensic guard or new nested-execution proof.
Never override TESTS, backend, assertions, global LDFLAGS or updater first-launch policy; stop on an error/modal/crash without retry.
Fresh Library namespaces are listed in each gate; userdata redirection alone does not isolate macOS preferences/caches.
Normal 94/archive 93 test cases preserve upstream distribution Lua-disable flags. No native/fullscreen/VoiceOver or shutdown-safety claim follows.
