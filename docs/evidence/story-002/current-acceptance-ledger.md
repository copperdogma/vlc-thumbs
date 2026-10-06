# Story 002 — current acceptance ledger

## Current disposition — completed, 2026-10-05

**Story status: Done for the declared functional MVP scope, including the basic
preference follow-up.** Final signed development build 155231 has a default-on
“Show timeline thumbnail previews” checkbox in Interface > Playback behaviour.
Native checks confirmed Save-off writes config 0 and hides previews; Cancel
leaves the setting unchanged; restart retains unchecked state; Save-on displays
a preview; explicit CLI-off suppresses preview events; normal seeking still
changes the slider while preserving its “Position” title and volume. See the
[native preference record](native-preview-preference-final.json),
[build manifest](app-build-preview-preference-final-155231.json), and
[local app update record](local-preview-preference-update.json).

The fresh ordinary-control comparison completed with 20 valid responses per
arm. Baseline median was 222.039 ms (range 158.141–617.109); feature median was
236.531 ms (range 113.493–526.612), a +6.527% median delta within the
prospective baseline-median +20% allowance. See the [machine-readable results](ordinary-control-preview-preference-final.json).
This is an approximate shared-host visible knob-render observation, not causal
speedup, precision p95, completed-seek latency, or a general-host guarantee.
Precise tail latency and causal-stall characterization remain deferred.

The prior 132643 evidence and three valid matched playback pairs remain dated
and inherited; reader/helper/service proof is unchanged. This follow-up did not
rerun preference toggles or reader checks across all four surfaces. Earlier
attempts and the withdrawn premature-closure record remain preserved.

### Dated 132643 functional and comparison evidence

The earlier 132643 records remain valid only for their declared scope. See the
[historical 20-per-arm comparison](pragmatic-before-after-validation.md) and
[machine-readable result](ordinary-control-pragmatic-before-after.json):
baseline median 343.047 ms (range 279.568–487.320), feature median 330.741 ms
(range 233.484–420.992), −3.587%, within the prospective +20% allowance. That
approximate shared-host knob-render observation was not causal speedup, p95,
completed-seek latency, or a general-host guarantee. The prior build's
controls, pending-hide/media-generation cancellation, playback pairs and
source-invariant reader/helper/service checks remain dated evidence rather than
new 155231 reruns. The 132643 manifest and original input hashes remain in its
[build record](app-build-controller-16ms-experiment-132643.json).

The signed 035125 panel-order guard experiment is rejected and historical
([manifest](app-build-window-ordering-035125.json),
[diagnostic](window-ordering-rejected-diagnostic.json)); the source guard was
removed and its helper output had been byte-identical to 022512.

Historical policy (superseded for current completion): the earlier shared-load
approach used a 20% p95 allowance, at least 100 responses per arm and a four-
block baseline variability screen. Preserve its attempts and conclusions as
history. The required comparison followed the pragmatic median protocol in the current
disposition above; the two protocols must not be conflated. Functional MVP
acceptance is separate from precise latency qualification. Inconclusive shared-host comparison and repeated
observations present in both arms without attribution are disclosed nonblocking
performance characterization for MVP; they do not establish “no stalls” or a
performance pass. Reproducible feature-attributable stalls remain defects.
The previously approved 150/150/1000/200 ms absolute thresholds remain a
versioned historical contract, not a regression attribution rule. The old
MP4/MKV rescore applies only to its recorded inputs.

The single authorized frozen-v4 shared-load 20% comparison ended invalid at
25 baseline / 48 feature responses when the expected feature knob was absent
at feature round 01 click 023: the complete frame remained at x=950 while AX
value changed from 5585.997 to 6651.446, with routed input and ownership valid.
Input fingerprints were unchanged and integrity was true. No partial quantile
is salvaged and no retry is authorized by this bounded lane. The archived
[inconclusive result](ordinary-control-shared-load-20pct-inconclusive.json)
records 30 load samples (1-minute load 12.17–18.94) and summed process CPU of
610–965% (multiple-core process units, including VLC and apparatus; not machine
utilization). This supports uncontrolled-load context only, not a causal
performance conclusion. Precise qualification is deferred as nonblocking MVP
characterization pending an appropriate quiet-window run.

The hourly review corrected an overextension of the ordinary-control rule:
CPU/RSS playback resources use matched baseline/candidate deltas, not a zero-
delta requirement. Acceptance uses the already declared worker/cache bounds and
the playback-integrity criteria in the root contract. Current measured costs
are approximately +2 percentage points CPU and +20–40 MiB RSS; record them as
costs, not as harmless or as a global pass. Repeated-ROI evidence cannot
attribute every stall, so the no-feature-attributable-stall-over-100-ms gate
remains unqualified as explicit nonblocking characterization for theMVP. See the [resource-contract decision trace](playback-resource-contract-decision-20261005.md).

