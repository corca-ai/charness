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
DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS = [
    "Fixed Decisions",
    "HTTP API contract",
    "Server backend stack",
    "Deferred Decisions",
    "Non-Goals",
]
DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR = 0.02
DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES = 100
DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS = [
    "proof: pointer",
    "proof: pointer-spec",
    "executable_proof: pointer",
    "public_spec_proof: pointer",
]
DEFAULT_PROMPT_ASSET_POLICY = {
    "source_globs": [],
    "min_multiline_chars": 400,
    "exemption_globs": [],
}
DEFAULT_SKILL_ERGONOMICS_GATE_RULES: list[str] = [
    "code_fence_without_helper_script",
    "long_core",
    "mode_option_pressure_terms",
    "portable_helper_path_ambiguity",
    "progressive_disclosure_risk",
]
VALID_SKILL_ERGONOMICS_GATE_RULES = frozenset(DEFAULT_SKILL_ERGONOMICS_GATE_RULES)

# DEFAULT_MUTATION_TESTING is stack-neutral. Policy values trace to
# craken-agents/.github/workflows/mutation-tests.yml (2026-05-14). Stryker-
# specific commands and tool wiring live in consumer adapters, not here.
DEFAULT_MUTATION_TESTING: dict[str, Any] = {
    "commands": {
        "dry_run": "",
        "full": "",
        "sample": "",
        "summary": "",
    },
    "score_break": 60,
    "schedule_cron": "17 */3 * * *",
    "changed_quota": 5,
    "max_files": 10,
    "auto_issue": {
        "enabled": False,
        "label": "mutation-test",
        "title": "Mutation test regression on main",
        "marker_token": "mutation-test-regression",
    },
    "workflow_path": ".github/workflows/mutation-tests.yml",
    "report_paths": {
        "summary_md": "reports/mutation/summary.md",
        "sample_md": "reports/mutation/sample.md",
        "log": "reports/mutation/run.log",
    },
    "declined": False,
}
MUTATION_TESTING_KNOWN_KEYS = frozenset(DEFAULT_MUTATION_TESTING.keys())
MUTATION_TESTING_COMMAND_SLOTS = frozenset(DEFAULT_MUTATION_TESTING["commands"].keys())
MUTATION_TESTING_AUTO_ISSUE_KEYS = frozenset(DEFAULT_MUTATION_TESTING["auto_issue"].keys())
MUTATION_TESTING_REPORT_PATH_KEYS = frozenset(DEFAULT_MUTATION_TESTING["report_paths"].keys())


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


