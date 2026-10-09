# Narrow autohide correction001

2026-10-08. Fresh user release00:29:21–00:59:21Z permits the reviewed small correction and bounded AppKit check; previous run deadline expired. This does not restart the earlier loop.

Only candidate `VLCMainVideoViewController.m:mouseOnControls` changes. It uses `self.bottomBarView` and converts the existing window-base point to each view before testing local bounds with AppKit edge semantics. Four guards/order/nil behavior remain; cache/thumbnail/tracking/timer/seek behavior is untouched.

Exact pre-edit bytes/mode are preserved. New delta receipt compares all72 historical R8 paths: only controller bytes differ, other71 bytes and all72 modes match; old affected-file backup matches R8. Historical freeze8, full009/010, apps016, revision13 and public11 remain preserved. Their validation does not qualify changed current source.

The tiny probe compiles with warnings treated as errors and runs actual extracted old/new methods with real AppKit views and an unshown window. All11 cases pass; five old failures reproduce then pass corrected: owner/common-nil and each translated/nonzero-bounds guard, alternating flipped views. Outside, nil and flipped edge semantics pass. No ordered/shown window, physical pointer movement or VLC process. This is predicate/coordinate evidence, not native applicability or the cause of Cam's observed fade.

First probe failed to complete and owned SIGTERM exit-15/partial output remains preserved. The undrained-PIPE wrapper matches a documented [subprocess deadlock risk](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait); ONE unchanged-binary direct-file run exits0 in0.062s. Capture plumbing is supported as a hypothesis, not stack-proven causality.

Successful run minimum sampled free1,717,420,032B; artifacts135,197B at receipt, under32MiB cap. Source-specific whitespace check passes. Full build requires>=5GiB versus~1.6GiB available;1GiB floor remains. No full make/package/native/runtime/source instrumentation/cleanup/commit/push/contact/install. Phase2 stays open.

Private artifacts: `work/story005-autohide-correction001/REPORT.md`, `correction.patch`, `source-delta-receipt.json`, `probe-filecapture-receipt.json`, retained first `probe-receipt.json`, `AppKitAutohideProbe.m`, and `DIAGNOSTIC-PLAN.md`. The diagnostic plan records identities/key/layout/geometry/callback/hide witnesses for one separately released stationary main-window trial; no diagnostic implementation was made.

Root independently rechecked all11 results/exit0, all72 source comparisons and backup/modes, and revision13's28 artifacts with zero hash mismatches. Process inventory found no remaining probe or VLC executable. `make methodology-compile`, `make validate` and `git diff --check` pass; these documentation checks do not qualify native behavior.
