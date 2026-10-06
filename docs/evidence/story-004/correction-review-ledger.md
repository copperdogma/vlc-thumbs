# Story 004 correction review ledger — 2026-10-05

This ledger records the corrected source and the proof currently attached to it. It is an evidence update, not a story status or closure decision.

## Cache retention correction

Current `src/macosx/VLCThumbnailCache.m` SHA-256 is `29399e7d40a2cfcc8b604640f0971f4107d7c6ccb7562d202436725aa9051d4a`. The demand-priority harness at `tests/story-004/cache_contract.m` ran 3,410 checks against both the retained mtime-only baseline and corrected source. The baseline failed 9 checks; two oversized-fault assertions are consequential setup failures because the baseline had already removed the fresh-demand manifest/payload. The corrected source passed 3,410/3,410. Full machine-readable results: [local contracts correction](local-contracts-correction-001728.json); raw result and logs remain in ignored `work/validation/story004/cache-demand-priority-results.json`, `cache-demand-priority-baseline.log`, and `cache-demand-priority-corrected.log`.

The rule is bounded and identity-scoped: demand-use membership is limited to512 sample records for the current identity. Meaningful RAM/disk touch and explicit store with `allowEviction:YES` promote; passive enumeration does not. Identity change/removal clears the set. Pruning selects background entries first, then demand/current-manifest entries when needed; the256MiB hard cap always wins. The comparison primary source was [RocksDB block cache priority pools](https://github.com/facebook/rocksdb/wiki/Block-Cache), adapted as a principle only: no RocksDB code or dependency was added.

The mapping count guard applies before ordinal selection for all containers. The persistent namespace is `v4:keyframe-countguard2:transform1`; prior potentially wrong-track cached images therefore cannot be reused. The focused mismatch regression fails on the installed222506 helper and passes for both protocols with the correction. Corrected and packaged records are retained in `track-count-corrected.json`, `track-count-corrected-v2.json`, and `track-count-packaged-native.json` under ignored `work/validation/story004/`.

## Candidate-specific evidence

Candidate `001728` was built and signed with pinned VLC source `6de05adcbaf2e8b85fe86aad4169393098628119`; its build manifest is [app-build-correction-001728](app-build-correction-001728.json). The service contract passed40/40 checks with zero failures, recorded in [local-contracts-correction-001728](local-contracts-correction-001728.json). A fresh-process mounted-SMB actual-pointer cohort yielded10/10 usable images; warmth was uncontrolled and the measurement is not compositor latency ([native NAS correction](native-nas-correction-001728.json)).

Final001728 comparison and delivery are now qualified: [20/arm controls](ordinary-controls-correction-001728.json), [three matched playback pairs](playback-correction-001728.json) and [installed normal-profile image](local-preview-update-001728.json). The earlier235648 controls/playback remain intermediate. Final scope and limitations are in the current acceptance ledger.

Review records in ignored `work/validation/story004/`: `codex-review-corrections.log` accepted the incompatible old Story002 runner finding as an explicit retirement; `codex-review-retired-runners.log` and `codex-review-demand-priority.log` reported no findings. The earlier mapping-cache defect is corrected by policy namespace invalidation. No public distribution, exhaustive format, forced NAS reconnect, or bookmark identity claim is added here.
