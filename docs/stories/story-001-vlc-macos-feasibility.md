---
id: "001"
status: Done
priority: High
ideal_refs:
  - ideal:req:previews
  - ideal:req:annotations
  - ideal:req:persistence
  - ideal:req:playback-quality
  - ideal:req:evidence
spec_refs:
  - spec:1
  - spec:2
  - spec:3
  - spec:4
adr_refs: [adr-001-media-metadata-storage]
decision_refs: [docs/decisions/adr-001-media-metadata-storage/adr.md]
depends_on: []
eval_refs:
  - root-timeline-experience
---
# Story 001 — VLC macOS timeline feasibility

## Goal

Find the smallest maintainable path to both requested interactions on VLC's
actual macOS timeline. Establish pinned source/build/UI evidence before choosing
an integration architecture. This is a feasibility proposal, not permission to
modify the installed VLC or a claim that a native fork is necessary.

## Acceptance Criteria

- [x] Verify current primary VLC extension/module documentation and source licensing; distinguish observations from intake suggestions.
- [x] Pin source revision/version and macOS/architecture/toolchain. Explain choice versus the intake's unverified 3.0.24 suggestion.
- [x] Map normal and fullscreen seek controls, time/position geometry, hover/right-click events, marker drawing and playback/decoder boundaries to source paths/symbols.
- [x] Compare existing upstream capability, Lua extension, native module and UI patch against BOTH interactions, including separate-window mismatch.
- [x] Establish a reproducible isolated build/launch path or record the exact failed command, blocker and next route. Do not replace installed VLC.
- [x] Define legal known-video fixture acquisition/generation, root test capture method and proposed measurable preview/seek/latency/playback thresholds.
- [x] Record a route recommendation, expected maintenance cost, unresolved API/storage questions and next integrated vertical slice. Update spec/state and compile graph.

## Out of Scope

Shipping either feature, distributing VLC, creating a remote, signing/notarizing,
modifying real media/notes, changing installed VLC, choosing annotation schema
without identity analysis, Windows/Linux support, colors/tags, paid AI calls.

## Approach Evaluation

Existing upstream behavior is the first baseline. A Lua extension is attractive
if it can manipulate the required native surface; a native module or UI patch
may provide control at greater build/maintenance cost. A companion window changes
the requested experience and needs a deliberate product decision. The source/build/probe investigation now recommends a small stable macOS GUI
patch and an independent contrib-libav helper; final implementation selections
belong to the feature stories' technical ADR gates. See the implementation
synthesis for the route matrix, concrete evidence and remaining qualification.

AI can assist research and implementation; a single model response cannot itself
provide native event handling or durable player state. The product is a
behavioral native UI feature, not a prompt-comparison task. No model capability
failure is asserted to justify code.

## Eval Ladder Context

Parent outcome: `root-timeline-experience`, deferred and never attempted.
This story establishes substrate and an honest test path; it does not pass the
root. No child deletion eval or measured parent failure exists. A fixture/build
probe here may become a capability check once its command and expected outcome
are real. Do not mark compile success as end-to-end proof.

## System Context / Integration Impact

This repository tracks methodology, source/build/probe evidence and feature
plans. Pristine pinned VLC is separate from a mutable ignored build workspace.
The arm64 app renders generated MPEG-4 and H.264; native main-window pause/seek
and fullscreen/detached display have been observed. The selected-window capture did not qualify floating fullscreen panel
interaction at this feasibility stage. Later Story 002/004 work implemented and
qualified thumbnail interaction on four native surfaces within the scopes in
their current ledgers. Preview extraction must not seek the playing input;
durable annotations must survive cache/history churn and app restart. The
integrated root remains deferred pending bookmark implementation.

## Decision Inventory / Open Questions

- Version/build: VLC 3.0.24 pinned and current-host arm64 build works; exact
  patches/configuration/toolchain and failed attempts are recorded.
- Integration: source-backed recommendation is a small stable native GUI patch
  with shared context/geometry/presentation and separate fullscreen adapter.
- Preview: contrib FFmpeg helper passed MP4/MKV/MPEG-4 timestamp probes;
  AVFoundation-only failed the tested MKV. IPC/performance/format proof remains.
- Storage: ADR-001 accepts lifetime separation. SQLite link/basic transactions
  verified; identity/schema choice remains a Story 003 ADR. Fresh full hashing
  is the conservative proposal with explicitly unmeasured large-file latency.
