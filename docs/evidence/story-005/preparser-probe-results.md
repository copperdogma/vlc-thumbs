# Unmodified preparser discrimination — 2026-10-05

Pinned VLC master `2e358f3098c2f2b7621d1dc568de8b61ad786322`, isolated arm64 baseline.
Standalone caller source hash
`663d41a25f150dfb6f93f8d20c43bb7ec47c6f5d064a7f601a5155d17f716d9b`;
probe binary hash
`df6aaa3bb62e432908063db9d72c70ddab6fb81fefbd3634d72f0e2ecb780a26`.
Compiler flags include `-Wall -Wextra -Werror`. No baseline source modification.

## Acquisition and provenance

44 sequential invocations, each with three requests:132 completions,126 pictures
and bounded RGBA exports, six expected no-picture internal invalid-ID results.
Nine generated media fixtures; internal/external and fast/precise modes; selected
red/blue tracks and an invalid-ID case. All repeats within each invocation return
identical pixels/date. No outer/process watchdog expired.

Ignored acquisition directory `work/story005-scout/preparser-matrix001` contains
commands, logs, JSON Lines, RGBA/PNG images, fixture hashes and pinned provenance:
`results.json`, `provenance.json`, `pixel-analysis.json`,
`neighbor-frame-analysis.json`, and independent FFmpeg raw references.
Portable fixture manifest/maps are in `work/story005-fixtures`; its manifest hash
is `6ce708b4728090bd799adb5ac66048a817b9dc48acff8b7e84bd55d6c5c20aab`.

Initial integration failures remain recorded: libtool required explicit CC tag;
master's media-player constructor requires three arguments; the strict compiler
rejects constant sleep and the probe now uses a finite deadline wait. First
external acquisition failed child creation without `VLC_LIB_PATH`; the working
configuration supplies baseline `modules` there and `modules/.libs` as
`VLC_PLUGIN_PATH`. No successful result is assigned to the failed acquisition.

## Required behavior discriminators

| Boundary | Locally observed result | Implication |
| --- | --- | --- |
| Standard MP4/MKV, VFR, positive-start MKV | Date-selected independent FFmpeg references match mean absolute RGBA error0.345–0.353 on changing synthetic images. Positive-start MKV fast sample is5s and precise sample6.125s. Internal/external agree. | Scoped time/pixel correspondence works on these fixtures. MP4 dates and MKV dates differ by the1µs tick-zero convention; record raw values. |
| Long-GOP MP4 | Fast request9.125s returns date0.083334s but pixels match source frame0 at0s (MAE0.352). Precise returns date9.083334s but pixels match frame216 at9s (MAE0.336). | The returned date is83.334ms later than the actual image on this fixture. It cannot yet support honest sample-time labels. |
| MP4 edit offset | Fast pixels match source PTS2s but date2.083334s; precise pixels match PTS4s but date4.083334s (MAE0.352/0.345). | Same material time/pixel discrepancy with edited timeline. No guessed offset correction adopted. |
| Rotation MP4 | Source has90° display matrix. Callback picture is320×180/orientation0. Pixels match unrotated frame96 at4s (MAE0.337), while date is4.083334s; the correctly rotated timestamp-selected reference differs MAE96.914. Actual image and correctly rotated101×180 reference inspected. | Both orientation and actual-time contracts fail; export cannot recover orientation that the picture no longer carries. |
| SAR MP4 | Picture retains SAR2:1; probe aspect-fit export is320×90. Independent display reference matches MAE0.940–0.941. | Scoped SAR preservation/export works. |
| Selected track | Diagnostic playback enumerates stable `video/1` and `video/2`. Internally, explicit1 yields red and2 yields blue. Externally, both yield default red. | Runtime confirms external item-option loss; explicit track transport is required. |
| Invalid track | `video/not-enumerated-invalid` gives no internal image with status-2147483648; externally it reports success and red pixels. | External mode silently ignores the invalid selection as well. |
| Repeated input lifecycle | Internal logs show three newly created thumbnail inputs for three requests on the same preparser/item. External child logs are unavailable through parent stderr; source recreates each child item/input. | A persistent process is not a persistent demuxer/decoder. Reopen cost remains a preparation concern. |

