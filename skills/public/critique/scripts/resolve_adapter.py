#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
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
_critique_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.critique_adapter_lib"
)
load_adapter = _critique_adapter_lib.load_adapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the critique adapter")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root for resolving the critique adapter")
    args = parser.parse_args()
    payload = load_adapter(args.repo_root.resolve())
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
