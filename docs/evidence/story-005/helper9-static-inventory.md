# Retained helper discriminator: static inventory

This is an already-listed Story005 Phase1 option, not a shipping decision.
Pinned master is `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
The existing qualified app, helper source/scripts and playback contribs remain
read-only. Proof owns only `work/story005-helper9-proof`, `helper9_*` test files
and `helper9-*` evidence. Require 1GiB free reserve and approximately1GiB maximum
incremental scratch allocation; no GUI, installation or upstream contact.

## Primary source observations

Master contrib `contrib/src/ffmpeg/rules.mak:1–12` selects the official FFmpeg9.0
release archive, with checksum verification in `contrib/src/ffmpeg/SHA512SUMS`.
Installed baseline headers report9.0 and libavformat63.1.100, libavcodec63,
libavutil61 and swscale10. All51 helper-referenced function names have declarations
in the installed headers. This text inventory is not compilation/ABI proof.

[Official FFmpeg9.0 Matroska source](https://github.com/FFmpeg/FFmpeg/blob/n9.0/libavformat/matroskadec.c):
ordinary stream creation does not publish TrackNumber in `AVStream.id` or stream
metadata. Its TrackNumber metadata at line4986 is inside the separate WebM DASH
manifest header, for streams[0]/tracks[0], not general multi-track MKV. The ignored
raw source receipt is `work/story005-scout/ffmpeg9-source-receipt.json`; downloaded
source SHA256 is `0c88b1ca79de4501fade5864304443493fbbfa26cd21bf95013ee89f186bcfd8`.
Current helper's private8.1.2 patch therefore still needs an isolated9.0 equivalent
or a separately accepted upstream change. No such acceptance is claimed.

Master MKV assigns TrackNumber to `fmt.i_id` in
`modules/demux/mkv/matroska_segment.cpp:1095–1106`; current helper uses qualified
count/codec-guarded ordinal mapping. Its3.0 timeline assumptions and acceptance
results do not qualify master. Current master stable IDs must be acquired,
not inferred from FFprobe indices.

Helper source is GPL-2.0-or-later and783 lines. Existing worker/service/cache/
scheduler sources total1096 more lines before UI/context/tests. Helper uses
Darwin Mach memory accounting and stat timestamp members; this inventory does
not propose a cross-platform helper. Existing stripped8.1.2 helper is16MiB.
Installed9.0 four static archives total approximately126MiB, not projected final
binary size. The prebuilt libavutil embeds LGPL2.1-or-later and no enable-gpl or
enable-nonfree build flag. Preserve complete source/dependency attribution.

Existing local build scripts require ignored configured8.1.2 source/object
replacement and absolute paths. A contribution cannot rely on those scripts
unchanged. Native upstream helper conventions are explicit executable targets
(`bin/preparser/Makefile.am`) and macOS package copying/rpaths/signing
(`extras/package/macosx/package.mak:80–81`). No retained-helper integration or
acceptance has been established.

## Bounded next experiment

Compile a copied current helper against actual9.0 contrib, then inspect pixels,
actual frame times, geometry and failures for ordinary and troublesome MP4s,
retained forward/backward requests and sampled fingerprint. Next adapt only the
TrackNumber object using checksum-verified official9.0 source and reproducible
configuration in owned scratch. Preserve original playback archives. Compare
reordered red/blue multi-track results with acquired master IDs. Stop on a new
broader requirement rather than silently reducing correctness/NAS/readiness gates.
