# Proposed contribution description

**Prepared for maintainer review; submission checklist incomplete.** Nothing has
been submitted. VLC's macOS scrub bar currently has no image preview of a hovered
time. This series extends the existing native hover panel with a keyframe image
and actual sampled-time caption, enabled by default with an Interface preference.
Pointer time remains the seek target; failure retains ordinary time hover.

The main-thread player context identifies the selected video and input epoch.
A service owns scheduling, bounded caches and stale-result cancellation, with
separate serial metadata/decode queues and private worker processes using normal
FFmpeg9 contrib libraries. RAM/disk caches are 32 MiB/256 MiB. Metadata plus sampled
SHA256 qualifies persistent reuse and fresh reopen; unsampled changes can escape
detection. Provisional current-session images expire within one shared 15-second
deadline that pointer movement cannot renew. Source failure/change clears them.
Regular local files, including mounted NAS files, qualify; URLs do not.

Matroska multi-video selection requires exact unique representable TrackNumber
identity. An opt-in bounded flat-timeline scan rejects ordered/linked or unsupported
structures and malformed/budget-exhausted inputs while retaining default demuxing.
Some playable files are intentionally unsupported. A leading distribution patch
lists five existing headers; the remaining review parts cover contrib, helper/build/
tests and native integration. Dependency ownership and the FFmpeg submission route
need maintainer agreement. The compact [review map and ownership question](README.md)
asks whether this retained helper boundary fits upstream expectations; native
preparser movie-time/presentation-lifetime requirements remain unresolved.

Historical qualification includes 77 helper checks, custom-AVIO fault checks,
288 counted native tests (one optional skip), separate guarded ENOSPC proof,
warm NAS pixel/time pairs and visible rendering on four control surfaces.
Ordinary controls and narrow matched playback/control measurements retain their
recorded scopes. One candidate SIGTERM shutdown ended in SIGSEGV; exact cause
remains unproved despite an unchanged upstream ownership defect and baseline
lifetime corroboration. A 133.332 ms screen-PTS hole prevents uninterrupted-video
claims. Conventional distcheck remains failed (80 pass, 5 skip, 7 fail); partial
installation/cleanup and a failed outer build runner do not establish a clean
end-to-end recipe. Actual VoiceOver navigation, precise detached seek behavior,
Intel/older macOS and universal latency remain unqualified. [LIMITATIONS.md](LIMITATIONS.md)
consolidates results, attribution, reproduction boundaries and submission gaps.
Two unchanged [native screenshots](demonstration/README.md) illustrate the historical
runtime; they do not qualify the current source changes.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**, with Cam's
approved credit. Developed with AI assistance under existing GPL/LGPL terms and
third-party notices. Credit asserts no sole ownership, assignment, waiver or
Signed-off-by. No binaries or fixture videos are included. Current helper/module builds and headless tests passed; changed helper/service
GUI behavior remains unqualified by the historical evidence.
