# Baseline readiness prerequisites

**Prepared for maintainer review; submission checklist incomplete; no submission.** These are baseline
repairs found while executing required gates, separate from the intended hover
feature. Maintainers may prefer independent review; no acceptance route is agreed.
Apply after the feature component, in the series order below.

| Part | Paths | Delta | Contract |
|---|---:|---:|---|
| 0001-build-order-macosx-install-and-clean-vtutils.patch | 3 | +21/−3 | Ordered transformed-name install/uninstall, required PIPSPI header, generated-nib and vtutils cleanup |
| 0002-clock-preserve-observed-system-origin.patch | 2 | +9/−2 | Observed clock origin plus same-point conversion invariant |
| 0003-tests-select-gnutls-for-pem-trust-fixture.patch | 1 | +36/−1 | Explicit GnuTLS for its PEM trust fixture, retaining default unknown-cert phase |
| 0004-opengl-initialize-legacy-version-fallback.patch | 1 | +1/−1 | Defined legacy GL major-version fallback |
| 0005-macosx-release-caller-owned-media-source.patch | 3 | +111/−0 | Balance owned source reference; actual-provider callsite test |
| 0006-macosx-retire-playback-ended-timer-during-termination.patch | 2 | +23/−1 | Invalidate playback-ended timer and guard termination; existing actual-controller test |
| 0007-macosx-fence-video-window-callback-lifetime.patch | 6 | +514/−52 | Video-window Disable/Destroy lifetime fence, actual-provider wiring regression and normal registration |

Parts 1–5 contain independent baseline concerns; untouched-base application has
not been qualified here. Part 6 regression extends a feature-created context test,
so the packaged prerequisite stack requires the feature component. Do not claim
the whole prerequisite series applies independently to upstream base.

The canonical 72-path combined stack passes normal 009 complete registered check and
conventional 010 complete distcheck, including lifetime 5/5 cases. These gates qualify the
combined stack, not independent base application/build of these prerequisites. Normal-Quit
observations are narrow; historical shutdown 004 causality remains user-accepted deferred.
See [CONTRIBUTION.md](../CONTRIBUTION.md) for executed commands and current evidence, and
[limitations](../feature-series/LIMITATIONS.md) for remaining native/platform boundaries.

Proposed commit subjects are the patch basenames rendered as the seven contracts
above; raw diffs contain no invented authorship, sign-off or assignment headers.
Existing notices remain; new actual-provider regression uses GPL-2.0-or-later.
Contributor/contact credit and AI disclosure are in the feature component.
No binaries, private logs, profiles or fixture media are package inputs.

Part 7 is a separate upstream lifetime concern, reviewed in the canonical feature-first
stack; independent untouched-base application/build is unqualified. Five focused
actual-provider cases have an old-source failure/new-source pass; normal 009 build/check
and complete 010 distcheck pass for these bytes; historical 004 causality remains
unresolved/deferred. Later narrow normal-Quit observations do not prove a causal fix.
