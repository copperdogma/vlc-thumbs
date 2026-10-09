# Story005 native port risk inventory

Read-only source/SDK inventory on2026-10-05, against upstream master
`2e358f3098c2f2b7621d1dc568de8b61ad786322` at
`work/upstream/vlc-master-story005`. No product-source edits, compilation, UI
interaction or new architectural selection. This bounds a possible port if
helper9 qualifies; root retains the integration decision.

## Retained boundaries and concrete compatibility risks

| Local owner | Reusable behavior | Exact port risk / required decision |
|---|---|---|
| `VLCThumbnailService` | Main-thread intent/completions, separate cache/decode/metadata lanes, finite preparation, latest demand, cancellation generations,15s source qualification,32MiBRAM/256MiBdisk | Its context/request/response contracts use `videoOrdinal` and `videoCount`. A master canonical ESID cannot silently become an old integer `videoID`/ordinal. Define selectedID→helper identity and fail closed, retaining helper9's actual proof boundaries. `requestURL` can construct a minimal duration0 context if caller fields differ; avoid using that fallback to paper over a mixed snapshot. |
| `VLCThumbnailWorker` | One persistent worker, bounded header/payload, deadline, epoch invalidation, stuck-worker refusal, dedicated fingerprint subprocess | Assumes helper beside app executable and protocolversion3, ordinal/count CLI and reply fields. The integrated native helper must have portable upstream build/package rules and matching handshake/version. Startup success alone does not qualify retained demux, actualPTS/rotation or selected track. Parent and helper cancellation/reap behavior require fresh tests. |
| `VLCThumbnailCache` | Bounded safe reads, disposable cache, actual-sample aliases, demand retention, source-qualified cross-open reuse | Current manifestversion4/headerprotocol3 and identity string `v4:keyframe-countguard2:transform1:…:ordinal:count` encode old transform/track semantics. New core sampling/normalization/helper behavior must get a distinct renderer/identity namespace and strict reply validation; never reuse plausible old wrong images. Root decides supported stable track identity. Preserve sampled-hash limitation; do not turn it into durable bookmark identity. |
| `VLCThumbnailScheduler` | Finite dyadic coverage, demand priority, deferred/terminal targets, one serial owner | Times are media microseconds; master uses `vlc_tick_t`. Explicitly convert/check invalid ticks and media origin. Do not infer master preparser fast-seek is always a keyframe equivalent to the old helper's `sampling:keyframe`. Scheduling diagnostics are counters, not proof of complete media coverage. |
| `VLCTimelineContext` | Session/generation invalidation and immutable context snapshots | Old `pl_CurrentInput`, `input_thread_t`, `video-es` choices and `VLCInputChangedNotification` are the3.0 integration model. Master uses `VLCMain.sharedInstance.playQueueController.playerController`, player callbacks and stable ES strings. `VLCInputChangedNotification` is absent in the inspected master GUI. Replace this source wholesale at its boundary; do not use a sequence of separate public player getters as an atomic snapshot. |
| `VLCTimelineInteractionController` | Presentation generation checks, bounded request ownership, honest pointer/actual caption, disable/hide lifecycle | Its separate `VLCTimelinePreviewPanel`/canvas/popup, legacy generic-slider geometry and tracking area conflict with master's existing slider hover window. Retain behavior in the existing owner; do not ship the parallel popup, separate tracking path or old fullscreen controller. Preserve original seek/scroll/AX ownership. |

Other direct hazards: imports `"VLCMain.h"`/`"misc.h"` need master paths/actual
headers; master GUI build uses `-I…/gui/macosx`, with main under `main/`.
`getIntf()` still exists in `main/VLCMain.h`; its existence does not revive old
playlist/input APIs. Host-specific fallback bundle ID
`org.videolan.vlc-thumbs.development` must become official package ownership.
The `NSDeviceRGBColorSpace` raw representation has no explicit portable color
contract; don't broaden to all color/HDR content from the orientation fixture.

## Small safe player snapshot seam

Pinned evidence:

- `VLCPlayerController.m:1665–1685` builds all-track metadata while holding the
  player lock, but `VLCTrackMetaData` stores `_esID = p_track->es_id` without Hold
  (`:2176–2183`). That raw pointer is borrowed, not a transferable preview handle.
- `selectedTrackMetadataOfCategory` (`:1703–1710`) obtains `p_track`, unlocks,
  then constructs `VLCTrackMetaData`. `include/vlc_player.h:1443–1452` explicitly
  says track pointers become invalid at unlock. Do not implement previews by
  calling `selectedVideoTrack.esID` afterward.
