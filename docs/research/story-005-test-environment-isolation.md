# Story005 test environment isolation

The general problem is a class-scoped test fixture leaving process-global state for later test classes. Apple's [XCTest setup and teardown guidance](https://developer.apple.com/documentation/xctest/set-up-and-tear-down-state-in-your-tests?language=objc) places shared class initialization and cleanup in the class setup/teardown methods. POSIX describes [environment variables](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html) as process state mutated through setenv/unsetenv; copies must preserve both absent and explicitly empty values. This is a serial class-fixture lifecycle repair, not support for concurrent environment mutation.

The normal focused real-controller test passed in `candidate-build-20261006T061726Z`. In the subsequent full main bundle (`candidate-build-20261006T062106Z`), the earlier `VLCLibraryDataTypesIntegrationTest` fixture replaced `VLC_PLUGIN_PATH` with the modules `.libs` directory. That directory has no normal `plugins.dat`; its scan failed to load the macOS dylib because Sparkle was unavailable in the test process. The later real-controller preflight observed configuration type0 for `macosx-control-itunes`, instead of integer48. Its preflight correctly failed before controller construction.

`VLCLibraryDataTypesIntegrationTest` already calls `VLCLibraryDataTypesIntegrationStop` in class teardown. Stop releases its LibVLC instance, but previously restored none of its four environment mutations. Core `src/modules/bank.c` clears config/module/cache state when the final bank user releases it; retained first-initialization state is a separate possible mechanism, not demonstrated by this failure. The leaking environment is directly demonstrated by the mutator and later preflight.

The approved correction is local to the fixture owner: save byte copies for exactly `VLC_USERDATA_PATH`, `VLC_PLUGIN_PATH`, `VLC_LIB_PATH`, and `VLC_LIBEXEC_PATH` before its first mutation; restore them once after `libvlc_release` on normal and failed setup teardown. Stop remains idempotent. The fixture's path policy, actual controller, epoch listener, and production configuration remain unchanged. No environment values are recorded in evidence.

The real-controller source remains frozen at SHA256 `f2abf48c08dbcbc56b7eed82dff443b9857c38675dd1ddc136a1759cc5b957bb`. The integration support repair is SHA256 `6847913b961fabfb3d03d8144e37c2ecba130893e495e2e0cb7d297f7a349c92`. Source inspection and `git diff --check` pass; runtime confirmation is pending independent review and a full main-bundle run. A focused-only pass cannot establish isolation from the preceding integration class.

Follow-through, 2026-10-06: independent review clears the scoped repair. The real
controller test passes after the preceding library integration class in both
independent full runs063243Z and064748Z. The latter whole suite is green:
269 main cases (one optional ENOSPC skip),7 context and12 hover, zero failures.
This closes the demonstrated serial fixture-isolation failure; it does not
establish concurrent environment mutation safety or native media eligibility.


## Reader activation discriminator — 2026-10-06

