# Story005 helper9 native mapping discriminator

Status: bounded diagnostic, not an architecture acceptance or native UI qualification. **Corrected after raw-record reconciliation:** the former helper9 origin2/gap-collapse claim was unverified and false; no helper repair is supported by that claim. Acquired 2026-10-05 against untouched master `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Experimental MP4 patch0004 is stopped and was not loaded here.

## Acquisition boundary

Ignored raw evidence: `work/story005-scout/helper9-native-mapping001/` (`results.json`, `oracle.json`, `selected-track-results.json`, `track-pixel-oracle.json`, `trim-source-oracle.json`, `provenance.json`, JSONL/log/RGBA files). Standalone diagnostic: `work/story005-scout/helper9-native-playback-probe.c`; compile005 log beside it. Core SHA256 `c6c4f10547b35391893f37b45779026872938f75eac3b5594d00d6414a67d7a0`, LibVLC SHA256 `fb74fde22b5becb4ffcc2554f5ca3236cff363d238f50010bbab419ad76dd484`, diagnostic source `56021f1a897e48d0ea44a456beb406581342e4096bf6af9985a973ad622ef365`, actual MachO `055bf7038f12965fc81700767ff92756865cad1d6f972f1b591bb13f7b16d5e0`. DYLD library receipts in per-case logs identify baseline paths. Explicit baseline core/lib/plugin environment avoids generated libtool wrapper loader substitution.

Public LibVLC playback uses a 320x180 RGBA memory sink, software decode, no audio/subtitles. It enumerates tracks during playback; explicit selection only proceeds for an exact stable ID found in that list. It pauses, seeks precisely, waits at most five seconds for a fresh display, settles 500ms, then separately calls `get_time`. Overall alarm30s and subprocess35s bound each invocation. No macOS native window was used while the machine was locked. Fixed memory output dimensions do not qualify native aspect/rendering behavior.

**Pixel callback and clock query are separate observations.** This harness does not expose the displayed picture's PTS or atomically correlate it with movie time. It proves which independently decoded frame the held image resembles, plus a separately sampled paused clock. Earlier attempts (`standard-4125`, `-002`, `-003`) are retained: immediate display readiness captured a queued pre-seek image; paused position callbacks did not provide exact-target readiness. They are excluded from the table. Final readiness alone is not the frame oracle.

FFmpeg independently decodes every presented frame of each fixture, scales bicubic, and ranks sparse pixels before full RGBA MAE on the top three. `oracle.json` retains commands, candidate ranks and frame counts. Low MAE (~0.34–0.74) strongly distinguishes the synthetic patterns from neighbors (~3.6–6+) but is not byte equality. FFprobe timeline here includes its normal edit-list handling; original untrimmed-source comparison is a separate oracle.

## Observations

Times in microseconds. “Held image PTS” is independent FFmpeg's best matching presented frame, not native callback metadata.

| Fixture/request | Separately queried native clock | Held image PTS/frame | MAE | Implication |
|---|---:|---|---:|---|
| standard MP4 /125000 |83334 |0 /frame0 |0.351 |First-GOP held image and clock differ by83334; no atomic correlation claim. |
| standard MP4 /4125000 |4083334 |4083333 /frame98 |0.351 |Later-GOP observations agree within1us. |
| positive-start MKV /6125000 |6125001 |6125000 /frame27 |0.349 |The initial5s gap is retained. |
| edit-offset MP4 /4125000 |4083334 |4000000 /frame48 |0.345 |Initial-GOP held image differs from queried clock; FFmpeg presents the two-second movie gap. |
| negative-CTTS MP4 /4125000 |4083334 |4000000 /frame96 |0.337 |No universal source-to-clock offset follows. |
| nonkeyframe trim MP4 /0 |83334 |No close in-edit frame; original source frame0 matches |0.352 original; best in-edit10.615 |Held image is outside the declared edit; no claim that clock labels that same sample. |

The trim oracle checks all192 in-edit presented frames, then the original `long-gop.mp4` first12 frames: original frame0 wins MAE0.352, next frame1 MAE3.632. This independently confirms outside-edit held pixels without asserting native sample provenance.

Container evidence, distinct from public `get_length` (not acquired): stock FFprobe standard start0/duration12s, edit-offset start0/duration14s, positive-start MKV start5s/duration17s. Baseline MP4 logs parse standard movie duration12s, edited movie duration14s, trimmed movie duration8s. A helper policy cannot collapse the edit-offset two-second empty edit and still call its label movie time. The executed helper9 records instead preserve this gap: both `work/story005-helper9-proof/unpatched-cases002/results.json` and `private-cases/results.json` report ready duration14000000, origin0 and actual2000000 for requests4125000/10125000/2125000. The independent helper oracle (`unpatched-oracle/comparisons.json`) matches presented frame0, PTS2000000, RGB MAE0.469728. Thus these captures support truthful movie-time labeling of the returned keyframe; they do **not** demonstrate gap collapse. Returning an earlier keyframe differs from precise playback and is permitted by the keyframe-first sampling contract.

## Selected track identity

Fresh runtime enumeration of legal reordered fixture `work/validation/story002/matroska-track-final-001/reversed-tracks.mkv` reports stable `video/1` and `video/2`. Explicit actual selection at2s yields:

| Native ID | Selected ID after request | Held color | Stock FFmpeg matching video ordinal | MAE |
|---|---|---|---:|---:|
|video/1 |video/1 |red [252,0,0,255] |1 |0.494 |
|video/2 |video/2 |blue [0,0,253,255] |0 |0.741 |

Wrong stream comparisons exceed126MAE. This demonstrates ordinal inversion, not count parity. The private helper9 agent separately reports its TrackNumber-sorted ordinal0→TrackNumber1/red and ordinal1→TrackNumber2/blue; that sort agrees with these native IDs in this qualified fixture. “Ordinal” must specify the owning pipeline; stock demux order differs.

Pinned source supports a bounded mapping: `modules/demux/mkv/matroska_segment.cpp:1106` assigns Matroska TrackNumber to `fmt.i_id`; `src/input/es_out.c:2382–2394` builds `video/<fmt.i_id>` for stable primary-source tracks (unstable adds `/auto`, preceding code may add source prefixes). `include/vlc/libvlc_media_track.h:113–118` documents `psz_id` and the stability certificate. `include/vlc/libvlc_media_player.h:1792–1811` defines get/set movie time in microseconds; selection documentation at2255 requires IDs obtained from a tracklist. Matroska `mkv.cpp:378–380` returns its PCR and its decode path at570–571 applies segment/codec shifts; ordered editions are outside this qualified flat-fixture lane.

## Required mapping or rejection

1. Master integration must carry the exact currently selected stable ID. For qualified flat Matroska, join a verified TrackNumber to native `video/<TrackNumber>`; check uniqueness/range, all relevant tracks and selected-ID presence. Do not infer ordinal correspondence from equal counts. Reject unknown, unstable, prefixed or ambiguous identities until independently supported. The diagnostic did not prove generalized MP4 multitrack identity or linked/ordered Matroska mappings.
2. The helper label contract is the actual selected **keyframe's movie-timeline PTS**, independent of playback's held image. Nearby-target policy may legitimately choose a different frame from precise native playback. Native first-GOP defects do not make false helper timestamps acceptable, and helper truth does not mean those native defects are fixed.
3. Positive flat Matroska retains its timeline gap (origin0 locally supports the existing policy). MP4 empty edits, nonkeyframe trims and signed composition offsets need qualification of independent movie-timeline labels; the tested empty-edit helper9 result already preserves its two-second gap. Native held-image/clock discrepancies alone do not establish a helper defect or require helper rejection. `src/thumbnail-helper/thumbnail-helper.c:192–218` chooses format/earliest start; `:258` subtracts it; `:702` adds it to requested time. These operations alone do not establish edit semantics across libav versions. Existing `normalized>=0` preroll exclusion cannot identify out-of-edit pictures unless its origin/mapping is correct.
4. Container lengths corroborate bounded timeline expectations, but this lane does not acquire public native length for all files or prove all helper9 labels. Root owns qualification and rejection policy. No global offset workaround, product fix, GUI proof, NAS/performance claim or general MP4 repair was added.

## Provenance correction

The initial version incorrectly asserted helper9 origin2/sourcePTS4→label2. That assertion was accepted from an earlier helper-agent message without checking its raw execution records. It was an unverified relayed interpretation, not a capture from any executed binary. Raw unpatched/private captures and the helper frame oracle refute it. The superseded note is preserved under ignored `work/story005-scout/helper9-native-mapping001/helper9-native-mapping-before-provenance-correction.md`; raw logs were not changed. No new experiment or product correction was performed. Native baseline observations above remain independent and explicitly non-atomic; they do not prove an unobserved helper bug.
