---
id: "007"
title: "Submit VLC timeline previews and obtain upstream disposition"
status: In Progress
priority: High
ideal_refs: [ideal:req:previews, ideal:req:evidence, ideal:req:media-integrity]
spec_refs: [spec:1, spec:5]
adr_refs: [adr-004-upstream-preview-integration]
decision_refs: [docs/decisions/adr-004-upstream-preview-integration/adr.md, docs/scout/scout-001-vlc-submission-process.md, docs/evidence/story-005/current-source10-final-verification.md, docs/evidence/story-006/validation.md]
depends_on: ["002", "004", "006"]
parent_story: "005"
category_refs: [spec:1, spec:5]
architecture_domains: [upstream-integration]
eval_refs: []
---
# Story007 — Submit VLC timeline previews and obtain upstream disposition

## Goal

Submit the prepared timeline-preview source contribution through VideoLAN's
GitLab process and own the entire review cycle until maintainers explicitly
accept or reject it. Monitor CI and discussions, respond thoughtfully, implement
requested corrections and validate affected behavior efficiently. Opening an MR
is an intermediate step, not completion. Cam requests this dedicated story on
2026-10-09 and prohibits other repository work until upstream disposition.

## Ownership and current substrate

This child owns Story005 Phase3. The new ID is explicitly requested and isolates
an external asynchronous review/decision boundary from completed local
implementation/qualification; it does not fragment the product feature. Parent005
stays open until this child records disposition. Depend on completed002/004/006,
not parent005 completion, to avoid a dependency cycle. No duplicated Phase3 executor.

Tracked source10 package: `patches/vlc-master/contribution-series-source10/`,
thirteen patches/72 paths, base `2e358f3098c2f2b7621d1dc568de8b61ad786322`,
combined tree `b7c0f24e442c35a57bb108d56b801fd05b624943`. Story006 is Done and
landed on project GitHub main at `1bf2374f73ccf126f33a2ba7b71cde61faca89e6`.
[Fresh process scout](../scout/scout-001-vlc-submission-process.md) reports latest
master `428110923693cd391229f8b6afce4e61debc04f0` on October9; refresh it at
execution. The October 13 qualification is historical. The October 30 refresh reconstructs the preserved source10 package, verifies its exact tree, and rebases onto `5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09`. Current exported successor head is `dd50411dad2b8c05144acbf0e7c63fb9150e0120`, tree `212c081ca9eb566a65b3979d272a788ae52653ea`; 16 patches / 70 paths. The final fixture-only warning treatment passes its affected compile and five lifetime cases. Bounded fresh build/unit/archive checks pass at the recorded scopes; the registered CLI quit gate remains blocked, and complete distcheck is unqualified. The replacement fork is ready and account sign-in is verified. No MR yet. See [current refresh](../evidence/story-007/upstream-refresh-20261030.md) and [historical qualification](../evidence/story-007/current-master-validation.md).

## Acceptance Criteria

- [x] **Current source branch:** Refresh canonical master, inspect intervening
  changes and construct an isolated source-only submission branch with the
  reviewed commits/real author identity. Verify exact application/tree and full
  target diff. Preserve the qualified package/apps/evidence; exclude project
  journals, private media, binaries and ignored harnesses.
- [ ] **Proportionate qualification:** Reuse evidence only for unchanged inputs.
  Resolve actual integration defects and run affected build/tests; retain written
  upstream gates including build, warning review, make check and complete
  distcheck when applicable. Disclose unavailable platform/reader/measurement
  coverage and unresolved shutdown causality. No repeated marathon by default.
- [ ] **Actual upstream MR:** Push the prepared branch to the contributor's
  VideoLAN GitLab fork and open a reviewable MR targeting current master through
  official workflow. Record public URL, fork/branch, base/head, commit mapping,
  concise rationale, review map, reproducibility and scoped validation/limits.
  A local draft, fork push or design-feedback draft alone does not satisfy this.
