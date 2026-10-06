# Story 002 — evidence and closeout status

**Current status: Done for the declared functional MVP scope, including the
basic Interface preference follow-up.** Final signed build 155231 has the
default-on “Show timeline thumbnail previews” checkbox in Interface > Playback
behaviour. Native checks covered Save-off/hide, Cancel, restart persistence,
Save-on/display, explicit CLI-off, and ordinary seek with Position title and
volume preserved. See [native preference results](native-preview-preference-final.json),
[build manifest](app-build-preview-preference-final-155231.json) and [local app
update](local-preview-preference-update.json).

The fresh ordinary-control comparison had 20 responses per arm: baseline median
222.039 ms (range 158.141–617.109), feature median 236.531 ms (range
113.493–526.612), +6.527%, within the prospective baseline-median +20%
allowance. See [raw machine-readable results](ordinary-control-preview-preference-final.json).
This approximate shared-host knob-render measure does not establish causal
speedup, p95, completed-seek latency or a general-host guarantee. Precise tail
and causal-stall characterization remain deferred.

The 132643 functional evidence and three valid matched playback pairs remain
dated/inherited; reader/helper/service proof is unchanged. This follow-up did
not repeat preference toggles or reader checks across all four surfaces. The
earlier functional-only Done disposition remains withdrawn history. The previous
[132643 comparison](pragmatic-before-after-validation.md) and its
[machine-readable result](ordinary-control-pragmatic-before-after.json) remain
preserved with their original scope. An earlier frozen-v4 [20% comparison](ordinary-control-shared-load-20pct-inconclusive.json)
remains invalid and unscored. The current [three paired playback runs](playback-cadence-16ms-current-summary.json)
retain their original dropped-frame/audio scope; unattributed repeats and
measured CPU/RSS costs remain disclosed.

## Historical evidence and attempts

The following dated candidate records retain their original policies/verdicts.
The prior closure was subsequently withdrawn; current reopened status above supersedes that disposition while preserving the dated historical record.

**Historical status: InProgress before the revisedMVP closure.**
[132643 16 ms controller](app-build-controller-16ms-experiment-132643.json),
with controller source SHA-256
`47b31fa472d778e0c48b304b6c07cf6e7f7a7a62cade31f42943093f4d093690`. Only the
controller source input differs from prior reversible
[072539](app-build-stable-strip-candidate-072539.json); helper/service/archive
inputs are unchanged. Outputs changed only for VLC, `libmacosx_plugin.dylib`,
and `plugins.dat`. This experiment has no performance qualification and does
not supersede earlier evidence. The
canonical signed [022512 baseline](app-build-tracknumber-022512.json) remains
preserved at `work/build/VLCPreLatency022512.app` with original controller
SHA-256 `f6d88892c4731659340a2d96ede7a61b02f40ed2c9ddf8424ae2853c089bc4cc`.
Neither 072539 nor 132643 is final pending valid baseline comparison and
controls, playback and reader qualification. VLC 3.0.24 pin
`6de05adcbaf2e8b85fe86aad4169393098628119`. Its private FFmpeg 8.1.2
libavformat archive SHA-256 is `93d8acfd4368bb6e0ea9e82a3b8cc5c0a27d1624cb6859bc4e8534c04d035d34`;
only `matroskadec.o` changed from the original across 539 members. The exact app
snapshot was preserved at `work/build/VLCPreLatency022512.app` before candidate
072539 was built. Manifest comparison shows unchanged helper and other unchanged
bundle outputs; differences were limited to the VLC executable,
`libmacosx_plugin.dylib`, and `plugins.dat` built with the controller change.

The signed [035125 ordering-guard build](app-build-window-ordering-035125.json)
is a rejected historical experiment. Root restored 022512 immediately after it;
the later 132643 reversible experiment is summarized above. Its only source
change was the repeated-panel-order guard (order-only reveal/parent/level);
helper output was byte-identical and service/context/geometry/helper inputs
were unchanged. Root removed the guard and restored 022512 after verifying the
controller input hash and every prior manifest output hash. The rejected app is
retained at `work/build/VLCWindowOrdering035125.app`.

## Proven on shared helper input and recorded candidate scopes

