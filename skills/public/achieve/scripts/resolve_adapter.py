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
adapter_policy = SKILL_RUNTIME.load_local_skill_module(__file__, "achieve_adapter_policy")


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="achieve resolve_adapter")
    parser = argparse.ArgumentParser(description="Resolve the optional achieve adapter policy.")
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to load the achieve adapter from")
    try:
        args = parser.parse_args()
        payload = adapter_policy.load_adapter(args.repo_root.resolve())
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
