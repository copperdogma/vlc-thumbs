# Remaining build gates and measured storage plan

Measured 2026-10-06T04:32:15.007648+00:00: `shutil.disk_usage(root).free` is 792686592bytes (0.738GiB). The existing monitor measures guaranteed available blocks through statvfs, asserts >1GiB before subprocess launch, checks every2s, and kills its owned groups on a breach. Finder purgeable space is not counted. No cleanup or near-floor runtime is authorized by this plan.

## Protected and regenerable measured footprints

Allocated `du -sk` values from the current APFS volume:

| Item | Allocated KiB | Meaning |
| --- | ---: | --- |
| baseline output |2331460|protected pristine baseline |
| candidate output |2649100|protected coherent build/app/tests |
| candidate source |253556|frozen source, generated configure included |
| candidate contrib prefix |1034892|selected installed dependencies, protected |
| candidate contrib build area |510068|normal FFmpeg source/objects/caches, protected for reproduction |
| candidate modules |604796|objects/plugins/tests/resources, protected |
| candidate core/lib/test |60064|generated code/test outputs, protected |
| candidate `macos-install` |203676|~199MiB generated stage; regenerable, no active build; potential cleanup requires distinct approval |
| candidate `VLC.app` |203896|~199MiB original signed feature app, protected |
| baseline generated tools |742120|~725MiB, necessary observed cost if independently rebuilding tools |

The previously proposed duplicate candidate prebuilt archive is now absent in the current filesystem; it provides **zero further reclaim**. The retained baseline archive remains protected. This lane did not delete it. Old proposals must not be added to current headroom. Regenerated macos-install alone cannot safely fund a new build from the current free-space level. APFS clones, snapshots and shared volume use make summing `du` an estimate, not guaranteed reclaim; the start guard must use actual available blocks.

## Concrete start thresholds

- Final registered native test round: wait for **1.5GiB verified available**. Reuses existing bundles; changed distribution-only bin list should not force production relink. Logs/bundles are small, while cache-contract sparse128MiB fixtures and temporary framework files warrant margin. Run once with `python3 work/story005-scout/baseline-build-monitor.py --candidate --ci-macos-tests`. Context7, cache/service5 and actual-slider6 already pass focused normal runs; this single integrated round follows the repaired initial full-suite failure.
- Conventional helper-disabled minimal distcheck: require **3.5GiB verified available**, approximately 2.76GiB additional free space now. This is a conservative measured-footprint planning envelope, not an executed peak. Existing Autotools recipe creates a distribution source, compressed archive, fresh `_build/sub`, `_inst`, temporary DESTDIR install, then another nested distribution. Bound each source/archive by current source253556KiB; bound no-contrib build objects by measured candidate non-staging/non-app outputs (~0.66GiB); allow one ~0.20GiB install and nested distribution. Expected upper planning peak ~1.7GiB plus1GiB reserve and ~0.5GiB uncertainty. Reuse the selected contrib prefix read-only, explicitly disable timeline-preview through AM_DISTCHECK flags, and provide its absolute `--with-contrib` path through DISTCHECK_CONFIGURE_FLAGS. This gate proves distribution/VPATH/install/uninstall branches, **not feature-enabled or all-source dependency reproduction**. No distcheck launched.
- Independent clean feature app using the same declared recipe (patched FFmpeg source, exact official prebuilt remaining inputs): require **5GiB verified available**, approximately 4.26GiB additional now. Observed output2.526GiB + source0.242GiB + independent tools0.708GiB + one prebuilt archive~0.201GiB gives ~3.68GiB, plus1GiB reserve, rounded up. New build tree must have no reused mutable objects; capture bootstrap/configure/contrib/helper/native/app/sign hashes and repeat necessary feature checks only after success. This remains unexecuted.
- Full public `build.sh -c` source build of **every** remaining contrib: require a provisional **8GiB available** (7.26GiB additional now) before an instrumented feasibility run. Only the selected FFmpeg/GSM/LAME/OpenJPEG source rebuild has been measured here; all-source remaining dependency peak is unknown. The extra ~3GiB is contingency, not a proven upper bound; preserve1GiB monitor and stop if growth invalidates it. Do not label same-prefix/prebuilt-assisted reproduction as this stronger gate.

## Current completed package and relocation boundary

Official existing-output app receipt042325Z passes152.4s, minimumfree1258991616bytes; `feature-original-app-manifest.json` records997 files/symlinks and preserved original Info.plist. The signed packaged helper executes two actual MP4/MKV frames from `/private/tmp` with system PATH only (`feature-packaged-helper-smoke.json`); helper TEXT sections match the frozen build helper, and selected dynamic linkage contains no build paths. Its first smoke attempt failed a harness-only image.type assumption; corrected version/payload assertions pass, both attempts retained.

A later relocation proof can move the **same** owned bundle to another ignored work path and back, without a clone, verify all original file/symlink hashes, then execute bounded helper checks and validate signatures. Native candidate identity isolation (org.videolan.vlc.story005.nativecandidate) must preserve original plist and prove code/resource equality outside the intended plist/signature metadata changes. Native owner exclusively operates UI. No relocation/metadata/native runtime currently runs below reserve. Full clean reproduction, Intel/olderOS and physical pointer/playback/accessibility gates remain explicit.
