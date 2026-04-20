#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules.setdefault(spec.name, module)
            spec.loader.exec_module(module)
            return module
    raise ImportError("runtime_bootstrap.py not found")


arm_cli_timeout = _load_runtime_bootstrap().arm_cli_timeout


def _repo_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "quality_adapter_lib.py").is_file())


def load_adapter(repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(_repo_root()))
    from scripts.quality_adapter_lib import load_quality_adapter

    return load_quality_adapter(repo_root)


def main() -> None:
    cancel_timeout = arm_cli_timeout(label="quality resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    try:
        args = parser.parse_args()
        payload = load_adapter(args.repo_root.resolve())
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
