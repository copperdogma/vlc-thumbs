# Proposed commit messages

Draft subjects and bodies for all thirteen existing patches, in the
[canonical application order](../CONTRIBUTION.md#apply-and-review). **P** denotes
`blocker-prerequisites/`; **F** denotes `feature-series/`. These messages describe
the current payloads; they do not add commit headers or change patch bytes.
The [validation table](../CONTRIBUTION.md#validation-and-limits) gives the combined
proof and limits. Component review groups are not independent release stacks.

## P0008 — macosx: hit-test autohide controls in local coordinates

Use the controller-owned bottom bar and convert the window pointer into each
control view's local bounds. This corrects missed-control hit testing caused by
the prior outlet and coordinate assumptions while retaining guard order and nil
behavior. Eleven source-extracted AppKit cases cover the change; returned-main
fade causality is not established. Apply before F0004's controller edits.

## F0000 — build: distribute existing headers beside their consumers

List five existing Apple/media-library headers in the three Automake source lists
whose consumers require them. Source archives then contain these inputs without
changing header bytes, runtime behavior or build flags. Complete conventional
distcheck covers archive completeness with the later build/cleanup repairs.

## F0001 — contrib: expose Matroska identity and bounded flat admission

Export TrackNumber for exact selected-video matching and add opt-in bounded
physical Segment admission. Reject ordered/linked timelines, malformed bounds
and exhausted budgets, restoring buffered demux position before ordinary reads.
Default demuxing is unchanged. F0002's generated admission and custom-AVIO
packet/fault fixtures exercise this contract through normal FFmpeg contrib.

## F0002 — bin: build and package the timeline preview helper

Add a protocol 4 retained worker using private normal-contrib FFmpeg libraries.
Bound source validation and requests, report actual keyframe time and selected
identity, and package/sign the helper beside VLC. Include synthetic fixtures and
identity/admission/custom-AVIO tests in the source distribution. The helper
requires F0001's contrib interfaces; the complete helper matrix has 77 checks.

## F0003 — macosx: add thumbnail service, cache and worker scheduling

Add 32 MiB RAM/256 MiB disk caches, finite scheduling, source-verification state
and bounded helper-process ownership. Reconcile covered/deferred/permanent work
to reach quiescence; finish hover history before callbacks so replacement demand
can run. Register cache/service/scheduler/worker regressions, including guarded
owned-volume ENOSPC. This foundation uses F0002's helper and precedes native
activation in F0004.

## F0004 — macosx: integrate player context and timeline hover previews

Extend the existing hover owner with selected-video/input-epoch context, finite
preparation and a default-on Interface preference. Label actual keyframe time,
cancel stale work and expire provisional images without pointer activity renewing
the deadline. Keep pointer time as the seek target and unsupported-media time
hover. Add context/player/hover regressions using F0003's service and test support;
P0006 later extends the actual-controller test.

## P0001 — build: order macOS installation and clean generated artifacts

Use an install-exec hook for the transformed macOS executable name and remove the
same installed name at uninstall. Distribute the required private header and
clean generated nib directories and `libvlc_vtutils.la`. These changes allow
complete source-archive install/cleanup checks after the feature build-list edits;
conventional distcheck passes through final cleanup.

## P0002 — clock: preserve the observed system origin

Keep the observed stream/system start times when computing the clock offset
rather than subtracting `VLC_TICK_0`. Extend the drift regression to require exact
conversion of the master's just-observed point. Existing clock tests and bounded
matched playback cover the combined composition; no universal timing claim is
made.

## P0003 — tests: select GnuTLS for the PEM trust fixture

Create the fixture's client credentials from GnuTLS rather than automatic TLS
backend selection. Skip when GnuTLS is absent, retain failed-initialization
handling and the default unknown-certificate phase. This makes the PEM-specific
registered test exercise its intended backend without changing production TLS
selection.

## P0004 — opengl: initialize the legacy version fallback

Initialize the major-version fallback to 2 before the legacy version query.
A query that cannot provide a major version then leaves a defined value.
Combined native playback covers the affected rendering path; all legacy drivers
and independent patch execution remain unqualified.

## P0005 — macosx: release the caller-owned media source

Release `GetMediaSource`'s caller-owned reference after the Objective-C wrapper
retains it. Add a registered regression compiling the actual provider callsite
with a wrapper double that follows the real Hold/Release contract, including null
results and wrapper destruction. This repairs reference balance without claiming
the cause of historical shutdown crashes.

## P0006 — macosx: retire the playback-ended timer at termination

Mark the player controller terminating, invalidate its delayed playback-ended
timer and reject queued state callbacks afterward. Extend F0004's actual-controller
context test to verify pending-timer cancellation and no new timer on a subsequent
STOPPED callback. That feature-created harness is a concrete application/test
dependency.

## P0007 — macosx: fence video-window callback lifetime

Fence callback ownership across Disable/Destroy, remove registered callbacks
before invalidating their owner, and balance deferred destruction. Register a
regression using the real provider/view operations, queued destruction and an
in-flight callback, with link-only support that creates no windows. The test
registration follows F0003/F0004's macOS test edits; its headless lifetime proof
does not establish native removal or universal crash-free shutdown.

Contributor/contact: **Cam Marsollier <cam.marsollier@gmail.com>**. Developed with
AI assistance. Retain GPL/LGPL and third-party notices. These drafts invent no
sole-ownership, assignment, waiver, sign-off or formal rights attestation.
