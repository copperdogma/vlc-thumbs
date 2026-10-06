# Local story build and validation

Read the active story and relevant Ideal/spec/state/graph, then verify substrate.
Plan the bounded change and honor the applicable plan gate and existing user
scope. Keep delegation disjoint, optional and proportional. Use current primary
VLC documentation/source for external interfaces. Deterministic UI/persistence
features need behavioral baselines; no paid model baseline is required.

Use `docs/runbooks/build-vlc-macos.md` for the verified current-host build
route and repairs. Reuse the existing isolated build and check free space;
record feature patches separately from compatibility repairs. `make validate` only checks workflow. When a candidate exists,
record actual native UI commands/observations and fixture evidence. Verify media
hashes, frame/time correspondence, playback and restart/identity behaviors.
Review scope honestly, then `/validate` and `/mark-story-done`; commit/push only
when requested. Remove redundant code/docs only inside authorized project scope.
