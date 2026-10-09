# Fixed-sleep asynchronous coverage failure

The normal full-suite `candidate-build-20261006T062106Z.log` reports one existing ServiceContracts failure: after `Spin(2.5)`, finite proactive coverage had completed six jobs, launched one reusable worker and issued seven requests; `active=1`, `pending=0`, `worker_ready=1`. The seventh job was in flight. No helper protocol/fault or unbounded retry evidence appears in that payload. The 60.577-second duration is for the whole method, which includes watchdog/fault scenarios; it is not the proactive assertion's timeout.

The same whole ServiceContracts method previously passed in 59.799 seconds (`candidate-build-20261006T033257Z.log`). The newer condition-based finite-preparation/quiescence method passed in 4.027 seconds (`candidate-build-20261006T054833Z.log`), including a 1.2-second stable-count observation and shutdown wait. Thus a fixed 2.5-second sleep is not equivalent to waiting for completion. Concurrent fresh compilation and fixture jobs were reported during the failing run; their causal contribution is not established.

The general failure class is asynchronous completion tested through an arbitrary sleep. Apple's [asynchronous XCTest guidance](https://developer.apple.com/documentation/xctest/asynchronous-tests-and-expectations) uses completion expectations with a bounded wait. The existing standalone quiescence test already uses a bounded completion condition followed by a separate stable-count observation. This separates completion, eventual inactivity and elapsed-time performance claims.

Root selected one quiet final whole-suite rerun after environment restoration and independent app compilation finish, which includes both ServiceContracts and condition-based quiescence. This avoids a redundant focused-plus-full run. No source changes are proposed before that experiment. If the fixed-sleep assertion fails again while bounded completion/quiescence passes, the smallest test repair is to replace that sleep with a completion predicate using the established five-second test bound. That would repair test synchronization rather than enlarge the worker's 15-second deadline or change product scheduling. Root selection and source freeze are required before such a repair.

Follow-through: the quiet063243Z run reproduced the fixed-sleep failure. Root
approved the existing5s completion predicate and independent review cleared the
test-only change. The normal independent focused pair064522Z passes; the final
whole suite064748Z also passes, including ServiceContracts in61.296s. The finite
count, one-worker and later fairness checks remain. Production/helper bytes and
the15s worker deadline are unchanged. The separate pipe fixture repair and its
non-reproducing probe are documented in `service-test-sync-repair-receipt.json`
and `feature-independent-test-pipe-diagnosis.md`; no load-causation claim follows.
