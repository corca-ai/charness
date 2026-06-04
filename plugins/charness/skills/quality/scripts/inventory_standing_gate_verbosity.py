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
_standing_gate_verbosity_lib_module = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_gate_verbosity_lib")
inventory = _standing_gate_verbosity_lib_module.inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the standing-gate verbosity inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
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
