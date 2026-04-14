#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter
from scripts.quality_policy_defaults import (
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    default_specdown_smoke_patterns,
)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preset-id", default="portable-defaults")


def build_items(repo_name: str, args: argparse.Namespace) -> list[tuple[str, object]]:
    specdown_smoke_patterns = default_specdown_smoke_patterns([args.preset_id])
    return [
        *base_adapter_items(repo_name, "skill-outputs/quality", preset_id=args.preset_id),
        ("preset_lineage", [args.preset_id] if args.preset_id != "portable-defaults" else []),
        ("coverage_fragile_margin_pp", 1.0),
        ("coverage_floor_policy", DEFAULT_COVERAGE_FLOOR_POLICY),
        ("specdown_smoke_patterns", specdown_smoke_patterns),
        ("spec_pytest_reference_format", DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT),
        ("prompt_asset_roots", []),
        ("prompt_asset_policy", DEFAULT_PROMPT_ASSET_POLICY),
        ("skill_ergonomics_gate_rules", DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
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
