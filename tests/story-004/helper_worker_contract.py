#!/usr/bin/env python3
"""Persistent extraction correctness/lifecycle tests; no native/NAS speed claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


def reply(process, timeout=17):
    # Unbuffered pipe reads, bounded line and exact payload. A missing reply is a failure.
    deadline = time.monotonic() + timeout
    def read_exact(size):
        data = bytearray()
        while len(data) < size:
            assert select.select([process.stdout], [], [], max(0, deadline-time.monotonic()))[0], 'reply timeout'
            part = os.read(process.stdout.fileno(), size-len(data))
            assert part, 'unexpected EOF'
            data.extend(part)
        return bytes(data)
    line = bytearray()
    while not line.endswith(b'\n'):
        assert len(line) < 4096, 'oversized header'
        line.extend(read_exact(1))
    header = json.loads(line)
    size = header.get('payload_bytes', 0)
    assert 0 <= size <= 320*180*4
    pixels = read_exact(size)
    assert header['version'] == 3
    if not header['ok']:
        assert size == 0
    return header, pixels


def start(helper, path):
    process = subprocess.Popen([str(helper), '--worker', '--input', str(path), '--video-ordinal', '0',
        '--video-count', '1', '--max-width', '320', '--max-height', '180'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    header, payload = reply(process)
    assert header['type'] == 'ready' and header['ok'] and not payload
    assert header['open_count'] == 1 and header['duration_us'] > 0
    return process, header


def finish(process):
    process.stdin.close()
    assert process.wait(timeout=3) == 0
    assert not process.stdout.read(), 'trailing protocol output'
    assert not process.stderr.read(), 'unexpected stderr'


def metadata_contract(helper):
    result = {'scope': 'Generated file metadata-only stat identity and blocked open/stat watchdog; no content freshness claim.',
              'helper_sha256': hashlib.sha256(helper.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory(prefix='vlc-helper-metadata-') as directory:
        folder = Path(directory)
        media = folder/'generated.bin'
        media.write_bytes(b'generated metadata fixture')
        argv = [str(helper), '--fingerprint', 'stat', '--input', str(media)]
        def acquire(path):
            run = subprocess.run([str(helper), '--fingerprint', 'stat', '--input', str(path)], capture_output=True, timeout=17)
            assert run.returncode == 0 and not run.stderr
            header = json.loads(run.stdout)
            assert header['ok'] and header['version'] == 3 and header['type'] == 'identity' and header['policy'] == 'stat'
            assert header['payload_bytes'] == header['bytes_read'] == header['read_calls'] == 0
            assert header['fingerprint'] == hashlib.sha256(('vlc-thumbnail-stat-v1:'+header['stat_identity']).encode()).hexdigest()
            return header
        before = acquire(media)
        assert acquire(media) == before
        link = folder/'linked.bin'
        link.symlink_to(media)
        assert acquire(link)['stat_identity'] == before['stat_identity']
        replacement = folder/'replacement.bin'
        replacement.write_bytes(b'generated other contents!')
        link.unlink(); link.symlink_to(replacement)
        assert acquire(link)['stat_identity'] != before['stat_identity']
        saved = media.stat()
        media.write_bytes(b'changed metadata fixture!!')
        os.utime(media, ns=(saved.st_atime_ns, saved.st_mtime_ns))
        assert acquire(media)['stat_identity'] != before['stat_identity']
        source = folder/'blocked-metadata.c'
        library = folder/'blocked-metadata.dylib'
        source.write_text(r"""#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
