# Development playback observer

`playback_capture.swift` is a bounded diagnostic for Story 002's three paired
60-second playback runs. It does not control VLC, seek, pause, change focus,
capture a microphone, or access other apps' audio. The main validation runner
owns native interactions, RC counters, app/helper resources and conclusions.
The observer alone does not qualify playback integrity.

## Build and short live qualification

From the `vlc-thumbs` workspace root, using the existing Xcode SDK:

```sh
xcrun swiftc -parse-as-library -O -framework AppKit -framework ScreenCaptureKit -framework CoreMedia -framework CoreVideo -framework AudioToolbox tests/story-002/playback_capture.swift -o work/validation/story002/playback-capture
```

The source compiled with Apple Swift 6.4, targeting arm64 macOS 27. This is
compile evidence; no capture permission, running-app capture or accuracy was
verified by its author. The main runner must perform that live qualification.

The first main-runner live smoke aborted before capture with
`CGS_REQUIRE_INIT (did_initialize)`. Standalone executables do not pass through
`NSApplicationMain`; Apple's [NSApplication.shared documentation](https://developer.apple.com/documentation/appkit/nsapplication/shared)
establishes that creating the shared application connects to WindowServer and
completes display initialization. The observer now creates it on the main actor
before ScreenCaptureKit calls and requests prohibited activation policy. The
next main-runner retry reached this policy change but macOS rejected it. Policy
rejection is now recorded rather than fatal: the observer creates no windows
and makes no activation calls. `observer_activation` in ready/summary records
requested/effective policy and whether the request was accepted; absence of a
Dock icon is not assumed when the host rejects the policy change. The revised
source compiles; a main-runner retry must establish actual capture behavior and
check that VLC retains focus. Capture permissions/filter scope are unchanged.

Open the owned synthetic fixture in the isolated development VLC. Supply its
PID and preferably the verified main video window ID (the fallback chooses the
largest eligible visible layer-zero window belonging to that PID):

```sh
work/validation/story002/playback-capture --pid "$vlc_task_pid" --window-id "$vlc_task_window_id" --output work/validation/story002/capture-smoke-001 --duration 3 --raw-audio
```

The executable rejects PIDs whose bundle ID is not
`org.videolan.vlc-thumbs.development`; it also verifies the PID/bundle in
ScreenCaptureKit's shareable content and confines window selection to that PID.
The selected window is recorded in the ready event and summary. ScreenCaptureKit
may need host capture authorization before it can list or capture that window.
If startup fails, use the explicit error; do not silently switch to whole-display
or whole-system capture.

Before benchmarking, verify that:

- `audio.jsonl` contains supported mono float32 PCM, nonzero 10 ms RMS windows
  at the expected generated-tone level, and stable presentation timestamps.
- `screen.jsonl` contains complete frames with changing ROI hashes while the
  synthetic video is moving. Verify the normalized ROI against the actual
  selected window geometry; the default upper-video ROI is `0.2,0.15,0.6,0.35`
  in top-left image coordinates. It must exclude title bar, letterboxing,
  controls and hover popup. Override with `--roi x,y,width,height` if necessary.
- A separate deliberate pause smoke produces the expected silent/unchanged
  intervals. That calibration pause is not part of a performance run. Capture
  selection/levels are not qualified merely because the process returned zero.

Use fresh output directories. Existing log/summary files are never overwritten.
All output must resolve beneath this workspace's `work/`, including symlinks.
Duration is greater than zero and at most 65 seconds. `--fps` accepts 30 or 60
(default 30), and the longest output raster edge is capped at 640 pixels.

## Paired runs

Use identical capture settings, ROI, native window size, fixture, playback
settings and pointer schedule for both app variants. For each run, start the
observer with VLC already displaying the paused synthetic video, wait for its
newline-delimited JSON `ready` stdout event, then start playback. `--duration 65`
allows the runner to select the actual 60-second playback interval from logs
while excluding startup and EOF silence. Record the runner's playback-start and
EOF timestamps alongside the ready event. Do not equate the observer's entire
65-second lifetime with active playback.

Suggested order: baseline 1 / feature 1, feature 2 / baseline 2, baseline 3 /
feature 3. Apply the same real-pointer motion in both variants; feature logs
must show actual hover demand and delivered images during active playback.
The native baseline still needs its own source/module provenance.

