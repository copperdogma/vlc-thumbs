#!/usr/bin/env python3
"""Retired Story 002 v2 cache/service fault runner; no disk image is created."""
import sys

if __name__ == '__main__':
    print('The Story 002 one-shot cache/service fault runner is retired.\n'
          'Use bash tests/story-004/test-cache.sh and bash tests/story-004/test-service.sh.\n'
          'See tests/story-004/README.md; historical physical ENOSPC evidence remains dated,\n'
          'and these current contracts do not claim a fresh mounted-disk ENOSPC trial.', file=sys.stderr)
    raise SystemExit(2)