static void delay(const char *operation, const char *path) {
    const char *selected = getenv("VLC_HELPER_TEST_BLOCK_METADATA");
    const char *target = getenv("VLC_HELPER_TEST_METADATA_TARGET");
    if (selected && target && !strcmp(path, target) && !strcmp(selected, operation)) {
        struct timespec sleep = {17, 0}; nanosleep(&sleep, NULL);
    }
}
static int delayed_open(const char *path, int flags, ...) { delay("open", path); return open(path, flags, 0); }
static int delayed_stat(const char *path, struct stat *state) { delay("stat", path); return stat(path, state); }
__attribute__((used)) static struct { const void *replacement; const void *original; }
interposes[] __attribute__((section("__DATA,__interpose"))) = {
    {(const void *)delayed_open, (const void *)open},
    {(const void *)delayed_stat, (const void *)stat}
};
""")
        subprocess.run(['xcrun', 'clang', '-dynamiclib', '-arch', 'arm64', str(source), '-o', str(library)], check=True)
        result['deadline_seconds'] = {}
        for operation in ['open', 'stat']:
            environment = dict(os.environ, DYLD_INSERT_LIBRARIES=str(library), VLC_HELPER_TEST_BLOCK_METADATA=operation, VLC_HELPER_TEST_METADATA_TARGET=str(media))
            started = time.monotonic()
            blocked = subprocess.run(argv, env=environment, capture_output=True, timeout=20)
            elapsed = time.monotonic()-started
            if operation == 'open':
                # Metadata-only stat must not open the input at all, even when
                # opening that exact path would block. Hashing still must.
                assert blocked.returncode == 0 and json.loads(blocked.stdout)['ok'] and not blocked.stderr
                assert elapsed < 3
                full_argv = list(argv); full_argv[full_argv.index('stat')] = 'sampled'
                result['metadata_avoids_open_seconds'] = elapsed
                full_started = time.monotonic()
                blocked = subprocess.run(full_argv, env=environment, capture_output=True, timeout=20)
                elapsed = time.monotonic()-full_started
                assert blocked.returncode != 0 and not blocked.stdout and not blocked.stderr
                assert 14 <= elapsed < 20
            else:
                assert blocked.returncode != 0 and not blocked.stdout and not blocked.stderr
                assert 14 <= elapsed < 20
            result['deadline_seconds']['blocked_'+operation] = elapsed
        result['checks'] = ['zero content reads, deterministic stat digest', 'symlink follows same target, retarget changes stat',
                            'restored mtime mutation changes metadata', 'metadata opens no descriptor; content open and metadata stat faults terminate without output corruption']
        result['pass'] = True
    return result


def teardown_contract(helper):
    result = {'scope': 'Generated fixture EOF teardown blocked-close watchdog. Completed response retained; no NAS/UI proof.',
              'helper_sha256': hashlib.sha256(helper.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory(prefix='vlc-helper-teardown-') as directory:
        folder = Path(directory)
        source = folder/'blocked-close.c'
        library = folder/'blocked-close.dylib'
        marker = folder/'block'
        media = ROOT/'work/fixtures/story-002/standard.mp4'
        source.write_text(r"""#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
