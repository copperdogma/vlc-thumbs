# October30 wider fork recovery and contribution-policy scout

## Decision

Seventeen days without a repository is an individual stalled fork, not demonstrated normal queueing or a blanket submission closure. Recommend ONE owner-controlled delete/recreate attempt with All branches, retaining all local contribution material and the support-ticket trail. Do not claim guaranteed recovery or a diagnosed single-branch bug. No remote mutation or outgoing communication performed in this scout. New VideoLAN policy requires the human contributor personally submit contributions/reports/replies; agent prepares and explains only.

## Actual current observations

- Public project5462 still200, created2026-10-13T05:28:35Z, preference-default main; branches404. Anonymous API omits import status/error.
- Project5485 madera/vlc createdOctober27 has real master/3.0.x/feature branches (HTTP200). New forks continue to work.
- Same other contributor has project5482 at anabobillo3/vlc-deletion_scheduled-5482 createdOctober26T14:20:20Z, main/branches404, and replacement5483 at anabobillo3/vlc created14:22:29Z, master/3.0.x/feature branches200. This is observed replacement chronology; its actual failure reason and exact deletion actions are unknown.
- Scoped Gmail search finds only ticket8252 automatic acknowledgment and our October23 follow-up; no later response. No fresh email sent.
- Current browser transport launches successfully, but its profile is anonymous (import URL404 with Sign In link). Earlier signed-in user Chrome is not inherited. No authentication bypass/cookie extraction/new token.

Primary data URLs:
- https://code.videolan.org/api/v4/projects/5462
- https://code.videolan.org/api/v4/projects/5462/repository/branches
- https://code.videolan.org/api/v4/projects/5482
- https://code.videolan.org/api/v4/projects/5483
- https://code.videolan.org/api/v4/projects/5483/repository/branches
- https://code.videolan.org/api/v4/projects/5485/repository/branches

## Policy finding that changes the submission plan

Official doc/VideoLAN_AI_Policy.md was addedOctober21 in8a097e63e92bd95e36c31d66283bff73fee19f55 (commit API verified). Current canonical raw bytes match the official GitHub mirror. Policy permits AI assistance with human understanding/responsibility and MR disclosure, but explicitly excludes an AI agent submitting anything on the contributor’s behalf even with approval, including issues/MRs/comments/review replies/reports/proposals. AI disclosure belongs in MR description or label; it excludes AI advertising/coauthor credit in commit messages. This is a concrete upstream requirement, not inferred reviewer preference.

- https://code.videolan.org/videolan/vlc/-/blob/master/doc/VideoLAN_AI_Policy.md
- https://raw.githubusercontent.com/videolan/vlc/master/doc/VideoLAN_AI_Policy.md
- https://code.videolan.org/videolan/vlc/-/commit/8a097e63e92bd95e36c31d66283bff73fee19f55

Our fork predates that policy by8days, so policy publication cannot itself explain the initial stall. No evidence that VideoLAN identified/blocked this account for AI usage. The October23 emailed follow-up occurred after the new policy; we had not discovered it and should have. Do not send more agent-authored submissions externally; supply human-reviewable drafts and code explanations. Existing disposition story remains open; final human submission/replies replace autonomous external execution.

## Recovery options and applicability

1. Administrator retry/unblock of RepositoryForkWorker via existing8252: best actual diagnosis, but acknowledgment only for13days. Agent can prepare precise follow-up; human sends.
2. Delete empty remote fork and create fresh fork selecting All branches (GitLab default), rather than previous Only default branch. Local contribution commits are not on the remote. First delete normally schedules deletion/restorable retention; do not assume this is a cancel-job control. Verify whether same slug is released; choose a fresh slug if needed. Do not immediately purge solely to skip retention. Owner action required before any real deletion; this scout is options only.
3. If a fresh fork also stalls, stop retries and have administrator inspect account/namespace/job/storage failure. No account/IP/namespace policy evasion, repeated duplicate projects or import-URL tricks.
4. A separate public downstream repository can preserve/share code, but it does not create a VideoLAN MR or establish acceptance. Not a replacement for this story’s disposition contract.

Official workflow/retention:
- https://docs.gitlab.com/user/project/repository/forking_workflow/ : All branches default; Only default uses single-branch/no-tags.
- https://docs.gitlab.com/user/project/working_with_projects/#delete-a-project : initial pending deletion, instance-specific retention; immediate deletion separately destroys related records.
- https://docs.gitlab.com/administration/sidekiq/sidekiq_troubleshooting/ : admin queue/job/log diagnostics.

## Broader discussion search

Bounded searches covered VideoLAN forum, developer/commit mailing lists, VideoLAN AI policy, generic GitLab stuck forks and cancel/delete/recreate documentation. No published VideoLAN blanket fork/submission shutdown found; current usable newer forks contradict a current blanket technical freeze. GitLab forum report https://forum.gitlab.com/t/stuck-at-forking-in-progress/116532 describes empty-shell projects and RepositoryForkWorker failures in2024: symptom analogy only, not this server’s diagnosis. External contributor grievances surfaced but are not primary evidence of this account’s treatment and were not adopted. No proprietary server diagnostics are available.

## Executed owner-approved recovery and new server evidence

At16:50UTC human completed login in accessible browser; exact cam.marsollier identity confirmed. Old5462 normal deletion dialog enumerated zero issues/MRs/forks/stars, seven-day recoverable pending deletion with finalNovember6. Confirmed scheduled deletion only; old project now cam.marsollier/vlc-deletion_scheduled-5462. Existing Fork button still pointsold; normal documented new-fork form /videolan/vlc/-/forks/new remains usable. ONE public replacement with Allbranches and personalnamespace created16:51:20Z as5493 at original /cam.marsollier/vlc.

Authenticated API navigation now works with ordinary browser session (no token/cookie extraction). GET /api/v4/projects/5462/import shows import_status:none and persisted import_error Unable to save project / PG::UniqueViolation / project_authorizations_pkey / duplicate owner-authorization row. Concrete server failure is established; whether original fork creation or the earlier failed empty-init wrote this error is not established. Do not infer active queueing from oldspinner. Replacement5493 shows import_status:started, import_error:null and correlation_id01M66VJ5DMKEXWWVNAQMK1AMC9. Early branches404 is pending, not a failed successor. Exact error search yielded no useful primary fix; do not invent database repair from user account.

Project deletion/refork is account/repository administration, not a contribution or review submission. No MR/report/reply sent; human-only submission policy remains. Any later support update should describe the actual database failure and new5493 separately and be sent personally by Cam.

October30 16:52:27UTC — Replacement5493 importstatusfinished/noerror; authenticated UI explicitly Theprojectwassuccessfullyforked and Up todatewithupstream. Independent public branches200:3.0.x b9322dfcf0de27219b964dcb0f8ffd7414908037; master5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09. Defaultmaster, forked_from_project435. Recovery PASS in~67seconds; this does not retrospectively prove singlebranch selection caused oldfailure. Old5462 recoverable scheduleddeletionNovember6; source/build/localinputs untouched. No MR/push/email. Screenshot docs/evidence/story-007/fork-recreated-20261030.png.
