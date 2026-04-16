#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_adapter_init_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
base_adapter_items = _scripts_adapter_init_lib_module.base_adapter_items
run_init_adapter = _scripts_adapter_init_lib_module.run_init_adapter
_scripts_quality_policy_defaults_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_policy_defaults")
DEFAULT_COVERAGE_FLOOR_POLICY = _scripts_quality_policy_defaults_module.DEFAULT_COVERAGE_FLOOR_POLICY
DEFAULT_PROMPT_ASSET_POLICY = _scripts_quality_policy_defaults_module.DEFAULT_PROMPT_ASSET_POLICY
DEFAULT_SKILL_ERGONOMICS_GATE_RULES = _scripts_quality_policy_defaults_module.DEFAULT_SKILL_ERGONOMICS_GATE_RULES
DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = _scripts_quality_policy_defaults_module.DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT
default_specdown_smoke_patterns = _scripts_quality_policy_defaults_module.default_specdown_smoke_patterns


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preset-id", default="portable-defaults")


def build_items(repo_name: str, args: argparse.Namespace) -> list[tuple[str, object]]:
    specdown_smoke_patterns = default_specdown_smoke_patterns([args.preset_id])
    return [
        *base_adapter_items(repo_name, "charness-artifacts/quality", preset_id=args.preset_id),
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
