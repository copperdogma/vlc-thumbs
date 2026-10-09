# Story005 reviewer-improvement loop

## Authorized scope and timing

Cam authorizes up to8hours to streamline contribution code without hurting readability, meet/exceed submission standards, improve reviewer confidence/ease, find bugs/regressions and retain only necessary high-quality tests. Root scouts/plans/coordinates; SOL6.1medium builders implement. No submission/contact/commit/push/publicbinary/installed-app update/otherproject changes. New installation from prior request remains untouched.

Start2026-10-07T01:32:48Z (Oct6 19:32 Edmonton); hardstop2026-10-07T09:32:48Z (Oct7 03:32 Edmonton). Hourly strategy checkpoints anchored02:32:48Z,03:32:48Z,...08:32:48Z, with hardstop overriding09:32. Stop earlier on convergence, minor-only returns, material blockers or nonconvergence. No recurring automation. Laststrategycheck=start; next02:32:48Z. Activeiteration and dependencywaits distinguished; elapsedwalltime cannot extendharddeadline.

## Mode, materiality and ownership

Strict-until-clean over the exact59 publicsource paths in revision10 manifest, fourpatches and13publicwrapperartifacts. Shared ADR/spec/story/readiness/buildrunbook/looprecord are coordinated root docs; docs reviewers find-only. Scope includes contribution's existing FFmpegdiffs, not a general FFmpeg/VLC cleanup. Dedicated existing candidatecheckout work/upstream/vlc-master-story005-candidate owns implementation, preservedbaseline work/upstream/vlc-master-story005 untouched; reproductioncheckout used only buildowner when released. Keep normal-contrib helper/protocol4/cachev5/nativecontext contracts and actualpreviewfour-surfaces/NAS/track/freshness behavior. Changes requiring architecture replacement are expansion candidates unless a bounded contained local change is independently justified.

Material: concrete bug, regression/security/data-loss, build/test/contract/evidence invalidation; test coverage deletion/consolidation or production refactoring receives fresh applicable verification even when expected equivalent. Readability improvements must remove real duplication/indirection or clarify ownership, not line golf. Do not chase cosmetic nits or optimize test counts. Unrelated upstream discovery ownership defect and exact shutdown-causality gap remain disclosed, not fixed under this loop. Non-green baseline/minimal distcheck and unavailable platforms/reader cannot be calledgreen.

Freshagents each fullround, singlepass, no nestedagents/loops. Sharedmeaning findings classified byroot. Materialfixresets originalboundedfullscope onlywhileconverging; two same-class materialpasses/two non-narrowing resets trigger systemic-audit/nonconvergence stop. Stopcleanverifier ratherthanfill8hours. Follow-through authorized directly byCam; no repeatedapproval for in-scope improvements.

## Baseline and first-round plan

Revision10 treecc0ec69e8be5ba2e60ccae6ea095b471b500a6ff at2e358f3098c2f2b7621d1dc568de8b61ad786322.59files +9981/-56; filenameclassification4559production/build/XIB,5035tests/fixtures,387docs. Currentqualifiedruntime producttree8ec1cdec6939c67eeb6bef0ff1bb035c168d0592 differs onlylater test/distribution/docs changes. Preserve source snapshots/existingindexes/qualifiedapps and priorfailures beforemutation. FreshGitstatusworks;17.12GiBfree,1GiBreserve. Priorcompletefile review/receipts remain historical; newchangedpaths mustrequalify.

Round1 find-only shards,20min pertechnicalworker/15minideation; no runtime:

| Worker | Scope |
|---|---|
| r1_helper_audit | Chelper/FFmpegidentity+admission+directtest applicability |
| r1_service_audit | service/worker/cache/scheduler correctness and simplification |
| r1_native_audit | atomiccontext/player/hover/settings/native ownership |
| r1_test_audit | all contributiontests/support/generators contractmap/redundancy/maintainability |
| r1_submission_audit | primary standards/build/license/publicsubmission gap audit |
| r1_reviewer_ideation | bounded reviewstructure/assurance/reproduction brainstorming |
| r1_build_baseline | exactsource/package snapshot, Gitbaseline/buildinventory/installpreservation |

