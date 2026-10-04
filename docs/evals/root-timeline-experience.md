# Root eval — integrated timeline experience

Status: deferred contract; no runner and no pass/fail attempt. Parent: none.

Input: a legally usable video with pinned bytes, duration and identifiable
frames/time positions; a pinned VLC candidate, macOS version, screen configuration
and empty isolated project-owned annotation/cache store. Golden workspace:
`tests/fixtures/golden/`. Do not modify the user's installed VLC or real notes.

Expected end-to-end outcome:

1. Open the video; hover known timeline positions including start/end and verify
   recognizable frame/time correspondence without changing playback position.
2. Reveal controls, right-click a chosen position, add a note, and verify its
   timestamp marker and hover text. Add another note, edit it, then delete it.
3. Continue playback and scrub normally. Check loading/failure and media-switch
   states; stale previews/notes must not appear on another video.
4. Quit the entire app, reopen the same video, and verify surviving markers,
   text and timestamps. Select a marker and verify the seek target.
5. Compare original video hashes and inspect keyboard/accessibility behavior.
   Check normal/fullscreen controls and state precisely which surfaces passed.

Before execution: set explicit measured tolerances for preview time/frame error,
seek error, cold/warm hover latency, playback impact and resource use, justified
by source/build feasibility. Log every required capability independently; a
partial pass is not root completion. Include failures and untested scenarios.

Changed/replaced-file identity, duplicate basenames, corrupt/failed note writes,
overlapping markers, duration unavailable and scaling form robustness cases.
Define expected handling before recording pass/fail. Root proof must show both
requested features; a compile, screenshot or isolated storage test cannot pass it.

Future child evals must name their parent and observed failure or a clearly
labeled planned capability question. No model benchmark/PromptFoo is required
for this behavioral proof shape.
