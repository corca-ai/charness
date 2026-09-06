#!/usr/bin/env python3
"""Parse SOURCE and refresh the consumer's cache."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 1:
        print("usage: refresh_cache.py SOURCE", file=sys.stderr)
        return 2

    source = Path(args[0])
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"refresh_cache.py: {exc}", file=sys.stderr)
        return 1

    cache = Path(".state/cache.json")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(cache.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
