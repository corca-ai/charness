"""Field validators shared by the quality adapter resolver.

Keeps resolve_adapter.py inside the SKILL_HELPER_FILE_MAX line budget while
new adapter fields accrete over time. Each validator returns the parsed value
or None, appending human-readable errors to the shared list.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from scripts.adapter_lib import (
    declared_fields_after_version_check,
    optional_string,
    optional_string_list,
)
from scripts.quality_policy_defaults import validate_skill_ergonomics_gate_rules
from scripts.quality_universes_lib import validate_universes as _validate_universes

_RESOLVER_DIR = Path(__file__).resolve().parent
if str(_RESOLVER_DIR) not in sys.path:
    sys.path.insert(0, str(_RESOLVER_DIR))
from runtime_budget_intent import runtime_budget_intent  # noqa: E402

RUNTIME_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
DEFAULT_STARTUP_PROBE_TIMEOUT_SECONDS = 20
Data = dict[str, Any]
Messages = list[str]
BudgetProfiles = dict[str, dict[str, dict[str, int]]]

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
    "nose_inventory_paths",
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


def validate_version_field(data: Data, validated: Data, errors: Messages) -> Data:
    """Returns the declared fields the caller's remaining passes may honor: empty on a
    refused version. The caller must rebind `data` to it -- a discarded return here is
    the pre-repair behavior, not a stylistic choice."""
    return declared_fields_after_version_check(data, validated, errors)


def apply_string_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value


def apply_runtime_fields(data: Data, validated: Data, errors: Messages) -> None:
    for field, validator in (
        ("runtime_budgets", runtime_budgets),
        ("runtime_budget_profiles", runtime_budget_profiles),
        ("runtime_budget_intent", runtime_budget_intent),
        ("runtime_budget_universe", runtime_budget_universe),
        ("startup_probes", startup_probes),
        ("command_timing_log", command_timing_log),
        ("quality_phases", quality_phases),
    ):
        value = validator(data.get(field), errors)
        if value is not None:
            validated[field] = value


def apply_list_fields(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    for field in LIST_FIELDS:
        items = optional_string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items


def validate_universes(value: Any, errors: list[str]) -> dict[str, Any] | None:
    return _validate_universes(value, errors)


def runtime_budgets(value: Any, errors: list[str]) -> dict[str, int] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("runtime_budgets must be a mapping")
        return None
    validated: dict[str, int] = {}
    for label, raw in value.items():
        if not isinstance(label, str) or not label:
            errors.append("runtime_budgets keys must be non-empty strings")
        elif isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
            errors.append(f"runtime_budgets.{label} must be a positive integer (milliseconds)")
        else:
            validated[label] = raw
    return validated


def runtime_budget_universe(value: Any, errors: list[str]) -> dict[str, Any] | None:
    """Validate the shape of the optional consumer-owned label lister."""
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("runtime_budget_universe must be a mapping")
        return None
    command = value.get("command", "")
    if not isinstance(command, str):
        errors.append("runtime_budget_universe.command must be a string")
    return {"command": command}


def _runtime_profile_id(value: Any, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string")
        return None
    if not RUNTIME_PROFILE_ID_RE.fullmatch(value):
        errors.append(f"{field} may only contain letters, numbers, dots, underscores, and hyphens")
        return None
    return value


def runtime_budget_profiles(value: Any, errors: Messages) -> BudgetProfiles | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("runtime_budget_profiles must be a mapping")
        return None
    validated: dict[str, dict[str, dict[str, int]]] = {}
    for profile_id, raw_profile in value.items():
        valid_profile_id = _runtime_profile_id(
            profile_id, "runtime_budget_profiles profile id", errors
        )
        if valid_profile_id is None:
            continue
        if not isinstance(raw_profile, dict):
            errors.append(f"runtime_budget_profiles.{profile_id} must be a mapping")
            continue
        budgets = runtime_budgets(raw_profile.get("budgets"), errors)
        if budgets is None:
            errors.append(f"runtime_budget_profiles.{profile_id}.budgets must be a mapping")
            continue
        validated[valid_profile_id] = {"budgets": budgets}
    return validated


def startup_probes(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("startup_probes must be a list")
        return None
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        prefix = f"startup_probes[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        label = raw.get("label")
        if not isinstance(label, str) or not label:
            errors.append(f"{prefix}.label must be a non-empty string")
        command = raw.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            errors.append(f"{prefix}.command must be a non-empty list of strings")
        probe_class = raw.get("class")
        if probe_class not in {"standing", "release"}:
            errors.append(f"{prefix}.class must be standing or release")
        startup_mode = raw.get("startup_mode")
        if startup_mode not in {"warm", "cold", "first-launch"}:
            errors.append(f"{prefix}.startup_mode must be warm, cold, or first-launch")
        surface = raw.get("surface")
        if not isinstance(surface, str) or not surface:
            errors.append(f"{prefix}.surface must be a non-empty string")
        samples = raw.get("samples", 1)
        if isinstance(samples, bool) or not isinstance(samples, int) or samples <= 0:
            errors.append(f"{prefix}.samples must be a positive integer")
        timeout_seconds = raw.get("timeout_seconds", DEFAULT_STARTUP_PROBE_TIMEOUT_SECONDS)
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, int | float)
            or timeout_seconds <= 0
        ):
            errors.append(f"{prefix}.timeout_seconds must be a positive number")
        if errors and any(message.startswith(prefix) for message in errors):
            continue
        validated.append(
            {
                "label": label,
                "command": list(command),
                "class": probe_class,
                "startup_mode": startup_mode,
                "surface": surface,
                "samples": samples,
                "timeout_seconds": timeout_seconds,
            }
        )
    return validated


def command_timing_log(value: Any, errors: list[str]) -> dict[str, Any] | None:
    """Pass-through structural check for the runtime command-timing-log source.

    Only the top-level shape is validated here so a gross type error
    (a non-mapping) marks the adapter invalid. The detailed field/schema
    validation (path, field_map, elapsed_unit, recent_window) is owned by the
    consumer `runtime_timing_log_lib`, which surfaces config errors through
    `profile_config_errors` so `check_runtime_budget` fails loud at the runtime
    gate rather than invalidating the whole adapter for a runtime-only field.
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("command_timing_log must be a mapping")
        return None
    return dict(value)