- AVC multi-video Matroska correspondence now has a bounded mapping: sorted,
  positive, unique Matroska `TrackNumber` values map to VLC's expected video
  count. A count mismatch, invalid identity, or unsupported mapping fails as
  unavailable. The original and reversed red/blue two-track cases plus a count
  mismatch pass all five checks
  ([mapping results](matroska-track-mapped-contract.json)). This supports the
  tested AVC multi-video MKV case; it does not qualify other codecs/containers.
- The helper input shared by 022512 and the rejected 035125 experiment passes 25 correctness/error cases and 200 standard MP4/MKV
  requests, with p95 32.85/44.12 ms
  ([results](helper-tracknumber-results.json)). The unchanged service count/cache
  isolation and forwarding contract passes 25 non-latency checks
  ([results](service-track-count-cache-contract.json)). A previous full service
  run has 600 settled requests and 26 checks per MP4/MKV container
  ([historical service results](service-tracknumber-results.json)); do not
  treat it as a visible-latency result.
- The final native guard record is from candidate 020311
  ([guard summary](native-final-guards.json)). Three delivered background mouse
  moves produced no new preview demand or panel; reactivation displayed the
  image and leaving the track hid it. A stationary physical pointer at AppKit
  (1000, 22) stayed fixed through a timeline resize from 1680 to 1450 points;
  the requested time changed from 53.7213 to 64.7613 seconds, and the visible
  caption showed 01:05 / Keyframe 1:04. Playback remained paused at zero. AppKit
  emitted tracking enter/move callbacks during layout animation, so the proof is
  about a stationary physical pointer, not a no-mouse-event condition. It is not
  a fresh UI timing cohort for 022512.
- The final mapping CLI review reported no findings. The earlier blanket
  multi-track rejection was a conservative provisional result and is superseded
  only for the AVC MKV fixture covered by the new TrackNumber proof.

## Responsiveness and playback status

Cam approved historical absolute MVP limits of 150 ms p95 for memory and disk
image delivery, 1 s for uncached delivery, and 200 ms for the initial time
caption. The [retrospective rescore](mvp-threshold-rescore.json) preserves the
retained older cohorts and their original 100 ms failures. On 2026-10-05 Cam
directed current qualification to use a measured pre-change baseline or that
baseline plus an explicit percentage allowance. Root selects the baseline
itself for ordinary-control response, with zero added allowance. Vanilla VLC
has no thumbnail feature, so report ordinary input/render response and the
candidate's thumbnail delay separately; the latter is descriptive and has no
vanilla denominator or invented threshold.
Playback CPU/RSS uses matched baseline/candidate deltas with the declared
worker/cache bounds; ordinary-control zero allowance does not imply a zero
resource delta. Current measured costs are about +2 percentage points CPU and
+20–40 MiB RSS, without a harmlessness or global-pass conclusion. The current
repeated-ROI evidence cannot attribute every stall. See the
[resource-contract decision trace](playback-resource-contract-decision-20261005.md).

The first fresh MP4 visible cohort, `continuous-hover-tracknumber-mp4-001`,
exited during template setup because the owned app was inactive. It produced
zero scored requests ([setup record](current-cohort-foreground-setup-failure.json)).
The subsequent 022512 MP4 cohort completed 350 production demands with zero
faults, but missed its historical absolute limits: p95 image/time was 666.165 ms
for miss, 648.142 ms for memory, and 722.136 ms for disk, with captions at the
same values ([cohort report](continuous-tracknumber-mp4-results.json)). No matched
unmodified-VLC baseline exists, so this result does not establish a regression.
The [ordinary-control baseline pilot](ordinary-control-baseline-pilot.json)
validated the measurement setup with 8 samples per arm, but is not p95
qualification. A later [incomplete paired attempt](ordinary-control-baseline-incomplete.json)
collected 25 baseline and 22 feature actions, then stopped because the settled
knob did not match the expected physical point. It establishes neither
qualification nor regression. A later fresh 100-per-arm collection failed
before feature samples; the next step is clean v3 controls, not a retry of that
cohort. Full MKV response timing is also pending.

