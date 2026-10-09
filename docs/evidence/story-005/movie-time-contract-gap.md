# Thumbnail movie-time contract gap

Read-only source review against VLC master
`2e358f3098c2f2b7621d1dc568de8b61ad786322`, inspected in
`work/upstream/vlc-master-story005`. No further product experiment was performed.
This records a contract gap and possible core work, not an architecture selection
or a finding that a helper alternative is unavailable.

## Three different boundaries

`picture.date` is documented only as a **display date**
([picture.h L140](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/include/vlc_picture.h#L140)).
Decoder pictures carry stream timestamps; this alone does not promise the
position of the displayed sample on the movie timeline.

Normal playback's player timer computes logical time from stream PTS minus
`input_normal_time` and the input start offset
([timer.c L365–389](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/player/timer.c#L365)).
The timer mutex protects its state, but normal time arrives separately from
output-clock points. It does not bind a picture to the origin/edit state that
produced it. Input statistics queries `DEMUX_GET_NORMAL_TIME`; failure supplies
an invalid update
([input.c L590–615](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/input/input.c#L590)).
MP4 has no implementation of that query in this pin. Its `DEMUX_GET_TIME`
subtracts `i_max_pts_offset`, while packet timing retains composition-shift and
shared track-offset handling
([mp4.c L1386](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/demux/mp4/mp4.c#L1386),
[L2359](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/demux/mp4/mp4.c#L2359)).
Consequently an independently observed CTTS stream-clock shift is not, by itself,
proof of an incorrectly dated picture. The existing clock converter maps stream
time to **system time**, not movie position
([clock.h L321](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/clock/clock.h#L321)).

Presentation eligibility is separate: reference samples may be needed to decode
an edit without being eligible for display in it. Normal video playback consumes
decoder preroll state and drops earlier pictures
([decoder.c L1496](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/input/decoder.c#L1496)).
The thumbnail queue instead forwards its first picture, without that check
([L1619](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/input/decoder.c#L1619)).
The preparser callback ignores time/clock events; it holds the returned picture
and stops/closes input before reading the result
([internal.c L384](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/preparser/internal.c#L384),
[L506](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/preparser/internal.c#L506)).
That teardown prevents result races; it does not establish movie-time provenance.

## Experiment remains stopped

[0004 results](mp4-candidate-results.md) and its
[build receipt](candidate-mp4-experiment-build-manifest.json) record the exact
candidate binaries. Removing the MP4 seek-start guard improved measured ordinary
positive-edit packet and picture correspondence. However, precise time zero on
the non-keyframe trim returned a picture date of `-3249999` VLC ticks; export
failed and produced no image. Baseline independently exported source frame zero,
outside that edit. Candidate pixels were unavailable, so the candidate date does
not establish their identity. These results prohibit a readiness claim for 0004.

## Reuse limits and minimum core path

No existing preparser-facing seam found in this bounded trace both converts an
exact picture to movie position and enforces its edit eligibility. Polling the
latest input time cannot establish that association across decoding/reordering
or edit transitions. No guessed offsets, fixture-specific constants, negative
date clamps, or compensating relabeling are justified.

Reusing decoder preroll rejection in the thumbnail queue is a narrow candidate:
discard ineligible preroll without consuming `b_first`. It reuses existing
marked precise-seek behavior. MP4 sets the next-display threshold only for
accurate seeks; fast/no-seek startup and edit-end/transition eligibility are not
established by that reuse. It also cannot correct edit mapping or expose movie
time. Normal playback correctness is not proven by source inspection.

If a core route is selected, the minimum work spans: demux stream/movie timing
and edit semantics; decoder presentation eligibility while retaining reference
samples; correlated time provenance on the private input/preparser result path;
and equivalent external-process transport. The existing normal-time query could
expose a deliberate MP4 clock origin without a new public API, but cannot alone
repair conditional edit mapping or carry edit bounds. Tests must distinguish
stream date from movie time and independently verify pixels, initial/fast/precise
seeks, signed CTTS, trimmed preroll, and edit transitions. Real clock/playback
validation remains required. This is larger than the approved one-line mapping
experiment; its design and scope remain undecided.
