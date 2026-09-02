#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_adapter_init = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapters.adapter_init_lib")
run_init_adapter = _adapter_init.run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return [
        ("version", 1),
        ("repo", repo_name),
        ("language", "en"),
        ("artifact_dir", "charness-artifacts/goals"),
        (
            "interview",
            {
                "max_questions": 15,
                "allow_provisional_local_fallback": False,
            },
        ),
    ]


def main() -> None:
    run_init_adapter(default_output=Path(".agents/achieve-adapter.yaml"), build_items=build_items)


if __name__ == "__main__":
    main()
