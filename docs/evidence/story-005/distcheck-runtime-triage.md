# Source archive runtime-test boundary

The guarded `072705Z` run on public revision8 compiled and linked the extracted
read-only archive, including all five previously omitted headers. It then failed
at `make check`:92 tests,80 pass,5 skip,7 fail. Elapsed437.5s; minimum free space
6,876,102,656bytes. This is not a distcheck pass. Install, installcheck, uninstall,
distclean and final self-containment stages were not reached.

The [official Automake contract](https://www.gnu.org/software/automake/manual/1.16.2/html_node/Checking-the-Distribution.html)
places those stages after the fresh VPATH build and tests. The failed run, archive,
test logs and generated translation deltas are retained. Do not skip failed tests
or weaken checks to relabel this result.

## Bounded diagnosis

Independent source comparison finds15 relevant failing-test and implementation
files byte-identical to the pinned source, reproduction checkout and archive.
The upstream minimal distcheck defaults already disable avcodec, avformat,
postproc and swscale; the feature adds helper-disable, and this host runner adds
macOS-GUI-disable. This is separate from the feature-enabled app/XCTest proof.

| Failure | Observed evidence and limit |
|---|---|
| Attachments | Explicit missing BMP encoder; the fixture exports BMP and avcodec is disabled. |
| CVPX image | PNG encoder loads, then no video converter is found. |
| SPU | `spu_Create` fails before subtitle tests; its required YUVA-to-RGBA converter is unavailable. |
| Input decoder | CC/subpicture assertion follows missing-converter messages; the shared prerequisite explanation is consistent, not separately demonstrated. |
| TLS | Known-certificate handshake fails. Test uses GnuTLS trust options while SecureTransport has higher selection priority; selected-client attribution is not logged. The pinned certificate is valid2016 through9999, excluding expiry. |
| Clock | Exact equality fails in simulated `drift_72`; this is not a measured two-hour wall-clock run. Cause remains unresolved. |
| OpenGL | Context/framebuffer checks succeed, then renderer setup reports `GL_INVALID_OPERATION`. Cause and any relationship to the locked session remain unproven. |

Root separately verified that current baseline, candidate, reproduction and
archive `src/misc/picture.c` all hash to
`304c826d1246002b4e02d07feebfe993a9e8eb596403314cc7531a74a2ac8fb0`.
The retained orientation prototype is not in this public series; an initial
reviewer reference to changed picture setup used obsolete scope and is withdrawn.

## Decision

No production or test change follows from these seven failures. Preserve the
unchanged feature suite result (288 counted, one optional-volume skip, zero
failures), with actual ENOSPC separately verified. Freeze the source guide with
the partial archive result and remaining native limits. Two existing baseline
selectors, clock and TLS, are authorized only as a bounded attribution diagnostic,
without rebuild, backend overrides or host changes. Both now reproduce the same
assertion failures on untouched master: clock drift_72 in1.848s and TLS acceptance
in0.982s, native exit134 each. The normal driver records FAIL while itself exiting0;
its exit is not a test pass. Both owned groups were reaped. See
[baseline attribution](baseline-clock-tls-attribution-result.md). Their normal
full configuration differs from distcheck, so matching failures are not a matched
whole-build comparison or proof of the selected TLS backend. OpenGL and native
interaction work wait for the interactive Mac.

The distribution runtime gate remains open. Broader upstream repairs or changes
to the acceptance criteria are not inferred from this diagnostic.
