#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preset-id", default="portable-defaults")


def build_items(repo_name: str, args: argparse.Namespace) -> list[tuple[str, object]]:
    return [
        *base_adapter_items(repo_name, "skill-outputs/quality", preset_id=args.preset_id),
        ("concept_paths", []),
        ("preflight_commands", []),
        ("gate_commands", []),
        ("security_commands", []),
    ]


def main() -> None:
    output = run_init_adapter(
        default_output=Path(".agents/quality-adapter.yaml"),
        build_items=build_items,
        add_arguments=add_arguments,
    )
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