Date-selected matching was checked against independent frame maps. For the three
problematic MP4 fixtures, a separate ±8-frame pixel search establishes the best
source-frame match rather than treating a successful response/date as proof.
References use FFmpeg's normal display transform; a separate `-noautorotate`
diagnostic identifies the missing rotation and actual image frame. Flat-color
selected-track fixtures prove track/color, not unique frame identity or PTS.
Fast mode is reported as actual-sample behavior; it is not asserted universally
to return a keyframe. No new core API or timestamp workaround was implemented.

### Targeted first/later-GOP timestamp discriminator

Eight further invocations/24 requests use the same unchanged source/binary and
baseline hashes above. Each case runs internal/external modes with three repeats;
all return pictures and identical repeated pixel hashes/date, with no watchdog
expiry. Raw evidence and independent ±8-frame pixel references are in ignored
`work/story005-scout/preparser-timestamp-discriminators001/{results,provenance}.json`.

| Fixture/request | Mode | Returned date s | Independently matched source frame/PTS | RGBA MAE |
| --- | --- | --- | --- | --- |
| Long-GOP MP4/10.125s | Fast, internal and external | 10.000000 | Frame240/10.000000s, keyframe | 0.3504 |
| Long-GOP MP4/10.125s | Precise, internal and external | 10.083334 | Frame242/10.083333s | 0.3430 |
| Standard MP4/0.125s | Fast, internal and external | 0.083334 | Frame0/0.000000s, keyframe | 0.3510 |
| Standard MP4/0.125s | Precise, internal and external | 0.083334 | Frame0/0.000000s, keyframe | 0.3510 |

The later long-GOP seek establishes correspondence within1µs while its earlier
seek has the83.334ms error. The standard file also exhibits the error in its
first GOP, despite its previously qualified4.125s sample. This discriminates
against a uniform timestamp offset or codec-wide conversion assumption and is
consistent with the separately investigated MP4 edit/timeline mapping branch.
It does not prove a product correction; no guessed offset subtraction was added.

## Bounded source-warm NAS diagnostic

Used only the existing generated300s,11,974,690-byte preparation fixture, copied
to a unique temporary file on the previously evidenced mounted SMB Movies share.
Copy and full SHA256 verification preceded acquisition, so source/OS warmth is
uncontrolled and explicitly warm-biased. Original fixture and private media were
untouched; the newly created copy was removed successfully. Three identical
150.125s fast requests were run per path, sequentially.

| Path | Local request ms | NAS request ms |
| --- | --- | --- |
| Core internal preparser | 13.757 /1.613 /1.423 | 237.960 /132.677 /137.316 |
| Core external preparser | 84.646 /2.097 /3.505 | 232.945 /213.898 /171.765 |
| Current retained private helper | 4.033 /3.709 /4.050 | 4.010 /3.796 /3.623 |

Helper startup/open is separate:3.533ms local/27.995ms NAS, one open for each
three-request sequence. Each helper request reports3,964,928bytes read. Core
internal logs show three input creations; core byte/open metrics are not exposed
by this caller. Core and helper all report the150s sample on this generated file;
that is not independent frame/time qualification of the long fixture.

Ignored `work/story005-scout/preparser-nas001/{results,provenance}.json` retains
exact commands, copy identity, cleanup result and raw helper replies. Timing
boundaries differ: core requests include request/input setup; helper request
operations follow separately measured startup. These observations identify a
retained-context question, not general speedup, cold-NAS,8GiB media, native hover,
playback/resource, cache/freshness or upstream acceptance proof.

## Disposition

Unmodified upstream reuse is demonstrably insufficient for selected-track
transport, rotation and truthful picture-date correspondence on the tested
fixtures. Timestamp/transform source diagnosis remains separate and unresolved;
the experiment does not choose the final architecture. Core reuse with bounded
extensions remains a candidate to investigate. Existing local helper/cache
contracts and independent product/native qualification remain required.
