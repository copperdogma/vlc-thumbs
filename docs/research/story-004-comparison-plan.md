# Story 004 prospective comparison plan — 2026-10-05

Declared before scoring a candidate. Preserve all attempts and raw evidence in
ignored work/validation/story004. Do not repeat invalid cohorts until a concrete
acquisition defect is fixed. Shared-host load is expected; report ranges rather
than demand a static machine or silently pool different builds.

## Frozen inputs

Story 002 build155231 app/source/binary hashes are frozen in
work/validation/story004/baseline-155231/manifest.json. Hashes match its recorded
manifest. Pristine work/build/VLCBaseline.app supplies ordinary-control/playback
baseline. Both feature and vanilla arms must record executable/module/helper,
observer/pointer/fixture hashes before and after acquisition.

## Preview/IO comparison

Compare the same local generated standard MP4/MKV and reported long mounted-SMB
H.264 movie. Private path/results stay ignored, no private video is copied or
uploaded. Pointer patterns: settled distant targets, repeat visits, stationary
miss, rapid sweep, jump/recenter and exit/reenter, then media close/reopen and
app restart. Start with four distant targets corresponding to the existing NAS
stage probes (1493, 3200, 6000, 4600 seconds) in that declared order, then their
repeat visits. Mirror generated-fixture targets inside its duration. Reuse the
frozen old helper versus candidate persistent worker for isolated initialization
and read metrics; this diagnostic does not substitute for native visible proof.

Keep initial worker preparation, per-request work and queue delay separate.
Record usable images, actual PTS, first useful image time, full completion time,
open/read/seek counts, source bytes, timeout/error/stale state, cache tier and
fingerprint cost. Fingerprint reads are separately attributed. OS/NAS cache warmth
is uncontrolled; no cold-source claim or causal speedup from one ordering pair.
Native proof must visibly include sparse preparation, settled hover and moving
hover, near-cache bridging, context changes and reopen. Compare success/ranges
and initialization waste, not absolute SLA/p95 gates inherited from Story 002.

## Ordinary control and playback

Use existing qualified phase/AX setup, real pointer and actual rendered-knob
observer. Fresh complete cohort: AB, BA, BA, AB temporal blocks, 5 responses per
arm per block, 20 per arm. Acceptance is candidate median <= baseline median
*1.20. Wrong owned window/PID, mismatched templates/geometry, canceled acquisition,
no actual observed rendering or changed inputs is inconclusive. Report all
samples and ranges; no completion-seek, p95 or general-host guarantee.

Run matched pristine/candidate playback pairs with background preparation and
hover active using the existing dropped-frame/audio/resource observer. Record
CPU/RSS deltas and unresolved visual-stall attribution under shared load. A
reproducible feature-caused disruption is a defect; capture setup failure cannot
be a pass. Native checks cover main/detached/native/custom fullscreen, preference
Save/Cancel/restart/off, normal seeking/volume and inherited reader focus.

## Deterministic contracts and decision boundaries

Retained-helper v2/v3 out-of-order pixels/PTS, bounded startup/request/idle/hard
faults; finite scheduler/gap/hover/fairness transitions; atomic partial cache,
checksum/schema/ownership/quota faults; cross-open/restart and media/track/version
replacement checks qualify their own boundaries. Cam subsequently delegated the freshness choice; ADR-003 accepts metadata plus sampled SHA256 and records the limitation for unchanged metadata/unsampled edits. Candidate runs use this accepted policy; full hash remains a deterministic diagnostic.

### Playback acquisition detail

The long-fixture choice was stated before baseline acquisition; this written detail was added during pair1 candidate acquisition, before scoring. Original matched playback/observer contract above remains unchanged.

Use a generated7200.491s MP4, video copied from the owned five-minute fixture, with a continuous440Hz64kbps AAC tone. Stream-copy loop24times yields287,360,717bytes (274MiB), avoiding a whole private movie copy or heavy video encode. Pair1 uses preparation-playback-001.mp4; subsequent pairs use fresh owned identities with the same bytes so preparation is active rather than already completed before observation. Pair order AB,BA,AB; same file within each pair,60s active interval, same owned display/audio observer and diagnostics enabled. Inspect actual background dispatches within each active interval rather than assuming a long duration establishes exposure. Shared-host loads remain uncontrolled. Native pointer only; no GUI interference during acquisition.
