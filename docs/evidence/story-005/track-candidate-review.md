# Selected video-track candidate review boundary

Pinned source: `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Detached source worktree: `work/upstream/vlc-master-story005-track`. Patch: `patches/vlc-master/0002-preparser-selected-video-track.patch`.

The request argument appends a nullable canonical stable ES string ID. Internal and external constructors validate a singular nonempty value, copy it before returning, and release it on every owned cleanup path. An explicit request creates a private input-item copy and appends trusted `video-track=-1` and `video-track-id` last overrides before input_Create snapshots ES selection; no shared input-item options are changed. An unavailable ID remains unavailable. NULL retains automatic selection.

JSON transports the optional owned request string and response acknowledgment. The worker acknowledges the requested-ID contract accepted by its internal request constructor. This is not independently measured decoded ES identity. External explicit requests reject absent or different acknowledgment and response-type mismatch before picture/file-success callback delivery. A missing field remains compatible for NULL automatic selection. All core, worker, serializer and request consumers must be rebuilt together; this private VLC field addition is not a new public libvlc API.

The callback boundary is fail-closed; a legacy worker might have written a file before its missing acknowledgment is rejected. The patch does not roll those filesystem writes back. Matched worker/core/serializer are required for explicit requests.

## Necessary mechanical corrections

- Zero-initialize the two existing stack arguments in `lib/parser.c` and `test/src/preparser/thumbnail.c`; an appended pointer otherwise has indeterminate contents.
- Read JSON `seek.pos` only for SEEK_POS. SEEK_NONE serializes no position and must deserialize successfully for default arguments.
- Correct both existing external-test guards to `defined(HAVE_VLC_EXTERNAL_PREPARSER)` so supported systems execute external regressions.
- Clean a rejected decoded response before reinitializing it, including its owned acknowledgment, picture and item.
- Route input creation, input start and new private strict-selection setup failures through the existing common completion/removal/callback path. Previously these early failures released a still-published request without a callback. The common path preserves interrupted status and exactly-once request removal/release; no allocator framework is added.

## Validation and remaining proof

All nine changed C translation units pass `clang -fsyntax-only` against the generated baseline configuration and includes, with implicit function declarations and incompatible pointer types treated as errors. `git diff --check` passes. Exact flags, source hashes and patch hash are in `track-candidate-source.json`.

The existing thumbnail test target now covers two mock tracks with distinct decoded dimensions (32×24 and 80×48), NULL/default, each valid ID, unavailable ID, empty/comma constructor rejection, copied caller lifetime, unsubmitted cleanup, and exactly one callback. Existing to-files target checks RGBA byte-count parity for both tracks and no file success for unavailable/invalid IDs. Transport cases cover both thumbnail request kinds, distinct owned strings, old missing acknowledgment, mismatch, correct acknowledgment, default absent field, invalid request strings, and JSON failure after acknowledgment allocation.

These regressions have not yet been executed. They require the matched candidate build owned by the integration builder. Real red/blue fixture track parity, selected-track identity under later player changes, process/cancellation timing and combined transform correctness remain runtime integration proof. OOM and private-copy/option/input-start allocation failures were source-reviewed, not forcibly injected. No product GUI, process implementation, image transform, MP4, source checkout outside this detached worktree, remote, commit or installed preview was modified by this candidate.

Revision 1 was rejected before integration because post-Create setters were too late for ES selection and deserialized response direction was assertion-only. Its exact patch/hash/source evidence are retained in `track-candidate-review-rejected-revision1.patch` and `.json`. Revision 2 adds pre-Create private selection, a wrong-direction transport regression, and external-preparser availability guards (process spawn alone is insufficient). Shared-item option assertions also verify conflicting original track-zero options remain unchanged. Runtime proof remains pending.

Revision 2 runtime proof: registered thumbnail tests passed both modes. Eight fresh candidate-header real URI requests show default/red=[254,0,0], blue=[0,0,255], matching byte hashes across internal/external; invalid video/999 returns no image in both. Default/red timestamps remain zero at requested6s, a separate known time gap. Registered to-files internal matrix/formats/alpha passed; external first NULL/default RGBA failed before selection because the existing JSON schema bounded format at JPEG. Revision 3 expands only that existing format validator through ARGB and adds PNG/RGBA/ARGB plus below/above-range transport checks. Source diff against revision2 is `track-candidate-revision3-review.diff`. Revision3 real to-files proof remains pending integration.

Revision3 final runtime: both actual registered targets pass once under the build owner guard. Eight real URI to-files requests pass default/red/blue with230400byte outputs and identical hashes across modes and previous picture-export probe. Invalid video/999 returns failure with no output file in each mode. The probe overwrites/frees its original ID before submission and asserts exactly one callback plus unchanged conflicting shared options. Detailed acquisition is `track-candidate-runtime-revision3-tofiles.json`. This supersedes pending revision3 to-files statements above while retaining failed revision2 evidence. No candidate source or binary changes occurred during this acquisition.
