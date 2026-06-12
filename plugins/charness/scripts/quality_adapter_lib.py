from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, optional_string, optional_string_list
from scripts.artifact_naming_lib import ARTIFACT_CLASSES, RECORD_PATTERN
from scripts.quality_bootstrap_lib import ADAPTER_CANDIDATES
from scripts.quality_policy_defaults import (
    DEFAULT_CHANGED_LINE_MUTATION_GATE,
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_MUTATION_TESTING,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES,
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR,
    DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS,
    DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    DEFAULT_STANDING_DOC_PROVENANCE,
    validate_changed_line_mutation_gate,
    validate_coverage_floor_policy,
    validate_mutation_testing,
    validate_prompt_asset_policy,
    validate_skill_ergonomics_gate_rules,
    validate_standing_doc_provenance,
)

STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
    "recommendation_defaults_version",
    "runtime_profile_default",
)
LIST_FIELDS = (
    "preset_lineage",
    "prompt_asset_roots",
    "adapter_review_sources",
    "acknowledged_recommendations",
    "gate_design_review_globs",
    "product_surfaces",
    "skill_ergonomics_skill_paths",
    "skill_ergonomics_runtime_install_skill_paths",
    "vendored_paths",
    "cli_skill_surface_probe_commands",
    "cli_skill_surface_command_docs",
    "cli_skill_surface_skill_paths",
    "cli_skill_surface_change_globs",
    "canonical_markdown_surfaces",
    "public_spec_section_exemptions",
    "public_spec_pointer_proof_markers",
    "concept_paths",
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"


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


def _int_value(value: Any, field: str, errors: list[str]) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{field} must be an integer")
        return None
    if value < 0:
        errors.append(f"{field} must be greater than or equal to 0")
        return None
    return value


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
        "artifact_class": ARTIFACT_CLASS,
        "preset_lineage": [],
        "coverage_fragile_margin_pp": 1.0,
        "coverage_floor_policy": dict(DEFAULT_COVERAGE_FLOOR_POLICY),
        "specdown_smoke_patterns": [],
        "spec_pytest_reference_format": DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
        "public_spec_section_exemptions": list(DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS),
        "public_spec_implementation_ref_density_floor": DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR,
        "public_spec_implementation_guard_min_lines": DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES,
        "public_spec_pointer_proof_markers": list(DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS),
        "prompt_asset_roots": [],
        "adapter_review_sources": [],
        "domain_language_contract": {},
        "acknowledged_recommendations": [],
        "gate_design_review_globs": [],
        "product_surfaces": [],
        "skill_ergonomics_skill_paths": [],
        "skill_ergonomics_runtime_install_skill_paths": [],
        "vendored_paths": [],
        "cli_skill_surface_probe_commands": [],
        "cli_skill_surface_command_docs": [],
        "cli_skill_surface_skill_paths": [],
        "cli_skill_surface_change_globs": [],
        "canonical_markdown_surfaces": ["AGENTS.md", "CLAUDE.md"],
        "prompt_asset_policy": dict(DEFAULT_PROMPT_ASSET_POLICY),
        "skill_ergonomics_gate_rules": list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
        "runtime_profile_default": "default",
        "runtime_budgets": {},
        "runtime_budget_profiles": {},
        "startup_probes": [],
        "quality_phases": [],
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "review_commands": [],
        "security_commands": [],
        "mutation_testing": copy.deepcopy(DEFAULT_MUTATION_TESTING),
        "standing_doc_provenance": copy.deepcopy(DEFAULT_STANDING_DOC_PROVENANCE),
        "changed_line_mutation_gate": copy.deepcopy(DEFAULT_CHANGED_LINE_MUTATION_GATE),
    }


