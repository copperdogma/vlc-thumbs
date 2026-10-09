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

The exact combined stack passes normal 009 complete check and conventional 010 complete
distcheck. Full helper 77 is historical; normal 009/010 reran helper-basic13 only.
See [limitations](LIMITATIONS.md) for distinct current native/platform boundaries.

## 3. macosx: add thumbnail service, cache, scheduler and worker foundation

Add separate 32 MiB RAM/256 MiB disk caches, bounded helper process ownership,
finite scheduling and source-verification state. Reconcile covered scheduler targets against deferred/permanent state to stop
covered positions retaining wakeups. Preserve causal supersession and finite
quiescence regression coverage. Complete terminal hover history
before invoking callbacks so a replacement request can remain unsatisfied and run.
Register cache/service/scheduler/worker tests and guarded owned-volume ENOSPC.
This foundation compiles and tests before production activation in part 4.

## 4. macosx: integrate coherent player context and timeline hover previews

Extend the existing hover owner with a default-on preference, selected-video/
input-epoch context and finite preparation. Label actual sample time, cancel stale
work and expire provisional reuse without pointer activity renewing the deadline.
Keep ordinary control owners; register context/player/hover tests once.

Historical helper 77 and intermediate foundation evidence retain their original scope.
Current normal 009 complete check and conventional 010 complete distcheck pass on the
canonical72-path stack. Current main/custom hover and narrow reader/seek evidence,
user-accepted deferred004 causality, stale exposed progress, unavailable platforms and
short-recipe execution boundary are detailed in [limitations](LIMITATIONS.md).
