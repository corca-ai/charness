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


def _repo_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "narrative_adapter_lib.py").is_file())


def review_adapter(repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(_repo_root()))
    from scripts.narrative_adapter_lib import review_narrative_adapter

    return review_narrative_adapter(repo_root)


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(review_adapter, label="narrative review_adapter", repo_root_help="Repo root to review the narrative adapter against")


if __name__ == "__main__":
    main()
