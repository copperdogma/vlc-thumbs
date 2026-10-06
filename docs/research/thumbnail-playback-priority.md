# Thumbnail work and playback priority — 2026-10-04

Problem class: speculative image extraction shares CPU/IO with deadline-sensitive playback under variable host load. Do not attribute a paired outlier to extraction without checking observer/load and scheduling.

## 2026-10-05 closeout contract correction

An hourly review corrected an unsupported extension of the ordinary-control
baseline policy. Zero added allowance applies to ordinary-control response;
playback CPU/RSS must be reported as a matched baseline/candidate delta and
judged against the declared worker/cache bounds. The current reported cost is
about +2 percentage points CPU and +20–40 MiB RSS. Keep this cost visible; it
does not establish harmlessness or a global pass. The current repeated-ROI
evidence cannot attribute every stall, so retain the no-feature-attributable-
stall-over-100-ms requirement and the <=1 percentage-point dropped-frame-rate
increase gate, along with no unintended seek, pause or audio interruption.
Decision details are in the [Story 002 resource-contract trace](../evidence/story-002/playback-resource-contract-decision-20261005.md).

Three matched 60-second baseline/feature pairs completed with identical source, settings, ROI and geometry. Displayed-plus-lost denominator gives increases 0.556, 0.500 and 3.111 percentage points. The third exceeds the proposed one-point limit; the gate remains failed. Baseline itself varies about 6–12% lost pictures. All six captures show no interior low-tone intervals or audio PTS discontinuities. Video repeat candidates exist in both arms, and capture gaps limit precise stall attribution. Full raw/report evidence remains under work/validation/story002/playback-analysis.json; the earlier collector timeout is excluded and retained diagnostically.

Apple's [task-priority guidance](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/power_efficiency_guidelines_osx/PrioritizeWorkAtTheTaskLevel.html) distinguishes QoS classes and their CPU/IO scheduling. [NSTask qualityOfService](https://developer.apple.com/documentation/foundation/process/qualityofservice?language=objc) sets the default priority of process operations and is selected before launch. Current queue/process had no explicit QoS; helper decoding already uses one thread and keyframes.

Decision, before further scored runs: explicitly assign Utility to both service queue and helper process. Utility keeps visible awaited previews responsive while yielding resources; Background risks the cold-preview budget. This is a scheduling experiment, not a demonstrated cause/fix for the outlier. Repeat the existing playback and native latency contracts on the rebuilt candidate. Diagnostics are developer-only and add candidate-only tracing/monitors; a production-path comparison should distinguish that overhead rather than claim it is normal playback cost.

Native MP4 timing attempt001 retained all350 demands. One supposed miss was a RAM hit because the persistent pointer hovered during startup before calibration. This invalidates that cache condition. Correct setup through ordinary media reopen after moving outside the track, creating a fresh generation; do not clear caches or hide the outcome. Native assignment timing is separate from compositor visibility, checked through actual image captures.

Follow-up experiment declaration, 18:11 UTC: rebuilt Utility candidate manifest app-build-20261004T180947.097865Z.json. Compare one fresh matched 60s pair with opt-in timeline diagnostics disabled in both arms (production path), retaining observer/pointer/resource settings. This jointly changes scheduling and removes tracing, so it cannot isolate their individual causal effects. If within the unchanged one-point gate, complete two further counterbalanced pairs; if outside, investigate before adding samples. Actual preview delivery/correspondence and latency remain separate instrumented native trials. Before-Utility analysis is preserved as playback-analysis-before-utility.json, including the failed third pair; no result is erased.

19:43 UTC follow-up: the selected production-path cohort now has three exact-geometry matched pairs. Pair2 was repeated because the prior recorded window height differed by one point; its old results remain diagnostics. Selected displayed-plus-lost increases are +0.1366, -1.1521 and -8.0783 percentage points, each inside the unchanged one-point limit. Audio has no interior low-tone interval or PTS discontinuity. The counter gate is numerically satisfied; it does not prove the strict stall criterion. Selected SCK unchanged-ROI candidates reach0.518/1.347/0.631s in the feature arms and also occur in baseline. Current investigation targets whether backing-surface capture represents actual screen changes, using standard display-space capture rather than further profiling retries. See playback-analysis-geometry-fixed.json.

Continuous display observer applicability (2026-10-04 20:29 UTC): nine-second owned display crop follows moving counter, deliberate pause and resume. Interior phases have147/89/147 frames,63/1/62 distinct hashes, max callback gaps below24ms, max frame PTS gap34ms; all frames carry WindowServer displayTime. No IO/capture error. First paired60s baseline collection kept continuous data through the active interval but exited with an already-stopped stream error at shutdown; preserve as diagnostic, no qualified pair. Existing observer overwrote delegate error with stopCapture error, losing possible causal evidence. Primary Apple documentation distinguishes [already-stopped state](https://developer.apple.com/documentation/screencapturekit/scstreamerror/code/attempttostopstreamstate) from [delegate stop causes](https://developer.apple.com/documentation/screencapturekit/scstreamdelegate/stream(_:didstopwitherror:)); next small dual-stream pilot records every origin/domain/code/time and keeps first cause. Do not suppress errors or relax gates based on apparent frame coverage.


## 2026-10-04 19:20 MDT — new paired playback intervals

Problem class: variable performance measurements with a potentially perturbing
observer; do not attribute a captured repeated image to one code change without
controlled comparison. Current drawing-only candidate's first two feature runs
have interior unchanged-counter intervals of117–133ms, while their baseline
runs show only EOF repeats. Retain all outcomes; audio continuity and acceptable
dropped-frame deltas alone do not settle the visual stall gate.

Primary sources: [Google Benchmark random interleaving](https://github.com/google/benchmark/blob/main/docs/random_interleaving.md)
recommends interleaved repetitions to reduce run-to-run variance;
[Apple SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
distinguishes complete generated frames from idle display samples.
Adopt controlled order/replication for any follow-up attribution; retain stream
status, timing and original captures. No change to the existing three-pair
acceptance protocol mid-run. Finish it first, inspect actual frame/status
records and EOF, then decide whether the provisional drawing change should be
rejected or tested in a bounded balanced comparison. Capture correctness does
not itself establish a causal feature regression or an unaffected playback pass.
No speculative production change or new profiler retry is warranted now.
