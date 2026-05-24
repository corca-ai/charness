#!/usr/bin/env python3
"""Report the RCA-to-learning conversion rate from the ledger.

Reports the rate twice: including seed events (sanity) and excluding them (the
figure a baseline target is set from). OFF-state honesty: until auto-append is
wired (slice 2), it prints the `auto_append: OFF` banner, emits `n/a` (not 0%)
for an empty seed-excluded window, and refuses to print a non-seed baseline rate
while zero non-seed events exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts import rca_ledger_lib as lib
except ImportError:
    import rca_ledger_lib as lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate the RCA conversion rate.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ledger", default=None, help="Override ledger path (defaults to canonical).")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    ledger_path = lib.resolve_ledger_path(repo_root, Path(args.ledger) if args.ledger else None)
    payload = lib.aggregate(lib.read_events(ledger_path))

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(lib.render_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
