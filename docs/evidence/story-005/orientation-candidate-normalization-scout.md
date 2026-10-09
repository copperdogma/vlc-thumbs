# Native picture normalization before export: bounded follow-up

Source baseline is `2e358f3098c2f2b7621d1dc568de8b61ad786322`; current candidate
contains reviewed prerequisite patches including0003. No product source changed
in this follow-up. Source/compiled caller/core hashes and commands are recorded in
`orientation-candidate-normalization-diagnostic.json`; ignored full logs/source
and actual PNG renderings are under `work/story005-orientation-normalize-diagnostic`.

## General problem and native choices

The obstacle is a presentation-transform contract crossing image encoding:
allocation now retains orientation, but encoding conflates the decoded input
format with the requested final pixel format. This is different from geometry
calculation at the caller. The proper caller already uses
`video_format_TransformTo(..., ORIENT_NORMAL)` before choosing101×180.

Pinned primary source/API inspection:

- `include/vlc_image.h` exposes `image_Convert` from an image handler with explicit
  input and output `video_format_t` parameters. There is no stronger comment
  guaranteeing arbitrary cached orientation changes.
- `src/misc/image.c:ImageConvert` directly passes those formats to
  `CreateConverter`, which sets input/output formats separately and requests a
  VLC video-converter module. It holds the input picture before filtering;
  the caller retains its own reference and owns the returned picture. Existing
  callers in `modules/spu/rss.c` release their original after conversion, while
  `modules/codec/ttml/substtml.c` returns the converted picture separately.
- `modules/video_chroma/swscale.c:Init` rejects differing orientation formats.
  `modules/video_chroma/chain.c:ActivateConverter` detects an orientation
  difference and selects `BuildTransformChain`; the chain calls
  `video_format_TransformTo` and uses the existing transform/conversion modules.
- `src/misc/image.c:CreateEncoder` initializes encoder input from source format
  and overrides requested dimensions, but retains source orientation. Therefore
  the converter sees sourceorientation5 → encoderinputorientation5, merely
  resizes the unrotated pixels, and reports the requested outputorientation0.
- `ImageWrite` conversion conditions consider chroma/dimensions, not orientation;
  encoder reuse considers output codec/dimensions only; converter reuse considers
  chroma only. `ImageConvert` cached-filter restart also considers chroma only.
  A shared correction needs these lifecycle cases tested, beyond one assignment.

## Small diagnostic

An ignored copy of the preparser probe inserts native normalization before its
existing export:

1. Copy/transform the display format to normal orientation; derive aspect-fit
   dimensions from transformed visible size and SAR.
2. Set target RGBA, explicit101×180 storage/visible size, zero offsets and1:1SAR.
3. Create a fresh `image_handler_t` per picture; call `image_Convert` with the
   original decoded format and this target. Fail unavailable on NULL.
4. Export the resulting normal RGBA picture, release it, delete the handler.
   Original callback picture ownership is unchanged. No manual pixel rotation,
   new raster library or product-source patch is used.

Three internal and three external precise requests pass. All report decoded
orientation5 and normalized/exported orientation0, dimensions101×180. Every output
has the same72720bytes and SHA256
`6b11ec391679eaca56213ee42b97d0b652db19b6b2e64982eeefd4389760e810`.
DYLD_PRINT_LIBRARIES logs identify the candidate libraries; the core hash is
retained separately from the preparser probe's source hash.

Compared with the existing independently rotated actual-frame96 reference,
RGBMAE is12.15354; against the unrotated squeezed reference it is128.92022.
Actual render inspection shows portrait color bars, diagonal and rotated frame
label in the corresponding orientation; both diagnostic PNG and reference PNG
were viewed. This supports the transform direction and unsqueezed aspect for
this fixture, but the12.15RGBMAE is not pixel equivalence or a qualified color
contract. The initial frame96 reference was stale for the concurrently integrated MP4
correction. Independent audit subsequently found exactRGBMAE0 at sourceframe98,
PTS4.083333, with FFmpeg bicubic scaling, and confirmed asymmetric portrait
raster direction. See `work/story005-scout/preparser-normalization-oracle001/results.json`.
The audit is reacquiring this proof with frozen0004/module hashes and actual
Mach-O loader logs; defer the final correspondence claim to that receipt.
This diagnostic itself changed no timestamp or conversion product source.

## Decision recommendation and limits

Use service-local explicit `image_Convert` normalization with a fresh image
handler for each conversion, before caching/presentation. This is a demonstrated
nativeAPI path and avoids a further shared-library source correction for the
consumer. Use deep `video_format_Copy`/Clean ownership in product code, not this
diagnostic's borrowed shallow display copy, and bound output dimensions/bytes.
The preparser already performs asynchronous extraction; conversion must also run
on the background work lane, not in a main-thread presentation callback.
The diagnostic does not measure conversion cost, cancellation or UI behavior.

Do not assume handler reuse across orientation changes is safe from this proof.
A later optimization may recreate the handler when the complete input/output
conversion signature changes, or separately test module reconfiguration.

An alternative upstream fix would honor requested output orientation when
initializing encoder input and include orientation in conversion/reuse checks.
Its smallest reviewable scope still requires tests for same-size rotation,
rotated→normal requests, normal→rotated requests, encoder reuse and converter
reuse. It would affect all image_Write callers and does not automatically fix
picture_Export's default geometry. No such source patch is proposed as already
correct or necessary for service progress; root chooses any shared follow-up.

Remaining qualification includes all eight actual transforms, SAR/crop pixel
behavior, color/scale differences, worker cancellation and conversion resource
bounds. This single fixture diagnostic does not establish broader format or
Story005 readiness.
