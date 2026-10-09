# Story005 native acquisition ledger

This is partial native evidence, not acceptance. Baseline is pristine upstream master `2e358f3098c2f2b7621d1dc568de8b61ad786322` (253 registered tests; original app unchanged). Native interaction used its owned metadata/signature wrapper, ultimately `VLCStory005Baseline006.app` / `org.videolan.vlc.story005.nativebaseline.discriminator006`. Candidate native evidence below uses the duration-corrected packaged source tree `8ec1cdec6939c67eeb6bef0ff1bb035c168d0592`, UI source set `c3b0c1d4eda22b35bf96e8890e138854c8a96e68f232bc4deca8bfcef60c7642`, and isolated `org.videolan.vlc.story005.nativecandidate`. See `feature-duration-fixed-original-app-manifest.json` and `feature-duration-fixed-app-relocation-isolation.json`; later source/support-only revisions are not silently qualified by these observations.

| Surface or gate | Baseline actual acquisition | Current candidate actual acquisition | Remaining qualification |
|---|---|---|---|
| Main embedded | Actual public video and controls; later source switch updated video/title but stale controls | Actual public300s video, physical midpoint/wheel interaction; wheel video214s; stale labels after seek | Pure hover image/time; complete keyboard/reader and drag |
| Detached | Actual playing pointer midpoint core155→171; Pause/Resume without seek core194 | Not acquired on duration-corrected candidate | Whole surface, hover and control preservation |
| Native fullscreen | Entered; actual quarter core79; Escape returned normal | Entered via verified control; actualvideo156s; Escape restored normal | Fullscreen drag attempted but quarterseek not verified; hover/render/keyboard |
| Custom fullscreen | Entered; actual midpoint video150.9/core174; Escape returned normal | Not acquired on duration-corrected candidate | Whole surface, hover and control preservation |
| Preference default/save/restart | Clean launcher baseline; no feature preference expected | Rebuilt candidate default1, saved0→restart0, saved1→restart1 through CUA Settings | Visible disabled ordinary-time hover and enabled-preview behavior |
| CLI precedence | Not applicable feature control | Saved Settings1 remained1 with explicit `--no-macosx-timeline-previews`; eligible public input had no timeline worker/cache | Strictly runtime suppression diagnostic, not visible hover proof; Settings itself reflects saved config |
| Preparation/cache | No feature service | Real unique cache: version5,7samples/7targets then8RGBApayloads+manifest; worker80484 exactpublic input/parent79822 | Visible thumbnail; restart qualification and freshness |
| Same-URI restart | Not feature disk proof | Quit79822; empty7056 launch stopped before media because CUA reported Maclocked | No disk-hit/requalification claim |
| MP4/MKV/selected native ID/rotation | Main functional baseline publicMP4; media switch defect exposed | Current actual publicMP4 playback; MKV/native track selection/rotation unacquired | Use existing public-fixtures002 manifest/oracles; no render acceptance from compile/helper-only checks |
| Matched controls/playback | Story005 cohorts not acquired | Story005 cohorts not acquired |20responses/arm+20% allowance;3x60s actual preparation pairs, pending all-builds quiet/authorized harness; prove preparation remains active across interval |
| Hover enter/exit/fade/reparent | Initial baseline pointer-time samples are bounded earlier setup evidence; not all surfaces | No visible preview verified | Human alternate-hover-harness reply pending; CUA physical actions only currently |

Root independently observed candidate79822 through exact-path CUA: public long file/5:00 queue, AX1:57/position0.3926/Pause followed by actualvideo2:01.750/frame2922, normal queue and faded controls. No preview image was visible, so this corroborates actual playback/window identity only. A later large gray region was traced to the animated synthetic testsrc2 gray cross, not a hover panel.

Known baseline limitations remain explicit: generic AX slider0.5 did not demonstrate core seek (RC stayed22 paused); subsequent resume removed input. Actual physical playing seek and Pause/Resume without seek were stable. Physical seeks can leave stale labels/position, including old duration after media switch, while core/video advance. Candidate controlsbar is unchanged; the narrow hover fix uses fresh typed atomic context duration. None of these defects qualify latency or permit stale-source preview content.

