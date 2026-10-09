# Helper9 movie-origin decision — bounded research

General problem: the first presentation timestamp is not necessarily the
container movie-timeline origin. A leading empty edit can delay the first frame
without moving movie zero. This review identifies a potential robustness policy;
the current acquisitions do not demonstrate an origin defect requiring repair.
It does not change the qualified helper/app or select the contribution route.

## Primary source and applicability

Inspected official FFmpeg9.0 release source, with the selected VLC contrib
patches, at `work/story005-helper9-proof/ffmpeg-9.0`. The archive SHA512 matches
VLC master `2e358f3098c2f2b7621d1dc568de8b61ad786322`'s pinned checksum; see
[download receipt](helper9-source-download.json) and
[build manifest](helper9-private-build-manifest.json).

- [AVFormatContext contract](https://github.com/FFmpeg/FFmpeg/blob/n9.0/libavformat/avformat.h#L1433): `start_time` is the first frame's position, deduced from streams, in AV_TIME_BASE units. `duration` is a duration, also potentially deduced from streams. Neither field promises a movie-zero normalization offset or an absolute endpoint. Local source lines1433–1451 agree with the [official API documentation](https://ffmpeg.org/doxygen/trunk/structAVFormatContext.html).
- [MOV edit-index handling](https://github.com/FFmpeg/FFmpeg/blob/n9.0/libavformat/mov.c#L4432): `mov_fix_index` accumulates edit durations in the edited timeline, retains leading empty-edit duration, handles negative CTTS through DTS shifting, and marks samples outside the edit for discard while retaining decode references. At local lines4648–4665 it deliberately preserves positive initial empty-edit time, sets stream start time to that gap, and adjusts the stream duration. Default options are `ignore_editlist=0`, `advanced_editlist=1` (lines12124–12129); this helper does not override them.
- [QuickTime edit semantics](https://developer.apple.com/documentation/quicktime-file-format/edit_list_atom/edit_list_table): edit duration uses movie timescale, media start uses media timescale, and media time−1 identifies an empty edit. Thus a leading empty edit occupies movie time rather than being a start offset to subtract. The official Markdown rendering was read because the HTML page requires JavaScript.
- FFmpeg9's existing [empty-edit seek reference](https://github.com/FFmpeg/FFmpeg/blob/n9.0/tests/ref/seek/empty-edit-mp4) starts packet PTS/DTS at5s for its5s initial gap. This is corroborating upstream coverage, not qualification of our helper.

## Potential robustness policy, not an approved repair

If separately warranted and approved, in the **owned helper copy only**, recognize FFmpeg's exact MOV-family demuxer
name `mov,mp4,m4a,3gp,3g2,mj2` in `origin_for()` and select origin0, as the existing
flat Matroska policy does. Preserve FFmpeg's already-edited packet/frame timeline:
seek using the movie request directly and report the selected presentation PTS
directly. Do not subtract `fmt.start_time`, add a guessed B-frame offset, or
reimplement MOV edits in the helper. Retain conservative rejection of a known
negative container start for this policy until its native interpretation is
qualified; negative decode preroll is a separate, expected condition.

This leaves ordinary B-frame files with start0 unchanged. Unit-rate positive
trims and negative-CTTS controls use FFmpeg's existing edit/composition mapping;
negative preroll remains decoded and excluded from selection. Existing PTS,
ordering, overflow, duration and resource checks remain necessary. Do not derive
an endpoint by blindly adding start_time to duration: generic duration estimation
and fragmented MOV differ. The measured edited fixture reports duration14s, which
already includes its gap.

## Discriminator and provenance discrepancy

[Native mapping evidence](helper9-native-mapping.md) records the edited fixture
`work/story005-fixtures/edit-offset.mp4`, SHA256
`387c7688c5e3df3196a6e49af67fd0bffbdee6bc8472a74bca49a89d440bebf1`:
movie duration14s; independent pixels at source frame48 correspond to movie4s.
The native clock query is not atomic provenance for that held picture.

The narrative discriminator says helper origin2 labels moviePTS4 as actual2.
However, the cited raw `work/story005-helper9-proof/unpatched-cases002/results.json`
currently records origin0 and actual2s for requests4.125/10.125/2.125; the private
case ledger agrees. Root independently confirmed these acquisitions. The frame
map places a keyframe at movie2s, so the result is truthful if its independently
measured pixels match that keyframe. A large gap from the pointer is permitted
by the declared keyframe MVP. These rows are counterevidence to the alleged
origin2 defect; the narrative must not authorize a repair or a retry loop.
Why the helper's acquired format origin differs from a separately reported
FFprobe start remains unresolved. It is not safe to infer the helper's runtime
AVFormatContext from another tool/version's output. The architecture owner may
choose one bounded instrumentation acquisition if that distinction affects the
next decision. The potential origin0 branch would not change the measured
origin0 fixture result.

If an actual origin defect is established and root approves a correction, the bounded before/after discriminator should retain exact
binary/fixture hashes, seek target, decoded selected PTS, returned actual time,
origin and independent pixel identity for the leading-gap fixture. Check existing
ordinary B-frame, trim, signed-CTTS and positive-start Matroska controls without
changing their fixtures. A first source frame at movie2 must retain label2; a
source frame at movie4 must retain label4. Keyframe sparsity may select a later
frame and is not an origin correction failure.

## Remaining qualification boundaries

Fragmented MOV can auto-disable advanced edit handling; arbitrary multi-edit,
non-unit-rate/dwell, malformed edits, negative presentation starts and other
whitelisted demuxers remain unqualified. Origin0 is a source-backed MOV timeline
policy, not proof of native parity for every MOV-family file. FFmpeg discard
propagation, independent pixels and duration/end behavior still need the small
local discriminator. No product edits, new experiments or core repair occurred
during this research pass.
