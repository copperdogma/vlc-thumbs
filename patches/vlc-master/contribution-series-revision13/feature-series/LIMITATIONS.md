# Current revision13 review qualification

**Prepared for maintainer review; submission checklist incomplete; no submission.**

The exact 72-path freeze passes executed normal 009 complete registered check and
conventional 010 complete distcheck through final distcleancheck. Native tests report 283 pass
and one optional skip among 284 unique cases; lifetime 5/5 and helper-basic 13/13 pass. Normal 94
and archive 93 test cases preserve upstream distribution Lua-disable flags; nested totals
overlap. Full helper 77 was not rerun by 009/010. Actual 010 used a private read-only artifact
preflight forwarding unchanged argv/status to the original driver. The shorter public host
recipe remains **unexecuted**; executed build/archive proof does not establish execution of
that changed route. No public forensic guard is required. Historical failures are retained.

Historical shutdown 004 remains unexplained and user-accepted **DEFERRED**. A bounded
comparison found one unchanged-baseline normal Command-Q SIGSEGV matching the earlier 015
ResizeNotify/logging pattern, distinct from 004's condition-wait pattern. One corresponding
candidate normal Command-Q exited 0 without SIGTERM. This establishes neither 004 causality,
shutdown frequency nor candidate exoneration.

Actual human VoiceOver main Position-to-Pause navigation, stable pause and resumed advancing
video pass narrowly. Spoken/exposed 5.5% disagreed with 38.417 s/7200 s; accurate media position,
precise seek, visible-preview navigation and fullscreen reader remain unqualified. A separate
comparison qualifies ordinary Play and two actual native CUA midpoint actions per arm with
decoded 150 s and >5 s continued video. Both arms exposed stale slider/time labels after actions;
no physical drag, quarter-position or universal accessibility claim follows.

Current main hover and custom-fullscreen 180-second Keyframe hover, actual UI Pause/Resume
and return to the main window are demonstrated. Returned-main hover and normal Quit were
not reached within that roundtrip's deadline; its full roundtrip remains unqualified.
A later bounded trial entered custom fullscreen and returned to the original main window
with strict playing state. Its one native hover route and capture passed, but independent
full-region image review showed the on-bar cursor and advancing 116.042 s/frame 2785 with
no thumbnail or Keyframe caption. Returned-main hover remains unqualified; the cause is
unknown, and this single negative capture does not establish a regression. No retry or
reader trial followed; VoiceOver was never enabled. Root's one Command-Q exited 0 without
SIGTERM and the parent was absent. No matching crash was present in the bounded inventory
(delayed reporting remains possible); no universal descendant-absence claim follows.

Intel/older-macOS/CI execution remain unavailable. These limits are review disclosures;
maintainer acceptance and completion of all native qualification remain separate decisions.

The preserved material below records historical results and failures, not current
combined-tree qualification. Baseline source pins refer to the pinned upstream
base; aggregate ownership repair changes one of those pins in the current tree.

# Qualification, unresolved faults and attribution

**Revision 11 historical qualification.** Revision 11
has exact five-patch source application and fresh scoped headless build/test proof.
Normal helper/module builds passed; helper 77 passed; the native suite ran 284
unique tests, with 283 passes and one optional owned-volume ENOSPC skip. The new
terminal-completion regression passes with the fix and fails against an isolated
original service object. The trim counterfactual rejects three error-only replies.
Final Automake test aggregation retains exactly three unique XCTest bundles/logs.
No new app packaging, GUI, reader, NAS or playback qualification is asserted.

The service-foundation intermediate separately compiled/linked fresh native
objects and passed 265 tests with one optional skip; helper build/basic passed.
Verified unchanged core/contrib/runtime inputs were reused. Initial missing-tool
and missing-runtime failures remain recorded; this is no from-scratch whole-build
proof. Historical results below belong to revision 10 or its explicitly unchanged
runtime predecessors, and do not qualify changed helper/service GUI behavior.

## Build, tests and distribution

| Historical evidence | Scope and remaining gap |
|---|---|
| 77 helper checks: 39 existing + 38 admission (8 admit/30 reject) | 32 pixel/time replies across 16 existing cases matched the prior freeze; not exhaustive formats/decoder safety |
| Custom-AVIO admission on/off | All 1,200 packets preserved; size-query, restore and mid-scan faults fail closed. ASan/UBSan covered probe/callback code, not linked FFmpeg; leak detection disabled |
| Revision-6 native suite: 288 counted executions, zero failures | 269 main (one optional-volume skip), 7 context, 12 hover; historical count includes overlapping hover coverage. Separate owned-volume ENOSPC proof passed |
| Independent native-arm64 build | Fresh tools, pinned official remaining contrib and normal patched FFmpeg compiled; packaged app's 997 files and signature verified. Outer runner exited nonzero after script mutation: no clean end-to-end runner pass |
| Source application/distribution | Revision 11: five patches independently applied to the pinned base and reproduced tree `f8f7d0fdb46c1ae25ba94049143d12ecb7daf96c`. Historical revision-10 archive membership/bytes and minimal configure/compile/link passed. Exact current source application proves neither new app behavior nor conventional distribution completion |

