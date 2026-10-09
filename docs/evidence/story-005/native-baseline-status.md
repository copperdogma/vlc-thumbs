# Native master baseline — setup stopped before UI acquisition

Pinned unmodified source: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
This is a baseline setup result, not native functional qualification or a feature
regression. All four surfaces, hover/time, seek/fade/reparent and keyboard/reader
behavior remain unacquired.

## Isolation and provenance

Original `work/story005-master-baseline/VLC.app` manifest outputs remain
byte-identical. `native-baseline-setup.json` contains expected/actual hashes.
An APFS clone at `work/story005-native-baseline/VLCNativeBaseline.app` differs only
in `Contents/Info.plist` and `_CodeSignature/CodeResources`; all executables,
plugins, resources and other files remain byte-identical. Owned Info.plist uses
`org.videolan.vlc.story005.nativebaseline`, removes document/URL associations,
and disables automatic updater checks. Deep strict ad-hoc signature verifies.

Pinned `src/darwin/dirs.m:190-225` derives config, user-data and cache directories
from the actual app bundle identifier. `src/config/dirs.c:30-47` accepts
`VLC_USERDATA_PATH`; it was set to the owned work directory without changing HOME.
`VLCLibraryController.m:439-442` gates library acquisition on the media-library
flag. Full argv/PIDs are retained in launch receipts. Library, recent tracking,
network metadata, external-player control, media keys, Apple remote and status
icon were disabled. Unique cache directory was briefly symlinked into owned work;
the mapping was removed after cleanup. The test may create defaults in its unique
macOS domain; it does not target the existing VLC or preview defaults domains.

## Acquisitions and blocker

1. Direct file admission at startup, PID74977: process aborted with
   NSInvalidArgumentException, nil value inserted into `_voutWindows` by
   `setupVideoOutputForVideoWindow:withVlcWindow:`. Source shows embedded video
   uses `VLCMain.libraryWindow`, created by applicationDidFinishLaunching.
   This suggests asynchronous startup readiness as the problem class; causation
   is not established. Stderr and argv are preserved as `launch-001-*`.
2. Readiness-gated empty queue, PID75431, `--no-playlist-autostart`: process lived
   in `[NSApplication run]` (bounded sample retained), but returned no visible
   owned windows/AX sliders and failed activation. No fixture was added.
3. Cua native app acquisition returned: “The Mac is locked and automatic unlock
   could not unlock it. Ask the user to unlock the Mac manually before
   continuing.” No lock/security settings were changed and no unlock attempted
   through alternative input.

Only exact owned PID75431 was terminated by its launcher cleanup; its absence
was confirmed. PID74977 had already exited. Existing user preview PID42247
remained alive. Minimum observed free space during this task was approximately
3.54GiB, above the 1GiB reserve.

## Bounded next acquisition

After the user unlocks the Mac, recreate only the owned cache mapping, run the
empty-queue launcher, and require an actual visible owned main window before
adding legal synthetic media through RC. Capture the main surface first; derive
slider/window coordinates from actual master AX and pixels. Then inspect detached,
native and custom fullscreen, verifying target PID ownership after transitions.
If the startup crash reproduces after visible readiness, revisit lifecycle
framing rather than adding retries or patching baseline source.

The adapted `tests/story-005/native-pointer.m` retains the old helper's exact
bundle ownership guard with the new unique ID. The Story004 feature runner is
inapplicable as-is: it requires the old development ID, 3.0 trace event hooks,
preview panel dimensions and fixed surface selection. Its existing RC and owned
capture patterns can be reused; master surface mapping and actual pixels must
replace those assumptions. No matched20-response or three60s playback comparison
was run. No VoiceOver launch or accessibility pass is claimed.

A bounded Apple AppKit lifecycle documentation lookup was attempted; its JS page
and linked Markdown could not be ingested by the web tool. This is an unavailable
external source, not evidence. The readiness-gated experiment was chosen from
pinned local launch/window lifecycle source and the existing harness pattern.

## Resume availability observation

After Cam's explicit resume, one read-only CUA `getState()` returned the normal
app/browser inventory in2.25seconds with no lock/automatic-unlock error. No app
was launched or selected, and no pointer/key action or installed-preview
interaction occurred. This clears the prior inventory availability failure;
actual owned baseline AX/screenshot availability remains to be established at
launch. No feature/surface qualification follows from inventory success.
The separately observed disk reserve remains below1GiB, so no native launch,
NAS copy or helper acquisition was attempted. The isolated baseline/candidate
four-surface and matched-comparison protocol is unchanged. No polling was done.

## Actual unlocked acquisition — bounded partial baseline

