#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cli_side_effect_probe_lib import build_inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--contract-file", action="append", default=[])
    parser.add_argument("--execute-probes", action="store_true")
    parser.add_argument("--fail-on-findings", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    contract_paths = [(repo_root / path).resolve() for path in args.contract_file]
    payload = build_inventory(
        repo_root,
        contract_paths=contract_paths,
        execute_probes=args.execute_probes,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in payload["findings"]:
            command = finding.get("command", "")
            path = finding.get("path", "<none>")
            print(f"{finding['type']}: {path} {command}")
    return 1 if args.fail_on_findings and payload["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
