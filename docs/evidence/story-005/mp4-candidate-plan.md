# Experimental MP4 edit timeline correction

This is an isolated Story005 prerequisite experiment, not a final contribution or
preview architecture qualification. Root approved the bounded plan in the story's
20261005-2040 entry. No installed application, original media or annotation store
is changed. Native playback validation belongs to the native owner and is pending
while the Mac is locked.

## Exact candidate

Detached source: `work/upstream/vlc-master-story005-timestamp`, clean base
`2e358f3098c2f2b7621d1dc568de8b61ad786322`. Only
`MP4_MapTrackTimeIntoTimeline` changes: remove the seek-start-DTS condition from
positive edit-media-time subtraction. Preserve signed decode preroll, empty-edit
handling, composition shifts and every other demux operation.

Patch: `patches/vlc-master/experimental/0004-mp4-edit-timeline.patch`.
Root reviewed this exact small diff before integration. Diff checking and clean
baseline patch application checking pass. No source commit was created.

## Why this experiment

Independent decoded pixels show that the same presentation-time mapping changes
with the seek's GOP. Standard first-GOP and long-GOP first-GOP pictures retain an
83.333ms edit offset; long-GOP next-GOP pictures agree with independent source
presentation times within one microsecond. See the separate preparser results.

[The 2021 timing consolidation](https://github.com/videolan/vlc/commit/7acbebf3eca9b01eeb5b5cdd200ed0771fc3f947)
introduced the starting-DTS guard to avoid negative offsets. Previous code applied
the edit offset then clamped negative DTS. [The 2023 extraction](https://github.com/videolan/vlc/commit/bde2098647ae4c44d70917907c719dbbf1a56d57)
preserved the guard. This history explains why a tiny correction still requires
signed-clock/preroll validation.

[Apple's composition-time documentation](https://developer.apple.com/documentation/quicktime-file-format/composition_offset_atom)
distinguishes decode ordering from presentation time. [Its edit-list description](https://developer.apple.com/documentation/quicktime-file-format/edit_list_atom/edit_list_table)
defines a media start mapped into the movie timeline and identifies empty edits.
For unit-rate nonempty edits the translation is media time minus the edit's media
start plus preceding movie-edit duration; a seek-start keyframe does not change
that translation. [FFmpeg's MOV implementation](https://ffmpeg.org/doxygen/trunk/mov_8c_source.html)
retains earlier reference samples for decoding and excludes samples outside the
edit when presenting. This is an external comparison, not local VLC proof.

Pinned `es_out.c` rejects PCR only at the invalid sentinel, and the input-clock
assertion likewise checks validity rather than positivity. This allows the signed
experiment; it does not establish correct real playback.

## Independent fixtures and diagnostics

`tests/story-005/mp4_generate_fixtures.py` writes a new directory only. It generates
its own legal `testsrc2` H264 media, then constructs positive non-keyframe trims,
two nonempty edits, signed CTTS controls and a dwell control. It preserves mdat
and its offsets by changing a trailing moov; source media is never overwritten.
Exact tool versions, commands, hashes and edit entries are in the fresh ignored
`work/story005-mp4-fixtures001/manifest.json`. FFprobe packet MD5, packet PTS/DTS,
frame times and format metadata accompany each fixture.

`tests/story-005/mp4_packet_probe.c` captures demux packets and PCR before decoding.
Its pattern follows upstream's demux runner; like that runner it links
`src/input/var.c` because input-config initialization is not exported. It has a
30s watchdog and 10000 packet/iteration limits. It reports no playback or clock
acceptance. Packet MD5 is an identity discriminator for synthetic encoded samples,
not a security assertion.

`tests/story-005/mp4_compare_packets.py` runs ten bounded scenarios on both builds
and compares packet identity/timing with the independent FFprobe maps. Duplicate
hashes across edits retain multiple reference options and report ambiguity.
First/next GOP, leading empty edit from the original fixture set, initial trim,
continuous edit transition, backward/forward seek, negative CTTS and unaffected
controls remain part of the wider required matrix. Packet-only checks do not
replace actual pixel or playback checks.

The baseline trim already emits the first encoded packet at PTS83.334ms while
FFprobe maps that same hash to PTS-3.25s/DTS-3.333333s as decode preroll. Baseline
packet capture therefore reproduces a larger trim limitation independently of
thumbnail export. It must not be silently promoted to acceptable presentation.

## Bounds and stop rule

Positive edit media times are admitted only within the existing conversion bounds.
For the observed nonnegative raw decode values, subtraction yields a signed value
no lower than minus the admitted edit media time. No new unsigned conversion or
clamp is introduced. Existing edit-duration sums and malformed-edit handling are
outside this patch. Inputs with unsupported rates or invalid bounds are controls,
not newly supported formats.

Do not compensate timestamps in the UI, clamp preroll, introduce a public API or
expand this patch. Stop on clock failure, shown preroll, an incorrect edit
transition or an unaffected regression. If those occur, preserve the exact
comparison and name the larger MP4 prerequisite before any further implementation.
