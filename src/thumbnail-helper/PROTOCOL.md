# Thumbnail helper protocol v2

One process per uncached demand; the service allows one running process and one
replaceable pending demand. A process reuses no playing VLC input.

Arguments (passed as an array, never through a shell):
`--input <absolute-local-path> --time-us <nonnegative-int64> --video-ordinal <int>
--video-count <1..128> --max-width <1..320> --max-height <1..180>`.
Legacy single-video invocations may omit video-count; multi-video Matroska
requires the actual native count to establish mapping.

Video ordinal follows VLC's selected video menu, excluding attached pictures.
For flat multi-video AVC Matroska, the helper-private libavformat patch exposes
TrackNumber in AVStream.id. Require native video-count equality, all supported
AVC codecs and positive unique IDs, then order videos by TrackNumber, matching
pinned VLC's map iteration. Reordered TrackEntries preserve selected images.
Count mismatch, unsupported multi-track codecs or multiple programs are explicit
ambiguous_track_mapping errors. Single-video extraction remains unchanged. The GUI must explicitly map its selected VLC video track or mark
unavailable; helper must not silently choose a different track. GUI rejects
nonseekable/nonlocal/unknown-duration input before requesting.

Stdout is one bounded JSON object line (max 4 KiB), then exactly its declared
raw RGBA8 payload. Success fields: `version:2`, `sampling:"keyframe"`, `ok:true`, `requested_us`,
`actual_us` (normalized presentation time), `width`, `height`, `channels:4`,
`payload_bytes`, `video_ordinal`, `decoded_frames`, `timeline_origin_us`,
`video_track_number` (container TrackNumber for Matroska, otherwise -1).
Payload <=320*180*4 bytes. Error is `version:2,ok:false,error:<fixed-code>` with
no payload and nonzero exit. Paths/user content need not be printed. Stderr
is bounded/redirected by caller; no malformed stdout is considered a success.

For flat Matroska/WebM, preserve block timecodes with timeline origin zero,
including an initial positive gap, matching VLC 3.0.24 native seeking. Negative
container starts are ambiguous and rejected; ordered editions remain unqualified.
Other demuxers normalize with container start_time where known, otherwise a
qualified earliest stream start, not selected-stream subtraction. Seek
backward and decode a qualified nearby keyframe while skipping non-keyframes.
Record actual PTS separately from the pointer target; keyframe gaps are accepted
for the MVP. Reject ambiguous/missing timing. EOF uses an available qualified
keyframe, not an invented beyond-end time. Respect display rotation,
sample aspect ratio and SDR color; unsupported transforms/HDR fail explicitly.
Unspecified SDR matrix uses BT.709 at encoded height >=720, otherwise BT.601;
unspecified range defaults limited except RGB/legacy YUVJ full-range formats.
Unsupported HDR/ICC and transforms return unavailable.
Only local regular files; disable network and external-resource protocols.
Read-only access, file-state checks before/after, five-second monotonic deadline,
limited decoder threads, a hard 320MiB tracked frame-buffer cap and 128MiB
individual AV-allocation cap. A 10ms watchdog terminates on observed RSS/physical
footprint above 512MiB; this is sampled and may briefly overshoot. No video writes.


Cache policy v3 includes the native video count and TrackNumber mapping version,
so entries from old file-global Matroska ordinals cannot be reused. Fresh
media-open namespaces/file guards remain. The private archive differs from the
pinned contrib archive in exactly one object; the reproducible build manifest
records every member hash and proves VLC playback libraries/source unchanged.

## Persistent worker protocol v3 (Story 004)

The v2 one-shot CLI/output above remains supported. Start a worker with
`--worker --input <absolute-path> --video-ordinal <0..127> --video-count <1..128>
--max-width <1..320> --max-height <1..180>` (no time argument). It opens and probes
once, retains the read-only descriptor, demuxer/index and decoder, and emits a
JSON line with `version:3,type:"ready",ok:true,duration_us`, no pixels. Then stdin
accepts exactly `id time_us\n`: two nonnegative int64 decimal numbers, one space,
at most 96 bytes including newline. Clean EOF ends the worker. Invalid, overlong
or incomplete requests emit `invalid_request` with zero payload and retire.