Earlier candidate cache absence was test setup: an owned cache-domain symlink was rejected by SafeAncestors. Only this unique symlink was preserved by rename, target retained, and a real0700 directory created after app quit. Earlier observations cannot qualify disk cache. No daily app/profile, global settings or private media were modified.

At the current stop, CUA exact-path binding reported Maclocked before restart media admission. Exact owned PID7056 stopped through its guarded launcher, exit0; PID79822/helper80484 are gone. No UI retry, automatic unlock workaround or alternate input was attempted. The pending restart inventory retains payload/manifest hashes and mtimes. Details and attempted setup failures are in `native-baseline-status.md`; raw owned receipts/logs are under ignored `work/story005-native-baseline`. CUA screenshots remain in the tool transcript; filesystem screenshot artifacts were not fabricated through undocumented APIs.


Ownership correction: read-only follow-up found candidate PID794/PPID1 and preparser801, started06:42:34UTC with no command options. This predates guarded7056 restart06:43:06UTC and its later locked CUAgetApp binding. The preceding CUA Quit→post-quit AX observation timed out and may have auto-launched the same app; timing and no-option argv fit, but no direct launch-event attribution is available and user ownership is not excluded. No termination or UI probing was performed. The earlier exit verification covered only79822/80484/7056, not every candidate process. Exact ordering/uncertainty is preserved in `work/story005-native-baseline/nativecandidate/unattributed-process-794.json`.


## Resumed candidate007 acquisition — 2026-10-06 07:27 Edmonton

The prior locked/permission-pending rows are historical. Cam explicitly authorized
screen and mouse use and the Mac is accessible. Native owner uses metadata-only
`VLCStory005Candidate007.app` /
`org.videolan.vlc.story005.nativecandidate.discriminator007`, with exact source
equivalence and signature in `isolated-candidate007.json`. Its loadable main text
hash is `e466c3872433bb228ab04d555d607d83acf1f2ee7479728cf5b1c1be86fae309`.
Fresh owned profile/cache and exact launches preserve unproven PID794.

Actual display composites under `work/story005-native-baseline/` show:

- Main: `candidate007-main/main-display-composite.png`, pointer02:29,
  Keyframe02:28, burned148.000/frame3552 while playback is51.625/frame1239.
- Native fullscreen: pointer02:30, Keyframe02:30, burned150.000/frame3600;
  pointer exit hides the panel and Escape returns to main.
- Custom fullscreen: `candidate007-custom/custom-fullscreen-hover.png`,
  pointer02:30, Keyframe02:30, burned150.000/frame3600. Rapid movement ends at
  correct04:56/image296.000/frame7104, without earlier-image final state.
- Detached: `candidate007-detached/detached-hover.png`, pointer02:30,
  Keyframe02:30, burned150.000/frame3600.
- MP4→12s MKV: detached midpoint00:06 now gives Keyframe00:06,
  burned6.000/frame144; old150s pixels are absent.
- Red→blue video selection: actual Video menu changes preview color to blue;
  owned worker explicitly carries video-input-id2/video-count2. Immediate static
  color capture does not establish caption timing.
- Rotation: `candidate007-detached/rotation-hover.png` shows portrait image with
  cyan at top/red at bottom, pointer00:06 and Keyframe00:00 (10s GOP).

Root independently viewed main, custom, detached and rotation artifacts. Isolated
CGWindow panel captures omit image/caption while actual display composites show
them; preserve this capture limitation. Same-URI independent reopen establishes
persisted availability only so far, not causal disk-hit proof. Reader, remaining
control/pref/freshness gates and scored performance remain open. Native owner
retains exclusive desktop acquisition until explicit handoff.


## Resumed revision9 acquisition — isolated candidate007

