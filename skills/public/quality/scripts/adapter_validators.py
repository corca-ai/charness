"""Field validators shared by the quality adapter resolver.

Keeps resolve_adapter.py inside the SKILL_HELPER_FILE_MAX line budget while
new adapter fields accrete over time. Each validator returns the parsed value
or None, appending human-readable errors to the shared list.
"""
from __future__ import annotations

from typing import Any

from scripts.quality_policy_defaults import validate_skill_ergonomics_gate_rules


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
            }
        )
    return validated


def skill_ergonomics_gate_rules(value: Any, errors: list[str]) -> list[str] | None:
    return validate_skill_ergonomics_gate_rules(value, errors)
