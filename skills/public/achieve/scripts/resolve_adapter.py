#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


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