That build uses a private FFmpeg 8.1.2 libavformat archive with SHA-256
`93d8acfd4368bb6e0ea9e82a3b8cc5c0a27d1624cb6859bc4e8534c04d035d34`, recorded
in the build manifest. Only `matroskadec.o` changed among 539 archive objects;
original VLC source and linked VLC libraries remain unchanged.

## Current functional acceptance

The declared functional criteria are supported by the
[findings-first acceptance review](shared-load-acceptance-review.md), which maps
current observations and source-invariant inherited proof separately. Current
[three-pair playback](playback-cadence-16ms-current-summary.json) meets the<=1pp
dropped-frame allowance for every pair; all six runs preserve source hashes,
80 physical pointer moves and zero interior digital-audio gaps. Unattributed
repeated imagery in both arms remains disclosed, without claiming no stalls.
The final preference follow-up verifies save/cancel/restart and regular seek
behavior on its tested main-window surface. Earlier native controls/main-reader
proof supplements inherited AX/focus ownership and four-surface reader
observations. This is not a fresh four-surface reader rerun. Fully visible
custom-entry proof is the declared scope; the earlier unknown no-host attempt
is retained below.

Decoder/service/context/geometry source and bundled helper match the tested
inputs. Thus correspondence, selected-track, bounds and fault/cache contracts
are reused in their recorded scope. Ordinary-control precision, broad MKV
percentiles, causal-stall characterization and public distribution remain
unqualified/deferred. No actual reproducible feature defect is waived.

## Historical attempt record

The dated candidate attempts below preserve their original policies and
limitations. Status phrases such as “Story 002 remains In Progress” describe
the attempt date only; they do not override the current Done disposition above.

The separate-process [MP4→MKV applicability run](cadence-16ms-cancel-mkv-applicability.json)
had no sub-16 ms intervals, so it did not test timer cancellation below one
cadence. A follow-up same-process burst did: AppKit coalesced 33 posted moves
(32 timeline moves and leave) into seven delivered timeline mouse moves, with
six intervals below 16 ms. Hide followed the last delivered timeline event by
9.134 ms, within the pending 16 ms interval; the RC remained paused at zero, and no later preview appeared
before the MKV switch. The new MKV generation displayed two expected keyframes
with unchanged source integrity ([focused record](cadence-16ms-single-process-burst-applicability.json)).
This closes only that pending-hide/cancellation behavior scope, not a latency
percentile or full MKV response cohort.

**Profiler and source attribution:** the initial VLC recording failed on partial
options JSON (57) and its notifier timed out; a full-schema Python preflight
proved loader acceptance only. A later exact-PID VLC trace passed the
recording/export gates and contained 213 main-thread backtraces. The single
350.36 ms instrumented transition showed display-commit and accessibility
window-ordering waits; sample weights are not CPU durations or a latency
distribution ([main-stack report](ordinary-control-profiler-main-stack-applicability.json)).
A clean-environment paired diagnostic captured one response per arm, 433.88 ms
enabled and 73.69 ms bypassed, with a sampled `NSWindow _setFrameCommon`
fence/backing-store wait under the preview path
([pair](ordinary-control-clean-profiler-pair.json)). This is not an effect or
p95 estimate. The 050009 NSPostASAP name/sender-coalescing candidate is rejected
after incomplete setup runs and is not retained; no `setFrameOrigin` speedup is
demonstrated. These profiler/coalescing results were recorded against the 022512
baseline; the current reversible experiment is 132643 above, and zero-added-
allowance acceptance remains unchanged.

**Current native setup outcomes:** the 050009 coalescing build
([manifest](app-build-coalescing-050009.json)) produced two incomplete ordinary-
control diagnostics: 5 valid observations and 20 valid observations, each
ending with foreground ownership false
([first](ordinary-control-coalescing-setup-failure.json),
[repeat](ordinary-control-coalescing-repeat-setup-failure.json)). In the repeat,
feature phase click000 kept the crop-containment guard true; exact-PID
move/down/up was observed. At +877 ms the collapsed app-active guard (owned
process exists, expected bundle ID and active state) read false; owned/post-held-
AX checks passed about 60 ms later. Cause of the guard result is unknown; this
does not establish an effect, ignored input, a foreign foreground app or a
latency judgment. Review found no source defect but `NSPostASAP` does not guarantee click
priority. Root restored the original controller and verified all 022512 bundle
output hashes; no queue change is retained. The subsequent stable 022512
[descriptive MKV cohort](current-mkv-cohort-foreground-setup-failure.json)
stopped at template bucket85 after six valid templates and zero scored requests.
This is the third foreground-ownership setup failure overall; unlike the two
preceding coalescing-run failures, it occurred on the stable original single-app
path. Cause remains unknown. UI performance metrics are paused while root
continues bounded guarded setup and applicability diagnostics under existing UI
authorization. The optional idle-desktop question remains unanswered and is not
a blocker; Story 002 remains In Progress.

