"""Field validators shared by the quality adapter resolver.

Keeps resolve_adapter.py inside the SKILL_HELPER_FILE_MAX line budget while
new adapter fields accrete over time. Each validator returns the parsed value
or None, appending human-readable errors to the shared list.
"""
from __future__ import annotations

import re
from typing import Any

from scripts.quality_policy_defaults import validate_skill_ergonomics_gate_rules

RUNTIME_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
DEFAULT_STARTUP_PROBE_TIMEOUT_SECONDS = 20


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


def _runtime_profile_id(value: Any, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string")
        return None
    if not RUNTIME_PROFILE_ID_RE.fullmatch(value):
        errors.append(f"{field} may only contain letters, numbers, dots, underscores, and hyphens")
        return None
    return value


def runtime_budget_profiles(value: Any, errors: list[str]) -> dict[str, dict[str, dict[str, int]]] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("runtime_budget_profiles must be a mapping")
        return None
    validated: dict[str, dict[str, dict[str, int]]] = {}
    for profile_id, raw_profile in value.items():
        valid_profile_id = _runtime_profile_id(profile_id, "runtime_budget_profiles profile id", errors)
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
        if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
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
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            errors.append(f"{prefix}.timeout_seconds must be a positive integer")
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


def skill_ergonomics_gate_rules(value: Any, errors: list[str]) -> list[str] | None:
    return validate_skill_ergonomics_gate_rules(value, errors)


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
