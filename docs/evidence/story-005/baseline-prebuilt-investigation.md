# Bounded prebuilt / CI investigation

2026-10-06 UTC. Source pin `2e358f3098c2f2b7621d1dc568de8b61ad786322`.

The official build script's default
`https://download.videolan.org/pub/videolan/contrib/aarch64-apple-darwin19/vlc-contrib-aarch64-apple-darwin19-latest.tar.zst`
returned404, recorded in baseline015951Z build log. Source-contrib fallback
progressed without substituting that archive.

Pinned `extras/ci/gitlab-ci.yml` defines a more precise artifacts.videolan.org
URL keyed by the latest commit that changes extras/tools, contrib, extras/ci,
or extras/package/macosx. `extras/ci/get-contrib-sha.sh macos-arm64` currently
returns HEAD locally, but the checkout is shallow and HEAD's visible subject is
a Qt-only change; its history boundary makes that result unsuitable evidence
for the real last contrib change.

Four bounded VideoLAN GitHub mirror commit-history queries at the pinned SHA
identified latest path changes: extras/ci15b71e3fa6d49ed2845dfb1324760984eae6101c
(Sep29), contrib55236e656987ea1b2a7dfe14ffe6b42d371abaef(Sep28),
extras/package/macosx c849f94b74dffc2fd21331bc86b72b508180d9dc(Sep17),
extras/tools275bbed0a08433de13c007bf00f1aad2ebd7acbb(Aug28).

Inferred candidate URL returned HTTP200,216247250bytes:
https://artifacts.videolan.org/vlc/macos-arm64/vlc-contrib-aarch64-apple-darwin19-15b71e3fa6d49ed2845dfb1324760984eae6101c.tar.zst
No archive was downloaded or substituted. Complete-history verification remains
needed before claiming the inferred commit is exactly the CI-derived key.

Canonical GitLab API reports pinned master pipeline744545 success and jobs
2873422(macos-arm64),2873421(macos-x86_64) success:
https://code.videolan.org/videolan/vlc/-/pipelines/744545
https://code.videolan.org/videolan/vlc/-/jobs/2873422
https://code.videolan.org/videolan/vlc/-/jobs/2873421
The arm64 job trace endpoint returns401; actual archive selection and full test
output are unknown. API and HTTP receipts are preserved under ignored
`work/story005-scout/`. This metadata is upstream CI evidence, not local app or
feature qualification.

Follow-up: parent authorized bounded history deepening. `git fetch --deepen=200
origin master` completed with HEAD unchanged and tracked source clean. Official
`get-contrib-sha.sh macos-arm64` then returned exactly
`15b71e3fa6d49ed2845dfb1324760984eae6101c`; the inferred archive key is now
locally confirmed by the official recipe. Source-fetch attempt015951Z was
interrupted after508s to use that exact official prebuilt through
`VLC_PREBUILT_CONTRIBS_URL`, rather than substituting a different-version archive.
Attempt020819Z records the URL/environment and official download/extract outcome.
All previous downloads/artifacts remain preserved. Independent source-contrib
reproduction is not claimed; the default generic latest URL failure remains.
