"""Field validators shared by the quality adapter resolver.

Keeps resolve_adapter.py inside the SKILL_HELPER_FILE_MAX line budget while
new adapter fields accrete over time. Each validator returns the parsed value
or None, appending human-readable errors to the shared list.
"""
from __future__ import annotations

from typing import Any

VALID_SKILL_ERGONOMICS_GATE_RULES = frozenset({
    "mode_option_pressure_terms",
})


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


def skill_ergonomics_gate_rules(value: Any, errors: list[str]) -> list[str] | None:
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
