#!/usr/bin/env python3
"""Replace one object in a private copy of pinned libavformat; preserve VLC's libs."""
import hashlib
import json
import pathlib
import re
import shlex
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(root):
    h = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            content = ('symlink:' + str(path.readlink())).encode()
        elif path.is_file():
            content = path.read_bytes()
        else:
            continue
        h.update(relative.encode() + b'\0' + hashlib.sha256(content).digest())
    return h.hexdigest()


def members(path):
    """Read Darwin/BSD ar members, excluding the regenerated symbol table."""
    data = path.read_bytes()
    if not data.startswith(b'!<arch>\n'):
        raise RuntimeError('Expected BSD static archive')
    offset, result = 8, {}
    while offset < len(data):
        header = data[offset:offset + 60]
        if len(header) != 60 or header[58:] != b'`\n':
            raise RuntimeError('Malformed static archive')
        size = int(header[48:58].strip())
        payload = data[offset + 60:offset + 60 + size]
        if len(payload) != size:
            raise RuntimeError('Truncated static archive')
        name = header[:16].decode().strip()
        if name.startswith('#1/'):
            name_size = int(name[3:])
            name = payload[:name_size].rstrip(b'\0').decode()
            payload = payload[name_size:]
        else:
            name = name.rstrip('/')
        if not name.startswith('__.SYMDEF'):
            if name in result:
                raise RuntimeError('Duplicate archive member: ' + name)
            result[name] = hashlib.sha256(payload).hexdigest()
        offset += 60 + size + size % 2
    return result


def main():
    repo = pathlib.Path(__file__).resolve().parent.parent
    source = repo / 'work/build/vlc-source/contrib/contrib-aarch64-apple-darwin27/ffmpeg'
    original = repo / 'work/build/vlc-source/contrib/aarch64-apple-darwin27/lib/libavformat.a'
    config = source / 'vlc_build/ffbuild/config.mak'
    patch = repo / 'patches/ffmpeg-8.1.2/matroska-track-number.patch'
    output = repo / 'work/build/thumbnail-libavformat'
    # This script owns exactly this ignored build directory. Never follow an
    # output symlink or mutate the original source, config or contrib archive.
    if output.is_symlink() or output.parent.resolve() != repo / 'work/build':
        raise RuntimeError('Unexpected private build path')
    for path in (source, original, config, patch):
        if not path.exists():
            raise RuntimeError('Missing pinned input: ' + str(path))
    if (source / 'RELEASE').read_text().strip() != '8.1.2':
        raise RuntimeError('Private patch requires pinned FFmpeg 8.1.2')
    original_hash, tree_hash = digest(original), source_digest(source)
    original_members = members(original)
    if 'matroskadec.o' not in original_members:
        raise RuntimeError('Expected exactly one original matroskadec.o')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    clone = output / 'ffmpeg'
    shutil.copytree(source, clone, symlinks=True)
    build = clone / 'vlc_build'
    link = build / 'src'
    if not link.is_symlink() or link.resolve() != source:
        raise RuntimeError('Unexpected configured FFmpeg source symlink')
    link.unlink()
    link.symlink_to(clone, target_is_directory=True)
    subprocess.run(['patch', '--batch', '--forward', '-F0', '-p1', '-i', str(patch)],
                   cwd=clone, check=True)
    # The configured contrib flags contain only SRC_PATH substitutions. Resolve
    # these explicitly rather than evaluating make or shell text.
    values = {}
    for line in config.read_text().splitlines():
        match = re.match(r'^(CC|CPPFLAGS|CFLAGS|AR|RANLIB)=(.*)$', line)
        if match:
            values[match[1]] = match[2].replace('$(SRC_PATH)', str(clone))
    if set(values) != {'CC', 'CPPFLAGS', 'CFLAGS', 'AR', 'RANLIB'}:
        raise RuntimeError('Missing configured compiler/archive flags')
    if any('$' in value for value in values.values()):
        raise RuntimeError('Unexpected unresolved configured flag')
    obj = output / 'matroskadec.o'
    # ffbuild/library.mak adds HAVE_AV_CONFIG_H for every library object.
    command = (shlex.split(values['CC']) + ['-I.', '-Isrc/', '-DHAVE_AV_CONFIG_H'] +
               shlex.split(values['CPPFLAGS']) + shlex.split(values['CFLAGS']) +
               ['-c', '-o', str(obj), str(clone / 'libavformat/matroskadec.c')])
    subprocess.run(command, cwd=build, check=True)
    archive = output / 'libavformat.a'
    shutil.copy2(original, archive)
    ar_command = shlex.split(values['AR']) + ['r', str(archive), str(obj)]
    ranlib_command = shlex.split(values['RANLIB']) + [str(archive)]
    subprocess.run(ar_command, check=True)
    subprocess.run(ranlib_command, check=True)
    private_members = members(archive)
    changed = sorted(name for name in original_members
                     if original_members[name] != private_members.get(name))
    if set(private_members) != set(original_members) or changed != ['matroskadec.o']:
        raise RuntimeError('Private archive changed unexpected members: ' + repr(changed))
    if digest(original) != original_hash or source_digest(source) != tree_hash:
        raise RuntimeError('Original VLC contrib inputs changed during private build')
    paths = [pathlib.Path(__file__).resolve(), patch, config,
             source / 'vlc_build/config.h', source / 'vlc_build/config_components.h',
             source / 'ffbuild/common.mak', source / 'ffbuild/library.mak',
             source / 'libavformat/matroskadec.c', source / 'RELEASE', original,
             repo / 'work/probes/thumbnail-plan/libav-build-provenance.json']
    manifest = {
        'schema_version': 1, 'ffmpeg_version': '8.1.2',
        'original_source_tree_sha256': tree_hash,
        'original_inputs_unchanged': True, 'changed_archive_members': changed,
        'compile_command': command, 'compile_cwd': str(build),
        'archive_command': ar_command, 'ranlib_command': ranlib_command,
        'input_sha256': {str(path.relative_to(repo)): digest(path) for path in paths},
        'patched_source_sha256': digest(clone / 'libavformat/matroskadec.c'),
        'object_sha256': digest(obj), 'private_archive_sha256': digest(archive),
        'object_architecture': subprocess.check_output(['file', str(obj)], text=True).strip(),
        'original_member_sha256': original_members,
        'private_member_sha256': private_members,
    }
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(archive)


if __name__ == '__main__':
    main()
