# Independent flat-timeline admission review

Read-only review against the frozen feature-port plan and FFmpeg9 pinned source.
This reviewer inspected source and fixture/test construction, without compiling,
running a helper, running native VLC or changing product files. Runtime admission,
AVIO restoration, normal dependency build and native playback proof remain separate
gates; this document makes no readiness or acceptance claim.

## Initial inspected source

Candidate-root relative paths and reported SHA256:

| File | SHA256 |
| --- | --- |
| contrib/src/ffmpeg/matroska-flat-timeline.patch | 34783e7e103df21b07c4ee44f8103cace27a22cac819702d991b75fa4da91975 |
| bin/timeline-preview/timeline-preview.c | 61fa2c51d2dd62a0bd7ea7d5b07744a166725a6dac0e5eb0fb6292bf4b604e0f |
| bin/timeline-preview/PROTOCOL.md | 30063a4f71a945238d5e34515514f2fdf35355f436c7bf5ffaaff53fcbb5e708 |
| bin/timeline-preview/test.py | dd42b041891b84e347fb6253259f6c2bb4a7781d91398e98546d16d9f4ce1414 |

Helper, protocol and test hashes were independently recomputed and matched. The
initial patch was inspected before an explicitly coordinated repair; it is
preserved by its owner as `flat-patch-first-34783e7.patch`.

## Findings reported during review

**F1: unknown first Segment can hide a later finite Segment.** The initial scan
replaced the unknown outer length with physical EOF, then parsed Info/Chapters
with all other IDs skipped as EBML_NONE. A second finite Segment or new EBML
header was therefore skipped inside that finite scan level. The existing
finite-first `end!=file_size` guard does not cover this case. Minimum correction:
explicitly reject Segment/header IDs in the admission scan and add unknown-first
multiple-Segment/header regression fixtures. This is a source-backed admission
defect, not a claimed runtime reproduction.

**F2: generic size fallback escapes restoration bookkeeping.** Initial code
called `avio_size(source)` before marking the physical cursor as moved. FFmpeg9's
implementation falls back to SEEK_END then an unchecked SEEK_SET restoration when
AVSEEK_SIZE fails. Such a custom source could return a size after failed restoration
and later return early before the patch's mandatory restoration. The actual
helper's callback returns cached fstat size on AVSEEK_SIZE and does not move, so
this is not a demonstrated normal-helper failure. Minimum correction: require a
direct supported size query, bracket it with cursor restoration on every path,
and avoid the generic fallback.

The owner began an explicit root-approved repair batch. Patch5b15937e2b0f7a1cdd2ac073d9187eadce2c428e7ebffb843ab2554dd377665d
contains F1's explicit Segment/header rejection; full final batch review awaits
its frozen hash.

## Sound boundaries and proof limits

The parser grammar uses isolated stack context and a separate512-byte AVIO buffer,
retains no chapter arrays, and skips finite media payloads. Immediate positive
ordered-flag rejection cannot be overwritten by a later unordered flag/edition.
Hard-link, family and nested chapter-link presence is checked in the matching
structural grammar; Tags cannot spoof read-only admission properties. Unknown
nested sizes are conservatively rejected. Existing EBML depth/extent checks and
explicit8MiB read,19999 scan-seek plus one restore,100000 node quotas bound the
scan, while helper watchdog bounds operation time.

The scan does not use seek indexes as proof: it walks physical Segment contents,
including late indexed/unindexed Info/Chapters. Raw callback restoration uses
original source->pos rather than avio_seek, preserving original AVIO buffer/fields.
The separate allocation is freed without freeing source buffer; temporary format
context releases no borrowed source. Restore failure invalidates admission.

Helper requests the opt-in option before open, requires that it was consumed and
checks read-only `flat_timeline_checked` plus nonnegative counters for Matroska.
Open/admission failures reach unsupported_input without stream selection, ready
reply or pixels; other formats do not claim Matroska certification. Ordinary
Matroska playback leaves option default0 and does not invoke the new scan.
Default-off source inspection is not playback proof.

Public generator `bin/timeline-preview/tests/generate_admission_fixtures.py` creates
one synthetic AVC keyframe and reconstructs structural controls independently of
the production admission parser. It exercises positive flat/default/unordered
cases; any ordered edition including hidden/late/duplicate flags; hard/medium/
family links; bogus Tags; malformed lengths/VINT; multiple finite Segments; unknown
Cluster conservative rejection;1200 finite Clusters and node quota exhaustion.
Its extent/flag/index oracle is explicitly not a full Matroska validator; ffprobe
opening does not prove ordered playback semantics. The public helper test requires
no ready/payload on rejected cases, certification/counters on admitted cases, and
byte-identical repeated time0 output around a second request to check buffered
state preservation. These assertions still require actual execution on the normal
contrib build. Tiny repeated-keyframe long fixtures prove scan structure, not real
NAS/performance behavior.

## Final repair batch source re-review

All four hashes in `helper-flat-prototype-source-freeze.json` were independently
recomputed and match the current files. F1 and F2 are closed in source. The scan
rejects a Segment or EBML header ID before syntax skipping, including after an
unknown first Segment. The size query is now direct AVSEEK_SIZE; moved state is
committed before that callback and every later early failure reaches raw callback
cursor restoration. No fallback SEEK_END or unchecked restoration remains.
Restoration failure keeps admission false. Original buffer ownership remains
untouched. No new material issue was found in this narrow repair.

The diagnostic compile receipt records actual candidate-config object compilation
with exit0. No normal dependency/helper runtime receipt was available at this
review. Unknown-first plus second-Segment/header fixtures are being added by the
public generator owner; those must execute with the existing positive buffered
decoder-state cases before admission is qualified. Generic callback failure
restoration is source-reviewed, not fault-injected here.

| Final source | SHA256 |
| --- | --- |
| `contrib/src/ffmpeg/matroska-flat-timeline.patch` | `abd605f770de85f739929c5d333bd45e8d35075b2b69720cfaecbdc0d278450e` |
| `bin/timeline-preview/timeline-preview.c` | `61fa2c51d2dd62a0bd7ea7d5b07744a166725a6dac0e5eb0fb6292bf4b604e0f` |
| `bin/timeline-preview/PROTOCOL.md` | `30063a4f71a945238d5e34515514f2fdf35355f436c7bf5ffaaff53fcbb5e708` |
| `bin/timeline-preview/test.py` | `dd42b041891b84e347fb6253259f6c2bb4a7781d91398e98546d16d9f4ce1414` |
