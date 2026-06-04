#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_standing_test_economics = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_test_economics_lib")
inventory = _standing_test_economics.inventory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the standing-test economics inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    args = parser.parse_args()

    payload = inventory(args.repo_root.resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(f"test files: {payload['test_file_count']}")
    print(f"nested CLI files: {payload['nested_cli_file_count']}")
    for finding in payload["findings"]:
        print(f"{finding['severity'].upper()} {finding['type']}: {finding['recommended_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
