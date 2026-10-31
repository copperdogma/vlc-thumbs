# October 30 VLC contribution refresh

Current local review source: **16 commits, 70 changed paths**. No upstream push, merge request or acceptance is recorded. Qualification has an unresolved CLI shutdown gate.

- Upstream base: `5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09`.
- Exported head: `dd50411dad2b8c05144acbf0e7c63fb9150e0120`.
- Expected combined tree: `212c081ca9eb566a65b3979d272a788ae52653ea`.

The preserved source10 patches were reconstructed and their original combined tree verified before rebase. These are new successor commits, not recovered October 13 commit identities. An isolated-index replay of all 16 exported patches produces the expected tree. The final test-shell cleanup documents its intentionally unimplemented properties and scopes diagnostics to that shell. Its affected compile and five lifetime cases pass. The final commit contains only this test support change; manifest.json distinguishes each tested and exported source identity.

## Apply

From a clean upstream VLC checkout at the base above, apply the numbered patch files in `series` order using `git am`. For example, set `PATCH_DIR` to this directory's absolute path, then run:

```sh
git switch -c timeline-previews-20261030 5ccc5fa83f287d7ab7cc493f8dc2a31655fd2a09
git am "$PATCH_DIR"/0*.patch
git rev-parse 'HEAD^{tree}'
```

Compare the resulting tree with the expected tree above. Replayed commit IDs can differ because committer metadata differs. From this package directory, `shasum -a 256 -c SHA256SUMS` verifies the preserved files.

## Qualification

| Check | Result |
| --- | --- |
| Normal arm64 app build/package and signature validation | PASS with full GNU libtool |
| Fresh helper matrix | 77 passed |
| Packaged helper protocol | 13 passed |
| Main macOS test bundle | 597 passed, one skipped, zero failed |
| Separate context / hover reentrancy bundles | 7 / 11 passed |
| Affected vout lifetime fixture | Fresh compile / five cases passed; targeted warnings absent |
| Final core test group | 96 passed after the test-link correction |
| Extracted source archive build / helper protocol | PASS / 13 passed |
| Registered CLI startup/quit check | BLOCKED: SAP thread join during medialibrary cleanup; stopped after 306.64 seconds |
| Complete conventional distcheck | NOT RUN: known blocked host gate; no complete pass claimed |

The default Dolt accelerator failed on duplicated Objective-C++ language tags. Full GNU libtool compiled the same sources and enabled features using the recursive make override `LIBTOOL=$(top_builddir)/libtool`. No Dolt source patch or feature disable is included.

The first full normal check failed in a newly added upstream audio-output test. A one-line link correction adds the existing compatibility library, fixing an unresolved tdestroy call during teardown. The full final core group then passed; the long, unchanged macOS groups were not rerun. The source archive was built separately after correcting the private wrapper's Git-directory boundary. Optional archive install/uninstall/distclean and fresh desktop/VoiceOver/performance campaigns were not run.

The earlier audit reported 17 media-item property warnings. Two further warnings at VLCWindow.h declarations were also caused by our empty test shell, not the real window implementation. Scoped media-shell diagnostics and dynamic window accessors eliminate all 19 fixture warnings without unused fake methods or production suppression. The final affected compile has zero warnings; no warning-free whole-tree claim is made. Thirteen whitespace entries are inherited nested FFmpeg patch context.

The source refresh drops our OpenGL initialization fix because an equivalent fix is now upstream, omits an already-distributed header, resolves test-support conflicts, and updates the dependency/Metal recipe. Thumbnail production logic was not manually changed during conflict resolution. Historical runtime evidence remains historical. The fifteen-patch predecessor remains unchanged under ignored work/story007-refresh-20261030/submission; its manifest and hash ledger are preserved with the compact evidence. The first fifteen successor patch IDs match it, so the warning-clean source differs only in the test shell.

[Detailed report and limitations](../../../docs/evidence/story-007/upstream-refresh-20261030.md) retain source provenance, first failures, fixes and coverage. [Source10](../contribution-series-source10/CONTRIBUTION.md) remains an unchanged predecessor package.

## Submission boundary

Current master has no merged native macOS seek-hover thumbnail implementation in this bounded scout. Overlapping [MR !7493](https://code.videolan.org/videolan/vlc/-/merge_requests/7493) remains open. This does not establish absence of every competing proposal.

[VideoLAN's current AI policy](https://code.videolan.org/videolan/vlc/-/blob/master/doc/VideoLAN_AI_Policy.md) requires Cam to personally review, understand and submit the contribution, and disclose AI assistance in the MR. Agents prepare the source and evidence; no agent submission is authorized by this package.
