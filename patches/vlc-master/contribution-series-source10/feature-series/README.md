# macOS timeline keyframe previews

Hovering VLC's native timeline shows an image and its actual **Keyframe** time,
so a user can inspect a scene before seeking. Pointer time remains the seek
target. An Interface preference disables previews; unsupported media and failures
retain ordinary time hover. Bookmarks are outside this contribution.

The player context supplies selected-video identity and an input epoch. The
service owns scheduling, cancellation, 32 MiB RAM/256 MiB disk caches and two
serial worker queues. Retained helper processes use VLC's FFmpeg contrib libraries
for bounded metadata/decode work outside the UI thread and player lock. Their
movie-time and retained-session contract motivates this boundary.

## Review map

| Logical group | Patches and entry points | Contract / checks |
|---|---|---|
| Distribution and contrib | F0000–1; `modules/{audio_output,misc,video_output}/Makefile.am`, `contrib/src/ffmpeg/` | Shipped headers, TrackNumber identity and bounded Matroska admission |
| Helper and packaging | F0002; `bin/timeline-preview/` | [Protocol and synthetic fixtures](#ordinary-build-check-and-distcheck) |
| Service and cache | F0003; `modules/gui/macosx/timeline/` | Worker ownership, bounded scheduling, source qualification, cache/service checks |
| Native consumer | F0004; player context, `VLCPlaybackProgressSlider`, preferences | Selected-video context, hover reentrancy and real-controller checks |
| Prerequisite repairs | P0001–8; [reason, dependencies and coverage](../blocker-prerequisites/README.md) | Build/distribution, clock/TLS/GL, ownership, termination and control hit testing |

These are independent reading groups, not independently qualified runnable stacks.
The helper/contrib boundary carries a separate decoder, protocol and admission
policy; service and native consumer tests cross that boundary. P0006–7 additionally
modify feature-created tests. Keeping the canonical order preserves those actual
dependencies; regrouping the text changes no source or architecture.

Use the [central validation table](../CONTRIBUTION.md#validation-and-limits) and
[exact limits](LIMITATIONS.md). The [manifest](manifest.json) pins source bytes,
modes, blobs and patch hashes. [Proposed messages](proposed-commit-messages.md) and
[description](contribution-description-draft.md) support review;
[demonstrations](demonstration/README.md) are historical illustrations.

## Apply the pinned series

Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Combined tree: `b7c0f24e442c35a57bb108d56b801fd05b624943` (72 paths).
Feature midpoint: `cce7f9917b8dc4d5432e7f83b2c840f8c3c5027b` (59 paths).

Start with a fresh checkout at the base. Set `review_package` to this package's
absolute path. From the pinned source root, apply all thirteen entries once:

```sh
set -e
test "$(git rev-parse HEAD)" = 2e358f3098c2f2b7621d1dc568de8b61ad786322
while IFS= read -r patch; do
  git apply "$review_package/$patch"
done < "$review_package/contribution-series"
```

P denotes `blocker-prerequisites/`; F denotes `feature-series/`:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

Component `series` files are review inventories. P0006–7 require feature-created
regression tests; neither feature-only nor whole-prerequisite independent releases
are qualified. The prerequisites touch 19 paths, six overlapping the feature paths.

## Ordinary build, check and distcheck

In the patched source, follow `bin/timeline-preview/README.md`'s **Configuration
and build** section for native arm64 Xcode/SDK/Metal, Python3.9+, tools/contrib,
the pinned remaining-contrib archive and source FFmpeg with both patches. Select
GNU sed before running distribution hooks and after reconstructing the official
tool environment. Use the feature-enabled distribution commands below in place
of that source document's historical minimal `--disable-macosx` example.
`bin/timeline-preview/tests/README.md` supplies the separate synthetic fixture
matrix; registered `make check` does not repeat all 77 helper matrix checks.
Neither source guide is an extra package input or an ignored private harness.

Retain exported compiler/SDK/architecture, original LDFLAGS, pkg-config isolation,
ncurses and tool PATH from the normal build. Set absolute `vlc_source`, `vlc_build`
and `vlc_contrib` paths and a fresh nonexistent `review_dir`, without spaces or
commas. Use Bash, Python3 and GNU make. HOME stays unchanged. Ordinary GUI tests
use the normal application identity and may write its preferences/caches; use the
optional isolated host below when that is undesirable.

```bash
set -eo pipefail
# Use the configured build and patched contrib from the source build guide.
make -C "$vlc_build" -j8 V=1
make -C "$vlc_build" -j8 check
# Keep the same feature-enabled configuration for the extracted archive.
test ! -e "$review_dir"
mkdir "$review_dir"
python3 - "$vlc_build" "$vlc_contrib" > "$review_dir/configure-flags" <<'PY'
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
while IFS= read -r flag; do configure_flags+=("$flag"); done < "$review_dir/configure-flags"
outer="$review_dir/outer"
mkdir "$outer"
(
  unset GIT_DIR GIT_WORK_TREE
  export GIT_CEILING_DIRECTORIES="$outer"
  cd "$outer"
  "$vlc_source/configure" "${configure_flags[@]}"
  make -j8 distcheck "DISTCHECK_CONFIGURE_FLAGS=${configure_flags[*]}"
)
```

This direct route is assembled from the ordinary configure/build/check/distcheck
commands already exercised, with the optional GUI identity override omitted.
Normal public commands passed in stages; a separate complete conventional
`make distcheck` passed through final distcleancheck with a read-only preflight
forwarding unchanged ordinary test-driver argv/status. Neither this uninterrupted
sequence nor the full optional public recipe has been executed end to end.
See the [central validation table](../CONTRIBUTION.md#validation-and-limits).

Require zero exits and registered PASS receipts through final distcleancheck;
retain optional skips. Preserve normal backend/assertions/tests, global LDFLAGS
and updater first-launch policy. These commands provide no native hover, reader,
playback-cost or universal shutdown verdict.

## Optional: isolated GUI test host

This retained recipe embeds a fresh test identity into the static host and gives
each check a separate userdata directory. It leaves normal package metadata and
installed VLC unchanged. Userdata redirection alone does not isolate macOS
preferences/caches. It requires the same paths/environment as above, and a fresh
`review_dir`; it includes another build/check and fresh outer distcheck.
The full uninterrupted recipe remains unexecuted.

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

Stop on error, modal dialog or crash and preserve logs. Require registered PASS
receipts and terminal distcheck success through final distcleancheck. Fresh
Library namespaces are listed per gate. Full helper fixtures remain separate;
registered normal/archive totals differ with upstream Lua-distribution flags and
nested native counts overlap them.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance; retain GPL/LGPL and third-party notices. Credit is no sole-ownership
claim, assignment, waiver or sign-off. No binaries or private media are included.