Model rationale: userrequestsSOL6.1mediumbuilders, retained for allfirstpassworkers; these are semantic/code/build judgments, not just mechanical scans. Root owns findings/disposition, architecture/coverage and acceptance.

## Finding ledger

Pending firstpass reports. No source edits authorized to workers yet. Everyfinding willbe accepted/rejected/follow-up with evidence, materiality and nextcheck. Proposals do notconstitutefacts or automatic scopeexpansion.

## Success and closure evidence

Measured reduction of avoidable code/test/review complexity; standards checklist linked to primarysources; compact reviewentrypoint and logicalpatchmap; distincttest-risk coverage map with justifiedkept/deleted cases; exactnewsource/packagefreeze and privacy/license/provenance checks; changedhelper/native/test/build paths rerun with qualified original/nativeevidence reused onlywhereunchanged. Finalfullround no materiallocalfindings; originalshutdown/distcheck/reader/platform limits retained. Finalreport states before/after source/tests/patch counts and remainingacceptance risks, no promise of upstreamendorsement.

## Round1 disposition and implementation

Freshfind-only shards completed; nativecontext/UI shard no materialfinding. Rootclassifications:

| Finding | Disposition/materiality | Action/proof |
|---|---|---|
| Terminalerror callback overwrites nestedreplacement hoverstate | accepted material correctness | Commit satisfiedstate beforecallback, re-enterfreshpump gates; ONE deterministicregression. Fixed selectorpasses, isolatedoriginalservice objectfails same testat5s; fullsuitepending |
| Trim/helpermultirequest tests accept error-only replies | accepted material validationgap | Sharedready/count/IDs/ok/payload validator; originalASTacceptsall3 fakeerrorcases, newrejectsall3; normalchangedhelper77/fullfixtures pass |
| Duplicatepurehover registration in2bundles | accepted testquality consolidation | Keepone isolatedregistration; alluniqueproductionhelper assertions retained |
| Cocoa-only trackinggeometrytest copieslogicwithoutproductioninstaller | accepted nonproductiontestdeletion | Remove17linemethod; no newNSWindowharness. Actualnative4surfacegeometry proof remains distinct |
| DeadSelection.requested/twotemporaryparserbuffers | accepted semantic-neutral codecleanup | Removeunusedfield/initializer andparse alreadyboundedNULterminatedspansdirectly;77helperchecks passnewnormalbinary |
| Publicready-to-submit wording contradicts explicitrequiredchecks | accepted material truth/standards | Preparedformaintainerreview;submissionchecklistincomplete. No waiver/CIgreen inferred |
| Crucial attributionlink escapespublicpackage | accepted material reproducibility/navigation | Consolidated sanitized in-packageLIMITATIONS; preserveeightunchangedsourcepins/actualfault/unprovedcause |
| Repeateddiary-shapedreviewprose | accepted reviewerburden | Shortfrontpage/396worddescription/ownershipsketch/testmenu; rootclaimcheckpendingfreeze |
| PTSnonnull vsbest-effortDTS provenance | follow-up hypothesis, notprovenvalidfilebug | PinnedFFmpeg source+scopeddecoderprobe:9existingfiles25keyframesequal; syntheticmetadata yieldsdifferentPTS/best. Intendedvalidfiletimeunproved, no speculativetimestamprejectpolicy |
| FFmpegENOMEMgenericdecode/read classification | follow-up minor low-priority consistency issue | Existingwatchdog/resourcebounds effective, no demonstratedlimitescape. Deferallocatorinjectionmachinery/semanticchange; disclose ratherthanaddingtestframework |
| Broadnativecontext/cache/decoder rewriteforfewerlines | rejected unsupportedcost/benefit | Existingdefensescoverdistinctcontracts; no demonstratedsmallersafealternative |

StaticuniqueXCTest count now284 (266main+7context+11hover), includingnewserviceregression. Original288countedexecutions was253other/upstream +31uniqueaddedfeature +4duplicatedpurehover; it wasnot288newtests. Currentcountreduces4duplicateexecutions and1nonproductionmethod, adds1meaningfulregression; assertcountfloors3410/40 wereassertionswithintwomonolithicmethods, notmethodcounts. No scenario-counttarget.

