#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from standing_gate_verbosity_lib import inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inventory(args.repo_root.resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for name, axis in payload["axes"].items():
            print(f"{name}: {axis['status']}")
            for finding in axis["findings"]:
                path = finding.get("path") or "<standing-gate>"
                print(f"  - {path}: {finding['type']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