Before the 035125 controller experiment, a [32-sample observer diagnostic](ordinary-control-observer-diagnostic.json)
completed with zero faults and eight responses per condition. Median ordinary
control response was 288.13 ms baseline / 420.84 ms feature per frame, and
254.70 / 406.04 ms per phase. This supports an added-feature-work hypothesis,
not p95 qualification. The rejected 035125
[window-ordering diagnostic](window-ordering-rejected-diagnostic.json) also
completed with zero faults: per-frame medians were 250.17 ms baseline / 382.47 ms
feature (132.30 ms extra, versus 132.71 ms before); per-phase medians were
242.4 / 362.89 ms. It showed no material relative gain and is not p95
qualification. Independent source review found no issue with the guard, but it
is not retained. Root restored exact 022512 and verified the controller input
hash and every old manifest output hash. No measured gain is claimed.

The later [phase-setup diagnostic](ordinary-control-phase-setup-failure.json)
also stopped before scoring any clicks: its templates failed before the first
`-click-` label. Baseline left/right templates placed the visible knob at 950 / 1090
points. In the feature right template, the exact-PID passive tap recorded the
nonce-tagged move/down/up sequence, and the held AXSlider value changed from
5585.997 to 6651.446; however, 14 complete frames through the 900 ms bound
continued to show the knob at 950. This establishes an accessibility-value
change without a corresponding visible knob update inside this observation
window. It does not establish ignored input, a blocked app, or a latency
regression. Fingerprints were unchanged, both owned apps exited cleanly, and no
profiler ran because setup failed before the first scored-click label.
Instrumented timing landmarks were mousemove about 26.68 ms after input,
context +0.058 ms, hover 50.223 ms after context, RAM service 155.254 ms, and
display 206 ms after mousemove; these are stage observations, not a qualified
latency sample.

The separate [preposition diagnostic](ordinary-control-preposition-diagnostic.json)
completed eight per arm with correct knob positions and medians of 96.8039 ms
baseline / 445.977 ms feature. It is diagnostic only and does not replace the
failed phase setup or qualify a percentile.

A follow-up [independent-capture diagnostic](ordinary-control-independent-capture-diagnostic.json)
did not reproduce the earlier missing visible draw: its feature right movement
updated the knob at 1090 points after 418.4809 ms, and a fresh crop showed the
same position as the retained stream. The wrapper then failed finalization by
calling `cleanup` instead of `close`; root verified the exact owned PID and argv,
quit that app, and confirmed the socket and process were gone. Screenshot timing
metadata was lost, so no screenshot/stream overlap or capture-freshness claim is
made. The report is unqualified, and this attempt will not be rerun.

The bounded [preview-work ablation](ordinary-control-preview-ablation-diagnostic.json)
completed eight responses per arm using the same 042439 diagnostic app,
geometry, fixture and observer; only the `VLC_TIMELINE_DIAGNOSTIC_BYPASS_PREVIEW`
environment flag differed. With preview enabled, median ordinary-control
response was 370.86554 ms (range 241.51–541.56 ms); with preview work bypassed,
it was 253.77404 ms (range 149.65–315.96 ms), a 117.0915 ms median difference.
All 16 responses passed the per-frame ownership, nonce-routed-input, held-AX
and visible-pixel guards. Fresh RC snapshots after every capture remained
paused at media time 50 or 59 seconds. App, observer, media and fixture
fingerprints were unchanged; both arms exited cleanly. This supports an
aggregate contribution from preview work under this observer condition, but
does not identify which bypassed component caused it and is not p95
qualification or baseline-relative acceptance.

The bypass groups metadata/context work, panel presentation and decoder demand;
the helper is unchanged. The experiment is diagnostic-only and changes no
shipping product source. The 042439 app manifest remains the exact provenance
record. Source and every prior 022512 manifest output were restored and verified
unchanged; 022512 remained the runtime at that point. The next reversible
candidate was 072539; the later 132643 controller experiment is recorded at
the top. Profiler stacks now provide
a component-level attribution lead. The later 050009 notification-coalescing
experiment was incomplete and not retained; its setup failures and stop decision
are detailed below. The baseline-only zero-added-allowance target remains
unchanged, as do separate MKV response timing and other closeout gates. Story
002 remains In Progress.