Guarded launch003 ownedPID2678 reached visible mainwindow2302 with an empty queue.
CUA read its actual AX tree; adding legal standard12sMP4 through RC then established
native video/controls without the earlier nil-window crash. Actual pointer
midpoint/right hover showed ordinary00:05/00:11time panels, and leaving removed
the child time window. Owned screenshots and window/PID/action receipts are
`work/story005-native-baseline/main-hover-actions.json` and `main-*png`.
Cua slider click changed Position from0.0104166to0.5; the subsequent Right key
left position unchanged, with actual focused roleAXSplitGroup. This is not a
keyboard accessibility pass. A Cua coordinate drag acquisition was inconclusive:
controls disappeared/end-of-short-media occurred and the wheel action rejected a
stale element ID. These attempts are unscored, not successful drag/wheel proof.

Changing to the existing synthetic300sMP4 updated the playqueue duration05:00 and
video frame, but the progress slider remained disabled/stale12sstate at0.5 even
after brief actual play/pause. This baseline behavior/setup problem is retained,
not attributed to the feature. Cua then entered actual native fullscreen by its
full-screen button; screenshot/AX showed same controller and video view, with the
stale timeline. AX fullscreen rect1698x17at15,1067 is in `native-ax.txt`. The Cua
fullscreen screenshot is tool observation; there is no separate saved local image.

Launch004 requested detached mode in the same unique defaults domain. Empty
startup was observed, but inherited native-fullscreen restoration state carried
into the session. After legal300sRCadmission, Cua AX timed out21seconds; owned
window screenshots/sample/argv/stderr are retained as `detached-failed-*`,
`detached-timeout-sample.txt`, and launch004 receipts. Session was terminated through
its exact owned process and child disappearance confirmed. PID42247 remained alive.
The launcher now checks the1GiBreserve continuously while its owned process runs.

Native setup must resolve private saved-state/defaults and reliable media readiness
before new variants or matched cohorts. Main time-hover and actual native-fullscreen
entry are observed; detached/custom fullscreen, reliable seek/drag/wheel/keyboard,
reader behavior, fade/reparent and four-surface acceptance remain unqualified.
Root selected a bounded source/research pass before another UI acquisition. No
matched20response or three60scomparison was started. Headless NAS comparison
followed only after owned baseline cleanup and localH1gate release.

### Discriminator005 preflight sequencing failure (2026-10-06 04:30 UTC)

The initial disk assertion failed, but the enclosing shell did not fail fast and continued signing the existing owned wrapper, compiling the existing test pointer helper, and launching the old-domain empty session. The continuous launcher guard stopped owned PID64110; subsequent `ps` shows it absent and installed preview PID42247 present. No media was admitted and no fresh-domain UI discriminator was acquired. The domain remains `org.videolan.vlc.story005.nativebaseline`. Raw executable hashes differ after signing, while the Mach-O code section hashes match the original baseline. This is a setup failure, not native feature evidence.

The launcher now checks its 1GiB reserve before profile/cache creation, log opening, or process creation. A mocked 4096-byte availability test refuses launch with zero process, profile-directory, symlink, and log-open calls. Future dependent setup commands must use one checked orchestrator or a fail-fast shell. Failed logs/session, process/space, raw/code integrity, and mock receipts are preserved under ignored `work/story005-native-baseline/guard-failed-discriminator005-*` and `launcher-low-space-mock.json`. Available space was 801136640 bytes at the recorded process check. Runtime remains on hold.

### Fresh-domain discriminator005 (2026-10-06; receipt UTC timestamp)

The owned wrapper was changed to fresh domain `org.videolan.vlc.story005.nativebaseline.discriminator005`, with the prior Info.plist and test sources preserved, and ad hoc signed. The launcher checked the 1GiB reserve before profile/log/process writes and continuously thereafter. Unique preference, saved-state and cache paths were absent before launch; userdata also used a new owned directory. All executable `__TEXT` sections match the original baseline after signing; raw signed executable hashes are separately recorded. No original baseline or installed app was modified.

Owned PID54095 opened normal empty library window2626 at896x456 (queue0), then one owned legal300s `preparation-base.mp4` opened detached window2634 with04:59 remaining and ready sliders. Actual pointer movement to midpoint showed02:30; clicking set both slider values0.5 and the main elapsed label02:29. Detached elapsed remained stale00:00. The central play/pause action sequence then removed the detached window and controls; final RC returned input stopstate5. A subsequent fullscreen click at the old window coordinate was refused by the PID ownership guard, so no unrelated UI received that click and no fullscreen was entered. The owned launcher stoppedPID54095 and exited0.

This excludes inherited fullscreen restoration as a necessary cause of initial detached admission for this run; it does not establish why the later playback transition stopped input. The existing recipe-incomplete seed remains supplementary. CUA inventory saw the fresh ID but binding rejected the ID and fullpath resolved cached old metadata, so the previously authorized exact-PID pointer/AX helper supplied the actions and captures. Evidence under ignored `work/story005-native-baseline/discriminator005-*` includes empty/detached/hover/afterseek pixels, trees/AX, argv/logs/RC, and integrity/result receipt. No four-surface, keyboard/reader, playback or candidate qualification is claimed. Following the one-failed-discriminator rule, no new UI session was launched.

