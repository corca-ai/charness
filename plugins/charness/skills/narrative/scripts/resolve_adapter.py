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


arm_cli_timeout = _load_skill_runtime_bootstrap().arm_cli_timeout


def _repo_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "narrative_adapter_lib.py").is_file())


def load_adapter(repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(_repo_root()))
    from scripts.narrative_adapter_lib import load_narrative_adapter

    return load_narrative_adapter(repo_root)


def main() -> None:
    cancel_timeout = arm_cli_timeout(label="narrative resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for resolving the narrative adapter")
    try:
        args = parser.parse_args()
        payload = load_adapter(args.repo_root.resolve())
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