The first actual-VLC profiler attempt failed at setup. Its partial
recording-options JSON failed when xctrace tried to load it (return code 57);
the recording-start notifier timed out after 15 seconds. The owned VLC was
cleaned up with exit 0 and source/app fingerprints were unchanged. This is an
options setup failure, not evidence that xctrace is unavailable, and it yielded
no usable stacks or profiling-latency result
([failure record](ordinary-control-profiler-options-setup-failure.json)).
Local `--show-recording-options` output established option availability only;
it did not validate the supplied JSON payload.

A subsequent [full-schema preflight](profiler-full-options-preflight.json) used
the generated seven-key configuration
([options](profiler-full-recording-options.json)) on a newly owned idle Python
process, not VLC. The 100 ms `xctrace record` exited 0 and reported that the
recording was saved ([stdout](profiler-full-options-preflight.stdout)); its
owned child was then terminated with status -15. This proves loader acceptance
for that schema and invocation, not useful stack capture or VLC behavior. Apple
documents generating option JSON with `--show-recording-options` and passing a
modified full JSON file with `--recording-options` in the [Xcode 27 release
notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes).
After that preflight, one exact-PID VLC transition produced interpretable
Time Profiler data ([main-stack applicability](ordinary-control-profiler-main-stack-applicability.json)).
The recording exported 1,394 rows, with 214 main-thread rows and 213 carrying
backtraces. The single instrumented input-to-visible transition took 350.36 ms;
this is a profiling observation, not a latency estimate or acceptance result.
The preview path includes `updatePreview` → `NSTextField.setStringValue` → view
invalidation → display-cycle/Core Animation commit work → an unfair-lock wait;
the sample-interval attribution was 163.29 ms. A separate accessibility-window
ordering path waited in SkyLight transactions, with 122.95 ms of sample weight.
These are sampled stack weights, not CPU durations or proven continuous waits.

A clean-environment [paired profiler diagnostic](ordinary-control-clean-profiler-pair.json)
then recorded one transition per arm: 433.88 ms enabled and 73.69 ms bypassed.
The enabled stack includes `NSWindow _setFrameCommon` fence/backing-store
waiting under `updatePreview` called from `mouseMoved`. The one-pair timing is
not an effect estimate, p95, or baseline comparison. It does support a focused
source-attribution experiment around repeated synchronous preview-window
positioning; it does not demonstrate that `setFrameOrigin` is faster or select
a fix.

The 050009 coalescing candidate is historical and not retained. Root built it
to coalesce repeated window-position updates by notification name and sender
using `NSPostASAP`; the source is archived at
`work/validation/story002/coalescing-source-050009.m`. The 5-valid-sample
[first diagnostic](ordinary-control-coalescing-setup-failure.json) and
20-valid-sample [repeat](ordinary-control-coalescing-repeat-setup-failure.json)
both ended with foreground ownership false, so neither is a completed response
comparison. In the repeat, feature phase click000 kept the crop-containment
guard true; a passive exact-PID tap saw move/down/up. At +877 ms the collapsed
app-active guard (owned-process existence, expected bundle ID and active state)
read false. About 60 ms later, owned-process and held-AX checks succeeded. The
cause of the guard result is unknown; these facts do not establish a coalescing
effect, ignored input, a foreign foreground app, or a product defect. Root's source review found no source
defect, while `NSPostASAP` provides no click-priority guarantee. The loop review
directed stopping retries. The [050009 manifest](app-build-coalescing-050009.json)
and both reports remain preserved; the original controller was restored and
every 022512 bundle output hash verified. No queue change is retained; current
production remains exact restored 022512 and the baseline-only zero-added-
allowance target remains unchanged.

The current 350-demand descriptive MKV cohort,
`continuous-hover-tracknumber-mkv-001` (session 20683), stopped during template
setup at bucket 85 after six valid templates and before any scored request. Its
setup record classified the frame as inactive or the crop as owned by another
main window ([record](current-mkv-cohort-foreground-setup-failure.json)). The
022512 source, app and test inputs were unchanged. This is the third foreground-
ownership setup failure overall; unlike the preceding two coalescing-run
failures, this one occurred on the stable original single-app path. Its cause
remains unknown. It is not
a completed MKV response cohort and provides no performance result. UI
performance metrics remain paused. Root continues bounded guarded setup and
applicability diagnostics under existing UI authorization; the optional idle-
desktop question remains unanswered and is not a blocker. Story 002 remains In
Progress.

