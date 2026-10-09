# Baseline tool archive acquisition

2026-10-06 UTC, source pin `2e358f3098c2f2b7621d1dc568de8b61ad786322`.

Problem class: unavailable or stalled dependency mirrors. The unchanged official
tool recipe returned VideoLAN HTTP404 for M4 1.4.21 and gettext 0.26; its GNU
automatic mirror fallback transferred zero bytes for more than one minute.
Attempt `baseline-build-20261006T015601Z` was stopped by SIGTERM after84s,
preserving the full log and generated tools. Earlier18s attempt015535Z was
interrupted to adopt the pinned official CI's Darwin19 triplet and `-x` checks.
Neither interruption is a compiler-failure result.

Direct GNU primary archive URLs returned HTTP200 in bounded local HEAD probes:

- https://ftp.gnu.org/gnu/m4/m4-1.4.21.tar.gz
- https://ftp.gnu.org/gnu/gettext/gettext-0.26.tar.gz

Decision: acquire those exact archives with `curl -fL --max-time120`, verify
SHA512 against the pinned `extras/tools/SHA512SUMS`, then restart the same
unchanged source incrementally. No package version or product-source change.
Parent approved this route and subsequent exact-source, matching-checksum mirror
substitutions. Verification receipt records the actual digest and result.

The baseline monitor uses a fresh output directory, stops the process group
below1GiB free, and performs no deletion. Existing `work/build`, old source,
apps, preferences and media remain outside its mutation scope.

Follow-up: M4 direct download completed; gettext GNU direct stalled after13MiB
and its bounded HTTP resume stopped below1024bytes/s for15s. A fresh exact-version
download from `https://mirrors.kernel.org/gnu/gettext/gettext-0.26.tar.gz` completed
in17s. Both complete archives match the pinned SHA512SUMS exactly; see
`baseline-tool-download-verification.json`. The GNU partial is retained under
ignored scout work and was not supplied to the build.
