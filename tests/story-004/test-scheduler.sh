#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
validation_dir="$repo_root/work/validation/story-004"
mkdir -p "$validation_dir"
clang -fobjc-arc -Wall -Wextra -Werror -framework Foundation \
  -I "$repo_root/src/macosx" \
  "$repo_root/src/macosx/VLCThumbnailScheduler.m" \
  "$repo_root/tests/story-004/scheduler_contract.m" \
  -o "$validation_dir/scheduler_contract"
"$validation_dir/scheduler_contract"
