# Native preview screenshots

These historical [custom-fullscreen](custom-fullscreen-hover.png) and
[detached-control](detached-hover.png) screenshots illustrate the feature. Both
show pointer time **02:30**, caption **Keyframe 02:30**, and the generated image
marking **150.000 / frame 3600** at 24 fps. Hover and playback times are separate.
The images are unchanged captures, not a recording or current-tree validation.

[Provenance](provenance.json) pins the original capture/runtime/image hashes.
The production build was `8ec1cdec6939c67eeb6bef0ff1bb035c168d0592`, not the
current combined tree. Use the [current validation table](../../CONTRIBUTION.md#validation-and-limits)
and [limitations](../LIMITATIONS.md) for present qualification. These images do
not prove responsiveness, accessibility, shutdown, cache reuse or cold/stalled
NAS behavior. No edited images, app binaries or private media are included.

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
