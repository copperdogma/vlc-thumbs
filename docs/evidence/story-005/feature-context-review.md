# Independent frozen context review

Reviewed against `feature-port-plan.md` and pinned master
`2e358f3098c2f2b7621d1dc568de8b61ad786322`. This review inspected source and existing
test receipts; it did not edit product source or run the app/test bundle.
No readiness claim follows from this review.

## Exact reviewed freeze

Receipt: `work/story005-context-proof/receipt-preference-repair.json`.
Paths below are relative to the candidate's `modules/gui/macosx` directory.
Every hash was independently recomputed and matched that receipt.

| File | SHA256 |
| --- | --- |
| `playqueue/VLCPlayerController.h` | `7594a27881387adb1ee071f3ada089e0f4003805672e4aa91526855b8d3fa2a4` |
| `playqueue/VLCPlayerController.m` | `a42a61bc7f2e1ee055f895a72d1534d98da6d9c018819b13190576d0e91f6353` |
| `timeline/VLCTimelineContext.h` | `83054f2032e15c3f93f6c2150d5c3e33174a10be6c4d3a25e60bc47acb766348` |
| `timeline/VLCTimelineContext.m` | `fd62db47d2f1d40fecce341aa19b0bd230ec8f3b6ad4740ea3895c8b043bbc40` |
| `timeline/VLCTimelineContextTests.m` | `eb274df240c87d708c44b6af95230579c28ddeb70190aaee4eee8691d598f378` |
| `timeline/VLCTimelineContextTestSupport.m` | `9820fc0f4e0b406ad89989ecd0ec44fc6be8f08a5e4424320713d3a174c54092` |
| `main/VLCMain.m` | `a4b6c24610624a551b0d8afbf697bcd3cf2ce0522791c4632fdf753e97194867` |

## Material findings

**C1: preference refresh publishes before committing enabled state.**
`VLCTimelineContext.m:138-142` calls preparation and posts the synchronous
`VLCTimelineContextChanged` notification before assigning `_lastEnabled`.
A legitimate notification observer that calls `snapshot` on an effective
preference change enters `refresh` again. The new enabled value still differs
from `_lastEnabled`, so that invocation prepares/posts again. An unconditional
snapshot-reading observer recurses until stack exhaustion. A reentrant prepare
consumer has the same stale-state problem. This follows from the exact code;
the existing test bundle did not exercise the observer pattern.

Minimum correction: commit the enabled state before external preparation and
notification callbacks. Add a synchronous observer that reads `snapshot` during
a preference toggle; assert bounded preparation/notification count and the
expected final preference. Consider nested preference transitions when committing
state so an outer invocation does not overwrite a newer nested state.

**C2: Main's termination path invalidates before stopping the context.**
`VLCMain.m:416-425` invalidates context, shuts service down, then posts termination
notification when invoked with nil. That nil path is called by the actual core
close hook at `VLCMain.m:233`. During the first invalidation notification,
context `_stopped` is still false. A synchronous snapshot reader can refresh the
still-started player's values into an eligible context and call preparation with
enabled true during termination. The context's own termination handler correctly
sets `_stopped` before invalidating, but it runs later in this path.

Minimum correction: enter the terminal context state before the first published
invalidation, and preserve service shutdown ordering. Add a Main-equivalent
termination sequence with a reentrant snapshot observer, asserting that no
eligible context or enabled preparation is published after termination begins.
No actual app restart was executed or claimed by this source review.

## Sound boundaries in this freeze

- `timelinePreviewSnapshot` reads URI, epoch, length, capabilities and selected
  video tracks under one player lock. NSString values are constructed while the
  borrowed ES pointers are valid; no input/track/ES pointer escapes. NSURL
  construction happens after unlocking and performs no filesystem work.
- Stable identity, exactly one selected video, numeric ID, bounded count,
  positive duration, seek capability, started state and local file URL determine
  eligibility. Invalid UTF8/unknown or nonstable selection becomes ineligible.
- Epoch mutation occurs synchronously in current-media and relevant state
  callbacks before main dispatch. The player callback contract explicitly holds
  the player lock (`vlc_player.h:2832`); the snapshot reads epoch under that lock.
  `vlc_player_OpenNextMedia` sends current-media notification when replacing its
  input, including same-item replacement. This supports the intended same-URI
  freshness boundary without comparing input-item addresses.
- Context dictionaries copy their values and compare epoch/identity/duration/
  eligibility before adding generation. Unchanged pointer snapshots do not call
  prepare, so they cannot renew preparation merely by pointer movement.
- Player notifications reread current values rather than trusting delayed
  userInfo. Standard `VLCConfigurationChangedNotification` and the existing
  `macosx-timeline-previews` effective value are used. Program/title refresh
  notifications are included. Startup invokes context after Main constructs its
  playqueue/player.

## Test evidence and limits

