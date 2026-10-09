# Build, test and runtime prerequisites

These repairs accompany the timeline-preview series because its complete build,
distribution tests and native playback exercise the affected paths. The concerns
can be reviewed separately; the serialized prerequisite component is not an
independently qualified stack.

## Application and dependencies

Apply the complete [aggregate series](../contribution-series) once from base
`2e358f3098c2f2b7621d1dc568de8b61ad786322`:

```text
P0008 → F0000 → F0001 → F0002 → F0003 → F0004
      → P0001 → P0002 → P0003 → P0004 → P0005 → P0006 → P0007
```

P denotes this directory; F denotes `feature-series/`. Component `series` files
are review inventories. The [aggregate manifest](../contribution-manifest.json)
pins intermediate trees and the combined tree
`b7c0f24e442c35a57bb108d56b801fd05b624943`: 19 prerequisite paths, six overlapping
the 59 feature paths, for 72 combined paths.

## Why each repair is included

| Patch | Defect/reason and source boundary | Dependency and relevant coverage |
|---|---|---|
| P0008 | `VLCMainVideoViewController.mouseOnControls` uses the controller-owned bottom bar and converts the window point into each view's local bounds. The old outlet/coordinate assumptions miss controls. | Applies before F0004, which later changes the same controller. Eleven source-extracted AppKit hit-test cases pass; this does not establish the cause of returned-main fade. |
| P0001 | `bin/Makefile.am` orders transformed-name install/uninstall correctly; macOS distribution includes `PIPSPI.h`; generated nibs and codec `libvlc_vtutils.la` are removed during cleanup. These paths prevented complete archive/install/cleanup qualification. | Serialized after feature build-list edits. Complete conventional distcheck exercises distribution, installation and final cleanup. |
| P0002 | `src/clock/clock.c` preserves the observed stream/system origins instead of subtracting `VLC_TICK_0`, restoring exact conversion of the master's just-observed point. | Existing `test/src/clock/clock.c` adds the same-point invariant; clock tests and bounded matched playback cover the combined result. No feature API dependency is introduced. |
| P0003 | The PEM trust fixture needs GnuTLS credentials, while automatic backend selection can choose another TLS client. `test/modules/misc/tls.c` explicitly selects GnuTLS for this fixture. | Test-only repair in the complete registered check. Missing GnuTLS is an optional skip; the default unknown-certificate phase and production backend selection are retained. |
| P0004 | `modules/video_output/opengl/gl_api.c` initializes the legacy major-version fallback to 2 when the version query cannot supply it. | Native playback exercises the combined rendering path. No dedicated all-driver/legacy-hardware test or independent patch qualification is claimed. |
| P0005 | `VLCMediaSourceProvider.m` releases the caller-owned `GetMediaSource` reference after the wrapper retains it, removing an extra ownership reference. | Adds a registered regression compiling the actual provider callsite with a wrapper double matching its Hold/Release contract. Covers the reference balance, not the cause of historical shutdown crashes. |
| P0006 | `VLCPlayerController` invalidates its delayed playback-ended timer at termination and rejects queued state callbacks afterward. | Extends `VLCTimelinePlayerContextTest.m`, created by F0004, to test actual-controller timer cancellation and post-termination STOPPED handling. Moving it before F0004 would require extracting/re-registering that test. |
| P0007 | `VLCVideoOutputProvider`/`VLCVoutView` fence callback ownership across Disable/Destroy and remove callbacks before their owner becomes invalid. | Uses the macOS test registration modified by F0003/F0004. Adds `vlc-vout-lifetime-test` compiling the actual provider/view operations with link-only support; tests queued destruction/in-flight callbacks without creating windows. It is not native window-removal or universal shutdown proof. |

Moving the existing patch files does not remove the coupling: P0006 needs
F0004's actual-controller harness; P0007's serialized registration hunk expects
F0004's context-test entries and uses shared test flags modified by F0003. The
latter is packaging/test coupling, not a new feature API dependency. Extracting
or re-registering the tests would change patch bytes and require intermediate
build/test proof; no narrow benefit justifies that change here. Keep the existing
order and use the table as logical review boundaries. Neither
the feature-only stack nor a reordered repair-only stack is a qualified release.

The [central validation table](../CONTRIBUTION.md#validation-and-limits) records
combined build, distribution, native and playback proof. [Detailed limits](../feature-series/LIMITATIONS.md)
retain measurement boundaries and unresolved shutdown causality. Use the
[ordinary reproduction route](../feature-series/README.md); no private harness
is required by the public build route.

Contributor/contact and AI assistance disclosure are in the [cover](../CONTRIBUTION.md#reproduce-and-credit).
Raw patches retain their notices and contain no invented authorship, sign-off or
assignment headers. No binary, profile, private log or fixture video is included.
