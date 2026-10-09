# Preparser experiment readiness — 2026-10-05

Scope: standalone caller of unmodified VLC master revision `2e358f3`. No upstream
source modifications, product port, native validation or external contact.

Prepared `tests/story-005/preparser_probe.c` and its README. Disposable compiler
wrapper: `work/story005-scout/build-preparser-probe.sh SOURCE BUILD`; it refuses
missing configured headers, libtool or LibVLC/core link artifacts. These files
are diagnostic substrate, not a completed minimal reuse proof.

Pinned primary source inspected locally:

- `test/src/preparser/thumbnail.c`: internal LibVLC/preparser setup and thumbnail
  request pattern; the existing test's source-date assertion is disabled.
- `include/vlc_preparser.h:130–149,438–475,497–512`: hold callback picture;
  callback may precede Submit return; cancellation may call synchronously;
  request release does not cancel an active request.
- `src/input/es_out.c:712–730,2872–2900,4442`: `video-track-id` uses canonical ES
  string IDs, rather than ordinal integers. Optional probe ID remains unused
  until same-baseline identity is established.
- `include/vlc_picture.h:482–499`, `src/misc/picture.c:549–661`: picture export
  dimension/SAR handling; probe records input/output orientation and writes
  bounded RGBA for independent inspection. Transform applicability is unproven.

The caller supports internal/external modes and diagnostic `enumerate` playback
with dummy video output. The enumeration reads `libvlc_media_player_get_tracklist`
after a bounded five-second observation, records `psz_id` and `id_stable`, and has
a30s overall alarm. Explicit track experiments require an enumerated stable string
ID, set `video-track=-1`, and reject empty/comma-separated IDs. No ID is guessed.
`include/vlc/libvlc_media_track.h:115–118` documents cross-instance stable IDs.

External-mode source inspection finds URI copied without item options at
`src/preparser/external.c:349–360` and child item recreation from URI at
`bin/preparser/main.c:218`. A default-track external result versus selected-track
internal result is therefore a discriminator to acquire, not a pass. No external
SIGTERM-resistance injection is implemented. These findings remain source evidence,
not a completed runtime experiment.

The caller preserves one preparser/item for sequential fast or precise requests;
records actual returned picture date/format, request wall time and bounded export;
uses a15s preparser timeout,17s caller deadline, cancellation without callback
lock,2s cancellation deadline, and finite process alarm covering init/teardown.
Emergency timeout is explicit exit124 and invalid acquisition.

Baseline build owner reports tools prerequisites still building; configured
`config.h`, `libtool`, `libvlccore.la` and `libvlc.la` were unavailable. No compile
or execution has occurred. Once baseline is ready, compile, run generated
fixtures sequentially, retain logs/JSON/raw images and pinned provenance, inspect
pixels and compare independent frame maps. Source PTS, transformation, selected
track, repeated reopen cost, and slow-storage behavior remain unresolved.
