# Initial scout — VLC upstream contribution (Story 002b / 005)

**Current status, 2026-10-07T06:44Z:** Phase1 is complete. Phase2 remains open:
normal009 full build/check and fresh016 offline package/relocation pass, but loaded
normal Quit/current native/reader are unqualified; complete010 distcheck passes through final cleanup. The desktop is currently locked; manual unlock was requested. Public11
remains unchanged; ignored combined source72 includes separate baseline
prerequisites. Current execution and exact evidence are in
[the blocker loop](../evidence/story-005/blocker-resolution-loop.md) and
[readiness ledger](../evidence/story-005/current-readiness-ledger.md).
The initial scout and dated findings below are preserved historical context.

**Scouted:** 2026-10-05. **Initial status:** bounded planning scout complete; full Phase 1
contribution/architecture audit was pending in
[Story 005 (002b)](../stories/story-005-open-source-contribution.md).
**Scope:** submission route, branch fit and existing thumbnail infrastructure.
No upstream build, port, implementation changes, maintainer contact or submission.
Cam clarified that this turn should finish the scout and story planning only.

## Sources and provenance

Canonical repository: [VideoLAN GitLab](https://code.videolan.org/videolan/vlc).
Source inspected through its official GitHub mirror at
[`2e358f3098c2f2b7621d1dc568de8b61ad786322`](https://github.com/videolan/vlc/tree/2e358f3098c2f2b7621d1dc568de8b61ad786322),
commit dated 2026-10-05 16:03:36 UTC. This is a research pin, not the selected
submission base. Our current app is VLC 3.0.24 at `6de05ad`, with qualified local
feature build 001728; [its evidence](../evidence/story-004/current-acceptance-ledger.md)
does not establish compatibility with current development source.

Some VideoLAN/GitLab browser pages were inaccessible. The developer-page mirror,
official mail archive, source mirror and read-only GitLab API supplied the findings
below. No comprehensive current issue/review-queue audit was performed.

## Findings and decisions for the story

### 1. Use the official contribution route and establish the target first

**Value:** high. **Effort:** Phase 1, then submission in Phase 3.
The [developer page](https://images.videolan.org/developers/vlc.html) points contributors
to master, source guidance and code conventions. It retains older patch-by-email
instructions. The later official
[merge-request migration announcement](https://mailman.videolan.org/pipermail/vlc-devel/2021-April/143228.html)
specifies a GitLab fork/MR workflow and identifies GitHub as a mirror. The GitLab
project API currently reports `master` as the default branch.

**Recommendation:** plan a GitLab MR, not a GitHub PR. Treat master as the leading
new-feature target; verify current guidance and related work before freezing the
base. A maintenance-branch backport is a separate decision. Do not submit our
3.0.24 patch unchanged merely because that is the version we built locally.
The historical announcement does not establish today's exact CI/bot timings.

### 2. Match the surrounding code and learn from focused accepted changes

**Value:** high. **Effort:** full audit in Phase 1; changes in Phase 2.
The official [code-conventions page](https://wiki.videolan.org/Code_Conventions)
emphasizes consistency within existing files and gives Objective-C documentation
and macOS API-availability guidance; its classical style list is not uniformly
enforced. This supports a target-file style inventory, not a repository-wide
reformat of unrelated code.

Two accepted maintenance examples found through the GitLab API:
[MR !9531](https://code.videolan.org/videolan/vlc/-/merge_requests/9531) explains a
macOS icon backport and its branch-specific tooling;
[MR !10132](https://code.videolan.org/videolan/vlc/-/merge_requests/10132) explains
a specific NSMenu index crash. They illustrate concise problem/rationale and
explicit branch context, not acceptance of our architecture or a complete master
style survey. Audit additional current macOS/core changes in Phase 1.

**Recommendation:** own the readability, tests, documentation and reproducibility
burden; present small coherent changes and a short review guide. Determine exact
CI/test, localization, license and author/sign-off requirements from current target
sources. No explicit AI-assisted contribution policy was found in this bounded
pass; whether another policy exists remains unverified.

### 3. Current development already has native hover and thumbnail services

**Value:** high. **Effort:** prototype/ADR gate before porting.
The inspected [progress slider](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/views/VLCPlaybackProgressSlider.m)
has a time-only hover window; its
[controls](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/windows/controlsbar/VLCControlsBarCommon.m)
use VLCPlayerController. The old VLCFSPanelController is absent from the inspected
master tree. Four-surface proof on 3.0 does not qualify these different controls.

The [preparser API](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/include/vlc_preparser.h)
provides time/position thumbnail requests, fast/precise seek, cancellation,
time/thread limits and external processes. macOS
[VLCMain](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/main/VLCMain.m)
creates a one-thread thumbnailer with a three-second timeout.

**Recommendation:** evaluate extending the existing hover and thumbnail facilities
before retaining the private helper. Exemplar: current slider plus preparser.
Invariant: ordinary seek behavior and correct media/track/sample-time association.
Adaptation: timeline-position images with bounded preparation and caching.
Proof target: a minimal actual native request on known-frame local/NAS fixtures,
including track selection, actual PTS, transforms and stale-request handling.
**Uncertainty:** none of that runtime equivalence was tested in this scout.

### 4. Existing process and cache lifetimes need careful comparison

**Value:** high. **Effort:** measured Phase 1 architecture experiment.
The [external preparser](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/preparser/external.c)
has reusable process pools, but
[ThumbnailerRun](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/preparser/internal.c)
creates/closes an input for each request. Reusing a process alone does not prove
we avoid the repeated open/probe cost that motivated Story 004.

[VLCLibraryImageCache](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/library/VLCLibraryImageCache.m)
uses a representative image at 15%, a 512-by-512 crop, per-media request coalescing,
and path/size/mtime disk identity. Its stale-image cleanup removes other JPEGs
for the same source. Those semantics differ from many positions and selected
tracks with bounded retention and our sampled-freshness contract.

**Recommendation:** reuse suitable primitives, but demonstrate NAS/session and
multiposition behavior before selecting the whole service/cache. Compare a small
upstream extension if necessary. Do not silently discard responsiveness or
freshness fixes to make a smaller-looking contribution.

### 5. The private dependency patch is an additional maintenance boundary

**Value:** high. **Effort:** architecture decision, then dependency work if retained.
Master's inspected [FFmpeg contrib recipe](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/contrib/src/ffmpeg/rules.mak)
selects 9.0. Our helper uses 8.1.2 plus a private Matroska TrackNumber patch, as
recorded in ADR-002 and [license/source notices](../../patches/README.md).

**Recommendation:** prefer avoiding that extra dependency seam through upstream
facilities if they meet the contract. Otherwise determine appropriate VLC/FFmpeg
ownership, version compatibility and separate submission/dependency order. Do not
make VLC reviewers recover our ignored dependency archive or host-specific build.

## Adopted for planning

- Three-phase story, before bookmarks, with contribution-map and architecture
  gates rather than immediate cosmetic cleanup.
- Existing-service reuse is the first simplification candidate; replacement of
  our helper is a hypothesis to test, not a decision already made.
- Clean build, branch-native tests, real UI proof, measured baseline/candidate
  comparison, independent review and exact public-diff review before submission.
- Focused MR/series, respectful review follow-through and honest disposition.

## Deferred / not inferred

Full coding/CI/legal/policy audit, live competing-feature search, maintainer interest,
selected target, prototype, rebuild and all implementation/submission work belong
to the story. No upstream acceptance, universal platform proof or completed
Phase 1 is claimed. No new architecture ADR was written without the experiment.

## Verification

Read-only source/document/API inspection and local story/ADR/source-footprint
comparison. Planning checks are recorded in the story work log after generation.
This pass performed no runtime test because it produced a plan, not a code change.

## Phase 1 current audit — 2026-10-05 (local; 2026-10-06 UTC)

The later request authorizes completing phases1/2, using SOL6.1 medium builders,
then halting before submission. The initial scout above is preserved historical
scope. Canonical GitLab project435's branch API and a fresh official-mirror clone
both identify master `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
The source checkout is isolated under ignored `work/upstream/vlc-master-story005`.
Runtime proof and narrow prototypes are summarized in the
[current readiness ledger](../evidence/story-005/current-readiness-ledger.md). The later selected mechanism is
[ADR004, ACCEPTED](../decisions/adr-004-upstream-preview-integration/adr.md)
as an implementation choice; runtime qualification and maintainer acceptance are separate.

### Contribution map

| Concern | Primary evidence and current interpretation | Preparation obligation |
|---|---|---|
| Repository/route | [Pinned README](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/README.md) identifies GitLab merge requests; GitHub is a mirror | Prepare a source series for canonical GitLab; no GitHub PR |
| Branch and patch checklist | [Sending Patches](https://wiki.videolan.org/Sending_Patches_VLC/) retrieved directly, page last edited2026-03-08: new work applies to master; stable is for backports | Freeze base, review complete diff, use focused changes with meaningful commit messages |
| Tests/distribution | Same checklist requires build, warning review and `make check`; added/moved/removed files also require `make distcheck` | Record actual tests, unsupported environments and failures; do not equate local scaffold checks with VLC proof |
| Style | [Code Conventions](https://wiki.videolan.org/Code_Conventions/), retrieved directly: surrounding consistency governs; new Objective-C avoids Hungarian notation; use class-purpose headers and availability handling | Match destination ARC/ownership/style, four-space indentation, no unrelated formatting |
| Authorship | Sending Patches requires correctly capitalized full author name and valid email; exact final attribution is a human fact | Do not manufacture authorship, sign-off or contributor attestations; confirm any missing identity before final commit preparation |
| Review conduct | Sending Patches directs replies/corrections in the MR, discourages needless rebases and individual pings; suggests re-requesting review after a week without response | Draft a concise review guide; actual review cadence belongs to phase3 |
| Licenses | Pinned macOS files carry GPL2-or-later, preparser core files LGPL2.1-or-later; [official legal page](https://images.videolan.org/legal.html) points to corresponding source obligations | Preserve applicable headers; inventory copied code and fixtures; source contribution does not qualify public binary distribution |
| Build matrix | [macOS build environment](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/extras/package/macosx/env.build.sh) sets minimum10.13; [CI](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/extras/ci/gitlab-ci.yml) defines x86_64 and arm64 jobs, Darwin19 triplets and Xcode26 arm64 runner | Local host is arm64 macOS27/Xcode27; runtime proof on it is not Intel/older-OS qualification |
| Native tests | CI builds using `build.sh -x`, compiles check targets with `make check TESTS=`, then runs `make -C modules check-macosx`; [XCTest list](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/tests/Makefile.am) has native data/formatter tests | Add meaningful tests to native build lists; inspect skip conditions; run broader relevant checks as available |
| Localization | Native controls use `_NS(...)`; [macOS POTFILES entries](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/po/POTFILES.in) register translatable source. Contribution checklist excludes unrelated `.po`/`.pot` churn | Mark new user strings, register source where needed, avoid fabricated translations |
| Accessibility | [ControlsBarCommon](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/windows/controlsbar/VLCControlsBarCommon.m) sets localized position label/title; existing hover panel is nonactivating and ignores mouse events | Preserve control semantics/focus; inspect and exercise actual keyboard/VoiceOver behavior on candidate |
| AI assistance policy | Searched pinned README/doc/CI, official contribution/style pages and targeted official-site results; no explicit VLC AI-assistance rule located | Unknown beyond searched scope. Do not infer approval, a ban, or apply another VideoLAN project's policy to VLC |
| Account/access | Public project/branch/MR/issues APIs are readable; selected review notes/discussions return401 | Submission-account permission and inaccessible feedback remain unknown; no account created or external message sent |

Written guidance is distinct from conventions inferred from accepted work:
[!9808](https://code.videolan.org/videolan/vlc/-/merge_requests/9808) reuses the
preparser for macOS local-item thumbnails; [!9502](https://code.videolan.org/videolan/vlc/-/merge_requests/9502)
removes blocking thumbnail acquisition; [!8453](https://code.videolan.org/videolan/vlc/-/merge_requests/8453)
addresses stale asynchronous cell results. These support focused rationale,
visible before/after evidence and explicit callback ownership. Sign-offs seen in
some descriptions do not by themselves establish a universal mandatory rule.
Their review comments were not accessible in this audit.

### Related work changes the integration question

[Open macOS!7493](https://code.videolan.org/videolan/vlc/-/merge_requests/7493),
head `6f53c171803cad33e6e987782832d21c07965bfd`, last updated2026-04-15,
already proposes a slider preview window and cache. The API reports unresolved
discussions. Its published diff adds a player-controller thumbnail call,
URI/rounded-position memory cache and preview delegate/window. It does not
establish selected-track/source-freshness/restart/NAS equivalence. Its old API
shape differs from the pinned request-handle preparser. No code from it has been
copied, and neither its age nor inaccessible discussion is permission to dismiss
or claim approval of a competing implementation.

[Design issue#29393](https://code.videolan.org/videolan/vlc/-/work_items/29393)
considers demux-provided, sideloaded, generated and media-library preview sources,
with shared lifecycle/player APIs. Its linked [September2025 meeting](https://code.videolan.org/videolan/medialibrary/-/issues/493)
records generation-cost concerns, fast-seek experiments and a possible initial
explicit-generation UI. That record is historical direction, not a measured
result on our host or a confirmed current product mandate. The pinned tree has
no `vlc_previews` API. Closed [!7822](https://code.videolan.org/videolan/vlc/-/merge_requests/7822)
is cited in the design issue as an on-the-fly approach whose architecture did not
fit. This is a concrete reason to resolve ownership before a large private port.

API searches covered the latest100 matching preview/thumbnail issues and MRs.
The100-row issue limits make the issue inventory bounded, not exhaustive.
Public MR metadata and diffs are available; note/discussion401 responses prevent
claiming a full review-history audit. Raw research receipts remain ignored in
`work/story005-scout`; durable conclusions and public links are recorded here.

### Initial gap matrix (retained planning baseline; current results below)

| Material gap | Pinned current behavior | Proposed discriminator/change | Verification |
|---|---|---|---|
| Native hover | `VLCPlaybackProgressSlider.m` has time-only nonactivating hover; ControlsBarCommon supplies duration | Reuse its tracking/presentation seam; account for fullscreen separately | Fresh real-pointer surfaces, hide/context races, geometry, controls |
| Selected track | Core exposes stable ES string identity and `video-track-id` selection; thumbnail arg has no dedicated track field | Probe a copied input item's canonical selected identity; reject unstable/ambiguous identity | Generated red/blue multi-track files, playback identity and resulting pixels |
| Actual time | Picture callback carries `picture_t`; timestamp assertion in `test/src/preparser/thumbnail.c` is disabled | Observe picture date independently before deciding whether API extension is necessary | Known frame/time, fast/precise, positive offsets/edit lists and VFR |
| Transform | Decoded picture has orientation/SAR/color; file export converts it | Establish what export applies; avoid duplicated transforms | Rotate/SAR/reference color fixtures and actual rendered output |
| NAS/open lifetime | `src/preparser/internal.c::ThumbnailerRun` creates/stops/closes input per request | Measure repeated request cost; retained session/multiposition extension only if needed | Local/slow-NAS timing plus open/read instrumentation, cancellation/watchdog |
| Cache shape | `VLCLibraryImageCache` uses one15%-position512x512 cropped image, path/size/mtime cache identity and per-source stale cleanup | Reuse suitable primitives, not its whole representative-artwork contract | Multiple positions/tracks, digest/guarded freshness, restart/corruption/eviction |
| Background work | Preparser executor/thread timeout bounds requests; no preview coverage scheduler | Preserve finite preparation, fairness and latest hover; resolve owner with shared preview direction | Queue bounds/faults, demand retention, matched playback and resource cohort |
| Public build | Local helper depends on ignored contribs/private FFmpeg8.1.2 patch; master contrib selects9.0 | Prefer native service; otherwise integrate dependencies openly with provenance | Fresh upstream checkout plus only proposed source patch builds |
| Fullscreen | Old `VLCFSPanelController` path is absent, but master still contains fullscreen resources/controls | Trace actual instantiated control classes before assigning adapter work | Main/detached/native/custom fullscreen UI proof; no inherited3.0 claim |

### Baseline and experiment status

SOL6.1 medium builder owns unchanged master build and another owns a standalone
preparser probe. Official CI's `VLC_FORCE_KERNELVERSION=19` is used to avoid
inventing a host-specific contrib triplet. Native Python is selected explicitly;
old Intel library search paths and previous3.0 repairs are not imported.
A1GiB reserve stops the new process group without deleting preserved artifacts.
Dependency mirror failures are recorded and exact pinned GNU archives may be
acquired from the primary GNU server only after upstream checksum verification.
The unchanged master app and independent initial candidate now build; each ran
253 native XCTest cases with no failures. This establishes build/test substrate,
not a feature port, its final independent reproduction or architecture selection.

### Experiment update and next decision — 21:06 local

The native [preparser matrix](../evidence/story-005/preparser-probe-results.md)
found selected-track transport, orientation and sample-time gaps. Narrow process
and picture-orientation corrections pass their actual registered regressions.
The track prototype selects the correct red/blue pixels in both execution modes
and fails for an invalid ID; corrected raw-file transport passes both registered
tests and the equivalent eight real file requests.
These patches retain their own scope and caveats in the readiness ledger.

The experimental MP4 edit subtraction passed ordinary positive-edit cases but
failed trimmed preroll; it has been removed from the integration candidate.
The [source trace](../evidence/story-005/movie-time-contract-gap.md) distinguishes
stream timestamps from movie position and display eligibility. Extending the
one-line experiment into general timing repair is deferred.

The next discriminator is the story's retained-helper option using current
FFmpeg 9 dependencies, source-reproducible private changes, and actual master
identity/timeline mapping. Existing 3.0.24 proof cannot qualify that port. This
tests an already-listed alternative without reducing the feature/NAS/freshness
requirements or implying acceptance of a private decoder by maintainers.

### Selected port and eligibility checkpoint — 21:34 local

ADR004 now selects the retained helper through the normal FFmpeg9 contrib source
recipe, with direct native TrackNumber mapping and master's existing hover panel.
The normal dependency/helper build succeeds; exact source and runtime receipts
live in Story005 evidence. This supersedes the prior discriminator-only status.
Independent review and fresh native qualification remain required.

The general issue behind H1 is presentation eligibility across two demuxers:
container track identity does not establish an identical virtual timeline.
[Matroska chapters](https://www.matroska.org/technical/chapters.html) distinguish
flat markers from ordered editions, while [segment linking](https://www.matroska.org/technical/notes.html)
can join content across files. The pinned VLC native demuxer honors ordered and
hard-linked presentations. FFmpeg9's existing parser ignores EditionFlagOrdered.
[The data layout specification](https://www.matroska.org/technical/diagram.html)
allows Chapters after Clusters and explains why absence of SeekHead can require
scanning all top-level elements; header-only absence of a flag cannot certify flat
eligibility. An existing-parser, bounded conservative admission check is being
designed and compared with generated fixtures. No unverified origin correction
or new general container parser is selected by this finding.


### Current architecture gap disposition — 22:30 local

This closes the phase1 investigation/plan gate, not phase2 qualification. ADR004
is the selected technical proposal and the three-part public series is concrete.
No maintainer direction is being treated as an implementation prerequisite or as
endorsement; inaccessible comments and any requested future design changes remain
explicit external uncertainty. No upstream contact occurred.

| Material gap and pinned source | Selected resolution | Current evidence and remaining proof |
|---|---|---|
| `src/preparser/internal.c` creates a new input per request; callback picture date does not certify movie presentation | Retained FFmpeg helper through normal contrib/build; no experimental core dependency | Independent helper pixel/movie-time oracles and exact32-reply parity pass; full native consumer remains open |
| Core thumbnail request lacks selected identity; Matroska native identity differs from libav stream index | Owned atomic player snapshot, protocol4 ID/count guard, normal TrackNumber patch and conservative parser-owned flat admission | Reordered/nonconsecutive IDs, direct selector/packet/playback comparisons and38 admission cases pass; unsupported virtual presentations fail before ready |
| Picture constructors drop orientation in native prototype path | Existing helper transform conversion retained; prototype orientation patch stays separate | Rotation/SAR/reference pixels match; final native visual presentation required |
| `VLCLibraryImageCache` stores representative cropped artwork, not multi-position/fresh-source previews | Dedicated bounded cache/service, fixed15s qualification, v5 mapping namespace | Source review and focused cache/service/context tests pass; final master restart/freshness and full suite pending |
| No timeline coverage scheduler in current preparser/hover owner | Finite background plan, one latest demand, demand retention and bounded worker lifecycle | Automated scoped contracts pass; matched active-preparation playback and controls still required |
| `VLCPlaybackProgressSlider.m` owns existing time-only panel; master fullscreen classes differ from3.0 | Reuse one slider/panel, localized settings and existing accessible controls | Production app compiles/packages; actual slider6 methods pass; baseline main/native-fullscreen partial acquisition, detached restart issue unresolved |
| Helper existed only in ignored local build machinery | Normal FFmpeg9 source patches, Autotools/Meson helper, official app packaging/signing, portable public fixtures | Normal app and helper build; draft3patch tree equality; clean independent reproduction/distcheck and available matrix proof remain open |
| NAS scan cost of complete presentation certification |512-byte isolated existing EBML parser scan with finite limits and cursor restoration | Two warm legal NAS layouts,72requests/36paired exact image/time results, one open each; cold/stalled/large-source latency remains unqualified |

Build and runtime work stopped again when free space fell to about831MiB.
The1GiB reserve is unchanged. The next native discriminator uses a fresh owned
bundle domain to exclude inherited fullscreen restoration, preserving old state.
The baseline sample shows `makeKeyAndOrderFront` entering an automatic AppKit
fullscreen transition and blocking in VLC's vout mutex. This supports a lifecycle
hypothesis, not attribution to the feature. [Apple's per-launch restoration guidance](https://support.apple.com/en-ie/102318)
and pinned `VLCMain`/`VLCLibraryWindow` restoration hooks informed that experiment.
The Apple developer Markdown endpoint was unavailable; no claim rests on it.

### Native baseline observation and app identity — 23:54 local

The storage hold is cleared. Final registered feature tests pass277 cases; native
consumer qualification remains independent. A fresh domain resolves the initial
detached setup, but a paused midpoint-seek/Play sequence reaches nearEOF before
the second click. Pinned `doc/clock.md` describes the nominal audio-master clock;
`VLCControlsBarCommon` simply delegates Play to `togglePlayPause`. Late PCR errors
alone do not establish a clock defect. Ordinary playing startup with the new
public300second fixture advances0→5seconds over5seconds; the next pause/seek
discriminator has not run because the test window becomes unobservable.

The general second problem is stale application identity and window acquisition
after modifying the same bundle path's identifier. [Apple's Launch Services guide](https://developer.apple.com/library/archive/documentation/Carbon/Conceptual/LaunchServicesConcepts/LSCConcepts.html)
directs explicit registration or an updated modification time after significant
registration metadata changes; [LSRegisterURL](https://developer.apple.com/documentation/coreservices/1446350-lsregisterurl)
can force replacement of cached registration. Updating only the owned bundle's
registration succeeds, but CUA still resolves that path to its former identifier.
This supports an additional tool-side identity-cache hypothesis, not a proved
VLC defect. The next bounded discriminator renames the same owned wrapper to a
new path without changing its identifier, executable or profile, then binds CUA
to that path. No global Launch Services reset, default-handler change, security
setting change or installed-app alteration is selected. If binding still fails,
stop new wrappers and report the tool/environment limitation.

### Real controller test initialization — 00:17 local

The new real-player epoch test initially aborts during controller teardown:
`resumeOtherAudioPlaybackApps` reads `macosx-control-itunes`, but the test process
has not registered the normal GUI module's option descriptor. This is distinct
from the epoch assertion under test. The revised harness preflights the descriptor
before constructing the controller and consumes the generated normal plugin cache
without scanning/loading duplicate Objective-C GUI classes in the test process.

The first cache-generation probe using the libtool shell wrapper still omitted
that descriptor. Running the normal built Mach-O cache generator with scoped
contrib framework and core-library paths includes it. [Apple's runtime protection
documentation](https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/RuntimeProtections/RuntimeProtections.html)
explains why dynamic-loader environment variables can be lost at protected system
process boundaries. That is consistent with the wrapper behavior; the successful
probe also supplies an explicit core-library path, so it does not isolate one
sole cause. The chosen public build prerequisite uses configure-derived paths and
the real cache generator after the GUI dependency, before normal/focused tests.
No system security setting or synthetic option descriptor is introduced. Runtime
test success is still a separate gate from this cache-generation proof.


### 2026-10-06 transient-controls capture disagreement

Problem class: sequential observations of transient native UI can disagree even when each capture is accurate. Actual1725 baseline live SCK has20 valid knob frames at391–1174ms after routed input, while the independent screenshot begins2481ms later and has no visible controls. Exact fade cause is unproven without timer/alpha/pointer traces. Pinned master `VLCMainVideoViewController.m` lines409–416/424–438/447–468/492–522 exposes mouse-over guards, configured autohide with1s minimum, fade and show logic; `VLCVoutView.m`214–229 posts show-controls on mouse movement. Existing Apple complete-frame/displayTime contracts remain the measurement boundary; a bounded documentation refresh returned JavaScript-only pages and adds no new factual evidence.

Decision: preserve the frozen2000ms measurement, then use a separate no-click reveal/park and independent screenshot, bracketed by unchanged paused/source/time/slider state. Native mouseMoved does not execute slider down/drag/wheel seeking. This post-measurement capture establishes independent center agreement only and cannot replace a response timestamp. Concurrent screenshot sampling would disturb the measured interval and adds unnecessary orchestration. Prepare a small fresh ignored successor and review before one local applicability test; no automatic retry, broader classifier or inferred product regression.


### 2026-10-06 visible-controls measurement configuration

The2311 post-read reveal independently confirms the baseline right knob, but controls disappear before the next precheck. Rather than continue reveal timing iterations, use VLC's existing identical `--mouse-hide-timeout=600000` setting prospectively for both control arms. Pinned `src/libvlc-module.c`365–367 documents milliseconds;1720 defaults1000 and defines no option-specific range. `VLCMainVideoViewController.m`432 and `VLCFullVideoViewWindow.m`76 divide by1000 and clamp to at least1s, with no explicit upper bound. Ten minutes covers the bounded600s measurement without changing its20-response/+20% criterion. These macOS consumers gate controls/titlebar and cursor hiding; other platform/magnify consumers exist, so this is not a universal no-effect claim. Seek/play action and direct helper/cache configuration remain unchanged. Prolonged hover-presentation eligibility is a setup effect to disclose. Verify actual command identity and visible controls in both arms; report latency with controls kept visible, with default fade evidence separate. Keep the frozen observer/routing/displayTime/independent-PNG contracts and no automatic retry. This configuration prevents the transient prerequisite from being the experiment, instead of weakening the classifier.

### Process lifecycle snapshot applicability (2026-10-06)

The1760 native setup captured matching collapsed-queue projection in both arms,
but an extra short-lived child lost its executable path between ps enumeration
and libproc lookup. This is a concurrent process-census race. Apple XNU
[proc_info](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/proc_info.c#L2046-L2061)
and [libproc](https://github.com/apple-oss-distributions/xnu/blob/main/libsyscall/wrappers/libproc/libproc.c#L249-L266)
explain ESRCH for PIDPATHINFO when no live process is found; these sources are
public main, not an assertion of exact installed-kernel identity. The local owned
child test confirms unreaped Z/path0-ESRCH, followed by waitpid/absence. See
`work/story005-process-lifecycle-plan001/owned-child-result.json`.

Selected technique: one bounded lifecycle check only for an extra child's
0/ESRCH, accepting confirmed absence or samePID/PPID/UID/start+Z. Record unknown
exited children without executable/resource claims. Keep app, full-argv worker
and explicitly pinned retained-worker checks strict. No full-snapshot retry or
name inference. Independent review clears isolated128f1063; caller wiring and
fresh014 integration are pending. This does not retroactively qualify1760 or
change source/cache/capture/scoring criteria.


### 2026-10-06 shutdown quiescence and unloaded plugin attribution

Problem class: background workers still executing code or waiting on data while a dynamic plugin unloads. The owned1801 candidate010 exit is an actual SIGSEGV, not clean shutdown: pthread condition wait returns into an unmapped image while another thread executes dlclose/module_EndBank. Static offsets align with the bundled UPnP worker and global mini-server pool, but the crash image inventory omits that plugin. Baseline/candidate whole UPnP binaries and UUIDs differ; only the suspected worker range is byte-identical. Static alignment alone does not prove runtime module identity or feature independence.

Bounded upstream history inspection found [pupnp PR586](https://github.com/pupnp/pupnp/pull/586), which drains workers before webserver-state destruction, and [PR646](https://github.com/pupnp/pupnp/pull/646), which fixes active-connection synchronization surviving mini-server shutdown. The pinned1.14.31 retains the older patterns. [Issue502](https://github.com/pupnp/pupnp/issues/502) concerns a related shutdown wait, not this exact fault. These sources motivate orderly quiescence, but do not identify our failing step. No speculative backport, UPnP disable or plugin-unload policy change is selected.

Selected local discriminator: at most three untouched baseline012 cycles using the same SIGTERM mechanism, retaining pre-quit vmmap ranges and a brief sample with actual plugin UUID. Stop first abnormal exit and compare retained crash signature; three clean cycles remain inconclusive. Frozen plan and plugin comparison: work/story005-playback-shutdown-attribution-plan001. The original crash, source/build differences and diagnostic perturbation remain explicit.


### 2026-10-06 asynchronous seek observation

The002 candidate drag physically reaches burned03:20/frame4800 while its immediately persisted oldrc response remains play3/currenttime32. Pinned `modules/control/cli/player.c`524–537 locks and queries vlc_player_GetTime; player.c1480–1487 uses seeking=false. timer.c596–645 returns requested seek_ts only for seeking=true; otherwise it interpolates the existing source point. SeekByPos input.c120–153 announces the seek before asynchronous input_ControlPush, and timer.c429–437 explicitly allows points before input-thread seek processing. macOS controller521–536 separately consumes requested seek on the main queue. This establishes an asynchronous-observation class, not a completed-seek guarantee from requested UI state. The250ms stats callback interval is not a convergence bound.

Adopt established [bounded condition waits](https://www.selenium.dev/documentation/webdriver/waits/) for unused unscored surface cases: one input action, fixed3s deadline including query completion,200ms polling, persist every strict reply. Only old time can be pending; parsing, identity, URI and play state remain strict. Preserve the predefined target tolerance with ordinary elapsed playback, then require at least5s continued core and burned-video advance. No seek resend, main-case retake or latency score. Earlier immediate-gate failures and missing first raw response remain explicit.


### 2026-10-06 GUI discovery ownership changes the shutdown diagnosis

The pinned upstream GUI has a concrete C-reference imbalance: `vlc_media_source_provider_GetMediaSource` returns an owned reference (include/vlc_media_source.h290); `VLCMediaSourceProvider.m`44–50 wraps it without releasing that reference, while `VLCMediaSource` initializer155 adds another Hold and dealloc321 releases only its own Hold. Core provider deletion247–250 only deletes the provider object, with no source/SD drain; libvlc cleanup destroys interfaces then provider then module bank. A leaked discovery source can prevent CloseSD and the shared wrapper's final UpnpFinish before unload. This better fits an idle condition-wait worker than only a detached thread's narrow return window. Root independently read these actual pinned files; source pins and complete ordering are in work/story005-playback-shutdown-attribution-plan001/gui-discovery-lifetime-research.md. Exact5678 causality remains unproved.

The public host explicitly stops/destroys discovery and bypasses Cocoa ownership, so its clean result is not the relevant comparison. EmptyGUI initialization sets LAN mode and loads media sources in VLCMediaSourceBaseDataSource.m108–110/195–217. Selected discriminator uses unchanged baselineGUI under [LLDB's existing breakpoint/thread inspection](https://lldb.llvm.org/use/tutorial.html), actual mapped UPnP identity and all threads immediately before that plugin's dlclose. No private media, inferior function calls, production instrumentation, permission changes or clean-run stress loop. A live worker/return continuation into the identified image at unmap positively violates bank.c's no-longer-used precondition; absent workers or unavailable debug identity is inconclusive. Debugger scheduling and final loader-reference uncertainty remain explicit.


### 2026-10-06 19:09 Edmonton — baseline lifecycle finding and stop decision

The source ownership audit establishes an unchanged upstream Cocoa GetMediaSource owned-reference imbalance. Actual baseline verbose logging confirms the affected UPnP services path activates without normal close while renderer discovery closes and later cleanup proceeds. The complete raw trace remains private because of LAN identities; [sanitized source/observation attribution](../evidence/story-005/shutdown-baseline-attribution.md) preserves source links, exact hashes and inference limits. Mapping/sampler/LLDB attempts remain failed/inconclusive and publicAPI short hold deviated. The source defect plus activated-path corroboration supports carrying a baseline lifetime hazard in focused maintainer review; candidate SIGSEGV exact causality remains unproved. Stop diagnostics and retain the fault; do not backport speculative UPnP fixes or claim clean shutdown. Final package and validation distinguish readiness from upstream acceptance.


### 2026-10-06 19:28 Edmonton — review burden and acceptance assessment

Cam asks whether the prepared series is a typical patch and likely to receive nearly issue-free acceptance. Fresh direct diff-line measurement: four patches,59files,+9981/-56. Parts0..3 add18/283/3659/6021lines respectively;34newfiles. Filename-based rough categories: tests/fixtures5035added,docs387,production/build4538 andXIB21 (4559combined). Tests reduce uncertainty but do not remove review/maintenance responsibility. These are source lines, not a measure of semantic complexity.

Fresh read-only official GitHub mirror API sample of12 latest commits: median1file and6addedlines; individual macOS cache-state change460b4747d8be0bc830be6969d07dfba3eb22fcc2 touches1file,+302/-58, and title-array change04d555a9d391f009d4f510f508fef58c39bdf810 touches1file,+3/-2. Sources: https://api.github.com/repos/videolan/vlc/commits?per_page=12 and https://github.com/videolan/vlc/commit/460b4747d8be0bc830be6969d07dfba3eb22fcc2 . This small latest-commit sample is descriptive only, NOT a distribution of whole MRs, typical feature size or acceptance probability. No statistical claim about standard VLC MR size is justified.

Official https://images.videolan.org/vlc/ currently advertises3.0.24; https://nightlies.videolan.org/ lists4.0 experimental development builds. Main site/wiki/GitLab browser endpoints were blocked/inaccessible on this pass; no fresh review-discussion or MR7493 status is claimed. Prior pinned architecture findings remain inputs, not fresh maintainer feedback.

Root and independent SOL6.1medium architecture assessment: useful serious reviewable implementation, substantial review burden, no grounds to promise zero findings or easy acceptance. Main risks are helper/shared-native-service ownership, separate FFmpeg TrackNumber/admission upstream boundaries, persistent IPC/cache/scheduler maintenance, incomplete supported matrix/non-green distcheck and actual unresolved candidate shutdown fault. Proven baseline ownership defect does not establish exact crash independence or oblige reviewers to accept that scope boundary. Recommendation for any later authorized submission: concise architecture rationale and targeted ownership/dependency questions with complete tested series available; expect revisions or architecture redirection. Existing ready-for-maintainer-review status does not mean merge-ready, endorsed or likely accepted as-is. No source/runtime/contact/submission changes made in this assessment.

### 2026-10-06 19:50 Edmonton — reviewer-improvement standards correction

Fresh audit rechecked the official [Sending Patches VLC](https://wiki.videolan.org/Sending_Patches_VLC/) checklist: error-free `make check` and complete `make distcheck` are requirements when adding files. Our preserved failed distcheck and incomplete terminal stages do not meet that checklist. Disclosing failures is necessary but is not a waiver. No successful full CI or maintainer exception is established. Current characterization is **prepared for maintainer review; submission checklist incomplete**. Phase2 readiness is reopened; old raw results remain preserved. No contact or submission authorized.

General reviewability comparison used [Google small changes](https://google.github.io/eng-practices/review/developer/small-cls.html), [LLVM code review](https://llvm.org/docs/CodeReview.html), and [Linux submitting patches](https://www.kernel.org/doc/html/latest/process/submitting-patches.html): prefer self-contained logical changes, related tests, buildable intermediate states and a short problem/ownership entrypoint. These are general engineering practices, not additional VideoLAN rules. Locally traced native dependencies support service/cache/worker/scheduler foundation before context/player/UI activation without new production stubs. Two parts would reduce the largest native patch by about24%; three parts do not reduce the largest and add proof cost. Decision conditional on actual normal intermediate build/test and final-tree identity; source tracing or successful apply alone is insufficient. No architecture replacement or loss of NAS/freshness/selected-track behavior is authorized by this packaging improvement.


### 2026-10-07 — current004 shutdown returns to condition-wait failure

Fresh canonical016 built from72freeze8 passes actualcoherent acquisition/completeprebind/strictmedia; two independently observed advancingburnins precedeONECommand-Q. ActualownedPID45655 exitsSIGSEGV-11/noSIGTERM. Exactcrash851fe682db84047f4699cd684b76e278865cf28c39f5ae845ad5cc0dd84fc241 faults pthread_cond_updateval/pthread_cond_wait, unknownreturn0x11d388d24, FAR0x11d3b5354. Currentmain/core/nativeUUIDs match016. CurrentGetMediaSourceRelease correction is alreadypresent. This does not establish a common cause with historical5678 or disprove the separate015queued-resize defect.

General problem class under investigation: a worker/condition surviving dynamic-image teardown. Established requirements remain orderly quiescence before freeing synchronization/storage or unloading code: [POSIX mutex lifetime](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_mutex_destroy.html), [Apple dynamic-library unloading](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/OverviewOfDynamicLibraries.html), and [crash symbolication](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report). These explain the mechanism class; they do not identify this process's missing image. Reuse prior pinned source/ownership and pupnp586/646 comparisons; no speculative dependency backport or plugin-unload suppression.

Boundedoffline report work/story005-native016-crash004-symbol-inventory/report.json SHA9d917824b925eb7ef9f97932a8a8b912d91dd8714b45a63fac83a3c77a3fb56c scans398existingimporttables/20waitimporters, then two smallUPnPranges. WorkerThread returnoffset0x44d24 implies hypotheticalalignedbase0x11d344000; x19-relative0x71308 equalsgRecvThreadPool, x0-relative0x71348 equalscondition+0x40, FARrelative0x71354 equalscondition+12. Strong staticcorrespondence remains candidate-only: runtimeimageUUID/range absent fromcrash. Stoplargerinventory; no blindnative repetition/debuggertoolrepair. Nextdecision depends on boundedcurrentCocoaownership audit andstrongstrategyreview; no productpatch or newruntime released.

### 2026-10-08 — patch ordering and embedded patch whitespace

A proposed prerequisites-first scratch replay fails at follow-up0006: it edits `VLCTimelinePlayerContextTest.m`, introduced by the feature series. Preserve revision13's published feature-first order; the component label does not establish independence from feature files. The standalone autohide correction can be tested separately ahead of that published order. No existing patch/order was changed.

The next strict replay stops on13 whitespace diagnostics in feature0001's newly added FFmpeg patch files. The general problem is serialized unified-diff data being linted as ordinary source: blank context lines contain a required leading space. The [Git apply manual](https://git-scm.com/docs/git-apply) documents that `warn` preserves supplied bytes, while `fix` changes them and `error-all` rejects them. Do not strip nested patch context markers to satisfy an outer whitespace gate. Root chose a bounded final static experiment: audit every diagnostic as an exact blank context marker inside the two embedded patch files, permit byte-preserving `warn` for that one patch only, retain strict checking elsewhere, and require the complete72-file result to match source9 exactly. Any additional diagnostic or output mismatch stops the experiment. This does not relax build/native qualification or alter the original public checker; the result is recorded separately in the build-attempt report.


## 2026-10-08: bounded multi-stage verification overhead

General problem class: repeated subprocess inspections plus inter-phase coordinator waits exhaust a shared verification deadline even when product packaging succeeds. Successor017 stops at840s reserve during final source pin; raw failure remains unchanged. Root independently sums both command receipts:1,592 UUID invocations/355.254s, including398 build paths queried in both normal/isolate phases. Worker timestamp decomposition estimates220.538s inter-phase waits (birthtime proxies include dispatch/setup),461.749s recorded subprocess spans and157.713s hashing/checkpoint/bookkeeping. This is orchestration time, not measured dwarfdump CPU.

Primary sources: [Python monotonic clock](https://docs.python.org/3/library/time.html#time.monotonic) documents a clock unaffected by wall-clock updates and shared across macOS processes; [LLVM dwarfdump](https://www.llvm.org/docs/CommandGuide/llvm-dwarfdump.html) documents multiple filename inputs and UUID output. Decision: no retry, extension or retroactive qualification in this run. A future separately reviewed continuous transaction should batch immutable UUID inventories, retain every398mapping/code-section/hash comparison and the same absolute stop/resource/cleanup guards, with no unbudgeted mid-transaction approval waits. Local Apple-tool multi-file output/parser compatibility has NOT been tested; a tiny read-only probe is required before adoption. Independent source9 full gates remain useful and are released separately; they preserve unqualified017 rather than qualify it.

Local follow-through: a distinct root-reviewed read-only retained017 method passes in7.248s. It freshly hashes/compares all398 actual binaries and sections and pins796existing raw UUID results to those exact binary bytes. No new batched Apple invocation is used, so batch-tool compatibility remains untested. This demonstrates applicability of content-addressed evidence reuse here; it does not prove universal speedup or turn the old deadline failure into a pass.


## 2026-10-08: exact patch composition without a source checkout copy

General problem class: deriving reproducible whole-source identities for a patch series while protecting a dirty shared checkout. Primary [Git environment documentation](https://git-scm.com/docs/git) specifies an alternate index and owned object directory, with read-only alternate object lookup; [git apply --cached](https://git-scm.com/docs/git-apply) applies only to the index and creates no commit; [write-tree](https://git-scm.com/docs/git-write-tree) derives a tree object from a fully merged index. Decision: root-reviewed bounded owned bare/index/object transaction, read-only existing baseobjects,13canonical patches with exact byte/mode/blob comparisons to source9. No fetch, sourcecopy, commit/branch or sharedindex mutation. A successful local receipt will qualify static composition identities only; distribution/native/submission gaps remain separate. Failed/incomplete local derivation must not be replaced by historical source8 tree IDs.

Local applicability PASS: owned-index13patch derivation completes12.971s/2.86MB, finaltreea568215775ffa7ddd6bbad393d466d79ae72e131. Root independently checks all72current-source bytes/modes/blobIDs against the actual full tree and31preserved inputs. No sharedindex/checkout mutation occurs. The method resolves sourceidentity uncertainty, not distcheck/native behavior.


## Helper function-result casts: inherited feature warnings, 2026-10-08

Find-only review identifies three avoidable feature-added -Wbad-function-cast warnings in timeline-preview.c450/565/566 as submission-readiness cleanup. Current source9 and historical source8 complete010 distcheck logs contain identical diagnostics; the helper SHA256 is unchanged. Inherited-source8 does not mean upstream-clean. A targeted existing-note search found no specific prior justification. Finite-angle/fmod4 and bounded1..320/1..180 output guards support representable conversions; the diagnostics establish no correctness or native-cause bug.

Official [Sending Patches](https://wiki.videolan.org/Sending_Patches_VLC/) was retrieved via bounded compressed curl: “The compiler does not mention new compilation warnings.” Rare unavoidable/counterproductive cases require explanation; no such exception is established here. [Clang](https://clang.llvm.org/docs/DiagnosticsReference.html#wbad-function-cast) and [GCC](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wbad-function-cast) classify direct function-result casts to nonmatching types. Proposed smallest cleanup assigns the same three double expressions to named temporaries before explicit integer casts, preserving guards and math; no suppression or algorithm change. Exact unapplied diff and bounded guard analysis: work/story005-helper-warning-review001/{REPORT.md,proposed-warning-cleanup.diff,proposal-provenance.json}. Root decides postgate application/new freeze and warning/behavior/build/package requalification. Active source9 gates and all historical evidence remain untouched; warning removal has not been locally demonstrated.

### Dependency-rule parsing clarification, 2026-10-08

GCC documents that dependency generation emits a make rule with backslash-newline continuations and -MP adds separate empty phony rules: https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html . The private warning-probe001 incorrectly consumed those phony target names as dependency paths; successor002 joins continuations and reads only the first logical rule, locally verifying all306 actual header paths/hashes for each arm. Correction to the earlier root attribution: the retained full-gate closure parser itself splits at a blank line and filters recognized source-header suffixes, which also excludes phony names ending colon. It does not literally use splitlines()[0]. No full-gate parser or acceptance assertion was changed by this clarification; probe002 first-rule applicability is demonstrated by its actual306-header correspondence, not assumed code identity to the gate parser.


### Signed framework provenance, 2026-10-08

General problem class: packaging legitimately transforms a signed Mach-O container, so a pre-signing whole-file hash is not a data-resource equivalence assertion. Apple TN2206 explicitly documents that signing modifies executables: https://developer.apple.com/library/archive/technotes/tn2206/_index.html . Current pinned VLC package.mak copies Sparkle then invokes codesign.sh with adhoc identity; codesign.sh force-signs Sparkle components/framework and validates signatures. Established comparison is exact static-data hashes plus mapped executable sections/UUID and independently verified signatures, with full current signed-container hashes retained as identity pins.

Local negative witness: source10 official make passes but package018 qualifier fails because its fifth resource row treats Sparkle as immutable data. DSA/nib/icon/assets are exact. Sparkle built417856B versus packaged399872B; LC_CODE_SIGNATURE offset398784 unchanged, blob19072→1088B. All30 backed sections and UUID match; packaged wholeSHAbe718bd1f0daafb7b874316e9fb9baf6fbf87a085f7d9727c9d4d23001c2cb32 is exact to historical qualified017. Pre-signature differing byte ranges are retained; no blanket whole-nonsignature-byte equivalence is claimed. Independent reconstruction confirms all398 mapped section/UUID results from original raw successful commands/current file hashes. This is analysis, not retroactive phasePASS.

Decision: preserve original supervisor/failure/outputs; prepare one distinct read-only retained-normal qualification using data-resource fullSHA and Sparkle's mapped Mach-O/signature proof, followed only by separately reviewed fresh018 isolation. Retain original900s composite budget, physical floor, all398 comparisons, complete metadata/security/source/history/namespace checks. No rebuild, source fix, skipped resource or weaker meaningful test gate. Root reviews concrete adapters before release. Native behavior remains unqualified.

### Contribution-policy refresh availability, 2026-10-08T04:02Z

Root's bounded web refresh could not retrieve the direct [Sending Patches VLC](https://wiki.videolan.org/Sending_Patches_VLC/) and [Code Conventions](https://wiki.videolan.org/Code_Conventions/) pages. The official [VLC developers compatibility page](https://images.videolan.org/developers/vlc.html) was accessible, but includes historical mailing-list advice and is not evidence of a changed submission route. The [pinned README](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/README.md) was accessible again. Retain the dated contribution map and existing pinned source/MR-route evidence as controlling inputs; disclose the unavailable wiki refresh instead of claiming fresh policy confirmation. No new AI-assistance rule, sign-off requirement, standards approval or maintainer acceptance is established by this refresh. Future submission preparation should recheck the canonical current route when accessible.
