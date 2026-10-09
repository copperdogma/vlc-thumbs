# Experimental MP4 mapping and normalization discrimination — 2026-10-05

Actual frozen candidate0001+0003+experimental0004, with0002 unapplied. Runtime
hashes match [build provenance](candidate-mp4-experiment-build-manifest.json):
core `d9901cfb98f17ec4eff691aac484fa98867460d9864a0b1cab997c9d7ae61c43`,
MP4 module `99ff53037f9b832259347d82d287d1dba027c97fc83380f1e49244dc0d9ca908`,
child `3627f0ee12674a61cadfecec890e4e5d11a2b95fcd01aec082aa05f11e0154ef`.
Probe source/binary hashes remain `7250c98f...`/`68169362...` as recorded in the
[orientation acquisition](preparser-probe-orientation-candidate.md). Actual MachO
invocation plus dyld traces establishes candidate core/plugin loading. The
packaged app is outside this experimental-module acquisition scope.

## Ordinary first/later-GOP pixel proof

16 invocations/48 requests: internal/external, fast/precise, three repeats each.
All complete successfully, all repeated hashes/date match within each invocation,
and all48 exports have bounded RGBA payloads. Independent ±8-frame FFmpeg pixel
search determines each source frame rather than trusting the callback date.

| Fixture/request | Seek | Returned date s | Matched source frame/PTS | RGBA MAE |
| --- | --- | --- | --- | --- |
| Long-GOP/10.125s | Fast | 10.000000 | Frame240/10s | 0.3504 |
| Long-GOP/10.125s | Precise | 10.083334 | Frame242/10.083333s | 0.3430 |
| Standard/0.125s | Fast | 0.000001 | Frame0/0s | 0.3510 |
| Standard/0.125s | Precise | 0.125001 | Frame3/0.125s | 0.3491 |
| Long-GOP/9.125s | Fast | 0.000001 | Frame0/0s | 0.3523 |
| Long-GOP/9.125s | Precise | 9.083334 | Frame218/9.083333s | 0.3314 |
| Edit-offset/4.125s | Fast | 2.000000 | Frame0/2s | 0.3523 |
| Edit-offset/4.125s | Precise | 4.083334 | Frame50/4.083333s | 0.3374 |

Both preparser modes have identical results. Returned dates now correspond to
the independently matched image within1µs in this ordinary fixture slice. The
correction changes which picture precise seeking chooses: for example, baseline
long-GOP9.125s gave source9s mislabeled9.083334s; experimental candidate gives
source9.083333s labeled9.083334s. This is image/frame proof, not just a relabeled
old image. Fast is described as observed actual-sample behavior, not a universal
keyframe guarantee.

Ignored `work/story005-scout/preparser-mp4-candidate001` contains commands,
raw images/logs, pixel references, full-frame rankings, repeat hashes,
`results.json`, `provenance.json` and frozen runtime `candidate-hashes.json`.

**These ordinary results do not qualify experimental0004 for shipping.** Separate
[MP4 candidate results](mp4-candidate-results.md) record unresolved negative-CTTS
packet correspondence and a non-keyframe trim precise-zero failure: out-of-edit
negative picture date, failed export and no candidate pixels. Presentation
eligibility/native playback and broader edit behavior remain prerequisites.
No guessed offset, clamp, new source fix or final architecture decision was made
by this experiment.

## Independent native normalization oracle

The separate diagnostic caller uses existing `image_Convert` to normalize the
picture to orientation0 RGBA101×180 before export; no manual pixel transform or
new product source change. Its original apparent RGB MAE12 against the prior
reference was a **wrong reference frame**, not a color-quality allowance:
experimental0004 changed the actual precise sample from frame96/4s to
frame98/4.083333s. A nine-frame independent oracle (frames94–102) finds exact
RGB MAE0.000 at frame98 when matching VLC's Bicubic scaling. Frame96 reference
MAE is11.9695; neighboring97 and99 errors are7.3070 and6.0526. No tolerance was
weakened to call the result good.

Fresh frozen-candidate acquisition through the actual MachO caller repeats three
internal and three external precise requests, all yielding date4.083334s,
source orientation5, normalized/exported orientation0, dimensions101×180, and
identical RGBA SHA256
`6b11ec391679eaca56213ee42b97d0b652db19b6b2e64982eeefd4389760e810`.
All six have exact RGB MAE0 against the independently rotated/scaled source
frame98. The asymmetric test pattern and sideways timestamp/counter were also
inspected; rotation direction and portrait raster fit match the reference.

Raw independent oracle: `work/story005-scout/preparser-normalization-oracle001`.
Scored repeated acquisition and exact candidate load traces/hashes:
`work/story005-scout/preparser-normalization-candidate002`.
The first repeat through its candidate-bound libtool launcher is retained in
`preparser-normalization-candidate001`; the second uses actual MachO explicitly
to obtain dyld proof. Diagnostic normalization source hash
`3d0b1c8cd478b3760a4e5cfff48d7f94607543922dcf10ffa0ab1068259159fd`, binary hash
`220b67f888e70fd9df55e1609d127eab49c2593930e79916da0b4518894d7193`.

This establishes one native API route for the chosen rotation fixture without a
generic exporter patch. It does not qualify all transforms, color/HDR, crop/SAR,
conversion cost/cancellation, handler reuse or native presentation. Shared
exporter scope versus service-local normalization remains the root's decision.
