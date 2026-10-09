# macOS timeline keyframe previews

**READY for bounded pre-submission review of Phases1/2; no submission.** The whole story remains InProgress; Phase3 is not authorized.
Hovering the native timeline shows an image and its actual **Keyframe** time;
pointer time remains the seek target. An Interface preference disables previews.
Unsupported media and failures retain ordinary time hover. Bookmarks are outside
this contribution.

Current qualification: Three current matched60s AB/BA/AB pairs pass bounded playback/preparation/audio/drop/resource qualification. All native frame/audio loss counters are zero; candidate-minus-baseline sampled mean CPU is+1.47/+2.20/+2.29 percentage points and combined sampled maximum RSS is+100.3/+100.6/+97.6MiB. Recorder overhead is measured separately. Complete pair1 was retained across a human-permission pause; the interrupted second pair was excluded and its failed cohort remains failed. System-mixed AAC/PCM continuity, variable-rate capture observations and sampled resources retain their limits; no per-app callback or universal smoothness claim follows.

Earlier actual main Position-to-Pause/Play reader navigation retains its narrow inherited scope. Current preview-visible/fullscreen VoiceOver is unmeasured; latest practical navigation was inconclusive, with no established defect. Autonomous reader setup stopped. Returned-main thumbnail/seekbar persistence is observed; ordinary title/buttons fade. Upstream ordinary fade occurrence is inherited, while current fade cause and broader preview lifecycle remain unknown.

## First review

The player/context supplies selected-video identity and an input epoch. The
service owns scheduling, stale-result cancellation, 32 MiB RAM/256 MiB disk
caches and two serial worker queues. Retained private helper processes use the
existing FFmpeg contrib libraries and keep metadata/decode work off the UI
thread and player lock. Their movie-time and retained-session contract motivated
this boundary; a future core thumbnail extension remains a maintainer option.
No endorsement is assumed.

| Review unit | Main concern |
|---|---|
| F0000 | Distribution lists for existing headers |
| F0001 | FFmpeg identity and bounded Matroska admission |
| F0002 | Helper protocol, build/package integration and synthetic tests |
| F0003 | Service, cache, scheduling and worker ownership |
| F0004 | Player context, native hover and preferences |
| P0001–8 | [Build, test and lifetime prerequisites](../blocker-prerequisites/README.md) |

The [current scope table](LIMITATIONS.md) separates executed proof from remaining
gaps. [Historical screenshots](demonstration/README.md) illustrate earlier builds,
not current native qualification. The [manifest](manifest.json) pins source bytes,
modes, blobs and patch hashes; [contribution description](contribution-description-draft.md)
and [proposed subjects](proposed-commit-messages.md) support review.

## Exact application

Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Combined tree: `b7c0f24e442c35a57bb108d56b801fd05b624943` (72 paths).
Feature midpoint: `cce7f9917b8dc4d5432e7f83b2c840f8c3c5027b` (59 paths).

P denotes `blocker-prerequisites/`; F denotes `feature-series/`:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

Apply all thirteen entries once from the pinned source root. P0006–7 depend on
feature-created regression tests; component `series` files are review inventories.
Neither the five feature patches alone nor an independently applied whole
prerequisite stack is a qualified runnable release. Maintainers may choose other
MR boundaries; doing so requires new application and qualification proof.

```sh
while IFS= read -r patch; do
  git apply "$review_package/$patch"
done < "$review_package/contribution-series"
```

Set `review_package` to this package's absolute path. There are 19 prerequisite
paths and six overlaps with the 59 feature paths; do not omit or reorder patches.

## Build, check and distribution recipe

Use the patched source's `bin/timeline-preview/README.md` for the pinned native
arm64 tools/contrib setup, including both FFmpeg patches and GNU sed selection;
`bin/timeline-preview/tests/README.md` describes synthetic fixtures and the full
helper matrix. Those are source-tree paths, not extra package inputs.

**Execution status:** literal public normal configure/build/prepare/relink and
normal-check commands passed in interrupted stages. The full public recipe below,
including its fresh outer distcheck, remains **unexecuted**. Separately executed
complete conventional distcheck passed using a read-only preflight that forwarded
unchanged argv/status to the ordinary upstream test driver. These are distinct
routes; no uninterrupted public-recipe PASS is claimed.

Retain the normal build's exported compiler/SDK/architecture, original LDFLAGS,
pkg-config isolation, ncurses, GNU sed and tool PATH. Set absolute `vlc_source`,
`vlc_build`, `vlc_contrib` and fresh nonexistent `review_dir` paths without spaces
or commas. Use Bash, Python3 and GNU make; HOME remains unchanged. The following
existing commands create separate GUI test identities without replacing normal
metadata or altering installed VLC:

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

Require zero exits, registered PASS receipts and terminal distcheck success through
final distcleancheck. Keep normal backend/assertions/tests, global LDFLAGS and
updater first-launch policy unchanged. Fresh Library namespaces are listed per
gate; userdata redirection alone does not isolate macOS preferences/caches.
Stop on error/modal/crash and preserve logs; the recipe provides no native hover,
reader, playback-cost or universal shutdown verdict. Full helper fixtures require
the separate matrix commands in the source test guide; `make check` does not rerun
all 77 matrix checks. Normal and archive registered totals differ with upstream
Lua-distribution flags; nested native counts overlap them.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance; retain GPL/LGPL and third-party notices. Credit is no sole-ownership
claim, assignment, waiver or sign-off. No binaries or private media are included.
