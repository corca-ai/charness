#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    items = base_adapter_items(repo_name, "charness-artifacts/impl")
    items.extend(
        [
            ("verification_tools", []),
            ("ui_verification_tools", []),
            ("verification_install_proposals", []),
            ("truth_surfaces", []),
        ]
    )
    return items


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/impl-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
