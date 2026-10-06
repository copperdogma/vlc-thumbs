# Native control-surface investigation — 2026-10-04

Pinned VLC 3.0.24 / 6de05ad, attempt-009 arm64 development app; macOS 27.0,
26A428. Bundle ID `org.videolan.vlc-thumbs.development`. Actual launch argument
arrays/logs accompany captures. No installed VLC or private media used.

| Surface | Observed | Remaining proof |
|---|---|---|
| Main window | Attempt-009 rendered synthetic MPEG-4, paused and clicked timeline to seek; screenshot/time changed | Feature hover, context menus, markers, accessibility |
| Detached window | `--no-embedded-video`; H.264 fixture renders and AX exposes Position slider, Play/Pause, time and fullscreen | Detailed seek/hover/context/keyboard and feature behavior |
| Custom fullscreen | Synthetic video fills fullscreen after native UI fullscreen action | Floating panel capture/interaction and feature behavior |
| Native fullscreen | `--macosx-nativefullscreenmode --fullscreen`; known H.264 frame70/time2.917 visibly rendered | Floating panel capture/interaction and feature behavior |

Selected-window screenshots and AX state did not expose the floating fullscreen
panel, including an `i` interface-toggle attempt. This tool has no hover/mouse-
move API. Source establishes the separate panel/slider path, but these captures
do not establish whether the panel is visible in the complete desktop composite.
Do not count this as successful panel interaction or diagnose a panel defect.
Both implementation stories must obtain actual fullscreen panel/hover evidence,
using an available pointer driver or a recorded human exercise if necessary.

Some preliminary three-second launch attempts returned to a playlist/paused
state; do not use `native-fullscreen.png` to claim video fullscreen success.
`native-known-fullscreen.png` is the verified native video capture. Later launch
records use `start_new_session=true` so the terminal invocation does not own the
app lifetime. Screenshots are state captures, not timing/performance runs.

Fixtures and hashes: build attempt 009 fixture.json and the adjacent
thumbnail-probe-20261004 provenance. Native/detached use the generated eight-
second H.264 clip; no broad container/format qualification follows from it.
