# ADR-001 — evidence synthesis

This summarizes the existing pinned-source investigation and Cam's accepted
storage direction. No new research run, provider comparison, runtime experiment,
or implemented persistence result is claimed.

VLC 3.0.24 macOS resume data is a preference dictionary keyed by decoded media
URI, holding integer seconds, plus a recency-order list. The source caps retention
at 30 and clears both keys with recent history. Existing bookmark input options
can carry names/times but are not proof of automatic durable per-file reopening.

User-authored short labels have a different lifetime from recent viewing history
and regenerated thumbnails. Accepted: durable feature-owned Application Support
store, disposable feature-owned Caches images, and optional small preference
settings. Reuse VLC media/lifecycle integration without coupling retention.

Evidence and source links are in ../adr.md and
../../../research/story-001-vlc-macos-timeline.md. Format, schema, directory names,
identity, migrations and quotas remain open. The implementation follow-up prompt
lists questions; no absent runtime is scored as failure.
