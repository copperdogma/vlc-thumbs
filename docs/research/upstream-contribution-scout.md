# Initial scout — VLC upstream contribution (Story 002b / 005)

**Scouted:** 2026-10-05. **Status:** bounded planning scout complete; full Phase 1
contribution/architecture audit remains pending in
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
