#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
validation_dir="$repo_root/work/validation/story-004"
mkdir -p "$validation_dir"
clang -fobjc-arc -Wall -Wextra -Werror -framework Foundation \
  -I "$repo_root/src/macosx" \
  "$repo_root/src/macosx/VLCThumbnailCache.m" \
  "$repo_root/tests/story-004/cache_contract.m" \
  -o "$validation_dir/cache_contract"
VLC_CACHE_TEST_ROOT="$validation_dir" "$validation_dir/cache_contract"
