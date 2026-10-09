# Owned legal NAS fixture inventory — read-only

`/Volumes/Movies` is presently mounted via SMB. Metadata-only inventory found the
previously generated synthetic Story005 MP4 copy recorded in
`work/story005-scout/preparser-nas001/provenance.json` (private exact mount/path
remains in ignored work). It is a regular nonsymlink file,11974690bytes,uid501.
The local source is `work/fixtures/story004/preparation-base.mp4`,300seconds;
prior source/copy SHA2560251953d1e959c2f1fb97bec17a946eb657898efa78462760ae1e067028c694f.
No NAS file contents were opened or hashed in this pass; no shares/files were
modified. The old receipt records cleanup success despite this path now being
present, so identity/ownership continuity must be reconfirmed before use.

Useful historical receipts:

- `work/story005-scout/preparser-nas001/results.json`: three NAS internal native
  callback delays237.960/132.677/137.316ms with3input creations; external
 232.945/213.898/171.765ms. Existing private helper startup27.995ms then repeated
 ~4msoperations with retained open_count1. Its cumulative reads grow to12.10MB.
  These are warm/uncontrolled source and historical helper facts, not currentH1.
- `tests/story-004/helper_comparison.py`: AB then BA order, record all responses,
  before/after metadata, exact binary hashes, per-request sample delivery and
  independent startup/shutdown errors; bounded process cleanup. Do not run it
  unchanged: it targets old protocol/ordinal binaries and private movie history.
- `work/validation/story004/nas-helper-comparison-sampled-001/results.json` and
  `nas-stat-open-comparison.json`: private movie historical timeout and sampled
  identity/metadata costs; source warmth uncontrolled. They are protocol/design
  references only. New legal manycluster fixture is required forH1.

## Proposed bounded manycluster acquisition route

The installed FFmpeg muxer help confirms `cluster_time_limit` milliseconds and
`cluster_size_limit` bytes. Use only generated lavfi content or the provenanced
local synthetic source. First remux the300second source locally with stream-copy
and `-cluster_time_limit 1000` into a new owned MKV. Inspect actual finite-size
Cluster count and source/container boundaries with the admission fixture/parser
lane before treating the filename/duration as proof of manycluster structure.
Retain FFmpeg command/version, output bytes/hash and count. Increase to a sparse
low-resolution1800second generated fixture if300clusters do not discriminate cost:
160x90,2fps,short GOP, bounded output size and 1secondcluster target. This yields
manyclusters without movie-sized payload; actual count must still be measured.

Root alone authorizes/acquires a fresh uniquely named synthetic NAS copy after
current helper build is ready; copy/hash can warm storage and must be reported.
Never reuse a preexisting pathname without verified ownership/hash, overwrite a
file, scan originals, clear host/server caches or force disconnection. Restrict
cleanup to the exact newly owned copy and record outcome.

Compare local/NAS and ungated/gated worker readiness plus three requests under
matched AB/BA order, exact helper/fixture hashes, admission element/seek/read
counters, startup and callback boundaries, failures and fixed independent15s
operation/watchdog deadline. Stationary queue preparation is irrelevant to helper
admission cost. Source/hash warmth, SMB cache and host activity remain confounds;
this is a bounded practical discriminator, notp95or causal-network attribution.
