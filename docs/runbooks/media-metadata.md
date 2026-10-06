# Media metadata storage

Follow accepted [ADR-001](../decisions/adr-001-media-metadata-storage/adr.md).

Reuse VLC's media/input identity access and lifecycle integration where useful.
Use a feature-owned Application Support store for durable timestamp/short-label
records and a separate feature-owned Caches area for regenerable thumbnail files.
Preferences may contain small settings. Do not append these assets to the
existing playback-resume keys or edit the live preferences plist directly.

Labels must survive app restarts, recent-history turnover/clearing, disabling
recent items, and thumbnail invalidation/eviction. Cleanup must remain confined
to disposable assets. Explicit label deletion/reset is a separate intentional
operation. Preserve original media bytes and isolate experiments from real stores.

No format/schema, directory name, replacement/move identity policy, quota,
extraction engine or migration is implemented yet. Resolve these against a
concrete build and test with isolated fixture stores before claiming persistence.
