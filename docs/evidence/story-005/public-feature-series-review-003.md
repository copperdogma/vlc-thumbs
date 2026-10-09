# Draft public series revision 3 — exact license, attribution and data review

Source base `2e358f3098c2f2b7621d1dc568de8b61ad786322`; packaged tree
`dc28a08ab00aa6d4c43b6e5681dfe673cee72a70`. This reviews the exact 54-file
manifest, not ignored binaries or generated media. Phase 2 remains incomplete.
No commit, sign-off, submission, install or runtime acquisition occurred here.

## License and retained-source evidence

All 27 new C/Objective-C/header/Python source files contain an explicit SPDX
identifier: 22 GPL-2.0-or-later and five LGPL-2.1-or-later. The helper/application
and new fault/custom-AVIO tests retain GPL intent; standalone generators/direct
dependency scripts retain LGPL notices. All nine modified existing macOS `.h`/
`.m` leading copyright/license/author comment blocks exactly match the pinned
base bytes. The six other new inputs are build lists, Markdown guides and the
two FFmpeg diffs. No third-party full source/header was silently relabeled.

The FFmpeg diffs modify `libavformat/matroskadec.c` in the normal LGPL2.1-or-later
FFmpeg9 source, with its existing project/authors notices retained in the target.
They are raw diffs, not standalone licensed replacement source or prepared
FFmpeg submissions. The earlier dependency inventory still applies: selected
FFmpeg normal config has GPL/nonfree/version3 disabled; GSM preserves permissive
notices, LAME uses LGPL/Library GPL, OpenJPEG uses BSD2-clause and zlib has its
permissive notice. The source recipes/checksums are public. The zlib linked
archive does not have a separate feature source-rebuild receipt; do not upgrade
that provenance claim. This is source-license compatibility/inventory, not a
public binary compliance or patent certification.

The helper README now includes the public admission generator, 77-case test and
custom-AVIO recipes. `bin/timeline-preview/Makefile.am` explicitly distributes
every helper guide/generator/harness/direct probe, including the admission
generator and `test-io.c`. Native application/test files are enumerated by their
Autotools sources lists. This static closure check is not distcheck execution or
clean independent reproduction.

## Concrete unresolved human facts

1. The helper header says `VLC timeline enhancements contributors`, without an
   identified holder. Cam must supply the accurate holder/credit convention for
   the retained original helper and newly contributed code; the agent cannot
   equate a configured Git author with copyright ownership. New native/test files
   mostly supply SPDX only, so individual credit has not been recorded there.
   This is an attribution fact gap, not a finding that SPDX is invalid or that
   upstream mandates one exact header style.
2. Confirm the actual human author/credit roster for these retained/adapted and
   new contributions, and the name/email to place on eventual commits. Cam
   Marsollier's configured name/email is available, but it does not establish sole
   authorship or authorize credits for others. Existing VLC/FFmpeg credits must
   remain. The README's AI-assisted provenance is already explicit.
3. The two eventual dependency contributions need truthful author metadata,
   rationale/regression messages and an agreed submission boundary. Raw diffs
   currently assert none. No discovered requirement or human DCO/rights
   certification is satisfied by inventing a Signed-off-by. Ask for such an
   attestation only if the final confirmed submission route requires it.

No commit or author/sign-off metadata was created during package preparation.
Root owns resolution and the final package. A reviewer can inspect this draft
before those facts are supplied; it must not be called ready to submit.

## Private-data and exact-source review

All 54 complete source inputs and all generated public-series artifacts were
checked for personal filesystem roots, mounted-volume/private NAS paths, SMB
URLs, private IPv4 addresses, wrapper work paths, prototype trace/event hooks,
private-key/API-key markers and NUL/binary data. No matches were found. Markdown
guide links use public-relative source paths or public specification/tool URLs;
example `/path/to` and mock `/fixture` test paths are portable placeholders.
Five generated Python bytecode files are explicitly excluded and preserved in
the ignored workspace. No fixtures, dependency libraries, apps or local logs are
in the series. No experimental core patches are dependencies.

Fresh sequential cached application of all three patches to the pin equals the
recorded source tree exactly. Temporary indexes/object storage were isolated;
baseline objects were only read through alternates. Baseline and candidate index
hashes are unchanged, and the candidate raw bytes were rechecked after capture.
The prior series/manifest/receipt are preserved separately. See
`public-feature-series-validation.json` for exact sizes/hashes and storage use.

These checks do not establish every conceivable secret identifier is absent or
any native behavior passes. Scoped local H1 and warm NAS evidence and the app
build are now recorded in the public draft README; full native acceptance,
independent reproduction/distcheck and attribution remain open.
