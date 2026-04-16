#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_standing_gate_verbosity_lib_module = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_gate_verbosity_lib")
inventory = _standing_gate_verbosity_lib_module.inventory


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