Existing `context-tests-run005.log` records6 tests and0 failures for the actual
context class with injected providers and escape stubs. They cover copied values,
same-URI epoch changes before main notification, unchanged preparation, delayed
notification values, selection components, effective preferences and a direct
context termination notification. They do not cover C1/C2's reentrant observers
or the Main-equivalent shutdown sequence.

Player lock/epoch code received syntax/source checks, not a real player/decoder
restart exercise. No live preference/CLI, full-app startup/termination, pointer,
native accessibility or source-reopen proof was performed by this reviewer.
The test support singleton stubs are explicitly isolated-test-only and must not
be linked into the application. Resolving C1/C2 and rerunning focused tests is
necessary; that alone does not establish native acceptance or readiness.

## Reentrancy repair re-review

The updated `receipt-reentrancy-repair.json` was independently checked against all
seven current files; every SHA256 matches. The original findings above are retained
as rejected-freeze history. C1 and C2 are resolved in this freeze.

`refresh` commits the current snapshot and enabled state before invoking preparation
or publishing notifications. Public `invalidate` now enters a terminal, idempotent
state and removes observers before private snapshot invalidation; same-URI changes
use the private transient clear. Player notifications, including already queued
main closures, check the terminal flag. These changes close the identified
reentrant snapshot and shutdown resurrection paths.

The new seventh test installs a synchronous snapshot-reading observer during a
preference toggle and a Main-equivalent direct invalidation. It bounds the former
recursive failure and checks preparation/notification counts. A genuine background
notification is queued before invalidation, then drained afterward; the test
asserts non-main execution before posting and checks that eligibility stays false.
`context-tests-run008.log` records seven tests and zero failures. Failed setup
attempts and the stale six-test binary are preserved and excluded by the receipt.
This reviewer inspected that source/log, without executing another bundle.

Updated exact hashes (relative to `modules/gui/macosx`):

| File | SHA256 |
| --- | --- |
| `playqueue/VLCPlayerController.h` | `7594a27881387adb1ee071f3ada089e0f4003805672e4aa91526855b8d3fa2a4` |
| `playqueue/VLCPlayerController.m` | `a42a61bc7f2e1ee055f895a72d1534d98da6d9c018819b13190576d0e91f6353` |
| `timeline/VLCTimelineContext.h` | `634bdd6e5b3663ae503ec24b8c6b4d7881c63b661088f31390d4f16f2d8d3373` |
| `timeline/VLCTimelineContext.m` | `152237519a537e2c92e55a6c8b9829dda13f51fc5d55101b8246637c9177ca8f` |
| `timeline/VLCTimelineContextTests.m` | `21c1b5cb71f319102a23241070458871153c1c2f133c6a970f4c0b3920fb9127` |
| `timeline/VLCTimelineContextTestSupport.m` | `9820fc0f4e0b406ad89989ecd0ec44fc6be8f08a5e4424320713d3a174c54092` |
| `main/VLCMain.m` | `a4b6c24610624a551b0d8afbf697bcd3cf2ce0522791c4632fdf753e97194867` |

No new material issue was found in the narrow repair. Real player lifecycle,
full-app startup/termination and native interaction remain separate gates.

## Actual controller epoch runtime closure and test-fixture isolation

The actual-controller harness
`timeline/VLCTimelinePlayerContextTest.m` SHA256
`f2abf48c08dbcbc56b7eed82dff443b9857c38675dd1ddc136a1759cc5b957bb`
was independently source-reviewed, including normal configuration descriptor
preflight before controller allocation. It retains two same-URI inputs, registers
a bounded observation listener after the real controller listener, and checks real
epoch/context-generation changes before main queue drain. Cleanup removes callback
sources and drains queued main work before player deletion.

`candidate-build-20261006T061726Z.log` records the focused method passing:
one test, zero failures,0.009seconds. The test never starts media and snapshots
remain ineligible with zero duration/video count. The no-suitable-audio-output
message is scoped to its none backend and supplies no native audio/playback proof.
This closes the narrow actual-listener epoch-before-main boundary; eligible
selected-track playback/reopen remains separate native proof.

The subsequent full-bundle preflight failure identified an existing integration
fixture's environment leak, not a production epoch regression. The approved
`tests/VLCLibraryDataTypesIntegrationTestSupport.m` repair SHA256
`6847913b961fabfb3d03d8144e37c2ecba130893e495e2e0cb7d297f7a349c92`
was independently recomputed and source-reviewed. It copies exactly four original
environment values before mutation, preserves absent versus explicitly empty,
cleans partial copy allocation before any mutation, and restores once after
LibVLC release. All setup failures including mkdtemp lead to Stop; repeated Stop
is safe. The existing class teardown owns this serial fixture lifetime. No
production/path policy changes or concurrent environment support are claimed.

The owner research note `docs/research/story-005-test-environment-isolation.md`
records the concrete class-order failure and separates module-bank speculation.
Source is clear for one quiet full main-bundle run with fresh output. Its runtime
is pending; the earlier focused pass cannot prove preceding-class isolation.
