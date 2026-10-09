# Combined-tree prerequisites

**READY for bounded pre-submission review of Phases1/2; no submission.** The whole story remains InProgress; Phase3 is not authorized. These repairs accompany the hover contribution
because required combined-tree builds/tests and playback use their affected
paths. Maintainers may review them separately; no independent application/build
of the whole prerequisite component has been qualified.

Base: `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
Current combined tree: `b7c0f24e442c35a57bb108d56b801fd05b624943`.
There are 19 prerequisite paths, six overlapping the 59 feature paths, for 72
combined paths. All source bytes/modes and intermediate trees are pinned in the
[aggregate manifest](../contribution-manifest.json).

## Apply exactly once

P denotes this directory; F denotes `feature-series/`:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

Use the [aggregate application loop and build/check/distcheck recipe](../feature-series/README.md).
Component `series` files are review inventories, not an alternate application
sequence. P0006–7 extend feature-created regression substrate and cannot simply
be moved ahead of the features. The five features alone are also not a newly
qualified runnable release. Any smaller/reordered submission needs its own proof.

## Review map

| Patch | Concern |
|---|---|
| P0008 | Controller-owned bottom bar and per-view local-coordinate autohide hit testing |
| P0001 | Ordered transformed-name install/uninstall, required header distribution, generated-nib/vtutils cleanup |
| P0002 | Preserve observed clock origin and same-point conversion invariant |
| P0003 | Select GnuTLS for its PEM trust fixture while retaining default unknown-certificate phase |
| P0004 | Initialize legacy OpenGL major-version fallback |
| P0005 | Balance caller-owned media-source reference; actual-provider callsite regression |
| P0006 | Retire playback-ended timer and guard termination; actual-controller regression |
| P0007 | Fence video-window Disable/Destroy callback lifetime; actual-provider wiring and normal test registration |

The exact combined tree passes normal build/full registered check and complete
conventional distcheck. These qualify this composition, not untouched-base
application/build of every part. P0008's focused source-extracted AppKit cases
pass; the current returned-main title/button fade remains unattributed and is not
claimed fixed. Clock/GL/lifetime changes required current matched playback/resources, now qualified by three bounded60s pairs. Three current matched60s AB/BA/AB pairs pass bounded playback/preparation/audio/drop/resource qualification. All native frame/audio loss counters are zero; candidate-minus-baseline sampled mean CPU is+1.47/+2.20/+2.29 percentage points and combined sampled maximum RSS is+100.3/+100.6/+97.6MiB. Recorder overhead is measured separately. Complete pair1 was retained across a human-permission pause; the interrupted second pair was excluded and its failed cohort remains failed. System-mixed AAC/PCM continuity, variable-rate capture observations and sampled resources retain their limits; no per-app callback or universal smoothness claim follows.

See the [current scope table and optional historical appendix](../feature-series/LIMITATIONS.md)
for native, reader, playback, shutdown and unavailable-platform boundaries.
Literal public normal-build/check commands passed in interrupted stages; the full
public recipe including outer distcheck remains unexecuted. Narrow normal-Quit
observations do not establish causal repair of historical shutdown failures.

Patch basenames provide proposed subjects. Raw diffs contain no invented author,
sign-off or assignment headers; notices remain. Contributor/contact and AI
assistance disclosure are in the [feature overview](../feature-series/README.md).
No binary, profile, private log or fixture media is included.