- `vlc_player_GetSelectedTrack` (`include/vlc_player.h:1567–1587`) returns only the
  first selected track even if several are selected. Iterate/count selection;
  no selection or multiple selected videos must have an explicit eligibility
  outcome instead of guessing a track.
- `vlc_es_id_GetStrId` is valid only while the ID lives; stability for future
  use must be checked with `vlc_es_id_IsStrIdStable` (`include/vlc_es.h:742–768`).
  Copy into an owned NSString while protected. No borrowed pointer escapes.

Minimal addition candidate: a dedicated preview-context snapshot method inside
`VLCPlayerController`, where `_p_player` is owned, reading current media,
`vlc_player_GetLength`, `vlc_player_GetCapabilities`, video-enable state, video
count and each selected video track in one `vlc_player_Lock/Unlock` interval.
Copy URI/selected stringID and primitive eligibility fields there, returning
only an owned immutable DTO/dictionary. If a media or ES object must escape,
Hold it before unlock and Release it at a defined owner boundary; prefer copied
scalars/strings for this consumer. Do not do filesystem/source work under the
player lock. Invalid duration, unsupported selection or unavailable identity
returns ineligible.

The context owner creates its own session/generation on main. Current-media
notifications are invalidation events even for reopening the same URI. Observe
`VLCPlayerCurrentMediaItemChanged`, `VLCPlayerTrackListChanged`,
`VLCPlayerTrackSelectionChanged`, `VLCPlayerLengthChanged`,
`VLCPlayerCapabilitiesChanged` and stop/state transitions; refresh from the new
atomic getter rather than trusting delayed callback arguments. Main callbacks
are dispatched asynchronously, so a coherent player snapshot plus presentation
generation is still needed. Seekable alone is insufficient for local-video
eligibility. A borrowed item address must not become a durable cache identity.

This new consumer seam avoids depending on the existing selected getter's
lifetime behavior without casually rewriting that unrelated metadata API or
its other selection callers. The exact typed method, stable/unstable-track
policy and stop/reopen generation semantics remain root decisions.

## Existing native hover owner

`views/VLCPlaybackProgressSlider.m` owns hover tracking/window/label,
`reportHoverAtPoint`, `showHoverAtSliderX:time:`, `hideHoverWindow`,
`viewDidMoveToWindow`, `mouseExited`, `mouseDown` and `setMediaDuration`.
Extend its existing nonactivating child panel with image/status/actual-time
presentation, keeping the pointer-time label and original bar-fraction mapping.
Do not blindly import the old knob-adjusted `VLCTimelineGeometry` formula;
master currently computes fraction from `barRectFlipped:NO`.

`windows/controlsbar/VLCControlsBarCommon.m:490–494` already owns slider hidden,
enabled, buffering/indefinite, position and mediaDuration updates; its AX labels
are “Playback position”/“Position” (`:151–152`). Keep those and seek/scroll actions.
`windows/video/VLCMainVideoViewController.m:447–508` owns show/hide/fade behavior.
The panel/request must cancel/hide when controls fade, the view becomes hidden,
loses its window or reparents for fullscreen, and on disable/media/track change.
A pointer-exit event alone cannot cover these transitions. Add behavior through
the existing controls/slider ownership rather than an old fullscreen class.
Existing hover appearance guards10.14/11 APIs and should remain intact.

## Minimum OS / compiler evidence

`extras/package/macosx/env.build.sh:4` pins minimum macOS10.13. GUI resource
rules in `modules/gui/macosx/Makefile.am` also use10.13. Locally inspected Xcode27
SDK declarations show the old retained APIs fit that floor: `NSJSONWritingSortedKeys`
is10.13; `futimens`10.13; `NSTask launchAndReturnError:`10.13;
`NSProcessInfo.thermalState`10.10.3. `NSTimer` block APIs/monospaced digit fonts
predate10.13. No unguarded newer API was found in this bounded six-owner pass.
That is availability inspection, not execution on10.13 or Intel.

Old worker `launch` is now deprecated in the current SDK; established nonthrowing
`launchAndReturnError:` fits the minimum and is a narrow port choice, retaining
failure cleanup. Existing raw `read`/`write` and `closeFile` should not be replaced
casually with newer NSFileHandle NSError APIs, many of which begin10.15. Keep
Darwin `F_SETNOSIGPIPE` descriptor-local; never change VLC global signals.
App/helper architecture, codesigning, executable layout and plugin/library search
paths need package proof for arm64/Intel; the host's old3.0 build does not qualify
master. Test source and normal builds must use ARC/framework flags from upstream,
not host-injected include paths or modified contrib headers.

## Preferences, localization and tests

- Option registration: `main/macosx.m` existing `add_bool` and `N_` labels.
  A default-on timeline-preview setting belongs here under interface behavior.
