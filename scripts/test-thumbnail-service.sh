#!/bin/bash
# Retired Story 002 v2 service runner; archived evidence remains historical.
set -euo pipefail
cat >&2 <<'MESSAGE'
The Story 002 one-shot service runner is retired for the persistent v3 service.
Use the current suites from the project root:
  bash tests/story-004/test-service.sh
  python3 tests/story-004/helper_worker_contract.py
  python3 tests/story-004/track_count_contract.py
See tests/story-004/README.md. Historical Story 002 latency results are not rerun by these contracts.
MESSAGE
exit 2
