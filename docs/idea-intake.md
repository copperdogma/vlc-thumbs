# VLC timeline enhancements — original intake

Captured 2026-10-03. The following overview is supplied by Cam. Embedded prior
assistant claims and suggestions are intake, not independently verified findings.

## Supplied overview (verbatim)

Is VLC open source?
Yes. VLC Media Player is open source and free software.

It’s developed by the nonprofit VideoLAN project. Most of VLC is licensed under GPLv2 or later, with some libraries under LGPL licenses.

That means you can inspect the source code, modify it, compile your own version, and redistribute modified versions subject to the license terms. Its source is publicly available, primarily on VideoLAN’s GitLab.

Does it have plugins/mods?

I'm looking for two things to enhance the scrub bar:

thumbnails, so if I make the timeline appear and hover back and forth I'll get thumbnail previews of the video.
bookmarking, so I could right-click on the timeline and annotate it. This would appear next time I open that same video. If I hover over the timeline bar and it appears it would also show each of my little annotations at the time index.
Yes. VLC has both a Lua extension/add-on system and a deeper native plugin architecture. VideoLAN explicitly describes VLC as modular, with hundreds of runtime-loadable plugins, and VLC has supported Lua “functionality extensions” for years.

For the two things you want, though, there’s a catch: VLC’s extension API is much better at adding menus/dialogs/actions than modifying the actual scrub bar UI.

Thumbnail previews on hover: I’m not finding a mature current VLC add-on that adds YouTube-style thumbnail previews directly over the timeline. This likely requires modifying VLC’s UI itself rather than a normal Lua extension.
Persistent annotated bookmarks on the timeline: there are VLC bookmark-related extensions/add-ons, and VLC already exposes seeking/time APIs, but I’m not finding one that does exactly what you describe: right-click timeline → add annotation → persistent visible marker on the scrub bar next time that same file is opened.
What you want is completely feasible technically, especially because VLC is open source. I’d implement it roughly like this:

Thumbnail cache

Generate thumbnails every N seconds, perhaps asynchronously with VLC/FFmpeg.
Store them in something like ~/Library/Application Support/VLC/... keyed by file path + size/modification date.
Hover position maps to timestamp and shows the closest cached thumbnail.
Persistent annotations

Right-click scrub bar → Add Bookmark/Annotation.
Save something like:
{
  "/Movies/foo.mkv": [
    {"time": 613.2, "text": "Great explanation"},
    {"time": 1421.8, "text": "Come back to this"}
  ]
}

Draw little ticks/dots on the timeline.
Hover the tick to see text; click it to seek there.
Ideally allow color/tag/delete/edit too.
Persistence

Don’t alter the video itself.
Keep a sidecar database keyed by a robust media identifier—path initially, perhaps hash + filesize for resilience if files move.
And this is important: because you’re on macOS, VLC’s UI implementation matters. A native source modification would probably be the clean route if the requirement is literally modifying the existing seek bar rather than putting a separate extension window beside VLC.

If you want, I can dig into the current VLC 3.0.24/macOS source tree, find exactly where its seek bar is implemented, and tell you how invasive these two additions would be—whether this is a pleasant little fork or a horrible project.

## Setup request (verbatim)

Grab all of the skills in the boardgame-ingester project one level up from here. Check ultima-iv-web as well.

Then set up this project using them and the setup project guidance (skill?) in there as well.

## Placement and interpretation

The target is `vlc-thumbs`, currently nested under `ultima-iv-web`.
The source projects are `/Users/cam/Documents/Projects/boardgame-ingester` and
`/Users/cam/Documents/Projects/ultima-iv-web`; neither is changed by this setup.
The explicit request authorizes local methodology/skill installation now;
no second import approval is needed. Ideal/spec are v0 drafts derived from this
intake, open to user refinement. No independent product-review approval is claimed.

Product intent: enhance the actual macOS VLC timeline with hover previews and
persistent annotated timestamps. A separate companion window would need an
explicit product decision because it changes the requested interaction.

