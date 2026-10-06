# Retained application identity for ordinary-control observation

2026-10-05. Prospective observer v4; implementation and headless checks only.
No native applicability, timing qualification, or historical-result salvage.

The general problem is durable process identity during asynchronous observation.
The installed AppKit SDK's `NSRunningApplication.h` documents that instances
remain valid after an application exits (lines58–59), and expressly directs
callers to use `isEqual:` rather than PID comparison for process identity
(lines103–107). Time-varying properties still require a serviced main run loop
in a common mode. Retaining an instance does not make these properties atomic
with a captured frame's presentation or eliminate race conditions.

Primary sources:

- [Apple NSRunningApplication](https://developer.apple.com/documentation/appkit/nsrunningapplication?language=objc),
  including instance lifetime and run-loop freshness.
- [Apple processIdentifier](https://developer.apple.com/documentation/appkit/nsrunningapplication/processidentifier),
  with the installed SDK's explicit `isEqual:` direction.
- [Apple NSWorkspace frontmostApplication](https://developer.apple.com/documentation/appkit/nsworkspace/frontmostapplication),
  identifying the application receiving key events.

Decision: validate and strongly retain one target at readiness, including owned
PID, expected bundle, exact canonical executable path, process existence, and
nontermination. Never retry acquisition or replace this retained target during
the capture. Every callback compares a fresh frontmost instance with that target
using `isEqual:`, and checks the expected identity, termination and OS existence.
Fresh per-PID lookup results remain explicit diagnostic fields; an absent lookup
does not replace the target or independently decide ownership. Exact CG window
and crop guards remain on every callback. AX ownership remains mandatory for
every complete presentation, with pre/post AX checks and nonce routing unchanged.

The new policy is `workspace-frontmost-retained-instance-v4`, observer version4,
runner schema4. The probe requires `--expected-executable` supplied from the
runner's exact owned executable; session and frame records expose the retained
and expected paths. The runner rejects older versions and identity mismatches.
The preserved v3 source/runner/binary hashes live under ignored
`work/validation/story002/control-retained-target-v4-001/`.

Local checks: warning-clean native compilation, five pure-pixel cases, Python
syntax, and offline parser mutations covering valid records, diagnostic-only
lookup absence, identity/termination/path/AX/window failures and preinput frames.
These checks do not demonstrate native `isEqual:` behavior or responsiveness.

Remaining qualification: root owns positive native controls plus independently
corroborated foreground-departure and target-termination negative controls.
Both negatives must reject observation; a later foreground restoration or a
retained object surviving exit must not salvage the capture. All earlier v3
failures remain preserved and unqualified. Any matched performance cohort must
use the same qualified observer version in both arms and retain Cam's baseline
plus0% allowance. This change establishes no cause for a historical failure.

## Prospective readiness acquisition correction,2026-10-05

The pragmatic comparison001 stopped at baseline block0click3 before posting
input: frontmostPID62322 and developmentbundle were correct, but the separate
per-PID NSRunningApplication lookup returned nil. Three measured baseline
responses do not salvage that cohort. This is harness readiness failure, not
a measured product slowdown or evidence of user interference.

Use the single NSWorkspace.frontmostApplication instance at readiness, then
validate it against exact ownedPID, canonical executable, bundle, OS existence
and nontermination before retaining. No retry/fallback/replacement is added.
Acquisition equality with itself is tautological, not independent corroboration;
fresh subsequent foreground equality plus unchanged CG/AX/input/pixel guards
continue to prove observation scope. Session records expose
`readiness_acquisition=validated-frontmost-instance`; binary/source hashes
distinguish the prospective v4 acquisition variant from earlier captures.
The existing native positive/foreground-loss/owned-termination qualification
is rerun before collecting a fresh whole pragmatic cohort. Source correction
does not modify either product app or retroactively qualify older samples.
Compilation retains the existing unused-callback-parameter suppression; five
pixel cases pass. No new capture framework or completed-seek claim.
