# Architecture synthesis — implementation selected, readiness open

ADR004 selects the retained FFmpeg9 helper through ordinary contrib/build rules,
bounded service/cache/preparation, an atomic current-player context and master's
existing hover panel. This is root's technical choice within Cam's phases1/2
authorization, not maintainer endorsement. Exact contracts, ownership and proposed
series are in the [frozen port plan](../../../evidence/story-005/feature-port-plan.md).

Unchanged master and an initial isolated core candidate build and each ran253
XCTest cases without failures. The core reuse discriminator exposed track,
orientation and sample-time problems. Small process/track/picture prototypes have
bounded passing evidence, but the MP4 correction hit trimmed-preroll failure.
A [correlated movie-time/eligibility contract](../../../evidence/story-005/movie-time-contract-gap.md)
would require a larger core design. Those prototypes are preserved separately;
none is a dependency of the selected feature port.

The [helper comparison](../../../evidence/story-005/helper9-discriminator.md)
demonstrates an unchanged helper compiling against actual FFmpeg9, matching
independent frame/moviePTS and rotation/SAR references, retaining one open across
forward/backward requests, and matching master-selected red/blue TrackNumbers
despite reordered Matroska entries. Root visually inspected paired outputs.
The alleged origin-collapse failure was refuted by exact raw records: origin0,
actual2s and duration14s match the initial-gap movie reference. It was an unsupported
relayed interpretation, explicitly corrected without a product repair.

Normal contrib source integration is chosen over maintaining a second private
FFmpeg recipe or publishing diagnostic archive surgery. Independent source review
finds VLC's avformat ES identity uses stream index, not AVStream.id; FFmpeg ID
selectors and Dolby Vision group inheritance are concrete affected consumers.
Focused generated-identity and forced-avformat comparisons remain required.

The port is active in disjoint SOL6.1 medium lanes. Native checks await an unlocked
Mac. The source/behavior gates, NAS/freshness/restart, controls/playback cohort,
clean reproduction, independent review and final public package remain open.
Existing !7493/#29393 are disclosed context, with no inferred acceptance or
rejection. See the [current ledger](../../../evidence/story-005/current-readiness-ledger.md).