While UI metrics are paused, two isolated signed stable-strip prototypes were
built ([061652](app-build-stable-strip-prototype-061652.json),
[061929](app-build-stable-strip-prototype-061929.json)). Review found the first
host union, based on the knob-center inset, could clip the full hover-range
gutter; a corrected build uses the full `VLCTimelineHoverBounds` endpoints.
This was not reproduced in UI. The transparent panel/card-view geometry and
[read-only recorder preflight](foreground-recorder-readonly-preflight.json)
have no endpoint, four-surface, clearing, stacking, resource or paired-response
proof; preflight confirms startup/run-loop applicability only, not notification
delivery. Canonical 022512 source/runtime and all bundle hashes were restored
after each build. No product change, performance gain, or UI behavior is
claimed. UI performance metrics remain paused while root continues bounded
guarded applicability diagnostics under existing authorization.

The [original-app applicability run](ordinary-control-foreground-applicability.json)
completed six interactions with stable single-app ownership and proved target
activation-notification delivery. It does not identify a cause for the earlier
foreground setup failures and provides no timing result. The first
[stable-strip endpoint diagnostic](stable-strip-main-coordinate-diagnostic.json)
used x=1537, outside the measured slider endpoint: the AppKit bounds were
1328×14 from x=208 (first included pixel x=209/local0; last x=1536), while AX
reported width1330 including alignment padding. This was a harness-coordinate
exclusion. The corrected six-move [visual result](stable-strip-main-visual-results.json)
passed left, middle, right x=1536, return, leave and re-enter with stable host
identity/bounds, hide/reveal and paused time zero. Root's PNG review saw captions
and clearing, with captures from the owned parent+child window group rather than
an isolated panel.

The [matched-control attempt](stable-strip-control-comparison-setup-failure.json)
failed at baseline template-right with zero scored samples. Its collapsed guard
read false at 941770.821 while crop containment and post-owned checks were true;
an independent activation receipt occurred at 941760.464, and no event arrived
before cleanup at 941771.310. Absence here does not prove that no transition
occurred and does not waive ownership. A separate six-interaction [guard
components check](ordinary-control-guard-components-applicability.json) passed
without reproducing the transient failure; its original wrapper had a
post-analysis `KeyError`, and its query-end timestamp precedes getter completion.
A 10 ms sampler recorded 5,996 observations (median cadence 10.03 ms, maximum
19.84 ms), also without reproducing the failure. These applicability checks do
not qualify latency. The guard discrepancy and earlier cause remain unresolved.
The [NSWorkspace launch pilot](workspace-launch-pilot-setup-failure.json)
returned the exact expected argv/PID but stopped before captures because RC
reported `stop` at time zero with empty counters. Its cleanup adapter reported
an ownership mismatch; a separate 07:01 `ps` check found the PID absent, without
an exact exit status. Read-only source review found remaining argv forwarded
and duplicate CLI media filtered; environment/cwd differences were unproved.
At the 07:03 stop review, no concrete defect had been established, so the
NSWorkspace route was abandoned without rerun or cause attribution. Subsequent
detached and seeded custom/native fullscreen checks are summarized in the
[four-surface visual record](stable-strip-four-surface-visual-applicability.json).
They support visual applicability only; the initial custom fullscreen
no-host results remain preserved, and full first-entry reliability, resize,
playing-media, playback/control, accessibility, resources and performance are
still unqualified. At that point original 022512 remained current with no
prototype retained; the later reversible 072539 candidate is recorded above.
Story 002 remains In Progress.

