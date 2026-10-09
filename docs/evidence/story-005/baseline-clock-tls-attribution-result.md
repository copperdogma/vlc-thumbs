# Untouched master baseline: clock and TLS attribution

The existing baseline at `2e358f3098c2f2b7621d1dc568de8b61ad786322` has a clean source checkout before and after these two runs. No rebuild or source/host fix was performed. Both existing arm64 test binaries were run once, sequentially, through the pinned Automake `autotools/test-driver` and their normal libtool wrappers, from the baseline test build directory. The only supplied environment value was the registered `srcdir`; the tests' unchanged `test_setup()` supplies the baseline modules paths. Exact commands, source/binary/library hashes, raw logs, TRS results, and bounds are in [the acquisition receipt](baseline-clock-tls-attribution-20261006T074008Z.json).

| Registered test | Automake result | Native exit | Time | Actual failure |
| --- | --- | --- | --- | --- |
| `test_src_clock_clock` | FAIL |134|1.848s|`drift_72`, `drift_check` at clock.c:662: converted drift differs from scenario total |
| `test_modules_tls` | FAIL |134|0.982s|known test-certificate acceptance, tls.c:188: `tls != NULL` |

Automake's driver itself returned0 after recording each FAIL; its driver exit is not a successful native-test result. Both owned process groups were absent after completion. The90s per-selector limit was not reached; minimum free space was28,227,846,144 bytes, above the1GiB reserve. Core dumps were disabled for these child processes only.

This reproduces the clock/TLS assertion signatures on untouched master with its full macOS configuration and normal contrib dependencies. The independent distcheck configuration is minimal, so this is not a matched whole-build comparison or proof of the exact backend cause. TLS logs show SecureTransport certificate-alias attempts, a GnuTLS server, and client handshake failure, but do not identify the selected client backend conclusively. Backend-selection remains a hypothesis. The already inspected pinned certificate's expiry is not implicated.

The normal baseline runs also log failure to dynamically load the macOS plugin because Sparkle is unavailable in these standalone test processes. No GUI was launched. No OpenGL tests, certificate/keychain/preference changes, backend overrides, or unknown-process termination were performed.
