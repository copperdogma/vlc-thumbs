# October 30 source and submission refresh

Current warning-clean successor: **16 patches / 70 paths**, export head `dd50411dad2b8c05144acbf0e7c63fb9150e0120`, tested source tree `212c081ca9eb566a65b3979d272a788ae52653ea`. The later [closeout validation](refresh-closeout-validation.md) records the intentionally incomplete test-shell warning treatment, affected five-case pass, source ownership control and project landing. The fifteen-patch build history below remains applicable only at its explicit scopes; it is preserved as predecessor evidence.

Status: Bounded refresh complete; qualification is partial because the registered CLI quit check stalled. October 13 results remain historical. No upstream push or MR.

Historical fifteen-patch review source is [the now-updated successor package](../../../patches/vlc-master/contribution-series-20261030/README.md): **15 commits / 70 paths**, base `5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09`, export head `4dd9f5e20631173cbf1343e6367c4ac4a3a836a9`, tree `330eb90675c4ffe744625c3d65fdbab55895c7c6`. Independent replay of all exported patches gives the exact tree and a clean checkout. A final message-only correction updates a stale header/Makefile count; the tested source tree is unchanged.

| Gate | Current result |
| --- | --- |
| Normal arm64 app/package/signature | PASS using full GNU libtool; default Dolt attempt failed |
| Fresh helper matrix | 77 passed |
| Packaged helper protocol | 13 passed |
| Main macOS bundle | 597 passed, one skipped, zero failed |
| Context / hover reentrancy | 7 / 11 passed |
| Final core group | 96 passed after one-line test-link repair |
| Extracted source archive build / helper protocol | PASS / 13 passed |
| Registered CLI startup/quit | BLOCKED; stopped after 306.64 seconds; observed SAP teardown join |
| Complete conventional distcheck | NOT RUN because the host gate is already blocked |

The first full normal check remains a failed collection. Current unit coverage combines its unchanged passing groups with the repaired complete core group. This is not an uninterrupted full `make check` pass. No fresh desktop hover, VoiceOver or performance qualification is claimed. No new tests were added.

Normal app artifacts bind to `e6e5bff` / tree `3b08612dc30215464c8fbc78e60c3bcf7217e316`. The later source change affects only a test link rule. Archive build and repaired core-group artifacts bind to `8cd1b7c` / tree `330eb90675c4ffe744625c3d65fdbab55895c7c6`; the final export has that same tree. The manifest preserves these distinct identities.

## Upstream feature scout

Canonical master and official mirror agree on `5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09` (October 30). Public API/tree/source inspection found no merged native macOS seek-position hover thumbnail implementation. Existing same-feature MR !7493 remains open (updated April 15), with preview-window/cache/player/slider changes. It is competing unmerged work, not absence of prior art. Core design #29393 remains open. Existing library thumbnail and mini-player preview paths do not implement seek-hover previews. Bounded MR search found no additional direct macOS implementation; exhaustive absence is not proven.

- https://code.videolan.org/videolan/vlc/-/commit/5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09
- https://github.com/videolan/vlc/commit/5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09
- https://code.videolan.org/videolan/vlc/-/merge_requests/7493
- https://code.videolan.org/videolan/vlc/-/work_items/29393
- https://code.videolan.org/videolan/vlc/-/merge_requests/7148 (library mini-player)
- https://code.videolan.org/videolan/vlc/-/merge_requests/7822 (closed Qt prototype)

## Source provenance and actual substrate

Exact October 13 source/build workspaces and 14-commit objects were not located in bounded current-checkout/temp/known-NAS-archive inventory. Tracked source10 thirteen-patch package and manifest remain recoverable. Reconstruct from original base `2e358f3098c2f2b7621d1dc568de8b61ad786322` and verify original combined tree `b7c0f24e442c35a57bb108d56b801fd05b624943` before current rebase. The documented extra Darwin fixture export fix must be assessed against current master; do not assume it is still needed or pretend new commits are original `8ef6bd09`. Missing raw fixtures/logs/deps cannot be inherited as fresh proof.

Root owns plan/integration/validation judgment. SOL 6.1 Medium worker is sole isolated source writer under ignored work/story007-refresh-20261030. Root preserves tracked predecessor package, dirty checkout, apps/media. About 18 GiB available; explicit macOS SDK 27.2 works. Current build substrate is being recovered with bounded downloads; full build not released before size/dependency check. New synthetic fixtures may be generated through retained public generators and labelled new inputs.

Human personally submits MRs/reports/replies under current VideoLAN AI policy; this pass does not publish remotely or start a native UI/performance/reader campaign.

## Source refresh and prerequisite decisions

Exact original 13-patch source10 tree verified before rebase. Initial fresh successor 14 commits included reconstructed documented Darwin fixture-table export; rebase dropped old P0004 because upstream `1f7b9510e272ae760068e455e6c9decd083f7277` initializes OpenGL version to 0 and every consumer tests >= 3. One LazyPreparser header distribution hunk is already upstream and omitted. Manual conflict unions affect macOS test framework/library fixture support and retain current upstream plugin-cache preparation; production feature logic was not manually changed.

