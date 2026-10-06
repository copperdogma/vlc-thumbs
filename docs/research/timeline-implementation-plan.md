# Timeline implementation plan

2026-10-04. Planning synthesis for Stories 002 and 003. Recommendations below
are candidates for the implementation plan/ADR gate, not accepted architecture
or completed features. The Ideal stays unchanged. Cam requested two stories:
one for thumbnails and one for bookmarks, with labels normally one to three words.

## What is established

VLC 3.0.24 is pinned at `6de05adcbaf2e8b85fe86aad4169393098628119`.
The isolated arm64 build plays, pauses and seeks generated media on this host.
Build attempt 009 and the [build runbook](../runbooks/build-vlc-macos.md) contain
the actual recipe, compatibility repairs, provenance and limits. The app is
161 MiB; the tools/contrib/build workspace is approximately 5.7 GiB. No clean
rebuild or general release qualification is claimed. Keep the existing build
and make incremental changes; recheck free space before new builds/large fixtures.

The actual native UI needs changes. Stable Lua provides dialogs and playback
access but no identified timeline drawing/hover hook; a loadable native module
does not establish a supported Cocoa slider composition API. The recommended
delivery is a small, reproducible patch series against this stable GUI plus
feature-owned source files, initially an isolated development app. A separate
companion window does not meet the requested experience. Moving to VLC master
adds baseline/build/regression work; its newer hover/tick code is a reference,
not a reason to switch now. See the [route inventory](story-001-vlc-macos-timeline.md).

Track patches, new source and build scripts in this project; keep upstream and
build outputs ignored. A fresh pinned checkout must accept the patches without
manual editing. Expect maintenance when upstream changes XIBs, slider geometry,
input lifecycle or packaging. No sustained fork/upstream commitment is implied.

## Native integration map

Paths below are relative to pinned VLC, generally `modules/gui/macosx/`.
Line numbers identify the inspected baseline, not future edited source.

| Area | Verified seam | Planned responsibility |
|---|---|---|
| Main and detached windows | `UI/MainWindow.xib:653`, `UI/DetachedVideoWindow.xib:167`; `VLCControlsBarCommon.m:293` | Timeline-specific tracking/context handling; preserve existing slider actions |
| Windowed slider | `VLCSlider.m` (137 lines), `VLCSliderCell.m:175,217` (354 lines) | Reuse drawn track/knob geometry; convert points to clamped timeline microseconds |
| Fullscreen panel | `UI/VLCFullScreenPanel.xib:70`; plain `NSSlider`; `VLCFSPanelController.m:203` (564 lines) | Separate thin adapter using the same timeline model; preserve panel styling |
| Fullscreen modes | `macosx.m:158`, `VLCVoutWindowController.m:520` | Exercise native Cocoa and custom fullscreen separately; default is custom |
| Media switch | `VLCInputManager.m:53,248` (766 lines) | Generation token and source snapshot; clear old visuals immediately; idempotent handling of old-clear/new-attach notifications |
| Duration/eligibility | `src/input/event.c:71`; `VLCControlsBarCommon.m:342` | Handle duration changes, can-seek and missing input; macOS input switch currently ignores `INPUT_EVENT_LENGTH` |
| Seek | `VLCCoreInteraction.m:455` (1,312 lines) | Integer microsecond seek request; validate actual arrival, not merely the method's YES result |
| Store roots | `src/darwin/dirs.c:123` | DATA and CACHE already include running bundle ID; append feature directory only |
| Shutdown | `VLCMain.m:353` (659 lines) | Cancel workers, drain durable operations; never defer ordinary saves until quit |

Use a timeline-specific adapter instead of adding media behavior to every
`VLCSlider` instance. Keep decoding, hashing, cache IO and SQL outside the large
existing controllers. Proposed files: `VLCTimelineContext`,
`VLCTimelineInteractionController`, `VLCThumbnailService`, `VLCThumbnailCache`,
`VLCAnnotationStore`, `VLCMediaIdentity`, plus a small preview helper. Names and
exact decomposition can change at implementation; these are ownership boundaries.

The shared context contains the current input generation, encoded source URL,
duration, seekability and video-track selection. Each view adapter owns its
tracking area and geometry. One presentation controller composes time, image and
short label content, avoiding competing tooltips. It must keep controls visible
while the pointer/editor is interacting, then restore normal fade behavior.
Do not intercept ordinary left-button scrubbing, wheel, keys or volume actions.

