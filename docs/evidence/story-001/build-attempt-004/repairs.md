# Build environment repairs before attempt 004

Attempt 003: source dependencies progressed, but Ninja 1.13 jobserver handling
caused Apple GNU Make 3.81 `read jobs pipe` errors. Meson install also logged
invalid jobserver descriptors. Wrapped the isolated tool Ninja executable with
an explicit `-j4`, which Ninja source ninja.cc:1731 shows disables its jobserver
client. Original executable retained as ninja.real. Wrapper:

```sh
#!/bin/sh
exec "$(dirname "$0")/ninja.real" -j4 "$@"
```

Autoreconf then failed in aribb24: PKG_CHECK_MODULES remained undefined and its
AC_DEFINE body was flagged. Tool prefix lacks pkg.m4; system pkg-config's macro
exists under /usr/local/share/aclocal. Added ACLOCAL_PATH for build macros only;
PKG_CONFIG_LIBDIR still excludes Intel library defaults. No upstream feature
source changed; all mutable tool artifacts remain in ignored work/build.
