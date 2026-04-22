from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file
from scripts.artifact_naming_lib import RECORD_PATTERN
from scripts.quality_bootstrap_lib import ADAPTER_CANDIDATES
from scripts.quality_policy_defaults import (
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    validate_coverage_floor_policy,
    validate_prompt_asset_policy,
    validate_skill_ergonomics_gate_rules,
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
LIST_FIELDS = (
    "preset_lineage",
    "prompt_asset_roots",
    "concept_paths",
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)
ARTIFACT_FILENAME = "latest.md"


def _load_adapter_validators():
    repo_root = Path(__file__).resolve().parents[1]
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts",
        repo_root / "skills" / "quality" / "scripts",
    )
    for candidate in candidates:
        if not (candidate / "adapter_validators.py").is_file():
            continue
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        import adapter_validators

        return adapter_validators
    raise FileNotFoundError("quality adapter_validators.py not found")


adapter_validators = _load_adapter_validators()


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


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def infer_quality_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/quality",
        "preset_lineage": [],
        "coverage_fragile_margin_pp": 1.0,
        "coverage_floor_policy": dict(DEFAULT_COVERAGE_FLOOR_POLICY),
        "specdown_smoke_patterns": [],
        "spec_pytest_reference_format": DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
        "prompt_asset_roots": [],
        "prompt_asset_policy": dict(DEFAULT_PROMPT_ASSET_POLICY),
        "skill_ergonomics_gate_rules": list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
        "runtime_budgets": {},
        "startup_probes": [],
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "review_commands": [],
        "security_commands": [],
    }


def _validate_version_field(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    version = data.get("version")
    if isinstance(version, int):
        validated["version"] = version
    elif version is not None:
        errors.append("version must be an integer")


def _apply_string_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in STRING_FIELDS:
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value


def _apply_policy_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    coverage_fragile_margin_pp = _float_value(
        data.get("coverage_fragile_margin_pp"), "coverage_fragile_margin_pp", errors
    )
    if coverage_fragile_margin_pp is not None:
        validated["coverage_fragile_margin_pp"] = coverage_fragile_margin_pp

    coverage_floor_policy = validate_coverage_floor_policy(data.get("coverage_floor_policy"), errors)
    if coverage_floor_policy is not None:
        validated["coverage_floor_policy"] = coverage_floor_policy

    specdown_smoke_patterns = _string_list(
        data.get("specdown_smoke_patterns"), "specdown_smoke_patterns", errors
    )
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

    skill_ergonomics_gate_rules = validate_skill_ergonomics_gate_rules(
        data.get("skill_ergonomics_gate_rules"), errors
    )
    if skill_ergonomics_gate_rules is not None:
        validated["skill_ergonomics_gate_rules"] = skill_ergonomics_gate_rules

    runtime_budgets = adapter_validators.runtime_budgets(data.get("runtime_budgets"), errors)
    if runtime_budgets is not None:
        validated["runtime_budgets"] = runtime_budgets
    startup_probes = adapter_validators.startup_probes(data.get("startup_probes"), errors)
    if startup_probes is not None:
        validated["startup_probes"] = startup_probes


def _apply_list_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in LIST_FIELDS:
        items = _string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items


def validate_quality_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_quality_defaults(repo_root)
    _validate_version_field(data, validated, errors)
    _apply_string_fields(data, validated, errors)
    _apply_policy_fields(data, validated, errors)
    _apply_list_fields(data, validated, errors)

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["gate_commands"]:
        warnings.append("No gate_commands configured; quality will rely on repo detection and proposals.")
    return validated, errors, warnings


def load_quality_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        data = infer_quality_defaults(repo_root)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
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
    data, errors, extra_warnings = validate_quality_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