This observer deliberately does not assign a passing score or attribute any
gap to VLC. Combine its evidence with the existing RC `stats`/`status` stream,
native observation and app/helper CPU/RSS samples. RC statistics update about
every 250 ms in pinned `src/input/input.c`; integer-second `get_time` and frame
totals cannot establish a 100 ms video-stall limit. Use `--play-and-pause` to
retain the current input after EOF for final counters, and exclude that planned
EOF pause from hover-induced pause judgments.

## Evidence schema

`summary.json` has schema version 1 and records PID, bundle ID, window ID/title/
frame, normalized ROI, requested FPS/duration, observer start in Unix and uptime
seconds, actual elapsed time, threshold and any capture/IO error.

`audio.jsonl` contains three principal event kinds:

- `format`: actual sample rate, channel count, PCM bits/flags and whether RMS
  analysis supports that format. Analysis accepts native little-endian mono
  float32 PCM only; unexpected formats count as unsupported rather than silently
  producing guessed levels.
- `buffer`: presentation timestamp, monotonic callback arrival relative to
  observer start, sample frames/duration, timestamp gap from the preceding
  buffer's expected end, and callback-arrival gap.
- `rms_10ms`: window start, actual duration, RMS, dBFS and comparison with
  `--silence-db` (default -60 dBFS). Windows span buffer boundaries; a timestamp
  discontinuity clears the partial window. Final partial windows are counted
  as omitted. Invalid buffers/analysis errors are explicit events or counts.

The audio summary retains timestamp discontinuities exceeding 2 ms, callback
gaps exceeding both 100 ms and three current-buffer durations, and all contiguous
below-threshold intervals. These include pre-playback and EOF silence. The
runner must select the known playing interval and calibrate the threshold
against the synthetic 440 Hz tone. `--raw-audio` writes optional mono float32
little-endian samples to `audio-mono-f32le.pcm` (about 12.5 MB for 65 seconds at
48 kHz); JSONL buffer metadata carries timing, because the raw file has no gaps
inserted and no header. No video images or movie files are written.

`screen.jsonl` records presentation timestamp, callback arrival, screen status,
timestamp/observer gaps and, for complete BGRA frames, raster dimensions,
integer ROI rectangle and FNV-1a 64-bit pixel hash. Screen status integers follow
`SCFrameStatus`: 0 complete, 1 idle, 2 blank, 3 suspended, 4 started, 5 stopped;
-1 means unavailable metadata. Idle means no new display frame, and extends the
previous ROI hash where it exists. Other noncomplete statuses terminate a
repeat segment. Summary keeps timestamp and observer gaps over 100 ms and
unchanged-ROI intervals lasting at least 100 ms. A gap resets repeated-image
tracking so the observer never joins an apparent freeze across missing capture
evidence. Repeat duration runs from the first observation of a hash through its
last observation, with resolution limited by the chosen FPS; it is not an exact
stall onset/end measurement.

## Interpretation and limits

The generated moving fixture makes a stable video ROI useful, but static scenes
in arbitrary media do not. A wrong ROI may produce a permanent false freeze or
miss a freeze because overlays are moving. Resizing the window or fullscreen
transitions during a benchmark change the interpretation; use separate fixed
surface runs if those need qualification.

An unchanged ROI is a freeze **candidate** until callback/timestamp continuity,
the fixture's known motion, native playback and paired baseline are checked.
Capture timestamp gaps and callback gaps are observer evidence and must not be
reported automatically as VLC stalls. If capture gaps prevent assessing the
100 ms contract, report that gate as unqualified and resolve the observer.

Audio capture observes the containing app's digital output, not speaker hardware
or a microphone. Silence/discontinuities can originate in capture. VLC's
`buffers played` counter increments when buffers are submitted; its CoreAudio
renderer can pad underruns with zeros independently of those totals. Compare
captured tone continuity with pinned CoreAudio `underrun of ... bytes` logging,
RC counters, native observation and paired timing before attribution.

Pixel hashing, capture and JSONL writes add observer load. Run the same observer
in both variants; resource measurement must separately identify VLC, thumbnail
helper and observer. No claims about uncaptured wall-clock peaks, physical audio,
unseen surfaces, other media formats or large-file behavior follow from this probe.

Primary API references: Apple's [ScreenCaptureKit app-level capture explanation](https://developer.apple.com/videos/play/wwdc2022/10155/),
[sample outputs](https://developer.apple.com/documentation/screencapturekit/scstreamoutputtype/audio),
and [capture sample](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos).
Local SDK headers independently establish status semantics, audio sample format
and microphone/audio configuration. The chosen short live smoke is the
applicability check; compile success alone does not establish it.