- Delivery: isolated development app first, never installed VLC. Public
  packaging, broader compatibility and upstream contribution remain future work.

## Tasks

- [x] Read upstream Lua/build/source guidance and pin relevant source under ignored work with provenance — source-manifest.json.
- [x] Record initial macOS seek UI/events and extension boundary inventory — research note; runtime/fullscreen behavior remains unqualified.
- [x] Record route matrix with exact supporting source pointers and unknowns — research note; native-module host API not qualified.
- [x] Verify local build prerequisites and establish isolated build/launch instructions — attempt 009 and build runbook.
- [x] Plan fixture and root scenario with measurable thresholds and UI evidence.
- [x] Write feasibility synthesis and measured probes/build attempts; record accepted ADR-001 and explicit future implementation ADR gates.
- [x] Refine the implementation plan/story boundary with the evidence; update spec/state and graph.
- [x] Run make validate and scope-appropriate build checks; no product pass from setup checks.

## Architectural Fit

Owning area: VLC macOS UI integration and timeline services. State spec:1 is
partial; spec:2 through spec:4 have no feature implementation. Pinned source,
working arm64 build and bounded decoder/store probes support concrete plans.
No annotation schema or feature runtime exists. ADR-001 now governs durable labels versus disposable thumbnail/history retention;
format/schema and media identity remain open. Source-project
ADRs, fixtures and game rules do not constrain this project.

## Files to Modify

- docs/research/scout.md — index primary research and feasibility findings.
- docs/research/ — source/UI/route synthesis with citations and applicability.
- docs/evidence/ — exact isolated build/probe attempts and results.
- docs/spec.md and docs/methodology/state.yaml — qualify constraints and substrate.
- docs/evals/root-timeline-experience.md — measurable thresholds/capture plan.
- scripts/ — only verified build/probe helpers required by the selected route.

## Redundancy / Removal Targets

No product implementation exists to remove. Replace unverified candidate text
with qualified facts while preserving original intake and failed experiments.

## Project Tenets / UI Verification

- [x] Preserve input media and real user state.
- [x] Pin provenance; keep hypotheses separate from observed facts.
- [x] Inspect actual native UI evidence and normal/fullscreen coverage, explicitly recording unqualified panel interaction.
- [x] Preserve baseline playback and user state during experiments; require feature-level playback/keyboard/accessibility proof in 002/003.
- [x] Keep changes scoped and conclusions proportional to measured evidence.

## Workflow Gates

- [x] Substrate inspected and written plan exists.
- [x] Applicable plan approval/authorization recorded before implementation.
- [x] Build complete: feasibility research/build/probes and planning finished, scope-appropriate checks run, summary shared.
- [x] Validation complete or explicitly skipped by user.
- [x] Story marked done via /mark-story-done.

## Plan

Cam authorized starting Story 001 on 2026-10-03, continuing through build
failures, then deep investigation and two-story planning on 2026-10-04. Feature
implementation has not been started by this feasibility work.

1. Pinned source and working build: completed with exact attempts/repairs and
   isolated development namespace; pristine source/installed VLC preserved.
2. Source/control and decoder/store investigation: completed. Native/detached/
   fullscreen baseline observations and floating-panel capture limitation are
   explicit; helper and SQLite probes establish availability, not product proof.
3. Fixture/threshold plan and synthesis: completed in
   `docs/research/timeline-implementation-plan.md` and the expanded root contract.
4. Two concrete implementation stories: 002 previews and 003 short labels,
   each including complete native UI, failures and behavioral evidence. These
   fulfill the original next-integrated-slice criterion together while preserving
   distinct decoder/cache and durable-identity validation boundaries.
5. Documentation/provenance/generated records validated; feasibility closed.
   Architecture selections and full native feature qualification remain inside
   002/003, consistent with this story's original shipping exclusions.

## Work Log

20261003 — Setup: preserved the overview and drafted this feasibility boundary.
Source/build/UI substrate is unverified; status Draft. No product work executed.

20261003 — Started: setup committed locally as fdf25f2 (push awaits remote).
Pinned pristine VLC 3.0.24 at 6de05ad; inspected native sliders, fullscreen panel,
bookmark options, Lua dialog boundaries, build script and host developer tools.
Research: docs/research/story-001-vlc-macos-timeline.md. Evidence:
docs/evidence/story-001/preflight.md and source-manifest.json. A bounded Luna
packet initially inspected master; main agent kept those hover/tick precedents
separate from stable capabilities. Status In Progress for authorized feasibility
work. No build or app launch and no implementation patch. Next: isolated
unmodified arm64 build with dependency provenance.

