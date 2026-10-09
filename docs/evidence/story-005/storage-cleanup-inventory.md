# Storage cleanup inventory — 2026-10-05

Read-only inventory for Cam's delegated cleanup review. No files were removed,
no process was stopped, and no hashes of large media/build trees were computed.
Sizes below are `du -sk` allocated KiB (filesystem block accounting), not
apparent byte lengths; directory totals can differ from summed regular-file
lengths. `df -k .` readings during this scan ranged from 1,361,684 KiB to
2,661,492 KiB available; the latest was 1,961,220 KiB. Free space is changing
while work runs; all observed readings remained above the 1 GiB stop guard.

## Active work and preserved boundaries

| Path | Allocated KiB | Tracking / state | Disposition |
|---|---:|---|---|
| `work/upstream/vlc-master-story005-candidate` | 253,496 | Entire `work/` tree ignored by `.gitignore:10`; active candidate | Preserve. Story005 implementation is active. |
| `work/upstream/vlc-master-story005` | 1,612,948 | Entire `work/` tree ignored; pinned source baseline | Preserve. (The parent `work/upstream` total is 2,538,968 KiB.) |
| `work/story005-master-candidate` | 2,816,796 | Ignored; current candidate build | Preserve. Active process list showed a `make ... check-timeline-service-edges` and XCTest against it. |
| `work/story005-master-baseline` | 2,331,460 | Ignored; baseline build | Preserve as the current comparison/control. |
| `work/story005-helper9-proof` | 381,236 | Ignored; retained helper proof | Preserve; active contracts and exact fixture/output history have not been replaced. |
| `work/story005-scout` | 957,696 | Ignored; Story005 scout records and pixel references | Preserve. Contains upstream receipts, retained prototype diffs, and helper/NAS pixel evidence; some files are in use by the candidate test/build workflow. |
| `work/story005-fixtures` | 5,216 | Ignored; generated portable fixture set | Preserve. Story005 result JSON points directly to these fixtures; generator/provenance is in `docs/evidence/story-005/fixture-generation.json`. |
| `work/story005-fixtures-before-output-check` | 5,216 | Ignored; prior successful generation retained | Uncertain; likely duplicate by name/size, but no byte-level comparison was done and it is explicitly preserved by the generation record. Not safe now. |
| `work/story005-fixtures-failed-rotation` | 5,420 | Ignored; failed fixture generation retained | Preserve as failure evidence; not a cleanup candidate. |
| `work/build` | 7,228,368 | Ignored; includes Story004 installed/qualified app builds and retained build output | Preserve. Story004 acceptance and delivery manifests rely on these artifacts; AGENTS explicitly says the qualified preview and unique acceptance evidence remain preserved. |
| `work/validation` | 1,920,856 | Ignored; includes Story004/002 raw acceptance evidence and prior attempts | Preserve. Current Story004 ledger links raw files under `work/validation/story004`; source commits do not back up these outputs. |
| `work/fixtures/story004` | 3,659,860 | Ignored generated media, not in Git index | Preserve for now. It contains 14 MP4s used in Story004 playback/preparation evidence. `docs/research/story-004-comparison-plan.md:64` documents the content recipe: copy owned five-minute video, add continuous 440 Hz/64 kbps AAC, stream-copy loop 24 times, yielding 287,360,717 bytes; later pairs use fresh file identities. A sample file has 287,360,717 logical bytes and 287,363,072 allocated bytes (2,355 bytes block padding). No per-file hash receipt was found in this scan, so regeneration does not by itself preserve historical file identity. |
| `work/story005-native-baseline` | 184,444 | Ignored | Preserve as current native baseline context/evidence. |
| `work/story005-public-fixtures001` / `002` | 7,032 each | Ignored | Preserve until source/license inventory and public-package fixture decision complete; similarly sized directories do not establish byte identity. |

Git checks: `git ls-files work` returned no tracked files; `git status --short
--ignored work` reports `!! work/`; `git check-ignore -v` points at the
`work/` rule. Story005 durable source/tests/evidence directories are currently
untracked project changes, so their files are not yet a committed backup.
Ignoring `work/` does not make its contents reproducible or disposable.

## Potential future savings, not safe to remove now

