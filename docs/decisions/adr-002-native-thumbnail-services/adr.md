---
status: ACCEPTED
date: 2026-10-04
story_refs: ["002"]
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity]
spec_refs: [spec:1, spec:2, spec:4]
related_adrs: [adr-001-media-metadata-storage]
---
# ADR-002 — Native timeline adapters and isolated thumbnail decoding

Accepted for Story 002 implementation under Cam's request to finish the story.
This selects the implementation route; behavior/performance remain to validate.

Native GUI patch on VLC 3.0.24 / 6de05ad, thin timeline-only windowed/fullscreen
adapters and one shared read-only media context/presentation. Stable source has
no qualified external slider-composition hook. Do not change installed VLC.
Track small patches and owned source; build/fixture binaries remain ignored.

Select one private arm64 helper linked to existing contrib FFmpeg 8.1.2 libs.
It passed the MP4/MKV/MPEG-4 timestamp probe. AVFoundation-only failed the same-
stream MKV; adding fallback would double qualification. Public LibVLC callbacks
lack frame PTS; host FFmpeg is x86_64 and not a product dependency.

Choose one short-lived process per uncached demand rather than a persistent
protocol for v1. This is a simplification to test: spawn/open overhead must pass
end-to-end latency. One active + one latest pending demand; replace obsolete
pending work, terminate obsolete/stuck worker, generation-check every reply.
If launch/open cost misses targets, retain the same API but evaluate a persistent
worker rather than weaken latency. Protocol is in src/thumbnail-helper/PROTOCOL.md.

Aspect-fit <=320x180, half-second buckets, immediate time/loading, 32MiB RAM LRU
and 256MiB disk LRU. Fresh namespace each media-open generation, selected track,
file device/inode/size/nanosecond mtime+ctime and transform/protocol version.
Check file state before hit/after decode. No cross-open image reuse without fresh
content identity, which is not required in 002. Continuous external rewriting
is unsupported; detect ordinary changes and clear/reject. Cache owns only its
Caches/TimelineThumbnails subtree; cannot touch Application Support labels.

Preserve existing seek/scroll/keyboard/AX and fullscreen fade. Required native
proof covers main, detached, native and custom fullscreen, error/cancel/media
switch, paired playback and root-defined preview thresholds. No separate UI.
No public binary distribution; helper packaging/source/license audit is recorded,
not treated as a general clearance. LGPL configuration alone is insufficient.

Alternatives and primary evidence: docs/research/timeline-implementation-plan.md,
docs/evidence/story-001/thumbnail-probe-20261004 and pinned VLC source inventory.
Missing/ambiguous PTS, selected-track mapping or unsupported presentation must
show unavailable rather than a wrong successful frame. Frame/time correctness,
latency and full fixture support are implementation acceptance gates.

## Sampling revision — Cam-directed keyframe MVP, 2026-10-04

Use existing compressed keyframes as the initial preview samples. They still
need decoding, scaling and color conversion, but non-keyframe decoding can be
skipped. Prefer the preceding available keyframe without searching forward
through a whole long GOP. Show pointer target time and actual sample time
separately. Verify sample identity/PTS, not an invented half-second proximity
requirement. Record coarse gaps; add denser decoded samples only if trying the
MVP establishes that they are needed.

Alternatives: exact demand decoding passed diagnostic timing/image checks but
adds work unnecessary for Cam's stated MVP; nearest-keyframe forward search may
require scanning a long GOP and is unnecessary initially. Keyframe cache seeding
and persistent indexing are optional optimizations, not prerequisites.

This revises sampling before keyframe scoring, preserves previous evidence, and
does not change the Ideal, media integrity, selected-track, resource, playback
or native interaction requirements. Native arm64 feature minimum is macOS 11,
matching the current arm64 build; older systems remain unqualified.

## Native timeline-origin correction — 2026-10-04

For flat Matroska/WebM, retain raw block timecodes rather than subtracting FFmpeg container start_time. Native VLC seek6s in a +5s MKV shows source1s, demonstrating an initial positive gap on VLC's17s timeline. The previous generic subtraction mislabeled and sometimes selected the wrong keyframe. Other format rules remain; negative Matroska starts are ambiguous, and ordered editions are unqualified. See [native validation research](../../research/native-hover-input-validation.md) for pinned-source and visual evidence. Service cache identity includes the revised policy.


## Initial final-review correspondence boundary (2026-10-04; scoped update below)

Menu ordinals are not general container identities. The helper explicitly
rejects multiple programs and multiple Matroska/WebM video streams with
`ambiguous_track_mapping`; their enumeration orders cannot be verified using
the selected public libavformat boundary. Standard single-video MP4/MKV
sampling is unchanged. This follows the existing explicit-unavailable contract;
it does not claim multi-video MKV selected-track support. See
[primary-source/local reproduction notes](../../research/thumbnail-track-correspondence.md)
and the two checked-in program/Matroska regression runners. A maintained broad
track-identity route remains a compatibility follow-up, not an inferred mapping.
The following update supersedes this blanket rejection only for the tested AVC
multi-video Matroska path.

## Bounded Matroska TrackNumber mapping — 2026-10-05

For AVC multi-video Matroska, use the actual Matroska TrackNumber rather than
assuming FFmpeg stream-array ordinal matches VLC menu order. The private helper
build links a private FFmpeg 8.1.2 libavformat archive with Matroska TrackNumber
exposed as stream metadata. It sorts positive unique TrackNumber values, checks
the discovered video count against VLC's expected count, and returns unavailable
for mismatch, invalid identity, unsupported mappings, or more than 128 streams.
Multiple programs remain unavailable because VLC's program-local menu ordinals
are not file-global stream identities.

The 022512 build manifest records private archive SHA-256
`93d8acfd4368bb6e0ea9e82a3b8cc5c0a27d1624cb6859bc4e8534c04d035d34`. The archive
audit compares all 539 members and finds only `matroskadec.o` changed; original
VLC source and linked VLC libraries remain unchanged. The generated AVC MKV
original/reversed red-blue fixture plus a count-mismatch case passes five checks
([mapping results](../../evidence/story-002/matroska-track-mapped-contract.json),
[archive audit](../../evidence/story-002/private-libavformat-tracknumber-build.json),
[build manifest](../../evidence/story-002/app-build-tracknumber-022512.json)).
This does not establish general Matroska, WebM, multi-program, or codec/container
equivalence.

The current helper's 25 correctness/error cases and 200 standard requests pass;
the current count/cache isolation and forwarding contract passes 25
non-latency checks. A prior full service cohort remains separately recorded.
Fresh native MP4/MKV visible-latency cohorts are required because the
helper/service inputs changed. The first MP4 attempt stopped during template
setup after VLC lost foreground and scored no requests; MP4 attempt 002 is active
under the bounded idle-desktop assumption and has no result yet. The old latency
rescore and earlier playback pairs do not qualify this new input set.
