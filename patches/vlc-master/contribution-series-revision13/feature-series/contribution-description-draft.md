# Proposed contribution description

VLC's macOS timeline gains an image and actual keyframe-time caption when the pointer
hovers over a position. This extends the existing native hover panel, defaults on, and
has an Interface preference. Pointer time remains the seek target; disabling previews
or encountering an unsupported source retains ordinary time hover.

The player context supplies selected-video identity and an input epoch. A service owns
scheduling, 32 MiB RAM/256 MiB disk caches and stale-result cancellation; separate serial
metadata/decode queues use private workers built through normal FFmpeg 9 contrib rules.
Metadata plus sampled SHA256 qualifies persistent reuse and fresh reopen; unsampled changes
can escape detection. Provisional images share a 15-second deadline that pointer activity
cannot renew. Regular local files, including mounted NAS files, qualify; URLs do not.

Matroska multi-video selection requires an exact unique representable TrackNumber. An
opt-in bounded flat-timeline scan rejects ordered/linked or malformed/unsupported inputs
while preserving default demuxing. Some playable files are intentionally unsupported.
The [review map](README.md) separates distribution, contrib, helper/build/tests and native
service/context/hover parts. Seven baseline readiness repairs are a separate prerequisite
component; canonical application and full-gate proof concern the combined stack. Dependency
ownership, FFmpeg routing and final submission boundaries need maintainer agreement.

The exact combined stack passes normal 009 complete `make check` and conventional 010 complete
`make distcheck`. Current main/custom hover and narrow reader/seek/Quit observations support
review, with inaccurate/stale exposed progress, a negative returned-main hover capture with unknown cause, incomplete fullscreen reader/roundtrip and
unavailable Intel/older-macOS/CI coverage disclosed in [LIMITATIONS.md](LIMITATIONS.md).
Historical shutdown 004 causality remains unexplained and user-accepted deferred; a later
baseline crash has a distinct known pattern, and one corresponding candidate Quit exits
cleanly. No crash-frequency or causal-exoneration claim follows. Actual executed gate
commands and their private read-only observation difference are recorded in
[CONTRIBUTION.md](../CONTRIBUTION.md); the shorter host recipe remains unexecuted.
Two unchanged [native screenshots](demonstration/README.md) illustrate historical rendering
and do not qualify subsequent source changes. Nothing has been submitted.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**, with approved credit.
Developed with AI assistance under retained GPL/LGPL terms and third-party notices.
Credit asserts no sole ownership, assignment, waiver or Signed-off-by. No binaries,
private media, raw logs or local paths are included. Maintainer acceptance is external;
remaining qualification is stated explicitly for review.