Cam explicitly authorized screen/mouse interaction including the existing native hover harness, and root confirmed CUA availability. The retained-helper candidate source tree is `48a6b53f29d7f99ea410ba0e9d7085f7d9673acb` (59-file public series). Its verified clone is `work/story005-native-candidate/VLCStory005Candidate007.app`, domain `org.videolan.vlc.story005.nativecandidate.discriminator007`; complete manifests, signature and loadable-section equality are in `isolated-candidate007.json`. Original candidate and PID794 were preserved. The test pointer allowlist now requires both exact domain and app path; its original is preserved. Each acquisition used a guarded owned PID, empty-window proof before RC admission, fresh output/config/userdata and the real unique007 cache directory. The standard public300s MP4 copy is SHA c5dfcf4a710b8db66e5032a06b862da8dcc0e09df00c4a3597b5c0f0ea7b9e8a. Session SHA8bc46b is unused12s fixture inventory, not admitted media.

| Gate | Actual revision9 result | Evidence and remaining scope |
|---|---|---|
| Main preview | Pointer02:29; Keyframe02:28; burned148.000/frame3552 | `candidate007-main/main-display-composite.png`, exact23241/window3443/panel3449; pointer exit removes panel |
| Native fullscreen preview | Pointer02:30; Keyframe02:30; burned150.000/frame3600; Escape exit | `candidate007-main/native-fullscreen-hover.png`; no universal geometry or performance claim |
| Custom fullscreen preview | Pointer02:30; Keyframe02:30; burned150.000/frame3600; Escape exit | `candidate007-custom/custom-fullscreen-hover.png`, owned35276; rapid440→1300→1695 moves end pointer04:56/Keyframe04:56/burned296.000/frame7104 |
| Detached preview | Pointer02:30; Keyframe02:30; burned150.000/frame3600 | `candidate007-detached/detached-hover.png`, owned40367; actual image/time established on all four surfaces |
| Context/format |300s MP4→12s standard.mkv midpoint becomes00:06/Keyframe00:06/burned6.000/frame144 | `mkv-context-hover.png`; no previous150s image retained; small format fixtures paused just after admission, no paused seek/resume |
| Selected native track | Default red; native Video Track→synthetic-blue gives actual blue preview | `two-tracks-{red,blue}-hover.png`; helper argv selected input ID2/count2; initial static-color captures do not establish precise sample-caption timing |
| Rotation | Portrait preview, red bottom/cyan top; pointer00:06 and Keyframe00:00 | `rotation-hover.png`;10s GOP legitimately samples0; display orientation matches fixture contract |
| Disable during work | Saved preference0, actual ordinary00:06 time-only tooltip, timeline worker gone | `preference-off-time-only.png`; saved config explicit0. Current007 restart/CLI recheck still pending |
| Independent reopen | Same public URI reopened by35276; visible150s sample and identical retained cache payloads | `candidate007-custom/reopen-cache-result.json`; demonstrates persisted availability/integrity, not causal disk-hit counters or completed source-failure qualification |
| Ordinary click/keyboard | Main physical playing click yielded core71/state3; Space pauses/resumes on candidate and baseline | Separate receipts preserve actual source/core evidence; no scored response latency. Tab remained focused on window in both arms |
| Actual reader | Settings off→on, Quickstart Use VoiceOver, actual reader process43677; hover preserved AXWindow/keywindow focus before/after in both arms | Actual reader setup succeeded; CUA app inventory falsely remained not-running. One documented VO-Shift-Down→VO-Right→VO-Space attempt per arm left coreplay3/windowfocus unchanged. Control activation, VOcursor/spoken-label coverage remain unqualified. Settings restored off and43677 gone |

Capture discriminator: panel-only `screencapture -l` omitted the layer-backed image and sample caption, while a simultaneous actual-display region including only the owned app bounds showed both correctly. This applies to same-domain11135 and isolated007 blank panel captures; it is not a demonstrated decoder or product-layout fault. The display composites are actual screen captures, not reconstructed images. Exact public-demo originals/hashes are preserved in `work/story005-native-baseline/public-demo-original-hashes.json`.

