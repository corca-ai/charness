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
