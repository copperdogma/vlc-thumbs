# Scout001 — VLC patch submission process

**Source:** Official VLC README, VideoLAN patch checklist and canonical GitLab API.
**Scouted:** 2026-10-09. **Scope:** submission mechanics and current written gates.
**Previous:** [October5 scout and subsequent audits](../research/upstream-contribution-scout.md).
**Status:** Research complete; recommendations only. No account, fork, upstream
branch, merge request, message, product change, commit or push created.

## Findings

1. **Canonical GitLab merge request — HIGH value, inline preparation.**
   The [current official README](https://raw.githubusercontent.com/videolan/vlc/master/README.md)
   requires GitLab MRs, with CI and discussions resolved before merge. The
   [official migration announcement](https://mailman.videolan.org/pipermail/vlc-devel/2021-April/143228.html)
   identifies contributor forks and GitHub as a mirror. Our GitHub project is the
   preparation repository, not VLC's submission destination. Recommendation:
   use a VideoLAN GitLab account, fork `videolan/vlc`, push a dedicated source
   branch, then open an MR targeting master. Account availability/access is not
   verified; account terms or credentials remain human actions when needed.

2. **Latest-master applicability — HIGH value, bounded next task.**
   [Sending Patches VLC](https://wiki.videolan.org/Sending_Patches_VLC/) requires
   latest master for new changes; bugfix branches are for backports. Canonical
   [master API](https://code.videolan.org/api/v4/projects/435/repository/branches/master)
   freshly reports default master at `428110923693cd391229f8b6afce4e61debc04f0`,
   committed2026-10-09T14:10:22+02:00. Our qualified base is
   `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Recommendation: check application
   and inspect intervening changes before submission. If adjustment is needed,
   preserve the qualified snapshot and validate affected consumers only. This
   scout has not tested current-master application or qualified a new base.

3. **Written submission checklist — HIGH value, mostly already implemented.**
   The checklist requires surrounding code conventions, applicable license,
   successful build on at least one configuration, error-free `make check`, no
   unexplained new warnings, complete `make distcheck` when files change, clean
   whitespace/indentation, no unrelated changes, full real author name/email,
   meaningful commit descriptions and a final diff inspection. Current source10
   preserves the build/check/distcheck, targeted warning cleanup, source licensing,
   author/contact and review-map evidence. Reuse it only where tested inputs still
   apply; local proof does not replace upstream CI. No new sign-off or AI-specific
   rule is established by these sources. The checklist is not an exhaustive
   policy inventory. Current thirteen messages are drafts; real Git author
   metadata and complete source-only diff must be inspected when constructing
   the submission branch.

4. **Review follow-through — MEDIUM value, Phase3 work.**
   Answer comments and correct concrete findings in the MR. The official page
   advises requesting review again after a week without response, avoiding
   personal pings and unnecessary rebases during review. It says maintainers
   perform the final rebase once accepted. Preparing initial latest-master
   applicability differs from repeatedly rebasing an open MR. Review timing,
   bot behavior and acceptance cannot be promised.

## Practical submission sequence

1. Check the complete thirteen-patch series against current master; resolve any
   actual source conflicts and run proportionate affected checks.
2. Establish the VideoLAN GitLab account/fork and construct the source branch
   with the reviewed messages and Cam's confirmed author identity. Exclude this
   project's development journal, private evidence, media and app binaries.
3. Inspect the exact source diff and commit history; open the GitLab MR using
   the concise description, patch/dependency map and scoped validation/limits.
4. Monitor upstream CI and respond to review; update the branch for concrete
   findings and request another review after a week if silent.

This is a recommended sequence, not authorization to publish or contact VLC.
Parent Story005 Phase3 remains open. No architecture change or new ADR is needed:
ADR004 already selects the mechanism and official route.

## Approved / deferred

- Research and persistent process guide: requested and completed.
- Current-master integration and source-branch construction: recommended next
  bounded preparation work, not performed here.
- Account/fork/MR submission and reviewer communication: deferred to an explicit
  submission instruction. No inferred maintainer preference is a blocker.
- New runtime campaigns, protocol/harness work, binary release and unrelated
  cleanup: skipped as unnecessary to this scout.

## Verification and evidence

The web tool freshly retrieved the official README and migration announcement.
It could not fetch the wiki/GitLab project page; bounded compressed HTTPS curl
successfully retrieved the actual wiki and canonical branch API. The wiki reports
revision66762, last edited2026-03-08T13:53. No changed detailed checklist rule was
observed against the October5 audit. Historical announcements are not current
bot/timing guarantees. Source10 package, Story006 validation and ADR004 were
compared locally; no submission branch or runtime test was made.

Local verification: reread this note/index, resolve local links, run project
methodology validation and whitespace check. Research receipts remain ignored
under `work/story006-submission-scout001/`.

## Execution obstacle research — October12

General problem class: asynchronous remote repository creation. The GitLab
[Project forks API](https://docs.gitlab.com/api/project_forks/) documents that
forking returns immediately and completes in a background job; import_status is
the authoritative progress indicator. Actual fork project5462 exists and points
to upstream435, while browser and unauthenticated git transport still report no
repository. Public project API omits authenticated import details; direct browser
API navigation is blocked by the client. Do not bypass browser controls, create a
duplicate fork or initialize an unrelated empty repository to hide the failure.
Decision: retain the fork and check again after independent build work; report a
persistent server-side dependency honestly if it remains. No cause is proven.

Gitpush SSH host trust is separately checked against the official HTTPS instance
configuration. Scanned ECDSA fingerprint matches
SHA256:SWGDwhH7ISsL56IFvLRIE92AgtckLdMeU3/F2sZRD+w. A task-local known-hosts
file retains strict verification; no accept-any-host fallback or global trust
change. User confirmation is pending before adding an authentication key to the
account. This is not a product validation issue.

### Corrected diagnosis after owner-requested workflow audit

Cam explicitly forbids sending administrator email and requests a correctness
recheck. Fresh read-only audit confirms fork5462 belongs to cam.marsollier and
links upstream435, correct transport URLs, and accepted registeredpublickey;
it does not establish repository provisioning failure. Public API omits import
state and normal browser API URLs are blocked by the client. The official GitLab
controller exposes a normal read-only `/-/import` status page. Actual authenticated
navigation to that page shows **Forking in progress** and asks that no repository
changes be made until completion. This actual UI status supersedes inference
from the no-repository page, public404s, defaultbranchmain and emptyimportform.

The earlier single Createemptyrepository attempt was premature while the fork
was pending; its Failedtocreaterepository result remains preserved, not promoted
to a server-cause finding. No import/retry/deletion/duplicatefork or administrator
email was performed. Wait for actual fork completion, then verify branches and
push the qualified source. Do not infer a failed job from missing repository
availability alone. Installed-version routing differs from current-source
controller details; observed finalstatus is authoritative.

Sources: [official GitLab import controller](https://github.com/gitlabhq/gitlabhq/blob/master/app/controllers/projects/imports_controller.rb),
[actual fork progress](https://code.videolan.org/cam.marsollier/vlc/-/import).

### October13 owner-visible investigation of delayed fork

Problem class: asynchronous server-side repository creation with incomplete owner diagnostics. Actual signed-in Chrome inspection confirms import page “Forking in progress” with no changes requested; project overview “No repository”; Repository Settings “A default branch cannot be chosen for an empty project.” General Settings confirms project5462 and upstream fork relationship VideoLAN/VLC. No failure reason, job identifier, progress percentage or retry control appears on these inspected surfaces. These observations establish unavailable repository, not whether job is queued, executing or stuck.

Primary references: https://docs.gitlab.com/api/project_forks/ describes asynchronous background forks and import_status; https://docs.gitlab.com/administration/sidekiq/sidekiq_troubleshooting/ describes administrator queue/job/log diagnostics. https://docs.gitlab.com/user/import/troubleshooting/ recommends status/errors and server logs for prolonged import failures; its file-import specifics are not direct fork-cause evidence. Authenticated API navigation was already blocked by browser policy; do not extract session credentials or bypass it.

Decision: no blind initialize/restart/delete/new-fork workaround. Recommend owner administrator contact to inspect project5462 fork job/queue/errors; Cam owns contact and email remains forbidden to agents. Existing3hour monitor stays active. Actual server cause remains unknown. Private screenshot: work/story007-submission-preparation/fork-owner-investigation.png.

### October15 comparison distinguishes individual stall from general closure

At17:30UTC (11:30am Edmonton), fork5462 remains project200/branches404 and signed-in /-/import still says Forking in progress, about60hours after2026-10-13T05:28:35Z creation. Strict pinned-host SSH authenticates successfully as cam.marsollier. Two later VLC forks are demonstrably usable: jonata/vlc5465 createdOctober13T17:55Z and ReVuZ/vlc5466 createdOctober14T13:24Z; both branches APIs return200 with master and3.0.x. Public VLC MR10531 was createdOctober15T12:29Z;10530 at11:19Z. References: https://code.videolan.org/api/v4/projects/435/forks?order_by=created_at&sort=desc&per_page=10 ; https://code.videolan.org/api/v4/projects/5465/repository/branches ; https://code.videolan.org/api/v4/projects/5466/repository/branches ; https://code.videolan.org/videolan/vlc/-/merge_requests/10531 . Raw comparison receipt is ignored work/story007-submission-preparation/newer-fork-comparison-20261015.json.

Inference: this is an individual stalled/incomplete fork, not evidence of a current blanket fork/submission pause. No matching official VideoLAN AI-driven submission pause/service notice found in bounded search; absence of a notice does not establish a universal AI policy. Our patch content has not been pushed. Newer forks have master while this incomplete project retains main; this is a diagnostic difference, not proof of a branch-selection cause.

GitLab documents asynchronous fork background jobs (https://docs.gitlab.com/api/project_forks/) and administrator queue/log diagnostics (https://docs.gitlab.com/administration/sidekiq/sidekiq_troubleshooting/). Its LFS administration page documents one possible indefinitely stuck-fork failure involving excessive LFS objects (https://docs.gitlab.com/administration/lfs/); no LFS error/limit evidence exists here, so do not assert that cause or change limits. Without administrator job/log access, queue failure, storage failure and per-project/account restrictions remain unconfirmed. Recommend Cam request administrator inspection of5462/import job. No email sent and no restart/delete/duplicate/initialization performed.

### October23 ten-day fork and ticket investigation

General class remains asynchronous server job failure with unavailable owner diagnostics. Primary GitLab issue https://gitlab.com/gitlab-org/gitlab/-/issues/524293 and proposed MR https://gitlab.com/gitlab-org/gitlab/-/merge_requests/229470 explain a single-branch fork API response reporting preference-default main while repository creation is asynchronous. This supports treating defaultmain as insufficient evidence of wrong fork setup; it does not explain10days without a repository or demonstrate this instance has that bug. Do not present AI-generated review comments on that MR as confirmed failure behavior. Official asynchronous contract: https://docs.gitlab.com/api/project_forks/.

Local small check: fork5462 metadata200/branches404 onOctober23. Today's fork5477 master exists/branches200 at ed4ca71a3a18a9788c8c830eaae5389ee08c7692; separate5473 branches500 observed once and not retried. Mail acknowledgment headers identify support project1775 videolan/videolan-support, workitem533415, IID8252; only automatic acknowledgment found. Private reply/unsubscribe capability values are not copied into project records. Owner approved in-thread follow-up sentOctober23.

Decision: request precise administrator job/error/retry action on existing8252; no speculative branch setting, import restart, deletion or duplicate fork. Server logs/admin access remain necessary for exact diagnosis. Browser attachment failed with profile-in-use; do not claim authenticated UI was inspected. Existing monitor is PAUSED/old path stale; no unsanctioned process kill/profile reset/scheduler resume.