20261003 — Resume-storage follow-up: traced VLCInputManager's decoded-URI/seconds
NSUserDefaults records, 30-entry retention and VLCDocumentController history
clearing. Recorded the recommendation to reuse lifecycle/identity access while
separating durable short labels from evictable thumbnails/history. No user VLC
store inspected or changed; no persistence schema accepted or implemented.

20261003 — ADR-001: Cam accepted the storage direction and requested a decision
record. Linked the accepted lifetime split; updated spec/state, root retention
cases and local storage guidance. No schema, runtime store or decoder selected.

20261003 — Disk preflight requested before building: internal free space measured
11.26 GiB; existing shallow source checkout 163 MiB including 25 MiB Git data.
Default host prebuilt-contrib URL returned 404 to a HEAD probe. Peak build size
unqualified; full build deferred pending workspace/capacity and budget. Evidence:
docs/evidence/story-001/disk-preflight.md and .json. No build, dependency download,
cleanup or filesystem relocation performed. Source/document research can continue.

20261003 — Build attempt 001 started at Cam's explicit request after disk check.
Created disposable work/build/vlc-source from pristine source using a local
shared clone. Invoked upstream build.sh with -a aarch64 -j 4 and isolated -C
build output; VLC_PATH=/usr/local/bin. Entire source/tools/contrib/build copy is
under work/build; pristine pinned source remains separate. Monitoring stops
below 1 GiB free and removes only this attempt's disposable workspace on a
low-disk stop. Exact command, log, disk samples and outcome are recorded in
docs/evidence/story-001/build-attempt-001/. No product feature code modified.

20261003 — Build attempt 001 finished: upstream exit 2 after 312.8 seconds.
Tools reached contrib setup; default aarch64-apple-darwin27 prebuilt archive
returned HTTP 404. No VLC compile/app launch. Disposable workspace 1.15 GiB;
lowest sampled free space 10.08 GiB; final free space 10.36 GiB. Disk threshold
not reached; artifacts retained for reuse. No evidence of insufficient space in
this partial attempt; full build peak remains unknown. Evidence:
docs/evidence/story-001/build-attempt-001/README.md, attempt.json and build.log.
Next: compare compatible pinned archive with upstream -c source-built contribs.
Story remains In Progress; no product patch or qualified build.

20261003 — Cam explicitly authorized continuing through failures until VLC builds.
Started attempt 002 with upstream -c to compile contrib dependencies from source,
reusing attempt 001 tools in the disposable workspace. Same disk monitor and
1 GiB stop/cleanup reserve. Evidence: build-attempt-002 command/metadata/log.
Build-only compatibility repairs are now authorized; no timeline feature patch
or installed VLC modification. Bounded lower-cost agent checks official archive
fallbacks in parallel; main owns compatibility and integration decisions.

20261003 — Attempt 002 stopped intentionally during source fetch: dependency scan
picked up system /usr/local libavcodec, verified Mach-O x86_64, while target is
arm64. No VLC compile. Attempt 003 sets PKG_CONFIG_LIBDIR to the isolated contrib
prefix and clears inherited PKG_CONFIG_PATH, excluding Intel pkg-config defaults.
Existing source downloads/tools retained; newly required arm64 dependencies now
fetching. Exact environment and stop reason captured in attempt JSON files.
Official archive fallback search found only older Intel targets, no qualified
arm64 package; source-built contribs remain the current route.

20261003 — Attempt 003 exited 2 in contrib compilation: Ninja 1.13 jobserver
client disturbed Apple GNU Make 3.81 job pipes; aribb24 autoreconf lacked pkg.m4
and reported undefined AC_DEFINE within unexpanded PKG_CHECK_MODULES. Attempt
004 wraps isolated Ninja with explicit -j4 (disables its jobserver client) and
sets ACLOCAL_PATH=/usr/local/share/aclocal for existing build macro definitions.
Intel runtime/library pkg-config paths remain excluded. Repair rationale and
wrapper recorded in build-attempt-004/repairs.md; compiled libraries reused.