New VideoLAN policy required removing repeated AI-assistance/drafting-rights boilerplate from fresh commit messages, with Cam author headers preserved. Message-only rewrite verified identical tree `3c65cb9248d7df5b30dc460cc9e71cf240021d5f`; historical reconstruction refs remain. AI disclosure stays in human-facing MR description. Current README dependency recipe was then updated to current CI contrib artifact because current master requires medialibrary 0.14.1. Source head e6e5bff8248b02509063534e28281a0c2d192bdd/tree3b08612dc30215464c8fbc78e60c3bcf7217e316 is 14 commits / 70 paths before any later build corrections. No upstream branch push.

Source worker receipts/mappings are under ignored work/story007-refresh-20261030; original tracked patch package unchanged. A reconstruction is not recovery of original October 13 commit objects.

## Toolchain repair

Xcode 27.2 lacked optional MetalToolchain. Apple documents normal installation at https://developer.apple.com/documentation/Xcode/downloading-and-installing-additional-xcode-components . Root executed xcodebuild -downloadComponent metalToolchain ; 838.9 MB official Apple component installed, Build 27B47. Actual metal --version returns 32023.922 and metallib resolves in mounted Apple toolchain. No shader disabling or altered global SDK selection. Upstream build tools are freshly built through their ordinary recipe; normal/contrib/test results are still pending until recorded below.


## First normal build failure: compiler wrapper

The first normal build exited 2 at unchanged upstream `modules/gui/skins2/macosx/macosx_dragdrop.mm`. Current Automake emits `--tag=OBJCXX`, while skins2 also supplies `--tag=CXX`. VLC's Dolt accelerator recognizes CXX but passes the unrecognized OBJCXX tag to its compiler wrapper as an executable name. This is a build-wrapper compatibility failure; it is not a timeline-preview compile error. Neither implicated upstream source file was changed by this series.

The standard alternative is full GNU libtool, which understands the language tags. The exact failing target passed in 4.02 seconds with `LIBTOOL='$(top_builddir)/libtool'`, preserving compiler flags and enabled features. Continue the ordinary make/package/check targets with this explicit recursive make variable override. Do not add an unrelated Dolt patch to the contribution or disable skins2. The first failure and the successful target proof remain in the worker logs.

