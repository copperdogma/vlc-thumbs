# TrackNumber dependency regression — baseline acquired

Scope: normal-contrib FFmpeg9 TrackNumber change for the root-selected
[feature plan](feature-port-plan.md). This lane changes diagnostic sources only;
no playback archive, qualified helper/app, or existing fixture was modified.
VLC base is `2e358f3098c2f2b7621d1dc568de8b61ad786322`.

## Portable diagnostic inputs

- `tests/story-005/feature_dependency_fixtures.py`: Python standard library plus explicit FFmpeg/libx264, fresh output directory, 1GiB reserve and16MiB fixture bound. Generates two-second red/blue AVC, sine audio, text subtitle and a2x2 PNG cover. Reencodes EBML sizes and block TrackNumber VINTs; removes optional seek/cue tables and checksums rather than retaining stale offsets. TrackUID references remain unchanged. No imported media.
- `tests/story-005/feature_dependency_probe.c`: direct `AVStream.id`, `avformat_match_stream_specifier` for both `#ID` and `i:ID`, stream-group IDs and bounded packet MD5/PTS/DTS/duration/flags. `ffprobe id=N/A` is not used as ID evidence.
- `tests/story-005/feature_dependency_run.py`:15-second per-invocation bound, binary/fixture hashes, expected modified IDs and exact baseline packet/property comparison. Malformed controls receive no valid-input parity assertion.

Generated canonical fixtures: `work/story005-feature-dependency-fixtures002/`.
The earlier001 generation used a BMP attachment and remains preserved;002 uses
a PNG cover to exercise FFmpeg's attached-picture stream behavior. All outputs
are synthetic and ignored. Public test-path/build-list registration is pending
coordination with helper/build owners; no upstream product/test files were edited.

| Case | TrackNumbers in ordinary TrackEntry order | Classification / expectation |
|---|---|---|
| nonconsecutive | videos7/red,31/blue; audio47; subtitle63 | Valid identity and mixed-stream control |
| reordered | same numbers, reversed TrackEntries | Valid; identity survives ordinal changes |
| int-max |7,2147483647,47,63 | Valid, largest positive representable `AVStream.id` |
| too-large |7,2147483648,47,63 | Valid Matroska integer/VINT; unrepresentable int must become−1, helper must fail closed |
| duplicate |7,7,47,63 | Malformed repeated identity; observe parser and require helper ambiguity rejection |
| zero |7,0,47,63 | Malformed TrackNumber; observe parser and require helper ambiguity rejection |

[Matroska's specification](https://www.matroska.org/technical/elements.html#TrackNumber)
defines TrackNumber as positive and used by block track identification. The
reconstructed valid cases also reach EOF and decode their expected colors;
this is focused evidence, not comprehensive Matroska conformance certification.

## Acquired baseline

The direct probe linked pristine master's actual FFmpeg9 archive. Exact compile
command, hashes and results are linked from
[baseline provenance](feature-dependency-baseline-provenance.json).
All four valid inputs reached EOF, exposing five streams and138 packets each.
All stream IDs were0, so `#0` matches every baseline stream; positive ID selectors
match none. Reordered TrackEntries reverse the stream ordinal order as expected.
The attached PNG is a separate video stream with the attached-picture disposition;
it must not increase the helper's playback video count of2.

Eight independent FFmpeg color acquisitions verify red/blue at the recorded
ordinals for the valid fixtures. The reference tool/version/commands are retained
in `work/story005-feature-dependency-baseline002/independent-pixels.json`. This
does not establish candidate decoder or VLC playback parity.

Baseline also accepts duplicate and zero controls at demux EOF. That acceptance
does not make them valid inputs; duplicated numbers can route both blocks to one
stream. No playback regression can be inferred from those controls.

## Candidate and remaining gates

Normal-contrib candidate acquisition subsequently completed; see
[candidate results](feature-dependency-candidate-results.md) and its exact
provenance. Expected candidate IDs are the positive
representable TrackNumbers,−1 for unrepresentable numbers, and unchanged0 for
the cover attachment. Both selector syntaxes must follow those identities.
Valid-input packet bytes/timestamps/properties must remain identical to baseline.
Matched forced-VLC-avformat selection, pixels and packet/time behavior are a
separate gate, acquired in that report; direct dependency probing cannot replace it.

FFmpeg9 [Matroska source](https://github.com/FFmpeg/FFmpeg/blob/n9.0/libavformat/matroskadec.c)
sets the Dolby Vision stream-group ID from the enhancement stream ID. This change
therefore affects that group identity. These generated AVC fixtures create no
such group, and no copyright-external Dolby Vision fixture was acquired. Runtime
group coverage remains unavailable; source inheritance is not a runtime pass.
No broader codec, ordered-edition, negative-start or origin-policy qualification
is claimed. Python compilation and local `git diff --check` passed.