## Early strategy checkpoint —2026-10-07T01:45Z

Verdict alignedandprogressing, but reviewability requires meaningfulboundaries, notlinegolf orlargeclaimgreenlabels. Usefuluncertaintyimproved: a realreentrancydefect andfalsepositivevalidationgap nowhavesmall fixes/counterfactuals; true testinventoryeliminates inflatedtestcountinterpretation. Wouldchoose boundedcontracts/sourceauditagain. PreserveNAS/freshness/selectedidentity ratherthanrewritehelper/nativearchitecture withoutnewproof.

Establishedalternative changesmechanism: self-contained logicaldependentchanges and progressive reviewentrypoints insteadonegiantfeaturediff pluschronologicalevidencediary. Freshprimary generalpractice sources https://google.github.io/eng-practices/review/developer/small-cls.html , https://llvm.org/docs/CodeReview.html , https://www.kernel.org/doc/html/latest/process/submitting-patches.html support relatedtests/buildablelogicalpatches. Thesearegeneral practices, notVideoLANpolicy. Nativepreparserreplacement remainsa differentarchitecture alternative, but recentADR004 comparison assumptionsstillapply(movie-time/eligibility/selectedtrack/retained-open); nonewlocalcounterexample justifiesredoingthatarchitectureexperiment now.

Decision continueclassifiedfixverification andshortselfcontainedreviewpackage. Boundednewdecompositionscout checks whether service/cache/worker substrate can precede context/UIactivation WITHOUTstubs/featureloss, correcting oldcoherenceassumption onlyif actualdependencies andintermediatebuildproof supportit. Smallestcomparison: exactsequentialapply/finaltreeidentity plus normalintermediatecompile/link, versusretain0003withfileitinerary. No intermediates claimedbuildableyet. No moretestframework/captureharnesses, cleanproxyshutdownruns, unsupportedplatformpromises or unrelatedVLCrepair.

Hourlyoperatorcadenceremainsanchored02:32:48Z; earlycheckpointdoesnotresetnextdeadline. Sourcefreeze/reviewpackage regeneration andfreshfullstrictverificationround follow materialchanges. Stopfirstnonconvergence/blocker orcleanround;8h isceilingnotworkquota.

## Validation and second-pass release —2026-10-07T01:49Z

Normal candidate plugin/helper build succeeds after using the already-installed pinned normal tools PATH (initial missing-automake failure preserved). Full native suite:284unique executions,283pass/1optional ENOSPCskip/0fail; helper77pass. Same regression with preserved original service object fails as expected; fixed object passes. Exact receipt reviewer-improvement-validation-001.json (SHA5254191dcdffebacc7d4225b85f7d55ccacc84c842e9f69b14d91c771f13d339). No GUI/new-app qualification claimed.

Fresh R2 find-only workers released for helper/contrib/directtests; service/cache/worker/scheduler/contracts/tests; and remaining native/context/UI/buildlists/tests. Original59path scope retained; no extra production simplifications planned. New split owner implements scratch five-part series and conditional normal intermediate build proof; candidate source remains frozen. Two-way native split would reduce largest native additions from6066 to4598 (24.2%); three-way adds a proof boundary without reducing largest. Adopt only after actual intermediate normal build/test and exact finaltree proof. Old revision10 package preserved in baseline snapshot.

Primary-standard correction applied to current story/AGENTS/state and prepended to historical readiness/final-validation reports: phase1 complete, phase2 reopened; required error-free makecheck/complete distcheck are unmet. No waiver or CIgreen inferred. Prepared for review is not ready to submit. Historical completed-readiness conclusion is superseded, raw evidence unchanged.

## R2 source result —2026-10-07T01:52Z

Fresh helper/contrib/directtest, service/cache/worker/scheduler and remaining-native/test shards all return `RESULT: no-issue` for material findings. Service audit explicitly traced nested replacement/context/cancel/shutdown after terminal callback; apparent scheduler sample growth is bounded by production cache-capacity retirement, so rejected as a defect. Existing ENOMEM classification stays minor; synthetic timestamp provenance stays an unproved hypothesis, neither receives speculative policy/test machinery.

