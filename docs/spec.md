# VLC timeline enhancements — Spec v0

This is the initial constraint map, derived from `docs/idea-intake.md`.
Unknown technical constraints are research questions, not measured failures.
No VLC version, plugin limitation, decoder, cache layout, or storage architecture
has been qualified. No AI inference is required by the product intent.

## spec:1 - VLC integration and delivery

Serves `ideal:req:annotations`, `ideal:req:previews`, `ideal:req:playback-quality`.
Product need: interactions on VLC's actual macOS timeline. Technical need:
identify the owning controls, event handlers, extension hooks and build path.
Current scope compromise: macOS first, local seekable videos, and local
development delivery; other platforms and public packaging deferred. A locally
built VLC is a possible first delivery if feasibility supports it, not an Ideal
requirement. Type: ecosystem/human scope.
The excerpt's suggestion that a native patch is necessary remains unverified.
Compare existing capabilities, Lua extension, native module, and UI patch against
both required interactions before selecting a route. Pin source revision,
macOS/build target and dependency provenance. Evolution: prefer upstream-supported
hooks if they meet the experience; retire a maintained fork when that becomes
possible. Root eval: root-timeline-experience. First story: 001.

## spec:2 - Thumbnail correspondence and responsiveness

Serves `ideal:req:previews`, `ideal:req:playback-quality`.
Product need: recognizable preview at the pointed time without seeking playback.
Potential limitation: decode cost, keyframe spacing, duration and display geometry
(physics/ecosystem); no performance measurements yet. Candidate compromise:
asynchronous sampled previews with cache/loading state. Sampling interval,
resolution, extraction engine and budgets remain undecided. Determine time/frame
error, cold/warm latency, playback impact, cancellation and resource bounds with
known frames and durations. Evolution: reduce sampling/cache complexity when a
simpler decoder path meets the measured interaction target. Remove stale previews
on media switch. Root eval owns proof; child benchmarks deferred until a decoder
and UI candidate exist. No invented benchmark results or timing floor.

## spec:3 - Annotation persistence and media identity

Serves `ideal:req:annotations`, `ideal:req:persistence`, `ideal:req:navigation`,
`ideal:req:media-integrity`.
Product need: durable correct notes and markers without altering media.
Annotation design preference: labels of one to three words. Entry and timeline/
hover presentation should suit short labels. Paragraph authoring is outside the
intended experience; a hard word-count limit has not been requested.
Technical acceptance: previews and annotations leave video bytes unchanged;
verify original hashes before and after the scenario. Notes and media remain
local by default in the initial implementation.
Initial scope: same unchanged local file; moved-file and cross-device portability
remain undecided. Type: ecosystem/human scope. Candidate compromise: local sidecar
or database; path/size/mtime versus stronger identity needs evidence. Cache identity
and annotation identity may have different lifetimes. File replacement must not
silently inherit unrelated notes; cache invalidation must not erase annotations.
Test restarts, duplicates, changed/replaced files, save failures and invalid data;
choose atomic write/migration strategy only with a concrete schema. Evolution:
simplify identity and storage when durable system-provided identity meets the
contract. Colors/tags/export deferred. Root eval owns persistence proof.

## spec:4 - Interaction quality and behavioral proof

Serves `ideal:req:playback-quality`, `ideal:req:navigation`, `ideal:req:evidence`.
Product need: markers, hover text, right-click add, edit/delete and marker seek
coexist with scrubber dragging, controls reveal/hide and playback. The requested
initial interaction is hover for previews and annotation text, right-click a
timeline position to add a note, and select a marker to seek. These gestures
express the intake preference; they are not the only possible realization of
the broader Ideal. Type:
ecosystem/physics. The normal/fullscreen UI mapping is unknown; inspect both
before promising parity. Candidate compromise: fixture-driven macOS UI checks
plus storage/decoder checks. Include overlapping markers, end/start boundaries,
scaling, unavailable duration, loading/error states, keyboard and accessibility.
Evolution: retain a small regression suite while simplifying instrumentation.
The initial proof scenario uses a legally usable known video: hover known
positions, add/edit/delete notes, play and seek, quit the entire app, reopen the
same file, inspect restored markers/text, and select a note. Verify frame/time
correspondence, seek target, restart persistence, playback behavior and original
video hashes. Record the VLC source/build, macOS version, fixture and tested
surfaces, including normal/fullscreen controls where supported and unavailable/
loading states. Detailed procedures belong in `docs/evals/root-timeline-experience.md`.
Root eval is a planned contract; no product runner or golden media exists yet.

## spec:5 - Project workflow and source obligations

Serves `ideal:req:evidence`, `ideal:req:media-integrity`.
Build need: repeatable source/build decisions and reviewable small changes.
Current execution compromise: intake, Ideal/spec, state/graph, stories, skills and
local checks (AI capability); no measured AI failure yet. Deletion eval deferred
until implementation supplies a repeated build task with a meaningful baseline;
then measure whether a lighter process preserves correct results. Keep evidence
and the user's chosen review involvement when simplifying. Licensing is a legal
constraint: verify selected source/library obligations before distribution;
this setup makes no distribution decision. Imported skill examples are overridden
by VLC-local runbooks, not treated as product requirements. Source projects stay
read-only. No port range is allocated; a native application needs no web port.
If a local web/API runtime is later introduced, obtain Conductor allocation then.
