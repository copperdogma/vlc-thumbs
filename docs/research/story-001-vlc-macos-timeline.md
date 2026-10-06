# Story 001 — first macOS timeline investigation

Date: 2026-10-03. Source baseline: VLC 3.0.24,
`6de05adcbaf2e8b85fe86aad4169393098628119`. Acquisition/host details:
`docs/evidence/story-001/preflight.md`; file identities: source-manifest.json.
This initial section is source inspection. Subsequent working-build and probe
results are in [the 2026-10-04 synthesis](timeline-implementation-plan.md);
the historical next-build proposals below are superseded there. No feature
persistence or integrated root proof exists.

## Stable-source observations

- Normal main window and detached-video window wire `VLCSlider`/`VLCSliderCell`
  to `VLCControlsBarCommon.timeSliderAction:`. The handler accepts click/drag/
  wheel events and sets input position using slider value / 10000. Source:
  [MainWindow.xib](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/UI/MainWindow.xib#L650-L660),
  [VLCControlsBarCommon.m](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCControlsBarCommon.m#L293-L332).
- Stable `VLCSlider` has scroll handling and styling, but no hover tracking or
  right-click override in the inspected file. `VLCSliderCell` supplies geometry
  and drawing; barRectFlipped returns control bounds, while drawing insets the
  bar. Mapping must follow actual drawn geometry and knob travel, not simply
  assume the entire view is the click track.
  [Slider](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCSlider.m),
  [cell](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCSliderCell.m#L170-L230).
- The separate fullscreen panel XIB instead declares an NSSlider with a regular
  sliderCell and calls `VLCFSPanelController.timeSliderUpdate:`. Its handler
  also sets input position from value / 10000. Native-fullscreen mode and VLC's
  legacy/custom fullscreen path are distinct in VLCVoutWindowController, so
  the panel mapping is not proof that every fullscreen configuration shares it.
  [Panel XIB](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/UI/VLCFullScreenPanel.xib#L70-L79),
  [controller](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCFSPanelController.m#L203-L235).
- Existing macOS bookmarks are a separate window with name/time editing.
  `add:` captures the current input bookmark and labels it Untitled; this is
  not right-clicking an arbitrary timeline position.
  [Bookmarks controller](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCBookmarksWindowController.m#L119-L138).
- Core UpdateBookmarksOption serializes name/time bookmarks as an input-item
  option; input.c can restore that option. This is a reuse candidate, not proof
  of automatic identity-based persistence when reopening a file after quitting.
  Serialization includes a TODO for escaping unsuitable values; short labels
  still need deliberate punctuation/encoding behavior.
  [Core](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/src/input/control.c#L591-L621).
- The inspected Lua README/dialog source describes extension dialogs and their
  standard widgets; macOS has a dedicated extensions dialog provider. These
  are not timeline views. Stable Lua input.c registers playing/item/subtitle
  methods, unlike master's dedicated time/position/seek bindings. Stable object
  and variable bindings offer a possible route through the input time/position
  variables, which still needs runtime qualification. No native-slider hover/
  drawing hook has been identified. The follow-up research packet checked the
  pristine stable checkout specifically; its generic-variable route is kept
  separate from the development API.
  [Lua README](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/share/lua/README.txt),
  [dialog implementation](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/lua/libs/dialog.c).
- LibVLC exposes separate media-player construction and current-window snapshot
  APIs. That supports considering an independent decoder, but a snapshot API
  is not an arbitrary-time thumbnail service or a performance qualification.
  [LibVLC media-player API](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/include/vlc/libvlc_media_player.h).

## Development-source comparison — do not conflate with 3.0.24

A bounded Luna research packet inspected VideoLAN master at
`da266629fdffc4bee4560d9c818efd16217efeda`. The main agent confirmed that SHA
against the primary Git origin. It contains a newer
[VLCPlaybackProgressSlider](https://github.com/videolan/vlc/blob/da266629fdffc4bee4560d9c818efd16217efeda/modules/gui/macosx/views/VLCPlaybackProgressSlider.m#L134-L170)
with Cocoa tracking and an existing hover time panel, plus A/B-loop tick drawing
in its cell. These are helpful precedents for a development baseline or a small
backport, not features already proven in the stable inspected slider. Changing
to development VLC would change build/API and regression scope; not selected.

## Route comparison — provisional judgment

| Route | What it already supplies | Gap against requested experience | Initial disposition |
|---|---|---|---|
| Existing stable bookmarks | Named current-position bookmarks and a separate editor | Integrated arbitrary-position labels, hover frames and automatic same-file restart persistence unproven | Inspect/reuse compatible semantics; not the complete floor |
| Lua extension | Playback/dialog facilities; a separate annotation workflow is plausible | No exposed native timeline hover/drawing seam identified | Does not presently satisfy the actual scrub-bar floor |
| Native module alone | Runtime native code and core access | Loading a module does not establish a supported composition API into the Cocoa slider | No qualified slider host seam; further inspection needed |
| Small macOS GUI patch on stable | Direct event/geometry/drawing ownership in the actual requested surface | Build, decoder/cache, annotation durability and fullscreen wiring need proof | Leading candidate for first isolated experiment |
| Development VLC GUI patch | Existing hover time-panel and tick-drawing precedents | Different baseline/toolchain and broader regression/maintenance exposure | Alternative if stable build/integration is unattractive |

This favors investigating a small native GUI change; it is not a final fork
commitment, formal impossibility proof for Lua, or completed add-on marketplace
survey. Reuse VLC's licensed source normally. Keep the one-to-three-word label
preference in the UI scope; no paragraph editor or hard word-count validator.

## Next bounded feasibility step

Establish an unmodified arm64 upstream build in ignored work space before any
product patch. The pinned script defaults to x86_64, expects `aarch64` for the
arm64 host triplet and rebuilds its own tools/contribs before configuring VLC.
It provides `-C` for a separate product build directory, `VLC_PATH` for extra
host tools, and `VLC_PREBUILT_CONTRIBS_URL` for an explicit contrib archive.
Prebuilt URLs are host-triplet/latest based; archive provenance must be pinned
if reused. Current SDK 27 compatibility and arm64 deployment settings need an
actual attempt; no compile success is claimed.

After baseline: use generated/legal known-frame media, qualify isolated app
launch/settings, inspect normal/detached/native/custom fullscreen controls, and
set concrete preview/seek/latency/playback tolerances. Compare independent VLC
decode versus another helper only if needed. The thumbnail decoder must never
seek the currently playing input. Annotation identity and durability remain an
unselected design boundary; existing bookmark options alone do not retire it.


## Existing playback-resume storage — 2026-10-03

Cam asked whether the existing per-video resume mechanism should also hold
thumbnails and short timeline labels. Pinned 3.0.24 source provides a concrete
answer, without reading or changing Cam's private VLC preferences:

- `VLCInputManager.m:635-687` reads `recentlyPlayedMedia` from standard
  NSUserDefaults, keyed by decoded media URI. Values are integer seconds; resume
  converts them to input time units.
- `VLCInputManager.m:718-764` writes that dictionary and
  `recentlyPlayedMediaList`, the recency-order array. It checks the recent-items
  preference and valid local file. It retains at most 30 resume entries and
  removes entries that no longer meet the playback-position retention criteria.
- `VLCDocumentController.m:37-46` clears both keys when clearing recent documents.
- The app's preference domain is `org.videolan.vlc`, ordinarily persisted by
  macOS under `~/Library/Preferences/org.videolan.vlc.plist`. The source uses
  NSUserDefaults; do not bypass it by editing the plist in a live app.

Sources:
[Resume code](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCInputManager.m#L635-L764),
[clear-history code](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCDocumentController.m#L37-L46),
[VideoLAN developer discussion of preference path](https://mailman.videolan.org/pipermail/vlc-devel/2022-March/143452.html).
The older discussion's retention thresholds differ from the pinned release;
use the pinned code for current thresholds.

Recommendation, not accepted storage/schema decision: reuse VLC's media/input
identity access and lifecycle integration, while keeping distinct retention.
Durable user labels belong in a feature-owned store under VLC's Application
Support area; regenerable thumbnail files belong in its Caches area with bounded
cleanup. Preferences may hold small feature settings. Do not append labels or
images into `recentlyPlayedMedia`: history eviction/clearing and resume-position
cleanup must not silently delete deliberately authored labels. A separate
NSUserDefaults key could technically hold tiny labels, but it does not provide
a unified per-video asset store and is not a reason to put images in preferences.
Revalidate filename/replacement identity beyond the existing decoded-URI key;
a thumbnail cache and permanent labels have different lifetimes.


Follow-up: Cam accepted the storage/retention direction and requested
[ADR-001](../decisions/adr-001-media-metadata-storage/adr.md). The earlier
recommendation is now accepted for storage areas and separate lifetimes only;
format/schema/identity/cache quotas remain open. No runtime qualification added.