def _validate_mutation_commands(
    raw: Any, validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    if raw is None:
        return
    if not isinstance(raw, dict):
        errors.append("mutation_testing.commands must be a mapping")
        return
    merged = dict(DEFAULT_MUTATION_TESTING["commands"])
    for key, value in raw.items():
        if key not in MUTATION_TESTING_COMMAND_SLOTS:
            warnings.append(f"unknown mutation_testing.commands sub-key: {key}")
            continue
        if not isinstance(value, str):
            errors.append(f"mutation_testing.commands.{key} must be a string")
            continue
        merged[key] = value
    validated["commands"] = merged


def _validate_mutation_auto_issue(
    raw: Any, validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    if raw is None:
        return
    if not isinstance(raw, dict):
        errors.append("mutation_testing.auto_issue must be a mapping")
        return
    merged = dict(DEFAULT_MUTATION_TESTING["auto_issue"])
    for key, value in raw.items():
        if key not in MUTATION_TESTING_AUTO_ISSUE_KEYS:
            warnings.append(f"unknown mutation_testing.auto_issue sub-key: {key}")
            continue
        if key == "enabled":
            if not isinstance(value, bool):
                errors.append("mutation_testing.auto_issue.enabled must be a boolean")
                continue
            merged[key] = value
        else:
            if not isinstance(value, str):
                errors.append(f"mutation_testing.auto_issue.{key} must be a string")
                continue
            merged[key] = value
    validated["auto_issue"] = merged


def _validate_mutation_report_paths(
    raw: Any, validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    if raw is None:
        return
    if not isinstance(raw, dict):
        errors.append("mutation_testing.report_paths must be a mapping")
        return
    merged = dict(DEFAULT_MUTATION_TESTING["report_paths"])
    for key, value in raw.items():
        if key not in MUTATION_TESTING_REPORT_PATH_KEYS:
            warnings.append(f"unknown mutation_testing.report_paths sub-key: {key}")
            continue
        if not isinstance(value, str):
            errors.append(f"mutation_testing.report_paths.{key} must be a string")
            continue
        merged[key] = value
    validated["report_paths"] = merged


def _validate_mutation_score_break(raw: Any, validated: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(raw, int) or isinstance(raw, bool):
        errors.append("mutation_testing.score_break must be an integer")
        return
    if raw < 0 or raw > 100:
        errors.append("mutation_testing.score_break must be between 0 and 100")
        return
    validated["score_break"] = raw


def _validate_mutation_int_field(
    name: str, raw: Any, validated: dict[str, Any], errors: list[str]
) -> None:
    if not isinstance(raw, int) or isinstance(raw, bool):
        errors.append(f"mutation_testing.{name} must be an integer")
        return
    if raw < 0:
        errors.append(f"mutation_testing.{name} must be greater than or equal to 0")
        return
    validated[name] = raw


def _validate_mutation_string_field(
    name: str, raw: Any, validated: dict[str, Any], errors: list[str]
) -> None:
    if not isinstance(raw, str):
        errors.append(f"mutation_testing.{name} must be a string")
        return
    validated[name] = raw


def _validate_mutation_declined(raw: Any, validated: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(raw, bool):
        errors.append("mutation_testing.declined must be a boolean")
        return
    validated["declined"] = raw


def _mutation_validated_defaults() -> dict[str, Any]:
    return {
        "commands": dict(DEFAULT_MUTATION_TESTING["commands"]),
        "score_break": DEFAULT_MUTATION_TESTING["score_break"],
        "schedule_cron": DEFAULT_MUTATION_TESTING["schedule_cron"],
        "changed_quota": DEFAULT_MUTATION_TESTING["changed_quota"],
        "max_files": DEFAULT_MUTATION_TESTING["max_files"],
        "auto_issue": dict(DEFAULT_MUTATION_TESTING["auto_issue"]),
        "workflow_path": DEFAULT_MUTATION_TESTING["workflow_path"],
        "report_paths": dict(DEFAULT_MUTATION_TESTING["report_paths"]),
        "declined": DEFAULT_MUTATION_TESTING["declined"],
    }


def _apply_mutation_top_key(
    key: str,
    raw: Any,
    validated: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    if key == "commands":
        _validate_mutation_commands(raw, validated, errors, warnings)
    elif key == "auto_issue":
        _validate_mutation_auto_issue(raw, validated, errors, warnings)
    elif key == "report_paths":
        _validate_mutation_report_paths(raw, validated, errors, warnings)
    elif key == "score_break":
        _validate_mutation_score_break(raw, validated, errors)
    elif key in {"changed_quota", "max_files"}:
        _validate_mutation_int_field(key, raw, validated, errors)
    elif key in {"schedule_cron", "workflow_path"}:
        _validate_mutation_string_field(key, raw, validated, errors)
    elif key == "declined":
        _validate_mutation_declined(raw, validated, errors)


def validate_mutation_testing(
    value: Any, errors: list[str], warnings: list[str]
) -> dict[str, Any] | None:
    """Validate the mutation_testing adapter block.

    Returns None when absent; defaults are supplied by infer_quality_defaults.
    Unknown top-level or nested sub-keys land in warnings (precedent: silent-
    ignore in coverage_floor_policy, etc., here surfaced as a warning so typo
    drift is visible).
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("mutation_testing must be a mapping")
        return None
    validated = _mutation_validated_defaults()
    for key, raw in value.items():
        if key not in MUTATION_TESTING_KNOWN_KEYS:
            warnings.append(f"unknown mutation_testing sub-key: {key}")
            continue
        _apply_mutation_top_key(key, raw, validated, errors, warnings)
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
