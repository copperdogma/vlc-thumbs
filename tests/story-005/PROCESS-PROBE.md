# VLC process termination discriminator

`process_probe.c` calls the pinned VLC `vlc_process_Spawn`,
`vlc_process_fd_Read` and `vlc_process_Terminate` APIs directly. It contains no
replacement process implementation. POSIX/macOS scope only; no preparser
callback, native hover, NAS or full worker-lifecycle qualification is claimed.

The executable is also its controlled child. `default` installs the default
SIGTERM disposition; `ignore` installs a handler that records SIGTERM and keeps
waiting. Child readiness is acknowledged through the actual VLC process socket
after signal disposition is installed. The parent records entry into termination
and, if it happens, return with raw wait status. On the pinned source, termination
sends SIGTERM then performs blocking waitpid; this is the runtime discriminator.

## Build and run

Wait for the baseline build owner's configured headers, libtool and
`src/libvlccore.la`. From that configured build directory, with absolute
`SOURCE`, `BUILD` and `PROJECT` paths supplied as shell variables:

```sh
bash "$BUILD/libtool" --tag=CC --mode=link xcrun clang -std=c11 -DHAVE_CONFIG_H -D_GNU_SOURCE \
  -Wall -Wextra -Werror -I"$BUILD" -I"$BUILD/include" \
  -I"$SOURCE" -I"$SOURCE/include" \
  "$PROJECT/tests/story-005/process_probe.c" "$BUILD/src/libvlccore.la" \
  -o "$PROJECT/work/story005-scout/process-probe"
DYLD_LIBRARY_PATH="$BUILD/src/.libs" python3 "$PROJECT/work/story005-scout/run-process-probe.py" \
  "$PROJECT/work/story005-scout/.libs/process-probe" \
  "$PROJECT/docs/evidence/story-005/process-probe-RUN.json"
```

Use the actual Mach-O/ELF binary in `.libs` if libtool creates a shell launcher.
Verify the executable and linked core library with `file` and `otool -L` on
macOS (or `ldd` on Linux); capture compiler/link command, source revision and
baseline library provenance in the evidence. Do not rebuild core from a copied
implementation or use stub libraries. Dynamic-loader failure is an unavailable
experiment, not evidence about termination.

The disposable Python launcher uses a new session for each case, remains outside
the test group, waits at most eight seconds and kills the whole group with
SIGKILL on timeout or any cleanup path. It obtains group members with POSIX `ps`,
checks the child inherited the dedicated group and records final live-member
verification. No broad process-name matching or existing app/build termination
is permitted. A surviving group member or missing handshake invalidates the case.
The launcher also cleans up if interrupted. Keep its logs and JSON together.

Expected discriminating evidence is a completed default control and an ignore
case with `termination_begin`, `child_sigterm_ignored`, no termination return,
outer timeout and zero final live group members. Such a result demonstrates this
controlled child's termination hang, not every slow filesystem or kernel state.
No finite reap guarantee should be inferred from an eight-second observation.

## Pinned source references

- `include/vlc_process.h`: exact API signatures and termination/I/O ownership.
- `src/posix/process.c:87–93`: executable path prepended to supplied arguments.
- `src/posix/process.c:124–148`: SIGTERM, socket shutdown, blocking reap.
- `src/posix/spawn.c:202–209`: `waitpid(pid, ..., 0)`.
- `src/preparser/external.c:660–665`: preparser failure uses that termination path.

Readiness is separate from execution. Until linked baseline artifacts exist and
the two cases run, the source-derived hypothesis remains unmeasured.

## Recorded run

The baseline core became available and the 20261006 run reproduced the
discriminator. Default control returned raw wait status15 (SIGTERM) and exited0.
The resistant child recorded SIGTERM; termination did not return within the
eight-second outer window. The wrapper killed that dedicated group with SIGKILL.
Both cases verified inherited child group identity and zero final group members.
See `docs/evidence/story-005/process-probe-runtime-20261006.json` and accompanying
logs, plus `process-probe-provenance-20261006.json` for exact command, linkage and
post-run hashes. This directly tests VLC's process API, not the full preparser
callback path or any real NAS failure.
