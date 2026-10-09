# H1 bounded warm NAS helper comparison

Normal source-built prior helper6d90de5b and current H1 helperb2b5e5d were
compared AB/BA/AB locally and on the mounted SMB NAS. Each owned process supplied
one ready reply and three persistent requests; twelve processes per fixture,
72successful requests across two fixtures. All36paired prior/current replies
match exact pixel SHA256 and actual sample time. Full headers, requested targets,
wall boundaries, commands, paths, source/binary hashes, exclusive-copy ownership
and before/after NAS stats/hash remain in ignored `work/story005-nas-admission00{1,2}`.
Public summary hashes and counters are in `nas-admission-comparison.json`.

| Legal generated fixture | Prior NAS ready ms, three pairs | H1 NAS ready ms, three pairs | H1 admission work |
|---|---|---|---|
| Two hours,1200finite Clusters,801904bytes |39.144,44.136,22.466|42.900,23.098,50.741|614401bytes,1201reads,1202seeks,1207nodes|
|300second video-only stream-copy remux,228finite Clusters,9452522bytes|55.065,44.446,23.141|50.019,86.020,38.090|117376bytes,230reads,231seeks,240nodes|

The second fixture was remuxed from the provenanced synthetic
`work/fixtures/story004/preparation-base.mp4`, with no encoder, using stream-copy,
1secondcluster time limit and20MiBoutput cap. Actual finite Cluster count228 was
measured by the public fixture structural oracle; requested muxer settings alone
were not treated as proof. Original MP4 is unchanged. New MKV SHA256 is
b4ec452c1c95b8cc18cd9802617444402a4dc6f2994536584621653cff5c7f8e.

Both retain open_count1 throughout all repeated requests. Requests took roughly
1.6–2.6ms on the compact fixture and3.1–5.1ms on the larger layout. H1 scan counts
are AVIO operation/source counters, not independently counted network round trips.
Prior ready total read32768bytes/1read/0seeks; H1 total ready647169bytes on the
1200cluster fixture and150144bytes on the228cluster fixture. Exact counter
boundaries are retained in each reply rather than adding incompatible measures.
The first local prior launch was268.453ms, other local prior launches6.085–7.091ms;
this startup outlier is retained and not excluded or labeled admission overhead.

Every response had an independent15second deadline; whole acquisition budgets
were240seconds, with continuous1GiBhost disk guard during reads and exact owned
process-group kill/reap cleanup on exit. Both completed without timeout/resource
stop. Minimum observed free space was1502244864bytes and1164750848bytes.
Post-run process-group inventory found zero remaining owned members. No NAS copies
were deleted; their unique exact paths are retained for root cleanup review.
User's installed preview PID42247 remained alive; its ongoing playback/helper and
shared host/build activity are confounds. Owned baseline GUI processes were stopped
before measurement, eliminating that test's playback/UI workload.

These fixtures were locally hashed, freshly copied and NAS-hashed before timing;
source/client/server warmth is uncontrolled. No caches were flushed, private movies
read, disconnection forced, cold-NAS distribution/p95claimed, nativeUI performed
or universal size/format bound established. These measurements support practical
bounded warm admission feasibility for the two layouts; the finite scan limits and
fail-closed contracts remain necessary on untested/stalled/larger sources.


## Reproduction limit found during final package review

The measured compact1200-Cluster fixture has a self-contained public generator.
The larger228-Cluster remux has exact input/output hashes and command in its
receipt, but a bounded trace did not recover the seed MP4's original generation
command/tool version. The older Story002 five-minute recipe has different recorded
bytes and must not be substituted as its provenance. This does not erase the
observed paired measurements, but they are supplementary local evidence rather
than a fully portable reproduction of that larger layout.

After headroom returns, generate a fresh five-minute synthetic seed with explicit
public CLI/tool provenance, remux it, measure actual Cluster structure and repeat
the same bounded comparison. Retain both old and new identities/results. No media
was generated during the storage hold and no equivalent hash was invented.
