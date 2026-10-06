---
status: ACCEPTED
date: 2026-10-05
story_refs: ["004"]
ideal_refs: [ideal:req:previews, ideal:req:playback-quality, ideal:req:media-integrity]
spec_refs: [spec:1, spec:2, spec:4]
related_adrs: [adr-001-media-metadata-storage, adr-002-native-thumbnail-services]
---
# ADR-003 — Persistent thumbnail preparation and cache freshness

## Context and Ideal alignment

Cam authorized finishing Story 004 and selected progressive broad coverage plus
hover priority. The current helper reopens/probes an 8.44 GiB NAS movie per miss;
measured reads dominate scaling. Reusing state closes the immediate-preview gap.
Thumbnail caches remain disposable under ADR-001, distinct from personal labels.

## Selected technical plan

Retain one helper per media/selected-track context. Keep file, demuxer and decoder
open. Version 3 pipe protocol: bounded ASCII request lines `id time_us`, then a
JSON line and its declared bounded RGBA payload. A startup ready response reports
duration and open/read metrics; request replies carry IDs, actual PTS and typed
errors. Keep the existing single-shot v2 CLI for correspondence regressions.
Flush packet/frame/decoder state after each backward keyframe seek. Do not change
track mapping, color/transform qualification or permit secondary/network IO.

One active extraction and one latest hover intent. Ordinary pointer movement
cancels presentation only; results can still enter the matching cache. Media,
track, preference, file-state changes and shutdown terminate obsolete workers.
Independent startup/request wall watchdogs: 15 seconds, idle wait exempt; CPU
budget is per operation, not a lifetime RLIMIT_CPU that kills healthy long-lived
workers. Retain allocation/decoder/RSS bounds (128/320/512 MiB), one codec thread.
Per-operation requests are finite and malformed input exits. Parent watchdog also
covers blocked pipe/file access and forced process death. A separate guarded
metadata helper performs file-state checks; the UI process never stats or resolves
remote media paths. A coordinator owns identity/cache state while a separate
serial extraction queue waits for decoding, so valid cached presentation does not
wait behind an active extraction. Collect bytes/open/seek
counts before deciding further demux optimization; no blanket skip_frame promise
removes codec delay or container IO.

Finite coarse plan: target about one sample per 30 seconds, at least 7 and at
most 255 interior points, capped by duration/half-second quantization. Empty
cache uses midpoint then quarter/eighth passes. Existing actual sample times guide
largest-gap selection, with deterministic earlier-gap tie handling. Latest hover
wins; nearby planned samples follow distance with earlier/later ties alternating.
Reserve every fourth background turn for global coverage to avoid starvation.
Pace background work by at least 250 ms and one previous operation's wall time
between jobs; hover can bypass background delay. Pause on system pressure when
observable and keep preparation bandwidth/concurrency intrinsically bounded.
Transient failures have finite backoff/retries; unsupported input stops automatic
preparation. Keep sample and alias counts bounded. Demanded samples may replace least recently
used retained samples; background work refuses overflow and stops at capacity.
Retain completed-in-session work even after disk eviction to avoid quota
regeneration loops.

Cache small raw samples once per actual PTS, selected track and transform/version.
Persist target-to-sample mappings incrementally in bounded atomic manifests.
Validate manifest/payload shape, digest, ownership and byte quotas before hits.
32 MiB RAM and 256 MiB disk limits remain. Close/restart is not eviction.
Nearest cached image may bridge pending work within half a coarse interval (at
least 2 seconds, maximum 60 seconds); show its actual time and preparing state.
No cached image from an obsolete context can be presented as current.

## Accepted cache freshness decision