While response metrics remain paused, two isolated stable-strip prototypes were
built and signed: [061652](app-build-stable-strip-prototype-061652.json) and
[061929](app-build-stable-strip-prototype-061929.json). Review corrected the
host union from the knob-center inset to the full hover-range endpoints after
finding a possible gutter clip; this was not reproduced in UI. The corrected
prototype uses a transparent wide panel and moves its card view within the
panel, setting host-window geometry only when needed. The [read-only recorder
preflight](foreground-recorder-readonly-preflight.json) proves startup/run-loop
applicability only, not notification delivery or transition capture. After each
build, root restored canonical 022512 source/runtime and verified bundle hashes;
no product or performance result is claimed. Endpoints, all four surfaces,
clear/hide, stacking, resource use and a matched ordinary-control comparison
remain unproved. UI performance metrics remain paused while root continues
bounded guarded applicability diagnostics under existing authorization.

The follow-on [original-app applicability run](ordinary-control-foreground-applicability.json)
completed six interactions with stable single-app ownership and proved actual
target activation-notification delivery. It supports the observer's applicable
notification path, not a cause for prior setup failures or any timing result.
The [first endpoint diagnostic](stable-strip-main-coordinate-diagnostic.json)
used x=1537, outside the measured slider endpoint: the AppKit bounds were
1328×14 from x=208, so the first pixel was x=209/local0 and the last included
pixel x=1536; AX reported width1330 including alignment padding. Its failure is
a harness-coordinate exclusion, not a product defect. The corrected six-move
[visual result](stable-strip-main-visual-results.json) passed left, middle,
right x=1536, return, leave and re-enter with stable host identity/bounds,
hide/reveal and paused time zero. Root's PNG review saw the middle/right
captions and clearing; captures include the owned parent+child window group,
not an isolated panel.

The [matched-control attempt](stable-strip-control-comparison-setup-failure.json)
failed during baseline template-right with zero scored samples. Its collapsed
ownership guard read false at 941770.821 while crop containment and post-owned
checks were true; an independent activation receipt occurred at 941760.464, and
no event arrived before cleanup at 941771.310. This absence does not prove no
underlying transition and does not waive ownership checks. A separate six-
interaction [guard-components applicability run](ordinary-control-guard-components-applicability.json)
passed without reproducing the transient guard failure; its original wrapper
had a post-analysis `KeyError`, and its query-end timestamp precedes getter
completion. A 10 ms sampler recorded 5,996 observations (median cadence 10.03 ms,
maximum 19.84 ms), without reproducing the failure. These applicability results
are not latency qualification. The guard discrepancy and prior failure cause
remain unresolved. The bounded [NSWorkspace launch pilot](workspace-launch-pilot-setup-failure.json)
returned the exact expected argv/PID but failed before any capture: RC reported
`stop`, time zero and empty counters. Its cleanup adapter reported an ownership
mismatch; a separate 07:01 `ps` check found the PID absent, with exact exit
status unavailable. Source inspection found VLC forwards remaining launch
arguments and filters duplicate command-line media; environment/cwd differences
remain unproved. The 07:03 stop rule abandoned this route: no concrete defect
was established, so there is no rerun or cause claim. Subsequent detached and
fullscreen checks are summarized in the [four-surface visual record](stable-strip-four-surface-visual-applicability.json):
detached passed six visual-applicability actions; two initial custom-fullscreen
left-endpoint attempts found no host, followed by seeded custom/native sequences
that passed visibility, stable-host and clearing checks. This establishes
four-surface visual applicability only. Fullscreen first-entry reliability,
resize, playing-media behavior, playback/control, accessibility, resources and
performance remain unqualified. The initial fullscreen failure cause remains
unknown. At that point canonical 022512 remained current and no prototype was
retained; the later reversible 072539 candidate is recorded at the top. Story
002 remains In Progress.

