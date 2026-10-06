# Native response delays under changing system load

2026-10-04. Problem class: end-to-end UI latency spans input delivery, asynchronous worker scheduling, main-thread UI work and WindowServer presentation. A correct cache hit can still appear slowly; one system CPU snapshot cannot identify the cause.

Primary guidance: [Apple — Analyze hangs with Instruments (WWDC23)](https://developer.apple.com/videos/play/wwdc2023/10248/) distinguishes busy, asynchronous and blocked-main-thread hangs and explains the input/render-server/display pipeline. [Improving app responsiveness](https://developer.apple.com/documentation/xcode/improving-app-responsiveness) recommends inspecting main-run-loop work and scheduling before optimizing. The latter search extract was available but the main HTML requires JavaScript; the video transcript was read directly.

Local observation: the full 022512 MP4 cohort `continuous-hover-tracknumber-mp4-002` remains fault-free during collection but cache-hit display delays exceed the approved 150ms target. Its first memory request records service elapsed121.61ms, controller elapsed154.29ms and literal visible image/time366.17ms. These timestamps have different starts; they are stage clues rather than directly subtractable execution times. Service elapsed is computed in the main-queue completion, so it includes worker work/scheduling and main-queue delivery delay, rather than timing RAM lookup alone. The earlier approved cohort rescore remains historical and cannot qualify this changed candidate.

A read-only snapshot during memory work showed WindowServer101.7%, VirtualMachine101%, mds_stores77.5%, coreaudiod60.2% and other active OS services. AC power was100% and `pmset` reported no recorded thermal/performance warning. A second bounded snapshot is retained at `work/validation/story002/continuous-hover-tracknumber-mp4-002/system-context.json`. No unrelated processes or power/indexing settings were changed. CPU contention is a hypothesis, not proven causation.

Decision: finish and retain the complete failing cohort before adapting. Use existing input/context/service/display/WindowServer timestamps to locate delay classes. Complete selected-track correctness UI checks while conditions may settle, then choose a small unchanged-candidate diagnostic before another full cohort or any tuning. Preserve thresholds and physical-pointer/owned-window proof; do not subtract observer overhead or replace visible latency with a service metric. No runtime change follows from this snapshot alone.

Remaining uncertainty: whether host load, observer workload, app scheduling, rendering or a new source path explains the changed distribution. Main-thread and render-stage diagnosis remains needed; no successful qualification claimed here.

## Baseline setup and visual-oracle correction

Cam requires baseline-relative regression criteria. Vanilla has no preview, so shared ordinary slider-knob response is the denominator; thumbnail wait remains a separate new-capability observation. A10-click unmodified-player pilot shows44–595ms visible feedback with0faults, not a qualification or proof of sole causation.

The first paired setup waited for a new state-transition event from an already paused oldrc interface. Pinned oldrc.c:1194 instead returns its paused marker and terminal status reply. Reuse the established continuous trial's fresh-log-offset plus fresh-statistics plus terminal-reply barrier; a historical state alone cannot pass. The failed setup remains archived with0captures.

The next paired setup found different complete-crop fingerprints while the visible knob remained at its expected position. Whole-frame equality is a stronger appearance contract than the intended position-response metric. Existing snapshot tooling offers tolerant pixel/perceptual comparison ([Point-Free SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing)); [OpenCV image thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) describes segmentation by intensity. No external dependency is added. Adapt the simpler region segmentation principle to the small seek-bar crop, using pinned VLCSliderCell's light-style white/.95-white knob against its .66–.75 gray bar. Recognize a unique bounded white cluster around the measured track centerline, validate independent old/new centers with2point tolerance and140point separation, preserve raw image hashes, and keep actual owned-pixel/display timestamps. This verifies knob location rather than background shade. Applicability is limited to the tested light appearance and2x scale; a failed visual guard remains a failed attempt. Native validation of the revised oracle is pending.

### 2026-10-05 — shared-control measurement pilot and incomplete cohort

Cam confirmed that the response target should be baseline, or baseline plus an
explicit percentage at worst. The current ordinary-control target selects
baseline with zero additional allowance; no positive percentage is inferred.
The independent light-style knob-position oracle passes its five bounded pixel
exercises and actual pilot003 (eight physical clicks per arm). Root inspected
both reference crops; centers match commanded950/1090pt. This is measurement
setup proof, not a percentile qualification.

The first full paired cohort stopped after25baseline and22feature scored clicks.
The next feature click retained the old1090pt knob during the900ms observation
window after a commanded950pt click. Input posting succeeded, but application
receipt and later response are unestablished. All app/media/test fingerprints
were unchanged and owned processes were cleaned up. Raw failed collection is
preserved; it supplies no100-request p95 verdict. The900ms capture duration is
an observation bound, not the user-selected performance target.

A possible observer effect requires checking before performance tuning: the
capture callback calls synchronous accessibility hit testing for every frame,
and preview changes produce more frames than baseline. Apple documents
accessibility messaging timeouts, reinforcing that these calls are external
messages rather than free pixel operations:
https://developer.apple.com/documentation/applicationservices/1459345-axuielementsetmessagingtimeout
Apple's Quartz event documentation describes posting into the event stream;
posting alone is not an application-handling acknowledgement:
https://developer.apple.com/documentation/coregraphics/cgevent/tappostevent%28_%3A%29
These primary sources inform the next diagnostic; neither establishes the
cause of this particular missed movement. Product/player code remains unchanged.

### 2026-10-05 03:29 UTC — bounded course review

An early loop-review after Cam's baseline correction recommends one interpretable
shared-control diagnostic before another full cohort. Existing matched playback
and control demonstrations do not supply the missing response measurement. The
100-request design is a qualification method; repeated observer repair is not
itself a completion criterion. Next experiment freezes the product and compares
both apps with per-frame versus pre/post-only AX queries, eight clicks per
app/observer condition. Both use a predeclared three-second observation window,
exact-PID passive tagged-event receipt, independently measured pixel knob
positions, and retained ownership/state checks. The phase-AX condition is a
diagnostic and cannot silently replace the stronger qualification guards.

Source review corrected the initial query-load assumption: baseline pilot had
51–52 callbacks per attempt, mainly idle; feature15–33 callbacks, mainly complete.
AX queries currently run on every callback, while pixel analysis runs only on
complete frames. Therefore complete-frame count does not establish which app
received more AX work or the sign of any observer effect. The existing20-pair
buffered preview experiment did not improve latency, but covered earlier hover
measurement rather than this new click observer; it is not repeated.

Next decision: classify routed input, accessible slider value and visible knob
for every diagnostic attempt. If another unexplained missing input or ownership
failure appears, stop percentile-cohort retries and resolve that setup event.
If the diagnostic is reliable and feature response is slower under both observer
modes, investigate added feature work rather than raising the baseline target.
No player code or positive percentage allowance is changed by this experiment.

### 2026-10-05 03:38 UTC — routing works; AX phase target correction

Diagnostic001 stopped in the first baseline template with zero scored clicks.
The exact-PID passive tap recorded the three tagged move/down/up events in order;
all per-frame ownership/time checks passed and the retained image shows the knob
at950pt. Post-hit ownership still points to the app, but the hit object's role
is no longer Slider (numeric value5585.997), unlike the pre-hit Slider/value0.
This newly introduced role assumption causes the observer exit, rather than a
VLC response failure. The hypothesis is that the point under the moved knob now
hits a descendant. Next correction retains the original owned Slider reference
for pre/post value queries and separately retains post-hit PID ownership, rather
than requiring a coordinate hit to return the same role before and after moving
a control. Actual role recording will test the descendant hypothesis. The
failed template and all raw routing/pixel rows remain unchanged.

### 2026-10-05 03:45 UTC — held-slider correction locally demonstrated

Fresh diagnostic002's first scored baseline left click records pre point-hit
AXSlider and post point-hit AXValueIndicator. Both belong to the exact owned
app; the retained Slider reference has the same identity/PID/role before and
after, and changes to5585.997 while the independent pixels move1090→950pt.
The passive tap records all three tagged events. This confirms the first
failure's point-hit descendant hypothesis without dropping role/ownership
requirements. The diagnostic is still running; one response does not establish
its overall validity or latency qualification.

### 2026-10-05 03:51 UTC — completed diagnostic and one product experiment

Diagnostic002 completes all32scored clicks, eight per app/observer condition:
all tagged sequences arrive, values/pixels match, zero faults/censored responses,
source/app/probe/pointer inputs unchanged. Median baseline/feature is
288.13/420.84ms with per-frame AX and254.70/406.04ms with phase-only AX. This
supports investigating feature work; removing AX from capture does not explain
the whole difference. Eight per condition remains diagnostic, no p95 claim or
qualification transfer from phase-only ownership. Report:
ordinary-control-observer-diagnostic.json.

Bounded next experiment changes only repetitive preview-window ordering.
Apple's current primary Markdown documentation confirms attached child windows
maintain relative ordering and orderFront changes screen-list order, using the
default window animation unless configured otherwise:
https://developer.apple.com/documentation/appkit/nswindow/addchildwindow(_:ordered:)
https://developer.apple.com/documentation/appkit/nswindow/orderfront(_:)
The current code calls orderFront and sets level on every pointer update.
Order only on reveal/parent/level change; keep geometry/image/helper/QoS/drawing
unchanged. First test the same balanced diagnostic on the resulting candidate
against unmodified VLC. Preserve022512 and its full results; a lower number on
a new build alone does not prove causal attribution. If no material gain,
revert this experiment and investigate before another product tweak.

### 2026-10-05 04:04 UTC — rejected ordering and isolated input diagnostic

Window-ordering experiment035125 completed the same32requests without faults.
Per-frame median baseline/feature250.17/382.47ms leaves132.30ms excess, versus
132.71ms before. The phase-only pair242.40/362.89ms differs, but does not support
qualified gain. Reject the experiment under the predeclared no-material-gain
rule. Controller source and every original022512manifest output SHA were
verified after restoring its preserved app; the experimental app is retained
under owned work. Report: window-ordering-rejected-diagnostic.json.

Next diagnostic changes only input preparation: preposition the physical pointer
at the eventual click point for800ms, then run the existing move/down/up probe
unchanged, eight clicks per arm with strong per-frame guards. This isolates
changed-hover presentation from click response. It is not an assertion that the
preview fully settled and does not replace the simultaneous move-and-click
observations or qualify p95. Old knob readiness still must be independently
correct before every scored click. A small wrapper records all preposition
commands/times and includes its own source hash in before/after fingerprints.
No new product tweak is justified before this comparison.

### 2026-10-05 — preposition result and phase-setup failure

The bounded preposition diagnostic completed eight samples per arm with the
expected knob positions. Median visible response was 96.8039 ms baseline and
445.977 ms feature. It remains diagnostic evidence, not a p95 qualification or
a matched ordinary-response conclusion ([report](../evidence/story-002/ordinary-control-preposition-diagnostic.json)).

A later phase-only AX setup attempt produced zero scored clicks because the
templates failed before the first `-click-` label. Baseline left/right templates
showed the knob at 950 / 1090 points. In the feature right template, the
nonce-tagged move/down/up sequence was observed by the exact-PID passive tap and
the held AXSlider value changed from 5585.997 to 6651.446, while 14 complete
frames through the 900 ms bound continued to show the visible knob at 950.
This supports only the bounded observation that accessibility state changed
without a visible knob update in those frames. It does not show that VLC ignored
input or was blocked, and it does not establish a latency regression. All
fingerprints remained unchanged, both owned apps exited cleanly, and no profiler
was started because setup failed before the first scored-click label.

Recorded landmarks were right mousemove about 26.68 ms after input, context
0.058 ms later, hover 50.223 ms after context, RAM service 155.254 ms, and
display 206 ms after mousemove. They are stage observations from this failed
setup, not a latency sample. Preserve the report
([phase-setup failure](../evidence/story-002/ordinary-control-phase-setup-failure.json));
do not retry the same run without a specific setup correction. The ordinary
response acceptance target remains matched unmodified VLC with zero added
allowance; preview delay remains descriptive and separate.

### 2026-10-05 04:22 UTC — independent draw check and one bounded ablation

Early loop review finds the investigation aligned but at a measurement local
minimum. A separate independent full-display/crop capture was taken before
changing attribution: the feature right movement reached the 1090-point knob
position after 418.4809 ms, and the fresh crop showed 1090, agreeing with the
original stream. The earlier missing-draw observation was not reproduced in
this attempt. Wrapper finalization failed because it called `cleanup` instead of
`close`; root verified the exact owned PID/argv, quit the app, and confirmed no
process or socket remained. Screenshot timing metadata was lost, so the record
cannot establish overlap or freshness relative to the original stream. The
preserved [diagnostic](../evidence/story-002/ordinary-control-independent-capture-diagnostic.json)
is unqualified and will not be rerun.

The next step is one aggregate preview-work ablation, not another observer
refinement or full cohort. A diagnostic-only app adds an environment-gated early
return in `updatePreview`: setting
`VLC_TIMELINE_DIAGNOSTIC_BYPASS_PREVIEW` keeps tracking but bypasses metadata /
context work, panel presentation and decoder demand together; the helper is
unchanged. It cannot attribute those components individually. The planned
eight-per-arm comparison
uses the same diagnostic app, geometry, fixture and observer; the unmodified
baseline arm stays unchanged. Its purpose is causal attribution only, with no
p95 qualification or shipping-source change. The [042439 build manifest](../evidence/story-002/app-build-preview-ablation-042439.json)
records this temporary app. Source was restored to f6d8889 and the prior 022512
manifest outputs were verified exact; at that historical review point the
runtime remained 022512. The later 132643 experimental build is recorded in the
current closeout section below. The comparison was still being prepared at
this review point; its completed result is recorded below. The next hourly
review was scheduled for 05:22 UTC.

### 2026-10-05 — aggregate preview-work ablation completed

The [diagnostic report](../evidence/story-002/ordinary-control-preview-ablation-diagnostic.json)
records eight scored ordinary-control responses per arm on the same diagnostic
app, geometry, fixture and observer; the bypass environment flag was the only
arm difference. All 16 passed the per-frame ownership, exact-PID nonce receipt,
held-slider AX and pixel-position checks, with no faults or censored responses.
Median response was 370.86554 ms with preview enabled (range 241.51–541.56 ms)
and 253.77404 ms with preview work bypassed (range 149.65–315.96 ms), a
117.0915 ms median difference. Fresh RC time/status snapshots after each
capture remained paused at 50 or 59 seconds. The before/after app, observer,
media and fixture fingerprints matched, and both app runs exited cleanly.

This supports an aggregate preview-work contribution under the tested observer
condition. Bypass groups metadata/context work, panel presentation and decoder
demand, so the result does not identify an individual cause. It is neither p95
qualification nor baseline-relative acceptance and does not change the
zero-added-allowance ordinary-response target. It made no shipping product
change: the helper and baseline were unchanged, and the exact 022512 runtime was
restored with all prior manifest output hashes verified. Root's next step is a
read-only component-level causal decision; no specific fix is selected yet.

### 2026-10-05 — profiler options loader preflight

The first actual-VLC Time Profiler attempt failed before recording. The options
file was only a partial JSON fragment; `xctrace record` returned57 with “Failed
to load recording options” because required data was missing. The recording-
started notifier timed out after15seconds. The owned VLC exited0 during
cleanup, with source and app unchanged. Preserve the
[initial failure](../evidence/story-002/ordinary-control-profiler-options-setup-failure.json).
It establishes an invocation/options setup failure only: xctrace was available,
but no profile was recorded and no stacks or latency conclusion are available.

The read-only `--show-recording-options` calls printed option availability but
did not validate payload semantics; partial, malformed and full payload probes
all returned the default successful listing. Apple’s [Xcode27 release
notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
document that this command emits recording options as JSON and that customized
options are passed as a JSON file using `--recording-options`. Adapting that
contract, a fresh [seven-key full-schema configuration](../evidence/story-002/profiler-full-recording-options.json)
with Time Profiler waiting-thread capture enabled was tested on newly owned idle
Python PID37429 for100ms. `xctrace record` returned0 and stdout says the recording
completed and was saved; the child was then terminated with status-15. The
[preflight result](../evidence/story-002/profiler-full-options-preflight.json)
and [stdout](../evidence/story-002/profiler-full-options-preflight.stdout) are
preserved. This proves that the loader accepted this full schema and command on
the idle Python target. It does not prove that a VLC recording produces useful
stacks or classify the UI delay.

Apple’s [Analyze hangs with Instruments (WWDC23)](https://developer.apple.com/videos/play/wwdc2023/10248/)
distinguishes a busy main thread from a blocked one and uses inspected thread
stacks to decide between them. A successful command exit alone is not evidence
of relevant stack rows. The bounded next attempt is one actual VLC transition
using exact-PID attachment and the accepted full configuration, then inspect
whether the expected stack data is present. It was pending at this point; later
applicability and clean-pair results are recorded below. Production 022512
remains restored; the baseline-only response target remains zero added
allowance; Story002 remains In Progress.

### 2026-10-05 — usable stacks and bounded coalescing hypothesis

The exact-PID VLC Time Profiler recording became interpretable after the
full-schema preflight. Its safe [main-stack summary](../evidence/story-002/ordinary-control-profiler-main-stack-applicability.json)
records 1,394 exported rows, 214 main-thread rows and 213 nonempty main-thread
backtraces. One instrumented input-to-visible transition took 350.357 ms. The
preview path runs from `mouseMoved` / `updatePreview` through text-field update,
display-cycle invalidation and Core Animation commit work to an unfair-lock
wait (163.286 ms of sample-interval weight). A separate accessibility-window
ordering path waits through SkyLight transaction work (122.949 ms of sample
weight). These weights reflect sampled intervals, not CPU duration or proven
continuous blocking; one transition does not establish cause. Raw trace TOCs
remain private and were not copied into shared evidence.

A minimal-environment [clean profiler pair](../evidence/story-002/ordinary-control-clean-profiler-pair.json)
contains one profiled response per arm: 433.88 ms enabled and 73.69 ms bypassed.
The enabled preview stack includes `NSWindow _setFrameCommon` fence/backing-
store waiting under `updatePreview` called from `mouseMoved`. The stack provides
a concrete attribution lead, while the single pair's timings are neither a
measured treatment effect nor p95/baseline acceptance. The prior profile is
also one instrumented transition and is not a latency estimate.

The research decision at that review point was to test one name/sender-coalesced notification for repeated
preview-window positioning, posted with `NSPostASAP`. Apple's [current
NSNotificationQueue documentation](https://developer.apple.com/documentation/foundation/notificationqueue)
describes deferred posting and duplicate coalescing; [NSPostASAP](https://developer.apple.com/documentation/foundation/notificationqueue/postingstyle/asap)
posts at the end of the current callout or timer. The [archived Cocoa
Fundamentals guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CocoaFundamentals/CommunicatingWithObjects/CommunicateWithObjects.html)
gives the concrete example of coalescing repeated expensive display-server
flushes with `NSPostASAP` (the guide is retired, so this is historical design
guidance). `NSPostWhenIdle` waits for actual run-loop idleness; under steady
input this can defer the work (inference from that trigger). This supports a
bounded experiment hypothesis, not a result. The experiment and its outcome are recorded below. No improvement is retained or demonstrated. There is no evidence that
`setFrameOrigin` alone improves response. Product source and current signed
022512 remain unchanged, as does the zero-added-allowance baseline target.

### 2026-10-05 — coalescing setup failures and retry stop

The 050009 diagnostic coalescing candidate is historical and was not retained.
The first ordinary-control run had five valid samples; the repeat had twenty.
Both reports ended with foreground ownership false, so neither is a completed
comparison. In the repeat's feature phase at click000, the crop-containment
guard remained true while a passive exact-PID tap observed move/down/up. At
+877 ms the collapsed app-active guard (owned-process existence, expected bundle
ID and active state) read false; about 60 ms later, owned-process and held-AX
checks succeeded. The guard result's cause is unknown. These runs establish no
coalescing effect, ignored input, foreign foreground app, product defect or
latency conclusion. Root's source review found
no source defect, and `NSPostASAP` gives no click-priority guarantee. The 06:03
loop review stopped retries on this path. The candidate source and manifest,
both incomplete diagnostics, and their limitations remain archived.

The original controller was restored and every prior 022512 bundle-output
hash was verified. No notification queue change is retained; current production
is exact restored 022512. The baseline-only ordinary-response target remains
matched unmodified VLC with zero added allowance, while thumbnail delay stays
descriptive.

The stable 022512 `continuous-hover-tracknumber-mkv-001` cohort then stopped
during template setup at bucket85 after six valid templates and zero scored
requests. The [setup-failure record](../evidence/story-002/current-mkv-cohort-foreground-setup-failure.json)
classifies the capture target as inactive or the crop as owned by another main
window; 022512 inputs were unchanged. This is the third foreground-ownership
setup failure overall; unlike the preceding two coalescing-run failures, this
one occurred on the stable original single-app path. Its cause is still unknown. It supplies no MKV
response or performance result. Root paused further UI metrics pending user
guidance on an idle-desktop window or alternate checks. Story 002 remains In
Progress.

### 2026-10-05 — stable-strip geometry prototype while UI metrics are paused

With UI metrics still paused pending the owner's asynchronous idle-state
guidance, a bounded isolated prototype tested a different view-geometry
approach. The first signed build, [061652](../evidence/story-002/app-build-stable-strip-prototype-061652.json),
used the host union of the slider-knob center inset. Review found that this
range could clip the outer gutter at the full hover-range endpoints; that was
a geometry review finding only, not a reproduced UI failure. The corrected
isolated [061929 build](../evidence/story-002/app-build-stable-strip-prototype-061929.json)
uses the full `VLCTimelineHoverBounds` xmin/xmax host union. Both builds used a
transparent wide `NSPanel` with a 336×224 card inside. The panel is attached
above the slider window with `addChildWindow:ordered:`, ignores mouse events,
and has its system shadow disabled; a managed canvas draws the background and
local shadow. The card `NSView` moves within the panel, and the host window
frame is set only when its geometry changes. The ignored
prototype sources remain at `work/validation/story002/stable-strip-source-061652.m`
and `work/validation/story002/stable-strip-source-endpoint-fix.m`.

This adapts the AppKit distinction between changing a view's frame origin and
moving its window: Apple's [`NSView.setFrameOrigin`](https://developer.apple.com/documentation/appkit/nsview/setframeorigin%28_%3A%29)
repositions the view in its superview and does not itself mark the view for
display; [`NSWindow.setFrameOrigin`](https://developer.apple.com/documentation/appkit/nswindow/setframeorigin%28_%3A%29)
moves a window in screen coordinates. [`NSWindow.addChildWindow:ordered:`](https://developer.apple.com/documentation/appkit/nswindow/addchildwindow%28_%3Aordered%3A%29)
maintains relative ordering while attached; [`NSWindow.ignoresMouseEvents`](https://developer.apple.com/documentation/appkit/nswindow/ignoresmouseevents)
makes the panel transparent to mouse events. The prototype disables
[`NSWindow.hasShadow`](https://developer.apple.com/documentation/appkit/nswindow/hasshadow)
and draws the card shadow locally; Apple notes that changing `hasShadow`
invalidates and recomputes the system window shadow. The preview canvas uses
[`NSView.wantsLayer`](https://developer.apple.com/documentation/appkit/nsview/wantslayer)
for managed layer-backed drawing. These APIs describe mechanics, not a
performance guarantee. The geometric hypothesis is that keeping the host
window stable while moving the card view may avoid repeated window positioning;
there is no measured gain or UI behavior result.

Both prototypes were isolated and signed. After each build, root restored the
canonical 022512 source/runtime and verified all bundle hashes; no production
change was retained. A three-second [read-only foreground-recorder preflight](../evidence/story-002/foreground-recorder-readonly-preflight.json)
produced two ready/final rows and exited0, but proved only startup/run-loop
applicability: it induced no transition, called no activation API, and did not
prove notification delivery. No UI, endpoint, stacking, four-surface clearing,
resource, or ordinary-control paired proof exists for the strip prototype.
Before any retention decision, those behaviors and a matched ordinary-control
comparison would need evidence. Observer ownership, crop, and geometry changes
are appropriate only if this prototype first proves useful. UI metrics remain
paused; this diagnostic work does not mark Story 002 done or blocked.

### 2026-10-05 — bounded activation, visual and guard applicability

The original 022512 single-app path now has one valid [foreground-applicability
run](../evidence/story-002/ordinary-control-foreground-applicability.json): six
interactions completed with stable ownership and six target activation receipts.
This proves notification delivery in that run; it does not attribute any prior
foreground-guard failure.

The first 061929 endpoint attempt was invalid because it moved to x=1537. Actual
AppKit slider bounds were x=208, width1328, height14, so the first included
pixel was x=209/local0 and the last was x=1536; the AX width1330 includes
alignment padding. Preserve the [coordinate diagnostic](../evidence/story-002/stable-strip-main-coordinate-diagnostic.json)
as a harness endpoint exclusion. A corrected [visual run](../evidence/story-002/stable-strip-main-visual-results.json)
completed six real-pointer moves at left, middle, right x=1536, return, leave
and re-enter. Host identity/bounds stayed stable, hide/reveal worked and media
remained paused at zero with source unchanged. Root's PNG review saw middle and
right captions (00:45 / keyframe 00:44 and 01:30 / keyframe 01:28) and clearing;
the screenshot method captured the owned parent+child window group, not the
panel in isolation. This is prototype visual-applicability evidence, not all-
surface acceptance or timing proof.

The [matched ordinary-control comparison setup](../evidence/story-002/stable-strip-control-comparison-setup-failure.json)
failed at baseline template-right with zero scored responses. Its collapsed
ownership guard read false at 941770.821 even though crop containment and the
post-owned check were true; target activation was recorded at 941760.464, with
no event observed before cleanup at 941771.310. A missing event during that
window does not prove no actual transition and does not waive the ownership
guard. This remains a setup failure, not a latency result.

A separate [guard-component applicability check](../evidence/story-002/ordinary-control-guard-components-applicability.json)
completed six baseline interactions without reproducing the transient guard
failure. Its first wrapper had a post-analysis `KeyError`; the sampler's
query-end value precedes getter completion. A six-interaction independent 10ms
sampler produced 5,996 readings with 10.03ms median and 19.84ms maximum callback
cadence, also without reproducing the guard failure. These checks neither
qualify latency nor explain the original failure. Root's bounded decision is
one new-instance registration/setup pilot using app-lifecycle notification
observation, consistent with Apple's
[`NSWorkspace.didActivateApplicationNotification`](https://developer.apple.com/documentation/appkit/nsworkspace/didactivateapplicationnotification)
contract. Do not resume repeated paired comparisons until that setup pilot
reports. The optional idle-desktop question is unanswered, but does not block
these already-authorized guarded diagnostics. The cause remains unknown; no
product change is retained, production remains original 022512, and Story 002
is In Progress.

### 2026-10-05 07:03 — NSWorkspace setup pilot abandoned

The bounded [workspace launch pilot](../evidence/story-002/workspace-launch-pilot-setup-failure.json)
used the exact expected `VLCBaseline.app` URL and returned PID67263 with the
expected bundle ID and intact process argv. It stopped before any capture
because RC could not establish a stable paused time-zero input; it reported
`stop`, zero media time and empty counters. The cleanup adapter then reported
an argv/config/socket ownership mismatch. A separate 07:01 `ps` check found
PID67263 absent, but the exact exit status was unavailable. Do not interpret
the cleanup mismatch as proof the process remained running or the later absence
as a confirmed clean exit.

Root's read-only source diagnosis found `work/upstream/vlc-3.0.24/modules/gui/macosx/darwinvlc.m` lines 230–286 pass remaining
arguments to VLC and play, while `work/upstream/vlc-3.0.24/modules/gui/macosx/VLCMain.m` lines 472–497 filters duplicate
command-line media in `openFiles:`. The launch argv remained intact; environment
and working-directory differences remain unproved. No concrete source or
launcher defect was established. Under the 07:03 stop rule (at most 15 minutes
for a concrete diagnosis and one fix only if a defect is demonstrated), abandon
the NSWorkspace route; do not rerun it or attribute the earlier guard failure.

This was an inconclusive setup failure, not a latency or native behavior result.
Canonical original 022512 is restored. At that point, detached and fullscreen
prototype checks remained pending. UI performance qualification remains paused,
and Story 002 remains In Progress.

### 2026-10-05 — four-surface stable-strip visual applicability

The detached 061929 prototype run completed six observations with stable host,
leave/hide and integrity true, paused at time zero. Root visually confirmed the
right endpoint caption 01:30 / Keyframe 1:28
([summary](../evidence/story-002/stable-strip-four-surface-visual-applicability.json)).

Custom fullscreen 001 and 002 each failed at the initial left endpoint because
no stable-strip host was found. The actual AX fullscreen slider bounds were
x=641,y=918,w=445,h=17; do not substitute the initially misreported hidden-main
rectangle or infer why the host was absent. In diagnostic003, custom and native
fullscreen were first seeded at middle, then left/middle/right/return/leave/
re-enter all passed visible-presentation, stable-host, hide and integrity
checks, with media paused at zero. Custom host was 795×240 at (466,690); native
host 795×240 at (466,697). Root visually confirmed custom right 01:30 / keyframe
1:28 and native return-middle 00:45 / keyframe 0:44 with clearing. An alpha=0
visibility observation occurred during initial fullscreen reveal before the
seeded sequence; it does not establish the historical no-host cause.

The [compact evidence ledger](../evidence/story-002/stable-strip-four-surface-visual-applicability.json)
links the detached result, both failed initial custom runs and the custom/native
seeded results. Together with main-window evidence, this establishes four-
surface visual applicability only. First-entry fullscreen reliability, resize,
playing-media behavior, playback/control, accessibility, resources and
performance remain unqualified on this prototype. Canonical 022512 is current,
no prototype change is retained, and no acceptance criterion is closed.
Performance qualification remains paused; Story 002 remains In Progress.

### 2026-10-05 — runloop-observer applicability stopped before scoring

The [observer pilot](../evidence/story-002/ordinary-control-runloop-observer-setup-failure.json)
used a revised main-loop pump with a 1ms no-op timer; the pixel self-test passed
5/5. The first baseline template failed before the planned negative attempt and
scored zero samples. At t0+0.302s it recorded `display_frame` index17/status1
while the collapsed target-app guard read false, crop containment and AX
ownership were true, and tagged routing plus after-owned checks passed. An
independent notification collector recorded target activation but observed no
transition before cleanup; that absence is not causal evidence.

Review identified latent negative-harness problems—`frame` versus
`display_frame` kind handling and no independent negative interval. Neither was
exercised, so negative validation is not established. Input hashes and the
canonical 022512 runtime remained unchanged. This is a setup failure with no
fix, response result or latency gain. Root's baseline-left-only split-component
and frontmost-snapshot classification run 002 is still running; no result is
claimed. Do not repeat performance measurements or attribute the guard
discrepancy from this pilot. At that point, classification run002 was still
pending; its later result is recorded below.

### 2026-10-05 — frontmost-v2 applicability and reversible 072539 candidate

Baseline-only frontmost-v2 applicability passed four positive controls
([summary](../evidence/story-002/control-frontmost-v2-001-contract-applicability.json)):
696 callbacks, zero failures, zero disagreements with the retained legacy
active/visible checks, and a five-case pixel self-test. The deliberate negative
used two Finder frames with PID759 and bundle `com.apple.finder`, observed target
activation/deactivation notifications, and completed the foreground-change
actions. The negative probe exited1 as expected. This demonstrates the
prospective frontmost-PID-and-bundle observer policy under that control. It does
not explain or waive any older guard failure. Frozen v1 probe/trial copies
remain separate; no primary guard change is made.

The baseline-left-only split-component/frontmost-snapshot classification run002
passed without reproducing the transient guard discrepancy; root stopped that
classification path. The subsequent fresh 100-per-arm ordinary-response
comparison stopped during baseline click010 after ten baseline observations and
zero feature observations. Routing and ownership checks passed, but the
observer reported three `SCFrameStatusIdle` callbacks with no pixels and no
complete presentation to score by 900ms. Held-slider AX changed from 6651 to
5586; serial idle AX queries took 422.24, 429.69 and 505.22ms. The archived
[incomplete-cohort record](../evidence/story-002/ordinary-control-frontmost-strip-001-incomplete.json)
preserves the result. Collection is invalid, with no partial salvage, candidate
failure or p95 claim. Slow AX calls are an observer-backpressure lead, not
causal proof.

Apple's ScreenCaptureKit guidance checks `SCFrameStatus.complete` before
processing frame content and returns no frame for other statuses ([status
enum](https://developer.apple.com/documentation/screencapturekit/scframestatus/complete),
[capture flow](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos)).
Observer v3 has passed prospective strong review and is implemented in the
observer and trial runner. It performs expensive AX checks only for
`SCFrameStatusComplete` frames while preserving frontmost, CGWindow/crop and
routing guards on every callback. Idle AX values are null/unmeasured; phases
remain separate and unqualified. The five-case pixel self-test and Python
compile pass, but a headless v2 replay was rejected for version mismatch and is
not v3 evidence. The first v3 qualification attempt failed before capture
geometry when an independent collector observed Codex foreground transitions
during setup. Cam later confirmed mouse/keyboard use during those transitions,
then finished; this contextualizes that focus change only and does not explain
earlier unexplained false-guard observations. The archived
[setup-failure record](../evidence/story-002/ordinary-control-complete-frame-v3-setup-failure.json)
does not qualify UI behavior, the candidate, or performance. Root's 13:09 loop
review records a 07:03→13:09 gap, without claiming hourly-review compliance.
The subsequent clean v3 applicability run passed four positive controls with
zero faults and independently corroborated the known Finder negative, which
the probe rejected as expected ([control record](../evidence/story-002/ordinary-control-complete-frame-v3-controls.json)).
This remains observer/control applicability, not feature UI or performance
qualification. The first eight-per-arm method pilot on 072539 ended invalid at
four baseline / five feature observations when the feature knob request at
x=1090 remained visually at x=950; input routing, ownership and AX value change
were observed, but the pixel response gate failed
([record](../evidence/story-002/ordinary-control-complete-strip-pilot-setup-failure.json)).
No partial p95 or effect is salvaged.

Root then built experimental [132643](../evidence/story-002/app-build-controller-16ms-experiment-132643.json),
with controller SHA-256 `47b31fa472d778e0c48b304b6c07cf6e7f7a7a62cade31f42943093f4d093690`.
Only that input differs from 072539; helper/service/archive inputs match and
VLC, `libmacosx_plugin.dylib`, and `plugins.dat` outputs differ. A separate
eight-per-arm method pilot completed without faults or input changes, with
descriptive response ranges 245.5–367.4 ms baseline and 241.8–385.2 ms feature
([summary](../evidence/story-002/ordinary-control-16ms-method-pilot.json)). This
is not p95 or effect qualification. The fresh formal 100-per-arm comparison
with v3, 900 ms, and zero added allowance ended invalid at 61 valid baseline and
75 valid feature observations. Baseline action 62 failed because one idle
callback reported the per-PID app object missing while the independent
foreground query still identified the expected VLC PID/bundle and parent crop
containment; no pixels were available. Cause is unknown. The archived
[failure record](../evidence/story-002/ordinary-control-16ms-formal-setup-failure.json)
preserves this without product-regression inference or partial metric salvage.
The signed original 022512 and source SHA-256
`f6d88892c4731659340a2d96ede7a61b02f40ed2c9ddf8424ae2853c089bc4cc` are
preserved. The 072539 source/build remains preserved as the prior reversible
candidate. Neither it nor the later 132643 experiment is final; matched
performance, playback and reader qualification remain pending.

Detached resize004 did not place the host beneath the stationary pointer: the
resize preserved aspect ratio at actual height743 instead of requested850,
moving the timeline from y1028 to y921 while the pointer remained at the old
location. The preview correctly hid. Preserve this as setup/geometry evidence,
not a reproduced defect. The 072539 visual proof remains applicability-only;
the 132643 build has only method-pilot evidence and a formal matched comparison
is running, without a result yet.


## Shared-machine workload clarification — 2026-10-05

Cam reports that two other AI threads continually use the machine, with changing resource demand. This is a plausible confounder for wall-clock response, decoding/display and screen-capture observations; it is not proof of the cause of any recorded failure. Exclusive keyboard/mouse ownership does not establish exclusive CPU, memory, storage or compositor availability. Alternating baseline/candidate order reduces systematic order bias but cannot guarantee matched background load.

Primary guidance: [LLVM benchmarking tips](https://llvm.org/docs/Benchmarking.html) recommends repeated measurements to recognize noise and reducing other running processes; it also distinguishes noise from measurement bias. Its Linux-specific tuning commands are not proposed for this macOS project.

The frozen v4 formal comparison remains invalid because the setup did not identify the expected pixel knob, despite changed accessibility value and passing ownership checks; there is no scored baseline/candidate comparison. The exact-zero allowance did not cause a scored rejection. Playback repeats in both arms remain unattributed. Recommendation: separate functional MVP proof from performance qualification, estimate repeatability/background-load uncertainty, and select a practical explicit regression allowance before another comparison. A short quiet window would improve an attribution experiment. No threshold, acceptance status or historical verdict is changed by this note, and no new benchmark is run.
