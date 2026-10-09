# Normal-contrib TrackNumber regression results

The generated valid-input dependency and forced-VLC-avformat comparisons pass
within this bounded scope. No native UI, general codec or Dolby Vision runtime
qualification is implied. Legal fixture recipes and malformed classifications
are in [baseline status](feature-dependency-regression-status.md).

VLC pin: `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Candidate uses the normal
source-built FFmpeg9 contrib, not the earlier private archive experiment.
[Contrib receipt](feature-contrib-build-manifest.json),
[runtime receipt](feature-runtime-build-manifest.json) and
[lane hashes](feature-dependency-candidate-provenance.json) identify the exact
sources, archives, core, modules and probes. Candidate libavformat SHA256 is
`2932267e550adb7fb88261c44599df4b6c5cb729f9dc08cc03d1a0045e4d3abb`;
baseline is `f18bb3ced0b6cced9d161b776f96ffc165e5e5ef37d61735f3cf5b5b87415bfa`.

## Direct FFmpeg observations

All four valid cases reach EOF with five streams and138 packets. Positive
representable TrackNumbers become `AVStream.id`; INT_MAX is preserved;
2147483648 becomes−1. Reversed entries expose IDs63/47/31/7 in that stream order.
The attached PNG retains ID0 and attached-picture disposition1024. Both `#ID`
and `i:ID` selectors match the expected stream identity. Every valid-case packet
MD5, PTS, DTS, duration, flags and stream index is identical to the pristine
baseline; stream properties other than IDs/selector results are unchanged.

Raw candidate/paired assertion results:
`work/story005-feature-dependency-candidate003/results.json`;
baseline: `work/story005-feature-dependency-baseline002/results.json`.
This is a direct API probe; ffprobe's display of `id=N/A` is not evidence here.

## Forced VLC avformat

Eight matched demux-only invocations (four valid inputs, both builds) reach EOF
with137 packets each. Track rows, payload MD5, PTS/DTS/duration/flags, PCR and end
rows are exactly identical between arms. The cover is handled as an attachment
rather than a playback packet stream. Logs confirm the forced `avformat` demux
capability; this build supplies it through the merged `avcodec` plugin.

Sixteen playback invocations select both video identities in the four valid
inputs using enumerated VLC stable IDs. Across each pair, track enumeration and
selected IDs agree, RGBA output is byte-identical, and independent expected
red/blue color checks pass. Reordered inputs correctly select blue as `video/2`
and red as `video/3`; ordinary inputs use `video/0` and `video/1`. The PNG cover
does not increase the two-track video menu. The queried playback clock is83001us
in both arms for the125000us seek; this separately sampled clock is not atomic
picture provenance or proof of movie-time correctness.

Raw commands, logs, pictures and comparisons are preserved under
`work/story005-feature-dependency-vlc004/`: `packet-invocations.json`,
`packet-comparison.json`, `playback-invocations.json`, `playback-comparison.json`.
Each probe links its own build's core/libvlc and loads that build's modules.
Candidate merged module SHA256 is
`12a2baef1773232885b23bcb7ab4daa439820f67747625fb1068901c59cb7ba5`;
candidate core is
`686613cc6d47689dc6a306b63d83835bf0a324de5131b028294a5424fea2fbbe`.

## Deliberate limits

Duplicate and zero TrackNumbers remain explicitly malformed controls: the
candidate probe exposes duplicate IDs7/7 and−1 for zero respectively. Their
parser acceptance does not establish valid media or a playback regression.
Helper fail-closed tests are owned by the helper builder; no such pass is inferred
from these dependency observations. No Dolby Vision stream group exists in these
generated AVC files; source inheritance of group ID remains a runtime coverage
gap. Ordered editions, other codecs/containers, origin repair, performance,
packaging and native UI are outside this lane. No product edits, playback archive
mutation, existing-fixture changes, install or upstream contact occurred.
