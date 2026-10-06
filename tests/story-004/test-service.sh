#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
output="$repo_root/work/validation/story004"
mkdir -p "$output"
xcrun clang -arch arm64 -mmacosx-version-min=11.0 -fobjc-arc -fblocks -Wall -Wextra -Werror \
 -I "$repo_root/src/macosx" "$repo_root/tests/story-004/service_contract.m" \
 "$repo_root/src/macosx/VLCThumbnailService.m" "$repo_root/src/macosx/VLCThumbnailWorker.m" \
 "$repo_root/src/macosx/VLCThumbnailCache.m" "$repo_root/src/macosx/VLCThumbnailScheduler.m" \
 -framework Cocoa -o "$output/service-contract"
"$output/service-contract" "$repo_root"
