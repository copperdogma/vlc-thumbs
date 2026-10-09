# Decisions

- [ADR-001: Media metadata storage and retention](adr-001-media-metadata-storage/adr.md)
  — Accepted: durable short labels in Application Support, disposable thumbnails
  in Caches, and small settings in preferences. Schema/identity/quotas remain open.

- [ADR-002: Native timeline adapters and isolated thumbnail decoding](adr-002-native-thumbnail-services/adr.md)
  — Accepted for Story 002; Cam selected keyframe-first MVP sampling. Extra
  decoded samples remain optional after trying the MVP.

- [ADR-003: Persistent thumbnail preparation and cache freshness](adr-003-persistent-thumbnail-preparation/adr.md)
  — Accepted for Story 004; persistent private helper, finite progressive
  coverage, hover priority, and metadata plus sampled-hash freshness for
  disposable thumbnails. Story 004 is reopened for selected-track count
  correspondence and useful disk retention under quota pressure.

Imported skill references to source-project ADR numbers are examples, not local decisions.

- [ADR-004 — Upstream preview integration](adr-004-upstream-preview-integration/adr.md): Accepted technical plan for Story005; retained helper on master through normal FFmpeg9 contrib/build, existing native hover owner and preserved behavioral contracts. Phases1/2 are locally qualified at the disclosed bounded scope in [current source10 verification](../evidence/story-005/current-source10-final-verification.md); no maintainer acceptance claimed.
