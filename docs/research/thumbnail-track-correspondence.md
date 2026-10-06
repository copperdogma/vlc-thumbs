# Thumbnail selected-track correspondence

2026-10-04 — final Story 002 review. Problem class: identifiers and enumeration
orders differ between two demuxers; a UI menu ordinal is not a stable container
track identity. Correctness requires a verified mapping or explicit unavailable.

Primary source inspection on the pinned build:

- VLC 3.0.24 `modules/demux/mkv/matroska_segment_parse.cpp:976` inserts tracks
  into a TrackNumber-keyed map. `matroska_segment.cpp:1126` iterates that map
  when adding supported elementary streams.
- FFmpeg 8.1.2 `libavformat/matroskadec.c`, `matroska_parse_tracks`, iterates
  TrackEntry array order and calls `avformat_new_stream`. Its public AVStream
  does not expose Matroska TrackNumber in this pinned path. Inspecting the
  generated fixture with ffprobe likewise yields no public stream ID.
- VLC program selection rebuilds its ES choices per program; libavformat's
  stream array is file-global. Multi-program MPEG-TS cannot use the local menu
  ordinal as a file-global video ordinal.

A review experiment reversed the two generated MKV TrackEntries without changing
TrackNumbers or packet content. Helper ordinals swapped the red/blue images.
Source inspection shows VLC's track map order remains TrackNumber-sorted.
The old ordinal contract could therefore return a wrong successful preview.
The official Matroska element reference was requested, but the web fetch timed
out; decisions here rely on the inspected pinned demuxer sources and generated
local reproduction, not an unread external reference.

Initial decision (2026-10-04): conservatively return
`ambiguous_track_mapping` for multiple programs and multiple Matroska/WebM video
streams because ordinal mapping had produced wrong successful images. This
remains the rule for multiple programs and unsupported formats, but the blanket
Matroska rejection was subsequently replaced for one bounded AVC MKV case.

Historical local tests: `multi_program_contract.py` generated two single-program
tracks and two separate programs, while the original `matroska_track_contract.py`
treated all multi-video MKV requests as ambiguous. Those results remain useful
for the tested multi-program and earlier implementation states; the latter's
blanket rejection is superseded below.

## Bounded AVC Matroska TrackNumber mapping — 2026-10-05

The correction keeps the inspected identity boundary explicit instead of
assuming the two demuxers enumerate tracks alike. A private FFmpeg 8.1.2
libavformat build exposes Matroska TrackNumber on each stream. The helper accepts
only positive unique TrackNumber values, sorts them to VLC's ordering, and
requires the discovered video-stream count to match VLC's expected count. More
than 128 streams, count mismatch, invalid TrackNumber, or another unsupported
case returns unavailable. Multiple VLC programs remain unavailable; their
program-local menus cannot safely map to libavformat's file-global stream list.

The [022512 app manifest](../evidence/story-002/app-build-tracknumber-022512.json)
records the linked private archive SHA-256
`93d8acfd4368bb6e0ea9e82a3b8cc5c0a27d1624cb6859bc4e8534c04d035d34`. The
[archive audit](../evidence/story-002/private-libavformat-tracknumber-build.json)
compares all 539 object members and finds only `matroskadec.o` changed; original
VLC source and linked VLC libraries remain unchanged.

The generated AVC two-track MKV keeps red/blue identity under original and
reversed TrackEntry order. A native-expected-count mismatch returns
`ambiguous_track_mapping` and no pixels. All five cases pass
([mapping contract](../evidence/story-002/matroska-track-mapped-contract.json)).
This is a narrow AVC multi-video MKV result, not a general Matroska/WebM or codec
claim. The current helper's 25 correctness/error cases and 200 standard requests
pass ([helper results](../evidence/story-002/helper-tracknumber-results.json));
the current service's 25 count/cache/forwarding checks also pass without timing
qualification ([service results](../evidence/story-002/service-track-count-cache-contract.json)).

Fresh native visible timing is still required. The first MP4 cohort stopped in
template setup when VLC was inactive and scored zero requests; MP4 attempt 002
is now active under the bounded idle-desktop assumption and has no result yet.
The earlier retrospective latency rescore and playback cohorts remain
scoped to their recorded inputs. Remaining uncertainty includes multiple
programs, WebM and other codecs, ordered editions, and negative Matroska origins.
No inferred stream identity is used for these cases. Final native unavailable
display proof is separate from helper protocol tests.
