# MP4 candidate experiment results — stopped

The one-line candidate corrects the measured positive-edit packet timelines, but
it does not satisfy the required thumbnail/presentation contract. A non-keyframe
trim returned an out-of-edit negative-time picture and image export failed. The
experiment stops here; no compensating timestamp constants or additional product
changes were made.

## Pins and scope

Base source: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Experimental patch: `patches/vlc-master/experimental/0004-mp4-edit-timeline.patch`.
Actual candidate MP4 module SHA256:
`99ff53037f9b832259347d82d287d1dba027c97fc83380f1e49244dc0d9ca908`.
Candidate core SHA256:
`d9901cfb98f17ec4eff691aac484fa98867460d9864a0b1cab997c9d7ae61c43`.
Builder receipt: `candidate-mp4-experiment-build-manifest.json`.
Separate probes link each build's own core/libvlc and load its modules. Exact
commands, environment, module/core hashes and raw logs are in ignored
`work/story005-mp4-packets001/`. The packaged application remains pre0004.

## Packet comparison

Twenty bounded invocations completed at EOF without timeouts or missing packet
hashes. This captures demux output before decoding. It does not exercise real
VLC clock consumption or prove which pictures are presented. Comparison tolerance
is two microseconds to cover independently rounded time-base conversions; values
subtract VLC_TICK_0 before comparison.

| Scenario | Baseline matching / mismatching packets | Candidate matching / mismatching packets | Candidate negative PCR observations |
|---|---:|---:|---:|
| base.mp4, seek 0us, precise | 0 / 288 | 288 / 0 | 2 |
| base.mp4, seek 9125000us, fast | 0 / 288 | 288 / 0 | 2 |
| base.mp4, seek 10125000us, precise | 48 / 0 | 48 / 0 | 0 |
| nonkeyframe-trim.mp4, seek 0us, precise | 0 / 288 | 288 / 0 | 80 |
| nonkeyframe-trim.mp4, seek 125000us, fast | 0 / 288 | 288 / 0 | 80 |
| two-edits.mp4, seek -1us, precise | 0 / 264 | 264 / 0 | 80 |
| two-edits.mp4, seek 3125000us, precise | 0 / 288 | 288 / 0 | 104 |
| negative-ctts.mp4, seek 0us, precise | 0 / 288 | 0 / 288 | 0 |
| negative-ctts-trim.mp4, seek 0us, precise | 0 / 288 | 0 / 288 | 78 |
| dwell-control.mp4, seek 0us, precise | 0 / 288 | 288 / 0 | 80 |

No captured PCR equals the invalid sentinel. Negative PCR reaching the diagnostic
callback is not clock acceptance. Multiple-edit packet hashes repeat: the oracle
retains every independent timestamp option and counts ambiguity. Matching one of
those options does not establish the edit traversal order or correct display.
Dwell is only a regression control; FFmpeg's linear frame output and a packet
match do not establish dwell semantics.

The signed-CTTS controls retain an 83.333ms offset in both baseline and candidate.
This is separate from the removed seek-start guard: VLC's composition-shift and
shared track-offset machinery remains unchanged. No broader time-normalization
claim is justified.

## Stop finding: non-keyframe trim at precise time zero

The fixture edits source3.25s through source11.25s into an eight-second movie.
Independent FFprobe marks preceding source samples as decode-only preroll and its
first display frame is source3.25s. Packet identity matches the generated source.

Baseline acquisition succeeded and exported source frame0 at reported date83.334ms.
Independent pixel MAE was0.3523 against encoded source frame0, versus20.2647 against
the correct first trim display frame. This proves an inherited out-of-edit
thumbnail behavior without relying on VLC's reported date.

Candidate acquisition reported success with a picture at `-3249999` VLC ticks
(media presentation time−3.25s), outside this edit. `picture_Export` returned
`-2147483648` and no image, and the probe exited5. Its encoder log warns that the
frame's time is earlier than its initial last-frame time and reports no encoded
image. Candidate pixel correspondence cannot be measured because no export was
produced; do not infer an actual candidate pixel hash from the date alone.

Raw baseline: `work/story005-mp4-baseline-pixels001/` including independent
FFmpeg oracle commands and raw references. Raw candidate:
`work/story005-mp4-candidate-pixels001/nonkeyframe-trim-precise0.jsonl` and `.log`.

## Remaining prerequisite

Correct edit mapping must be paired with presentation eligibility: preserve
reference samples for decoding, suppress pictures outside the current edit, and
keep sample labels tied to the movie timeline. The preparser's no-seek/zero-time
path and thumbnail queue do not by themselves enforce that eligibility. Negative
image dates also expose the export path's encoder limitation. Ordinary first/later
GOP comparisons can still describe the mapping improvement, but they cannot
qualify this patch for shipping or submission.

The existing conversion bounds protect admitted positive edit offsets; this
candidate adds no unsigned conversion or clamp. A normalized−1us timestamp plus
VLC_TICK_0 would collide with the invalid zero sentinel; the current measured
fixtures do not exercise that boundary. Multi-edit duration accumulation,
unsupported media rates and malformed edit semantics remain outside this patch.

Native startup, trimming, continuous edit transitions and seek playback are still
unqualified; the Mac was locked. Root owns any decision to pursue the larger
prerequisite. No further product edits, installed-app changes, commits or upstream
contact occurred.
