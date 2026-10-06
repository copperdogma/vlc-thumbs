# Sparse keyframe coverage — 2026-10-04

Cam reports that existing keyframes provide more than enough indication in
ordinary use. Keep that inexpensive sampling policy as the default. The open
question is coverage in unusual encodings, rather than exact-frame previews.

## Primary evidence and local check

[x265's encoder documentation](https://x265.readthedocs.io/en/4.2/cli.html)
documents an infinite GOP with only an initial keyframe, and periodic intra
refresh that refreshes blocks over multiple frames instead of inserting full
keyframes. Playability therefore does not promise regularly spaced frames that
our helper recognizes as independently usable keyframes. This is not proof that
every codec can produce a playable file with zero such frames.

A generated 24-second H.264 fixture has 288 decoded frames and exactly one
independently probed keyframe at 0 seconds. Current helper requests at 12, 23.9
and 24 seconds all return that image with actual time 0, in 268/34/33 ms. Source
and helper hashes remain unchanged. Detailed recipe, hashes and results are in
`docs/evidence/story-002/sparse-keyframes.json`. This validates sparse-file
behavior, not a no-keyframe recovery route or a supplementary-image fallback.

## Direction and uncertainty

Use keyframes first. If coverage is inadequate, supplement only those regions
with decoded thumbnail images; never insert keyframes into or re-encode the
video. A maximum usable time gap is a better criterion than average keyframes
per minute: the average can conceal a long empty stretch.

No numerical gap threshold has been selected, and the current MVP has no
gap-filling fallback. A future implementation must bound decoding work, preserve
honest sample timestamps, and test sparse and recovery-based streams. Missing
keyframe flags alone cannot guarantee that decoding a requested frame is cheap
or possible. Keep unsupported/unrecoverable cases explicitly unavailable.
