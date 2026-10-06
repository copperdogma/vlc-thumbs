---
title: "Separate durable timeline labels from resume history and thumbnail cache"
status: "ACCEPTED"
date: "2026-10-03"
ideal_refs:
  - ideal:req:persistence
  - ideal:req:annotations
  - ideal:req:media-integrity
spec_refs:
  - spec:2
  - spec:3
story_refs:
  - "001"
related_adrs: []
---
# ADR-001: Media metadata storage and retention

**Status:** ACCEPTED — storage ownership and retention only; format, schema,
media identity and cache policy remain open. Not implemented or runtime-qualified.

## Context

Cam asked where VLC remembers a video's playback position and whether thumbnails
and timeline bookmarks should use the same storage. After the explanation of
separate durable labels and disposable thumbnails, Cam said “that sounds good”
and requested this ADR.

The pinned macOS VLC 3.0.24 source stores resume positions in NSUserDefaults:
`recentlyPlayedMedia` maps decoded media URIs to integer seconds, and
`recentlyPlayedMediaList` tracks recency. The usual preference domain is
`org.videolan.vlc`, persisted by macOS under
`~/Library/Preferences/org.videolan.vlc.plist`. The code uses NSUserDefaults,
not direct edits of that file.

This is recent playback history, with at most 30 retained resume entries. Entries
can also be removed by position-retention rules; clearing recent documents clears
both resume keys. It is not a durable per-video catalog. Existing named bookmark
input-item options are another useful VLC facility, but do not prove automatic
same-file restart persistence. User-authored timeline labels are one to three
words and must survive routine resume-history eviction and thumbnail cleanup.

## Ideal Alignment

Remembered moments are already present when the video is revisited. Keeping
intentional labels separate from disposable history and generated images serves
that outcome, preserves original videos, and avoids imposing manual saving or
organization. Storage details belong here and in the spec, not in the Ideal.

## Options

| Option | Benefits | Costs / outcome |
|---|---|---|
| Extend existing resume-history records | Reuses current video lookup and preferences | Couples labels to 30-entry eviction, position cleanup and history clearing; unsuitable for images. Rejected. |
| Separate annotation key in NSUserDefaults | Simple for small labels; distinct retention is possible | Technically viable, but couples a growing per-video collection to preferences and does not house image assets. Not selected. |
| Feature-owned durable store in Application Support, images in Caches | Distinct lifetimes, bounded regenerable images, integration with VLC-owned application areas | Requires explicit identity/store contracts and independent cleanup. Selected. |
| Metadata and images alongside each video | Potential portability with the file | Changes the user's folders, requires adjacent write access, and adds move/copy behavior. Not selected as the initial default; export/portability remains future scope. |

## Decisions

1. Reuse VLC's existing media/input access and lifecycle integration where
   appropriate. Preserve normal playback-resume behavior. Existing URI keys are
   a source of media identity, not sufficient proof of replacement/move handling.
2. Store durable timestamped labels in a feature-owned store under VLC's macOS
   Application Support area. Do not add them to `recentlyPlayedMedia` or make
   their lifetime depend on recent-items settings, history limits, playback
   completion, or clearing recent history.
3. Store generated thumbnails separately in a feature-owned area of VLC's macOS
   Caches location. They are regenerable and may be invalidated or evicted under
   a bounded resource policy. Cleanup must never delete or rewrite labels.
4. Keep small feature settings in preferences when appropriate; image data and
   per-video thumbnail collections do not belong in NSUserDefaults.
5. Leave original video bytes untouched. Resolve platform directories through
   supported APIs and select explicit feature subdirectories during implementation;
   do not write directly to the live preferences plist.

Accepted scope is this storage/retention split. It does not select SQLite versus
JSON/plist, a schema, exact folder names, hashing, extraction engine, sampling
interval, quotas, migrations, or a VLC fork. It does not authorize changes to
installed VLC or real user data.

## Research Summary and Evidence

Pinned source: `6de05adcbaf2e8b85fe86aad4169393098628119` (VLC 3.0.24).

- [Resume read/write and retention](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCInputManager.m#L635-L764): URI-to-seconds preferences, recent-items gate, validity checks, position criteria and 30-item retention.
- [Clear recent documents](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/modules/gui/macosx/VLCDocumentController.m#L37-L46): both resume keys are cleared.
- [VideoLAN preference-path discussion](https://mailman.videolan.org/pipermail/vlc-devel/2022-March/143452.html): confirms the macOS preference file and resume meaning. Its older retention thresholds are not used as current-release evidence.
- [Existing bookmark option serialization](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/src/input/control.c#L591-L621): name/time input-item options, including an escaping TODO. Not a qualified durable catalog.

Local source investigation: `docs/research/story-001-vlc-macos-timeline.md`.
The location split is an engineering decision based on these lifetimes; it is
not a claim that VLC already implements this feature store. No private preference
contents were read, no user state changed, and no persistence behavior tested.

## Consequences

Labels survive app restarts, recent-history turnover and disposable cache cleanup.
Thumbnail growth can be bounded without sacrificing the user's annotations.
Separate directories do not solve media identity, atomic writes, corruption,
backup or concurrent access; those need concrete implementation contracts.
Reset/privacy behavior must make deliberate label removal explicit rather than
silently inheriting the semantics of clearing viewing history.

## Dependencies and Affected Surfaces

Story 001 establishes the native source/build and persistence seams. Spec:2 and
spec:3 own cache and durable-label constraints; the root timeline eval owns
end-to-end proof. No dependency ADR exists. No new story is needed for this same
feasibility/persistence work line. The Ideal remains implementation-free.

## Integration Checklist

- [x] Spec:2/spec:3 link the accepted storage/retention boundary.
- [x] Methodology state records the decision without claiming implementation; graph regenerated.
- [x] Story 001 links this ADR and records remaining persistence work.
- [x] Root eval adds history/cache lifetime regression cases, deferred until runnable.
- [x] AGENTS records the accepted boundary; other architecture choices stay open.
- [x] Local storage runbook captures the rules for future implementation.
- [x] Decision index and existing research cross-link the ADR.

## Remaining Work / Research Needed

- [ ] Choose identity for same-file lookup, duplicates and file replacement; assess moves/renames separately.
- [ ] Choose the simplest durable format/schema with atomic writes, recovery and versioning.
- [ ] Confirm supported directory-resolution APIs and actual namespacing in the selected build.
- [x] Define thumbnail freshness, cancellation and size/age eviction bounds independently of labels — ADR-002; fresh media-open namespaces, file-state guards, latest-demand cancellation, 32 MiB RAM/256 MiB disk LRU are exercised in Story 002. No age expiry is used; obsolete session entries are bounded and evicted by disk LRU.
- [ ] Verify restart persistence, over-30-video history turnover, history clearing, recent-items disabled, and cache cleanup using isolated stores.
- [ ] Specify deliberate label deletion/reset behavior and relevant backup/privacy expectations.

Implementation questions are not reasons to reopen the accepted lifetime split
without new evidence. Research follow-up is scoped in the bundled prompt;
no paid or multi-provider research is required by this ADR.

## Discussion / Work Log

20261003 — Source investigation: traced playback resume storage and history
clearing in pinned VLC 3.0.24; recommended separate durable labels and image cache.
20261003 — Cam accepted the direction and requested this ADR. Recorded the
storage/retention decision, alternatives, evidence, consequences and open schema/
identity details. No implementation or product verification performed.