- [ ] **Continuous shepherding:** Keep an actionable review ledger with comment/
  CI link, revision, request, response/change, validation and resolution status.
  Monitor new feedback and pipelines; answer and implement scoped corrections
  until resolved. Concrete architecture changes require revisiting ADR004;
  material scope loss or new legal/rights attestation requires Cam's decision.
- [ ] **Reliable monitoring:** Use the separate GPT-6 Luna Low checker every three hours once resumed; it is currently paused. It is intended to watch fork readiness first, then the submitted MR,
  reporting noteworthy changes back to this coordination chat. Check MR
  state, discussions and relevant CI; act on meaningful changes and report
  decisions, failures or required human input. Stay quiet when unchanged. Avoid
  personal pings and unnecessary rebases; request review again after a week of
  silence per official guidance. Record last check and next check. Silence,
  failed CI, changes requested or waiting for a maintainer remains open work.
- [ ] **Explicit terminal disposition:** Record maintainer acceptance or rejection
  with permanent URL/comment, timestamp and exact revision. A merged MR is
  acceptance evidence. An unmerged explicit maintainer acceptance may qualify
  only if unequivocal and final, with accepted scope/revision and remaining merge
  mechanics clearly distinguished; a label alone or informal interest is not
  enough. Rejection requires an explicit maintainer decline/reason, not merely
  bot closure, stale status, silence, or our own withdrawal.
- [ ] **Complete contribution outcome:** If maintainers require multiple MRs,
  record each and keep this story open until the full proposed feature has a
  definitive acceptance/rejection outcome. Accepted prerequisites alone do not
  mean the preview feature was accepted. Mixed outcomes require explicit scope
  accounting and Cam's decision where feature scope changes.
- [ ] **Disposition closeout:** Resolve outstanding obligations, summarize accepted
  changes or rejection reasons and record reusable conventions. Close this story
  only after the terminal criterion above; acceptance and rejection both satisfy
  the requested process endpoint, but rejection is never reported as feature
  adoption. Reconcile parent005 Phase3 truth and stop monitoring only after
  disposition. Do not automatically begin another repo task.

## Exclusive repository focus

Until explicit acceptance or rejection, all other repository work is deferred:
bookmarks, history/privacy features, sparse-keyframe fallback, opportunistic
cleanup, unrelated refactors and new feature stories. Necessary integration,
CI fixes, reviewer-requested changes, documentation and validation belong here.
Waiting on upstream is not permission to fill time with unrelated work. Do not
remove the hold because an MR was opened, local tests passed, feedback was
answered, a time budget expired or maintainers went quiet. Cam may explicitly
change this sequencing rule; otherwise preserve it across resumed sessions.

## Approach Evaluation

- **One coherent MR:** Uses the current documented thirteen-commit order and
  existing review map. Lowest initial restructuring cost; inspect upstream
  application and actual feedback before selecting submission packaging.
- **Linked smaller MRs:** Useful if concrete upstream dependencies or maintainer
  requests justify it. Track dependency order and final feature disposition;
  cannot mark complete on partial prerequisite acceptance.
- **Draft design MR:** Only when a concrete unresolved architecture question
  prevents a reviewable source proposal. Must be labeled and subsequently
  completed; does not satisfy submission readiness or terminal disposition.

Reuse canonical source package, existing messages, scoped qualification, scout
and ADR004. No AI-capability eval ladder applies: human review plus source/CI
and affected native behavior define this external validation contract. An LLM
cannot establish upstream acceptance; only observed upstream evidence can.

## Tasks / Plan

- [x] Inspect current master/application and prepare isolated integration branch.
- [x] Resolve account/fork access through normal authorized login flow; hand off
  unavoidable human security/account actions without bypassing them.
- [x] Construct real commits from the canonical series and reviewed messages;
  inspect author/license/source diff and run proportionate changed-input checks.
