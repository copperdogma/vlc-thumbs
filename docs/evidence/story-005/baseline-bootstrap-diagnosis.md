# Baseline bootstrap macro discovery

Attempt020819Z stopped with exit1 after164.7s, after exact official contrib
extraction/native-tool build but before VLC configure or compile. First missing
macro: `PKG_PROG_PKG_CONFIG` required but not defined. Subsequent undefined
`AC_*`, `dnl` and `m4_n` reports are a cascade, not independently diagnosed.

Problem class: third-party Autoconf macro discovery across different installation
prefixes. Owned extras/tools/share/aclocal contains VLC's freshly built tools'
macros but no pkg.m4. Host pkgconf2.5.1 and its macro are installed separately:
`/usr/local/share/aclocal/pkg.m4`, SHA256
`07f90de7dad7478234c170dd8c85bdbab9252e4d9e3fc4d2c54ef274ff370141`.
Generated aclocal.m4 does not include that file/PKG macro definition.

Established solution: Automake's `ACLOCAL_PATH` external macro search path.
Pinned VLC bootstrap lines28–31 explicitly cite GNU's macro-search manual:
https://www.gnu.org/software/automake/manual/html_node/Macro-Search-Path.html
Network fetch timed out. The exact newly built Automake1.18.1 source's
`extras/tools/automake/doc/automake.texi` lines3637–3652 confirms colon-separated
ACLOCAL_PATH directories add third-party macros and explicit-I paths retain
precedence. Local primary tool source is the applicability evidence.

Proposed minimal experiment: set `ACLOCAL_PATH=/usr/local/share/aclocal`, run the
official bootstrap explicitly to replace the incomplete generated configure,
then rerun the official build. This changes host macro discovery, not product
source or library discovery. PKG_CONFIG_PATH stays empty and PKG_CONFIG_LIBDIR
stays isolated until the official configure recipe selects its owned contrib
prefix. No libc/header/library paths are relaxed. A bootstrap pass will verify
whether the diagnosis covers the terminal failure.

Result: parent approved the repair. Official bootstrap with owned tools first in
PATH, native Python3.14, `ACLOCAL_PATH=/usr/local/share/aclocal` and unchanged
PKG_CONFIG isolation exited0, ending `Successfully bootstrapped`. Generated
aclocal.m4 now contains pkg.m4 definitions. Full output is
`baseline-bootstrap-repair.log`; tracked source remains clean. The baseline
monitor now retains that exact ACLOCAL_PATH override for reproducible retries.
