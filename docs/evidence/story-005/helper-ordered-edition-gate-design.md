# Ordered-edition admission: bounded read-only design

2026-10-06. H1 is an actual enforcement gap, not a demonstrated failure of the
flat fixtures. No product source edits or new ordered-edition acquisitions in
this pass. Root chooses the implementation. The frozen helper meanwhile passed
all39 focused tests on the normal source-built contrib binary; its precise scope
is recorded in helper-protocol4-normal-test-provenance.json.

## Primary facts

Matroska's ordered editions define a virtual timeline and may select/reorder
ranges and linked segments. One ordered edition is sufficient; title count does
not certify a flat timeline. EditionFlagOrdered defaults0 and accepts0/1.
[Official chapters specification](https://www.matroska.org/technical/chapters.html),
[official element schema](https://www.matroska.org/technical/elements.html).

Chapters may appear after Clusters. Without SeekHead, a parser must search the
whole file for top-level elements; normal ordering guidance does not prove that
an arbitrary input's indexes are complete.
[Official data layout](https://www.matroska.org/technical/diagram.html),
[official ordering guidance](https://www.matroska.org/technical/ordering.html).

Exact FFmpeg9 source: `libavformat/matroskadec.c:685–694` parses EditionEntry but
ignores EditionFlagOrdered (`EBML_NONE`). Header3478–3492 stops at the first
Cluster, then executes SeekHead. SeekHead1960–1995 does parse referenced Chapters
on a seekable source; it skips Cues and merely breaks/marks a broken index after
an entry parse error. Consequently a new flag exposed from the existing header
pass alone cannot certify late/unindexed Chapters or a broken/incomplete index.

Existing EBML parsing validates element lengths against parent bounds at
1371–1420, forbids unknown-length EBML_NONE elements, and skips finite-size
unneeded payload with ffio_limit/avio_skip plus an endpoint-byte read at
1520–1542. These are usable primitives for a conservative metadata admission
scan, without decoding media or writing a new helper container parser.

The native public title flags are MENU, INTERACTIVE and MAIN (`vlc_input.h:96–98`),
not ordered-edition status. Native MKV virtual_segment.cpp124–145/253 distinguishes
ordered editions internally. No reliable already-exposed native discriminator
was found. Counts or ordinary chapter lists would be inference.

## Smallest reliable conservative route

Prefer an opt-in Matroska demux admission option (normal FFmpeg default remains
unchanged), implemented inside the existing FFmpeg EBML parser, rather than a
metadata tag or a helper-side byte parser. The helper requires the option for
Matroska, verifies it was supported/consumed, and rejects missing support. Root
may choose a different public spelling or export scheme; no new API is assumed
here.

The opt-in preflight must visit the complete selected Segment before successful
open/ready, independently of SeekHead completeness. Use a small admission syntax
with the existing `ebml_parse` machinery: recognize Chapters/EditionEntry and
EditionFlagOrdered; skip all finite-size unrelated top-level payload, including
Clusters, by the existing EBML_NONE path. An isolated scan context avoids
reparsing into normal track/chapter lists or changing packet queues/index state.
Restore the original parser/AVIO position and levels after successful admission.
This needs explicit state/seek-error review, not just a boolean insertion.

Reject any nonzero ordered flag immediately, or latch an OR across every edition.
A scalar that is reset/overwritten by subsequent EditionEntries is insufficient.
Immediate rejection also handles malformed repeated1-then0 flags conservatively.
A missing flag is the schema's flat default, not an explicit positive assertion.

Require seekability and a known finite physical source bound. Allow a Segment's
unknown length only when bounded to that source end for the admission pass.
Reject unknown-length Clusters or other unskippable elements rather than scanning
media payload or claiming completion. Reject parse errors, nonprogress, bounds
failure, unsupported multi-Segment layout, inability to restore position, or
budget exhaustion. Keep the existing wall/CPU/RSS/source-change guards active.
This conservatively withholds previews for some otherwise valid layouts; root
must record that boundary. Ordinary finite-size generated MP4/MKV qualification
need not be weakened.

Do not publish admission through an ordinary AVDictionary key that Tags can
spoof or later overwrite. A supported opt-in demux option whose successful open
requires complete admission is sufficient; if a status is exported, use a
read-only/export AVOption or equivalent parser-owned property. FFmpeg opt.h362–367
provides established EXPORT/READONLY flags. Verify the helper is querying the
selected demuxer's parser-owned state, not searching untrusted file metadata.

## Minimum generated tests before acceptance

- Flat/no Chapters, simple chapter edition, and positive-start/red-blue fixtures
  remain accepted with unchanged pixel/time identity.
- Single ordered edition rejected; multiple editions ordered-first then flat,
  flat-first then ordered, ordered hidden/nondefault, and duplicate flags1-then0
  all rejected. Mixed editions must never overwrite positive evidence.
- Chapters before first Cluster and after Clusters with correct SeekHead,
  omitted SeekHead and an incomplete/broken SeekHead all rejected when ordered.
  Finite-size late simple Chapters remain accepted if admission fully completes.
- Unknown-size Cluster, truncated Chapters, lengths exceeding Segment/file,
  missing/unsupported gate and failed restore fail closed without pixels.
- Tags containing a fake admission marker cannot bypass ordered rejection or
  force rejection of ordinary flat files solely by metadata key spelling.
- Bound a many-element or stalled source with the independent launcher; retain
  actual cleanup/timeout receipts. No proof by header-only parsing or title count.

A full metadata walk introduces seek/read overhead for large NAS files; measure
it under the existing15s operation bound and parent watchdog. Completion versus
unknown is a behavioral contract. Before implementation, root should resolve
whether the conservative unknown-size rejection fits the contribution's declared
support; no broader ordered-chapter playback support is proposed.

## Linked segments and scan cost (root source finding incorporated)

The gate must also reject hard/medium linking. VLC virtual_segment.cpp145–217
can turn an unordered edition into `b_fake_ordered` when Prev/NextUID resolves;
reject those links even when the linked file is presently unavailable. Require
Info parsing for PrevUUID/NextUUID, and recursive ChapterAtom parsing for
ChapterSegmentUUID/ChapterSegmentEditionUID. Do not skip ChapterAtom wholesale:
an ordered flag alone does not exclude linked virtual timelines. SegmentFamily
is a relationship, not proof of flatness; conservative rejection of its presence
is acceptable only as an explicitly declared format limitation. Current file's
own SegmentUUID is ordinary identity and must not be confused with linking.
[Official linking notes](https://www.matroska.org/technical/notes.html).

The admission walk is O(top-level element count + examined chapter/link metadata),
not O(media payload bytes), but NAS costs remain substantial. Existing AVIO's
32KiB buffer can refill around each skipped element's endpoint and next header:
rough order up to64KiB read and1–2 seeks per Cluster, plus metadata. These are
source-based estimates, not measurements. Thousands of small Clusters could
exhaust15s wall time through NAS round trips even with small total read volume.
A smaller dedicated admission AVIO buffer could reduce bytes, but adds ownership
and restoration obligations and does not eliminate round trips. Do not invent
a throughput/p95 guarantee from the watchdog.

Expose admission read/seek/element deltas, apply a documented finite work limit
and existing active deadline, and test a long many-Cluster generated file locally
and on NAS before qualification. Bound exhaustion means unsupported/unavailable,
never successful flat admission. Fixed tiny seek caps may exclude ordinary long
movies, so root must choose them against supported-media requirements rather
than silently shrinking scope. Requiring a complete-looking SeekHead is not a
substitute: an attacker can omit late Chapters from that index. A reliable native
parser-owned eligibility property could avoid duplicate scanning, but no existing
public property was identified; title count remains insufficient.

Add generated hard-link Prev/NextUID and medium-link chapter UID cases (including
nested ChapterAtom and unordered edition), ordinary current SegmentUID controls,
missing linked file, and late-link Info/Chapters to the admission test matrix.
