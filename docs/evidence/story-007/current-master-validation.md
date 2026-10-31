# October13 historical submission qualification

Historical snapshot only. The fork/access/monitoring statements below describe October13, not current state. The October30 refresh is recorded in [upstream-refresh-20261030.md](upstream-refresh-20261030.md); it must pass its own applicable gates.

October13, 2026: applicable build gates PASS. Submission itself is pending fork
import and local SSH unlock; no upstream branch or MR has been published.

Base: `392bc1d0abdb7396b6c97fef206efa1d23868e19`.
Head: `8ef6bd094a0c48727e155417a4a07aad617680c3`.
Tree: `85cdddd06a1324ca43e620d40b76f54f4d023e39`.
The clean isolated submission branch contains fourteen commits/72 changed paths,
authored by Cam Marsollier <cam.marsollier@gmail.com>. Original thirteen commit
bodies are preserved after rebase. The additional four-line Darwin test linker
fix retains the dynamically discovered fixture table under current dead stripping.
Production linker behavior and test assertions are unchanged.

| Check | Observed result |
|---|---|
| Fresh bootstrap/configure/normal build/package and conventional signing | PASS |
| Full registered normal check | PASS, 167.77s; groups6/30 (29pass,1skip)/25/94/host1 |
| macOS XCTest | 266 cases:265pass,1skip,0fail; context7 and reentrancy11 also pass |
| Complete conventional distcheck | PASS exit0,598.810s, archives-ready banner; groups6/30 (29pass,1skip)/25/93/host1 |
| Actual current helper protocol |13 cases executed per normal and archive helper, PASS |
| Positive helper decode | Retained legal MP4/MKV fixtures PASS; header fields excluding elapsed operation time and pixels match retained references |
| Source preservation | Submission clean; owned build source retains99 generated PO/POT paths only; no translations in submission |

The conventional archive configuration disables optional Lua and therefore has93
integration cases versus94 in the normal configuration. Prior77 helper checks
remain predecessor evidence, not fresh current-base execution. Minimum observed
free space was42,581,917,696 bytes; no owned build executable remained at terminal.

The first normal check failed15 integration cases because current Darwin dead
stripping removed the mock table. Failed flag experiments remain preserved;
the final quoted wildcard export passed both a real EOF case and fixtureless
core before the complete suite. The first distcheck stopped on missing shallow
clone metadata; boundary metadata was repaired only in owned clones, reachable
objects verified, and the complete successor passed. Neither failure is erased.

There are no contribution production-file/changed-line warnings in the normal
build. Archive tests emit17 unchanged link-only shell warnings, identical to the
qualified predecessor log; lifetime tests pass. The tree is not warning-free.
Thirteen inherited whitespace entries occur inside nested FFmpeg patch context;
the new commit's whitespace check passes.

Private raw evidence is retained under ignored
`work/story007-current-master-gates001/`: `REPORT.md`, `final-receipt.json`,
`executed-commands.json`, `commit14-receipt.json`,
`actual-current-helper-execution.json`, `positive-helper-smoke.json`, diagnosis,
original failures and logs. These are local provenance, not public source files.

No new native hover/playback/VoiceOver/performance campaign or installed-app
change was performed. Earlier scoped product evidence and its Intel/older macOS,
preview-visible reader, intermittent shutdown causality and seek-precision limits
remain disclosed. Build success does not resolve those limits or establish
maintainer acceptance.

An independent read-only workflow audit confirms account/fork/target/key identity.
The authenticated import page still says “Forking in progress”; absence of a
repository does not establish server failure. The earlier single premature
initialization attempt is preserved and will not be repeated. No email was sent;
Cam forbids email. The separate GPT-6 Luna Low checker is ACTIVE every three hours
for fork readiness first, then actual MR feedback, and reports noteworthy deltas
to the coordinator while staying quiet on unchanged pending state.
