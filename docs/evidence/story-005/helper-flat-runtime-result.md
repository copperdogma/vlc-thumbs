# H1 normal-contrib local runtime result

The opt-in existing-EBML-parser gate passed the actual normal-contrib helper's
38-case admission matrix and39 existing helper checks (77 total). This closes the
local source/fixture gate; NAS efficiency and native acceptance remain open.
No GUI, installation, contact or submission occurred.

Binary SHA256 `b2b5e5d13bf6d3e92f9e23193ec516d86b1f54547783fb5c53ce2fbbf6dadf73`
used the normal source-built FFmpeg9 archive, not diagnostic object replacement.
Exact source, dependency, generator, fixture and command hashes are recorded in
`helper-flat-normal-provenance.json`, `feature-h1-contrib-build-manifest.json`
and `feature-h1-helper-build-manifest.json`.

Eight flat admission fixtures were accepted. Thirty ordered/link/unknown-size/
incomplete/malformed/budget/boundary fixtures failed before ready/pixels. The
matrix includes late unindexed Chapters, mixed editions and repeated ordered
flags, forged metadata, hard/medium/family links, unsupported unknown-size
Clusters,100001-node exhaustion, and unknown-first Segment concatenation/new
EBML-document boundaries. Rejections are conservatively reported as
`unsupported_input`; validity and reasons come from the independent generator's
structural oracle, not inference from a generic FFmpeg error.

| Local fixture | Scan bytes | Physical reads | Physical seeks | Nodes | Ready operation |
|---|---:|---:|---:|---:|---:|
|6s, one finite Cluster|513|2|3|8|656us|
|7200s,1200 finite Clusters|614401|1201|1202|1207|3550us|

The entire many-Cluster process including three persistent requests completed
in55.3ms locally. The scan uses a512-byte buffer, avoiding the former projected
32KiB refill per Cluster. These are single local observations, not p95/cold-NAS
performance or a promise that every admitted movie opens within that time.
The15s operation and8MiB/20000-seek/100000-node bounds remain fail-closed guards.
Read/seek budget exhaustion was source-reviewed, not separately runtime-exhausted;
structural-node exhaustion was exercised. Deadline or kernel-I/O hard realtime
is not established by successful fast fixtures.

All32 pixel replies across16 existing media cases exactly match the prior normal
helper's RGBA SHA256, requested/actual/origin times, dimensions and payload size.
The intentional mapping change and new admission counters are excluded from
that parity comparison. This includes the initial-empty-edit origin0/movie2
regression, trim movie6.75 keyframe, negative CTTS, selected red/blue,
nonconsecutive/reordered identities, INT_MAX, rotation and SAR. Existing independent
pixel oracles remain relevant because rendering/time behavior is unchanged;
this does not replace native UI qualification.

Actual normal-libavformat customAVIO fault proof passed separately before the
storage hold. Admission on/off produced the same full1200-packet SHA256 stream.
Unsupported size queries failed closed; injected restore failure and mid-scan
read failure returned checked0 and attempted one restore. Test/callback code was
compiled with ASan/UBSan; the linked normal FFmpeg library was not instrumented,
and leak detection was disabled on macOS. This is useful buffer/ownership and
fault evidence, not exhaustive memory-safety qualification.

The resumed matrix used an independent60s outer launcher and continuous1GiB
reserve checks. Each helper had its own dedicated process group and20s outer
case deadline; both per-case and final external group checks found no members.
The run completed in3.74s, minimum free space1835364352bytes. Matrix/provenance/
parity outputs were133539bytes; pixels stayed in memory. No failed acquisition,
recompilation or new large output was introduced in this resumed run.

Next: sample the actual NAS cost with preserved legal fixtures and compare
against the pre-admission helper. Warm/cold cache state and I/O boundaries must
be explicit; a timeout merely establishes safe refusal, not acceptable latency.
