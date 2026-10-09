#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Rebuild one FFmpeg9 Matroska object in owned scratch; preserve playback archives."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import tarfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--proof', type=Path, required=True)
parser.add_argument('--prefix', type=Path, required=True)
parser.add_argument('--resume-configure', action='store_true', help='Reuse reviewed owned patched source after preserved configure failure')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
proof = args.proof.resolve(strict=True)
prefix = args.prefix.resolve(strict=True)
source = proof / 'ffmpeg-9.0'
build = proof / 'ffmpeg-build'
archive = proof / 'libavformat-helper-private.a'
manifest = {'steps': [], 'original_archive': str(prefix / 'lib/libavformat.a')}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def guard():
    if shutil.disk_usage(proof).free < 1024 ** 3:
        raise RuntimeError('Less than 1 GiB free reserve')
    size = sum(p.stat().st_size for p in proof.rglob('*') if p.is_file() and not p.is_symlink())
    if size > 1024 ** 3:
        raise RuntimeError('Proof scratch exceeds 1 GiB')

def run(name, command, cwd, environment=None, timeout=90):
    guard()
    log = proof / (name + '.log')
    with log.open('xb') as output:
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        start = time.monotonic()
        try:
            while process.poll() is None:
                guard()
                if time.monotonic() - start > timeout:
                    raise RuntimeError(name + ' timeout')
                time.sleep(.25)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
    step = {'name': name, 'command': command, 'cwd': str(cwd), 'status': process.returncode,
            'elapsed_seconds': time.monotonic() - start, 'log': str(log)}
    manifest['steps'].append(step)
    (proof / 'private-build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if process.returncode:
        raise RuntimeError(name + ' failed; inspect preserved log before another attempt')

def members(path):
    data = path.read_bytes()
    assert data[:8] == b'!<arch>\n'
    offset = 8
    result = {}
    while offset < len(data):
        header = data[offset:offset + 60]
        assert header[58:60] == b'`\n'
        length = int(header[48:58].strip())
        name = header[:16].decode().strip()
        payload = data[offset + 60:offset + 60 + length]
        if name.startswith('#1/'):
            count = int(name[3:])
            name, payload = payload[:count].rstrip(b'\0').decode(), payload[count:]
        else:
            name = name.rstrip('/')
        if not name.startswith('__.SYMDEF'):
            assert name not in result
            result[name] = hashlib.sha256(payload).hexdigest()
        offset += 60 + length + length % 2
    return result

guard()
if args.resume_configure:
    manifest = json.loads((proof / 'private-build-manifest.json').read_text())
    assert source.is_dir() and build.is_dir() and not archive.exists()
    assert digest(proof / 'matroska-track-number-9.0.patch') == manifest['helper_patch_sha256']
else:
    assert not source.exists() and not build.exists() and not archive.exists()
    official_archive = proof / 'ffmpeg-9.0.tar.xz'
    expected = (root / 'work/upstream/vlc-master-story005/contrib/src/ffmpeg/SHA512SUMS').read_text().split()[0]
    assert hashlib.sha512(official_archive.read_bytes()).hexdigest() == expected
    manifest['official_archive_sha512'] = expected
    manifest['original_archive_sha256'] = digest(prefix / 'lib/libavformat.a')
    with tarfile.open(official_archive) as tar:
        for member in tar.getmembers():
            destination = (proof / member.name).resolve()
            assert destination.is_relative_to(proof) and not member.issym() and not member.islnk()
        tar.extractall(proof)
    assert (source / 'RELEASE').read_text().strip() == '9.0'
    contrib = root / 'work/upstream/vlc-master-story005/contrib/src/ffmpeg'
    recipe = (contrib / 'rules.mak').read_text()
    patches = re.findall(r'\$\(APPLY\) \$\(SRC\)/ffmpeg/(\S+)', recipe)
    manifest['contrib_patches_sha256'] = {name: digest(contrib / name) for name in patches}
    for i, name in enumerate(patches):
        run('contrib-patch-%02d' % i, ['patch', '--batch', '-f', '-p1',
                                    '-i', str(contrib / name)], source)

    matroska = source / 'libavformat/matroskadec.c'
    before = matroska.read_text()
    anchor = '        par = st->codecpar;\n'
    assert before.count(anchor) == 1
    after = before.replace(anchor, '        /* Helper-private TrackNumber identity; out-of-range is unmappable. */\n'
                           '        st->id = track->num > 0 && track->num <= INT_MAX\n'
                           '               ? (int)track->num : -1;\n' + anchor)
    import difflib
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                       fromfile='a/libavformat/matroskadec.c',
                                       tofile='b/libavformat/matroskadec.c'))
    (proof / 'matroska-track-number-9.0.patch').write_text(patch)
    matroska.write_text(after)
    manifest['helper_patch_sha256'] = digest(proof / 'matroska-track-number-9.0.patch')
