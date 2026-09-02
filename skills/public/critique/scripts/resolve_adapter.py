#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_critique_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.critique_adapter_lib"
)
_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
normalize_adapter_result = _adapter_lib.normalize_adapter_result


def load_adapter(repo_root: Path) -> dict[str, object]:
    return normalize_adapter_result(_critique_adapter_lib.load_adapter(repo_root), skill_id="critique")
# Command output is unconditionally YAML since the 2026-08-14 --json removal. This main
# hand-rolled its own `json.dump(..., sys.stdout)` instead of going through
# `skill_runtime_bootstrap.run_adapter_cli` like its sibling resolvers, so the repo-wide
# sweep of that driver did not reach it.
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the critique adapter")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root for resolving the critique adapter")
    args = parser.parse_args()
    payload = load_adapter(args.repo_root.resolve())
    emit_yaml(dict(sorted(payload.items())))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