Reader sources supplied by root: Apple's normal activation route https://support.apple.com/en-gb/guide/voiceover/vo2682/mac and documented group interaction https://support.apple.com/guide/voiceover/control-your-mac-with-keyboard-commands-vo2681/mac / https://support.apple.com/en-ie/guide/voiceover/cpvokys07/mac. The shortcut failed in both arms; standard Settings activation and welcome completed. No speech/privacy/security settings changed, and VoiceOver returned to its observed initial off state. `reader-comparison-007.json`, per-arm `reader-focus.json` and actual captures retain the precise limits.

Quiet handoff: owned11135,23241,35276,40367,42187,47495,55355 and their workers have exited. Unattributed794 remains, untouched. No post-quit CUA AX observation was used. Fresh007 cache persists at `~/Library/Caches/org.videolan.vlc.story005.nativecandidate.discriminator007/TimelineThumbnails`; all raw profiles/captures are in ignored `work/story005-native-baseline/candidate007-{main,custom,detached,reader}` and `baseline-{keyboard,reader}`. Latest detached geometry is global734,229,460,300, slider749,479,430,17, capture scale2. Root has received exclusive quiet handoff before OpenGL testing/performance setup.

Remaining gates: current007 preference disable/enable restart and visible CLI precedence; source replacement/failure and independent freshness/reopen qualification; full keyboard/reader activation/navigation; remaining click/drag/wheel/volume/fade/reparent edge cases; prospective validated adapter/classifier and20-response-per-arm controls plus three actually-active60s preparation pairs. No compile/service/old native evidence silently fills these gaps. The baseline paused-seek/resume and stale-label limitations remain explicit.


Reader precision addendum: actual reader-running hover/focus acquisition covers the detached surface only. Baseline55355 and candidate47495 both retained active key window global734,229,460,300 and AX focused role AXWindow before/after midpoint movement. Candidate `reader-hover.png` visibly contains150.000/frame3600 with Keyframe02:30; baseline shows only ordinary02:30 tooltip. Both actual screenshots show the VoiceOver outline around the hover time label. Therefore AX/keywindow stability is established, but VOcursor stability on a playback control is not established; pointer-following reader behavior may explain both. No reader coverage is claimed for the other three surfaces, and no spoken-label/control activation acceptance is inferred.

Media provenance correction: each candidate007 `session.json` now labels empty startup, unused12s inventory and actual admitted initial public300s source separately. Exact original files are retained as `session-original-inventory-uncorrected.json`. Original public300s generation manifest SHA4713dabb6676b09e0d1bd062c29d5a8323a98857019c3612e98ab9bf257a8cc3, generator SHA8f1574da92ba62c1da44abb3e38156f24a37406bc3d1f0a2c2eaffdbf9c3516d, and complete FFmpeg8 command/tool provenance remain in `work/story005-public-long001/manifest.json` / `feature-dependency-public-long-receipt.json`. Later public generator repairs changed its current SHA to7122c3a80b4f6ade690b47e8854a57d84bdda8684d144ea7e6a6dd4c274f00ec; it is not the exact original generator bytes. FFmpeg n8.0 `libavfilter/vsrc_testsrc.c` lines678-692 and839-852 explain testsrc2's built-in VGA bitmap font and time/frame drawing (https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavfilter/vsrc_testsrc.c). No external font, private media or fake overlay was used to create the burned-time demonstration.


## Bounded candidate007 functional follow-up

Acquisition ended after 801.807 seconds of its prospective900-second budget. `work/story005-native-baseline/candidate007-followup/followup-result.json` retains exact session archives, screenshots/hashes, source mutation receipts and RC observations. This addendum corrects the prior header: the packaged production tree is8ec1cdec6939c67eeb6bef0ff1bb035c168d0592; the public revision9 tree48a6b53f29d7f99ea410ba0e9d7085f7d9673acb contains subsequent support-only changes and equivalent runtime. Clone equivalence is `isolated-candidate007.json`, not the previously mis-scoped/nonexistent revision9 isolation pointer. Session originals are preserved beside corrected receipts. The actual unique real cache root is `~/Library/Caches/org.videolan.vlc.story005.nativecandidate.discriminator007/TimelineThumbnails`, version5, with non-symlink ancestors; no work-cache or symlink assumption applies.

