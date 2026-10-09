# Prebuilt SDK path metadata repair

Attempt021602Z configured successfully and compiled core/macOS/codec modules,
then stopped exit2 after198.8s at the optional ncurses plugin link. Official
exact prebuilt `lib/pkgconfig/ncursesw.pc` Libs embeds an absolute
`-isysroot .../MacOSX26.2.sdk`; this SDK is absent on the Xcode27 host. That
flag overrides the actual SDK27 path and leads to `ld: library 'm' not found`.
Only ncursesw.pc and libchromaprint.pc retain this SDK path in .pc/.la metadata;
chromaprint's framework search path is not yet a terminal failure.

Problem class: prebuilt build-host metadata leaking into consumer compilation.
Established Autoconf/pkg-config escape hatch is the documented NCURSES_LIBS
environment override. Pinned generated configure --help lists NCURSES_LIBS and
configure lines71976–71985 explicitly uses a supplied value before querying
pkg-config. Keep all product modules enabled and override only libs to the
actual owned contrib prefix plus `-lncursesw`; actual host compiler SDK remains
set by the official build environment. No .pc, source, dependency or build-code
edit is required. No system-library discovery broadening.

Forcing reconfigure preserves existing generated Makefile as ignored
`work/story005-master-baseline/Makefile.before-ncurses-override`, then the
official build script regenerates it. Exact NCURSES_LIBS override is recorded
in attempt022001Z and the monitor. Source remains pinned/clean; existing
objects are reused only through the official make dependency graph.
