# Story 004 validation

Local contract runners use generated media/faults and isolated ignored caches.
They do not establish native macOS interaction, NAS performance or playback safety.

```
python3 tests/story-004/helper_worker_contract.py --output work/validation/story004/helper-worker-contract-final.json
bash tests/story-004/test-scheduler.sh
bash tests/story-004/test-cache.sh
bash tests/story-004/test-service.sh
python3 tests/story-004/track_count_contract.py
```

The helper runner retains v2/v3 pixel/actual-time correspondence on seven fixtures,
idle reuse, guarded EOF teardown, input mutation, malformed requests, full/sampled hash recipes and
independent blocked-read/open/stat watchdogs. `--metadata-only` isolates the last
metadata checks. The service runner uses a generated fault worker and real Cocoa
run loop to prove coalescing, active-work preservation, cache bypass, actual-time
reuse, full restart reuse, context cancellation and current-hover invalidation.
Cache/scheduler runners check bounded ownership, corruption, quotas, progressive
coverage, retry/defer behavior and deterministic priorities.

`service_smoke.m` additionally exercises the real helper and generated standard.mp4.
Build it with the same Cocoa compile inputs as test-service.sh, substituting the
smoke source. Its output is work/validation/story004/service-smoke.json.

`helper_comparison.py` implements the predeclared AB then BA diagnostic from
[the comparison plan](../../docs/research/story-004-comparison-plan.md).
Use a fresh output directory under work/validation/story004 and explicit media and
targets. It records helper hashes, startup/request times, IO and actual image
hashes. Missing media creates a setup-invalid record. This comparison includes
uncontrolled source/OS cache warmth and is not native latency or playback proof.

Native control/presentation and playback acquisition require an unlocked desktop.
NAS qualification requires the Movies mount. Keep invalid attempts, do not treat
missing samples as successful or weakening the acceptance threshold. The candidate
remains isolated in work/build/vlc-arm64/VLC.app; do not replace the user's daily
app before native qualification. ADR-003 accepts metadata plus sampled verification, enabled in the current
candidate; unusual changes outside sampled ranges can evade that policy.

The real-service smoke also accepts explicit repo, media, output and comma-separated
seconds arguments. Use an output under work/validation/story004. Its strict
one-worker assertion may fail on a genuine timeout/retry; retain that failure
and callback evidence rather than weakening it or treating a recovered image
as a latency pass. NAS source warmth remains uncontrolled.

Current-session provisional checks additionally prove RAM-only lookup, one final cache owner, latest hover while older metadata blocks, context-wide replacement clearing, cancellation, fresh-open qualification, a shared15s deadline across pointer moves, known-failure suppression and sustained-cache-hover preparation fairness. `preparation_smoke.m` uses the same compile inputs and real helper to complete the finite7-point90s plan without hover and reload that coverage without decoding.

Native drivers: `native_nas_trial.py` (explicit app/media/duration/output/variant) retains first useful and final verified assignments separately; `native_surface_trial.py` takes app/output/mode/build-manifest and uses the compiled owned `native-window.m` helper to raise a selected detached AX window before pointer input. Compile that helper with Cocoa and ApplicationServices to work/validation/story004/native-window. `preview_cli_off_trial.py` verifies actual pointer input with previews disabled, no feature events/helper children and intact Position/paused playback. Main MP4/MKV use the existing native_hover_trial.py with the story004 followup probe. Each acquisition requires a fresh output and immutable inputs during collection.

Fault interposition runs against the unstripped build helper, as the original fault contract specifies. A trial using the stripped/signed app helper reached the outer blocked-read timeout; its expected injected startup obstruction was not qualified. Do not weaken delivered signing or infer a fault pass from that invalid injection acquisition. Normal packaged-helper behavior is independently exercised by native trials.

The count-guard regression generates red/blue MP4 and single-video MP4/Matroska fixtures. It tests v2/v3 native count mismatch rejection plus matching-count blue samples. Optional `--native-vlc work/build/vlc-arm64/VLC.app/Contents/MacOS/VLC` establishes that VLC ignores the malformed first track and decodes the second; this is demux/decoder proof, not physical-pointer proof. The service suite additionally seeds the old mapping-policy cache and requires new-policy decoding. Cache regressions verify RAM retention age, passive enumeration, exact-quota background pressure/reopen and no-follow timestamp ownership. Demand-priority coverage bounds current-identity membership to512 sample records, verifies promotion by meaningful RAM/disk touch and explicit `allowEviction:YES` store, confirms identity change/removal clears it, checks background pruning before demand/current-manifest entries, and verifies the hard256MiB cap can still evict them. The frozen mtime-only baseline fails9/3410 checks (including two oversized-fault setup consequences); corrected source SHA-256 `29399e7d40a2cfcc8b604640f0971f4107d7c6ccb7562d202436725aa9051d4a` passes3410/3410. Full result: `work/validation/story004/cache-demand-priority-results.json`.

The incompatible Story 002 v2 service/cache-fault commands are retired with exit2 and point here. Historical Story 002 fixtures/contracts/evidence are retained for provenance, not offered as current persistent-service runners. Current full-quota/read-only/corrupt-cache contracts do not claim a new physical mounted-disk ENOSPC trial.