Each request response is one <=4096-byte JSON line followed by exactly its
`payload_bytes` RGBA bytes. Successful fields match v2 except `version:3` and
additional `id`. Errors include `version:3,id,requested_us,ok:false,error` and
`payload_bytes:0`. Startup errors may have no requested_us. Seek backward for
every request, flush codec buffers, and clear packet/frame/selection references;
request order can move in either direction without inheriting decoder state.
Track mapping, timestamp and display qualifications are unchanged. File descriptor
and path stat identities must match startup before and after every request;
`media_changed`, resource limits and timeouts retire the worker.

Ready and responses report cumulative `bytes_read`, `read_calls`, `seek_calls`,
`open_count:1`, and `operation_us` (monotonic elapsed startup/request work).
Responses also report `request_bytes_read`, `request_read_calls`,
`request_seek_calls`. Calls count actual system read/lseek operations; AVSEEK_SIZE
queries are excluded. These are diagnostics, not a network-transfer meter.

Startup, each active request and worker teardown have independent 15-second wall and process CPU
budgets. EOF/retirement re-arms the watchdog before releasing decoder/demuxer resources
and closing the descriptor. Idle time between requests is exempt; worker CPU is not constrained by
one lifetime RLIMIT_CPU. Existing 512MiB sampled RSS/physical footprint, 128MiB
allocation, 320MiB tracked frame-buffer, pixel/packet/frame bounds still apply.
The worker watchdog NEVER writes stdout: asynchronous hard termination produces
EOF, which the parent must classify as failure (and may SIGKILL on its own
startup/request deadline). This prevents an error header corrupting an in-flight
RGBA payload. Cooperative failures produce typed zero-payload replies. Parent
bounds stdout IPC as well; a blocked output write is not an idle extraction.

## Isolated fingerprint operation

`--fingerprint full|sampled|stat --input <absolute-path>` emits one JSON line:
`version:3,type:"identity",ok:true,fingerprint:<lowercase-SHA256>,policy`,
`stat_identity:"dev:ino:size:mtimeSec:mtimeNsec:ctimeSec:ctimeNsec"`, `bytes_read`,
`read_calls`, `payload_bytes:0`. Full mode hashes every byte afresh. Sampled mode
hashes the entire file when <=1MiB; larger files hash 16 evenly spaced 64KiB
windows (including head/tail, <=1MiB read), prefixed by the NUL-terminated
`vlc-thumbnail-sampled-v1` domain, each window's offset and length as unsigned
64-bit big-endian integers, then window bytes. Offsets are
`floor((size-65536)*window_index/15)`. Small-file hashes are conventional SHA256
for either content policy (full or sampled). Caller includes policy in cache identity.

Descriptor/path stat matching before and after, regular-file-only read-only I/O,
15s wall/CPU budget and memory watchdog apply. Hard limits terminate with EOF;
cooperative errors return a fixed code and zero payload. Full timeout never
qualifies reuse. Sampled identity cannot detect changes entirely outside sampled
windows with preserved stat metadata; it is an explicitly weaker optional policy,
not evidence of full content equality. Cache policy selection belongs to ADR-003.

`stat` mode performs metadata checks without reading file contents: bytes_read
and read_calls are zero. Metadata-only mode performs guarded pathname status
observations before/after and opens no media descriptor; full/sample hashes
retain descriptor and pathname guards. Its fingerprint is SHA256 over the ASCII string
`vlc-thumbnail-stat-v1:` followed by stat_identity, without a terminating NUL.
This compact metadata digest is NOT a content identity and never qualifies
cross-open content freshness. Open/fstat/path stat/close remain inside the
independent 15-second operation watchdog; symlink targets are followed by the
read-only open and descriptor/path identities must agree before/after. No path
resolution or file path is exposed in output. Metadata deadline regression:
`python3 tests/story-004/helper_worker_contract.py --metadata-only`.

Focused regression command:
`python3 tests/story-004/helper_worker_contract.py`.

Focused teardown watchdog regression:
`python3 tests/story-004/helper_worker_contract.py --teardown-only`.

### Track-count guard correction (2026-10-05)

Both v2 with a supplied `--video-count` and v3 reject a native/helper count mismatch with `ambiguous_track_mapping` before choosing an ordinal, for every container including single-video Matroska. The legacy count-less v2 route is retained; multi-video Matroska still requires its existing explicit count/codec/TrackNumber qualification. Persistent image identity uses `v4:keyframe-countguard2:transform1`, preventing reuse of images from the older `keyframe-tracknumber` mapping policy; manifest format remains v4. This guard rejects demonstrated ambiguity rather than establishing universal stream correspondence for every codec/container.
