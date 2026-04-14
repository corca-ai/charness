#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]

REPO_ROOT = _runtime_root()
sys.path[:0] = [str(Path(__file__).resolve().parent), str(REPO_ROOT)]

from adapter_validators import (
    runtime_budgets as _runtime_budgets,
)
from adapter_validators import (
    skill_ergonomics_gate_rules as _skill_ergonomics_gate_rules,
)

from scripts.adapter_lib import load_yaml_file
from scripts.quality_bootstrap_lib import ADAPTER_CANDIDATES
from scripts.quality_policy_defaults import (
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    validate_coverage_floor_policy,
    validate_prompt_asset_policy,
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
LIST_FIELDS = ("preset_lineage", "prompt_asset_roots", "concept_paths", "preflight_commands", "gate_commands", "security_commands")
ARTIFACT_FILENAME = "quality.md"

def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    errors.append(f"{field} must be a string")
    return None

def _string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    errors.append(f"{field} must be a list of strings")
    return None

def _float_value(value: Any, field: str, errors: list[str]) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        errors.append(f"{field} must be a number")
        return None
    result = float(value)
    if result >= 0:
        return result
    errors.append(f"{field} must be greater than or equal to 0")
    return None

def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "skill-outputs/quality",
        "preset_lineage": [],
        "coverage_fragile_margin_pp": 1.0,
        "coverage_floor_policy": dict(DEFAULT_COVERAGE_FLOOR_POLICY),
        "specdown_smoke_patterns": [],
        "spec_pytest_reference_format": DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
        "prompt_asset_roots": [],
        "prompt_asset_policy": dict(DEFAULT_PROMPT_ASSET_POLICY),
        "skill_ergonomics_gate_rules": list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
        "runtime_budgets": {},
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "security_commands": [],
    }

def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    version = data.get("version")
    if isinstance(version, int):
        validated["version"] = version
    elif version is not None:
        errors.append("version must be an integer")

    for field in STRING_FIELDS:
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    coverage_fragile_margin_pp = _float_value(data.get("coverage_fragile_margin_pp"), "coverage_fragile_margin_pp", errors)
    if coverage_fragile_margin_pp is not None:
        validated["coverage_fragile_margin_pp"] = coverage_fragile_margin_pp

    coverage_floor_policy = validate_coverage_floor_policy(data.get("coverage_floor_policy"), errors)
    if coverage_floor_policy is not None:
        validated["coverage_floor_policy"] = coverage_floor_policy
    specdown_smoke_patterns = _string_list(data.get("specdown_smoke_patterns"), "specdown_smoke_patterns", errors)
    if specdown_smoke_patterns is not None:
        validated["specdown_smoke_patterns"] = specdown_smoke_patterns
    spec_pytest_reference_format = _string(
        data.get("spec_pytest_reference_format"), "spec_pytest_reference_format", errors
    )
    if spec_pytest_reference_format is not None:
        validated["spec_pytest_reference_format"] = spec_pytest_reference_format
    prompt_asset_policy = validate_prompt_asset_policy(data.get("prompt_asset_policy"), errors)
    if prompt_asset_policy is not None:
        validated["prompt_asset_policy"] = prompt_asset_policy
    skill_ergonomics_gate_rules = _skill_ergonomics_gate_rules(
        data.get("skill_ergonomics_gate_rules"), errors
    )
    if skill_ergonomics_gate_rules is not None:
        validated["skill_ergonomics_gate_rules"] = skill_ergonomics_gate_rules
    runtime_budgets_value = _runtime_budgets(data.get("runtime_budgets"), errors)
    if runtime_budgets_value is not None:
        validated["runtime_budgets"] = runtime_budgets_value
    for field in LIST_FIELDS:
        items = _string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["gate_commands"]:
        warnings.append("No gate_commands configured; quality will rely on repo detection and proposals.")
    return validated, errors, warnings

def find_adapter(repo_root: Path) -> Path | None:
    return next((path for candidate in ADAPTER_CANDIDATES if (path := repo_root / candidate).is_file()), None)

def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        data = infer_repo_defaults(repo_root)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_path": str(Path(data["output_dir"]) / ARTIFACT_FILENAME),
            "errors": [],
            "warnings": [
                "No quality adapter found. Using default durable artifact location.",
                "Create .agents/quality-adapter.yaml to record gate commands and preset lineage.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "quality-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": str(Path(data["output_dir"]) / ARTIFACT_FILENAME),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    sys.stdout.write(json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