static int media_fd = -1;
static int capture_open(const char *path, int flags, ...) {
    int descriptor = open(path, flags, 0);
    const char *target = getenv("VLC_HELPER_TEST_CLOSE_TARGET");
    if (target && !strcmp(path, target)) media_fd = descriptor;
    return descriptor;
}
static int delayed_close(int descriptor) {
    const char *marker = getenv("VLC_HELPER_TEST_CLOSE_MARKER");
    if (descriptor == media_fd && marker && access(marker, F_OK) == 0) {
        struct timespec delay = {17, 0}; nanosleep(&delay, NULL);
    }
    return close(descriptor);
}
__attribute__((used)) static struct { const void *replacement; const void *original; }
interposes[] __attribute__((section("__DATA,__interpose"))) = {
    {(const void *)capture_open, (const void *)open},
    {(const void *)delayed_close, (const void *)close}
};
""")
        subprocess.run(['xcrun', 'clang', '-dynamiclib', '-arch', 'arm64', str(source), '-o', str(library)], check=True)
        environment = dict(os.environ, DYLD_INSERT_LIBRARIES=str(library),
            VLC_HELPER_TEST_CLOSE_TARGET=str(media), VLC_HELPER_TEST_CLOSE_MARKER=str(marker))
        process = subprocess.Popen([str(helper), '--worker', '--input', str(media), '--video-ordinal', '0',
            '--video-count', '1', '--max-width', '320', '--max-height', '180'],
            env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        try:
            header, _ = reply(process)
            assert header['type'] == 'ready' and header['ok']
            process.stdin.write(b'91 1000000\n')
            header, pixels = reply(process)
            assert header['id'] == 91 and header['ok'] and pixels
            marker.touch()
            started = time.monotonic()
            process.stdin.close()  # EOF arrives after response while extraction watchdog is idle.
            status = process.wait(timeout=20)
            elapsed = time.monotonic()-started
            assert status != 0 and 14 <= elapsed < 20, (status, elapsed)
            assert not process.stdout.read() and not process.stderr.read(), 'teardown must not append corrupt protocol bytes'
            result['deadline_seconds'] = {'blocked_close_after_response_eof': elapsed}
            result['completed_response'] = {'header': header, 'pixel_sha256': hashlib.sha256(pixels).hexdigest()}
            result['pass'] = True
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, default=ROOT/'work/build/thumbnail-helper/thumbnail-helper')
    parser.add_argument('--output', type=Path, default=ROOT/'work/validation/story004/helper-worker-contract.json')
    parser.add_argument('--idle-seconds', type=float, default=16)
    parser.add_argument('--metadata-only', action='store_true')
    parser.add_argument('--teardown-only', action='store_true')
    args = parser.parse_args()
    if args.teardown_only:
        value = teardown_contract(args.helper)
        output = args.output.parent/'helper-teardown-contract.json'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(value, indent=2)+'\n')
        print(json.dumps({'pass': value['pass'], 'deadline_seconds': value['deadline_seconds'], 'output': str(output)}))
        return
    if args.metadata_only:
        value = metadata_contract(args.helper)
        output = args.output.parent/'helper-metadata-contract.json'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(value, indent=2)+'\n')
        print(json.dumps(value))
        return
    result = {'scope': 'Generated fixture v2/v3 parity, out-of-order state reset, protocol, mutation, idle survival. No NAS/native proof.',
              'helper_sha256': hashlib.sha256(args.helper.read_bytes()).hexdigest(), 'fixtures': [], 'checks': []}
    for name in ['standard.mp4', 'standard.mkv', 'nonzero.mkv', 'vfr.mkv', 'rotation.mp4', 'edit-offset.mp4', 'long-gop.mp4']:
        path = ROOT/'work/fixtures/story-002'/name
        process, ready = start(args.helper, path)
        record = {'name': name, 'ready': ready, 'samples': []}
        try:
            for ident, target in enumerate([7000000, 1000000, 9000000, 0, 7000000], 1):
                process.stdin.write(f'{ident} {target}\n'.encode())
                header, pixels = reply(process)
                baseline = subprocess.run([str(args.helper), '--input', str(path), '--time-us', str(target),
                    '--video-ordinal', '0', '--video-count', '1', '--max-width', '320', '--max-height', '180'],
                    capture_output=True, timeout=7)
                line, _, expected = baseline.stdout.partition(b'\n')
                single = json.loads(line)
                assert header['id'] == ident and header['requested_us'] == target
                assert header['ok'] == single['ok']
                for key, value in single.items():
                    if key != 'version':
                        assert header[key] == value, (name, target, key, header, single)
                assert pixels == expected, (name, target, 'pixel difference')
                assert header['open_count'] == 1 and header['bytes_read'] >= ready['bytes_read']
                record['samples'].append({'header': header, 'pixel_sha256': hashlib.sha256(pixels).hexdigest()})
            finish(process)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
        result['fixtures'].append(record)
    path = ROOT/'work/fixtures/story-002/standard.mp4'
    for bad in [b'bad\n', b'1 -2\n', b'1 2 3\n', b'1 '+b'0'*97+b'\n', b'1 2']:
        process, _ = start(args.helper, path)
        process.stdin.write(bad)
        process.stdin.close()
        header, pixels = reply(process)
        assert not header['ok'] and header['error'] == 'invalid_request' and not pixels
        assert process.wait(timeout=3) != 0 and not process.stdout.read()
    result['checks'].append('malformed and overlong/incomplete input rejected')
    process, _ = start(args.helper, path)
    time.sleep(args.idle_seconds)
    assert process.poll() is None, 'idle operation wrongly timed out'
    process.stdin.write(b'99 1000000\n')
    header, _ = reply(process)
    assert header['ok'] and header['id'] == 99
    finish(process)
    result['checks'].append(f'idle {args.idle_seconds}s then extraction and clean EOF')
    with tempfile.TemporaryDirectory(prefix='vlc-helper-worker-') as directory:
        copied = Path(directory)/'mutation.mp4'
        shutil.copyfile(path, copied)
        process, _ = start(args.helper, copied)
        with copied.open('ab') as stream:
            stream.write(b'changed')
        process.stdin.write(b'77 1000000\n')
        header, pixels = reply(process)
        assert not header['ok'] and header['error'] == 'media_changed' and not pixels
        assert process.wait(timeout=3) == 0 and not process.stdout.read()
    result['checks'].append('mutation rejected before extraction and worker retired')
    def fingerprint(path, policy):
        run = subprocess.run([str(args.helper), '--fingerprint', policy, '--input', str(path)], capture_output=True, timeout=17)
        value = json.loads(run.stdout)
        assert run.returncode == 0 and value['type'] == 'identity' and value['ok']
        assert value['payload_bytes'] == 0 and value['policy'] == policy
        return value
    with tempfile.TemporaryDirectory(prefix='vlc-helper-identity-') as directory:
        sample = Path(directory)/'identity.bin'
        data = bytearray((bytes(range(256))*16384))  # 4 MiB, private generated data.
        sample.write_bytes(data)
        full = fingerprint(sample, 'full')
        sampled = fingerprint(sample, 'sampled')
        assert full['fingerprint'] == hashlib.sha256(data).hexdigest()
        assert full['bytes_read'] == len(data) and sampled['bytes_read'] == 1048576
        digest = hashlib.sha256(b'vlc-thumbnail-sampled-v1\0')
        for index in range(16):
            offset = (len(data)-65536)*index//15
            digest.update(offset.to_bytes(8, 'big')+(65536).to_bytes(8, 'big')+data[offset:offset+65536])
        assert sampled['fingerprint'] == digest.hexdigest()
        assert fingerprint(sample, 'sampled')['fingerprint'] == sampled['fingerprint']
        old_stat = sample.stat()
        data[0] ^= 1
        sample.write_bytes(data)
        os.utime(sample, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
        assert fingerprint(sample, 'full')['fingerprint'] != full['fingerprint']
        assert fingerprint(sample, 'sampled')['fingerprint'] != sampled['fingerprint']
        sampled = fingerprint(sample, 'sampled')
        full = fingerprint(sample, 'full')
        data[70000] ^= 1  # Outside sampled windows: demonstrably weaker content check.
        sample.write_bytes(data)
        os.utime(sample, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
        assert fingerprint(sample, 'sampled')['fingerprint'] == sampled['fingerprint']
        assert fingerprint(sample, 'full')['fingerprint'] != full['fingerprint']
        assert fingerprint(sample, 'sampled')['stat_identity'] != sampled['stat_identity']  # ctime changed.
        sample.write_bytes(b'small generated fixture')
        assert fingerprint(sample, 'sampled')['fingerprint'] == hashlib.sha256(sample.read_bytes()).hexdigest()
    result['checks'].append('full SHA256 and sampled window recipe, deterministic repeat, changed sampled bytes, unsampled limitation, small full hash')
    # Inject a blocking read into only the private unsigned helper process.
    # This proves the independent watchdog works when AVIO cannot poll interrupts.
    with tempfile.TemporaryDirectory(prefix='vlc-helper-deadline-') as directory:
        folder = Path(directory)
        source = folder/'blocked-read.c'
        library = folder/'blocked-read.dylib'
        marker = folder/'block'
        source.write_text(r"""#include <stdlib.h>