Discriminator005 trace clarification: launcher session `fixture_sha256`8bc46b... is inventory of unused12sstandard.mp4; startup was empty. RC admitted300spreparation-base.mp4 SHA0251953d.... Afterseek tree05:33:44.668UTC has bothsliders0.5, main02:29 and detached stale00:00. Following first central coordinate click964,379, tree05:34:00.845UTC already has bothsliders0.99675846,04:59/-00:00 and Pausecheckbox1. Second identical click and tree05:34:01.416UTC then show only one window and no controls. Therefore nearEOF preceded the second action; it was not a confirmed PauseAXpress and EOF/action causality remains unknown. All actions were coordinate pointer single clicks, no AXbuttonpresses. Midpoint move/click964,487 was not an endpoint action.

### Fresh-domain ordinary-play discriminator006

Fresh isolateddomain`org.videolan.vlc.story005.nativebaseline.discriminator006` opened an empty normal library window2768 (screenshot retained), then admitted newly generated public300sMP4 SHAc5dfcf4a... withordinaryplayingstart (`--start-paused`removed). Monotonic trace records RCtime0then5 over5s, length300,is_playing1. There was no observed initial clockleap. After admission, exact-PIDAXtree returned no windows/controls and onscreenCGinventory was empty, although focused-windowAXreported460x300at735,229. One owned-app reactivation returnedtrue but no observable controls. CUAinventory remainedavailable and identifiedthefreshID. BeforeadmissionCGwindowX-1581 differedfromAXX208, consistentwithvisibility/Spaceuncertainty, notprovedcause. NoverifiedPausecontrolwasavailable, so Pause/seek/resume/fullscreenwere not attempted. Ownedstoprequested; receipts are`work/story005-native-baseline/discriminator006-*`. This is an incomplete UI acquisition, not clock/feature qualification.

### Registered same-domain006 CUA binding attempt

The exact owned wrapper directory mtime was updated, and Launch Services `lsregister -f` completed with exit0 for that path only. Document and URL claims were absent. The same006 domain and profile launched owned PID55341 with an empty queue and ordinary playing flags. CUA binding by the new ID still returned “Invalid app”; binding by the exact path still resolved the old `org.videolan.vlc.story005.nativebaseline` and reported “Running application not found.” No Mac locked message was returned, and no media was admitted.

This establishes continued tool identity binding failure after the bounded registration repair, not a physical UI result. The owned launcher exited0 and PID55341 is absent. Registration, launch and result receipts are retained. No global Launch Services reset, default-handler change, profile variant or product change was attempted.

### Fresh-path binding and verified paused-seek reproduction

Renaming only the owned wrapper to `VLCStory005Baseline006.app` retained the same006 domain/profile and exact signed executable bytes. Registering that exact new path succeeded. CUA immediately bound the new path and observed the normal empty queue window, supporting a persistent tool path-cache explanation for earlier binding failure.

The newly generated public300sMP4 (SHA c5dfcf4a...) played normally: CUA elapsed00:03 then00:19, rate1.0x; RC time15, length300 and playing state3. Verified CUA Pause73 changed to Play(on) at00:22. A CUA midpoint click on slider4 set value0.5 while elapsed remained00:22; RC confirmed pause state4 and time22. Verified CUA Play17 then immediately removed the detached window and controls, returning the library with queue1. Thus the paused-seek/resume failure reproduces with the public fixture and confirmed Play/Pause controls; the old seed and ambiguous center clicks are not necessary causes. No fullscreen was attempted.

CUA action monotonic timestamps are saved in `path006-cua-actions.json`; Python RC timestamps use a separate monotonic origin in `path006-trace.json`. Pause-to-midpoint was15.236s; midpoint-to-resume11.291s; resume action-to-observation134ms. Tool screenshots show empty library, paused controller and returned library. Full launch, registration, RC, logs and result receipts are under ignored `work/story005-native-baseline/path006-*`. Owned stop was requested immediately after preserving the failure. This remains baseline behavior/setup evidence, not a candidate feature regression.

### Actual pointer playing-seek and four-surface observations

CUA physical midpoint click on the playing detached timeline reached core time155, then171 after the bounded ten-second observation. Pause/Resume without seeking preserved playing state and core time194. Native fullscreen entered through its verified control; a physical quarter seek reached core time79 and Escape restored normal controls. A separate ordinary embedded session entered custom fullscreen through VLC's Enter fullscreen control, physically sought midpoint (video150.9, later RC174), and exited via Escape. Main embedded, detached, native and custom fullscreen surfaces are therefore observed, with confirmed core pointer seeking on the latter three. Hover-only, reader, exhaustive keyboard and matched performance proof remain pending.

