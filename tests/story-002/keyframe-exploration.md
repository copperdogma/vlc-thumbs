# Keyframe thumbnail exploration — 2026-10-04

Historical exploration before Cam selected the keyframe MVP. The 0.5-second
correspondence gate discussed below belonged to the earlier exact-frame strategy;
Cam subsequently accepted coarse keyframe previews with their actual timestamp.
Current keyframe qualification is in `helper-keyframe-results.json` and validates
actual keyframe identity/presentation while reporting pointer delta honestly.

Cam's idea of using existing compressed keyframes can reduce decode work, but
these fixtures do not contain ready-made thumbnail images. A keyframe is a
compressed video frame that still needs decoder and color/scale work. An index
helps locate it without decoding every preceding frame. The current helper
already uses backward demux seeking, then decodes forward to a nearby requested
presentation time; it does not decode the whole video for each hover.

Independent host FFprobe (`-skip_frame nokey -show_frames`) found standard
1080p24 keyframes every two seconds, from 0 through 58 s. The diagnostic
12-second long-GOP video has only two keyframes, at 0 and 10 s. Across twelve
representative hover targets per file:

| Fixture | Nearest-keyframe misses >0.5 s | Worst keyframe error | Worst current-helper error |
|---|---:|---:|---:|
| Standard 60 s / two-second GOP | 6 / 12 | 1.5 s | 0.016667 s |
| Diagnostic 12 s / ten-second GOP | 9 / 12 | 5.0 s | 0.016667 s |

The long-GOP midpoint at 5 s is five seconds from either available keyframe.
Near EOF, the standard video at 59.5 s is 1.5 s from its last keyframe. Therefore
nearest-keyframe-only previews would fail the accepted <=0.5 s correspondence
gate on ordinary targets. This is measured against independent indexed frame
times, not just a helper success flag.

A bounded same-host-FFmpeg experiment compared ordinary precise input seeking
at each target with `-skip_frame nokey` seeking at the nearest indexed keyframe.
Both produced one decoded 320x180 RGBA image; `showinfo` verified output PTS.

| Fixture | Full decode median | Keyframe-only median |
|---|---:|---:|
| Standard | 198.03 ms | 172.63 ms |
| Long GOP | 170.76 ms | 165.89 ms |

These are twelve-process diagnostic medians, including CLI startup/open, rather
than acceptance percentiles or an isolated decoder-speed measurement. The
research FFmpeg runs x86_64 on this arm64 host; its times cannot establish the
private arm64 helper's savings. Media was recently accessed and OS caches were
warm/uncontrolled. The long-GOP clip is deliberately low resolution. No GUI,
cache or playback comparison was attempted, and no helper/UI code was changed.

Keyframe indexing remains useful for seek boundaries and possible future cache
seeding. Serving only those images would require a separately accepted weaker
correspondence contract; the present evidence supports retaining precise
forward decoding for successful previews. An approximate loading placeholder
would also need explicit UI semantics and validation before adoption.

Exact commands, target arrays, keyframe maps, output PTS, input/helper hashes and
trial timings are in ignored `work/validation/story002/keyframes.json`; the
bounded measurement recipe is `work/validation/story002/explore-keyframes.py`.
Both source hashes match generation and the helper hash stayed unchanged.
Final helper validation is independently recorded in
`work/validation/story002/helper-results-v3.json` (22 correctness/error cases
and 200 successful settled helper requests). This exploration does not qualify
the native timeline or complete the integrated root eval.

## Accepted keyframe MVP qualification

After Cam selected coarse previews, the protocol v2 helper was independently
qualified against actual decoded keyframe flags/PTS and pixels, with coarse
pointer deltas reported instead of failing the old exact-frame gate. Candidate
SHA-256 is `23fe2f7d8a04aa27f4ee4ddb098d01d2a97edfda59c3a1b2880b462fc473eaa5`.
All 22 presentation/timing/track/fault cases and 200 settled standard requests
passed; source/helper hashes remained unchanged and MP4/MKV RGBA matched exactly.

| Standard fixture | Requests | Helper p95 | Maximum | Sampled peak RSS |
|---|---:|---:|---:|---:|
| MP4 | 100 | 39.31 ms | 40.18 ms | 22.89 MiB |
| Same-stream MKV | 100 | 47.53 ms | 52.99 ms | 27.19 MiB |

These remain helper-only timings with Python resource sampling and warm or
uncontrolled OS caches. Native hover input/presentation, cache and competing
playback timings require separate proof. Sparse previews are deliberate:

| Fixture | Independent keyframes | Maximum spacing | Example pointer → actual image |
|---|---:|---:|---|
| Standard MP4/MKV | 30, from 0 to 58 s | 2 s | 12.125 → 12 s; endpoint 60 → 58 s |
| 12 s long GOP | 2, at 0 and 10 s | 10 s | 9.125 → 0 s |
| Five-minute low-resolution | 6, from 0 to 250 s | 50 s | 244.25 → 200 s |

The standard 100-request sequence had up to 1.5 s pointer distance. The five-minute
example is 44.25 s early, demonstrating the accepted sparse-GOP tradeoff rather
than suggesting uniformly dense thumbnails. The edit-offset fixture at pointer
0 uses its first qualified keyframe at 2 s, honestly recording the future image
time. The oracle otherwise requires a preceding keyframe when one is available.
No extra samples are decoded by default. Full result and density maps are in
`work/validation/story002/helper-keyframe-results.json`.
