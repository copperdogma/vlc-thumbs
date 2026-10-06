# Working VLC 3.0.24 macOS development build

2026-10-04: attempt 009 exits 0 and assembles VLC.app. Exact command, source
commit, environment and measured disk use are in attempt.json. Final binary is
arm64 and reports VLC 3.0.24-0-g6de05ad. Upstream signature verification passed;
after development-profile isolation/re-signing, strict deep verification passed
again. All 339 bundled Mach-O objects are arm64; dependency scan found no
/usr/local, /opt/homebrew or disposable build-path dynamic dependencies
(bundle-dependencies.json). Native GUI played generated MPEG-4 video, paused, and sought via a timeline
click from 00:00 to 00:02; the rendered frame timestamp is 2.333.

See verification.json, version.txt, fixture.json, playback-smoke.log,
gui-accessibility.txt, gui-seek-accessibility.txt, gui-smoke.png and gui-seek.png.
Dependency download hashes are in dependency-downloads.json; source fetches were
checked by upstream rules. Reproduction: docs/runbooks/build-vlc-macos.md.

## Repairs and scope

- Source-built contribs (`-c`): default prebuilt arm64 archive returned HTTP 404.
- Excluded Intel pkg-config library defaults with PKG_CONFIG_LIBDIR.
- Added ACLOCAL_PATH to existing pkg.m4 build macros (not runtime libraries).
- Wrapped isolated Ninja with -j4 to avoid Make 3.81 jobserver errors.
- Forced isolated tools to native /usr/bin/python3; rebuilt six Meson packages
  whose earlier Intel Python detection selected x86_64 assembly/features.
- Local contrib patch ignores /usr/local for CMake library/header searches;
  rebuilt four packages with host-library leakage. Patch in attempt 008.
- Disabled Sparkle auto-update in this development build; old framework/SDK
  deployment combination was unavailable.
- Refreshed VLC configuration after dependency repair to remove stale -lb2.

No preview/bookmark feature patch. No installed VLC, user media or real VLC
preferences changed. GUI uses org.videolan.vlc-thumbs.development; first-run
metadata prompt skipped only in that profile and network metadata disabled.
Initial GUI AX timeout traced by process sample to that first-run modal prompt.

After re-signing plugins, regenerated plugins.dat and signed that cache file,
then re-sealed the outer app without re-signing plugins again. This preserves
plugin mtimes and removes stale-cache warnings while retaining valid signature.
Initial command-line smoke rejected unsupported --no-one-instance before
playback; retry removed it. Playback then exited 0, selected avcodec, displayed
its first picture and reached EOF. Headless window/hardware-decoder warnings do
not establish native GPU behavior; actual GUI rendering is captured separately.

Current whole workspace ~5.7 GiB; no low-disk stop or artifact cleanup occurred.
These are measured successful-build footprint and sampled headroom, not a
universal storage requirement. A full clean rebuild was not repeated; final
success is incremental after the recorded repairs. Fullscreen, audio, other
formats and both requested enhancements remain untested/unimplemented.