The subsequent [runloop-observer attempt](ordinary-control-runloop-observer-setup-failure.json)
also stopped before scoring: the revised 1 ms no-op-timer observer passed its
five-pixel self-test, but the first baseline template failed before the planned
negative attempt, leaving zero qualified samples. At t0+0.302s it recorded
`display_frame` index17/status1 while the collapsed target-app guard read false
and crop/AX ownership were true; tagged routing and after-owned checks also
passed. An independent collector recorded target activation but no transition
before cleanup; absence is not causal proof. Review found unexercised latent
negative-harness issues (frame-kind mismatch and missing independent negative
interval). Inputs and canonical 022512 remained unchanged. This is no fix, no
latency gain and no response qualification. A subsequent bounded left-only
split-component/frontmost-snapshot classification run 002 passed without
reproducing the prior guard discrepancy; root stopped further classification
runs.

The prospective v2 foreground policy is recorded in the [control contract
applicability summary](control-frontmost-v2-001-contract-applicability.json).
Four positive controls produced 696 callbacks with zero failures or legacy
disagreements; a deliberate Finder interval was rejected using two frames with
PID759 / `com.apple.finder`, independent activation/deactivation notifications,
and successful actions. The negative probe exited1 as expected; its five-pixel
self-test passed. V2 keys foreground evidence on PID plus bundle while keeping
process/object/CG AX/crop/pixel/nonce guards. The active/visible policy remains
distinct and prospective; no earlier failure is waived or explained. Frozen v1
probe and trial sources are preserved in `work/validation/story002/`.

