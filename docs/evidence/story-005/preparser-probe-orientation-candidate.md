# Orientation candidate and export discriminator — 2026-10-05

Scope: actual integrated candidate0003 core, internal/external preparser and
generated rotation fixture. No native UI, product bridge or final design decision.
Core frozen throughout acquisition at SHA256
`d9901cfb98f17ec4eff691aac484fa98867460d9864a0b1cab997c9d7ae61c43`.
Candidate child SHA256
`3627f0ee12674a61cadfecec890e4e5d11a2b95fcd01aec082aa05f11e0154ef`.
Explicit dyld load traces prove candidate LibVLC/core, plugins and child context.

The original probe already calculated display geometry using
`video_format_TransformTo(..., ORIENT_NORMAL)` before SAR/aspect fitting. Its
source/binary hashes are retained in the earlier report. First candidate attempt
used the libtool launcher, which prepended baseline dynamic-library paths ahead
of supplied candidate paths; it returned orientation0 and is setup-invalid for
candidate0003. That attempt remains recorded. All scored candidate runs invoke
the actual `.libs/preparser-probe` MachO with explicit candidate dynamic-library
and plugin paths, with `DYLD_PRINT_LIBRARIES=1`.

## Integrated result

Three internal and three external precise requests at4.125s all return raw
picture320×180, orientation5, SAR1:1, date4.083334s. Orientation preservation is
now demonstrated on the actual preparser path. Both modes' existing display-fit
caller exports101×180, reported orientation0, but the raw pixels are still the
unrotated image squeezed into portrait dimensions. Actual export and independent
correct portrait image were inspected. The known image/date discrepancy remains:
the pixels match source frame96/PTS4s, not the returned4.083334s date.

## Caller-sizing discriminator

After preserving the original binary/source, the diagnostic caller gained
`VLC_PROBE_EXPORT_GEOMETRY=naive|auto-height|display-fit`. This only selects
export arguments and records requested dimensions; it does not transform pixels
or patch the core. Updated probe source SHA256
`7250c98f562dc890a8f828a2c0dfa22a82e90af2921cdb06de05b1ef6604b3e4`,
binary SHA256
`681693622cc4ee9ce14a8dd33c01c028c24396b9506295321395d6fc88fc4c80`.

| Geometry | Requested size | Export result | MAE versus unrotated source frame96 | MAE versus display-rotated frame96 at result size |
| --- | --- | --- | --- | --- |
| Naive | 320×180 | 320×180/orientation0 | 0.3368 | 96.4306 |
| Auto height | 0×180 | 296×180/orientation0 | 0.7383 | 96.2344 |
| Display fit | 101×180 | 101×180/orientation0 | 0.8734 | 96.3039 |

Independent references use generated fixture frame96, FFmpeg normal display
rotation or explicitly `-noautorotate`, and matching scale dimensions. Three
successful export calls do not establish correct presentation. Correct caller
sizing alone cannot restore missing pixel rotation. Automatic aspect calculation
uses unrotated dimensions and a coded-dimension denominator in the inspected
source; the negotiated result is296×180. The probe does not yet log coded source
dimensions, so it does not attribute that exact width to a particular padding
value. This geometry behavior is separate from the pixel-transform failure.

Source inspection: `picture_Export` creates its output format without carrying
orientation; `ImageWrite`/`CreateEncoder` retain input orientation in the encoder
input/converter path. Swscale rejects *differing* input/output orientations
(`modules/video_chroma/swscale.c:429`), so describing it as silently ignoring
an orientation mismatch would be inaccurate. Here the converter scales pixels
while its two formats retain the same orientation, and the exported format is
reported normal. A separate explicit pixel-transform step in the caller, or a
correct image/export conversion path, is required. This experiment does not
choose where upstream should own that step.

Ignored `work/story005-scout/preparser-orientation-candidate001` retains original
and updated probes, failed/scored acquisitions, exact dyld traces, raw exports,
independent references, `geometry-results.json`, `geometry-pixel-analysis.json`
and `geometry-provenance.json`. Final core hash matches the frozen initial hash;
freeze released only after all acquisitions/references completed. Experimental
MP4 mapping changes are a separate subsequent receipt and proof boundary.
