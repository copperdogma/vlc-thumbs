# Shutdown baseline attribution — bounded contribution limitation

The contribution coordinator accepts this focused contribution as ready for maintainer review/submission by Cam with the limitations below. Nothing has been submitted. No crash fix or feature exoneration is claimed.

## Source ownership finding

The pinned upstream API requires releasing the owned reference returned by `vlc_media_source_provider_GetMediaSource`. The Cocoa provider passes that reference to its media-source wrapper without releasing the original reference. The wrapper adds a hold and later releases only that hold. This leaves an owned reference outstanding. A services-discovery instance is destroyed only when its source reference count reaches zero; provider deletion does not recursively close surviving discovery children. The final module-bank cleanup can unload plugin images without checking those references. UPnP services-discovery close joins its search thread and releases the shared wrapper; the wrapper's final destruction calls `UpnpFinish`.

This is a concrete unchanged upstream ownership defect and a lifetime hazard. It is distinct from proving the original crash's exact cause. The eight source files below are byte-identical between the pinned baseline and final candidate. Primary source locations:

- [include/vlc_media_source.h:290](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/include/vlc_media_source.h#L290)
- [modules/gui/macosx/library/media-source/VLCMediaSourceProvider.m:44](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/library/media-source/VLCMediaSourceProvider.m#L44)
- [modules/gui/macosx/library/media-source/VLCMediaSource.m:155](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/gui/macosx/library/media-source/VLCMediaSource.m#L155)
- [src/media_source/media_source.c:173](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/media_source/media_source.c#L173)
- [src/modules/bank.c:756](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/modules/bank.c#L756)
- [src/misc/objects.c:126](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/src/misc/objects.c#L126)
- [modules/services_discovery/upnp-wrapper.cpp:43](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/services_discovery/upnp-wrapper.cpp#L43)
- [modules/services_discovery/upnp.cpp:347](https://github.com/videolan/vlc/blob/2e358f3098c2f2b7621d1dc568de8b61ad786322/modules/services_discovery/upnp.cpp#L347)

## Sanitized baseline observation

One untouched baseline GUI verbose run activated both UPnP services discovery and renderer discovery. The retained EOF trace has services activation at line 87, renderer activation at line 64 and renderer removal at line 181, followed by later keystore cleanup at line 184. It contains no services-discovery removal entry. The baseline child exited 0 and was observed absent. The 19,455-byte original trace has SHA256 `9d8e050310dbf59a7a10579cf825d78950baeb46aa53db06969b6ad0093278dc`; raw trace content, LAN service identities and addresses are intentionally excluded.

This strongly corroborates activation of the affected baseline lifetime path and a missing close entry while other teardown continues. It does not prove a live worker at plugin unload, establish the exact runtime image UUID, or reproduce/explain the candidate crash. A five-second mapping timeout ended collection after about 5.802 seconds; the planned post-mapping hold was not completed. Sample, mapping and LLDB diagnostics were inconclusive. A short separate public diagnostic host missed its planned hold and explicitly stopped/destroyed discovery, bypassing the Cocoa ownership path; its clean result cannot exonerate that path.

## Retained candidate limitation and review scope

The original candidate process terminated with child status −11 (SIGSEGV) during SIGTERM shutdown. Five other retained playback retirements exited 0. Exact crash causality remains unproved; no production change addresses the ownership defect or the crash. The source defect and baseline activation evidence support disclosing this as a baseline limitation for focused contribution review, not asserting clean lifecycle behavior.

The six playback intervals' numerical zero-percentage-point frame-loss increase and complete captured digital audio remain scoped characterization. The candidate 133.332 ms screen-PTS observation gap does not establish uninterrupted video or a feature-caused stall. Ordinary controls and visible four-surface preview evidence retain their declared scopes; actual VoiceOver functional navigation was unavailable. Conventional distcheck remains failed (80 pass, 5 skip, 7 fail); structural distribution results do not replace it. Full reader, precise detached drag/held-state, universal latency, Intel/older-system and exhaustive-format qualification are not claimed.

## Pinned unchanged file hashes

- `include/vlc_media_source.h`: `80ac2c27a432e5991f4220007058d01d60e56ee2a5573eaa79787d0c990ed6bb`
- `modules/gui/macosx/library/media-source/VLCMediaSourceProvider.m`: `2a844487fc97b61272c21be4223555a936439d9322edc72c1890cec78b3d57ef`
- `modules/gui/macosx/library/media-source/VLCMediaSource.m`: `e23d631f8f46556307861da9255bcca918ac52fe721870651db6fc27b5d2d99c`
- `src/media_source/media_source.c`: `cd8225c1081a45b58d7f5e117e169c61bd6b07ceee5eaa64f18249f66303c839`
- `src/modules/bank.c`: `165ecfcaffa8c54931967f4e59b295b546eda8608df0d6d3e7ae804f75f3c8a6`
- `src/misc/objects.c`: `d25da3893002609987227b5a8c2b381b3fc3c76163daaab89937ddc4844885c1`
- `modules/services_discovery/upnp-wrapper.cpp`: `9da68e858a243b2a4a9dbff36a0ea66ce688d037f162d308ba71b841510b7e4a`
- `modules/services_discovery/upnp.cpp`: `f60eb2b1bf0267160f4d742ae8cc8f48e40c046522d08c8206f7279b1634a82a`
