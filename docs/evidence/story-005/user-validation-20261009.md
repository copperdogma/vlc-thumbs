# Owner test delivery validation — 2026-10-09

## Findings first

No confirmed material product defect found in current source10/final13. Two P2 documentation/provenance findings were corrected: current planning/spec/story prose still reported historical blockers, and older public patch snapshots presented their own revision as canonical without routing to the current reviewer copy. Historical evidence and frozen patch/manifests are preserved; current routing is explicit in `patches/vlc-master/README.md`.

## Scope, evidence and checks

Commands: `git status --short`, `git diff --stat`, `git diff`, `git ls-files --others --exclude-standard`; retained complete diff and file-read inventories in `work/story005-user-validation-20261009/`. All 10 tracked changed files and 503 untracked docs were opened/read/hashed; all 73 untracked code/test paths were opened/read/hashed (66 unique contents). New routing prose was separately inspected. Logs/receipts were mechanically read and parsed with targeted semantic review of current claims; inventory completeness does not imply exhaustive runtime coverage.

Two SOL6.1 medium packets covered documentation/contracts and code/tests, with root integration judgment. ADR001–004, Ideal, spec and Story005 were considered; ADR004 selected retained FFmpeg9 helper is aligned with current source. Current72 source hashes/modes match source10 freeze. Existing full normal checks, helper77, complete conventional distcheck, native/package/relocation, ordinary main reader inheritance and fresh three-pair playback results remain applicable because product code is unchanged. No full product suite or reader setup repeated for documentation or app metadata changes.

`codex review --uncommitted` completed exit0 in120.45s, no actionable defects confirmed. This is advisory, not a replacement for candidate evidence. Accepted/rejected finding ledger is retained in the private validation directory. Fresh `make methodology-compile validate` and `git diff --check` pass; selected changed/current documentation links resolve. Current final reviewer checker records29 artifacts/13 patches/two PNGs exact. The separate owner app receives signature, executable correspondence and helper relocation checks in its delivery receipt.

## Story Validation

| Requirement | Status | Grade | Evidence and boundary |
|---|---|---|---|
| Phase1 contribution map | Met | B | Dated official guidance/scout, target/process/style/build/licensing record; missing maintainer/AI-policy facts stay unknown. |
| Phase1 architecture/product fit | Met | B | ADR004 and selected port plan; native reuse alternatives and helper/time/track/NAS boundaries explicit. |
| Phase1 reviewable plan | Met | B | Exact patch map/dependencies; no assumed maintainer agreement. |
| Phase2 native fit | Met at selected scope | B | Live helper/service/context/hover ownership reviewed; no confirmed material defect; conventions/settings/accessibility preserved. |
| Phase2 independent reproduction | Met locally; broader platform coverage Partial | B | Full normal tests/helper77/conventional distcheck/package proof; Intel/older macOS/external CI unavailable. |
| Phase2 strong verification | Met for accepted bounded scope; exhaustive coverage Partial | B | Four-surface and current019 proof/inherited unchanged paths plus matched playback; broader reader/precision-seek coverage unmeasured and shutdown cause explicitly deferred. |
| Phase2 maintainer-ready package | Met for local reviewer copy | B | Current final29 checker and exact13 patch series; historical public snapshots separately labelled. |
| Phase3 submission/follow-through | Unmet; outside this request | — | No upstream submission, MR or acceptance. |

Overall grade **B** for the authorized Phases1/2 owner-test slice. Quality: High; testing coverage: Partial with substantial scoped native/build evidence; documentation: Good after corrections. No blanket A-grade/all-platform/crash-free claim. Build complete and fresh validation complete at disclosed scope; whole-story marked-done gate remains pending Phase3, not an implementation failure for this delivery.

Remaining Story Gaps: Intel/older macOS/external CI, preview-visible/fullscreen VoiceOver, precision-seek coverage and uninterrupted public recipe remain coverage limits; historical shutdown cause remains owner-deferred unresolved. Revisit only with an appropriate platform, concrete defect or explicit scope expansion; no blind observer/reader retry quota. Maintainer ownership/boundary acceptance remains external. Phase3 requires separate user authorization, actual submission and review disposition. Bookmarks are separate.

Closure recommendation: **Keep open** for whole Story005; retain accepted bounded Phases1/2 completion. No other checkbox edits are proposed. Current application delivery is separately authorized by the user and does not authorize submission/commit/push.

Impact: owner gets the current VLC4 timeline-preview candidate rather than an older installed prototype. Pointer time remains the seek target; thumbnail caption is actual keyframe time. Unsupported media fails back to ordinary time hover. Measured preparation overhead remains about1.5–2.3 CPU percentage points and about100MiB sampled maximum RSS above baseline.

Learning-review explicitly considered: **RESULT: no-candidate**. The stale status problem is already covered by validate's positive-claim/evidence and documentation consistency requirements; a new live workflow rule is not warranted. No memory/workflow mutation.

## Next steps

1. Keep Story005 open for Phase3; use the separately installed owner test app for ordinary playback, hover, fullscreen/return and preference testing.
2. Record any concrete failure with the media/container, action and expected/actual behavior; revalidate affected code if a fix is needed.
3. Submit only after a separate owner instruction. No further approval is needed to deliver the requested test app.

## Delivered app

Installed `/Users/cam/Applications/VLC Timeline Test 2026-10-09.app` (display name **VLC Timeline Preview — 2026-10-09**, version4.0.0-dev), separate identity `org.videolan.vlc.story005.ownertest20261009`. [Delivery receipt](../../../work/story005-user-validation-20261009/app-execution001/receipt.json) PASS in302.520s:398 code sections/UUIDs equal qualified019, nonmain loadables exact, deep-strict signature PASS, MP4 and positive-start MKV helper pixels/header correspondence PASS. Standard VLC/two older owner apps/source72/019/settings preserved; no GUI trial launched. New delivery reuses qualified product code; native behavior is inherited rather than retested here.

## Owner acceptance and project landing

Cam reports the installed app looks good and explicitly invokes finish-and-push. This records owner acceptance of the observed test experience, not exhaustive coverage. The [current13-patch package](../../../patches/vlc-master/contribution-series-source10/CONTRIBUTION.md) is copied byte-for-byte from the checked29-artifact reviewer copy, preserving its manifest/source pins. Project-repository landing is authorized; VLC submission remains Phase3 and is not performed. Whole Story005 remains InProgress.

Landing whitespace inspection excludes byte-preserved raw `.patch`/`.diff` and `.log` artifacts, whose diff-context and terminal-output whitespace is data. One prose trailing space was removed; the remaining prose/tooling check passes. Outgoing secret scan found no credential material; synthetic demonstration images were visually checked. Local developer paths remain in historical build records; no private media/apps/binaries are included.
