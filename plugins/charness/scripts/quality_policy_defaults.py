from __future__ import annotations

from typing import Any

DEFAULT_COVERAGE_FRAGILE_MARGIN_PP = 1.0
DEFAULT_SPECDOWN_SMOKE_PATTERNS = [
    r"\bgrep\s+-q\b",
    r"\[pycheck\]",
    r"\b(?:uv\s+run\s+)?python\s+-m\s+pytest\b",
    r"\bpytest\b.*\s-k\s+",
]
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
DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
DEFAULT_PROMPT_ASSET_POLICY = {
    "source_globs": [],
    "min_multiline_chars": 400,
    "exemption_globs": [],
}
DEFAULT_SKILL_ERGONOMICS_GATE_RULES: list[str] = []
VALID_SKILL_ERGONOMICS_GATE_RULES = frozenset({
    "mode_option_pressure_terms",
    "progressive_disclosure_risk",
})


def default_specdown_smoke_patterns(preset_lineage: list[str]) -> list[str]:
    return list(DEFAULT_SPECDOWN_SMOKE_PATTERNS) if "specdown-quality" in preset_lineage else []


def merge_coverage_floor_policy(value: Any) -> dict[str, Any]:
    merged_policy = dict(DEFAULT_COVERAGE_FLOOR_POLICY)
    if not isinstance(value, dict):
        return merged_policy
    for key, default_value in DEFAULT_COVERAGE_FLOOR_POLICY.items():
        item = value.get(key)
        if isinstance(default_value, str) and isinstance(item, str):
            merged_policy[key] = item
        elif isinstance(default_value, float) and isinstance(item, (int, float)):
            merged_policy[key] = float(item)
        elif isinstance(default_value, int) and isinstance(item, int):
            merged_policy[key] = item
    return merged_policy


def merge_prompt_asset_policy(value: Any) -> dict[str, Any]:
    merged_policy = dict(DEFAULT_PROMPT_ASSET_POLICY)
    if not isinstance(value, dict):
        return merged_policy
    for field in ("source_globs", "exemption_globs"):
        item = value.get(field)
        if isinstance(item, list) and all(isinstance(entry, str) for entry in item):
            merged_policy[field] = list(item)
    min_chars = value.get("min_multiline_chars")
    if isinstance(min_chars, int):
        merged_policy["min_multiline_chars"] = min_chars
    return merged_policy


def validate_coverage_floor_policy(value: Any, errors: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("coverage_floor_policy must be a mapping")
        return None
    validated = merge_coverage_floor_policy(value)
    for field in ("exemption_list_path", "gate_script_pattern", "lefthook_path", "ci_workflow_glob"):
        item = value.get(field)
        if item is not None and not isinstance(item, str):
            errors.append(f"coverage_floor_policy.{field} must be a string")
    min_statements = value.get("min_statements_threshold")
    if min_statements is not None and not isinstance(min_statements, int):
        errors.append("coverage_floor_policy.min_statements_threshold must be an integer")
    for field in ("fail_below_pct", "warn_ceiling_pct", "floor_drift_lock_pp"):
        item = value.get(field)
        if item is not None and not isinstance(item, (int, float)):
            errors.append(f"coverage_floor_policy.{field} must be a number")
    if validated["min_statements_threshold"] < 0:
        errors.append("coverage_floor_policy.min_statements_threshold must be greater than or equal to 0")
    if validated["fail_below_pct"] < 0:
        errors.append("coverage_floor_policy.fail_below_pct must be greater than or equal to 0")
    if validated["warn_ceiling_pct"] < validated["fail_below_pct"]:
        errors.append("coverage_floor_policy.warn_ceiling_pct must be greater than or equal to fail_below_pct")
    if validated["floor_drift_lock_pp"] < 0:
        errors.append("coverage_floor_policy.floor_drift_lock_pp must be greater than or equal to 0")
    return validated


def validate_prompt_asset_policy(value: Any, errors: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("prompt_asset_policy must be a mapping")
        return None
    validated = merge_prompt_asset_policy(value)
    for field in ("source_globs", "exemption_globs"):
        item = value.get(field)
        if item is not None and not (isinstance(item, list) and all(isinstance(entry, str) for entry in item)):
            errors.append(f"prompt_asset_policy.{field} must be a list of strings")
    min_chars = value.get("min_multiline_chars")
    if min_chars is not None and not isinstance(min_chars, int):
        errors.append("prompt_asset_policy.min_multiline_chars must be an integer")
    if validated["min_multiline_chars"] < 0:
        errors.append("prompt_asset_policy.min_multiline_chars must be greater than or equal to 0")
    return validated


def validate_skill_ergonomics_gate_rules(value: Any, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("skill_ergonomics_gate_rules must be a list")
        return None
    validated: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            errors.append("skill_ergonomics_gate_rules entries must be non-empty strings")
            continue
        if item not in VALID_SKILL_ERGONOMICS_GATE_RULES:
            rendered = ", ".join(sorted(VALID_SKILL_ERGONOMICS_GATE_RULES))
            errors.append(
                f"skill_ergonomics_gate_rules contains unknown rule `{item}`; valid rules: {rendered}"
            )
            continue
        if item not in validated:
            validated.append(item)
    return validated
