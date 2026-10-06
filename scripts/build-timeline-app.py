#!/usr/bin/env python3
"""Incrementally build/bundle Story 002 using the existing qualified arm64 app.

This does not download dependencies, build a fresh VLC baseline, run the app,
or touch installed VLC. Stop the development app before using this command.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import plistlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / 'work/build/vlc-arm64'
APP = BUILD / 'VLC.app'
MACOS = APP / 'Contents/MacOS'
PLUGIN = BUILD / 'modules/.libs/libmacosx_plugin.dylib'
HELPER = ROOT / 'work/build/thumbnail-helper/thumbnail-helper'
EVIDENCE = ROOT / 'work/validation/story002'


def apply_module():
    spec = importlib.util.spec_from_file_location('apply_vlc_patches', ROOT / 'scripts/apply-vlc-patches.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def preflight(patcher):
    patcher.inspect()
    for path in [BUILD, APP, MACOS, PLUGIN, HELPER, BUILD / 'bin/vlc-cache-gen',
                 MACOS / 'VLC', MACOS / 'plugins/libmacosx_plugin.dylib', MACOS / 'vlc-thumbnail-helper',
                 MACOS / 'plugins/plugins.dat', APP / 'Contents/Info.plist']:
        patcher.owned_path(path)
    for path in [BUILD / 'Makefile', BUILD / 'modules/Makefile', MACOS / 'VLC',
                 MACOS / 'plugins/libmacosx_plugin.dylib', APP / 'Contents/Info.plist',
                 BUILD / 'bin/vlc-cache-gen']:
        if not path.is_file():
            raise RuntimeError('Existing qualified arm64 build/app required; see build runbook: ' + str(path))
    # This runner only replaces the existing GUI module/helper. Reserve four
    # copies of their current sizes for compiler/linker/copy/signing temporaries,
    # plus 128 MiB. A fresh VLC/dependency build needs a separate space check.
    # The qualified baseline predates the private helper. Its first build must
    # reach the compiler; use a conservative size estimate until output exists.
    helper_size = HELPER.stat().st_size if HELPER.is_file() else 32 * 1024 ** 2
    required_free = 128 * 1024 ** 2 + 4 * (PLUGIN.stat().st_size + helper_size)
    if shutil.disk_usage(BUILD).free < required_free:
        raise RuntimeError(f'Less than {required_free // (1024 ** 2)} MiB free for this incremental build; stop before creating more artifacts')
    processes = subprocess.check_output(['ps', '-axo', 'command='], text=True).splitlines()
    if any(line.strip().startswith(str(MACOS / 'VLC')) for line in processes):
        raise RuntimeError('Stop the development VLC app before replacing its binaries')
    architecture = subprocess.check_output(['lipo', '-archs', str(MACOS / 'VLC')], text=True).strip()
    if architecture != 'arm64':
        raise RuntimeError('Qualified app executable must be arm64 only: ' + architecture)
    # The compiler and helper use only this existing contrib namespace.
    if not (patcher.SOURCE / 'contrib/aarch64-apple-darwin27/lib/pkgconfig/libavformat.pc').is_file():
        raise RuntimeError('Pinned arm64 contribs are missing; this command does not rebuild them')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only preflight; no build or bundle changes')
    args = parser.parse_args()
    patcher = apply_module()
    preflight(patcher)
    if args.check:
        print('Preflight passed: pinned checkout, existing arm64 app, owned paths, stopped app, free space.')
        return
    # Evidence is also confined to this checkout, even if a parent was symlinked.
    if EVIDENCE.resolve() != EVIDENCE.absolute():
        raise RuntimeError('Evidence path must not contain symlinks')
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log_path = EVIDENCE / ('app-build-' + stamp + '.log')
    print('Build log: ' + str(log_path), flush=True)
    commands = []
    environment = dict(os.environ, PATH=str(patcher.SOURCE / 'extras/tools/build/bin') +
                       ':/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
                       ACLOCAL_PATH='/usr/local/share/aclocal', PKG_CONFIG_PATH='',
                       PKG_CONFIG_LIBDIR=str(patcher.SOURCE / 'contrib/aarch64-apple-darwin27/lib/pkgconfig'))
    with log_path.open('w') as log:
        def run(command):
            commands.append(list(map(str, command)))
            log.write('\n' + json.dumps(commands[-1]) + '\n')
            log.flush()
            subprocess.run(commands[-1], cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT, check=True)

        run([sys.executable, ROOT / 'scripts/apply-vlc-patches.py'])
        run(['make', '-C', BUILD / 'modules', '-j4', 'libmacosx_plugin.la'])
        run(['bash', ROOT / 'scripts/build-thumbnail-helper.sh'])
        preflight(patcher)
        for binary in [PLUGIN, HELPER]:
            arch = subprocess.check_output(['lipo', '-archs', str(binary)], text=True).strip()
            if arch != 'arm64':
                raise RuntimeError('Refusing non-arm64 binary: ' + str(binary))
        # Save the replaced module once for local baseline comparisons. This may
        # already be a feature module on later runs; the manifest labels it so.
        backup = EVIDENCE / 'pre-run-libmacosx_plugin.dylib'
        if backup.resolve() != backup.absolute():
            raise RuntimeError('Pre-run module backup must not be a symlink')
        if not backup.exists():
            shutil.copy2(MACOS / 'plugins/libmacosx_plugin.dylib', backup)
        shutil.copy2(PLUGIN, MACOS / 'plugins/libmacosx_plugin.dylib')
        shutil.copy2(HELPER, MACOS / 'vlc-thumbnail-helper')
        plist_path = APP / 'Contents/Info.plist'
        with plist_path.open('rb') as handle:
            info = plistlib.load(handle)
        info.update(CFBundleIdentifier='org.videolan.vlc-thumbs.development',
                    CFBundleName='VLC Timeline Development', CFBundleDisplayName='VLC Timeline Development')
        plist_temp = plist_path.with_name('Info.timeline-build.plist')
        patcher.owned_path(plist_temp)
        with plist_temp.open('wb') as handle:
            plistlib.dump(info, handle)
        os.replace(plist_temp, plist_path)
        # Simple preferences has feature-owned outlets; bundle its matching nib.
        run(['xcrun', 'ibtool', '--minimum-deployment-target', '11.0', '--compile',
             APP / 'Contents/Resources/English.lproj/SimplePreferences.nib',
             patcher.SOURCE / 'modules/gui/macosx/UI/SimplePreferences.xib'])
        run(['codesign', '--force', '--deep', '--sign', '-', APP])
        run([BUILD / 'bin/vlc-cache-gen', MACOS / 'plugins'])
        run(['codesign', '--force', '--sign', '-', MACOS / 'plugins/plugins.dat'])
        # Deep signing here would change module mtimes and invalidate the cache.
        run(['codesign', '--force', '--sign', '-', APP])
        run(['codesign', '--verify', '--deep', '--strict', APP])
        helper_deps = subprocess.check_output(['otool', '-L', str(MACOS / 'vlc-thumbnail-helper')], text=True)
        for line in helper_deps.splitlines()[1:]:
            dependency = line.strip().split(' (', 1)[0]
            if not dependency.startswith(('/usr/lib/', '/System/Library/')):
                raise RuntimeError('Unexpected helper dependency: ' + dependency)
        inputs = [patcher.PATCH, ROOT / 'scripts/apply-vlc-patches.py', pathlib.Path(__file__).resolve(),
                  *sorted((ROOT / 'src/macosx').glob('*')), ROOT / 'src/thumbnail-helper/thumbnail-helper.c']
        outputs = [MACOS / 'VLC', MACOS / 'plugins/libmacosx_plugin.dylib', MACOS / 'vlc-thumbnail-helper',
                   MACOS / 'plugins/plugins.dat', plist_path, backup]
        manifest = {'schema_version': 1, 'built_at_utc': stamp, 'source_pin': patcher.PIN,
                    'baseline_requirement': 'Existing qualified build; no dependency acquisition in this runner',
                    'bundle_id': info['CFBundleIdentifier'], 'minimum_macos': '11.0', 'commands': commands,
                    'log': str(log_path.relative_to(ROOT)), 'helper_dependencies': helper_deps,
                    'inputs_sha256': {str(path.relative_to(ROOT)): sha(path) for path in inputs},
                    'outputs_sha256': {str(path.relative_to(ROOT)): sha(path) for path in outputs},
                    'helper_build_manifest': json.loads((HELPER.parent / 'build-manifest.json').read_text())}
        manifest_path = EVIDENCE / ('app-build-' + stamp + '.json')
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built isolated app: ' + str(APP))
    print('Manifest: ' + str(manifest_path))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