- [ ] Open official MR with concise description and attach its URL to this chat.
- [ ] Create `docs/evidence/story-007/review-ledger.md` with revision/CI/discussion
  and disposition evidence; approved three-hour Luna Low checker is currently paused and has a stale path/fork target; do not describe it as active.
- [ ] Respond to each actionable request, fix scoped issues, update evidence and
  let upstream CI run. Reuse unchanged proof rather than restart broad campaigns.
- [ ] Track all linked MRs if splitting becomes necessary.
- [ ] Capture explicit acceptance/rejection; reconcile parent and final report.
- [ ] Validate records, stop monitoring at disposition, close via mark-story-done.

Story creation does not itself publish an MR or start automation. Under the current VideoLAN AI policy, Cam must personally submit the MR, reports and reviewer replies. Agents may prepare these and implement scoped corrections. No agent-authored remote submission or unrelated outbound messages or rights claims.

## Workflow Gates

- [ ] Build complete: submission/revision work and terminal upstream disposition
  recorded, with no remaining scoped review obligations.
- [ ] Validation complete: applicable checks and upstream outcome evidence inspected.
- [ ] Story marked done via `/mark-story-done` after explicit acceptance/rejection.

## Current execution / previous blocker resolution

The upstream fork blocker is resolved: replacement5493 completedOctober30 with real master/3.0.x branches; old5462 remains scheduled forNovember6 deletion. The dedicated SSH key authenticated previously. No MR has been submitted. Current source/build readiness is being reassessed after the project move: the old ignored work/source/build tree is not at the new checkout, so October13 results remain predecessor evidence only.

## Current refresh plan — approved owner request October30

Cam asks to refresh/rebase and run applicable tests, and check whether thumbnail support has landed. This is continuation of the existing approved submission-preparation scope, with no new feature or architecture change authorized.

1. Read-only scout current canonical master, known macOS thumbnail MR7493/core issue29393 and competing/landed work. Distinguish native macOS hover previews from Qt/artwork capabilities. If upstream now supplies the feature, recommend dropping or narrowing the local series rather than blindly porting it.
2. Inventory/recover original submission source/dependencies/evidence through known paths. Preserve dirty project checkout, tracked predecessor package, apps/media and historical failures. If exact old14commit objects are unavailable, reconstruct only with explicit successor provenance, never claim recovered oldhash identity.
3. Establish a clean isolated source branch and pin master. Rebase/apply the actual reviewed series, drop prerequisites already upstream, resolve only concrete integration conflicts, inspect the entire resulting diff and current submission requirements.
4. Run proportionate current-input normal build/registered checks, affected helper positive/protocol checks and conventional distribution checks when build substrate/resources permit. No extended native hover/VoiceOver/performance campaign. Use affected native smoke only if actual UI behavior changes; disclose unrun coverage. No redundant tests or manufactured green results.
5. Review/revise current evidence and human-reviewable submission package. Human personally submits MRs/reports/replies under October21 VideoLAN policy. No upstream post/email/MR, unrelated work or cleanup in this refresh.

Delegation: lower-cost read-only upstream scout; SOL6.1medium source/build worker; root owns planning, integration decisions and final validation judgment. Source mutation has one designated writer after the scout/inventory determines actual applicability. Native runtime/app installations are not implied by source tests.

## Architectural Fit / Files to Modify

ADR004's current native/helper/cache mechanism and spec:1/5 are retained. A new
architecture decision is unnecessary for creating this external review story;
review-driven material changes must update applicable decisions. No product
coverage or integrated bookmarks/root PASS is established here.

- This story, parent005 Phase3, `docs/plan.md`, state and generated graph/index:
  single owner and exclusive focus; parent005 is a large historical record,
  so add concise current links rather than rewriting its history.
- `docs/evidence/story-007/`: MR/revision/CI/review ledger and final disposition.
- Current contribution package and isolated upstream source branch: only actual
  integration/reviewer changes, with matching hashes and affected proof.
- Installed app/media, historical packages/raw failures and other worktrees:
  preserve; no cleanup or release is implied.

