# Process lifecycle discriminator readiness — 2026-10-05

Prepared `tests/story-005/process_probe.c`, `PROCESS-PROBE.md` and ignored
`work/story005-scout/run-process-probe.py`. The C caller links unchanged VLC core
and uses only signatures inspected in pinned `include/vlc_process.h`. It spawns
itself as a controlled child through the actual VLC API, waits for readiness,
then enters `vlc_process_Terminate(process, true)`.

The control accepts SIGTERM. The resistant child handles SIGTERM, records it
and continues waiting. The wrapper remains outside a dedicated test session,
applies an eight-second deadline, kills the entire test group on every cleanup
path and records `ps` evidence of zero final live members. Child group identity
must match the dedicated parent group. Interrupted launcher paths also clean up.
No installed apps, existing builds or broad process-name matches are used.

Source hypothesis: `src/posix/process.c:128,144` sends SIGTERM and then blocks
in `vlc_waitpid`; `src/posix/spawn.c:206` uses blocking `waitpid(..., 0)`.
The preparser error path calls that termination API at
`src/preparser/external.c:660–665`. POSIX spawn does not request a new child
process group, so the controlled child inherits the wrapper-created test group.

Wrapper Python syntax compilation passed. At preparation time the baseline
directory `work/story005-master-baseline` contained a partial configure attempt,
with no configured `config.h`, `libtool` or `src/libvlccore.la` available.
No C compilation, linking or runtime process experiment has occurred.

Await the baseline build owner's library readiness, then capture the exact
build/link command, source revision, executable/core linkage and both runtime
cases. A completed control plus resistant-child timeout with signal receipt and
verified cleanup would demonstrate this controlled process-termination hang.
It would not qualify preparser callback behavior, NAS responsiveness, kernel
uninterruptible I/O or the complete native feature. Readiness is not execution.

## Executed after core readiness — 20261006 UTC

Baseline owner confirmed configured substrate and arm64
`src/.libs/libvlccore.9.dylib`. Built the probe with actual baseline libtool/core,
`-Wall -Wextra -Werror`; initial libtool compiler-tag inference failed, then
explicit `--tag=CC` linked successfully. No source/core change was needed.

The normal SIGTERM child returned and was reaped (raw wait status15). The
resistant child installed its handler before acknowledging readiness, recorded
SIGTERM and remained alive with the parent blocked in termination until the
eight-second outer deadline. Dedicated group18235 contained only parent18235
and controlled child18236 at timeout; cleanup used SIGKILL on that group.
Both cases verified child group identity and ended with no group members.

`process-probe-runtime-20261006.json` and four stdout/stderr logs hold actual
results. `process-probe-provenance-20261006.json` holds exact build/run commands,
source revision, compiler/platform, binary/core linkage and SHA256 snapshots
captured after the run. Source remained clean at pinned2e358f3. The wrapper and
executable remain ignored disposable artifacts. `process-probe-build-*` logs
preserve failed and successful compile attempts.

Conclusion: unchanged VLC process termination can fail to return within eight
seconds for this controlled SIGTERM-resistant child. The external preparser's
use of the same termination function is source evidence; end-to-end preparser
callbacks, NAS stalls and recovery remain separate, unmeasured behavior.
