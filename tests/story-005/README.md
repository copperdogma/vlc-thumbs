# Unmodified master preparser experiment

`preparser_probe.c` is a standalone internal-API caller for pinned VLC master
`2e358f3`. It follows `test/src/preparser/thumbnail.c`, rather than adding a core
API or porting the product. It needs the configured source/build include paths,
`libvlc` and `libvlccore`, and the built VLC plugins. Compile against exactly the
same configuration as that baseline; preserve the compiler command, baseline
revision, configuration, binary hashes and plugin path in acquisition evidence.

```
preparser-probe enumerate MEDIA
preparser-probe internal|external MEDIA OUTPUT_PREFIX TARGET_US REPEATS fast|precise [VLC_ES_STRING_ID]
```

Use generated synthetic media and an existing ignored output directory. One
invocation reuses one preparser and one input item but submits a new sequential
request each time. Capture stdout as JSON Lines and stderr as VLC logs. Export
files are `OUTPUT_PREFIX-000.rgba`, etc.; dimensions/byte count are in the JSON.
The payload is raw RGBA8 from `picture_Export`, aspect fitted within320×180 using
the returned picture's display orientation and SAR. Do not apply another rotation
to these files before checking whether VLC's export already transforms them.
Export failure is an experimental result, not permission to substitute a decoder.
The default geometry is orientation-aware `display-fit`. Diagnostic environment
`VLC_PROBE_EXPORT_GEOMETRY=naive` requests320×180 directly; `auto-height` requests
0×180 to inspect automatic aspect behavior. Each mode records requested and
actual export dimensions. These modes do not apply pixel rotation themselves.
For candidate libraries, invoke the actual `.libs/preparser-probe` binary:
the generated libtool launcher prepends the libraries it was built against,
which can override supplied candidate `DYLD_LIBRARY_PATH`. Preserve dyld load
traces to establish the actual candidate core/plugins/child.

Every row records internal/external mode, requested time, fast/precise mode, raw picture date,
validity, date minus `VLC_TICK_0`, picture chroma/orientation/SAR, completion status,
wall time and export result. The picture date is an observed field; it is not
asserted to be source PTS. Compare pixels against an independent generated-frame
map, including positive-start MKV and edit-offset MP4. Measure repeated requests
separately: elapsed time plus plugin logs can expose repeated input open/probe;
timing alone does not establish reopen/read cost or NAS speedup.

`enumerate` opens diagnostic playback with dummy video output, observes it for
five seconds, and reads `libvlc_media_player_get_tracklist`. It emits each video
track's `psz_id`, `id_stable`, selected state and codec. This finite observation
does not establish exhaustive discovery. Only stable IDs support use across the
separate diagnostic playback/thumbnail input instances; retain the exact ID and
fixture/baseline provenance. It has a30s overall watchdog.

The optional track argument is VLC's canonical ES **string ID**, never a menu
ordinal or guessed Matroska TrackNumber. At the pinned source,
`src/input/es_out.c:712` reads `video-track-id` through `EsOutPropsInit`,
`:2872` matches it against `es->id.str_id`, and `:4442` wires that option to video.
The explicit option also sets `video-track=-1` and rejects empty IDs or commas.
Only test an explicit stable ID obtained from the same pinned VLC input's enumeration.
Compare red/blue tracks and
invalid IDs; an invalid request silently choosing the default is a material gap.

Test internal and external modes separately. Source inspection finds external
request transport copies URI without the input item's options
(`src/preparser/external.c:349–360`); the child creates its item from that URI
(`bin/preparser/main.c:218`). An internal selected-track image versus external
default-track image would demonstrate that gap, not a passing selected-track
contract. Date/SAR/orientation transport still needs observed pixel/time checks.
External mode also requires the baseline's `vlc-preparser` child executable and
its runtime lookup configuration. No child-source injection or SIGTERM-resistance
experiment is included in this caller.

Each preparser request has15s timeout. The caller waits at most17s, cancels
outside the callback mutex (cancellation may call synchronously), then allows2s
for completion. A finite process alarm also bounds initialization and teardown.
Timeout/emergency exit124 is an invalid acquisition with an explicit JSON error.
The callback holds any returned picture; the caller releases picture and request
after completion, then input item, preparser and LibVLC. Hardware decode is off.

Initial fixture matrix: standard MP4/MKV, long GOP, VFR MKV, positive-start MKV,
MP4 edit offset, rotation, SAR and generated two-track red/blue media; run fast
then precise sequentially with at least three repeats. This is local phase1
discrimination, not native hover, playback/resource, NAS, cache, freshness,
selected-track acceptance or public packaging proof. Font-dependent fixtures
remain local experiment inputs until portable legal regeneration is established.

## Current readiness

The diagnostic source compiles against the isolated pinned-master baseline.
[Current experiment results](../../docs/evidence/story-005/preparser-probe-results.md)
record132 synthetic requests, independent pixel/time references, selected-track
and rotation gaps, and a bounded source-warm NAS comparison. Those results do
not establish product/native acceptance. The earlier readiness note is retained
as historical evidence of the build dependency gate.
Subsequent [orientation/export discrimination](../../docs/evidence/story-005/preparser-probe-orientation-candidate.md)
and [experimental MP4/native normalization proof](../../docs/evidence/story-005/preparser-probe-mp4-candidate.md)
use separately frozen candidate receipts. Experimental MP4 ordinary-frame
correspondence does not qualify the patch's remaining trim/CTTS behavior.