Conventional distcheck's main test directory reported **80 pass, 5 skip, 7 fail**:
clock drift, decoder subpicture, SPU creation, TLS, BMP encoding, OpenGL and CVPX
conversion. Install/installcheck/uninstall/DESTDIR cleanup/redist/distclean were
not reached. Untouched-master normal-configuration runs reproduced clock drift_72,
TLS `tls.c:188`, and OpenGL `filters.c:134` GL_INVALID_OPERATION with the same
cvpx_gl/glsampler_builtin/vout_macosx provider selection. That configuration differs
from minimal distcheck; exact causes and matched whole-build equivalence are not
established. Other failures are not all attributed. No failing tests were disabled.

A separate revision-8 structural distribution trial returned zero for install,
installcheck, uninstall and DESTDIR commands, with zero regular-file residuals.
But the unchanged install recipe failed `cd` and ran `mv` in the build directory:
correct executable-name installation is unproved; empty installcheck proves no
functionality. Redist retained five headers/twelve helper inputs. Distcleancheck
failed on `bin/vlc` and extra-only `libvlc_vtutils.la`. Revisions 9/10 changed only
the source guide; this partial trial does not supersede failed make-check/distcheck.

Earlier failed launchers/host setup included unset-variable handling, BSD sed,
PATH placement, ancestor Git revision discovery and missing archive headers.
Host corrections did not erase those failures. Acquisition digests are not
publisher signatures. All-contrib source builds, Meson, Intel and older macOS
execution are unqualified. VideoLAN's [submission requirements](https://wiki.videolan.org/Sending_Patches_VLC/)
call for error-free make-check and full distcheck when adding files; no waiver or
maintainer agreement is asserted.

## Native, NAS and playback scope

Visible preview evidence covers main/native-fullscreen/custom-fullscreen/detached
controls, recorded media/track/rotation, preferences/restart and source failure/
replacement. Ordinary wheel/volume/Space/click behavior has four-surface evidence.
Later physical main/custom gestures, custom click/drag followed by five seconds
of playback and Escape/main reparenting passed; shared `setPositionFast` is unchanged.
An immediate main-window position assertion ignored asynchronous completion;
a detached ±3-second coordinate projection was uncalibrated. Neither proves a
regression. Precise main/detached seek accuracy, detached held-button behavior
and full reader/freshness/restart coverage remain unqualified. Historical baseline
VoiceOver activation was unavailable; later candidate reader evidence is qualified above.

Warm NAS comparison: generated five-minute/300-Cluster media, 36 requests/18
prior-current pairs with exact image pixels/sample times. Older 72-request/36-pair
results on tiny 1,200-Cluster and recipe-incomplete 228-Cluster media are supplementary.
Warmth was uncontrolled; AVIO counters are not network round trips. Cold/stalled/
larger-source NAS, hard kernel-IO timing and universal latency are unqualified.
Sampled SHA256 reads sixteen 64 KiB windows for large files and all bytes up to
1 MiB; unsampled changes can escape detection. Source guides retain identity,
cache corruption/eviction, provisional-expiry and same-URI reopen review recipes.

The foreground/unoccluded/paused rendered-knob cohort had 20 valid responses per
arm: baseline median 141.765354 ms, candidate 146.676000 ms (+3.463925%), within
the declared +20% allowance. Both used 600,000 ms visible controls. Default fades,
occlusion, completed seeks, simultaneous hover and p95 are not qualified by it.

Three matched AB/BA/AB pairs retained six central 60 s playback intervals with
pointer outside the timeline: 0 percentage-point paired loss-fraction increase,
and captured digital audio without PTS discontinuities or below −60 dBFS gaps.
No physical speaker proof. Cache progress (27–30 new target aliases per 10 s bin)
supports recurring preparation, not continuous decoding or hover stress.
Candidate pair 1 has a **133.332 ms screen-PTS observation hole**; callback gaps
were tracked separately. No uninterrupted-video or causal-stall conclusion follows.