Saved0 was observed in Settings after a real same-profile restart without `--ignore-config`; `off-restart-hover.png` shows ordinary02:29 with no image. Saved1 was then observed at the next restart, while explicit `--no-macosx-timeline-previews` produced `cli-off-hover.png` time-only despite the saved checkbox1. Removing the override at another restart gave `on-restart-hover.png`: pointer02:29, Keyframe02:28, burned148.000/frame3552. These are actual visible preference/restart/CLI precedence checks, not config-only inference.

Only the owned `public-followup.mp4` was changed. Original public300s bytes were preserved by rename to `public-followup-preserved.mp4`, with SHA c5dfcf4a710b8db66e5032a06b862da8dcc0e09df00c4a3597b5c0f0ea7b9e8a. On disappearance, reenter immediately showed02:29+Unavailable with no image while video continued; after16seconds controls had faded, and fresh reenter again showedUnavailable. Replacement used public fixtures002 standard.mp4 copied exclusively to the absent same owned path, then clear/reopen: `replaced-source-hover.png` shows pointer00:05, Keyframe00:04, burned4.000/frame96, queue00:12; prior148s pixels are absent. This demonstrates failure clearing and changed-byte reopen requalification. Checking source/provisional15-second expiry did not naturally occur, so its exact native deadline remains automated scope. Persisted reopen remains availability/integrity proof, not a causal disk-hit measurement.

Actual playing wheel seek, volume wheel and Space pause/resume were exercised on all four surfaces: main97490 (RC78/pause, volume60; stale AX time labels persisted), native fullscreen97490 (physical midpoint click reached about160s; wheel back gave100s, volume100, keyboardPause/Resume), detached15820 (wheel gave65s, volume60, Resume RC74/play3), custom fullscreen18899 (wheel gave87s, volume100, Resume RC103/play3). Escape exited both fullscreen modes before stopping. Native fullscreen click screenshot and detached control screenshot are retained; controls naturally faded in later no-input captures. Main drag using doubled screenshot coordinates did not establish a seek; one native drag with alternate relative mapping changed Play state and ended RC117/paused, so neither is accepted as drag proof. No further coordinate retries were made. Exact click/drag/fade edges on detached/custom remain unacquired; no universal or latency acceptance follows from these functional checks.

Quiet checkpoint: all follow-up-owned PIDs74982,83554,91783,97490,15820,18899 exited through exact launcher ownership, with per-phase logs/config/argv preserved. Unattributed794 remains untouched.007 cache and all originals remain preserved. No native source changes, global settings, private media, additional reader trials or scored performance acquisition occurred. Remaining gates are practical drag and detached/custom click/fade edges, full spoken/control reader acceptance (actual detached reader focus proof remains narrow), causal disk-hit/exact provisional deadline, and root-reviewed pilot then20-response-per-arm and three active60-second playback pairs.


## Unscored adapter calibration — first setup failure

Root released a ten-minute, one-attempt-per-case live calibration after independent review. Fresh output `work/story005-master-calibration-20261006-0800` retains `freeze-verification.json`: all four adapter source and two compiled observer hashes matched reviewed freeze b6554cd5a7acb9b56cd232bf1cc5717b3efc85e2cbbd7487326b44a69f7d6ccb. A guarded baseline006 empty launch ownedPID42243 started with fresh config/userdata, privacy flags and no media. The first exact-path CUA binding returned `Computer Use server error -10005: timeoutReached` after9.4196seconds. Per the prospective stop rule, no retry/fallback, media admission, observer launch, classifier/input/parser/cache/audio acquisition or score followed. All remaining cases are explicitly unattempted in `calibration-stop.json`. Exact launcher-owned42243 exited and `owned-exit.json` independently confirms PID absent; no post-quit CUA call. Candidate007/011 and reserved008/009/010 were not launched by this pilot. This is a tool/setup failure, not a product control/performance failure. Desktop is quiet and returns to root for its next decision.


