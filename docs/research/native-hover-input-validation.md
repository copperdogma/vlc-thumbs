# Native hover input validation — 2026-10-04

Problem class: asynchronous input automation can deliver discrete button events
without leaving a persistent pointer in the same position or producing movement
through a tracking region. Successful click seeking does not prove hover input.

Bounded primary-source research:

- [Apple: Using Tracking-Area Objects](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/TrackingAreaObjects/TrackingAreaObjects.html):
  an owner can be any object; attaching before window membership is supported.
  InVisibleRect tracks geometry changes automatically. ActiveAlways supports
  inactive applications. Enter/exit delivery order is not guaranteed.
- [Apple: Monitoring Events](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/MonitoringEvents/MonitoringEvents.html):
  local monitors observe application dispatch, return the original event to
  preserve behavior, and should be removed before lifecycle completion.
- [Apple: XCUIAutomation](https://developer.apple.com/documentation/XCUIAutomation)
  and [coordinate hover](https://developer.apple.com/documentation/xcuiautomation/xcuicoordinate/hover()):
  standard UI testing has an explicit hover operation. Our permitted Sky API
  exposes clicks and drags but no hover. No alternative automation framework
  has been adopted or run.

Decision: retain the conventional tracking-area design pending actual input
proof. Compare event coordinates with persistent pointer coordinates and use
an opt-in, pass-through local event monitor as a diagnostic only. Request a
small human pointer baseline while Cam is at the unlocked computer. Do not
replace tracking with polling or rebuild areas based only on automation clicks.

Local evidence: both adapters initialize with attached windows; real generated
video opens, plays and pauses. Sky right clicks do not produce fresh entry or
movement traces. One earlier entry hid after about 100ms. This does not yet
establish either a tracking defect or a pointer restoration behavior in Sky.
The local-monitor diagnostic is authored but not yet built/run; real-pointer
baseline remains pending. Update findings after that bounded test.

Local diagnostic test, 16:24 UTC: the pass-through monitor is built and run.
Sky right-click generates mouseMoved/rightDown/rightUp at slider {733,7},
but NSEvent.mouseLocation maps to {1076.875,271.47265625}, outside slider
{0,0,1335,14}. The area remains attached and fully visible. Actual human
movement elsewhere produces matching event/persistent coordinates. Therefore
Sky posted coordinates cannot qualify sustained hover on this host. Keep the
real-pointer baseline; no tracking workaround is justified by these clicks.

Human hover at 10:45 Edmonton crashed in CFRelease from VLCSliderCell.dealloc.
Pinned source shows an owned CVDisplayLink and no subclass copyWithZone contract.
Apple [NSCopying guidance](https://developer.apple.com/documentation/foundation/nscopying)
requires subclasses to handle their additional ownership state. We removed the
cell copy entirely and read live bar/knob rectangles without value writes.
The report proves unsafe copying, not the exact invalid pointer state.
9000 native geometry queries pass with copy/value setters guarded against use;
20 real pointer entry/exit moves preserve paused playback and survive.
A composite screenshot shows main-window image at pointer 00:35 / keyframe 00:34;
custom fullscreen image at 00:28 / keyframe 00:28 also appears and survives.

Cam authorizes any computer interaction technology for autonomous hover tests.
The development-only native-pointer.m targets only the isolated bundle ID,
warps the persistent pointer and posts a matching Core Graphics movement event.
Apple [cursor-warp documentation](https://developer.apple.com/documentation/coregraphics/cgwarpmousecursorposition(_:))
states warp alone generates no event; the explicit movement event completes
the interaction. Local traces now show matching physical and event coordinates.
The probe does not activate the application during hover: doing so at every
move changed custom fullscreen state and is unsuitable for input testing.

Cam requests a taller hover area. Apple [accessibility guidance](https://developer.apple.com/design/human-interface-guidelines/accessibility)
recommends 28x28pt targets on macOS. Choose 32pt total height centered on the
existing timeline, clamped within the containing controls view. Track on the
parent so the extra vertical area actually receives movement; observe slider
geometry/window resize. Keep slider drawing, action, AX role and actual click
hit target unchanged. Fullscreen volume/buttons lie below the expanded area.
Native main-window above/below/leave checks pass with paused position unchanged
at 00:15. Owned composite screenshots in ignored validation work show the image
when hovering above and below the 14pt visible track; outside 32pt removes it.
Resize and the revised fullscreen targets remain to validate.

2026-10-04 18:52 UTC — Fullscreen setup correction on the final Utility
candidate (manifest 180947). The pristine baseline initially also produced a
black capture of the fading fullscreen panel. Explicit application activation,
300ms settling, persistent movement within the video, and prompt capture
revealed the baseline controls. Both focus snapshots reported active, so this
is a successful setup sequence, not proof that inactivity caused the failure.
Avoid Sky state retrieval during fullscreen tests because it can raise the
main window behind the video. Native guarded AX focus and owned-window capture
keep the actual fullscreen window focused.

The same sequence on final candidate PID81993 visibly passes above-track
(y912), below-track (y940), and leave (y900) for the timeline at y918..935.
Paused AX position3400.85888671875 is unchanged across these moves. Moving
into the video and waiting four seconds hides the panel; a fresh move reveals
it and the thumbnail again. A guarded actual timeline click then changes
position to7270.58837890625 while still paused, visibly00:43 with keyframe00:42.
Owned-panel captures and action records: ignored fullscreen-final/.
Pinned VLCFSPanelController autohideCallback only fades while the persistent
pointer is outside the panel; this makes persistent pointer state essential.
No product workaround or fade-timer change was required.

2026-10-04 19:07 UTC — Review catches final tooltip assignment ordering:
VLCFSPanelController.setupControls runs after the earlier adapter constructor.
Moving construction after setupControls clears the final generic tooltip while
retaining VLC's translated AX labels. NSPanel focus/mouse flags alone do not
exclude its AX subtree; a nondisplayed AppKit probe confirms accessible window
children by default. Explicitly exclude the decorative panel element, children
and navigation children. Apple accessibility customization documentation:
https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/ImplementingAccessibilityforCustomControls.html

Build190039 signs/verifies. Actual own AX tree before/while main hover has25/26
rows; the extra row is an empty AXGroup, without preview image/time/state
descendants. Position and volume sliders remain exposed, and focus stays on
the main video window. This is hierarchy/focus proof, not actual VoiceOver
speech testing. Fullscreen tooltip and remaining native lifetime checks pending.

## Native Matroska time-origin correction — 2026-10-04

Actual owned UI checks on the +5s flat MKV measured VLC duration17s. Ordinary seek6s displays burned source1.250s/frame30; seek16s displays source11.250s/frame270. The helper previously added FFmpeg start_time5s before seeking and subtracted it from the result. Consequently hover6.125 mislabeled raw keyframe5 as0; hover11.125 could choose raw15 (future relative to VLC) and label it10. Pinned VLC `modules/demux/mkv/mkv.cpp` GET_TIME returns raw PCR and SET_TIME forwards rawtime toSeek; ordered editions have additional mappings in virtual_segment.cpp and remain unqualified.

Select origin0 for probed `matroska,webm`, preserving positive initial gaps; keep other format policy unchanged, including MP4 edit-gap video2s with container/audio0. Reject negative Matroska starts as ambiguous. Fresh helper pilot returns5/5/5/15s for0/6.125/11.125/16.125 requests; independent keyframe map contains5/15. Update oracle with the native timeline convention and explicit11.125 image-selection regression; bump service cache identity policy prefix. Preserve prior helper/source/manifest in ignored helper-before-mkv-origin-fix and raw native screenshots/actions in native-time-origins-001/002. Ordered chapters, codec-delay variants and general WebM coverage remain limitations. Rebuild and native post-fix proof required; previous native candidate/cohorts retain their exact hashes.


### Continuous visible observer applicability — 2026-10-04 21:07 UTC

The prior one-demand pilot had correct on-screen pixels but reused an old media
generation. Pinned oldrc rejects playlist commands while paused; the existing
native trial runner already handled this. Reused its normal resume → confirmed
play → stop → confirmed stop → add sequence, with the pointer off the timeline.
The next same-API sRGB pilot independently prepared a reference in the prior
generation, proved a different reopened generation, and produced one real miss
with a matching displayed keyframe and pointer caption. Service assignment was
131.52 ms; raw WindowServer timestamps are retained separately. This validates
the measuring method only. No cache clearing or product seam was used.

ScreenCaptureKit defaults to display color space, so references and measurements
must share explicit sRGB capture/wrapping. The complete-frame readiness gate
requires one real full buffer; unchanged paused displays then produce idle
frames, per the SDK's SCFrameStatusIdle contract. Measured completion now also
requires complete frame status, WindowServer display time and PTS after physical
pointer input, matching owned-panel bounds, image and the new pointer caption.
Remaining step: 100 settled out-of-order outcomes per actual cache condition on
each standard container, with every error retained and counted as failure.


### VoiceOver observer applicability — 2026-10-04 21:18 UTC

This is an observer failure, not a product accessibility verdict. Launching the
previously off system reader opened its Quickstart dialog. The first query of
VoiceOver's documented `last phrase.content` timed out; after choosing Use
VoiceOver it returned -1728. The caption keyboard route did not yield usable
spoken text. Stopped the reader successfully with its ordinary Quit command,
verified no VoiceOver process remained, and stopped only the development player
launched by this test. A finally-handler timeout initially interrupted cleanup;
the cleanup was repaired explicitly and the failure retained in
work/validation/story002/voiceover-applicability-001. No speech proof claimed.

Apple's [general VoiceOver commands](https://support.apple.com/guide/voiceover/general-commands-cpvokys01/mac)
and [caption panel guide](https://support.apple.com/en-mz/guide/voiceover/unac078/mac)
provide the established keyboard/caption approach when scripting is unavailable.
The local VoiceOver.sdef defines read-only `last phrase.content`; neither that
definition nor an AX-hidden preview proves real announcement behavior. Next
experiment must obtain actual caption/speech evidence or a brief witnessed
reader test, while keeping the previously off reader state restored afterward.


### Continuous observer phase race — 2026-10-04 21:22 UTC

The corrected RC-status pilot scored three real misses and one RAM hit. The next
RAM attempt retained a correct native display trace but zero post-input capture
frames. Raw rows show the second readiness callback at input t0 +12.87 ms while
`postInput` remained false. It set `finished=YES` after the main thread had reset
that shared flag; the main thread then stopped immediately and emitted its
generic timeout error. This is an asynchronous phase-transition race in the
observer, not an absent thumbnail.

Use separate readiness and measurement state: readiness only increments
`warmFrames`; arm t0/deadline/postInput on the serial capture queue before posting
physical input. The established dispatch_sync contract orders completion before
the caller proceeds (local SDK dispatch/queue.h). Preserve the old observer and
all failed outcomes, then require one clean three-demand miss/RAM confirmation.
Do not launch a full cohort on another observer failure. This repair changes no
product code, timing target, or selected-frame/caption criterion.


### TLS regression-test applicability — 2026-10-04 21:53 UTC

Problem class: platform/backend-specific trust configuration in a portable
regression test. The test configures gnutls-dir-trust and gnutls-system-trust,
while logs show Secure Transport client selection and GnuTLS server fallback.
The fixture certificate is valid from 2016 until9999; expiry is not the cause.
[Apple custom trust anchors](https://developer.apple.com/documentation/security/sectrustsetanchorcertificates(_:_:))
and [GnuTLS certificate credentials](https://www.gnutls.org/manual/html_node/Certificate-credentials.html)
describe backend-specific custom trust configuration. This suggests a mismatch
hypothesis, not a proven local cause. A bounded unmodified-test comparison
with saved baseline core/libVLC and TLS plugins reproduces the same assertion;
dyld logs prove baseline loading. These four binaries are identical to feature.
Record the inherited failure and defer backend repair beyond thumbnail scope.
Do not change system trust or disable certificate validation to pass it.


### Observer-load versus AppKit drawing — 2026-10-04 22:07 UTC

The planned20 paired RAM AB/BA diagnostic completed without faults; all
image/time/keyframe/cache/focus/geometry and app/media integrity checks pass.
Buffered callbacks cost at most1.27ms, yet buffering did not improve response:
heavy median110.02ms/p95143.45ms; buffered median125.36ms/p95184.22ms.
Median heavy-minus-buffered paired delta is-19.51ms; only5/20 image pairs
improve by a60Hz interval. Diagnostic only, not qualification; buffering uses
pre/post ownership guards rather than per-frame guards. Stop observer tuning.
Post-assignment median delays remain71.77/69.52ms heavy/buffered; percentiles
are non-additive, and these data do not identify a single cause.

Problem class: deferred native drawing/compositor scheduling for a transient
UI. Apple's [NSWindow displayIfNeeded documentation](https://developer.apple.com/documentation/appkit/nswindow/displayifneeded())
explains that dirty views normally draw on event-loop passes, and the method
draws only dirty views when explicitly needed. Apple's [view drawing guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CocoaViewsGuide/SubclassingNSView/SubclassingNSView.html)
describes display messages for immediate drawing. Next bounded experiment:
request displayIfNeeded only on the336x224 hover panel after loading, same-
bucket time updates, unavailable state and image assignment. Preserve original
assignment trace and separately record draw-call duration. Keep helper/QoS,
geometry, caches and latency thresholds unchanged. Compare one20-pair RAM
diagnostic to the existing205111 source-candidate diagnostic (sequential runs,
not product-arm randomization), then revert if it does not materially
reduce presentation delay. No full latency/playback qualification until the
experiment changes the next decision.


### Drawing result and interactive scheduling — 2026-10-04 22:12 UTC

The displayIfNeeded20-pair run completes without faults. Heavy observer median
improves110.02→67.52ms and its post-assignment median71.77→37.31ms; p95
remains125.39ms, above100ms. Buffered median125.36→117.48ms; p95192.35ms.
These are sequential source-candidate diagnostics, not randomized product arms
or qualification. Draw-call median0.086ms/max0.108ms; no force-flush/private
API used. Keep the small drawing change provisionally for qualification.

Residual worker-to-main/cache scheduling costs reach27–34ms although most RAM
work is under1ms. Apple's [User Initiated QoS](https://developer.apple.com/documentation/dispatch/dispatchqos/userinitiated)
assigns this class to work providing immediate results for the user's action;
[Utility QoS](https://developer.apple.com/documentation/dispatch/dispatchqos/qosclass-swift.enum/utility)
is for work the user is not actively tracking. Next bounded experiment changes
only the serial service queue to User Initiated. The expensive helper process
stays Utility, single-threaded and separately resource-bounded. Preserve the
drawing-only app/source before this change. Run one20-pair diagnostic and
service contracts; then literal latency/playback checks if the result supports
the change. Priority improvement is a hypothesis, not proof of preserved
playback; no cache semantics or thresholds change.


### 22:21 UTC — drawing-only tail attribution

Read existing20-pair heavy-observer records without further UI work while desktop
exclusivity is pending. All four demands above100ms are dominated by the
assignment-to-visible interval (63–99ms); two also have26–30ms service intervals,
whereas the other two services finish below1ms. Input-to-mouse is24–26ms in these
four. Queue QoS can address only part of the observed tails. This descriptive
partition does not identify whether AppKit/compositor delivery or capture
presentation is responsible for the remaining interval. No overhead is subtracted
and no new product tweak is selected. Full rows, estimator and scope are archived
in `docs/evidence/story-002/drawing-tail-stages.json`.


### 22:23 UTC — scoped experiment review

Read-only review of controller/service differences against saved pre-experiment
sources finds no actionable correctness defect. Explicit drawing remains on the
main thread and only touches the preview panel; generation/presentation/hover
checks precede asynchronous image attachment. Source behavior does not prove
visible performance. The changed serial queue's User Initiated QoS covers the
whole performRequest, including disk writes, directory sorting and pruning, not
only RAM lookup. Decoder NSTask explicitly remains Utility. Retention therefore
requires fresh playback evidence under real cache demand; service contract passes
alone do not qualify the scheduling tradeoff. Display assignment traces precede
the explicit draw call, and draw duration is not compositor completion. Primary
contracts: https://developer.apple.com/documentation/appkit/nswindow/displayifneeded%28%29
and https://developer.apple.com/documentation/foundation/process/qualityofservice.


### 23:56 UTC — asynchronous foreground contention on resumed validation

Cam resumed an idle-desktop interval. Two guarded QoS diagnostic attempts002/003
stopped during prior-generation template setup, before scored RAM pairs. Both
observed target_app_inactive while parent crop and panel geometry remained valid;
current frontmost-app reads returned ChatGPT. App/source hashes remained unchanged.
This establishes a focus transition, not its cause: user interaction versus app
activation behavior remains unresolved. Do not silently reactivate inside scored
captures or filter failed samples. Retain both complete failed setups and ask
which condition applies before further full attempts.

Bounded general research: Apple's XCUIApplication state contract describes app
state as asynchronous and foreground after successful activation; NSWorkspace
provides didActivateApplicationNotification on its own notification center for
tracking transitions. Adopt state/transition observation, rather than fixed sleeps
or automatic retries. A small unscored activation monitor is the next experiment
if Cam reports the computer was idle. No broad automation-framework migration is
justified by these two setups.

Sources: https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/state-swift.property
and https://developer.apple.com/documentation/appkit/nsworkspace/didactivateapplicationnotification.


### 2026-10-04 18:06 MDT — rejected queue-priority experiment

Focus-transition-diagnostic.json records42s stable owned foreground activity,
including unscored hovers; activation away follows owned-player cleanup. Attempt004
then retains all20 correct RAM pairs. Heavy median126.06/p95183.73ms fails the
unchanged100ms target and gives no useful gain over the drawing-only experiment.
Sequential product runs are not randomized evidence of regression causality.
Restore Utility queue QoS, preserve helper Utility and provisional explicit drawing.
The existing scored traces place slowest assignment-to-visible intervals88–129ms,
with additional17–21ms mouse-to-hover and25–35ms service intervals. Draw calls are
about0.1ms. The remaining interval's cause is still unproven. Archive allrows in
paired-visible-interactive-qos-diagnostic.json; do not subtract observer cost.
Bounded presentation research precedes the next product experiment. Apple's
CATransaction and NSView wantsLayer contracts identify layer transactions and
implicit rendering; they do not themselves justify global transaction flushing.
Sources: https://developer.apple.com/documentation/quartzcore/catransaction and
https://developer.apple.com/documentation/appkit/nsview/wantslayer.


### 2026-10-04 18:09 MDT — transition-only panel ordering experiment

Primary-source review selects one narrow lifecycle experiment: maintain attached
child-window order and call orderFront only on reveal, parent change or level
change. Apple documents relative order preservation for attached child windows.
The prior code orders front and assigns its level on every pointer demand.
Its contribution to tail latency is unproven. Keep frame positioning, explicit
drawing, decoder/helper, Utility queue, observer and thresholds unchanged; record
ordered/was_visible/parent_changed/level_changed booleans. First-show and reopen
in the guarded template/measurement sequence must preserve actual visible image,
captions and owned geometry. A retained candidate also needs fullscreen transition
stacking and hide/reveal proof. One20-pair diagnostic follows, then revert without
clear gain and reassess presentation profiling before further speculative tweaks.

Do not use global CATransaction.flush: Apple's contract discourages it when a
run loop exists, and it affects the implicit transaction rather than just this
panel. Modern AppKit already uses Core Animation, so wantsLayer=false alone
cannot justify a rendering-path rewrite.

Sources: https://developer.apple.com/documentation/appkit/nswindow/addchildwindow(_:ordered:)
https://developer.apple.com/documentation/appkit/nswindow/orderfront(_:)
https://developer.apple.com/documentation/quartzcore/catransaction/flush()
https://developer.apple.com/documentation/macos-release-notes/appkit-release-notes-for-macos-10_14.


### 2026-10-04 18:23 MDT — bounded main-thread profiling results

Ordinary-hover-main-profile.json retains a valid20s main-thread statistical sample
with14925 of15098 main-thread samples in ordinary event waiting. It excludes the
ScreenCaptureKit observer and cannot attribute its recorded presentation tails.
Under the two-pair capture diagnostic, first profiling wrappers accidentally
selected the short-lived compiled-options --longhelp process before the actual
player. Exact --rc-unix ownership distinguishes the long-lived player. Corrected
003 matches the trial's ownedPID and the method completes correctly, but sample
returns0 with no thread stacks. Returncode alone is not profiling proof; archive
captured-main-profile-inconclusive.json. Instrumented trial timings never qualify
p95. sample's localhelp documents duration, -mayDie and symbol-loading behavior;
no further wrapper retries or product changes are justified by an empty report.
Next investigation should use controlled profiler/target lifetimes and preserve
an existing method's owned PID handle, rather than app-name discovery. Actual
phase attribution under capture remains open. Foreground is stable in successful
sessions; no user diagnosis is required to proceed with profiling.
