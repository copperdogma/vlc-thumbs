# Native preview screenshots — scoped demonstration

[Custom fullscreen](custom-fullscreen-hover.png) and
[detached controls](detached-hover.png) show actual visible previews: pointer time
**02:30**, caption **Keyframe 02:30**, and synthetic image marking **150.000 /
frame 3600** (24 fps). Hover and playback times are separate. These unchanged
captures are not a recording; no image editing or app binary is included.

Rendering was also acquired on main and native-fullscreen controls; this package
illustrates two of those four surfaces. Screenshots cannot qualify latency,
reader navigation, complete controls, restart reuse, cold/stalled NAS or playback
cost. See [qualification and unresolved faults](../LIMITATIONS.md).

## Source correspondence

[Provenance](provenance.json) pins capture/image/runtime hashes. Captures used the
duration-corrected production tree `8ec1cdec6939c67eeb6bef0ff1bb035c168d0592`,
not a build of all revision-10 source files. Later test/distribution/guide changes
left production runtime hashes unchanged at that freeze. The [manifest](../manifest.json)
pins the source series separately. Current combined normal 009/complete 010 pass
independently of these historical captures. These captures do not qualify current changed
foundation GUI behavior or current native/reader readiness.

Native-arm64 candidate007 was an owned metadata-only app clone: 997 files and
10 symlinks inventoried, changed Info.plist/main executable identity/signature
metadata, matching main loadable sections and other files/symlinks. An owned
profile/cache isolated it from installed VLC and user data. This experimental
isolation is not a proposed product change; local receipts are not package inputs.

## Reproduce the image content

From the patched VLC source root, with test-only FFmpeg/ffprobe available:

```sh
fixture_root=$(mktemp -d)
python3 bin/timeline-preview/tests/generate_fixtures.py --long-only \
  --output "$fixture_root/long" --ffmpeg ffmpeg --ffprobe ffprobe
```

The explicit recipe generates 300 s of 320×180/24 fps testsrc2, two-second GOPs
and a 440 Hz/48 kHz ALAC tone. FFmpeg's [testsrc2 source](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavfilter/vsrc_testsrc.c)
uses built-in time/frame digits without external fonts. Tool versions/container
output can change bytes; retain the regenerated manifest rather than expecting
the captured hash. Open the generated MP4 with previews enabled; physically hover
150 s in custom fullscreen or detached controls and compare pointer, caption and
image marking. No new capture or fixture generation was performed for this page.