General problem class: reliable assistive-technology activation before assessing
product accessibility. CUA Command-F5 did not start VoiceOver in the candidate
session; that is not evidence of a hover feature regression or reader pass.
[Apple's current activation guide](https://support.apple.com/en-gb/guide/voiceover/vo2682/mac)
documents System Settings → Accessibility → VoiceOver as a normal alternate route
and Option-Command-F5 for Accessibility Shortcuts. Decision: after one unchanged
baseline shortcut comparison, the exclusive native owner may inspect initial off
state, temporarily enable through documented CUA UI, assess actual focus/control
behavior, then restore initial off state. Existing user authorization for native
validation and screen/mouse interaction covers reversible setup; no security,
speech or login settings change. Local result remains pending. Failure to activate
through the bounded UI route stays unknown rather than becoming a product finding.

The UI activation route locally started an actual VoiceOver process, although CUA
app inventory continued reporting it not running. Do not substitute that inventory
for actual process/UI proof. Apple documents [group interaction](https://support.apple.com/guide/voiceover/control-your-mac-with-keyboard-commands-vo2681/mac)
and [interaction commands](https://support.apple.com/en-ie/guide/voiceover/cpvokys07/mac):
VO-Shift-Down enters nested groups. A bounded per-arm group/control activation and
hover-focus discriminator follows; mere repeated VO-Right or generic AX focus does
not establish spoken navigation. Exact result and restored initial reader state
belong in the native receipt.


## Calibration launcher preconditions — 2026-10-06

General class: fail-closed GUI launch readiness before binding a tool that may
auto-launch an absent app. The first calibration stopped at CUA timeout, but raw
`baseline/stderr.log` shows the preceding actual cause: unknown
`--no-video-autoresize`. Pinned `modules/gui/macosx/main/macosx.m:148` declares
`macosx-video-autoresize`, and successful functional sessions use
`--no-macosx-video-autoresize`. The temporary launcher did not propagate child
exit status or require a live child/socket before CUA bind. CUA's current documented
getApp auto-launch semantics explain why a later no-option006 instance is plausible;
PID42789 timing agrees but direct launch attribution is not proved. Preserve it.

Decision: reuse the established successful launcher/flags, verify all selected
options against pinned source/help, require owned child alive plus exact executable/
start identity, ready owned RC socket and actual empty-window evidence before any
CUA binding. Propagate failed child startup as setup failure; never infer readiness
from successful parent exit or a returned PID. A fresh pristine baseline012 clone
avoids acting on unproven006. Preserve first failed/unattempted receipts. One
revised bounded pilot may proceed after reviewed preflight, with no product, observer
threshold, permission or metric changes. This is an understood setup correction,
not a new sequence of heuristic UI retries.


## Unix socket naming preflight — 2026-10-06

General class: platform IPC path-size constraints in long test-artifact directories.
The corrected launcher created native windows, but oldrc refused its124-byte path;
pre-bind guard prevented CUA/media/input and propagated failure. Pinned
`modules/control/cli/cli.c:877–893` rejects strlen(path) >= sizeof(sun_path).
[Apple XNU sockaddr_un](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/un.h)
defines sun_path[104], leaving103bytes for a nul-terminated path. Established
functional sessions already use short named sockets. Decision: use a fresh real
0700 short directory under owned work/, with b.sock/c.sock; compute UTF-8 absolute
path bytes <=103 before launching, while keeping descriptive artifacts elsewhere.
No symlink, systemtemp/globalconfig or production change. Review the full dynamic
setup offline before one next launch; preserve previous failed pilot receipts.
The source/SDK/platform contract and raw refusal explain this setup failure, not
SCK or feature behavior. Local short-path pilot remains pending.

## Timestamped readiness discriminator — 2026-10-06 09:02

Corrected0828 startup passed real empty-window/RC/executable readiness and CUA
binding in both arms. The interruption preserved600s cleanup; exit-file birth
metadata falls at first launch+600.337/+600.344s, while recovery happened later.
No measurement ran. Empty CG/AX queries lack saved timestamps or adjacent live
identity proof, so neither a hidden-window defect nor a query failure is established.
The helper enumerates OnScreenOnly; its AX wrapper suppresses attribute errors.
Pinned video-view presentation logs mean attachment, not makeKeyAndOrderFront.
See ignored0828/window-readiness-diagnosis.md and final-case-inventory-diagnosis.json.

Decision: one baseline-only120s experiment records exact live process and fresh
RC source/state/time around window/tree/focus queries at1/3/5s after admission,
plus one owned actual frame. No seeks or performance observers. This tests
asynchronous lifecycle/readiness at the observation boundary before introducing
hidden-window workarounds. First critical failure ends the experiment; success
only qualifies that precondition and does not unlock scored trials by itself.

## Immediate startup is not playback readiness — 2026-10-06 09:18

One candidate-only diagnostic completed19.761s/120s. Exact live56367 returned
757bytes: correct sourceURI, unknown state4294967295, no numeric get_time,
six zero counters and endmarker. No duplicate source/state lines occurred. Strict
parser rejection is correct; original0918 lostreply cause remains unknowable.
PinnedCLI player.c maps requested STARTED to stnum−1 printedunsigned, requested
PLAYING to compatibility3; listener broadcasts raw PLAYING enum2 instead. Do not
confuse event and requested-state numeric contracts. This is asynchronous startup
readiness, not evidence of malformed source, slower control or framing duplication.

Decision: prepare one prospective bounded condition-based startup check before
the unchanged strict requested-state barrier. Every intermediate rawreply and
timeboundary must be preserved; a pending startup state never counts asplaying.
Exactsource, playing3, currenttime and nonzero decoded/displayed/audio counters
are required before measurement. No fixed fitteddelay, retry of rejectedmeasurement,
parser allowance or source/product change is justified. Tiny offline failclosed
cases and rootreview precede runtime; desktop remains single-owner.

## Finite acquisition must not depend on model handoffs — 2026-10-06 09:28

0924 passed actualowned prebind/CUA, but contextcompaction consumed120s before
admissionmarker. Zero startupreplies; exact12908 cleaned at120.044s. The late
marker remains preserved and cannot count asmediaadmission. Generalclass:
interactive controller latency inside a bounded experiment. Reuse self-contained
process orchestration with deterministic stages, explicitdeadlines and final
receipts. For this no-inputcheck, actualCG/AX/Popen/RC guards replace unnecessary
CUA handoff; no artifact or acceptancecontract changes. One command executes
prebind→admission→conditionreadiness→strictbarrier→ownedcleanup, so agentcompaction
cannot stall the experiment between stages. Offlineplanreview precedes release.

## Multiplexed status notifications — 2026-10-06 09:43

Self-contained0935 actual790-byte reply has exactsingleURI and requested unknown
4294967295 plus unsolicited play2, zero counters/endmarker. Baseline6655 cleanup
exit0/absence after1.474s; no controlmeasurement. This demonstrates asynchronous
notification/request interleaving in thisattempt. Old0918 lostreply stays unknown.
Generalpractice separates responses andnotifications with explicittype/correlation
([JSON-RPC2.0 specification](https://www.jsonrpc.org/specification), responseid vs
notification). That is a mechanism comparison, not a claim VLCCLI usesJSON-RPC.
POSIX socket page fetch returned403; pinnedCLI is the directlocalcontract.

Root requests boundedread-only primarysource comparison: readiness-only typed
classification of disjoint listener/snapshot pairs vs nativeAX advancement before
strictquery vs structuredAPI withoutinterface/artifactchanges. Preserve everyraw
byte and final68e6 strictvalidator. Do not broadlyignoreduplicates or inventbatch
framing. Decide from exactpair/locking guarantees and uncertainty beforecode or
one nextlocalcheck. Desktopquiet; publicfeaturepatches unaffected.

## Unbundled GUI test identity — 2026-10-07 02:43Z

The official top-level VLC smoke uses --ignore-config, but native Cocoa defaults and cache construction are independent of classic vlcrc loading. PID88237's prior real-profile preservation is unknown because no before-state receipt exists; do not infer isolation or restore guessed values. General class: separate test-process application identity from installed application state without changing HOME.

Apple's [single-file code-signing instructions](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html) document an embedded Info.plist. Installed ld documents -sectcreate; SDK CFBundle.h documents __TEXT/__info_plist. Apple's [preference-domain guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/UserDefaults/AboutPreferenceDomains/AboutPreferenceDomains.html) ties the persistent application domain to bundle identifier. Pinned Darwin dirs.m derives app-specific config/cache/userdata paths from NSBundle.mainBundle identifier.

Decision: adapt standard target-only embedded metadata to the normal noinst test launcher, rather than add production core environment interfaces or alter the smoke assertions/default interface. A harmless same-source Foundation executable actually reports null identifier without metadata and unique identifier with metadata. A second owned probe reproduces bin/Contents/Info.plist symlink topology with the pinned original plist and still reports the embedded unique identity. Neither probe calls defaults APIs, launches VLC/GUI or writes profiles. Receipts live at work/story005-blockers-smoke-identity-probe.

Actual VLC linker-section verification and normal smoke remain required. Unique app-specific namespaces may exist under normal Library directories; they are owned test output, not all confined to work. Global Foundation domains remain host context. This mechanism does not supply whole-system sandboxing or retroactive profile-preservation evidence.

## One-shot timer teardown — 2026-10-07 02:43Z

New official default-GUI smoke crash has matching binary UUIDs and a main-thread NSTimer callback into onPlaybackHasTruelyEnded after interface retirement. The baseline manually invokes that callback during teardown and clears its ivar without cancelling the still-scheduled timer. Apple's [Timer programming guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Timers/Articles/usingTimers.html) explains run-loop retention and invalidation; dropping an ivar is not cancellation.

Decision: invalidate before clearing and guard termination/state callbacks against late queued STOPPED rearming. A compact extension to the existing real-controller test passes one normal build/run, asserting captured timer invalidation, nil state and rejection of late STOPPED. No additional test method or broad callback rewrite. Exact two-file repair and focused receipt: work/story005-blockers-player-timer-scout. Full normal smoke is still pending; the original older UPnP-worker SIGTERM crash remains a separate unresolved observation.


### 2026-10-07 — live resource inventory during configure

An offline diagnostic monitor stopped on FileNotFoundError for conftest.ts1 after directory listing and before stat. Configure legitimately creates/removes temporary files. The [Python filesystem iteration contract](https://docs.python.org/3/library/os.html#os.scandir) warns that membership can change during iteration. Use ENOENT-only handling for a live, explicitly non-atomic resource snapshot and record vanished entries; preserve strict immutable input checks and other errors. A separate prospective resume retains the original budget/deadline and failed evidence. This is monitor correction, not product-build success; local probe and actual resumed applicability remain pending.


### Compiler command provenance — 2026-10-07T17:44Z

A generated compiler variable can change even when input CC and CFLAGS match. Current diagnostic configure selects C23 and appends -std=gnu23 to CC/CPP/CCAS; current normal config.log records C23 unsupported and C11 default. Exact historical reason remains unproved. Compare effective compiler variables and actual compilation commands, not only CFLAGS/config.h. doltlibtool commands are actual compile witnesses; requiring a literal libtool prefix falsely rejects them. See work/story005-compiler-provenance-audit001/report.md and stopped diagnostic003. No normal build defect inferred; no repair in the stopped window.


### Concurrent UI-transition observation — 2026-10-07T19:09:47.229711+00:00

Generalclass: externalUIaction and post-actionmodelreceipt latency. Existingseparatecaller/rootprocesses can observe concurrently from an atomic same-directory marker; Python os.replace https://docs.python.org/3/library/os.html#os.replace suppliespublicationcontract. An in-process threading.Event https://docs.python.org/3/library/threading.html#event-objects needs an additionalbridge here, so notselected. A validpre-actionpausedsnapshot mustremainpending duringresume, notfailure orsuccess; original10s deadline staysanchoredatpre-actiontime.

Actual002 typedresume qualifies6.8317865s afteroriginaltimestamp,15.938412s beforefullrootreceipt; prior001collectedzeroreplies after14.87slatehandoff. Current002collects34replies. Local synthetic actualhelper source/IOfailure/malformed/timeoutcounterfactuals pass and no productsource/toolbinarychanged. Actualoriginalmainreturn/strictplaying passes. Entire240s manualmultistageprotocolstilltimesoutbeforereturnedhoverinput; retainedpartialproofdoesnotqualifyfullroundtrip. Stopfurthergrowth/replaythisrun. Finalreceipt89e3fa687e0b1e21086fb8947c3a9c5f89a14cba62067346668db574abe6abb8.
