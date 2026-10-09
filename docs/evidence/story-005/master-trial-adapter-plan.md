# Master matched-trial adapters — prospective design

Read-only planning on 2026-10-06. No desktop inputs, screen/audio capture, app
launch, benchmark acquisition, scoring, production edit or fixture generation
occurred. The native owner retains exclusive acquisition. New driver ownership
would be only `tests/story-005/master_control_trial.py` and
`master_playback_trial.py`; the existing pointer/session/observer sources stay
unchanged. Root must review this addendum and hand off the desktop before running.

## Diagnosis and reuse boundary

This is an observer-qualification/coherent-setup problem, not a slower seek or
missing-trace problem. Story004's control driver delegates to Story002's
`baseline_control_trial.py`: fixed development bundle ID, fixed window/AX/crop,
2x raster, light-knob width 6..32px, two fixed points and paused-zero setup.
`control_response_probe.m` independently hardcodes that development bundle in
foreground guards. Story002's `playback_capture.swift` also hardcodes it. Changing
Python constants or passing another PID does not change these binary guards.
The master baseline's paused-seek/resume and stale bar defects are separate; do
not reproduce their setup automatically or call RC progress rendered feedback.

Reuse the old generic JSONL logger, exact-identity guards, process-group cleanup,
RC counter parsing, sampled resource accounting and complete-frame timing policy.
Do not reuse old Arm/launch defaults, helper trace paths, event-count inference,
classifier thresholds, burn-counter assumptions or historic baseline manifests.
Source paths inspected: Story004 `pragmatic_control_trial.py` /
`playback_ready_trial.py`; Story002 `baseline_control_trial.py`,
`playback_benchmark.py`, `playback_capture.swift`, `playback_analysis.py` and
`control_response_probe.m`; Story005 verification plan/current feature source.