TEST_FILE_DISCOVERY_KNOWN_KEYS = {"command", "patterns", "patterns_mode"}
TEST_FILE_DISCOVERY_MODES = {"extend", "replace"}


def test_file_discovery(value: Any, errors: Messages, warnings: Messages) -> Data | None:
    """Validate the adapter-owned test-file discovery block."""
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("test_file_discovery must be a mapping")
        return None
    command = value.get("command", "")
    if not isinstance(command, str):
        errors.append("test_file_discovery.command must be a string")
        command = ""
    patterns = value.get("patterns", [])
    if not isinstance(patterns, list) or not all(
        isinstance(item, str) and item for item in patterns
    ):
        errors.append("test_file_discovery.patterns must be a list of non-empty strings")
        patterns = []
    patterns_mode = value.get("patterns_mode", "extend")
    if patterns_mode not in TEST_FILE_DISCOVERY_MODES:
        errors.append("test_file_discovery.patterns_mode must be extend or replace")
        patterns_mode = "extend"
    for key in value:
        if key not in TEST_FILE_DISCOVERY_KNOWN_KEYS:
            warnings.append(f"test_file_discovery.{key} is not a recognized key")
    return {"command": command, "patterns": list(patterns), "patterns_mode": patterns_mode}


LINT_IGNORE_DISCOVERY_KNOWN_KEYS = {"directives"}
LINT_IGNORE_DIRECTIVE_KNOWN_KEYS = {"tool", "suffixes", "pattern", "scope"}
LINT_IGNORE_DIRECTIVE_SCOPES = {"inline", "file", "leading"}