| Path | Allocated KiB | Why it may be reconsidered | What must happen first |
|---|---:|---|---|
| `work/fixtures/story004` | 3,659,860 | Largest generated-media set; a sample playback MP4 has 287,360,717 logical bytes and 287,363,072 allocated bytes (2,355 bytes allocator padding). | Candidate for later cleanup only after preserving the owned five-minute source, recording a deterministic command and validating hashes for all 14 outputs, and confirming evidence consumers do not need original file identities. APFS clone sharing can make actual reclaimed space far lower than `du` allocation. |
| `work/validation/story002` | 1,213,684 | Large historical build/test output tree. | Map every current acceptance reference, especially build manifests and inherited UI evidence, to a preserved result/archive; no broad deletion is supported by this scan. |
| `work/validation/story004` (within `work/validation`) | Not separately measured | Holds the current unique Story004 raw acceptance evidence. | Keep; only prune superseded material after line-by-line evidence-reference review and verified archival. |
| `work/story005-scout` | 957,696 | Includes old experiments and pixel/sample outputs. | Do not remove while phases 1/2 are active. First identify superseded subtrees by evidence reference and verify results have a replacement; no full-content or hash comparison was done. |
| `work/build/vlc-source` and `work/build/vlc-arm64` | Combined parent `work/build`: 7,228,368 | Large source/build outputs with multiple preserved preview apps. | Retain the qualified 3.0.24 preview and all unique Story004 artifacts. A future exact app/build inventory may identify redundant historical builds, but no current safe subset was established. |
| `work/build/*.app` (14 historical app bundles) | 2,541,528 | Individual bundles range 181,456–181,640 KiB; names identify intermediate controls/experiments and several are preserved comparisons. | Potential space to recover after mapping each bundle to manifests/screenshots/evidence consumers and confirming a superseding preserved artifact. Not safe now: baselines and comparisons remain, and APFS clone sharing means summed `du` allocation does not predict bytes reclaimed. |
| `work/story005-master-candidate/contrib/contrib-aarch64-apple-darwin19/vlc-contrib-aarch64-apple-darwin19-latest.tar.zst` | 211,180 (216,247,250 bytes) | Build-owner receipt `docs/evidence/story-005/feature-owned-storage-reclaim-proposal.json` records the candidate and baseline copies with the same SHA-256 `4eb8a33a9ea17c78bf348f922eff3d5f815673cb2839b1f6ef5796654867d973`. Baseline acquisition receipt: `baseline-prebuilt-archive.json`. | Safe-after-Cam-approval duplicate candidate. Build owner confirms baseline retains the identical archive and no active use was found. Removing the candidate copy leaves the baseline copy and acquisition receipt; APFS may reduce actual recovered bytes. |
| `work/story005-master-candidate/macos-install` | 183,564 | Build-owner receipt records 1,401 files, no app links into staging, and no active build-stage process. Canceled official build PID 27296 exited before packaging; focused test builds use `modules/.libs`. | Safe-after-Cam-approval regenerable staging candidate. Reproducer: `make -C work/story005-master-candidate macos-install` with the native SDK/build environment; `package.mak:16–22` uses `DESTDIR` install. Preserve candidate app/output and logs. |

The two Story005 paths above are classified as safe-after-Cam-approval; this
inventory itself does not authorize their deletion. Other candidates need the
stated evidence/reproducibility checks. In particular, do not delete the active master candidate or baseline,
current helper proof, Story004 unique acceptance outputs, or Story005 source and
pixel references to reclaim space during the running candidate test.

## Process observation and limits

At scan time, process inspection found an active candidate `make` check and
`xctest`, a monitor script under `work/story005-scout`, plus ordinary VLC and
its timeline helper. This is sufficient to protect candidate outputs; it is
not a complete filesystem-wide process audit. The scan was limited to project
`work/` paths and known evidence references, and did not enumerate home storage,
inspect NAS media, stop processes, or hash large trees.


## Resume capacity and staging freshness — 22:32 local

Cam reported1.1GB free. The first fresh `df`/`statvfs` measurement was below the
reserve; later ordinary filesystem capacity rose to2084753408bytes and guarded
work resumed. Apple's [volume-capacity guidance](https://developer.apple.com/documentation/foundation/checking-volume-storage-capacity)
and [Disk Utility description](https://support.apple.com/en-ph/guide/disk-utility/dskutl1005/mac)
distinguish capacity/available/purgeable reporting. This does not establish that
purgeable space caused the earlier discrepancy; storage also changed over time.
The build guard retains filesystem available bytes and its1GiB reserve.

The official candidate app subsequently built, packaged and signed successfully.
Thus the earlier `macos-install` row's cancelled-build state is historical; any
future cleanup must use the refreshed package manifest/current consumer check,
not assume the staging contents are still the cancelled attempt. No deletion is
authorized. The latest observed free capacity is about760MiB, so runtime/build
work is held again. Final small source/docs receipts do not establish headroom
for independent reproduction or native acceptance.
