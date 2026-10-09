# Proposed contribution description

Add keyframe previews to VLC's native macOS timeline so users can inspect a
scene before seeking. The hover panel shows an image and its actual keyframe
time; pointer time remains the seek target. Previews default on, have an
Interface preference, and fall back to ordinary time hover for unsupported media
or failures. Bookmarks are outside this series.

The existing player supplies selected-video identity and an input epoch. A
service owns finite scheduling, stale-result cancellation and 32 MiB RAM/256 MiB
disk caches. Serial metadata and decode queues use retained private helpers built
through normal FFmpeg contrib rules. The helper boundary preserves measured
movie-time and retained-session behavior without changing normal demuxing.

Support is limited to regular local files, including mounted NAS files. Exact
selected-track mapping and bounded flat-Matroska admission reject unsupported
cases. Fresh reopen requalifies metadata plus sampled SHA256; unsampled changes
can escape detection. Provisional images share a 15-second deadline that pointer
activity cannot renew.

The [review map and reproduction instructions](README.md) describe the feature
and accompanying build/test/lifetime repairs. Apply the complete thirteen-patch
[canonical order](../CONTRIBUTION.md#apply-and-review): the repair tests depend on
feature-created substrate. The [validation table](../CONTRIBUTION.md#validation-and-limits)
summarizes executed build, helper, distribution, package, native and playback
proof with its limits. [Detailed limitations](LIMITATIONS.md) preserve unresolved
shutdown causality, reader/precision-seek gaps, unavailable platforms and the
unexecuted uninterrupted public recipe. [Historical screenshots](demonstration/README.md)
illustrate earlier rendering rather than current native qualification.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance under retained GPL/LGPL and third-party notices. Credit asserts no
sole ownership, assignment, waiver or sign-off. No maintainer endorsement or
upstream acceptance is assumed.
