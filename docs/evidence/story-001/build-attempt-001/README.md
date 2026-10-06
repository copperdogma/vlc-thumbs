# Initial upstream build attempt 001

Date: 2026-10-03. Pinned VLC 3.0.24 commit: `6de05adcbaf2e8b85fe86aad4169393098628119`.
Exact command/environment and disk measurements: [attempt.json](attempt.json).
Complete upstream output: [build.log](build.log).

Result: exit code 2 after 312.8 seconds. Prerequisite tools
completed sufficiently to enter contrib setup. Downloading the default prebuilt
contrib archive returned HTTP 404:

`http://download.videolan.org/pub/videolan/contrib/aarch64-apple-darwin27/vlc-contrib-aarch64-apple-darwin27-latest.tar.zst`

The attempt did not reach VLC configuration/compilation or produce a qualified
app. This is an unavailable dependency archive, not an observed disk failure.

- Initial free space: 10.88 GiB.
- Lowest sampled free space: 10.08 GiB.
- Final free space: 10.36 GiB.
- Retained disposable workspace: 1.15 GiB, including source,
  downloaded/extracted tool packages and tool build outputs.
- The 1 GiB free-space stop threshold was never reached. No cleanup performed.

These measure this partial attempt only; the full build's peak remains unknown.
The earlier 30 GiB suggestion was an unmeasured conservative budget, not an
upstream requirement. Other host disk activity can affect free-space samples.

The pristine source remains in `work/upstream/vlc-3.0.24`. All build mutations
are confined to ignored `work/build/`; installed VLC and user settings/media
were untouched. No product feature patch was applied.

## Supported next routes

Pinned `extras/package/macosx/build.sh` lines 274–291 supports `-c` to fetch and
compile contrib dependencies from source, or `VLC_PREBUILT_CONTRIBS_URL` to select
another prebuilt archive. An alternative archive needs compatible architecture,
SDK/deployment assumptions and recorded provenance; changing the triplet to make
a download succeed is not sufficient qualification. Source-built contribs can
reuse the completed tools, but add an unmeasured build phase and compatibility
checks. Neither route was executed in this initial attempt.
