# Independent frozen helper review

Read-only source/contract review of the frozen protocol4 helper, 2026-10-06 UTC.
No helper, protocol, test, dependency, build or UI source was edited by this
review; no processes were launched. This artifact does not claim contribution
readiness, normal-contrib reproduction, or native qualification.

## Exact reviewed source

Pinned master base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Files are under `work/upstream/vlc-master-story005-candidate`:

| File | SHA256 |
| --- | --- |
| `bin/timeline-preview/timeline-preview.c` | `8b6dbe3a28c45bab10d3286e28f119aff79687121fa2ed04ffe25c6a97ce8a82` |
| `bin/timeline-preview/PROTOCOL.md` | `97a9fd6748a8c58ef7db513731a42b96af41f4311cb857e185f17fcbb68c470d` |
| `bin/timeline-preview/test.py` | `199d1d30e7f72d17dec2699a627ed194b7ff83e315b263cf4370b29b048d580b` |
| `contrib/src/ffmpeg/matroska-track-number.patch` | `23baeb78b81fcb51e5068feaba2ad6f8ddfedfc3eb7dd5bca3b7d56df5ce2602` |

Hashes were independently recomputed and match the builder's freeze receipt.
Comparison source: `src/thumbnail-helper/thumbnail-helper.c`. Contract source:
`feature-port-plan.md`. Builder receipts are
`helper-protocol4-source-freeze.json`, `helper-protocol4-focused-tests.json` and
`helper-protocol4-diagnostic-build.json`.

## Material finding requiring disposition

**H1: flat Matroska eligibility is stated but not enforced by this helper.**
The helper accepts the Matroska demuxer at C lines955 onward, validates track
identities and uses origin0 at lines242 onward. It does not inspect ordered
editions or reject a non-flat chapter timeline. The pinned VLC native demuxer
honors `EditionFlagOrdered` in
`modules/demux/mkv/matroska_segment_parse.cpp:1607-1609`; the inspected FFmpeg
Matroska parser does not expose that field. A protocol disclaimer that ordered
editions are unqualified does not establish that only flat files reach this
mapping. No ordered-edition counterexample was executed during this review.

Root must either establish an upstream eligibility boundary that excludes these
inputs, authorize a bounded conservative rejection/feature discriminator with a
generated regression, or explicitly retain this unresolved limitation. Do not
claim that generic Matroska success proves native ordered-edition timeline parity.
This finding does not justify changing the corrected initial-gap MP4 origin
policy, or implementing a speculative general container parser.

## Source conclusions

- Selection arguments are required and numerically bounded; old ordinal flags,
  duplicates and unknown flags are rejected. Matroska selection matches the
  requested input ID exactly, validates positive IDs and uniqueness across
  nonattachment streams, excludes cover attachments, guards video count and
  preserves AVC-only multi-video scope. No fallback path was found. Other
  containers require exactly one nonattached video; their input ID is an echoed
  parent identity under the sole-stream/count contract, not a discovered ID.
- Decoder/frame/packet/AVIO ownership remains consistent. The accounting wrapper
  owns original frame buffers until the final reference is released; guard
  lifetime encloses frame and codec teardown. Partially constructed input and
  output allocations are cleaned. No new use-after-free or double-free was found.
- Local regular-file acquisition uses custom I/O, denies secondary opens and
  checks descriptor/path metadata around open and requests. These checks and
  sampled fingerprints are not durable media identity or proof against every
  unsampled edit. The unchanged source-policy caveat remains necessary.
- Worker framing is bounded; malformed lines retire the worker. Pixel output
  failure exits without appending JSON to a partial payload. Worker watchdog
  failures emit no bytes, so the parent must treat EOF/timeout as failure and
  terminate/reap. Idle/output blocking relies on the parent's IPC/lifetime bounds;
  teardown restarts an operation deadline. One-shot output occurs after monitor
  shutdown. Userspace watchdog bounds do not establish hard kernel-I/O deadlines.
- Keyframe timestamps are derived from decoded sample timing and are never
  replaced with the request time. Overflow/sentinel, missing/corrupt timing and
  negative-preroll handling fail or skip explicitly. The retained origin policy
  was not changed merely to follow prior mislabeled evidence.
- The normal-contrib TrackNumber assignment fits AVStream's format-specific ID
  contract and avoids truncation. VLC avformat demux uses stream ordinal for its
  ES ID; mux creates fresh output streams. No direct VLC playback use of this
  field was found. FFmpeg ID selectors and Dolby Vision group IDs are concrete
  affected consumers; focused dependency proof remains necessary.

## Test truth and remaining proof

The builder's receipt records39 passing diagnostic cases, including selected
7/31 identities/reordered entries, other track kinds/attachments, INT_MAX and
invalid identities. This reviewer inspected the source and receipt, without
independently rerunning that binary. The private archive diagnostic is not a
normal-contrib build result.

`test.py` checks corrected initial-gap origin0/actual2s, sparse trim keyframe
actual6.75s, dimensions for rotation/SAR, persistent open_count1, repeated sample
bytes, hash-policy parity and strict malformed requests. These checks do not
claim dense seek accuracy or copy the discarded initial-gap origin2 allegation.
Rotation/SAR dimension assertions alone are not independent pixel-quality
oracles; retained separate pixel references are required for that claim.

This39-case script does not directly force watchdog expiry, blocking NAS I/O,
resource exhaustion, unknown/corrupt PTS, source mutation during acquisition or
request, partial stdout, or every EOF/drain path. Those bounds received source
review here; their current-master runtime fault proof remains a separate gate.
The test harness independently bounds helper groups and checks no final group
members. It is not the product parent's watchdog or reaping implementation.

No other material new source defect was found in the inspected frozen helper.
Proceeding with bounded integration/dependency tests does not settle H1 or the
remaining fault, packaging, architecture, licensing and native acceptance gates.