One accepted minor reporting correction: recursive Automake TESTS already includes focused bundles; their extra explicit entries duplicate result aggregation but do not execute targets twice. Remove exactly those2 lines. Normal pinned Automake regeneration and config.status succeed; expandedTESTS/TEST_LOGS become3 unique names each, unchanged3-entry check-macosx bundle list. Receipt work/story005-review-test-registration-fix/receipt.json; final Makefile SHA402fddc59a12527a4c37c754e3f20c9e001d34285b5534f5a18f94dc5be6d9d3. This is not a second same-class material duplicate-execution finding and does not reset fullround; applicable targeted registry proof covers it.

Public-wrapper preflight finds obsolete checker readiness/unchanged0003 assumptions and historical screenshot equivalence wording. Accepted material metadata corrections are part of the already-planned package refresh, not new production defects. Checker updated to exact package/source/mode/blob/applyreceipt consistency, package-contained links/attribution and unchanged0000/1 baseline lineage. Original screenshots/runtime pins explicitly historical throughrev10; changed helper/service have fresh headless qualification only. Finalcheckerexecution/fullfresh wrapperreview await finalpackagefreeze. No fullround calledclean before that.

## Split decision —2026-10-07T01:56Z

Adopt the five-part series: existing distribution prerequisite and contrib patch; refreshed helper; service/cache/worker/scheduler foundation; context/player/UI activation. Final source remains exactly59 paths/treef8f7d0fdb46c1ae25ba94049143d12ecb7daf96c. Actual intermediate foundation normal bootstrap/configure/fresh-native-object plugin+main-XCTest compile/link pass. Helper normal build/basic pass. Full registered intermediate suite outerexit0,265tests/1optionalvolume skip/0fail; logSHA63da1c38e2fb21ff6e58966e45b3905bb289cbafaee19aa376db4f834cecd531. No redundant focused repeats after success.

Initial bootstrap missing macro path and first test run missing existing medialibrary/runtime plugins remain preserved failures. Existing unchanged normal core/contrib/runtime inputs reused with source/hash checks; no final native objects reused. Seven fresh configure feature probes differ; bounded source/ABI inspection finds only declarations/fallback selection, no sharedstruct/calling-convention difference. Full fresh core/contrib rebuild and olderOS compatibility are not claimed. Initial missing-runtime abort is setup incompleteness, not silently waived product evidence. Final apply/tree/modes proof independently matches exact latest source including2line reporting correction. Frozen publicpackage refresh nowreleased; final wrapper reviewer still pending.

## Closure —2026-10-07T02:00Z

Final fresh wrapper reviewer returns RESULT:no-issue after exact15artifact hashes/sizes,59source modes/blobs/apply consistency, screenshots/privacy, licensing,8baseline sourcepins and recorded build/test log checks. Finalmanifest87e9831a3c7b4bc544251c9a5ba9b8594eabec579e10ac2bd959d586ff5e529c;5patches515238B/15artifacts4300005B; conservativeproof14999170B<20MiB. Two stale future-tense phrases corrected before finalmetadata confirmation; no source/patch change. Production source−77bytes/net−1line; total source+2445bytes due needed regression/stronger assertions, not a broad reduction claim. Largest native unit6021→4598additions (23.6% smaller relativeoriginalrev10). Unique contributiontestmethods31; nativeexecutioncount288→284 removes redundant/low-value coverage while addingone meaningful regression.

Final state: converged for bounded local source/reviewer-improvement scope; standards/phase2 qualification incomplete with disclosed broader blockers. Two rounds plus final fresh package review, no additional fullround/diagnostic repeats. End before first hourly02:32:48Zcheckpoint; early01:45comparison preserved, hourlyanchor never shifted. No minimum8h quota. Finalvalidation reviewer-improvement-final-validation.md owns grading/Keepopen recommendation; historical revision10 reports superseded onlyforreadiness, originals preserved. Learningreview no-candidate because existingmandatory-gate/evidence guidance already covers readiness correction. No liveworkflow/memory/otherproject change.

Installed3app plist/executablehashes/signatures unchanged; no newGUI acquisition/appinstall/contact/commit/push/submission/cleanup. Preserve scratchreceipts and1GiBreserve (lastbuild17.37GBfree). Buildlanes quiet. Halt here.
