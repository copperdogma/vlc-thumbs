# Platform SQLite availability probe

2026-10-04, current arm64/Xcode 27 environment. Tiny probe only; no annotation
feature, identity hashing, two-process test or real user database.

Compiled from `sqlite-platform-probe.c` with `xcrun clang -arch arm64
-mmacosx-version-min=10.7 -lsqlite3` into ignored work/probes/bookmark-plan.
Actual Mach-O minimum is macOS 11.0, SDK 27.0. Link target is system
`/usr/lib/libsqlite3.dylib`; no new dependency download. Source and complete
output are retained here, binary remains ignored. Probe directory ~60 KiB.

Header/runtime SQLite 3.54.0; threadsafe=2. DELETE journal, synchronous=3
(EXTRA), fullfsync=1, foreign_keys=1 and timeout=500 read back successfully.
Committed insert/revision edit worked; stale revision update affected zero rows;
rollback preserved the committed label; quick_check returned ok. Unique temporary
probe database cleanup returned zero. No crash or power-failure guarantee follows.

Each process must configure/read back its own connection settings. Future tests
cover concurrent writers, bounded busy failure, retry idempotency, revision
conflicts and interruption before/after acknowledged commit. A serial worker
queue owns each connection. Full-file identity latency is still unmeasured.
