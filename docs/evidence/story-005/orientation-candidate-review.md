# Story005 picture-orientation candidate

Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`. Isolated detached source:
`work/upstream/vlc-master-story005-orientation`. Patch:
`patches/vlc-master/0003-picture-preserve-orientation.patch`, SHA256 `10cd20163e1725af368429a0dff377bc0d538b54aef0e41c80b4a5da532c539e`.
No commit, submission, application installation or baseline/in-flight source edit.

## Problem and decision

The general problem class is presentation metadata loss during buffer allocation,
including later zero-copy cloning. FFmpeg's primary
[display matrix documentation](https://ffmpeg.org/doxygen/trunk/group__lavu__video__display.html)
defines the matrix as the transform needed for correct presentation. Locally,
`video_format_Setup` (`src/misc/es_format.c`) explicitly resets orientation to
normal; `picture_InitPrivate` copies the supplied format, then calls
`picture_Setup`, which invokes that reset. Both `picture_NewFromFormat` and
`picture_NewFromResource` use this path; `picture_Clone` constructs a resource
picture. A decoder-buffer-only repair would be lost at the clone boundary.

Decision: restore only `fmt->orientation` immediately after the format setup in
`picture_Setup`. The patch leaves dimensions, crop validation, SAR reduction,
plane counts, pitch/line alignment and allocation calculations as established.
It preserves metadata; it does not apply a transform to pixels during allocation.
No new API/dependency, generic format copy or exporter redesign is introduced.

## Caller and converter impact review

- `picture_NewFromFormat` and `picture_NewFromResource` receive an existing
  `video_format_t`; the supplied orientation survives ordinary allocation and
  clone resource creation. `picture_New` still starts with normal orientation
  from `video_format_Setup`.
- All direct `picture_Setup` caller sites at the pinned source were inspected:
  OpenGL software PBO `modules/video_output/opengl/interop_sw.c`, DRM dumb-buffer
  template `modules/video_output/drm/buffers.c`, and Windows screen cursor
  `modules/access/screen/win32.c`. Their storage geometry logic remains untouched.
  This inspection does not claim GPU/Windows/DRM runtime qualification.
- `modules/codec/avcodec/video.c` already propagates decoder input orientation to
  its output video format. Allocation must retain that existing metadata.
- `modules/video_chroma/swscale.c` rejects differing input/output orientations;
  `modules/video_chroma/chain.c` detects that difference and builds an explicit
  transform chain using `video_format_TransformTo`. Restoring metadata agrees
  with this separation between a buffer and a presentation transform. No caller
  dependence on losing orientation was found in this bounded review.
- Caution: `picture_Export` calculates source aspect from the unrotated input
  dimensions; it has no swapped-axis normalization in that calculation. The
  correction should permit rotation selection, but portrait aspect fitting may
  require an additional, separately justified fix. Actual pixels/dimensions must
  be checked after integration before claiming transform correctness.

## Regression and diagnostic evidence

The existing registered `test/src/misc/image.c` now includes a focused helper
before LibVLC initialization. For RGBA and I420, it checks all eight orientation
values through allocation and clone, nonzero valid crop offsets, 4:3 SAR,
unchanged storage/visible dimensions, and plane layout against a normal picture.
Clones share the input pixel pointers and retain the checked geometry. No test
Makefile was changed.

`orientation-candidate-diagnostic.json` records commands, return codes and source,
object, executable and baseline dylib hashes. The exact new helper was extracted
without edits to an ignored standalone driver:

- Unchanged baseline dylib: aborts at the non-normal allocation orientation assert.
- Candidate `picture.o` plus that same baseline dylib: passes all helper asserts.
- Original eight-value probe: baseline allocation and clone both reset values1–7
  to0; candidate allocation and clone preserve values0–7. Separate JSONL files
  retain the negative and positive outcomes.
- The complete modified upstream `image.c` compiles with `-Wall -Wextra -Werror`.
  The first manual command omitted the build's standard `TOP_BUILDDIR` macro and
  failed in the unchanged `test.h`; second compilation supplies the normal test
  macros and succeeds. Both results are preserved.
- `git diff --check` passes; baseline source remained clean during this lane.

This is diagnostic linked-object proof, not genuine execution of the registered
upstream test against a rebuilt candidate library. That execution, cross-platform
coverage and actual rotated thumbnail pixel comparison remain pending the root's
review and build-owner integration. Baseline rotated-picture failure is recorded
in `preparser-probe-results.md`; it is not a candidate success claim.

## Integration handoff

Root reviews exact patch, then build owner applies it to the integration candidate.
Run registered `test_src_misc_image`; re-run the orientation probe against the
rebuilt candidate library, then request/export the synthetic rotated MP4 through
both internal and external preparsers. Compare orientation, storage/display
geometry and RGBA pixels to an independently rotated reference at the actual
sample frame. Preserve any remaining timestamp failure separately. This narrow
patch is a prerequisite correction, not complete Story005 readiness.