## Redundancy / Removal Targets

Retire duplicate parent/child Phase3 execution instructions by routing parent005
to this story. Preserve historical evidence. At disposition stop the monitoring
mechanism so no stale recurring follow-ups persist.

## Work Log

20261009 — Cam explicitly requests a new MR story with acceptance/rejection as
its endpoint and continuous feedback handling; all other repo work is deferred
until that outcome. Created Pending from current qualified substrate and fresh
process scout. No MR, upstream contact, automation, implementation, commit or
push performed during story creation.

20261011 — Cam explicitly authorizes upstream submission under his name and asks to be told if account creation is needed. Confirmed existing contributor metadata Cam Marsollier <cam.marsollier@gmail.com>. Root uses build-story with the existing written plan; this authorization covers submission, scoped revisions and later monitoring. SOL6.1-medium worker prepares isolated source-only commits/current-master comparison; root owns external actions. Browser shows VideoLAN GitLab sign-in, no authenticated account; human login/account question pending while preparation continues. Existing project dirt, package/apps and source snapshots preserved.

20261011 — Isolated source branch prepared under work/story007-submission-source. Thirteen canonical commits under Cam Marsollier <cam.marsollier@gmail.com> reproduce original exact composition before clean rebase onto current master0fddbac8470745c5530e0b37ca0d5b581817ac68. Head360cd225bd33a08c71aec64c4e84dbcd509ed433; treefad7229563e59a6458f5e7029095b8c34603e14c;72paths. Seven overlapping upstream build/Main paths inspected; actual feature implementations/tests unchanged, but new sections/dead-stripping and native dependencies prevent whole new-base build inheritance. Root still requires focused normal build/check/distcheck before claiming current-base pass. Receipt/report in work/story007-submission-preparation. No app/build/push/MR or automation.

20261011 — Actual GitLab browser alert and Cam’s confirmation establish account pending administrator approval. Status Blocked. Cam will check hourly and tells root to chill; hold further execution/polling until approval/continuation. Source commits and local MR draft retained, no alternate account or administrator contact. Story remains unfinished; all unrelated repo work remains deferred.

20261012 — Cam reports signed in and explicitly resumes rebased build checks/submission. Root verifies actual Chrome authenticated identity cam.marsollier; account approval blocker cleared. Public default-master-only fork created at https://code.videolan.org/cam.marsollier/vlc (project5462), repository initialization still pending in browser. No MR yet. SOL6.1-medium builder rebases cleanly to canonical392bc1d0abdb7396b6c97fef206efa1d23868e19 with head085acbf79ae2a15e928da647a589b4773ee5f92c/tree3fa662c19ce98931dcbe9a5300d909b7dd448f09; actual13commits preserved. Fresh configured build/registeredcheck/distcheck work uses independent owned directories; prior native/helper scope retained rather than repeated. GitLab has0SSHkeys; root asks per-action confirmation to register existing publickey for authentication only with90day expiry, no grant yet. Requested3hour verylowcost checker will start after MRcreation; separate LunaLow scheduled checker preference pending because thread heartbeat uses parent model.

20261012 — Cam gives action-time permission to add existinggithub_rsa.pub and explicitly selects separateLunaLow checker. Actual key2955 registered asAuthentication only, expires2027-01-10; fingerprint matches agreedkey. Strict task-local host trust matches officialinstancefingerprint. Server accepts publickey but encrypted privatekey cannot sign inBatchMode/nativeKeychain route; humanTerminalssh-add unlock requested without sharingpassphrase. Cron vlc-upstream-mr-feedback createdPAUSED withverifiedgpt-6-luna/low/3hour schedule and correctprojecttarget; enableonlyafteractualMR. Forkrepository stillabsent afterboundedrecheck, pendingremoteinitialization/sourceunknown. No MR yet.

