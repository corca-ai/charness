#!/usr/bin/env python3
"""Schema + closed-enum validation over the RCA conversion ledger.

Blocks only on malformed lines (changed-surface scope). The conversion rate is
advisory and is never evaluated here; this validator must not become a
whole-artifact gate on the metric value.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from scripts import rca_ledger_lib as lib
except ImportError:
    import rca_ledger_lib as lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate every line of the RCA ledger.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ledger", default=None, help="Override ledger path (defaults to canonical).")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    ledger_path = lib.resolve_ledger_path(repo_root, Path(args.ledger) if args.ledger else None)
    errors = lib.validate_ledger(ledger_path, lib.load_schema())

    result = {
        "status": "valid" if not errors else "invalid",
        "ledger_path": lib.portable_path(repo_root, ledger_path),
        "error_count": len(errors),
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        print(f"invalid: {len(errors)} malformed line(s) in {result['ledger_path']}", file=sys.stderr)
        for entry in errors:
            print(f"  line {entry['line']}: {entry['error']}", file=sys.stderr)
    else:
        print(f"valid: {result['ledger_path']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