configuration = next(line for line in subprocess.check_output(
    ['strings', str(prefix / 'lib/libavutil.a')], text=True).splitlines()
    if line.startswith('--prefix='))
options = shlex.split(configuration)
manifest['original_configuration'] = options
sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
compiler = subprocess.check_output(['xcrun', '--find', 'clang'], text=True).strip()
replacements = {
    '--prefix=': str(proof / 'unused-install-prefix'),
    '--cc=': compiler, '--host-cc=': compiler,
    '--extra-cflags=': '-Werror=partial-availability -isysroot %s -mmacosx-version-min=10.13 -DMACOSX_DEPLOYMENT_TARGET=10.13 -arch arm64 -I%s' % (sdk, prefix / 'include'),
    '--extra-ldflags=': '-L%s -isysroot %s -mmacosx-version-min=10.13 -DMACOSX_DEPLOYMENT_TARGET=10.13 -arch arm64' % (prefix / 'lib', sdk),
}
for tool in ['nm', 'ar', 'ranlib']:
    replacements['--' + tool + '='] = subprocess.check_output(['xcrun', '--find', tool], text=True).strip()
effective = []
for option in options:
    matching = next((key for key in replacements if option.startswith(key)), None)
    effective.append(matching + replacements[matching] if matching else option)
manifest['configuration_substitutions'] = replacements
effective.append('--host-cflags=-O2 -isysroot ' + sdk)
manifest['effective_configuration'] = effective
build.mkdir(exist_ok=args.resume_configure)
environment = dict(os.environ, PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'), PKG_CONFIG_PATH='')
run('configure', [str(source / 'configure'), *effective], build, environment)
run('matroska-object', ['make', '-j2', 'libavformat/matroskadec.o'], build, environment)
object_path = build / 'libavformat/matroskadec.o'
manifest['generated_config_sha256'] = {str(p.relative_to(build)): digest(p) for p in
    [build / 'config.h', build / 'config_components.h', build / 'ffbuild/config.mak']}
shutil.copyfile(prefix / 'lib/libavformat.a', archive)
run('replace-object', ['xcrun', 'ar', '-r', str(archive), str(object_path)], proof)
run('ranlib', ['xcrun', 'ranlib', str(archive)], proof)
original_members = members(prefix / 'lib/libavformat.a')
private_members = members(archive)
assert original_members.keys() == private_members.keys()
changed = [name for name in original_members if original_members[name] != private_members[name]]
assert changed == ['matroskadec.o'], changed
assert digest(prefix / 'lib/libavformat.a') == manifest['original_archive_sha256']
manifest.update(private_archive_sha256=digest(archive), object_sha256=digest(object_path),
                changed_members=changed, original_members=original_members,
                private_members=private_members,
                license=(source / 'COPYING.LGPLv2.1').read_text(),
                scratch_bytes=sum(p.stat().st_size for p in proof.rglob('*') if p.is_file()))
(proof / 'private-build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'archive': str(archive), 'changed_members': changed, 'scratch_bytes': manifest['scratch_bytes']}))