A bounded primary-source check supports retaining the actual display boundary:
Apple documents [displayTime](https://developer.apple.com/documentation/screencapturekit/scstreamframeinfo/displaytime)
as when WindowServer displays the frame, and
[complete](https://developer.apple.com/documentation/screencapturekit/scframestatus/complete)
as successful generation of a new frame. Neither callback arrival nor media PTS
is a substitute for displayTime. Those contracts do not certify a new knob
classifier or exclusive ownership; local positive/negative pilot evidence must.

Native owner supplied existing read-only evidence: normal main screenshot
`work/story005-native-baseline/main-mid-hover-2302.png`, detached screenshots,
and actual normal-main AX rect (223,798,548.5,17), CG window (208,392,896,456),
1792x912 raster (2x). The existing master screenshot shows a white pill knob on
black controls; the old 6..32px light classifier is unqualified for this shape.
Candidate revision9 screenshot has faded controls, so is not a classifier pilot.
These are dated observations, not geometry constants for a future driver.

## Proposed smallest driver inputs and guards

Both drivers accept explicit app paths, bundle IDs, exact PIDs, RC socket paths,
fixture and manifest, observer/tool executables and their source/build manifests,
geometry JSON, fresh output, and an approved protocol receipt. No3.0 path defaults
or global preferences. Current supplied IDs are
`org.videolan.vlc.story005.nativecandidate` and
`org.videolan.vlc.story005.nativebaseline.discriminator006`; a new domain must be
explicitly supplied and independently validated, never substituted from a name.
Native owner reports a new baseline domain is being isolated, so do not hardcode006.

Prefer attaching only to native-owner prepared sessions: validate plist ID,
canonical executable, PID/start identity, process-group inventory, owned RC socket,
frontmost exact instance and fixed observed window before each block. Drivers own
only newly spawned observer processes, each in a dedicated process group; never
kill attached app/helper processes, daily VLC or another acquisition. Retain all
raw records. On timeout cancel observer groups with TERM/5s then KILL/5s, reap and
record survivors. Parent/native owner owns app lifetime. Require >=1GiB reserve,
512MiB aggregate output cap, finite trial/capture counts and monotonic outer bounds.
Refuse existing output directories and overlapping active acquisition leases.

No driver will launch or move a pointer until an explicit reviewed acquisition
mode is selected; a default planning/validation mode does no UI/runtime work.
Geometry must include window ID/bounds, display scale, actual slider/bar/crop,
two target points and calibrated old/new knob centers with saved pilot frames.
No observer-version or classifier claim can come solely from caller assertions.

## Ordinary control collection

Keep 20 valid responses/arm, four5-response blocks in AB,BA,BA,AB order,
prospectively fixed baseline median +20%, no overhead subtraction or p95 claim.
Retain template/seed attempts, missing/ambiguous responses and exclusion reasons.
No automatic replacement of exclusions; stop dependent collection and let root
choose a new cohort if readiness/routing/classifier/ownership fails.

Boundary: first independently classified new knob center within calibrated
2pt tolerance on an owned complete frame whose displayTime AND presentation PTS
are >=physical input t0. Require distinct pre-input old center, qualified
post-input new center and exact retained target identity. RC seek/current-time
responses are separate diagnostics, never the denominator or completed-seek proof.
Phase-only AX receipts remain pre/post ownership, not per-frame ownership.

Pilot both master arms under the same surface/display/fixture: actual input,
pre/post centers, no-input negative capture, occluded/unfocused/terminated target
refusal, classifier-positive saved images and identical geometry. This needs a
master-aware observer build (external driver input) and approved pointer mechanism.
Old probe cannot be used unchanged. New observer source adaptation is outside
this two-driver lane and needs a root-selected owner/scope.

## Three matched playback pairs

Use the legal7200s `preparation-two-hours.mp4` and manifest under
`work/story005-public-playback-long001`; pin source/generated SHA256, streams,
framehash and first-minute PCM before/after. Start with the proven empty-window
readiness then explicit media open; do not use inherited paused-zero/seek-resume.
Require fresh current playing/counter barriers and a qualified master-aware
window/display plus owned-app audio observer. Pair orders AB,BA,AB,60s per arm;
shorter acquisition is only setup. Use identical approved pointer-hover schedule
in both arms if retaining the earlier exposure protocol; no clicks during playback.

Record actual frame PTS/display/callback boundaries separately, audio RMS/silence
and capture gaps, playing-state observations, decoded/displayed/lost-picture
counter deltas, app/owned-worker CPU/RSS and shared-host load. Unchanged screen ROI
is a candidate repeat, never causal stall attribution. Keep the1percentage-point
dropped-picture allowance; no playback pass if audio/observer/state evidence fails.
The old observer's burned-counter ROI logic must be checked against the new
fixture's first-minute framehash; a long fixture alone does not validate it.

Preparation witness proposal without production tracing: use a fresh explicitly
owned candidate cache, record its bounded manifest snapshots plus exact helper
identity, and compare newly completed target aliases against all recorded hover
request targets. New alias times not requested by any hover establish proactive
completion; helper existence/CPU or pixels alone do not. Require such completions
near beginning and end, preferably every10s bin, and preserve gaps. This is a
sampled completion witness, not continuous decoder occupancy. Root must approve
this witness and its sampling overhead (matched baseline empty-cache sampling)
before collection. Existing native7/8-cache-image observations do not prove60s
active work. If finite preparation finishes early, exclude the trial;7200s media
duration is not permission to assume a queue stayed active. No missing traces may
be inferred as jobs or preview deliveries.

## Decision requested before broad code

The observer/classifier and active-preparation seams are not yet straightforward.
Do not create nominally runnable drivers that silently accept stale observer IDs,
invent receipt APIs or weaken active-preparation proof. Root should choose the
external master-aware observer adaptation owner, qualify geometry/classifier and
approve the cache witness (or another independently observable witness). Then the
two Python drivers can be small explicit-input orchestration around those actual
capabilities, with syntax/offline-parser checks before native handoff. Native
qualification and acceptance remain root-owned; this note makes no measured result.


## Approved adapter implementation and offline freeze

Root expanded ownership to four NEW master-specific sources; the old observers,
session harness, native pointer implementation and product sources remain intact.
The preceding proposal is historical. Root selected a background-preparation-only
playback cohort with the pointer parked outside the timeline; no hover schedule is
used and no simultaneous-hover or worst-case playback claim is permitted.

The implementations are `tests/story-005/master_control_trial.py`,
`master_playback_trial.py`, `master_control_response_probe.m` and
`master_playback_capture.swift`. All app/bundle/PID, fixture/manifest, socket,
geometry, output and observer paths are explicit inputs. All inputs/outputs are
confined to owned work except the narrowly validated read-only production cache:
`~/Library/Caches/<exact isolated Story005 bundle>/TimelineThumbnails`. Its setup
receipt must match exact bundle/PID/UID/path and preserved original cache plus fresh
empty-before-media-open state. Cache ancestors reject symlinks; the exact cache
and bundle parent require current-user ownership and no group/other write access.
The adapters never create, clear or write these caches. Native setup owns that work.
Default driver mode validates only. Acquisition requires an exact reviewed plan
hash and exclusive root/native handoff; controls additionally require CG input
permission and live qualified positive/negative observer pilot receipts for both
arms. App processes are attached and never killed; spawned observers have bounded
owned process-group termination/reaping. Fresh outputs, a 1 GiB free reserve and
512 MiB output bound are enforced. Candidate007 is supplied explicitly, with no
old nativecandidate or VLC3.0 path defaults.

Offline receipt: `work/story005-master-adapter-offline001/freeze.json`, with exact
source/binary/receipt hashes. Both native observers compile without diagnostics;
both Python drivers pass AST/help checks. The prospective matched-arm classifier
is fixed at RGB minimum 190 and width 12..48 pixels at scale 2, with five center rows,
minimum three consistent rows, unique cluster and at most 2 pixels center spread.
Existing candidate main/native/detached images give centers 317.5/577.5/783.5 points;
saved baseline main gives 238 points. All have five consistent rows and widths
36/36/36/36/34 pixels. A real empty candidate-bar crop gives no valid knob.
These saved images establish pixel applicability only, not live timing or ownership.

Fresh RC barriers now require exactly one numeric state 3 playing or state 4 paused,
exact file URI for the manifest-pinned name/hash/size, and a counter-block terminator.
Five handcrafted protocol-string checks accept playing/paused and reject numeric
state 4 posing as playing, wrong URI and missing terminator. They are parser checks;
actual master RC output/counter parsing must be qualified by a bounded setup pilot.

Controls retain 20 valid trials per arm in AB,BA,BA,AB blocks, report medians against
baseline+20%, and preserve exclusions without replacement. The timing boundary is
exact tagged routed input to complete ScreenCaptureKit frame displayTime of the
rendered knob; media/frame source time and completed seek are separate.

Playback remains three matched 60 s pairs AB,BA,AB. An initial cache snapshot occurs
entirely after t0 and must end before t0+0.75s. Six further snapshot reads begin at
9.25/19.25/29.25/39.25/49.25/59.25s and must finish before their nominal endpoint
minus0.1s. Thus target-set differences are bracketed wholly inside the measured
60 s, including near its beginning/end. Reads crossing deadlines exclude the trial.
Each bin must add exact target aliases with valid selected-source/track/render key,
referenced payload digest/shape/time/selection and the same retained worker PID,
start/executable/parent/input context. Early-finished preparation excludes rather
than assumes activity. Manifest read start/end bounds are retained; synchronous
atomic cache writes support sampled completions, never continuous occupancy.
The observer checks foreground/window/pointer every 100 ms; periodic focus commands
are removed so they cannot consume the endpoint witness budget. The screen/audio
capture begins before t0, spans t1 and retains actual displayTime/mach conversion,
PTS and callback boundaries separately. Baseline uses the same snapshot cadence
with an empty owned cache. CPU/RSS are sampled separately for app and helper.

Next bounded live pilot requires native setup-owner agreement and a new explicit
root release: both-arm classifier positive/negative and routed ownership; actual
numeric source/state/counter barriers; exact worker argv/start parsing; small real
cache alias/payload snapshots and their cost; actual screen/audio host-clock
coverage. Capture/read costs may invalidate the prospective deadlines and must be
reported, not silently loosened. No scored control or 60 s cohort collection follows
a desktop handoff automatically. Independent source review precedes live pilot.

## Bounded live calibration protocol (not yet authorized to run)

Independent reviewer cleared freeze `b6554cd5a7acb9b56cd232bf1cc5717b3efc85e2cbbd7487326b44a69f7d6ccb`
for calibration. Native owner currently retains desktop control for its functional
follow-up. A new explicit root release and native-owner setup receipt are required.
The calibration budget is 10 minutes from handoff, one attempt per case, with no
scored collection, replacements or retries. Stop on ownership, authorization,
reserve, capture or parser failure; preserve the failed attempt and remaining cases
as unattempted. Outputs use one NEW owned `work/story005-master-calibration-<id>`
directory, never existing recordings. Root chooses the exact ID at handoff.

Native setup receipt must supply, separately for both arms: absolute isolated app,
exact bundle identifier, executable SHA256, actual PID and start identity, RC socket,
legal fixture and manifest SHA256, exact current source URI, CG window ID/frame,
scale and AX timeline rectangle. Candidate domain007 is explicit; the old
nativecandidate domain and an unproven PID are not acceptable defaults. Native
owner opens the legal source using its established clean-media readiness procedure;
no inferred paused-seek-resume workaround is introduced. It confirms current source
and state using fresh RC output, and supplies no-input pre/post window screenshots
with independently inspected knob-center bounds. Both arm classifier profiles stay
fixed at `[190,12,48]`; do not fit a new threshold after seeing results.

The frozen control observer requires an input action and caps its crop at 400 points
wide by 100 high. Use a localized timeline crop covering the two qualified test
positions and their pill extents, rather than passing the full 511-point main bar.
The native setup receipt supplies those coordinates and independently observed
centers; the clicked point alone is not a measured center. The no-input negative
uses a native no-input window screenshot and the existing saved-image mode, since
neither `--move` nor `--click` is an observe-only command. Do not add another observer
or silently treat a movement event as no input.

Commands below are structured argument recipes; substitute only values from the
reviewed native receipt. Use existing `master_control_trial.run(argv, out, name,
timeout)` for owned process-group guards and fresh stdout/stderr. It never terminates
attached VLC. The two binaries are the frozen compiled executables under
`work/story005-master-adapter-offline001`; verify their freeze hashes first.

1. Capture the current owned window without input:
   `['/usr/sbin/screencapture', '-x', '-l', str(window_id), str(fresh_png)]`
   with a 5-second command bound. Native `focus`/`inspect` checks must identify the
   exact owned app/window before capture. This records only that window, never an
   unrelated app or whole desktop. Confirm PNG dimensions/scale against the frame.
   Inspect the actual pill bounds independently; store measured center/uncertainty.
2. For each arm, one right seed and one left positive, each bounded to 12 seconds:
   `[control_probe, '--bundle-id', bundle_id, '--classifier', '190,12,48', '--pid',
   str(pid), '--expected-executable', executable, '--rect', crop_csv, '--point',
   point_csv, '--click', '--count', '120', '--duration-ms', '2000', '--ax-mode',
   'phase', '--output', fresh_jsonl, '--save-last-image', fresh_crop_png]`.
   Acquire independent no-input window screenshots before/after; compare observed
   knob centers with the complete readiness/post-input frames. Require exact
   nonce-tagged move/down/up routing, retained foreground/app/executable/window,
   owned pre/post AX, complete frames, displayTime/timebase and no capture errors.
   Report calibration only; do not include these values among the 20 scored trials.
3. Each arm's no-input negative: take a no-input screenshot as in step1, then run
   `[control_probe, '--classify-saved', descriptor_json]` with a 5-second bound.
   Descriptor uses exact screenshot window origin, scale2, fixed classifier and an
   independently selected timeline crop that excludes the actual knob. Require
   `knob.valid == false`, no input posting/routing and no implied latency result.
4. One candidate refusal for each staged condition, with the same frozen positive
   command and a distinct fresh output, bound12 seconds. Unfocused: native owner
   activates the other isolated OWNED arm; confirm target is not foreground.
   Occluded: native owner uses an owned same-app window/dialog over the input point
   and records AX hit/geometry showing the point is not its slider. Terminated:
   native owner exits a genuinely owned calibration target, retains its PID/start
   receipt and verifies it is absent. No fabricated PID or user-app foreground
   tricks. Require nonzero exit, explicit ownership error, and ZERO `input_posted`
   and `input_routed` records. Do not invoke a negative unless its staged preflight
   evidence is present. Termination is last; native owner owns any later relaunch.
5. Fresh RC/parser pilot: set `arm['fixture']` from the exact manifest-qualified
   fixture and call `rc_barrier(arm, 'pause')` for each paused control arm. Native
   owner separately establishes actual playback; call `rc_barrier(arm, 'play')`.
   Preserve full raw replies/read intervals; require state4/state3 respectively,
   exact source URI, counter terminator and all six nonnegative decoded/displayed/
   lost video/audio counters parsed by `master_playback_trial.counters`. A state
   transition failure is a pilot exclusion, not permission to invent a core fix.
6. One 8-second screen/audio pilot per playing arm, each bounded to 15 seconds:
   `[playback_probe, '--bundle-id', bundle_id, '--expected-executable', executable,
   '--pid', str(pid), '--window-id', str(window_id), '--timeline-rect', timeline_csv,
   '--roi', roi_csv, '--owned-display-audio', '--duration', '8', '--output',
   fresh_capture_directory]`. Park the pointer outside the timeline before launch
   and keep it there. Require exact owned active window, no microphone/unrelated
   audio, complete screen frames, actual displayTime conversion, audible owned
   audio, finite PTS/callback stamps and coverage for this short pilot interval.
   Verify same-host clock conversion against recorded before/after host timestamps;
   this does not qualify a 60-second trial or causal screen-stall attribution.
7. Real cache pilot: native owner supplies an exact isolated real cache path/setup
   receipt and selected source/track/render key/header fields. Call `cache_snapshot`
   and `process_snapshot` at three native-agreed points two seconds apart. Preserve
   exact target sets/differences, manifest/raw hashes, header shape/time/selection,
   helper PID/start/executable/parent/input arguments and read bounds. Validate the
   actual schema and ps/counter output, plus per-snapshot cost against the prospective
   0.75-second witness budget. This is a small parser/cost pilot, not continuous
   occupancy or six qualifying 10-second bins. Apply the same sampling cadence to
   the baseline empty observer namespace.

Cache setup decision: root selected metadata-only source-equivalent isolated cohort
domains008/009/010, one fresh candidate namespace per scored playback pair, plus
dedicated fresh domain011 for the short schema/audio/capture pilot. Domain007 and
its functional records stay intact; a saved007 census is supplementary only. The
same frozen fresh validators apply to011: no require_fresh exception, fabricated
empty receipt or additional-manifest allowance. The pilot must not consume008/009/010
or claim six qualifying bins from its short captures. Build owner prepares four
metadata-only clones within its existing bounds. Native setup supplies exact011
bundle/app/PID/start/socket/source/window/cache path and fresh-empty/ownership
receipt, alongside the baseline setup. No cache deletion, work symlink,
SafeAncestors bypass or daily-cache access is permitted.

Prospective main geometry, conditional on native owner confirming BOTH arms' CG
frame `[208,392,896,456]` and timeline y798/h17: common crop `[300,798,320,17]`,
points `[350,806.5]` and `[570,806.5]`. These fit both previously recorded main bars
and the observer's400-point cap, with room around both pills. Native owner must
independently inspect the actual pre/post centers; these inputs are not presumed
centers. If geometry differs, stop and prospectively freeze new shared geometry
before any input. Root review and setup agreement remain required.

A successful calibration yields both-arm geometry/observer pilot receipts and real
schema/clock/counter receipts for root review. It grants no permission to start the
20-per-arm controls or three matched 60-second pairs. Those need the final reviewed
plan, fresh source/cache setup and another exact acquisition handoff.


## Revised setup and paused control clarification

The first calibration stopped before media/input/observer acquisition. Original
receipt directory: `work/story005-master-calibration-20261006-0800`. Its owned
baseline PID42243 exited on the invalid launcher option `--no-video-autoresize`;
the established option is `--no-macosx-video-autoresize`. The subsequent CUA bind
timeout is setup evidence, not an SCK or product result. No retries ran in that
attempt. The original freeze and all failure receipts remain preserved.

Root selected a pristine metadata-only baseline012 to avoid touching an unproven
006 auto-launched instance. Revised calibration uses baseline012/candidate007 for
controls and separate fresh baseline012/candidate011 sessions for playback. All
identities/PIDs/geometries are acquired afresh; none come from terminated sessions.
Native owner verifies exact owned launch process alive, CLI socket, visible empty
window and executable/domain before CUA bind or admitting media. Root approves that
preflight before ONE revised bounded pilot. Native owner is the sole desktop actor;
this builder supplies recipes and analyzes artifacts read-only.

Control cohort: native owner starts ordinary playback on the legal300-second
fixture, confirms current source/playing state3, then uses actual Pause and confirms
state4 before the right seed/left positive. The metric is paused rendered knob
feedback only. Do not resume a session after these seeks: stop the owned session.
If paused pixel knob feedback fails, stop with calibration inconclusive; do not
switch to playing or change acceptance. This is a prospective local experiment,
not an inferred paused-zero workaround or a completed-seek/media-clock claim.
Playback uses newly opened independent baseline012/candidate011 sessions on the
legal7200-second fixture, with no preceding control fixture admitted to011. Its
fresh namespace must contain only that source/key manifest. Receipts/plans and
source/fixture hashes remain distinct across modes; clone equality cannot transfer
media or observer acceptance across them.

Updated strings-only control freeze:
`work/story005-master-adapter-offline001/freeze-paused-cohort.json`. Original
`freeze.json` stays untouched. Updated Python AST/help checks pass; observer source
and binary hashes are unchanged, so no native recompilation occurred. Scored
collection remains unauthorized pending calibration and root review.


## Diagnostic-only asynchronous stream/request-boundary correction

The0918 controls calibration qualified baseline playing3 then Pause4 source/counter
and pregeometry checks, but stopped on candidate's first strict playing barrier.
Its raw failure reply was lost; no observer, control seeks, positive/negative or
refusal cases ran. Cleanup211.640 seconds was within the600-second bound. Native
receipt explicitly records one reveal movement after failure caused by dependent
orchestration before inspecting the failed result. Future actor calls must be
sequential: inspect/persist each result, stop on failure, then permit dependent input.

General problem class: asynchronous stream/request-boundary observability. Bounded
research reused pinned `modules/control/cli/cli.c`370–424 and `player.c`55–93,
960–1013. Requests and player broadcasts share a per-line output lock and grammar;
there is no batch request identifier. This supports preserving observed bytes and
bounds before validation; it does not establish why0918 failed or justify accepting
multiple states/sources, unknown states or truncated replies. Native owner's
`work/story005-candidate-rc-readiness-plan-20261006-0913/research-note.md` retains the
full pinned-source inventory and observed admission transition, separately from
the lost failure reply.

`RCBarrierError.evidence` now contains request, socket, expected source URI and
state, read start/end, decoded raw reply plus exact base64 bytes, retained-byte count,
truncation marker and error type/message. Socket creation/connect/send/receive/close
and parser failures retain this structured evidence. A256 KiB diagnostic cap rejects
an oversized reply and preserves its bounded prefix explicitly as truncated. Both
driver exclusions persist `barrier_failure`; playback preserves it before observer
cleanup can raise a separate error. Successful return shape and strict `validate_rc`
source are unchanged. Independent callers must catch `RCBarrierError`, write its
JSON-safe `evidence` under fresh owned output, and STOP before any dependent input.

Offline fake streams cover valid playing/paused, wrong state/source, duplicate
state/source, truncated EOF, creation/connect/send/partial receive/close errors,
invalid UTF8 and oversized reply, plus both real driver exclusion/persistence paths
with acquisition mocked. Sixteen checks pass; no real socket, app, observer or UI
ran. Existing parent parser acceptance matches in all12 representative comparison
cases, and its function source is exactly unchanged. Both Python AST/help checks
pass. New native recompilation is unnecessary: observer sources/binaries unchanged.

Preserved parent Python source copies: `work/story005-master-adapter-offline001/
rc-diagnostics-parent/`. Original freezes remain untouched. Reviewable successor:
`freeze-rc-diagnostics.json`, exact `rc-diagnostics.diff`, offline receipt
`rc-diagnostic-offline.json` and check source under the same ignored directory.
This diagnostic freeze does not release another pilot or scored acquisition.

## Diagnostic successor — 2026-10-06 09:16

0918 controls calibration stopped before observers at candidate strictplaying
barrier; original rawfailure was lost. Diagnostic successorfreeze SHA256
68e6cd3d24a4596b0002dfe10bad6b026f8d24bb989e20d2644064ce79101666
retains bounded exactbytes/base64/readbounds/request/expectedsource/state/socket
and original error in RCBarrierError.evidence. Both drivers persist barrier_failure.
validate_rc is source-identical to aa401b; successful ASCII replyshape is unchanged.
New256KiB cap is failclosed; native observer sources/binaries remain frozen.
16 scopedofflinechecks and independentreview pass. This is diagnostic proof, not
livequalification. Root releases one candidate007-only120s immediate rawbarrier
experiment, no pointer/Pause/observer/repeat/scoring, with exactliveidentitybrackets
and timestampedcleanup. Furthercohorts depend on actualdiagnosis.
