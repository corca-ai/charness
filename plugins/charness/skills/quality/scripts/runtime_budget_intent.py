"""Validate adapter-owned scheduling intent for runtime budget labels."""
from __future__ import annotations

from typing import Any

RUNTIME_BUDGET_INTENT_KEYS = {"always", "conditional", "external"}


def _mapping(value: Any, field: str, errors: list[str]) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"runtime_budget_intent.{field} must be a mapping")
        return {}
    result: dict[str, str] = {}
    for label, explanation in value.items():
        if not isinstance(label, str) or not label.strip():
            errors.append(f"runtime_budget_intent.{field} keys must be non-empty strings")
        elif not isinstance(explanation, str) or not explanation.strip():
            errors.append(f"runtime_budget_intent.{field}.{label} must be a non-empty string")
        else:
            result[label] = explanation.strip()
    return result


def runtime_budget_intent(value: Any, errors: list[str]) -> dict[str, Any] | None:
    """Return normalized `always`, `conditional`, and `external` groups."""
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("runtime_budget_intent must be a mapping")
        return None
    for key in value:
        if key not in RUNTIME_BUDGET_INTENT_KEYS:
            errors.append(f"runtime_budget_intent.{key} is not a recognized key")

    raw_always = value.get("always", [])
    if not isinstance(raw_always, list) or not all(
        isinstance(label, str) and label.strip() for label in raw_always
    ):
        errors.append("runtime_budget_intent.always must be a list of non-empty strings")
        raw_always = []
    always = [label.strip() for label in raw_always]
    seen: dict[str, str] = {}
    for label in always:
        previous = seen.get(label)
        if previous is not None:
            errors.append(
                f"runtime_budget_intent label `{label}` is declared more than once "
                f"({previous} and always)"
            )
        else:
            seen[label] = "always"

    conditional = _mapping(value.get("conditional", {}), "conditional", errors)
    external = _mapping(value.get("external", {}), "external", errors)
    for group, entries in (("conditional", conditional), ("external", external)):
        for label in entries:
            previous = seen.get(label)
            if previous is not None:
                errors.append(
                    f"runtime_budget_intent label `{label}` is declared more than once "
                    f"({previous} and {group})"
                )
            else:
                seen[label] = group
    return {"always": always, "conditional": conditional, "external": external}
