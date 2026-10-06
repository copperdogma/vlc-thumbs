#!/bin/bash
# Build only the project helper from the already-built, pinned arm64 contribs.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
contrib_prefix="$repo_root/work/build/vlc-source/contrib/aarch64-apple-darwin27"
helper_build="$repo_root/work/build/thumbnail-helper"
if [[ ! -f "$contrib_prefix/lib/pkgconfig/libavformat.pc" ]]; then
  echo 'Existing pinned arm64 VLC contrib libraries are required; see build runbook.' >&2
  exit 1
fi
mkdir -p "$helper_build"
python3 "$repo_root/scripts/build-private-libavformat.py"
export PKG_CONFIG_LIBDIR="$contrib_prefix/lib/pkgconfig"
export PKG_CONFIG_PATH=''
# shlex retains each pkg-config flag as an argv element, including spaces in
# paths. No host include/library paths or downloads enter the build.
python3 - "$repo_root" "$helper_build" <<'PY'
import hashlib, json, pathlib, shlex, subprocess, sys
repo, output = map(pathlib.Path, sys.argv[1:])
source = repo / 'src/thumbnail-helper/thumbnail-helper.c'
flags = shlex.split(subprocess.check_output(['pkg-config', '--static', '--cflags', '--libs',
    'libavformat', 'libavcodec', 'libavutil', 'libswscale'], text=True))
private_archive = repo / 'work/build/thumbnail-libavformat/libavformat.a'
if flags.count('-lavformat') != 1:
    raise RuntimeError('Expected exactly one pinned libavformat link flag')
flags = [str(private_archive) if flag == '-lavformat' else flag for flag in flags]
command = ['xcrun', 'clang', '-arch', 'arm64', '-mmacosx-version-min=11.0', '-std=c11',
    '-Os', '-Wall', '-Wextra', '-Werror', '-Wl,-dead_strip', '-Wl,-S',
    str(source), '-o', str(output / 'thumbnail-helper'), *flags]
subprocess.run(command, check=True)
subprocess.run(['strip', '-x', str(output / 'thumbnail-helper')], check=True)
dependencies = subprocess.check_output(['otool', '-L', str(output / 'thumbnail-helper')], text=True)
for line in dependencies.splitlines()[1:]:
    dependency = line.strip().split(' (', 1)[0]
    if not dependency.startswith(('/usr/lib/', '/System/Library/')):
        raise RuntimeError('Unexpected non-system dependency: ' + dependency)
prefix = repo / 'work/build/vlc-source/contrib/aarch64-apple-darwin27'
inputs = [source, repo / 'scripts/build-thumbnail-helper.sh']
inputs += [repo / 'scripts/build-private-libavformat.py',
           repo / 'patches/ffmpeg-8.1.2/matroska-track-number.patch', private_archive,
           repo / 'work/build/thumbnail-libavformat/build-manifest.json']
inputs += sorted((prefix / 'lib').glob('libav*.a')) + [prefix / 'lib/libswscale.a']
inputs += [prefix / ('lib/' + name) for name in ['libgsm.a', 'libmp3lame.a', 'libopenjp2.a']]
manifest = {'schema_version': 1, 'command': command, 'architecture':
    subprocess.check_output(['file', str(output / 'thumbnail-helper')], text=True).strip(),
    'dependencies': dependencies, 'contrib_prefix': str(prefix),
    'sha256': {str(path.relative_to(repo)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
    'binary_sha256': hashlib.sha256((output / 'thumbnail-helper').read_bytes()).hexdigest(),
    'ffmpeg_provenance': 'work/probes/thumbnail-plan/libav-build-provenance.json',
    'private_libavformat_provenance': 'work/build/thumbnail-libavformat/build-manifest.json'}
(output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(output / 'thumbnail-helper')
PY
