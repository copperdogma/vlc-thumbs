# Queued video-window callbacks during shutdown

2026-10-06, 22:40 Edmonton. Problem class: asynchronous callbacks retaining a raw C resource beyond the resource's teardown boundary, with lock-order constraints on safe cancellation.

The independent loaded normal-Quit001 experiment played the synthetic source, then received one actual Command-Q. Owned PID17589 exited SIGSEGV without SIGTERM. Its retained report (`work/story005-native015-normalquit001/VLC-2026-10-06-222119.ips`, SHA256`b48b0a3ff1d04ca6ca58dc1604f543c94e07cade7c86c2ccdcb46db333ac911a`) faults on the `org.videolan.vlc.vout.events` queue through `vout_display_window_ResizeNotify`, object logging and `vlc_vaLogCallback`. Relevant packaged binary identities match app015. This is a different stack from the historical5678 condition-wait/unmapped-return crash; a shared cause is unproved.

Pinned source is VLC master`2e358f3098c2f2b7621d1dc568de8b61ad786322`. Root independently compared these candidate files with that exact revision; all are byte-identical:

| File | SHA256 |
| --- | --- |
| `VLCVoutView.h` | `467f9e1a9aaebdd01120f0346baa2e497df9770d4577cee8198ca6f46beecce4` |
| `VLCVoutView.m` | `4dd9f2cbd5ce5e5696a9ed5c8ac22ed1d64f3e4b22ab4e90c4c69bbd7eeb31ee` |
| `VLCVideoOutputProvider.m` | `1fe27b32bf7ab062cda089503bdbed2a9e3feadbd0902dbd7eec7cfaa8af541a` |
| `src/video_output/window.c` | `fcdb4a3abddb86b822892585ebd8558405cb9fb5540ed8adf2876f5bfdbadd7d` |
| `src/video_output/video_window.c` | `e86feb5aa4cd128c70e6feced09bff7e32aaa393dabc9ff731de699b46c60add` |
| `src/misc/messages.c` | `60fd293560463a0f1c70eed9c5ef6cd7f079d69a6d7c2ccefca83be8b87f497c` |

The first three live under `modules/gui/macosx/windows/video/`. Layout asynchronously reads the reusable view's `_wnd` without its mutex. Disable schedules main-thread removal, the operations table lacks `.destroy`, and removal does not clear `_wnd`. Core window deletion frees both the C window and callback-owner state. Removal also later dereferences the raw window key to obtain its parent. This establishes an unfenced lifetime defect on the observed path. The exact freed allocation responsible for the crash remains unproved; unchanged baseline code does not exonerate feature-dependent shutdown timing.

Established alternatives were compared before proposing a repair. Apple's [dispatch-queue guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/OperationQueues/OperationQueues.html) explains asynchronous block capture, explicit ownership of referenced storage, and serialization limited to one queue. [Block variable ownership](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Blocks/Articles/bxVariables.html) distinguishes retaining Objective-C objects from copying raw pointers. A blind main/event-queue synchronous drain is unsuitable: the existing resize comment documents a RenderPicture/display-lock cycle. Waiting inside WindowDisable also risks reversing core window-lock and mouse/fullscreen lock order.

An exact in-tree precedent is `modules/video_output/apple/VLCVideoUIView.m` at the same pin: `detachFromParent`248–259 invalidates the window under the reporting mutex, `reshape`371–374 reports under that mutex, and Close450–456 calls detach at `.destroy`. Adapt that lifetime boundary for macOS reuse rather than altering logging, disabling video, swallowing callbacks or changing core unload policy.

The selected proposal is a small per-C-window resize lifetime record, binding generation and separate resize gate. Queued layout captures the record/generation/dimensions rather than the view/current raw pointer. Destroy invalidates and waits at the safe core boundary; disable only revokes queued work without waiting under the window lock. Handle retains, reused views, mouse bindings, callback removal and asynchronous opaque-key consumers must close coherently. A shared mouse/resize gate would introduce another main→mutex→resize→display→main cycle, so it is rejected.

Root has released only an ignored patch draft and compact regression-feasibility plan to a SOL6.1medium builder. No shutdown fix, source application, app rebuild or runtime repetition is authorized by this note. Require production-callsite old-source failure/corrected pass where compactly feasible, independent ownership/lock review, then one fresh exact-build normal-Quit experiment. Unit or SIGTERM success alone cannot qualify the failing UI path. Any inability to close the class within this bounded design must be reported before widening the harness or provider architecture.


## Reviewed correction — 2026-10-07T04:51Z

The destroy-only/nonblocking-disable prescription above is superseded. A view-owned vout reference preserves the C-window allocation on the normal owner path, but does not prove that logger/global context remains available after nonfinal `vout_Close`. Revoke the per-window generation at Disable, then quiesce the independent resize gate before returning. Keep Destroy as final idempotent invalidation. Never wait on the reusable view's mouse mutex at either boundary.

The bounded strong review independently checked normal StopDisplay: it joins rendering, clears display, removes the mouse handler under state.lock, and clears the clock before Disable. Subsequent ResizeNotify has only a brief state update, logging, clock_lock with no clock, and display_lock with no display; ReportSize supplies no acknowledgement callback. It does not acquire window/resource/player locks or require main-thread dispatch. Splitter and OpenGL cleanup release their resize-state locks before Disable. This is scoped in-tree consumer closure, not a universal external lock-graph proof. Root verifies pinned include/vlc_window.h195–202 expressly forbids owner callbacks invoking window functions, and238–239 forbids disabling inside a callback; direct callback-to-Disable reentrancy violates the existing contract.

The separate mouse plan is qualified only for the normal vout owner: clear the matching binding before dropping the view-owned vout hold, and clear p_vout before vout_Release to handle reentrant destruction. Splitter/GL can directly delete windows, while this macOS provider already assumes a vout parent; do not generalize normal-owner mouse lifetime proof to them. Strong review accepts the bounded draft direction, not an implemented or proven crash repair. SOL6.1medium may write one ignored concrete patch draft and compact actual-production regression proposal only. Candidate application, compilation and native trials remain held by resource admission; no causality or successful-shutdown claim.


## Draft disposition — 2026-10-07T05:01Z

The exact ignored three-file draft SHA27e07a08e37684a05c3466cab137429fc26f308380f0217e09a77c6a22dee4df passes only nonmutating apply-check (+246/-52 Git lines). Focused independent review found no further concrete product defect, but the proposed helper-level harness does not prove actual provider Disable/Destroy wiring, lacks disable/rebind and in-flight Destroy cases, and its20ms negative observation cannot exclude descheduling. Root accepts these as validation blockers. Draft is preserved unapplied; no compile/runtime/counterfactual or crash-fix claim. Do not widen the fake GUI or resume design churn under the storage hold. A compact actual-provider regression strategy and resource admission are prerequisites to future implementation.