Each app/helper had 61 resource samples. Across pairs, sampled mean CPU was
1.33–1.73% baseline app, 3.06–3.70% candidate app, 0.72–0.96% helper; maximum sampled
RSS was 210.03–215.98 MiB, 213.11–269.80 MiB, 30.03–35.64 MiB respectively. These
are separate samples, not interval CPU or true peaks. Capture overhead, host load,
order and unflushed warmth limit interpretation.

## Actual shutdown fault and bounded baseline attribution

Candidate pair 3 terminated with **SIGSEGV (child status −11) during SIGTERM
shutdown**; five other retirements exited 0. Process absence is not clean shutdown.
The frozen numerical analysis accepted any non-null exit status and therefore did
not reject this crash. All six original runs remain retained. No production change
fixes it, and exact causality remains unproved.

At the pinned base, `vlc_media_source_provider_GetMediaSource` returns an owned
reference. The Cocoa provider passes it to a wrapper without releasing the original;
the wrapper adds/releases only its own hold. Source discovery closes only when
its reference count reaches zero; provider deletion does not close surviving
children. Final module-bank cleanup can unload plugin images without checking
those references. UPnP close joins its search thread; wrapper destruction calls
`UpnpFinish`. This is an unchanged upstream ownership defect/lifetime hazard,
not proof of this candidate crash, a crash fix or feature exoneration.

Eight unchanged source pins below give primary locations and SHA256 values at
base `2e358f3098c2f2b7621d1dc568de8b61ad786322`:

| Source | SHA256 |
|---|---|
| [include/vlc_media_source.h:290](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/include/vlc_media_source.h#L290) | `80ac2c27a432e5991f4220007058d01d60e56ee2a5573eaa79787d0c990ed6bb` |
| [VLCMediaSourceProvider.m:44](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/library/media-source/VLCMediaSourceProvider.m#L44) | `2a844487fc97b61272c21be4223555a936439d9322edc72c1890cec78b3d57ef` |
| [VLCMediaSource.m:155](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/library/media-source/VLCMediaSource.m#L155) | `e23d631f8f46556307861da9255bcca918ac52fe721870651db6fc27b5d2d99c` |
| [src/media_source/media_source.c:173](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/media_source/media_source.c#L173) | `cd8225c1081a45b58d7f5e117e169c61bd6b07ceee5eaa64f18249f66303c839` |
| [src/modules/bank.c:756](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/modules/bank.c#L756) | `165ecfcaffa8c54931967f4e59b295b546eda8608df0d6d3e7ae804f75f3c8a6` |
| [src/misc/objects.c:126](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/misc/objects.c#L126) | `d25da3893002609987227b5a8c2b381b3fc3c76163daaab89937ddc4844885c1` |
| [upnp-wrapper.cpp:43](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/services_discovery/upnp-wrapper.cpp#L43) | `9da68e858a243b2a4a9dbff36a0ea66ce688d037f162d308ba71b841510b7e4a` |
| [upnp.cpp:347](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/services_discovery/upnp.cpp#L347) | `f60eb2b1bf0267160f4d742ae8cc8f48e40c046522d08c8206f7279b1634a82a` |

One untouched baseline GUI run activated UPnP services and renderer discovery.
Its EOF trace includes renderer removal and later keystore cleanup, without a
services-removal entry; the child exited 0 and was observed absent. The 19,455-byte
trace SHA256 is `9d8e050310dbf59a7a10579cf825d78950baeb46aa53db06969b6ad0093278dc`.
Raw logs/LAN identities are excluded. This corroborates the affected baseline
path and missing close entry; it proves neither a live worker at unload nor runtime
image UUID nor candidate crash cause. Mapping timed out after about 5.802 s,
missing its post-mapping hold; sampling/mapping/LLDB were inconclusive. A separate
diagnostic host missed its hold and explicitly destroyed discovery, bypassing
the Cocoa ownership path; its clean result cannot exonerate that path.

## Contributor and redistribution boundary

Cam approved contributor/contact credit: **Cam Marsollier <cam.marsollier@gmail.com>**
(from Git configuration); development used AI assistance. Existing source notices,
including collective helper credit, remain. Helper/application sources use
GPL-2.0-or-later; standalone fixture scripts retain LGPL-2.1-or-later notices;
contrib licenses/notices remain applicable. Credit is no sole-ownership claim,
assignment, waiver, sign-off or formal rights attestation. Maintainers may request
more precise source credit and different patch boundaries. Source-license review
does not qualify binary/media redistribution. No app/library/fixture video, NAS address,
raw private log or local receipt is a package input. No external contact occurred.
