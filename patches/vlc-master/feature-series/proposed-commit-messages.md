# Proposed commit messages — draft text only

No commits, sign-off or submission exist. Contributor/contact: Cam Marsollier
<cam.marsollier@gmail.com>, with approved credit and disclosed AI assistance.
Retain existing third-party notices and GPL/LGPL terms; credit asserts no sole
ownership, assignment or waiver. Final submission boundaries need agreement.

## 0. build: distribute existing headers beside their source consumers

Declare five existing Apple/media-library headers in three Automake source lists
so source archives contain their consumers' inputs. Header bytes, runtime code,
conditions and flags are unchanged. Archive completeness is separate from tests.

## 1. contrib: expose Matroska track identity and opt-in flat admission

Export TrackNumber for exact selected-video matching and add an opt-in bounded
physical Segment scan. Reject unsupported ordered/linked timelines, malformed
bounds and exhausted budgets; restore demux position before ordinary reading.
Default demuxing remains unchanged. Generated admission cases and custom-AVIO
packet/fault probes cover this contract. FFmpeg review/ownership remain unagreed.

## 2. bin: build and package the timeline preview helper with portable tests

Add a protocol4 worker using private normal-contrib FFmpeg libraries. Bound
requests/source validation, report actual keyframe time and selected identity,
and package/sign beside VLC through normal build rules. Include synthetic
fixtures and dependency/admission/custom-AVIO recipes in the source distribution.

Current strengthened helper77 checks passed. The independent app compiled and its signature
verified, but its outer runner failed. Conventional distcheck failed (80 pass,
5 skip, 7 fail); installation-name correctness and distclean remain unqualified.
These results do not satisfy the submission checklist; see [limitations](LIMITATIONS.md).

## 3. macosx: add thumbnail service, cache, scheduler and worker foundation

Add separate 32 MiB RAM/256 MiB disk caches, bounded helper process ownership,
finite scheduling and source-verification state. Complete terminal hover history
before invoking callbacks so a replacement request can remain unsatisfied and run.
Register cache/service/scheduler/worker tests and guarded owned-volume ENOSPC.
This foundation compiles and tests before production activation in part 4.

## 4. macosx: integrate coherent player context and timeline hover previews

Extend the existing hover owner with a default-on preference, selected-video/
input-epoch context and finite preparation. Label actual sample time, cancel stale
work and expire provisional reuse without pointer activity renewing the deadline.
Keep ordinary control owners; register context/player/hover tests once.

Current headless proof: normal helper/module builds; helper77; 284 unique native
executions, 283 passes and one optional ENOSPC skip. Intermediate part 3 compiled
and ran 265 tests with one skip and zero failures using verified reused core/contrib/runtime inputs.
Historical native rendering and ordinary-control evidence remains scoped through
revision 10. Changed helper/service have no new packaged-app/GUI qualification.
Actual VoiceOver, precise detached seeks, cold/stalled NAS and universal latency
remain unqualified; the actual shutdown SIGSEGV has unproved cause. Conventional
make-check/distcheck requirements remain unmet; see [limitations](LIMITATIONS.md).
