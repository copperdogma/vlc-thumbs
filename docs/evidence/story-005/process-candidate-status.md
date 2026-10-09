# First candidate: forced POSIX process termination

Candidate is a detached worktree at pinned
`2e358f3098c2f2b7621d1dc568de8b61ad786322`, separate from the unchanged baseline.
No commits, submission, installed-app changes or baseline-source/output changes
were made by this task.

`patches/vlc-master/0001-process-force-termination.patch` contains only the
POSIX SIGTERM-to-SIGKILL change, clarified forced-termination wording and a new
POSIX process regression registered in Automake/Meson. Existing attribution is
preserved. New test source uses LGPL-2.1-or-later, without invented author/sign-off.
The patch passes application check against unchanged baseline and diff whitespace
check. Exact file/patch hashes are in `process-candidate-preflight.json`.

## Runtime evidence and limits

The diagnostic compiles the actual candidate `src/posix/process.c` directly into
the new test executable, linking unchanged baseline core for other VLC functions.
It is not a fresh complete candidate-core build or build-registration proof.
The baseline negative control compiles the same test against unchanged core only.
Both use an independent eight-second process-group wrapper; controlled children
also have their own three-second alarm before acknowledging readiness.

- Candidate diagnostic passes forced termination with SIGKILL status; repeated
  Kill, concurrent reader completion, later read EOF, failed write and reap;
  unforced close/reap preserving exit42. All three child groups matched the
  dedicated test group, with zero final members. Evidence:
  `process-candidate-diagnostic-runtime-003.json` and logs.
- Unchanged baseline negative control fails the forced SIGKILL assertion after
  its child safety alarm. It does not hang or leak children. Evidence:
  `process-candidate-diagnostic-baseline-negative.json` and logs.
- Initial diagnostic compilation called a nonexistent semaphore destroy API;
  removed that call after inspecting the actual header. Failed build retained in
  `process-candidate-diagnostic-build.log`.
- Initial runtime regression required exact post-Kill EPIPE and failed with
  observed EINVAL22. Root explicitly kept this separate from forced-termination
  scope. The final test requires aborted I/O and logs errno; it does not qualify
  exact EPIPE. Original failures retained in `process-candidate-diagnostic-runtime`
  and `...-002` evidence. The product errno behavior/header promise remain unchanged.

The concurrent-reader semaphore proves thread entry, not the exact instant it
blocks inside the operating system. Its bounded read and child watchdog preserve
cleanup even under adverse scheduling. No hard realtime deadline, NAS stall,
end-to-end preparser callback/recovery, Windows or other POSIX platform result is
claimed. SIGKILL addresses userspace SIGTERM resistance; kernel wait remains a
separate limitation.

## Remaining qualification

Build owner is preparing a separate candidate output for genuine upstream
configuration, core build and registered test execution. Automake/Meson
registration has been authored but not yet exercised. Independent lifecycle/test
review, candidate-native core execution, available broader checks and distribution
coverage remain pending. Focused diagnostic success is not Story005 completion
or a complete preview contribution ready for submission.