Candidate techniques: asynchronous extraction, sampled thumbnail cache,
path/size/mtime or stronger identity, sidecar/database, native UI patch.
None is an accepted architecture. VLC 3.0.24, licensing details, extension limits,
and absence of existing add-ons need current primary-source verification.

Open questions: normal/fullscreen control parity; initial version/build target;
rename/move portability; file replacement behavior; optional colors/tags;
cache budget and measured latency floor; private use versus distribution.
Defaults for planning: local seekable videos on macOS, both normal/fullscreen
controls inspected, same unchanged file persistence, local data, optional
colors/tags deferred. These are provisional defaults, not confirmed preferences.


## North Star correction — 2026-10-03

Cam: “Okay, double check the ideal. It's supposed to be sort of a North Star,
what if we had magic kind of approach. Make sure there's little to no
implementation in there. That should be in something like spec instead.”

Applied: Ideal now describes immediate exploration and effortless remembered
moments. macOS/local-file scope, possible local VLC build, concrete gestures,
byte/hash checks, build/fixture provenance and test procedures live in the spec
and existing root eval. Requirement IDs remain stable; no new architecture or
product validation is claimed.

## Annotation length clarification — 2026-10-03

Cam: “By the way, the notes I'm talking about are like one to three words.
That's it. It's not a whole paragraph that's going to be attached to a specific
point. So just when we get around to the design, that's what I'm after.”

Design intent: moment annotations are brief labels of one to three words.
Design entry, markers and hover presentation around that scale. This is a
content/design preference; no hard word-count validator is requested.


## Initial build authorization after disk check — 2026-10-03

Cam: “Okay, whatever. Just try the initial build like you were planning to do
and we'll see what happens. If I don't have enough space, we'll just delete the
build artifacts and we'll figure it out.”

This supersedes the earlier capacity deferral: attempt the unmodified build in
a disposable project-owned workspace, monitor free space, and remove that
attempt's generated workspace if disk runs short. Preserve pristine source,
project files, logs and unrelated data. The earlier 30 GiB suggestion was an
unmeasured planning allowance, not a demonstrated VLC requirement.

## Feature planning request — 2026-10-04

Cam: “Go for it. Deep dive and planning out the work. Make it into one story
for thumbnails and one for bookmarks, I'd think.”

Plan two complete user-facing feature stories, supported by source/build and
bounded feasibility evidence. Keep implementation in spec/stories/ADRs and
preserve the short-label intent. This request authorizes planning, not a new
feature implementation, commit or push.

## 2026-10-04 — MVP preview sampling clarification

> As a MVP we could just use keyframes. It’s not like the requirement was
> “render every single frame at every single point on the timeline”. It’s just
> a way to get a sense of what’s around there so you can find the general spot
> on the timeline you’re after. If keyframes are too coarse we can render
> additional ones at greater expense.

This authorizes keyframe-first MVP sampling. The Ideal remains the North Star;
implementation and acceptance tradeoffs are recorded in spec:2, ADR-002 and
Story 002. No extra sampling is required before trying the MVP.


### 2026-10-04 — preview responsiveness MVP acceptance

After trying the native previews, Cam approved changing the initial engineering
criteria to150ms cached-preview p95 and200ms initial time/loading p95. Disk
previews150ms and uncached images1s stay unchanged. Original100ms failures are
preserved; this changes the MVP contract, not the implementation-free Ideal.

## NAS preview follow-up story request — 2026-10-05

After reviewing the large SMB-file investigation and proposed reusable worker,
cache, preparation and error-state changes, Cam said:

> I like all of that. Write that up as a new story.

Cam proposed prioritizing the current hover, then expanding in both directions,
letting active thumbnail work finish, and filling from the beginning when there
is no hover. Cam also requested inspiration from established players without
copying their choices uncritically, and asked for stored thumbnails to be reused
after closing and reopening a video. Story 004 records that direction, finite
sparse coverage, persistent disposable-cache retention and explicit identity/
lifecycle decisions. This request creates the story; implementation has not
started. Original Story 002 validation remains scoped historical evidence.