Calibration cause correction: the original baseline42243 stderr explicitly says `Unknown option --no-video-autoresize`; the established/source-declared option is `--no-macosx-video-autoresize`. Thus the launcher exited before binding. The downstream CUA timeout does not demonstrate an availability outage. Root's read-only process trace found no-option baseline42789 starting08:16:43, consistent with getApp auto-launch after the owned process exited; its ownership remains unproven and it is preserved untouched alongside794. Original launcher, error and initial classification receipts are retained. A corrected prospective launcher and option-source review confirm all17 flags against pinned master declarations; no revised launcher was run. `prebind_guard.py` refuses an exited Popen, absent/wrong-owner RC socket, wrong executable, nonempty/non-stopped RC, missing visible owned normal window or missing exact AXWindow title before allowing a single CUA bind. Offline mocked dead/media/missing-status cases refuse without spawning apps. Root will release freshbaseline012 and a reviewed revised pilot separately; no006 retry occurred.


## Corrected calibration0825 — pre-bind socket refusal

Root approved one corrected run with freshbaseline012 after reviewing option declarations and pre-bind guards. The paused-cohort freeze aa401b868ea86bb958c02f95ff46a4ec572db1b2b9d554441ce0aab6a3659b2f and all source/observer hashes matched. Exact012/011 domain+app paths were added to the test-only pointer allowlist, with prior source preserved; compiled helper path/hash stay in fresh output `work/story005-master-calibration-20261006-0825`. Actual owned VLC child57285 used corrected functional option names and an eight-second bounded pre-bind wait. `oldrc` rejected its124-byte RC socket path with `rc-unix value is longer than expected`; pinned `modules/control/cli/cli.c` lines877-893 require path length strictly below sockaddr_un.sun_path capacity including null. The pre-bind guard refused the missing socket, propagated startup failure through launcher exit1, and stopped only its owned child (child exit0, independently absent). No CUA binding, media admission, calibration input, observer/capture/parser, candidate007/011 or reserved008–010 launch occurred. All remaining cases are preserved unattempted in `calibration-stop.json`; original launch/logs remain intact. This is another launcher-precondition failure, not native feature/observer failure. Next setup requires a prospectively validated short owned socket path, as established functional f7.sock/c.sock used; no retry occurred in this attempt. Unproven794/42789 remain untouched, and desktop is quiet.


## Corrected calibration0828 — interruption and original bound expiry

Four unique74-byte sockets b1/c1/b2/c2 under real0700 `work/mc0828` were reviewed before launch; prior socket plans remain preserved. Root released one ten-minute pilot using the unchanged paused-cohort observer freeze. Actual owned baseline012 PID82223 and candidate007 PID82282 passed alive/executable, short RC socket, empty stopped5/no source, visible CG normalwindow and exact AX empty-title pre-bind checks; one CUA binding per app succeeded. Public300s long-preparation.mp4 was admitted by RC to each. Their subsequent read-only pointer inspect/AX queries returned empty owned onscreen windows/sliders for both, while stderr records native video presentation. No visible playing control readiness, actualPause state4, shared geometry/centers or rendered-feedback qualification was established before an intentional turn interruption. Empty preflight CG frames were207,392,898,456, so the historically proposed208,392,896,456 geometry was never silently accepted or used for observer input.

On Cam's Continue, the first read-only recovery inspection found650.386 seconds elapsed and−50.386seconds remaining on the original600-second bound. Both launcher lifetimes had already ended; owned82223/82282 exited0 and independently verified absent. No relaunch/reset, post-quit CUA, observer or calibration input occurred. All classifier/ownership-refusal/RC-counter/short screen-audio/cache cases are explicitly unattempted in `work/story005-master-calibration-20261006-0828/interruption-budget-stop.json`; raw readiness/session/logs remain. Candidate011 and reserved008–010 were never launched, and unproven794/42789 remain present untouched. The pilot is inconclusive setup/interruption evidence, with no product/performance score. Desktop returns quiet to root for its next bounded decision.