20261003 — Attempt 004 completed contrib libraries and reached VLC configure,
then exited 1 because Sparkle was absent. Pinned sparkle rule excludes it on
SDK >13.1 when deployment minimum remains 10.7 (missing libarclite). For isolated
development baseline, attempt 005 uses supported VLC_CONFIGURE_ARGS=--disable-sparkle;
no auto-update facility in this build. Playback/UI and dependency compile remain
required. All prior compiled dependencies reused; no product feature patch.

20261004 — Attempt 005 linked VLC plugins but dav1d failed: arm64 objects
referenced x86 SIMD symbols. Meson logs confirmed x86_64 host from Intel
/usr/local Python. Isolated tools/bin/python3 now points to native /usr/bin/python3
3.9.6 (Meson requires >=3.7). Rebuilt six affected Meson libraries by invalidating
stamps and installed .a/.pc files. Attempt 006 confirmed aarch64 detection and
rebuilt dav1d/fribidi/librist; stopped when freetype was unavailable. Corrected
the invalidation target from directory name freetype to actual stamp .freetype2;
attempt 007 continues rebuilding freetype, harfbuzz and bluray before VLC link.
Architecture-repair manifest lives under build-attempt-006.

20261004 — Attempt 007 passed AV1 linking, then libarchive plugin failed on
-lb2. CMake had discovered Intel optional b2/lz4/zstd libraries despite pkg-config
isolation. Added local CMake ignore-prefix /usr/local, invalidated/rebuilt four
CMake packages with detected host prefix entries (archive, chromaprint, vncclient,
x265); patch and manifest recorded under attempt 008. Rebuilt libarchive.pc now
contains only archive/z/bz2, but VLC's old generated Makefile retained -lb2.
Attempt 009 removes only generated top-level Makefile to force configuration
refresh; compiled objects remain available. No new archive-library failure.

20261004 — Attempt 009 succeeded (exit 0), VLC.app assembled and upstream code
signature verification passed. App binary is arm64, VLC 3.0.24-0-g6de05ad.
Separate generated bundle identifier org.videolan.vlc-thumbs.development isolates
NSUserDefaults/core directories. Re-signed app, refreshed/signed plugin cache
and strict deep verification passed. Generated silent MPEG-4 decoded to EOF
(exit 0) and native GUI rendered frame timestamp 1.917. Pause changed button to
Play; click seek changed playback time to 00:02 and rendered frame 2.333. Initial
AX timeout traced to first-run online metadata modal; only development defaults
seeded and metadata networking disabled. Existing installed VLC not run/modified.
Whole workspace ~5.7 GiB, app 161 MiB; no low-disk stop. Exact logs, verification,
dependency download hashes, fixture identity and screenshots under attempt 009.
Build reproduction/limitations recorded in docs/runbooks/build-vlc-macos.md.
Full clean rebuild not repeated. Auto-updater disabled; audio/fullscreen/other
formats and feature behavior unqualified. Story remains In Progress: route
synthesis, fuller controls observation and root fixture/threshold planning remain.
Learning review considered: platform-specific build repairs belong in runbook,
no separate durable workflow-learning candidate or live skill change warranted.

20261004 — Final baseline checks: strict deep codesign verification passed;
all 339 bundled Mach-O objects are arm64. otool dependency scan found no
/usr/local, /opt/homebrew or work/build absolute dependency leakage. Workflow
validation and diff whitespace checks passed; pristine source status clean.
Development GUI left paused on synthetic media for review. No commit/push.

20261004 — Deep-dive/planning completion: source/control inventory and native
fullscreen/detached observations recorded, with floating-panel capture limits.
AVFoundation MP4 extraction worked but same-stream MKV failed; existing-contrib
arm64 libav helper passed all 15 tiny fixture requests with paired MP4/MKV RGB
hashes. System SQLite arm64 link/basic transactions/revision guard verified.
Probes are diagnostic only. Synthesis and full fixture/threshold contract now
support complete Story 002 thumbnails and Story 003 short labels, as requested.
No feature code or installed VLC/user store change.

20261004 — /validate and /mark-story-done: all seven original ACs, eight tasks
and five project tenets met within feasibility scope. Bounded review identified
cache-freshness and latency-population ambiguities; corrected explicitly.
Evidence: docs/evidence/story-001/planning-validation.md. Workflow/links/JSON/
whitespace checks pass; app signature and pristine source rechecked; media hashes
unchanged; Ideal unchanged. Story 001 Done, 002/003 Pending, root deferred.
No feature proof or public packaging claim. No commit/push performed; next
landing request is /finish-and-push, separately from starting Story 002.
