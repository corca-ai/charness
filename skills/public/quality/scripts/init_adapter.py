#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.adapter_init_lib import base_adapter_items, run_init_adapter

DEFAULT_COVERAGE_FLOOR_POLICY = {
    "min_statements_threshold": 30,
    "fail_below_pct": 80.0,
    "warn_ceiling_pct": 95.0,
    "floor_drift_lock_pp": 1.0,
    "exemption_list_path": "scripts/coverage-floor-exemptions.txt",
    "gate_script_pattern": "*-quality-gate.sh",
    "lefthook_path": "lefthook.yml",
    "ci_workflow_glob": ".github/workflows/*.yml",
}
DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = (
    r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preset-id", default="portable-defaults")


def build_items(repo_name: str, args: argparse.Namespace) -> list[tuple[str, object]]:
    specdown_smoke_patterns = []
    if args.preset_id == "specdown-quality":
        specdown_smoke_patterns = [
            r"\bgrep\s+-q\b",
            r"\[pycheck\]",
            r"\b(?:uv\s+run\s+)?python\s+-m\s+pytest\b",
            r"\bpytest\b.*\s-k\s+",
        ]
    return [
        *base_adapter_items(repo_name, "skill-outputs/quality", preset_id=args.preset_id),
        ("preset_lineage", [args.preset_id] if args.preset_id != "portable-defaults" else []),
        ("coverage_fragile_margin_pp", 1.0),
        ("coverage_floor_policy", DEFAULT_COVERAGE_FLOOR_POLICY),
        ("specdown_smoke_patterns", specdown_smoke_patterns),
        ("spec_pytest_reference_format", DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT),
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
