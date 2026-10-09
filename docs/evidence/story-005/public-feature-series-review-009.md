# Draft public series revision 9 — exact license, attribution and data review

Source base `2e358f3098c2f2b7621d1dc568de8b61ad786322`; packaged tree
`48a6b53f29d7f99ea410ba0e9d7085f7d9673acb`. This reviews the exact 59-file
manifest, not ignored binaries or generated media. Phase 2 remains incomplete.
No commit, sign-off, submission, install or runtime acquisition occurred here.

## License and retained-source evidence

All 28 new C/Objective-C/header/Python source files contain an explicit SPDX
identifier: 23 GPL-2.0-or-later and five LGPL-2.1-or-later. The helper/application
and new fault/custom-AVIO tests retain GPL intent; standalone generators/direct
dependency scripts retain LGPL notices. All ten modified existing macOS `.h`/
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

All 59 complete source inputs and all generated public-series artifacts were
checked for personal filesystem roots, mounted-volume/private NAS paths, SMB
URLs, private IPv4 addresses, wrapper work paths, prototype trace/event hooks,
private-key/API-key markers and NUL/binary data. No matches were found. Markdown
guide links use public-relative source paths or public specification/tool URLs;
example `/path/to` and mock `/fixture` test paths are portable placeholders.
Five generated Python bytecode files are explicitly excluded and preserved in
the ignored workspace. No fixtures, dependency libraries, apps or local logs are
in the series. No experimental core patches are dependencies.

Fresh sequential cached application of all four patches to the pin equals the
recorded source tree exactly. Temporary indexes/object storage were isolated;
baseline objects were only read through alternates. Baseline and candidate index
hashes are unchanged, and the candidate raw bytes were rechecked after capture.
The prior series/manifest/receipt are preserved separately. See
`public-feature-series-validation.json` for exact sizes/hashes and storage use.

These checks do not establish every conceivable secret identifier is absent or
any native behavior passes. Scoped local H1 and warm NAS evidence and the app
build are now recorded in the public draft README; full native acceptance and attribution remain open. Independent build/helper/
registered-suite proof is scoped below; conventional distcheck failed and is
not qualified.

## Current runtime evidence and remaining gates

The reviewed environment and synchronization test repairs are verified. The
independent focused service run passed two tests with zero failures. The quiet
independent registered suite passed 288 counted tests: 269 main with one explicit
optional-volume skip, seven context and twelve hover; zero failures. Its source
scope is revision 6 tree `1a567b8705d3f744afc2b873458a5e8af02f7a7b`.
The optional actual-ENOSPC selector passed separately with its owned-volume guard.
These results replace the earlier pending runtime descriptions; no new run is
claimed by this review correction.

Later revisions add source-header distribution declarations and reconcile the
helper guide. Their runtime/test/build inputs preserve that tested source scope.
The final archive membership/bytes, minimal configuration, compilation and
linking passed. Conventional distcheck then reported 80 pass, five skip and
seven fail; install/installcheck/uninstall/DESTDIR cleanup/redist/distclean were
not reached. Bounded untouched-master normal-configuration tests reproduced
clock and TLS failures, but that configuration differs from minimal distcheck;
TLS-client attribution and other causes remain unproven. Independent app
artifact/signature verification is separate from its outer runner's exit 1.
Actual native preview, complete controls, reader, restart reuse and matched
playback/performance acceptance remain unqualified. Human attribution is pending.

## Historical freeze descriptions

Revision 4 captured the focused player/controller test, SDK/host recipe, service
fault and optional ENOSPC tests, duration repair and representative long-fixture
generator. The GPL player test uses synthetic owned input identifiers with
playback disabled and normal VLC plugin descriptors; it tests the ineligible
input epoch boundary, not selected-track, duration or native GUI behavior.

Revision 5 added the existing library test support's owned plugin-path environment
restoration after libvlc release. Revision 6 added bounded completion waiting and
separate no-reader write-fault scenarios with explicit cancel/join. Independent
review cleared both repairs, and the current focused/suite results above verify
their runtime scope. At those historical freezes production code was unchanged
from revision 4; that historical statement is not a claim that every later
source-series file is identical to revision 4.

Revision 7 added four unchanged Apple headers to two Automake source lists.
Revision 8 added unchanged LazyPreparser.h to its media-library consumer list,
forming the leading five-header/three-Makefile distribution patch. Their earlier
archive failures and source proofs remain preserved in reviews 001–008 and their
separate receipts. Revision 9 changes only the helper README from revision 8;
patches 0000/0001/0003 and all runtime/test/build inputs are unchanged. The guide
records executed proof, host-tool/Git containment prerequisites, failed distcheck
and baseline-comparison limits. No source/patch/license/attribution change occurs
in this evidence-note correction.


### Attribution addendum — 2026-10-06 resumed authorization

The unresolved-human-credit language above records the earlier review snapshot.
Cam subsequently approved contributor credit, AI-assistance disclosure and an
open-source contribution under existing VLC GPL/LGPL terms. Contributor/contact
identity is taken from current Git configuration: Cam Marsollier
<cam.marsollier@gmail.com>. Existing third-party notices and collective contributor
source notices remain. This does not assert sole copyright ownership, assignment,
waiver or Signed-off-by. No mandatory source-header rewrite was identified; any
maintainer request for holder precision remains a review question. Wrapper metadata
now expresses this distinction and passes an independent59-source/9-artifact hash
and privacy/link/identity check. Manifest SHA256 after that metadata-only update:
`6eb4c9a5ee0ec6c0238592a86a2ea3570868d47be1c27079f6a3f85b715ac987`.
Source tree and all four patches remain unchanged. Native/performance acceptance
and actual demonstration packaging remain open; nothing has been submitted.
