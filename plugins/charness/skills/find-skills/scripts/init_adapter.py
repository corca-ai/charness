#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return base_adapter_items(
        repo_name,
        "skill-outputs/find-skills",
    ) + [
        ("trusted_skill_roots", []),
        ("prefer_local_first", True),
        ("allow_external_registry", False),
    ]


def main() -> None:
    written = run_init_adapter(
        default_output=Path(".agents/find-skills-adapter.yaml"),
        build_items=build_items,
    )
    print(written)


if __name__ == "__main__":
    main()
