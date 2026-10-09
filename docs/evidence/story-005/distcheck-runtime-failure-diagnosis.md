# Conventional distribution runtime-test failure

The frozen 072705Z run made the distribution archive, checked five header memberships/bytes, configured and compiled the read-only VPATH source, linked normal platform modules/executables, and entered make check. It failed after 437.5 seconds. The test/ directory reports 92 tests: 80 pass, 5 skip, 7 fail, 0 error. Earlier test directories have separate summaries in the preserved main log; they are not included in that 92 count.

The exact failure sources, direct clock implementation and test registrations (11 paths) are byte-identical to pinned 2e358f3098c2f2b7621d1dc568de8b61ad786322; see distcheck-failure-source-pin-comparison.json. This is source identity, not a pristine-runtime counterfactual. The selected minimal configure profile comes from upstream AM_DISTCHECK_CONFIGURE_FLAGS, disabling avcodec/avformat/postproc/swscale/fribidi and other optional features, plus explicit disable-timeline-preview/disable-macosx. The helper and macOS GUI feature are not runtime-tested by this profile. The separately registered feature-native 288/1 skip/0 failures and independently built helper proofs remain distinct.

| Test | Actual failure | Bounded interpretation |
| --- | --- | --- |
| test_src_clock_clock | drift_72 scenario equality assertion at clock.c:662, after normal/lowprecision cases | Root cause unqualified; no timing, compiler or regression attribution without a controlled comparison. |
| test_src_input_decoder | mock closed-caption decoder cannot obtain output subpicture; input_decoder_scenarios.c:480 | Subpicture/module/configuration requirement unresolved. |
| test_src_video_output_spu | spu_Create returns NULL; spu.c:1020 | SPU setup requirement unresolved; missing first default plugins/plugins.dat warning alone is not a demonstrated cause. |
| test_modules_tls | SecureTransport certificate alias lookup error -25300; handshake fails, tls.c:188 | Platform credential/backend selection differs from PEM fixture assumptions; no keychain mutation or bypass performed. |
| test_src_player_attachments | no encoder for BMP; exit142 | Consistent with disabled avcodec profile, not established as complete causal explanation. |
| test_modules_video_output_opengl_filters | GL_INVALID_OPERATION assertion, filters.c:134 | Platform/offscreen graphics behavior unresolved. |
| test_src_misc_image_cvpx | no matching video converter and NULL export block, image_cvpx.c:86 | Consistent with disabled swscale profile; complete cause unqualified. |

Pinned extras/ci/gitlab-ci.yml:514-515 explicitly compiles core test targets with make check TESTS= before the separate macOS check target. This explains why the existing upstream macOS CI recipe does not itself establish successful execution of all these conventional runtime tests. It is not used here to disable tests or claim success.

Install/installcheck/uninstall/DESTDIR uninstall/redist/distclean portions of conventional distcheck were not reached. No clean distcheck claim, test allowance change, flag change, runtime source repair or retry is made. All seven exact .log/.trs files, suite/main logs, guarded receipt and archive are preserved in the owned directory recorded by distcheck-runtime-failure-preservation.json. The root agent owns any next bounded diagnosis/scope decision.

A subsequent bounded, no-rebuild comparison ran only the already-built untouched-master clock/TLS selectors. Both reproduce their assertion signatures (clock drift_72 at clock.c:662 and TLS at tls.c:188). See baseline-clock-tls-attribution-20261006T074008Z.json/result.md. This narrows feature-regression attribution for those two cases only: the normal full baseline configuration differs from minimal distcheck, no matched whole-build comparison was made, and the selected TLS client/backend cause remains unproven. No additional distcheck retry or test disabling followed.