**Selected practical cache contract:** encoded source URI, resolved-target device/inode, size,
nanosecond mtime/ctime, selected track, transform/protocol versions, plus fresh
SHA-256 of 16 evenly distributed 64 KiB ranges including head/tail (at most
1 MiB total; small files hash fully). Check file state before/after fingerprint
and extraction. Already-qualified immutable local cache hits use one guarded
metadata observation after local lookup, immediately before delivery. The
metadata-only helper performs guarded pathname stat before/after without opening
the media; sampled/full content checks retain descriptor guards. Cache
lookup does not launch competing extraction work. Cam delegated the new
live-presentation choice; a previously loaded RAM sample may be shown
provisionally in the same qualified context with explicit Checking source state
while fresh validation runs. It is not a validated hit. Fresh open qualification
still gates all reuse, including retained RAM from a prior generation. A mismatch,
source error or15s presentation deadline clears the current image; pointer
movement cannot extend that deadline. Known failures suppress provisional reuse
until source verification recovers. Media/track/disable/close immediately clears.
No live-session TTL or older
metadata-observation reuse is introduced. The guarded helper opens the current symlink target on each context; no remote
path resolution runs in the parent. Sample verification is
off-main with a finite deadline; an unreadable/disconnected file gets no disk hit.
Ordinary replacements and changes to sampled ranges invalidate retained previews.
A deliberately or unusually modified file that preserves all metadata and changes
only unsampled bytes can evade this policy. It is not complete content equality.
This weaker boundary applies only to disposable thumbnails; labels retain their
separate Story 003 decision. Cam delegated the decision on 2026-10-05. Selected this boundary for disposable
previews, enabling it under the explicit spec revision; the limitation remains
part of acceptance and diagnostics.

Alternative: fresh full SHA-256 on every open proves content identity under stable
file guards but must read the whole file before cache reuse. On the reported
movie this is 8.44 GiB rather than at most 1 MiB of fingerprint reads, plus NAS
seek cost for sampled ranges. Measure real times; do not infer throughput from
size alone. Full verification can stay asynchronous, but cached images cannot
be described as verified before completion. A sampled hash cannot be upgraded
to this guarantee by increasing a small fixed sample count.

## Options considered

- Per-hover processes: retains isolation, repeats proven initialization cost.
- Persistent demuxer plus isolated decoders: extra IPC/ownership without current
  evidence of a decoder-specific fault requiring it.
- Persistent private libav worker: selected existing dependency boundary.
- Chronological background fill: less seeking, poor early whole-video coverage.
- Progressive gap coverage plus hover demand: selected user direction; measure
  NAS coverage per elapsed time and playback before calling it faster.
- Full hashes versus metadata-only versus metadata and sampled fingerprints:
  only full reads prove every byte unchanged. Sampled fingerprints are recommended
  for disposable previews with the explicitly weaker guarantee above.

## Primary evidence and applicability

[FFmpeg demuxing](https://ffmpeg.org/doxygen/8.0/group__lavf__decoding.html)
documents open/read/seek/close on retained contexts;
[decoder utility functions](https://ffmpeg.org/doxygen/8.0/group__lavc__misc.html)
cover flushing reusable decoder state. Verify against the pinned 8.1.2 headers
and generated fixture behavior. Existing-player primary sources and exact
progressive ordering simulations are in
[the NAS research note](../../research/nas-thumbnail-latency.md).
No external player code is copied or added as a dependency.

## Consequences and qualification

This revises ADR-002's short-lived helper and cancellation assumptions. Its old
proof stays historical. New restart, replacement, crash/hang, cache ownership,
selected-track/time/transform regressions and four-surface native proof are
required. Freeze build155231 as feature baseline before replacement; use pristine
VLC for ordinary control/playback. Record paired local/NAS results, all failures,
bytes and resource cost under shared-host load. No universal tail latency claim.

## Status

Technical plan selected under Cam's implementation request. Cam delegated the
freshness choice on 2026-10-05; metadata plus sampled hashing is accepted for
disposable previews, with the unsampled-change limitation above. The historical222506 normal-case candidate had bounded helper/cache/service contracts,
main/detached/native-fullscreen/custom-fullscreen interaction evidence, NAS
restart/cache reuse, controls, playback and preference evidence recorded in the
[current acceptance ledger](../../evidence/story-004/current-acceptance-ledger.md).

**Current status (2026-10-05): Story004 corrections are complete on001728.**
The original adversarial findings and failed intermediate pressure case remain
recorded. All-container count guards plus mapping-policy namespace invalidation
prevent unsafe old-image reuse. Bounded demand-first retention protects meaningful
hover use from background cache pollution while preserving the hard disk quota.
Final contracts/NAS/control/playback and delivered image pass under the current
ledger; unchanged native/preference/reader evidence is reused explicitly.
Bookmark identity/schema and integrated-root qualification remain separate/deferred.
