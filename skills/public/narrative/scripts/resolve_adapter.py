#!/usr/bin/env python3
from __future__ import annotations

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
_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
normalize_adapter_result = _adapter_lib.normalize_adapter_result


def _repo_root() -> Path:
    return next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "scripts" / "adapters" / "narrative_adapter_lib.py").is_file()
    )


def load_adapter(repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(_repo_root()))
    from scripts.adapters.narrative_adapter_lib import load_narrative_adapter

    return normalize_adapter_result(load_narrative_adapter(repo_root), skill_id="narrative")


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="narrative resolve_adapter", repo_root_help="Repo root for resolving the narrative adapter")


if __name__ == "__main__":
    main()