Primary references: [GNU libtool language tags](https://www.gnu.org/software/libtool/manual/html_node/Tags.html), [GNU Automake manual](https://www.gnu.org/software/automake/manual/automake.pdf), and [Dolt's upstream description of its libtool accelerator](https://dolt.freedesktop.org/). Local diagnosis is in `work/story007-refresh-20261030/logs/dolt-objective-cxx-diagnosis.md`. This is an explicitly qualified build-recipe adjustment; the unmodified default accelerator path did fail.


## First full test run and isolated audio-test diagnosis

The first complete registered `make check` run exited 2 after 808.84 seconds. The main macOS bundle completed 598 cases (597 passed, one skipped, zero failures), with separate context (7) and reentrancy (11) bundles passing. The final core group passed 95 of 96 tests; the new upstream `test_src_audio_output_dec` alone crashed with exit 139.

Its crash report shows a null call from `var_DestroyAll` during audio-filter teardown after its resampling assertions, not a fatal Sparkle loader error. The test directly compiles `misc/variables.c`, which needs the platform replacement for `tdestroy` on this host. The executable leaves `_tdestroy` dynamically looked up, while libvlccore's replacement is private; upstream's test link line omits the compatibility library. The static mock-module table is actually exported, ruling out the previous fixture-export problem.

General problem class: a standalone test compiles an internal source file without linking its platform compatibility objects. [GNU Autoconf's replacement-function guidance](https://www.gnu.org/software/autoconf/manual/autoconf-2.60/html_node/Generic-Functions.html) describes including replacement objects when the platform function is missing. Choose the existing project's compatibility library rather than writing a replacement or changing the test's assertions. A focused relink/test is authorized to prove this diagnosis before any source fix. The unrelated Sparkle scan warning is retained, with no framework-search workaround justified by this stack.


The focused relink passed in 2.01 seconds: `_tdestroy` changed from an unresolved dynamically looked-up symbol to a locally defined function. The same Sparkle scan warning remained, demonstrating it was not the crash cause. The minimal correction adds the existing `../compat/libcompat.la` to this new test's LDADD, following existing project practice. No test assertion or application behavior changed.

Successor commit `8cd1b7ce65d67886ca5f3afa802fb888226b659e`, tree `330eb90675c4ffe744625c3d65fdbab55895c7c6`, contains only that test-link correction. The complete final core group then passed 96/96 in 16.04 seconds. Do not relabel the initial full run as a pass: current normal coverage combines its unchanged passing groups with the successor's complete core-group rerun. Normal app/helper artifacts retain their earlier `e6e5bff` provenance; the successor changes only a test link rule. Conventional archive qualification is pending.


## Remaining host shutdown gate and bounded archive decision

After the unit groups, the registered root host script runs `./vlc --ignore-config --rc-fake-tty -vv -Irc,oldrc vlc://quit`. Its owned process remained alive during cleanup. A three-second process sample shows the blocking chain: Darwin termination → libvlc cleanup → medialibrary 0.14.1 device-lister destruction → media-source release → SAP services-discovery Close → thread join. UPnP search messages also occur, but the sample does not establish UPnP as the blocking call. Do not infer a thumbnail regression or definitive upstream fault from unchanged source paths alone.

The owner previously deferred ambiguous shutdown-causality work. Bound this check at 300 seconds, preserve the sample and unresolved result, and avoid a new shutdown campaign. A conventional distcheck would repeat the already passing long unit suite before reaching the same known host gate. The next check is therefore source-archive generation/extraction/configuration/build with the same feature flags, not a claimed complete distcheck. Record those archive steps separately and retain complete distcheck as unqualified. No test or enabled network feature is removed to obtain a passing label.


## Archive outcome and final preservation

The ordinary source archive was generated and extracted. The first private wrapper attempt failed before compilation because its Git ceiling covered the outer build but not the sibling extracted source. Git then found the enclosing project and attempted to rewrite a read-only revision file. This is a private setup defect, not an upstream source failure. The correction covers their common ancestor; exact `git rev-parse` isolation was verified before continuing the existing build. No source patch, repeated archive generation or reconfiguration was required.

The corrected archive build and its 13 registered helper protocol checks passed. Combined active archive attempts took 542.05 seconds (351.37 initial setup plus 190.67 continuation). Optional install/uninstall/distclean were not run; no complete conventional distcheck pass is claimed. Payload checking found 67 of 70 changed paths byte-identical, with the standard configure date freeze and two Meson files omitted by the existing Autotools archive format. The Git patch package preserves all 70 paths; this archive check does not qualify Meson packaging.

Generated changes to 99 PO/POT files were snapshotted and restored only in the owned source workspace. Final source is clean. The original tracked source10 package remains unchanged, and unrelated main-checkout dirt is preserved. The exported successor was independently replayed to the exact combined tree before preservation. Compact receipts accompany this report; raw attempts, dependencies, fixtures, source and binaries remain under ignored `work/story007-refresh-20261030/`.

The root selected the 300-second host bound under the owner's focused-check scope; actual stop was 306.64 seconds including handoff latency. Owned process-group absence was verified. The raw stop receipt's wording “owner-approved300s” does not mean Cam explicitly chose that number. Shutdown origin remains unproven and unresolved; do not identify this hang with an earlier crash or call it definitively unrelated to the series.


## Warning scope and durable receipts

The final broader audit found **17 test-fixture compiler warnings** on the inherited link-only `VLCMediaLibraryMediaItem` stub in `VLCVoutLifetimeTestSupport.m` (protocol-property synthesis and SecureCoding property implementation). Production changed-line compiler diagnostics were zero in the collected logs. An earlier partial-log statement of zero warnings did not cover this test compilation and must not be promoted to an all-source warning-free claim. The stubs and their passing lifetime tests were not changed in a late warning-cleanup cycle. Thirteen diff whitespace entries belong to inherited nested FFmpeg patch context.

[Compact validation summary](refresh-20261030/validation-summary.json), [source replay receipt](refresh-20261030/submission-replay-receipt.json), [warning scope](refresh-20261030/final-warning-scope.json), dependency/fixture hashes and first-attempt receipts are preserved under [refresh-20261030](refresh-20261030/README.md). The source package and receipt directories each include SHA256SUMS. Main-checkout methodology validation and whitespace checks are separate from native test qualification.


## Owner-authorized warning cleanup

The owner asks whether the remaining findings are our responsibility and authorizes scoped corrections followed by validation/check-in/push. The 17 diagnostics originate in our deliberately incomplete test shell, so we own documenting that boundary. Narrow diagnostic handling applies only to that shell, with a comment explaining why no media properties or secure-coding methods are simulated. The window shell declares its intentionally unused overridden accessors dynamic instead of allowing conflicting implicit synthesis. Production diagnostics and actual behavior are unchanged; implementing sixteen unused fake properties would make this fixture less clear.

The affected source was freshly recompiled and its five registered video-output lifetime cases passed. All 19 fixture warnings are absent in the final affected compilation. The two diagnostics at upstream VLCWindow.h declarations were also caused by our incomplete window shell; the real implementation provides explicit accessors. Final tested/exported head `dd50411d` and tree `212c081c` match; no production change was needed. The final 16-patch export replays to that tree. Previous normal app/archive/helper/native/core checks are reused only for unaffected content; no full product-suite rerun is claimed.

Independent artifact review found two documentation defects: a stale current status in the review ledger, and raw-workspace-relative paths in the promoted validation receipt. The ledger now distinguishes current and historical status. The receipt retains its original bindings plus an explicit preserved/raw-only path map, and the fifteen-patch predecessor manifest/hash ledger is preserved. These corrections change evidence navigation, not past outcomes.
