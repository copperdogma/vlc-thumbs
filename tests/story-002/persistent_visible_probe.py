#!/usr/bin/env python3
"""Small bounded JSONL client for visible-capture-probe --serve."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import select
import subprocess
import time
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
DEFAULT_PROBE = WORK / 'validation/story002/persistent-visible-capture-probe'
HASH_RE = re.compile(r'^[0-9a-fA-F]{16}$')


class PersistentProbeError(RuntimeError):
    pass


def _owned(path: Path, *, must_exist: bool = False) -> Path:
    path = Path(path).absolute()
    resolved = path.resolve(strict=must_exist)
    if resolved != path or not resolved.is_relative_to(WORK) or resolved == WORK:
        raise ValueError(f'Path must stay beneath {WORK} without symlinks: {path}')
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


class PersistentVisibleProbe:
    """Own one probe server process and its fresh output/log files.

    Commands accept either ``expected_hash`` or the calibration pair
    ``settle_ms`` and ``count``. Server stdout is reserved for JSONL acks;
    stderr goes to an exclusively created file beneath ``work/``.
    """

    def __init__(self, target_pid: int, probe: Path = DEFAULT_PROBE,
                 server_log: Path | None = None):
        self.target_pid = int(target_pid)
        self.probe = _owned(Path(probe), must_exist=True)
        if not self.probe.is_file() or not os.access(self.probe, os.X_OK):
            raise ValueError(f'Probe must be an executable existing file: {self.probe}')
        if self.target_pid <= 0:
            raise ValueError('Target PID must be positive')
        self.probe_sha256 = _sha256(self.probe)
        default_log = WORK / 'validation/story002' / f'persistent-visible-server-{self.target_pid}-{time.time_ns()}.log'
        self.server_log = _owned(Path(server_log) if server_log else default_log)
        self.process: subprocess.Popen[bytes] | None = None
        self.server_pid: int | None = None
        self._stdout_buffer = bytearray()
        self._stderr_file = None

    @staticmethod
    def _owned_fresh(path: Path) -> Path:
        resolved = _owned(Path(path))
        resolved.parent.mkdir(parents=True, exist_ok=True)
        if resolved.parent.resolve() != resolved.parent or resolved.exists():
            raise ValueError(f'Output must be fresh and have canonical work/ parents: {resolved}')
        return resolved

    def _check_binary(self) -> None:
        if _sha256(self.probe) != self.probe_sha256:
            raise PersistentProbeError('The exact probe binary changed while the server client was active')

    def _read_json_line(self, timeout: float = 5.0) -> dict[str, Any]:
        if not 0 < timeout <= 5:
            raise ValueError('JSONL read timeout must be in (0, 5] seconds')
        deadline = time.monotonic() + timeout
        fd = self.process.stdout.fileno() if self.process and self.process.stdout else None
        if fd is None:
            raise PersistentProbeError('Probe server stdout is closed')
        while True:
            newline = self._stdout_buffer.find(b'\n')
            if newline >= 0:
                line = bytes(self._stdout_buffer[:newline])
                del self._stdout_buffer[:newline + 1]
                try:
                    value = json.loads(line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise PersistentProbeError(f'Probe server emitted invalid JSONL: {exc}') from exc
                if not isinstance(value, dict):
                    raise PersistentProbeError('Probe server acknowledgement must be a JSON object')
                return value
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Probe server JSONL acknowledgement exceeded 5 seconds')
            readable, _, _ = select.select([fd], [], [], remaining)
            if not readable:
                raise TimeoutError('Probe server JSONL acknowledgement exceeded 5 seconds')
            chunk = os.read(fd, 4096)
            if not chunk:
                code = self.process.poll() if self.process else None
                raise PersistentProbeError(f'Probe server closed stdout before acknowledgement (exit {code})')
            self._stdout_buffer.extend(chunk)
            if len(self._stdout_buffer) > 65536:
                raise PersistentProbeError('Probe server JSONL line exceeds 65536 bytes')

    def start(self) -> dict[str, Any]:
        if self.process is not None:
            raise PersistentProbeError('Probe server is already started')
        self._check_binary()
        self.server_log.parent.mkdir(parents=True, exist_ok=True)
        if self.server_log.exists() or self.server_log.parent.resolve() != self.server_log.parent:
            raise ValueError(f'Refusing to overwrite or follow symlink for server log: {self.server_log}')
        self._stderr_file = self.server_log.open('xb')
        self.process = subprocess.Popen([str(self.probe), '--serve', str(self.target_pid)],
                                        cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self._stderr_file, bufsize=0)
        self.server_pid = self.process.pid
        try:
            ready = self._read_json_line(5.0)
            if (ready.get('ready') is not True or ready.get('server_pid') != self.server_pid or
                    ready.get('target_pid') != self.target_pid):
                raise PersistentProbeError(f'Unexpected server ready acknowledgement: {ready}')
            return ready
        except BaseException:
            self.close()
            raise

    def send(self, point: Sequence[float], output: Path, *, expected_hash: str | None = None,
             settle_ms: int | None = None, count: int | None = None,
             save_last_image: Path | None = None) -> dict[str, Any]:
        if not self.process or self.process.poll() is not None:
            raise PersistentProbeError('Probe server is not running')
        self._check_binary()
        if len(point) != 2 or any(not isinstance(v, (int, float)) or isinstance(v, bool) or not __import__('math').isfinite(v) for v in point):
            raise ValueError('point must contain two finite numbers')
        if expected_hash is not None:
            if not HASH_RE.fullmatch(expected_hash):
                raise ValueError('expected_hash must be 16 hexadecimal characters')
            if settle_ms is not None:
                raise ValueError('Use expected_hash or settle_ms/count, not both')
        elif (not isinstance(settle_ms, int) or isinstance(settle_ms, bool) or not 1 <= settle_ms <= 2000 or
              not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 100):
            raise ValueError('Calibration requires settle_ms in [1,2000] and count in [1,100]')
        output_path = self._owned_fresh(Path(output))
        command: dict[str, Any] = {'point': [float(point[0]), float(point[1])], 'output': str(output_path)}
        if expected_hash is not None:
            command['expected_hash'] = expected_hash.lower()
            if count is not None:
                if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 100:
                    raise ValueError('count must be an integer in [1,100]')
                command['count'] = count
        else:
            command['settle_ms'] = settle_ms
            command['count'] = count
        save_path = None
        if save_last_image is not None:
            save_path = self._owned_fresh(Path(save_last_image))
            command['save_last_image'] = str(save_path)
        payload = json.dumps(command, allow_nan=False, separators=(',', ':')).encode() + b'\n'
        if len(payload) > 65536:
            raise ValueError('Command exceeds 65536 bytes')
        try:
            self.process.stdin.write(payload)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise PersistentProbeError(f'Could not write command to probe server: {exc}') from exc
        ack = self._read_json_line(5.0)
        if set(ack) != {'returncode', 'output', 'count'}:
            raise PersistentProbeError(f'Unexpected command acknowledgement schema: {ack}')
        if ack['output'] != str(output_path) or not isinstance(ack['count'], int):
            raise PersistentProbeError(f'Command acknowledgement does not match output: {ack}')
        if not output_path.is_file() or output_path.resolve() != output_path:
            raise PersistentProbeError(f'Probe did not leave its owned output file: {output_path}')
        if save_path and (ack['returncode'] == 0 and (not save_path.is_file() or save_path.resolve() != save_path)):
            raise PersistentProbeError(f'Probe did not leave its requested owned PNG: {save_path}')
        return ack

    def close(self) -> None:
        process = self.process
        if process is None:
            return
        if process.stdin and not process.stdin.closed:
            try:
                process.stdin.close()  # EOF is the normal server shutdown signal.
            except OSError:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        if process.stdout:
            process.stdout.close()
        if self._stderr_file:
            self._stderr_file.close()
            self._stderr_file = None
        self.process = None

    def __enter__(self) -> 'PersistentVisibleProbe':
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
