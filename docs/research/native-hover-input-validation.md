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


### 2026-10-07 06:33 UTC — fresh016 AX setup acquisition discriminator

General problem class is asynchronous app activation and malformed/stale accessibility acquisition during native setup. Actual fresh016 normalQuit001 passes exact PID/path/socket empty-state/CG window ownership, but the complete AXWindows-root traversal produces AXApplication roots recursively and fails the unchanged empty-window guard. The diagnostic prefix is truncated; guard parses the full output, so increasing retention is not a remedy. No media admission, CUA binding or normal Quit occurs. Owned SIGTERM cleanup exits0; no new shutdown failure follows. Cause remains unknown.

Reuse the existing foreground-state research above and Apple NSRunningApplication activation contract: [official API](https://developer.apple.com/documentation/appkit/nsrunningapplication/activate(options:)), installed macOS SDK NSRunningApplication.h lines127–148. Activation requests do not establish immediate or guaranteed foreground state. Selected bounded next proposal: after exact Popen/PID/start/path/empty RC/ownedCG proof, invoke the existing allowlisted activate action once and observe focus plus unchanged complete prebind guard within the existing8s bound. No helper modification, longer timeout, repeated activation or AXApplication-as-AXWindow waiver. Direct CUA discovery changes observation and activation together and is deferred. If correctly owned active state still fails unchanged acquisition, stop this method and reconsider an independently specified observer route. Preserve001 failure and owned preexisting016 profile; no deletion/fresh-profile claim. This is a setup hypothesis, not a product fix or demonstrated result; separate frozen002 plan/root admission is required.


### 2026-10-07 06:55 UTC — discriminator stopped; desktop unavailable

Revised002 retained the same8s envelope and unchanged complete prebind, requiring observed active focus/owned geometry after one activation. The existing activation command returnedfalse/nonzero before focus/media/Quit; owned SIGTERM cleanup exited0 with parent/sampled preparser absent. Root's independent read-only CUA inventory then explicitly reported Mac locked and automatic unlock failed. This proves current desktop unavailability, without attributing every earlier AX symptom. Acquisition method stopped; no helper repair or further launch. Manual unlock requested asynchronously. Complete conventional distcheck010 passed independently; it does not supply native or reader proof. After unlock, verify actual availability and review a fresh bounded plan instead of replaying consumed callers.


### 2026-10-07 16:52 UTC — asynchronous geometry snapshots

General class: cross-observer snapshot consistency while a newly ordered native window may be changing. Trial003 compares CG window1317 at16:46:23.759 (212,394,888,452) with AX focus at23.945 (208,392,896,456). ONE activation and observed active state pass; stale preactivation geometry comparison fails. No media or normal Quit occurs; owned SIGTERM cleanup0 and sampled absence are separate. No animation cause is established.

Primary Apple documentation describes [CG current-window information](https://developer.apple.com/documentation/coregraphics/cgwindowlistcopywindowinfo(_:_:)), [CG upper-left screen coordinates](https://developer.apple.com/documentation/coregraphics/kcgwindowbounds), and [AX upper-left global coordinates](https://developer.apple.com/documentation/applicationservices/kaxpositionattribute). There is no source-backed reason to apply a coordinate-scale correction. AppKit supports [automatic ordering animations](https://developer.apple.com/documentation/appkit/nswindow/animationbehavior-swift.property); this makes temporal disagreement plausible, not proven locally.

Candidate smallest discriminator: observe the SAME owned CG window ID immediately before and after AX focus, within the existing8s setup envelope; retain1point equality, original complete prebind, one activation, unchanged binaries and all ownership/resource guards. Wait for a coherent bracket rather than compare against a historical frame. Persistent disagreement or malformed acquisition stops; no threshold widening or longer deadline. Strong strategic review pending; no new runtime released by this research entry.

Strong early review adopts one prospective004 discriminator. Stable CG brackets with disagreeing active AX stop immediately; only valid changing CG geometry may remain pending within the unchanged8s. Missing or changed ID and malformed data stop. No runtime has yet established the hypothesis.


### Human-assisted reader activation — 2026-10-07T21:13Z onward

Cam returns and explicitly requests root try VoiceOver, asking for help only at a blocker. This is a new reader-only task after the old20:43Z loop ended, not a reset of its deadline. Existing Ideal playback/accessibility and Story005 strongverification apply; ADR004/source72R8 unchanged. General class is first-run screen-reader onboarding and observation, not demonstrated VLC failure. Fresh Apple [generalcommands](https://support.apple.com/guide/voiceover/general-commands-cpvokys01/mac), [interactioncommands](https://support.apple.com/guide/voiceover/interaction-commands-cpvokys07/mac), and [captionpanel](https://support.apple.com/en-in/guide/voiceover/unac078/mac) support ordinary Control-Option navigation/defaultaction and visible captions; reuse human speech witness when automated readerAX is unavailable.

InitialreaderOFF/processabsent. CommandF5 yields no settingchange; actualSettingsOFF→ON then QuickstartUseVoiceOver yields readerPID69341. Toolquerytimeouts are not terminalprocessproof: read-onlypgrep shows actualCoreServicesVoiceOver, and Cam explicitly says “I can hear it talking.” Captionpanelalready1, scriptingpermission0 unchanged. Tutorial shows it can restrictcommands for practice. Two rootclose attempts hitCUAuserchangedguard; stop ratherthanretry, askCamcloseonlytutorial/leaveVOon. No VLC launched yet. One plain016 reader-only plan prepared bySOL6.1medium/rootreviewed;15mintrial max/source/app/history/resources preserved. Scope Position→neighbor actualreader navigation/sampledspokenphrases, ONEpause/resume, cleanup. Visiblepreviewnavigation/precisionseek remainunqualified; no new source/build/runtimeotherlanes.


### Reader001 human witness and protocol correction — 2026-10-07T21:30Z

After direct shortcutsfailed, Camexplicitlyasksrootrepeatactivation. Supported UtilityGeneral Displaywelcome1→0 temporary plus SettingsOFF→ON starts actualreaderPID7766; Camconfirms speech again. Rootdidnotchange scriptingpermission. ActualautomatedctrlaltF/typePosition/Return producesnoobservableVOfeedback and aVLCScaleToScreen overlay; thosekeysarenot creditedasreader navigation. CamphysicalControlOptionF/typePosition/Return doesannouncePosition and continuouslychangingpercentage(~0.1increments); speech repeatedlycutsoff. PhysicalFindPause/Return/VOSpace producesCamwitness ofbriefpause+pausedannouncement; no stablepausedburninpair or typedpausedstate captured. Rootsentnoresume; workeronlyreadonlystatus/time aftermedia. Recordedstatusplay221/259/290 thenactualstop5 atoriginal300sfixtureend. Causeofreportedrestartunknown. OwnedfallbackSIGTERM0/parent+sampledpreparserabsence, no fullreader/nativeQuitpass. Source72/app/history retainedexact.

Generalfailureclass is interactivehumanvalidation outlasting a shortfinitefixture, plus synthetic-keyreaderobservability. Existinglegal7200s streamcopyfixture+physicalhumancommandschanges applicability: durationoutlasts900s trial withoutreload/seek, actualspeechwitness alreadyvalidated. PrepareONEfreshreader002 plan usinglongfixture/unchangedapp/source, separatequestions fornavigation/pause/play, twoactualburnins+typedcurrentstateperaction, same15minbound/resources. Rootreviewbeforerelease; noadditionalproducttests/build/readerframework. Percentagechatter baselinecomparison remainsread-onlysourcehypothesis, nota regressionverdict. Original002bloopdeadline remainsended; thisisCam's new reader-onlytask.

### Reader002 physical validation closeout — 2026-10-07

The existing7200s fixture lets human handoffs complete within the original900s trial (480.752s actual). Cam physically finds Position, moves to Pause, activates it, returns to Position and hears5.5%; root sees two unchanged38.417s/frame922 images, Play action and typedpause4. ExposedAX5.5% matches speech but does not match38.417/7200, so this is control-value speech evidence only: media-position accuracy and precision seek remain unqualified. PhysicalFindPlay/activate resumes; root images109.000/frame2616→207.167/frame4972 and typedplay3 confirm advancement. Cam hears complete understandable1.3%,1.4%,1.5% everyfewseconds. Main ordinary controls/navigation pass narrowly; visiblepreview/fullscreenreader untested.

Root ONECommand-Q exits0 withoutSIGTERM; historical004crash cause remains unresolved. VoiceOver restoredOFF/processabsent; Utilitywelcome1 restored, scripting0 unchanged. The read-only chatter scout finds baseline-identical slider/position update paths; inherited notification behavior is a hypothesis, without audible baseline comparison or causal trace. No source fix follows. Reader001 partial results remain preserved.

### Small main seek comparison — 2026-10-07T22:40Z

Cam authorizes bounded existing-app comparison and accepts deferring deeper intermittent shutdown work. Reuse existing async-seek condition research and exact012/016/legal300s fixture. Root native CUA slider-center actions avoid uncalibrated quarter endpoints while controls are faded; adapt two targets to150s, first forward then backward after continuedplayback. Source/time/state strict observer uses3s from observation start, recording actiondelay; this is settledcorrespondence, not historical input-to-arrival performance qualification. Actual burnedframes independently confirm seeks and>=5s continuation in both arms. Paused baseline18.875s/AX0.0630636 andcandidate11.958s/AX0.0399193 match rounded progress.

After slider actions both expose stale0.5/time labels while actualvideo advances. Baseline-identical ControlsBarCommon timeSliderAction sets dragflag on mouseDown, clears on mouseUp; updateTimeSlider returns while dragged. This is a concrete applicable source hypothesis for action-sequence staleness, without proving delivered events or cause of reader0025.5%. No physical-pointer, drag, subframe, otherposition/surface or universalAXaccuracy claim; no repair warranted. Queue visibility differs by preservedprofiles, so midpoint comparison is normalized, not geometry-matched latency.

Baseline normalQuit crashes on vout.events ResizeNotify/logging, matching015 namedframes/confirmedbaselineUUIDs, distinct from004conditionwait. Stop cohort/reassess, then one explicitly reviewed candidate-only continuation preserves failure and source/app/history; candidate normalQuit exits0. This establishes upstream resize-crash susceptibility, not004attribution or failure rate. No additional runtime/instrumentation. Evidence work/story005-seek-quit-comparison001/.

## Returned-main negative capture: bounded strategy check, 2026-10-07

The latest final-ui-closeout001 capture used the same main-window rectangle, AX slider rectangle, 60% point, observer and approximately 0.65-second independent capture timing as successful mainhover001. A coordinate or scale mismatch is therefore not supported by this comparison. The routed event identifies the owned application and AXSlider; it does not establish delivery to `VLCPlaybackProgressSlider.mouseMoved:` or the tracking-area owner.

Pinned slider source uses `NSTrackingActiveInKeyWindow`. Saved foreground/AX-focus observations establish application activity, not AppKit key-window state. `hoverIsAvailable` also checks `timelineControlsVisible`; that state was not recorded. Reparenting hooks reinstall tracking areas, so the current source does not demonstrate an omitted reinstall. The 7200-second fixture differs from the earlier successful 300-second fixture, but `reportHoverAtPoint:` ordinarily displays a time panel even when thumbnail preparation is disabled or unavailable. Absence of that panel weakens decode latency alone as an explanation. The 17-point-high stream crop covers the slider band, not the panel above it; the independent full-region image is the actual negative rendering evidence.

This is the established asynchronous event-delivery/tracking-state problem class described by the Apple Tracking-Area and Monitoring Events sources at the top of this note. Those contracts still fit; no alternate tracking framework or speculative product workaround is warranted. Decision: stop synthetic replay and preserve the negative result. The smallest different mechanism is a physical-pointer comparison on the same legal 300-second fixture before and after fullscreen, with actual rendered hover and ordinary controls observed. Human availability remains unanswered. If this reproduces with physical input, a later scoped diagnostic must distinguish key-window/tracking callback and control-visibility state before proposing a product fix. No runtime, build or instrumentation is released by this analysis.

The source and outgoing revision13 remain unchanged. Phase2 is incomplete; shutdown004 investigation remains user-accepted deferred. The current verifier ends after this find-only pass rather than generating another patch/hash cycle. Detailed comparison: `work/story005-returned-hover-diagnosis001/report.md`.

## Physical hover and focus confound, 2026-10-07

Cam's physical witness on the paused 300-second fixture is positive but transient: a thumbnail appears, then the whole playback controls and seek bar disappear after one or two seconds while stationary. Eight full-region captures contained the paused frame but no controls/pointer/panel. They missed the reported transient and do not prove no hover occurred. The known controller hides the preview with controls, while its fade timer and mouseOnControls guard are inherited from baseline; the witness does not prove why that guard did not keep controls visible. The XIB includes the time slider inside bottomBarView, so a proposed missing-slider hit region is rejected. A window-versus-parent coordinate mismatch remains unproved without actual runtime geometry/state. A bounded fresh Apple coordinate-doc fetch failed; installed SDK NSView.h confirms conversion APIs but not the current cause. No source fix was made.

CUA binding returned an empty Home window instead of the owned media window. Subsequent process inventory found additional PID65651, canonical016 without isolated arguments, started at16:55:04 Edmonton around the previous post-Quit AX observation. Its origin is consistent with UI observation relaunch, not independently traced. It existed during this trial and introduces focus ambiguity; it was not silently treated as the owned media process. Root confirmed empty Home, issued one CUA Command-Q without querying that app after exit, and ps confirmed no remaining VLC executable. Future native admission must distinguish process identity from shared bundle identity and avoid post-Quit app queries that can reopen the application. Existing exact-owned-view checks caught the mismatch before CUA input into the media trial.

Two different methods have now failed to provide steady returned-hover rendering proof. Stop instance-level replays under loop-verify's non-convergence rule. The smallest next audit should establish one actual application instance, stable foreground/key-window ownership, persistent pointer/view coordinates, and control-visibility/callback/hide transitions during the same physical hover episode. Capture must span the actual action rather than relying on a typed reply followed by a delayed burst. No new diagnostic instrumentation, build or runtime is authorized by this note. Human witness and pixel proof remain separate; no policy/skill change or source/package cycle follows.


## Focus/autohide source audit terminal, 2026-10-08

Problem class: independent native UI state machines using different coordinate and activation domains. Pinned source audit finds a concrete inherited modern-nib mismatch: File Owner bottomBarView is wired, controlsBar object's bottomBarView is omitted, but mouseOnControls reads the latter. Classic nib wires both, and migration can set classicYES; this source-reachable flaw is not established as the actual physical-trial cause. Separately the predicate compares window-base mouse coordinates directly to superview-relative frames. Library embedding/glass reparenting makes nonidentical spaces reachable; actual failed-run transforms remain unknown. Candidate hideControls sets timelineControlsVisibleNO, immediately hiding the preview with the controls.

Primary contracts checked by root: [Apple View Geometry](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CocoaViewsGuide/Coordinates/Coordinates.html), [Tracking Areas](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/TrackingAreaObjects/TrackingAreaObjects.html), plus existing Event Monitoring research above. Decision: proposed controller-owned bottom-bar guard and per-view point conversion; no application. Next measurement, only if separately authorized, requires one admitted exact process, actual slider-window key ownership, live layout/outlets/converted geometry, callback/visibility/hide reasons and full-region capture armed before physical entry. Existing external AX/CG receipts cannot supply all internal guards; another uninstrumented replay is not the next step. Local test in this audit is pinned source/nib comparison only, not runtime validation. Full findings/precise hooks: `work/story005-focus-autohide-audit001/REPORT.md`.

Previous60-minute run expired2026-10-07T23:46:45Z. Fresh GoAhead covered only00:19:13–00:34:13Z find-only audit, now terminal. Source/app/package preserved; Phase2 remains open. No runtime/build/source change released.


## Narrow correction and AppKit regression, 2026-10-08

Root reviewed/applied controller-owned bottom-bar protection and per-view window-to-local conversion. The11 actual-method AppKit cases pass, including five old failures; this demonstrates the predicate correction, not the prior physical fade cause. First failed undrained-pipe run remains retained; identical-binary direct-file run supports capture-plumbing diagnosis without stack proof. Python's [subprocess primary documentation](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait) supplies the general deadlock class. No product change was made for the harness obstacle. Historical R8/app/package proof remains historical after the one-file source delta. Diagnostic fields are planned only; full build waits for>=5GiB free and a separate release. [Evidence](../evidence/story-005/autohide-correction001.md).


## 2026-10-08: foreground ownership is a diagnostic boundary

The general problem is asynchronous foreground ownership during native UI setup. The one baseline-only acknowledged audio-channel probe stopped before its observer: an earlier focus observation was active, a later one inactive, with the same208,392/896×456 window geometry. No frontmost-other-app identity or activation notification stream was retained, so external focus theft, app self-deactivation and stale-observation causes remain unresolved. `work/story005-source10-audio-ack-plan001/runtime-terminal001.json` independently marks FAILED despite caller/cohort exit0: their inherited empty-AssertionError-string truth test incorrectly suppresses failure exit. Do not reuse exit0 alone as a verdict. Original evidence is immutable; no corrective replay occurred.

Bounded primary-source refresh: Apple [activate(options:)](https://developer.apple.com/documentation/appkit/nsrunningapplication/activate(options:)) describes an activation attempt and its return value, not a lease on later foreground ownership. [didActivateApplicationNotification](https://developer.apple.com/documentation/appkit/nsworkspace/didactivateapplicationnotification) supplies the affected NSRunningApplication and requires registration on NSWorkspace.notificationCenter. Official Markdown was read directly after the browser fetch rejected its MIME type. Established alternative to repeated activation/sleeps is to observe actual active/frontmost identity transitions alongside acquisition and decision timestamps. That would discriminate ownership loss; it is a future audit mechanism, not a demonstrated cause or released tool repair.

Decision: stop the current private native-harness iteration after startup identity/presentation, missing audio and now foreground setup barriers. No further cohort, diagnostic retry, focus forcing, timeout change, permission change or weakened performance criterion is released. All source10 headless/package gates and actual physical hover outcomes retain their narrow scope. The separate returned-main view-owner diagnostic remains reviewed but unbuilt, awaiting human availability; original admission and stop clocks remain. A future native setup audit should be separate from collecting benchmark arms, and any channel-only probe should justify whether it needs foreground geometry at all. No such change is applied here.


### 2026-10-08 — preserve effective build settings in private diagnostics

General problem class: expanded compiler/link argv is insufficient to reproduce a build when the wrapper changes environment-derived platform settings. The first autonomous diagnostic020 baseline link exited0 but failed strict LC_ID/UUID/backed-section equality before any diagnostic source compilation or GUI launch. Both plugins have the same LC_ID; production records minimum macOS27.0/SDK27.0, the private link minimum11.0/SDK27.0. All235 production objects record27.0;32 backed-section entries differ. This is a reproducibility failure, not a measured product regression. Original failed outputs remain preserved.

The direct recipe inherited MACOSX_DEPLOYMENT_TARGET=10.13 from the gate plan. Current normal Makefiles/config.status set that variable empty; Objective-C uses plain clang without an explicit minimum flag. C/C++ flags differ and cannot establish the Objective-C target. Historical package receipts did not capture the actual child target, so the wrapper explanation remains an inference. [Apple’s build-setting reference](https://developer.apple.com/library/archive/documentation/DeveloperTools/Reference/XcodeBuildSettingRef/1-Build_Setting_Reference/build_setting_ref.html) defines the deployment target and SDK-based default; the installed Apple ld.1 platform-version documentation describes minimum-version-dependent linker assumptions.

Decision: prepare one separately reviewed successor with the target explicitly empty, matching current normal Make metadata. Preserve every other input/flag and require actual identical baseline LC_ID, UUID and backed sections before diagnostic compilation. No equality waiver or semantic-equivalence claim. See work/story005-autonomous-diagnostic020-plan002/deployment-target-failure-classification.md and deployment-target-audit.READONLY.json for primary local evidence.

The environment-corrected003 link reproduces all35 backed sections, but the strict UUID gate still fails. A full read-only comparison accounts for the remaining difference: all60,344 symbol entries match; the entire symbol string table matches after one archive debug-path spelling replacement (`modules/../compat` versus normalized `compat`) and trailing null padding. Remaining headers differ only in UUID/string-table length/link-edit length/signature offset; signature page hashes independently verify. [Apple’s ld64 manual](https://github.com/apple-oss-distributions/ld64/blob/main/doc/man/man1/ld-classic.1) documents debug-map path normalization for identical builds. Preserve lexical archive spelling as well as resolved file identity in one separately reviewed successor; keep the UUID equality gate. Full evidence: work/story005-autonomous-diagnostic020-plan003/OSO-path-readonly-comparison.json. No runtime or product conclusion follows from either failed build.


### 2026-10-08 — diagnostic queries must respect reparented window classes

The first qualified diagnostic020 trial reached stable paused main playback, then aborted during ONE fullscreen entry before any hover move or capture. Its stderr and actual−6 exit identify NSInvalidArgumentException for `-[VLCWindow videoViewController]` inside S005Diag. This is an instrumentation-introduced failure; it does not establish a source10 regression or explain historical shutdown004. Original app, build and runtime receipts remain retained.

Local primary source VLCVideoWindowCommon.m creates a plain VLCWindow for custom fullscreen and reparents the controller view into it. An Objective-C cast does not supply the subclass getter. Decision: guard the diagnostic query by actual class and selector support, and log class/capability/ownerKnown explicitly; unavailable ownership must remain unknown. Preserve the independent controller argument and other existing trace fields. A fresh021 identity keeps used020 preferences and failure evidence intact. Also retain safely sampled helper identities before the fullscreen transition, rather than trying to reconstruct them after parent exit. These narrow diagnostic corrections need actual build/runtime qualification; no fade-cause claim follows yet.


### 2026-10-08T07:02Z — finite owned-PID automation instead of a live bridge

Diagnostic021 first runtime reached coherent paused playback but expired120s while waiting for root fullscreen setup; no hover input/captures. A post-expiry launch-capable CUA locator timed out and created a distinct default-profile instance. Sampled mainthread sits in persistent-state restoration/sidebar bookmark observation/open. This does not establish a thumbnail regression or exact I/O root cause. Original and unintended instance terminal receipts remain separate.

For asynchronous GUI lifetime control, primary Apple [AXUIElementCreateApplication](https://developer.apple.com/documentation/applicationservices/1459374-axuielementcreateapplication) creates an accessibility object for an existing PID; [AXUIElementPerformAction](https://developer.apple.com/documentation/applicationservices/1462091-axuielementperformaction) applies a supported action. Reuse established finite-state automation: one unique action from current AX, observe current owned CG/AX state before the next action, stop on ambiguity/timeout. This changes coordination mechanism, not observation criteria. Proposed minimal adaptation of existing observer only; no fresh runtime result yet. Used021 namespaces must be anchored and retained rather than deleted or described as virgin. Existing source/app/pointer ownership and120/300/45s bounds remain.


### 2026-10-08T07:16Z — exact nil application readiness state

The self-contained021 run002 retained actual exit2/empty stdout/two-line ownership refusal with appNil=1, nil identifier/path and finishedLaunching0 before activation. Exact OS process/start/executable remained owned; parent66936/helper66941 stopped via bounded SIGTERM0 and are absent. No fullscreen/hover input/capture. Independent audit2a2973283ad6094e238b0566b46e4623543ddc3d70f421941c0d36b2f01ce8e6 preserves source/apps/namespaces/old001/002 receipts. The earlier root-admission missing capture-region Boolean refusal is separately retained as prelaunch failure, not product evidence.

Apple [runningApplicationWithProcessIdentifier](https://developer.apple.com/documentation/appkit/nsrunningapplication/init%28processidentifier%3A%29?language=objc) explicitly permits nil. The [NSRunningApplication main-run-loop/property contract](https://developer.apple.com/documentation/appkit/nsrunningapplication?language=objc) does not guarantee eventual metadata registration or establish why this lookup was nil. Treat this as an observable pending state, not a proven hydration cause.

Selected standard finite-readiness adaptation: a caller-local read-only structured inspect keeps actual exit/stdout/stderr and exact OS identity before/after. Only the exact known nil refusal may remain pending in the existing8s startup envelope/150ms observation spacing. Wrong/incomplete nonnil identity, timeout, other exit, malformed output or changed OS identity stops. Existing exact Workspace ID/path, owned current CG, full prebind and ONEactivation remain mandatory before media/AX/input. No guard widening, timeout increase, observer compile or global harness repair. New separately named run003 preparation pending root review; original failed runs immutable. Local classifier counterexamples will verify classification only, not prove runtime applicability.


### 2026-10-08 — empty bookmark state as a bounded startup discriminator

General problem class: a fresh native application domain can initialize filesystem-backed sidebar defaults during UI setup, making a hover trial depend on unrelated permission/persistent-state work. Diagnostic021 trial003 captured a Documents access prompt in all three unique image groups, including before hover entry; no Allow/Don’t Allow was granted. The prompt’s presence does not establish its exact triggering call or explain earlier startup failures exclusively. Trial003 used AX fullscreen-button return, whereas the historical019 physical negative used Escape; source convergence at toggleFullscreen does not prove actual input/focus/timing equivalence. Its33 pinned captures and202 sampled hold callbacks are diagnostic observations, not an acceptance or fade-fix claim. Evidence: `work/story005-autonomous-diagnostic021-plan007/visual-trace-corroboration003.json` and the unchanged terminal audit/trace003 receipts.

Pinned source supplies a minimal future setup discriminator: `VLCLibrarySegment.m:845–850` seeds `defaultBookmarkedLocations()` only when `stringArrayForKey:VLCLibraryBookmarkedLocationsKey` returns nil. An explicit empty array is nonnil, so it avoids that default media-source preparse (`:72–94`) and the bookmarked-location existence loop (`:857–869`). `VLCLibraryWindowNavigationSidebarViewController.m:164–182` returns at count0 before watcher `open(..., O_EVTONLY)`. Therefore, a separately identified fresh private domain preseeded with `VLCLibraryBookmarkedLocations=[]` could test whether excluding default sidebar/bookmark work removes this particular setup confound, without altering product source, old profiles, or macOS permissions. Count0 is suitable for a fresh domain; it should not be generalized as cleanup of existing watcher resources. Other media/source/filesystem paths could still request Documents access. No such preference change or runtime experiment was performed by this read-only finding; root must separately review any candidate/domain and release the one experiment.


### 2026-10-08 — private qualification traversal cost

The022 clone transaction completed four copy/signature commands and398 loadable comparisons, then failed its110-second guard during repeated preservation inventory. The inherited guard recursively counted all997 clone files for every file visited by manifest(), making a single inventory quadratic. This is a private validator cost, not a VLC product failure. Preserve the original failed transaction.

A distinct read-only retained qualification used one payload phase-boundary scan, one old-app/namespace/history pass, cheap per-file free-space/deadline checks, one clone inventory, all398 backed-section/UUID comparisons and397 non-main byte comparisons, plus strict signature verification. It passed in2.639s under the same110s/1GiB/256MiB limits, with original failure and partial clone pinned. Apply payload checks at owned write boundaries; repeated read-only per-file checks need not recursively rescan an immutable owned app. This does not permit skipping preservation or accounting concurrent writes. Receipt: work/story005-autonomous-diagnostic022-plan008/qualification001/retained022-receipt.json (0df9b7296aeeecd33fe951928bc04783a7fdd3110b2f004cb5c572b66aa31e6d).

### 2026-10-08 — stale system permission dialogs

Root full-display capture shows a stoppedDiagnostic021 Documents-access request and another dialog behind it. App-only CUA screenshots/AX do not show this system-owned overlay, so app-only absence is insufficient setup proof. Actual running UserNotificationCenter was discovered by process path, but CUA refused control for safety reasons. No alternate interaction technology was used to bypass that refusal; no access was granted. Reader/native acceptance stays held until those dialogs are cleared. Root confirmed actual System Settings VoiceOverOFF and closed the inspection utility; reader settings were never changed.


### 2026-10-08 — permission identity during isolated native UI tests

General problem class: OS privacy prompts can invalidate automated focus/key/transition observations, while distinct test bundle identities and ad hoc signatures make permission persistence uncertain. Apple TN3179 (https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy) states that local-network privacy tracks code signatures, recommends an Apple-issued signing identity for reliable macOS identity tracking, and uses the main executable UUID; missing or shared UUIDs can behave unexpectedly. The official Markdown endpoint was read directly after the web renderer could not fetch its text/markdown representation. These retained metadata-only clones intentionally preserve their source executable UUIDs and use local signatures, so privacy-identity behavior is a disclosed test limitation, not a demonstrated VLC feature defect.

Local evidence: the audiochannel001 diagnostic completed background app-filtered audio acquisition after human clearing of earlier dialogs. The separately identified Diagnostic022 then produced a fresh Local Network permission dialog. Its first runtime failed on the original8s return-transition deadline after Escape was posted; that failure preceded root stop by8.364s. A prompt is a confound, not proof that it intercepted Escape or caused the timeout. Decision: retain current qualified app identities and wait for explicit human dismissal before any distinct future trial; do not grant permissions, reset privacy stores, change signing/security settings, or manufacture new identities as a workaround. A recurrence must be reported rather than treated as reliable permission persistence. Fresh matched playback still needs its original foreground/audio/geometry/cache criteria; acquisition-only success does not waive them.


### 2026-10-08T15:00Z — reuse one observable launch-readiness contract

The general problem is asynchronous readiness across OS process/RC, Workspace registration and CG/AX presentation. Latest production019 reader startup again failed before activation/media/VoiceOver with generic exact-domain/path stderr; that does not identify which guard operand failed. BaselineAudio001 startup succeeded in its separate34-frame trial. No generic refusal will be retried or retroactively relabeled.

Apple [NSRunningApplication](https://developer.apple.com/documentation/appkit/nsrunningapplication?language=objc) permits missing PID lookup and nullable identity metadata and documents main-run-loop semantics; [finishedLaunching](https://developer.apple.com/documentation/appkit/nsrunningapplication/isfinishedlaunching?language=objc) is an observable launch-notification state, not ownership proof. Root rechecked the primary pages and the systemic audit checked installed SDK headers. Cooperative [NSWorkspace launch](https://developer.apple.com/documentation/appkit/nsworkspace/openapplication(at:configuration:completionhandler:)) is an established alternative, but would change launch/ownership/environment semantics.

Decision: prefer reuse of the already qualified021 caller-local structured inspect/classifier plus its diagnostic-only refusal header on new private019/performance observer derivatives. Preserve exact allowlist/action guards and before/after kernel PID/start/executable/hash checks. Only exact structured appNil1/nilidentity/finishedLaunching0/expectedcwd/exit2 may remain pending within the SAME original8s budget; all other mismatches/timeouts/malformed results fail. Existing accepted CG/AX/prebind/ONEactivation criteria stay mandatory. finishedLaunching is recorded context, not a new admission requirement. No new probe, input engine, event framework or standalone startup runtime.

This is a HELD systemic proposal, not a product/source fix or proven recovery. Existing021run003 demonstrated accepted Workspace with CG[] then window, not a measured nil-to-ready transition. Latest019 cause and future progression remain unknown. Next verification is exact minimal diff review and meaningful classifier counterexamples before any separately released intended reader/performance run; no blind replay. See `work/story005-systemic-launch-readiness-audit001/REPORT.md` (bcc65ca2…).


### Prospective reader measurement correction — no retrospective pass

A known private-plan mismatch was identified before another reader run: it demanded visible OS pointer glyph and all ordinary title/buttons in the initial pair. Actual baseline frames hide the glyph, and the product controller deliberately calls `[NSCursor setHiddenUntilMouseMoves:YES]` at451. Ordinary title/button fading also exists upstream. The Story005 and verification-plan43–45 reader contract instead requires actual accessible title/role/value, focus and activation.

Root accepted an independent requirements judgment to correct only a NEW prospective reader protocol: exact native entry requested/actual coordinates, >=1s initial seekbar/image/time-caption pair with source/paused/focus/geometry correspondence, then actual VoiceOver Position→ordinary-control navigation and Play/Pause caption/cursor/typed/burnin/restoration evidence. Glyph and title/button visibility become retained observations, not prerequisites. No continuous/human stationarity claim is made. If preview hides during navigation, qualify only reader interaction starting from a visible preview. Old failures/inconclusive receipts, performance criteria and all resource/action/restoration limits stay unchanged. Review: `work/story005-systemic-launch-readiness-successor001/root-prospective-reader-contract-review001.json`. No runtime or product acceptance follows from this decision.


### 2026-10-08 — VoiceOver enabled setting versus operating reader

General problem class: an assistive-technology preference, application catalog and actual operating reader can disagree. Current reader startup succeeded, and root changed Settings VoiceOver OFF→ON with AX confirmation, but CUA catalog reported VoiceOver isRunning=false and the captured display showed no reader caption/cursor. The reader trial remains failed/unqualified; root restored the initial OFF state and settings. These observations establish neither a VLC defect nor why reader output was absent.

Bounded read-only process inspection at2026-10-08T15:16:29Z found existing VoiceOver Quickstart PID69348/PPID1/PGID69348, usercam, started WedOct7 15:14:25, executable `/System/Library/PrivateFrameworks/ScreenReader.framework/Versions/A/Resources/VoiceOver Quickstart.app/Contents/MacOS/VoiceOver Quickstart`; no main VoiceOver executable matched that scan. This old process does not prove today's toggle created a pending dialog, foreground presence or operating reader. Root then selected that known existing exact app path through CUA; inspection timed out with -10005/timeoutReached after5s, without AX/window or action proof. No launch, kill, relaunch or onboarding action occurred. Prior project research already records CUA catalog reporting not-running while an actual VoiceOver process ran; catalog absence alone is not process/onboarding absence.

[Apple's activation guide](https://support.apple.com/en-euro/guide/voiceover/vo2682/mac) supports both Command-F5 and Settings; it documents a welcome dialog where Return turns VoiceOver on, Space starts tutorial, V suppresses future welcome and Escape turns it off. No documented different activation backend or reliable recovery from this mismatch was found. Actual retained `work/story005-reader-applicability002/startup.json` records Command-F5 no observed change, then Settings OFF→ON and actual Quickstart UseVoiceOver action, followed by mainPID69341 and Cam hearing speech. Historical reader002 later has genuine navigation/pause/play evidence; it supplies no current preview-visible qualification.

Decision: do not repeat a known ineffective shortcut or reset processes/settings. Root's pending question asks only whether a welcome dialog is visibly present. If independently visible and separately authorized, ordinary Return/UseVoiceOver is the smallest supported completion of the demonstrated onboarding route; never post Return blindly to an unresponsive or unbound window. Verify actual reader output/cursor/caption responding to commands, not the switch alone. Apple's [NSWorkspace.isVoiceOverEnabled](https://developer.apple.com/documentation/appkit/nsworkspace/isvoiceoverenabled) describes current running state, but adding a probe is not proposed. The [caption panel](https://support.apple.com/en-lamr/guide/voiceover/unac078/mac) shows reader speech content, not proof of audible output.

Apple's [Screen Sharing settings](https://support.apple.com/en-mt/guide/voiceover/vo37c1caa6fe/mac) can hide remote visuals or silence remote speech independently; applicability to this CUA session is unknown. Async activation/onboarding, catalog limitations, remote routing and permission overlays remain hypotheses, not causes. No setting changes, new harness, retry or runtime release follows; independent performance work remains separate.


### 2026-10-08 evening — capture duration and foreground evidence

Performance006 stopped after83s during its first baseline arm: zero eligible arms, five unattempted. The observer requested65s but used650 relative100ms sleeps plus synchronous guard work; this concretely permits cumulative duration drift. Samples continued to the caller deadline without the normal stop marker. Actual cause remains unclear: loop delay, a blocked query, or guard-triggered stop await cannot be distinguished retrospectively.

Apple documents [Task.sleep](https://developer.apple.com/documentation/swift/task/sleep(nanoseconds:)) as waiting at least the duration; its [clock guidance](https://developer.apple.com/videos/play/wwdc2022/110355/) supports elapsed monotonic deadlines. Root accepted a minimal private-copy proposal with lifecycle markers, preparation only. Preserve65s capture,60s active interval, t0+70 caller deadline, every guard and scoring requirement. One compile, existing usage/dead-owner controls and one non-scoring baseline qualification are proposed; any failure stops. No007 six-arm benchmark release precedes reviewed qualification PASS, flushed summary and owned absence. Original source, binary and failed evidence remain immutable.

Root’s foreground discriminator records VoiceOverOFF and BringAlltoFront exposing app AXSettings rather than the whole Finder surface; no VoiceOver toggle occurred. The small Settings image does not support a StageManager conclusion. These observations establish neither reader operation nor the capture timeout’s cause. See `work/story005-capture-shutdown-audit006/BUILD-PLAN.HELD.md`.


## User-authorized AppleScript recovery,2026-10-09

General problem: native foreground/onboarding delivery disagreed with app-specific AX and accepted activation requests. AppleScript activation provided a materially different backend and actual whole-display Settings foreground proof. Apple recommends ordinary close/reopen for an app that does not work as expected ([guidance](https://support.apple.com/en-gb/102152)); this is general advice, not Quickstart-specific causal evidence. ONE ordinary quit of existingQuickstart69348 was followed by verified exit, ONE SettingsOFF→ON and visible welcome completion. MainVoiceOver63411 and response-linked tutorial caption then appeared. The tutorial close action timed out, but subsequent whole-display proof showed it gone with reader retained. No forcequit/preferences reset occurred. Causality remains uncertain; successful recovery does not prove the old helper caused startup failure. User scriptingTRUE is now the baseline. Native output/readback then timed out behind a visibly observed macOS Automation permission prompt, which is separate from the [VoiceOver scripting checkbox](https://support.apple.com/en-kw/guide/voiceover/cpvougen). Human grant/decline is pending; no bypass. This proves reader startup only, not VLC preview-visible navigation.


### 2026-10-09: reader observation interrupted by question UI

A human-ready capture first observed Finder Data rather than Utility. In a separate capture, whole-display Utility remained foreground while the Codex question announced “ChatGPT has new system dialogue” and the native VoiceOver cursor stayed on Codex Add files. This establishes an observation/input confound, not a VLC defect or the cause of all earlier failed navigation. Preserve both captures as inconclusive. For the next check, deliver a plain instruction before backgrounding Codex and observe without creating another question dialog; do not change the user's announcement preferences. Apple documents independently tracked keyboard and reader cursors: https://support.apple.com/en-lb/guide/voiceover/vo15534/mac . Actual control-linked directional proof and a sufficient finite input window remain required. Receipt: work/story005-voiceover-applescript-20261009/human-focus-capture-terminal001.json.