Source wiring establishes four required test surfaces: main window, detached
video window, native fullscreen and custom fullscreen. Baseline GUI evidence is
in [control-surfaces-20261004](../evidence/story-001/control-surfaces-20261004/README.md).
Floating fullscreen controls were not exposed by the selected-window capture;
full panel interaction/hover remains an explicit implementation qualification
gate. This is a capture limitation, not proof the panel works or is broken.

## Thumbnail route: one private decoder helper

The probes changed the recommendation. AVFoundation extracted images from our
MP4s but rejected the same H.264 stream in MKV. A small arm64 executable linked
against the **already built FFmpeg 8.1.2 contrib libraries** decoded all three
fixtures and exposed per-frame timestamps. Prefer that single helper route;
select it in an integration/decoder ADR before product implementation.

| Candidate | Evidence and disposition |
|---|---|
| AVAssetImageGenerator | Native async API and transform support; 5/5 MP4 requests succeeded, 5/5 MKV requests failed with -11828. Keep as an alternative, not a sufficient sole engine for the first MP4+MKV floor. |
| Private helper using pinned libavformat/codec/util/swscale | 15/15 tiny-fixture requests succeeded; MP4/MKV RGB hashes match at all five targets. Preferred candidate; IPC, timing normalization and production error handling remain work. |
| Independent public LibVLC player | Reuses VLC breadth; public pixel callbacks lack frame PTS and `get_time` is an input clock, not a frame identity. Snapshot returns before completion. Keep if helper coverage proves inadequate; no seek/sleep/next-frame correctness assumption. |
| Host FFmpeg CLI | Useful research fixture generator; installed executable is x86_64 and unrelated to the arm64 app. Reject as a product dependency. Building a bundled CLI is possible but duplicates capabilities available through contrib libraries. |
| Playback-input snapshot | Wrong moment unless seeking playback; reject because hover must leave viewing undisturbed. |

Measured libav open times were 0.61–2.35 ms and decode/scale requests 0.43–5.14 ms
on 3–8 second, 320×180 fixtures. The helper is 17.2 MB decimal (~16.4 MiB), arm64,
minimum OS 11, with only system dynamic dependencies. These numbers exclude
IPC, image encoding, native UI, realistic resolutions and cold storage. They
are feasibility evidence, not promised latency or percentile results.
The [probe source/results/provenance](../evidence/story-001/thumbnail-probe-20261004/LIBAV-README.md)
are retained; tiny probe code is not production-ready.

Proposed service behavior:

- Launch one private helper from the application bundle, using argument arrays
  or a framed local pipe protocol, never shell interpolation. No web server,
  listening port, external install, network media or uploads. Restrict protocols
  and external resource access so a local container cannot fetch remote media.
- One running decode plus one replaceable latest pending request. Requests and
  replies carry media generation, request ID, video stream, desired time, maximum
  dimensions and transform version. Bound message/image sizes before allocation;
  discard mismatched replies even if cancellation arrives too late.
- Seek backward to a keyframe, flush, decode forward and select the nearest
  qualified frame using its presentation timestamp. Correctly drain/retry codec
  send/receive, handle EOF/B-frames, stream/container starts, edit offsets, VFR and
  missing/ambiguous PTS. Compare normalized time with VLC's visible timeline;
  subtraction of stream start alone is not a universal mapping.
- Support the selected video track or explicitly show preview unavailable when
  it cannot be mapped; never silently preview another track. Respect aspect
  ratio, rotation and color interpretation. v1 need not bake subtitles or
  user video filters into thumbnails; document that presentation compromise.
  Unsupported HDR/color mapping must not quietly show misleading colors.
- Start with aspect-fit 320×180 bounds and half-second cache buckets. Choose a
  frame within the end-to-end correspondence budget, including quantization.
  Timestamp appears immediately; loading/unavailable state never shows the last
  video's image or an old timestamp's image as current.
- Demand-first generation; optional adjacent prefetch only when idle. No full
  movie pre-scan. Proposed limits: decoded-image LRU 32 MiB, disk LRU 256 MiB,
  one worker with measured memory/CPU cap, five-second decode timeout and bounded
  restart/backoff. Kill a stuck worker without touching playback.
- Disk key includes canonical source URL, a file freshness fingerprint,
  selected stream, bucket, renderer/decoder version and transforms. Cache files
  are atomic, validated on read and freely regenerable. A missing/corrupt cache
  is a miss. File change/switch invalidates requests immediately; cache cleanup
  is confined to its feature directory and cannot reach annotation storage.

