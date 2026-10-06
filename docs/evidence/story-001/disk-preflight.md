# Story 001 — disk-capacity preflight, 2026-10-03

Cam requested disk-footprint investigation before the first build. No build,
dependency installation, large archive download, or cleanup was started.

## Measurements

- `df -h .`: internal APFS data volume reports about 11 GiB available, 100%
  capacity after rounding. Python disk_usage readback: 12,092,178,432 bytes
  (11.26 GiB free) at this check. This is transient, not a capacity guarantee.
- `du -sh work/upstream/vlc-3.0.24`: 163 MiB allocated, including 25 MiB `.git`.
  Git pack reports 24.12 MiB. The existing source is a shallow release checkout,
  so it does not carry full upstream history.
- `du -sh work`: 163 MiB. No tool/contrib/product build trees exist yet.
- `df -h` also identifies an SMB-mounted volume (mount name omitted) with about
  8.7 TiB available. This is network storage, not an external local SSD; build
  performance/filesystem compatibility there has not been tested.

## Why source size is not the peak build size

Pinned [macOS build script](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/extras/package/macosx/build.sh)
boots/builds host tools, installs or builds contrib dependencies, compiles VLC
and assembles VLC.app. Source archives, extracted dependency sources, compiled
objects/static libraries, installed dependency prefixes and app artifacts may
coexist. A separate VLC `-C` build directory does not relocate extras/tools or
contrib work by itself. Copying only the final build directory to other storage
would therefore leave meaningful writes on the internal disk.

[Contrib makefile](https://github.com/videolan/vlc/blob/6de05adcbaf2e8b85fe86aad4169393098628119/contrib/src/main.mak#L593-L606)
uses a host-triplet prebuilt archive by default. HEAD-only probe of the HTTPS
variant for this host:

`https://download.videolan.org/pub/videolan/contrib/aarch64-apple-darwin27/vlc-contrib-aarch64-apple-darwin27-latest.tar.zst`

returned HTTP 404. No archive body was downloaded. This does not prove no
compatible archive exists elsewhere, but we cannot assume the default prebuilt
route limits dependency space. Do not change the kernel triplet blindly to
borrow another archive; verify its provenance/SDK/architecture first.

No authoritative or locally measured peak requirement for this exact build was
established. Do not report an invented precise build size. Multiple GiB is a
planning risk based on the source/build stages, not a measured requirement.

## Disposition

Do not start the unbounded full build on the current 11.26 GiB headroom. Source
inspection and small document work can continue. Prefer a local external SSD
for the entire tools/contrib/source/build workspace, or free substantial internal
capacity first. About 30 GiB free is a conservative initial planning target,
not a proven VLC minimum or guarantee. A build should have an explicit budget,
free-space monitoring and a reserve for macOS; dependency route and archive/
installed sizes still need qualification. A source-built contrib route may need
more than that planning allowance.

Network storage could hold archives or a workspace after compatibility testing,
but its large free-space number alone does not qualify compiling there. No
external location is selected and no unrelated files were inspected or deleted.