- Simple Preferences: `UI/SimplePreferences.xib`,
  `preferences/VLCSimplePrefsController.h/.m`; existing playback-behavior group
  title aroundline419, `setupButton:forBoolValue:` at570, reset/load paths from614,
  save config and `VLCConfigurationChangedNotification` at1125–1126.
  Use upstream outlets/load/save/cancel lifecycle; no dynamic prototype checkbox
  in the public package. Saved runtime effects must honor inherited CLI override
  as the existing contract requires.
- Localization: use the existing `_NS`/`NSTR`/`N_` extraction conventions for
  preferences and loading/unavailable/source-check/actual-frame text. Old
  interaction controller uses literal English strings and string-composed
  “Keyframe … · Checking source…” captions; localize complete templates and
  plurals where relevant. New files must be in upstream `po/POTFILES.in` if
  required by the current extraction list, and in normal GUI build sources.
- XCTest seam: `modules/gui/macosx/tests/Makefile.am` supports
  `ENABLE_MACOSX_XCTESTS`, ARC/Foundation/Cocoa and `check-macosx`. Existing tests
  directly compile selected implementation units; adapt cache/scheduler/geometry
  contracts to this harness without copying Python orchestration into VLC.
  Player snapshot/context tests need a bounded injectable core or dedicated
  fixture seam, not a live UI in every unit test. Native screenshots/physical
  hover, actual AX, controls/preferences/fullscreen/playback/NAS still require
  separate functional proof.

## Diagnostic and private material to omit

`VLC_TIMELINE_DIAGNOSTICS`, `VLCTimelineTrace` external-path JSONL writer,
view-ancestry dumps, local event monitor (`diagnosticMonitor`), pointer/event
observation and benchmark display metadata are prototype measurement substrate.
Omit those public runtime hooks; use upstream logging and portable tests where
useful. Do not strip generation checks/cancel/source qualification merely because
trace calls sit beside them. Counter access used by deterministic tests can be
internal to the test seam rather than a public product API.

Exclude local methodology/AGENTS/docs diary, old3.0 patches, app bundles, private
NAS/media/paths, ignored build repair scripts, absolute `/Users/cam` flags,
fixtures with unverified licenses, fake-worker orchestration dependent on this
workspace and test installers that write the app/real preferences. Public legal
fixture generation/build commands must work in a clean upstream checkout.

Root should freeze the exact snapshot/worker/protocol/cache/panel ownership plan
before builders edit native files. This inventory does not select a retained
helper architecture or mark Phase2 ready.

## Local source inventory hashes

- `src/macosx/VLCThumbnailService.h`: `655747ebac912c9410156c4d204aff33715c22ae764b24d749d416e2c86919ff`
- `src/macosx/VLCThumbnailService.m`: `aafccd70fc3af1d0eacc3d9a44c26f9a27ee95a64e03fd7a9c351445ad155f44`
- `src/macosx/VLCThumbnailWorker.h`: `70c89178a08f46802793312381a39da118a21c62b9b003fda2fc2d724b74b570`
- `src/macosx/VLCThumbnailWorker.m`: `0a782004ca3b1f9412d87cdb4077c2e484d16dcdc88f28492247733b2fef2be3`
- `src/macosx/VLCThumbnailCache.h`: `32f95e71cdb97011a36b501101da78d525fab893003f5388ee2b1c62c54b5170`
- `src/macosx/VLCThumbnailCache.m`: `29399e7d40a2cfcc8b604640f0971f4107d7c6ccb7562d202436725aa9051d4a`
- `src/macosx/VLCThumbnailScheduler.h`: `3358d1078438a65971e67c116d7f1400c69b8033a700427faf7a480419e3c5ec`
- `src/macosx/VLCThumbnailScheduler.m`: `634a6263a641807b2f9c47bf9c66e742f57f4f1c25823deee72f6fc119491fe6`
- `src/macosx/VLCTimelineContext.h`: `651c0dcf20eb90eeda70b1547bf51689b3fdd6fefd7a5cd74507a02d79b73244`
- `src/macosx/VLCTimelineContext.m`: `007285760d6d1825614a72ab92c57e13bf94a1b1c79e7c0daeb881081aa88430`
- `src/macosx/VLCTimelineInteractionController.h`: `cd13975b82961511db69cde96c7dcf68221a576999376944e23dfb021c9789fc`
- `src/macosx/VLCTimelineInteractionController.m`: `46caca8f470beb2bb28661c1ce9d347f782131b492ce8130a24a60c0e70986bc`
- `src/macosx/VLCTimelineGeometry.h`: `3b2de60bba6b5feade74387816aa0406d7fbd085469810e1eeafbe7594d07334`