The decoder ADR must settle cache freshness explicitly. Proposed conservative
v1: a fresh namespace per media-open generation, plus canonical URL, device/inode,
size and high-resolution modification/change times checked before cache reads
and after decode. Cross-open images are misses unless freshly verified content
identity authorizes reuse; previews can decode immediately without waiting for
a whole-file hash. This avoids trusting an old fingerprint across replacement
or restart and keeps correctness independent of Story 003. Session-only disk
entries are bounded scratch reuse, reclaimed by normal cache cleanup. Unchanged
local files are the scope; continuous external rewriting during playback is
unsupported. Metadata guards detect ordinary mutation, not every possible
same-fingerprint change. Any broader metadata-only reuse needs an explicit
weaker-contract decision, not an unnoticed optimization. Include preview tests
for same-size/preserved-mtime replacement on reopen and replacement during an
in-flight request, in addition to bookmark identity tests.

Runtime config reports LGPL 2.1-or-later and GPL/version3/nonfree disabled; static
dependencies include zlib, GSM, LAME and OpenJPEG. This inventory is **not** a
distribution clearance. Preserve exact source/checksums/configuration, review
matching licenses and source/relink obligations before packaging for others.
Add the helper to the app's build, copy and signing steps; test execution from
the development bundle without relying on a shell PATH or local library prefix.

## Bookmarks: compact labels and a transactional catalog

Recommended first UI: right-click any timeline point → Add label → small
single-line editor with captured time. Enter saves, Escape cancels. Input is
trimmed, nonempty, Unicode-safe; one to three words guides sizing and examples,
not a hard word-count validator. Right-click a marker offers edit/delete. A
marker click seeks while preserving playing/paused state. No paragraph editor,
colors, tags, global search, import/export or move/rename reassociation in v1.

When controls appear, show marker ticks and brief labels where space permits.
Hover reveals the full short label in the same presentation as the thumbnail.
Dense positions cluster with a count and a compact selectable list; never drop
a label or pick an arbitrary overlapping marker. Provide keyboard-accessible
add-at-playhead and a compact label list/menu for read/seek/edit/delete, while
retaining the timeline as the primary interaction. Expose meaningful accessible
names/timestamps/actions and preserve the existing slider role and key handling.

Every edit captures annotation ID/revision, media identity, input generation and
time. Switch/stop clears visible markers and invalidates open entry context.
A queued transaction can finish only for its captured media; its completion
cannot populate another video's UI. Duration eligibility changes independently
of position updates. Do not hash or save on the 100 ms playback position tick.

### Proposed identity, with an explicit responsiveness tradeoff

Canonical encoded file URL + full-content SHA-256 + size is the conservative
correctness baseline to measure first. Open a readable regular file read-only,
resolve symlinks, hash asynchronously, check file metadata before/after and
revalidate the path before accepting identity. Keep notes unavailable with a
small verifying state until identity is established; playback must continue.
Save against the captured verified identity. Detect ordinary external mutation
and fail closed; continuous concurrent external modification is outside v1.

Same canonical path and same bytes restore notes, including after reboot.
Replacement bytes at that path must not inherit old labels, even when size and
mtime are preserved. Keep the old record. Copies/renames/moves at other paths
do not automatically reconnect, even if bytes match. Direct target/symlink paths
share canonical identity; retargeted links do not inherit the old target's notes.
Duplicate basenames never match. No writes beside videos, so read-only media
directories work. Parse the encoded URI before path normalization; preserve
spaces, percent signs and non-ASCII characters correctly.

Full hashing may visibly delay labels on large files. Story 003 starts by measuring
it on representative sizes/storage while playing. A fast canonical path +
volume/file identity + size + modification/change-time guard is the alternative,
but changes the guarantee for undetectable same-fingerprint edits. Cached digest
reuse based only on that guard does not verify content anew. Record measured
latency and the exact guarantee in an identity/store ADR before choosing;
do not silently weaken replacement protection or call a partial hash complete.
Apple explicitly says `NSURLFileResourceIdentifierKey` is not persistent across
system restarts, so it cannot be the sole durable identity.

### Proposed storage and failure semantics

