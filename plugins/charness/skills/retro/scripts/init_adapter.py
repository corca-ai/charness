#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return [
        *base_adapter_items(repo_name, "skill-outputs/retro"),
        ("default_mode", "session"),
        ("weekly_window_days", 7),
        ("evidence_paths", []),
        ("metrics_commands", []),
    ]


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/retro-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