20261012 — Rebased normalbuild139.58s/package62.44s PASS; zerofeaturepath/changedlinewarnings. Fullmakecheck FAIL15integrationtests while266macOScases (265pass/1skip) and25modulespass. Actualnm proves currentDarwindeadstripdropsdynamicallydiscoveredmocktable. Twoflagnegativewitnessespreserved; wildcardexportroot passesrealEOF3.016s andnofixturecore1s withoutnewwarning. Rootreviewed4lineDarwin-onlytestMakefilefix committedas14th8ef6bd094a0c48727e155417a4a07aad617680c3/tree85cdddd06a1324ca43e620d40b76f54f4d023e39. Productiondeadstrip unchanged. Correctedfullcheck/distcheck underway; firstfailedgate remainsfailed. No runtimecampaign or oldapp/sourcechanges.

20261012 — Cam rejects administratoremail and asks correctnessaudit. IndependentSOL6.1medium read-only review confirms canonicalfork/account/transport/keyregistration, but cannotinferfailure frommissingrepo. Rootnavigates documentednormal /-/import page: actualForkinginprogress. Earlieroneempty-initattempt premature;failedresponsepreserved, noserverfaultclaimed. Noemail/importrestart/newfork/deletion. Waitforcompletionwithno repomutation. Correctedfullcheck green167.77s; completecurrentdistcheck002 progressingafterownedshallowmetadatarepair.

20261013 — Fresh current-master normal build/package, corrected full registered check and complete conventional distcheck PASS. Fourteen commits/72 paths; submission clean; two retained positive helper fixtures and13 actual protocol cases per normal/archive helper pass. Prior77 remains prior-input evidence only. Inherited test-shell warnings and earlier failed witnesses disclosed. Root receives source writer handoff. Fork remains importing; SSH unlock pending. Approved Luna Low three-hour checker ACTIVE for fork readiness then MR feedback; no email or remote source publication.

20261013 — Fresh dedicated Ed25519 key created at Cam’s request, mode0600/no passphrase; explicit action-time registration approved. Actual GitLab2958 fingerprint/scope/expiry verified; strict-host SSH Welcome @cam.marsollier exit0. Old key unchanged. Public branches still404; no remote push/MR/email.

October13 4:59pm Edmonton — Cam requests another24hours of waiting; no rush. Hold submission/escalation until2026-10-14T22:59:48Z (October14 4:59pm Edmonton). Approved Luna3hour checker records quietly during hold and reports once on first check after it ends; no email/fork mutation, all unrelated work deferred.

October15 — Cam explicitly approves emailing the fork report to videolan@videolan.org for administrator routing. Gmail confirms SENT from cam.marsollier@gmail.com, message/thread1a140ac614d7fa8b, subject Stalled VLC fork cam.marsollier/vlc (project5462). Report contains public fork identity/status and failed early initialization disclosure; no credentials/private source/attachments. This scoped approval supersedes earlier no-email rule for this report only. Await reply; no upstream push/MR or administrator resolution claimed.

October23 — Owner reports October17 ticket8252 acknowledgment and requests renewed investigation. Cam Gmail search/read confirms only automatic acknowledgment in ticket thread1a14981f32a36961; no later response found in scoped search. Live public project5462 returns200/defaultmain; branches404. New fork5477 createdOctober23 has readable master (HTTP200);5473 branches returned500 once, not generalized. Therefore owner fork remains individually unavailable after10days; server cause unknown. Browser tool cannot attach because its shared profile is already in use; no current authenticated UI proof and no browser process/lock changed.

Repository now exists at /Users/cam/Documents/Projects/vlc-thumbs; old nested path is absent. Existing monitor config is PAUSED and targets old path. No evidence of current continuous monitoring; preserve paused status rather than infer authorization to reverse an unknown pause. No ignored work directory found at new checkout; prior build evidence remains historical, not freshly reverified.

Cam explicitly approves one ticket follow-up. Gmail SENT message1a16a13956e92603 in existing ticket thread1a14981f32a36961, asking administrator to inspect RepositoryForkWorker queue/failure and advise on supported retry. No new ticket, fork mutation, push/MR or additional build campaign.