Prefer system SQLite over JSON because transaction/locking machinery is useful
for crashes and multiple VLC launches. JSON remains a viable small-data option
only with a real cross-process lock, serial read/modify/write and atomic replace;
atomic replacement alone does not prevent lost updates. ADR-001 fixes retention
and directories, not this choice. The platform arm64 link and basic revision transactions were verified in the
[SQLite probe](../evidence/story-001/bookmark-probe-20261004/README.md). Record
the schema decision before implementation; no ORM, server or daemon.

Proposed schema v1: `media(id UUID, identity_version, canonical_url,
content_sha256, size_bytes, created_at_us)` with unique URL/digest/size, and
`annotation(id UUID, media_id, time_us, label, revision, created_at_us,
updated_at_us)`, indexed by media/time/id with foreign keys. Integer microseconds,
not slider fractions, are durable truth. Root resolves through VLC_DATA_DIR,
then `TimelineAnnotations/annotations.sqlite3`; development and tests inject
isolated roots. Cache resolves separately through VLC_CACHE_DIR.

Use a serial background connection, parameterized statements, transactions,
bounded contention waits and revision-checked edits/deletes. Reload on activation
and before mutation; surface stale-edit conflicts without overwriting. Proposed
small-store settings: DELETE journal, synchronous EXTRA, fullfsync ON on macOS;
verify returned settings and cost. A save is acknowledged only after commit.
Failure preserves the draft/previous committed data and gives a recoverable
message. Quit drains pending work; it is not the primary save trigger.

Unknown newer schema, corruption or invalid records must not cause silent
delete/recreate. Preserve the original and disable unsafe writes. Future
migrations require a verified backup and transaction; no legacy import in v1.
No automatic label eviction or missing-file purge. Avoid indefinite backup
copies of deleted personal labels without an explicit retention policy. Normal
deletion is not a claim of forensic erasure. Failure tests use injected errors
and isolated stores, never filling the real disk or corrupting user data.

## Story boundaries and proof

Story 002 owns the preview helper/service/cache and the shared timeline context,
geometry and presentation seam. Story 003 owns durable identity/store and the
complete label UI, reusing that seam. They have different outputs, lifetimes,
failure cases and behavioral contracts, so two stories are warranted. Neither
becomes a backend-only task; all supported UI surfaces stay within each story.
Recommended execution order is 002 then 003. Each depends on Story 001's actual
source/build; bookmark storage does not depend on successful thumbnail decoding.
If worked independently, create/reuse the same UI adapter instead of forking it.

Both implementation plans must select their architecture with a short ADR at
the first gate. Their acceptance matrices and the [root contract](../evals/root-timeline-experience.md)
define initial targets and legal generated fixtures. These are planned capability
questions; root has never run and there is no fabricated failing root score.
After 002 run preview proof. After 003 run bookmark proof and the integrated
root, including both services together, restart, media identity and all surfaces.

Quick ideation curation: queueing theory suggests latest-demand replacement;
database concurrency suggests revisioned commits; map labeling suggests clusters
instead of dropping dense annotations; ephemeral/durable storage lifetimes
suggest independent eviction. Kept those mechanisms. Rejected whole-video
precompute (startup/disk cost), a separate companion UI (wrong experience),
dual extractors by default (extra qualification), and preferences-only history
reuse (wrong retention). The main planning thread owns these recommendations.

## Primary references and limitations

- Pinned VLC source links and API comparisons: [source inventory](story-001-vlc-macos-timeline.md).
- [Apple image extraction](https://developer.apple.com/documentation/avfoundation/creating-images-from-a-video-asset)
  and installed SDK `AVAssetImageGenerator.h` for async generation/tolerances.
- [Apple file resource identifier](https://developer.apple.com/documentation/foundation/urlresourcekey/fileresourceidentifierkey),
  [symlink resolution](https://developer.apple.com/documentation/foundation/nsurl/resolvingsymlinksinpath).
- [SQLite isolation](https://www.sqlite.org/isolation.html),
  [pragma behavior](https://www.sqlite.org/pragma.html),
  [Apple atomic writes](https://developer.apple.com/documentation/foundation/nsdata/writingoptions/atomic).
- Installed FFmpeg headers and matching source/config hashes are recorded in the
  libav probe provenance. `best_effort_timestamp` is heuristic timing; unsupported
  or ambiguous media must fail clearly rather than receive a guessed preview.

Neither a quick decoder result nor successful baseline fullscreen video proves
feature usability, real-world performance, persistence or release readiness.