The [runloop-observer diagnostic](ordinary-control-runloop-observer-setup-failure.json)
failed at its first baseline template before the negative attempt, with zero
qualified samples. The revised main-loop pump and 1 ms no-op timer passed five
pixel self-tests, but at t0+0.302s `display_frame` index17/status1 coincided
with a false collapsed target-app guard while crop and AX ownership were true;
routing and after-owned checks passed. A separate activation receipt without a
transition before cleanup is not causal proof. Review identified unexercised
negative-harness limitations: frame versus `display_frame` kind handling and no
independent negative interval. Inputs remained unchanged and no latency result
or fix is established. Root's baseline-left-only split-component/frontmost
snapshot classification run 002 passed without reproducing the prior guard
discrepancy; root stopped further classification runs. The prospective [frontmost-v2
contract applicability](control-frontmost-v2-001-contract-applicability.json)
passed four positive controls (696 callbacks, zero failures and zero legacy
disagreements) and one Finder negative, supported by two exact PID/bundle frames,
activation/deactivation notifications and successful foreground actions. This
validates the prospective observer policy only; no prior failure is waived or
explained, and no latency claim follows. The formal 100-per-arm comparison
stopped during baseline click010 after ten baseline observations and zero
feature observations because three capture callbacks were idle and no complete
presentation could be scored ([incomplete cohort](ordinary-control-frontmost-strip-001-incomplete.json)).
Routing and ownership checks passed; this is an invalid cohort, with no partial
salvage, candidate-failure claim or latency result. Idle AX-query times support
only an observer-backpressure hypothesis. Apple documents filtering for
complete ScreenCaptureKit frames ([status](https://developer.apple.com/documentation/screencapturekit/scframestatus/complete),
[capture flow](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos)).
A v3 observer policy has now passed prospective strong review and is implemented:
AX reads run only on `SCFrameStatusComplete`, while frontmost/CGWindow/crop
guards remain on every callback; idle AX is null/unmeasured and phases remain
separate and unqualified. The five-case pixel self-test and Python compile pass.
Its first qualification attempt stopped before capture geometry after the
independent collector observed Codex foreground transitions during setup. Cam
later confirmed mouse/keyboard use during those transitions, then finished;
this contextualizes that focus change only, not earlier unexplained false-guard
observations ([setup-failure record](ordinary-control-complete-frame-v3-setup-failure.json)).
The clean follow-up passed four positive controls with zero faults and
independently corroborated the known Finder negative, which the probe rejected
as expected ([control record](ordinary-control-complete-frame-v3-controls.json)).
This is observer/control applicability only, not UI feature or performance
qualification. A headless v2 replay was rejected for observer-version mismatch
and does not count as v3 validation.
Root's 13:09 loop review records a 07:03→13:09 gap, without an hourly-compliance
claim. The first eight-per-arm pilot ended invalid at four baseline / five
feature observations: the feature's requested x=1090 knob remained at pixel
center x=950 although input routing, ownership and AX value change passed
([failure](ordinary-control-complete-strip-pilot-setup-failure.json)). No partial
p95 or effect is salvaged. The later 132643 method pilot passed eight responses per arm (16 total)
without faults or input changes; descriptive ranges were 245.5–367.4 ms
baseline and 241.8–385.2 ms feature, not a p95 or acceptance result
([summary](ordinary-control-16ms-method-pilot.json)). The formal 100-per-arm
v3/900 ms/zero-allowance comparison ended invalid at 61 valid baseline and 75
valid feature observations. Baseline action 62 failed because a single idle
callback reported the per-PID app object missing while the independent
foreground query still identified the expected VLC PID/bundle and parent crop
containment; no pixels were available. Cause is unknown; this is no product
regression finding and no comparison, p95 or effect estimate is salvaged
([record](ordinary-control-16ms-formal-setup-failure.json)).

Candidate-specific 132643 [surface applicability](cadence-16ms-surface-applicability.json)
records bounded main-window, detached, native and prepared alpha-ready custom
first-entry physical-hover/clear evidence; the detached host ID did not survive
resize. The prepared custom scope passed after the earlier no-host attempt; keep
that failure and its unknown cause as history, and do not infer general
first-entry reliability from the scoped pass. Do not claim a four-surface
reader/accessibility pass or infer the formal guard failure from these UI
results. The separate earlier detached resize004 missed the
expected host after aspect correction changed actual height to743 versus850 and
moved the bar y1028→921 while the pointer stayed outside; it correctly hid and
does not establish a feature defect. Candidates 072539 and experimental 132643
remain reversible, not final, pending valid matched baseline, controls, playback
and reader checks.

The configured VLC suite remains 51 pass, 1 skip and 1 baseline-reproduced TLS
failure ([suite record](upstream-tests.json)); it is not a green suite and does
not exercise the native GUI. The old blanket multi-track rejection describes a
superseded candidate; the current mapping extends support only to the declared
AVC multi-video MKV fixtures. Story 003 and the integrated root evaluation
remain separate. Do not mark Story 002 done while current latency and selected
path closeout checks are pending.