After physical seeks, timeline labels/value stayed stale while video and RC time advanced. Following a300s-to12s media switch, title, queue duration and video updated to standard.mp4/00:12/00:04.9, while the slider was disabled at0.5 and time buttons retained00:21/-04:38 from the earlier300s input. This baseline defect remains explicit. It cannot justify a candidate preview using stale duration or stale source pixels. Detailed receipts are `playing-pointer-*`, `embedded-custom-*` and `baseline-four-surface-partial.json` under ignored work. Both sessions left fullscreen before quitting through CUA.

### Candidate initial preference observation before duration repair

The isolated candidate bound through CUA, opened with an empty queue, and showed Show timeline thumbnails checked1 in Settings. Cancel closed Settings; no preference save or media admission occurred. The first test RC socket path exceeded the Unix-domain length limit, explicitly reported in stderr. A harness-only shorter owned socket path retained the app, ID and profile; that second empty launch was stopped when root requested a candidate rebuild for atomic context duration authority. Both owned sessions exited; default preference evidence belongs to the old candidate freeze and is not functional thumbnail proof. Receipts are under `work/story005-native-baseline/nativecandidate/failed-long-socket-*`, `socket-repair.json` and `pre-duration-rebuild-*`.


### Rebuilt candidate preferences, real cache and native surface observations

The released duration-corrected candidate uses `org.videolan.vlc.story005.nativecandidate` and the same owned bundle/profile. CUA Settings observed default Show timeline thumbnails checked1, saved disabled0, then a restart without `--ignore-config` retained0. Saving enabled1 and another restart retained1. A separate explicit `--no-macosx-timeline-previews` launch retained saved Settings checkbox1 but admitted the eligible public300sMP4 without a timeline worker or cache; this is runtime diagnostic evidence of CLI blocking, not visible hover precedence proof. The saved config and exact argv/session receipts are preserved under `work/story005-native-baseline/nativecandidate/`; `preference-lifecycle.json` separates these observations.

The initial unique cache-domain symlink was rejected by the production SafeAncestors policy. Root authorized preserving only that owned symlink and its target, then creating a real0700 directory at the exact unique cache path. All parents were verified real directories. `cache-migration.json` records the setup change. Earlier absent-cache/RAM-only observations cannot establish disk behavior. With the real directory and enabled preference, PID79822 admitted public `long-preparation.mp4` SHAc5dfcf4a...; helper80484 opened that exact input. Read-only observation confirmed version5 manifest with7samples/7targets and7RGBA payloads; later pre-restart inventory contained8payloads plus1manifest. This establishes actual preparation/cache creation, not visible preview qualification.

CUA observed the actual moving public fixture in the main window. Verified Pause/Resume without seek worked. Native fullscreen entered through its verified fullscreen control and Escape returned to the normal window. A physical fullscreen drag attempted1792,2085→860,2085 did not establish quarter seek: subsequent RC163/play3 and AXposition0.519 were inconsistent with that requested target. The failed attempt is retained in `native-fullscreen-observation.json`; no drag or hover success is inferred. Subsequent normal-window wheel changed position0.719 and actual video to214s/frame5138, while labels remained stale02:46/-02:13, matching the disclosed baseline stale-controls class. A large gray shape in one fullscreen screenshot was initially suspected as a panel; its change to the fixture's gray cross in the next frame disproved that interpretation. No visible preview was observed.

CUA quit PID79822 after leaving fullscreen. The guarded same-media restart launched only an empty queue as PID7056; exact-path CUA binding then returned “The Mac is locked and automatic unlock could not unlock it. Ask the user to unlock the Mac manually before continuing.” No media was admitted or alternative input attempted. The owned launcher stop marker terminated only PID7056 and exited0. `restart-lock-block.json` and `disk-before-restart.json` preserve this unacquired restart attempt. Same-URI disk qualification, remaining candidate surfaces/formats/reader, pure hover and matched performance remain open. Candidate runtime is stopped pending a fresh user unlock observation. No unrelated app, daily preferences or global cache was changed.


Ownership correction: read-only follow-up found candidate PID794/PPID1 and preparser801, started06:42:34UTC with no command options. This predates guarded7056 restart06:43:06UTC and its later locked CUAgetApp binding. The preceding CUA Quit→post-quit AX observation timed out and may have auto-launched the same app; timing and no-option argv fit, but no direct launch-event attribution is available and user ownership is not excluded. No termination or UI probing was performed. The earlier exit verification covered only79822/80484/7056, not every candidate process. Exact ordering/uncertainty is preserved in `work/story005-native-baseline/nativecandidate/unattributed-process-794.json`.