#include <unistd.h>
#include <time.h>
static ssize_t delayed_read(int fd, void *buf, size_t count) {
    const char *marker = getenv("VLC_HELPER_TEST_BLOCK_READ");
    if (fd > 2 && marker && access(marker, F_OK) == 0) {
        struct timespec delay = {17, 0}; nanosleep(&delay, NULL);
    }
    return read(fd, buf, count);
}
__attribute__((used)) static struct { const void *replacement; const void *original; }
interpose __attribute__((section("__DATA,__interpose"))) = {(const void *)delayed_read, (const void *)read};
""")
        subprocess.run(['xcrun', 'clang', '-dynamiclib', '-arch', 'arm64', str(source), '-o', str(library)], check=True)
        environment = dict(os.environ, DYLD_INSERT_LIBRARIES=str(library), VLC_HELPER_TEST_BLOCK_READ=str(marker))
        worker_args = [str(args.helper), '--worker', '--input', str(path), '--video-ordinal', '0', '--video-count', '1', '--max-width', '320', '--max-height', '180']
        marker.touch()
        started = time.monotonic()
        blocked = subprocess.run(worker_args, env=environment, capture_output=True, timeout=20)
        assert blocked.returncode != 0 and not blocked.stdout, 'startup watchdog must terminate without corrupting stdout'
        startup_elapsed = time.monotonic()-started
        assert 14 <= startup_elapsed < 20
        marker.unlink()
        process = subprocess.Popen(worker_args, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        header, _ = reply(process)
        assert header['type'] == 'ready'
        marker.touch()
        started = time.monotonic()
        process.stdin.write(b'81 7000000\n')
        assert process.wait(timeout=20) != 0
        assert not process.stdout.read(), 'request watchdog must terminate without stdout corruption'
        request_elapsed = time.monotonic()-started
        assert 14 <= request_elapsed < 20
        result['deadline_seconds'] = {'blocked_startup_read': startup_elapsed, 'blocked_request_read': request_elapsed}
    result['checks'].append('independent 15s startup/request watchdog kills injected blocked read with no stdout corruption')
    result['metadata'] = metadata_contract(args.helper)
    result['teardown'] = teardown_contract(args.helper)
    result['pass'] = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'pass': True, 'fixtures': len(result['fixtures']), 'checks': result['checks'], 'output': str(args.output)}))


if __name__ == '__main__':
    main()