The prior [072539 manifest](app-build-stable-strip-candidate-072539.json)
records the reversible candidate used for the initial 100-per-arm comparison.
That attempt stopped at baseline click010 after 10 baseline observations and 0
feature observations because the observer received no complete presentation
frame ([incomplete-cohort record](ordinary-control-frontmost-strip-001-incomplete.json)).
Input routing and ownership checks passed, but three callbacks were idle and no
response could be scored. The cohort is invalid: no partial result is salvaged,
and it is not evidence of candidate failure or a latency result. The recorded
idle AX-query times motivate an observer-backpressure hypothesis only. Apple
ScreenCaptureKit guidance processes complete frames and treats idle callbacks
as having no new frame ([status](https://developer.apple.com/documentation/screencapturekit/scframestatus/complete),
[capture flow](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos)).
A v3 observer policy has now passed prospective strong review and is implemented
in the observer and trial runner: expensive AX checks run only on
`SCFrameStatusComplete`, while frontmost/CGWindow/crop guards remain on every
callback; idle AX state is null/unmeasured, and phases remain separate and
unqualified. The five-case pixel self-test and Python compile pass. Frozen v2
sources are retained. The first v3 qualification attempt failed before capture
geometry when the independent collector observed Codex foreground transitions
during setup. Cam later confirmed mouse/keyboard use during those transitions,
then finished; this contextualizes that actual focus change only and does not
explain earlier unexplained false-guard observations. See the
[v3 setup-failure record](ordinary-control-complete-frame-v3-setup-failure.json).
This provides no UI qualification and no candidate/performance result. The v2
headless replay was rejected for version mismatch and is not v3 evidence. Root's
13:09 loop review records the 07:03→13:09 review gap; no hourly-compliance claim
is made. The subsequent clean v3 applicability run passed four positive
controls with zero faults and independently corroborated the known Finder
negative, which the probe rejected as expected
([control record](ordinary-control-complete-frame-v3-controls.json)). The
balanced eight-per-arm method pilot ended as an invalid, incomplete cohort:
four baseline and five feature observations, stopping on feature
`round-02-per-frame-click-001` because the requested right knob at x=1090 was
not visible in the pixels (the center remained x=950). Input routing, ownership
and an AX value change passed, but the required pixel response was absent. The
[failure record](ordinary-control-complete-strip-pilot-setup-failure.json)
preserves the exact scope; no partial p95, effect estimate or acceptance result
is reported. After that pilot, root built experimental
[132643](app-build-controller-16ms-experiment-132643.json) with controller
SHA-256 `47b31fa472d778e0c48b304b6c07cf6e7f7a7a62cade31f42943093f4d093690`.
Against 072539, only that controller input differs; helper/service/archive
inputs are unchanged and expected app outputs differ. This is not performance
qualified, and the pilot did not run this build. A separate 16 ms method pilot
on 132643 then completed eight responses per arm with no faults and unchanged
fingerprints; descriptive ranges were 245.5–367.4 ms baseline and 241.8–385.2 ms
feature. This is method-pilot evidence, not p95 or effect qualification
([summary](ordinary-control-16ms-method-pilot.json)). The fresh formal
100-per-arm comparison using v3, 900 ms, and zero added allowance ended invalid
at 61 valid baseline and 75 valid feature observations (baseline action 62
triggered the guard failure). One idle callback reported the per-PID app object
missing while an independent foreground query still identified the expected
VLC PID/bundle and the parent crop remained contained; no pixels were available.
The archived [failure record](ordinary-control-16ms-formal-setup-failure.json)
preserves this without assigning a product cause. No partial comparison, p95,
effect estimate or acceptance result is reported.

The 132643 candidate-specific [surface summary](cadence-16ms-surface-applicability.json)
records main-window, detached and native physical-hover/clear applicability in
their bounded scopes; the detached host ID did not survive resize. Custom first
entry remained incomplete (zero hosts at the first five points, host returned
after leave/reentry), and is still under investigation. Do not claim a four-
surface pass or latency acceptance from these checks.
The separate detached
resize004 setup missed its expected host after aspect correction changed actual
height to743 (not requested850), moving the bar y1028→921 while the pointer
remained outside. The preview correctly hid; this is not a defect reproduction.
Do not retain or finalize the 072539 or 132643 candidates until a valid matched
comparison and required controls/playback/reader proofs pass.

The current native selected-track result passes all four original/reversed MKV
menu checks: Track 1 red and Track 2 blue with expected TrackNumbers and
keyframe-zero captions; the reversed fixture remained paused at zero. Both
sources were preserved ([native result](native-selected-track-results.json)).
The multi-program TS displays Preview unavailable, stays paused at zero and
preserves source; the installed helper returns `ambiguous_track_mapping`
([native result](native-program-unavailable-results.json)). The native service
diagnostic differs (`malformed-reply`), so exact error classification remains
unproven. These behavior proofs do not establish latency.

The last three-pair playback, controls, and four-surface reader evidence belongs
to the earlier 012354 original-presentation candidate
([playback](playback-original-presentation-restored-results.json),
[controls](controls-original-presentation-restored.json),
[reader](voiceover-restored-remaining-surfaces.json)). Root is resolving the
proportional selected-track/geometry playback checks for the new mapping path.
No new three-pair result is claimed for 022512.

## Historical remaining closeout before the shared-load revision

- The 132643 candidate now has bounded visual applicability across main,
  detached, native fullscreen and the later alpha-ready custom fullscreen
  entry. The earlier custom no-host attempt remains historical with cause
  unknown. Focused main-window reader/control checks also pass in their recorded
  scope; no four-surface reader result is claimed. See the [current
  applicability record](cadence-16ms-current-applicability.json).
- A focused MP4-to-MKV transition check passed generation and stale-preview
  behavior and displayed two correct MKV keyframes. It did not test a sub-16 ms
  movement interval, produce a full MKV response cohort, or qualify latency
  ([record](cadence-16ms-cancel-mkv-applicability.json)).
- A separate same-process burst covered six delivered intervals below 16 ms;
  hide followed the last delivered timeline event by 9.134 ms, within the
  pending interval, with no display before the MKV switch. This
  is focused pending-hide/cancellation proof, not a latency result or a full MKV
  response cohort ([record](cadence-16ms-single-process-burst-applicability.json)).
- Ordinary-control matched-baseline latency remains unqualified. Playback
  stall attribution remains unresolved; the repeated-ROI evidence cannot
  attribute every stall. Keep no-unintended-seek/pause/audio interruption,
  <=100 ms feature-attributable-stall, and <=1 percentage-point dropped-rate
  gates open.
- Keep Story 002 In Progress. Resource comparison reports matched CPU/RSS
  deltas against declared worker/cache bounds; ordinary-control zero allowance
  does not imply a zero resource delta. See the
  [resource-contract decision trace](playback-resource-contract-decision-20261005.md).

Multiple programs remain explicitly unavailable: a local menu ordinal is not a
file-global track identity. Negative Matroska origins, ordered editions, broad
codec/platform compatibility, and public binary distribution remain
unqualified or deferred. The configured VLC suite remains 51 pass, 1 skip, and
1 baseline-reproduced TLS failure ([suite record](upstream-tests.json)).
