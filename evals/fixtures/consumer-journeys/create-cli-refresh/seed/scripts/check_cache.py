#!/usr/bin/env python3
"""Read and report the status of the current cache."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if args:
        print("usage: check_cache.py", file=sys.stderr)
        return 2

    cache = Path(".state/cache.json")
    if not cache.is_file():
        print("missing")
        return 1

    try:
        json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("invalid")
        return 1

    print("ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