def _validate_version_field(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    version = data.get("version")
    if isinstance(version, int):
        validated["version"] = version
    elif version is not None:
        errors.append("version must be an integer")


def _apply_string_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
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

    specdown_smoke_patterns = optional_string_list(
        data.get("specdown_smoke_patterns"), "specdown_smoke_patterns", errors
    )
    if specdown_smoke_patterns is not None:
        validated["specdown_smoke_patterns"] = specdown_smoke_patterns

    spec_pytest_reference_format = optional_string(
        data.get("spec_pytest_reference_format"), "spec_pytest_reference_format", errors
    )
    if spec_pytest_reference_format is not None:
        validated["spec_pytest_reference_format"] = spec_pytest_reference_format

    public_spec_implementation_ref_density_floor = _float_value(
        data.get("public_spec_implementation_ref_density_floor"),
        "public_spec_implementation_ref_density_floor",
        errors,
    )
    if public_spec_implementation_ref_density_floor is not None:
        validated["public_spec_implementation_ref_density_floor"] = public_spec_implementation_ref_density_floor

    public_spec_implementation_guard_min_lines = _int_value(
        data.get("public_spec_implementation_guard_min_lines"),
        "public_spec_implementation_guard_min_lines",
        errors,
    )
    if public_spec_implementation_guard_min_lines is not None:
        validated["public_spec_implementation_guard_min_lines"] = public_spec_implementation_guard_min_lines

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
    runtime_budget_profiles = adapter_validators.runtime_budget_profiles(
        data.get("runtime_budget_profiles"), errors
    )
    if runtime_budget_profiles is not None:
        validated["runtime_budget_profiles"] = runtime_budget_profiles
    startup_probes = adapter_validators.startup_probes(data.get("startup_probes"), errors)
    if startup_probes is not None:
        validated["startup_probes"] = startup_probes
    quality_phases = adapter_validators.quality_phases(data.get("quality_phases"), errors)
    if quality_phases is not None:
        validated["quality_phases"] = quality_phases

    domain_language_contract = data.get("domain_language_contract")
    if domain_language_contract is None:
        return
    if not isinstance(domain_language_contract, dict):
        errors.append("domain_language_contract must be a mapping")
        return
    validated["domain_language_contract"] = dict(domain_language_contract)


def _apply_list_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in LIST_FIELDS:
        items = optional_string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items


def _apply_mutation_testing(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_mutation_testing(data.get("mutation_testing"), errors, warnings)
    if block is not None:
        validated["mutation_testing"] = block


def _apply_standing_doc_provenance(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_standing_doc_provenance(data.get("standing_doc_provenance"), errors, warnings)
    if block is not None:
        validated["standing_doc_provenance"] = block


def _apply_changed_line_mutation_gate(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_changed_line_mutation_gate(data.get("changed_line_mutation_gate"), errors, warnings)
    if block is not None:
        validated["changed_line_mutation_gate"] = block


def validate_quality_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_quality_defaults(repo_root)
    _validate_version_field(data, validated, errors)
    _apply_string_fields(data, validated, errors)
    configured_artifact_class = data.get("artifact_class")
    if configured_artifact_class is None:
        validated["artifact_class"] = ARTIFACT_CLASS
    elif isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
        validated["artifact_class"] = configured_artifact_class
    else:
        errors.append("artifact_class must be one of: current, history, rolling")
    _apply_policy_fields(data, validated, errors)
    _apply_list_fields(data, validated, errors)
    _apply_mutation_testing(data, validated, errors, warnings)
    _apply_standing_doc_provenance(data, validated, errors, warnings)
    _apply_changed_line_mutation_gate(data, validated, errors, warnings)

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
            "artifact_class": data["artifact_class"],
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
        "artifact_class": data["artifact_class"],
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def load_quality_adapter_strict(repo_root: Path) -> dict[str, Any]:
    """Load the quality adapter for validators and gates.

    Strict callers should fail when the returned payload has `valid: false`.
    Keeping the helper separate from advisory inventory call sites makes that
    intent explicit without changing the base payload shape.
    """
    payload = load_quality_adapter(repo_root)
    payload["load_mode"] = "strict"
    return payload


def load_quality_adapter_permissive(repo_root: Path) -> dict[str, Any]:
    """Load the quality adapter for advisory inventories.

    Advisory inventories may still produce useful partial evidence from
    validated defaults and other readable fields when one adapter field is
    invalid. They must surface this degraded state instead of silently treating
    it as a clean inventory.
    """
    payload = load_quality_adapter(repo_root)
    payload["load_mode"] = "permissive"
    if payload.get("valid") is not True:
        warnings = list(payload.get("warnings", []))
        warnings.append(
            "Quality adapter is invalid; advisory inventory is using validated defaults "
            "and readable fields. Treat findings as best-effort until adapter errors are repaired."
        )
        payload["warnings"] = warnings
    return payload