def lint_ignore_discovery(value: Any, errors: Messages, warnings: Messages) -> Data | None:
    """Validate adapter-declared lint-suppression directive matchers."""
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("lint_ignore_discovery must be a mapping")
        return None
    for key in value:
        if key not in LINT_IGNORE_DISCOVERY_KNOWN_KEYS:
            warnings.append(f"lint_ignore_discovery.{key} is not a recognized key")
    raw_directives = value.get("directives", [])
    if not isinstance(raw_directives, list):
        errors.append("lint_ignore_discovery.directives must be a list")
        raw_directives = []
    validated: list[dict[str, Any]] = []
    for index, directive in enumerate(raw_directives):
        parsed = _validate_lint_directive(
            directive, f"lint_ignore_discovery.directives[{index}]", errors, warnings
        )
        if parsed is not None:
            validated.append(parsed)
    return {"directives": validated}


def _validate_lint_directive(
    directive: Any, prefix: str, errors: list[str], warnings: list[str]
) -> dict[str, Any] | None:
    if not isinstance(directive, dict):
        errors.append(f"{prefix} must be a mapping")
        return None
    tool = directive.get("tool")
    if not isinstance(tool, str) or not tool:
        errors.append(f"{prefix}.tool must be a non-empty string")
    suffixes = directive.get("suffixes")
    if (
        not isinstance(suffixes, list)
        or not suffixes
        or not all(isinstance(item, str) and item.startswith(".") for item in suffixes)
    ):
        errors.append(f"{prefix}.suffixes must be a non-empty list of dot-prefixed extensions")
    pattern = directive.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        errors.append(f"{prefix}.pattern must be a non-empty regex string")
    else:
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"{prefix}.pattern is not a valid regex: {exc}")
    scope = directive.get("scope", "leading")
    if scope not in LINT_IGNORE_DIRECTIVE_SCOPES:
        errors.append(f"{prefix}.scope must be one of inline, file, leading")
    for key in directive:
        if key not in LINT_IGNORE_DIRECTIVE_KNOWN_KEYS:
            warnings.append(f"{prefix}.{key} is not a recognized key")
    if any(message.startswith(prefix) for message in errors):
        return None
    return {"tool": tool, "suffixes": list(suffixes), "pattern": pattern, "scope": scope}


def skill_ergonomics_gate_rules(value: Any, errors: list[str]) -> list[str] | None:
    return validate_skill_ergonomics_gate_rules(value, errors)


def nose_inventory_paths(value: Any, errors: list[str]) -> list[str] | None:
    """Validate the clone-inventory scope as non-escaping repo-relative paths."""
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append("nose_inventory_paths must be a list of non-empty strings")
        return None
    invalid = [
        item
        for item in value
        if (
            PurePosixPath(item).is_absolute()
            or PureWindowsPath(item).is_absolute()
            or PureWindowsPath(item).drive
            or PureWindowsPath(item).root
            or ".." in PurePosixPath(item).parts
            or ".." in PureWindowsPath(item).parts
        )
    ]
    if invalid:
        errors.append(
            "nose_inventory_paths entries must be non-empty repo-relative paths without '..': "
            + ", ".join(repr(item) for item in invalid)
        )
        return []
    return list(value)


def quality_phases(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("quality_phases must be a list")
        return None
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        prefix = f"quality_phases[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        label = raw.get("label")
        if not isinstance(label, str) or not label:
            errors.append(f"{prefix}.label must be a non-empty string")
            continue
        if label in seen:
            errors.append(f"{prefix}.label `{label}` is duplicated")
            continue
        seen.add(label)
        writes = raw.get("writes_git_tracked_artifact", False)
        if not isinstance(writes, bool):
            errors.append(f"{prefix}.writes_git_tracked_artifact must be a boolean")
            continue
        validated.append({"label": label, "writes_git_tracked_artifact": writes})
    return validated
