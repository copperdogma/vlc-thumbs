# Conventional distcheck host-tool prerequisite

The pinned upstream Makefile.am:230 distribution hook uses GNU `sed -i` and same-line `c\text`. Native BSD sed rejected the distribution filename as a command. This is a distribution-tool portability prerequisite, not a changed feature-source failure.

Primary sources: [GNU sed manual](https://www.gnu.org/software/sed/manual/sed.html) documents GNU in-place editing and change-command syntax; [GNU stable 4.10 announcement](https://lists.gnu.org/archive/html/info-gnu/2026-04/msg00009.html) supplies release archive URLs and the SHA256 used. Exact archive SHA256 is `4d179ffaf92ec4dcec541f7c032be1c3b9a1856f4970adb95a505221702f5277`. The primary FTP endpoint timed out under a 60-second bound; the matching 2,826,040-byte archive from `https://mirrors.kernel.org/gnu/sed/sed-4.10.tar.gz` matched the primary checksum. No detached-signature verification is claimed.

Decision: build normal GNU sed 4.10 from its verified release source into owned `work/story005-gnu-sed/prefix`, without installing globally or changing VLC's distribution hook. Place this prefix first on PATH only for the distribution operation. The fully written runner configures `--disable-nls`, builds with four jobs, installs to that prefix, reports version and tests the exact failing sed expression against disposable two-file input.

The earlier shell-unset failure is preserved separately: upstream env.build.sh expects optional unset variables, so the frozen runner uses `set -eo pipefail`, without nounset. All launchers and failure logs remain preserved.

The failed distribution operation regenerated 98 PO files and po/vlc.pot (99 tracked translation paths). Their exact generated-only diff is preserved as gzip with integrity check and per-path index/generated hashes in `distcheck-generated-po-preservation.json`; the public 56-file index tree remains `1a567b8705d3f744afc2b873458a5e8af02f7a7b`. Distribution contents containing generated translations are distinct from the proposed public source series. No translation generation enters public patches.

The local smoke and final unchanged-recipe retry outcomes will be recorded in their guarded-run receipts. No global host security or tool installation changes are made; installed apps and unrelated processes remain untouched.

Post-environment preflight exposed that env.build.sh:96 reconstructs PATH from VLC_PATH; adding sed only before sourcing was insufficient. That two-second preflight failure (070447Z) never launched make. The corrected immutable runner adds the owned prefix to VLC_PATH. Its post-environment preflight (070532Z) passes GNU sed 4.10 and all critical command paths; the one actual recipe retry is 070541Z.
