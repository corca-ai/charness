#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    repo_root = next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "lint_ignore_inventory_lib.py").is_file())
    import sys

    sys.path.insert(0, str(repo_root))
    from scripts.lint_ignore_inventory_lib import inventory_lint_ignores

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = inventory_lint_ignores(args.repo_root.resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            codes = ",".join(finding["codes"]) or "*"
            print(f"{finding['tool']}:{finding['scope']}:{codes} {finding['path']}:{finding['line']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