## October30 upstream policy correction

Official VideoLAN AI policy addedOctober21 requires human personal submission of issues/MRs/replies/reports even with AI assistance. Earlier autonomous external-execution permission describes owner authorization, but does not establish compliance with that new upstream rule. Root may prepare, review, explain and validate locally; Cam must understand/vouch for the proposal and personally send upstream submissions/replies. Keep AI assistance disclosed in MR; audit commit-message restrictions before eventual submission. Story remains open through explicit disposition. See ../research/story-007-fork-recovery-and-policy-20261030.md. No deletion/refork action is authorized by the owner’s options question alone.

October30 approved recovery executed: old5462 scheduled forNovember6 deletion/recovery retained; zero issues/MRs. ONE new fork5493 at originalURL, Allbranches selected. Authenticated importstatusstarted/noerror, readinesspending. Old5462 saved duplicate project_authorizations_pkey database failure discovered; exact trigger unknown. No human-required contribution submission performed.

October30 16:52:27UTC — Replacement5493 importstatusfinished/noerror; authenticated UI explicitly Theprojectwassuccessfullyforked and Up todatewithupstream. Independent public branches200:3.0.x b9322dfcf0de27219b964dcb0f8ffd7414908037; master5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09. Defaultmaster, forked_from_project435. Recovery PASS in~67seconds; this does not retrospectively prove singlebranch selection caused oldfailure. Old5462 recoverable scheduleddeletionNovember6; source/build/localinputs untouched. No MR/push/email. Screenshot docs/evidence/story-007/fork-recreated-20261030.png.

October30 — Owner requests current-master rebase/test refresh and new thumbnail-support scout. Existing approved Story007 plan resumed after successful fork recreation. Parallel read-only source recovery and upstream applicability packets launched; no source mutation released before applicability/substrate evidence. Actual project checkout is /Users/cam/Documents/Projects/vlc-thumbs; old ignored work absent here. Historical October13 gates retained at exact earlier revision, not current-master proof.


## October 30 bounded source refresh — handoff

Completed owner-requested current-master/feature scout, exact-tree reconstruction, rebase and focused qualification through SOL 6.1 Medium source/build delegation. Current canonical master still has no native macOS seek-hover thumbnail implementation; MR !7493 remains open. Dropped already-upstream OpenGL/header changes, resolved test-support conflicts, refreshed dependency/Metal instructions and fixed the new upstream audio-output test's missing compatibility linkage.

Preserved [15-patch successor](../../patches/vlc-master/contribution-series-20261030/README.md) independently replays to the exact tested source tree. Source is clean; predecessor package and unrelated checkout dirt are preserved. Fresh app/helper/macOS/core/archive checks pass at their stated scopes. The normal CLI quit check stalled in SAP join during medialibrary cleanup and was stopped; origin remains unproven. No full make check/distcheck pass, fresh desktop/VoiceOver/performance campaign or upstream publication is claimed. At that stage seventeen test-stub warnings were disclosed; the subsequent warning cleanup is recorded below. See [refresh report](../evidence/story-007/upstream-refresh-20261030.md) and compact receipts. Story remains In Progress through human submission and upstream disposition; monitoring remains paused.


## Owner-authorized warning closeout and project landing

Cam requests ownership judgment, scoped fixes and validation/check-in/push. Our link-only test fixture owns the 17 diagnostics: document its intentionally absent GUI/media behavior and scope only the irrelevant property diagnostics to the empty shell. No fake unused methods, production suppression or new tests. Fresh affected compile/five lifetime cases pass; source16 tree is replay-verified. Independent artifact review's stale-ledger and promoted-relative-path findings are corrected. Current validation/landing details are in [refresh-closeout-validation](../evidence/story-007/refresh-closeout-validation.md). This local preparation slice may land while Story007 remains open through human submission and upstream acceptance/rejection; the CLI shutdown and full distcheck limitations are retained.
