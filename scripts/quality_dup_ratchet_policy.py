"""Adapter policy for the boy-scout duplicate ratchet (item 5, slice 2).

Lives in its own module rather than piling onto ``quality_policy_defaults`` (which
already sits at its length cap): the dup-ratchet block is the most standalone of
the quality gate blocks — it has its own portable gate script
(``skills/public/quality/scripts/check_dup_ratchet.py``), its own policy library
(``dup_ratchet_lib``), and its own reference
(``skills/public/quality/references/dup-ratchet.md``). ``quality_adapter_lib``
imports the default + validator from here.
"""

from __future__ import annotations

from typing import Any

# DEFAULT_DUP_RATCHET is opt-in/inert: enabled:false makes check_dup_ratchet.py a
# no-op (exit 0) so the portable default stays stack-neutral. A consuming repo
# enables it and points review_artifact_path / gate_baseline_path / scope_paths at
# its own artifacts. floor_F is the healthy fixable floor (boy-scout arm softens to
# advisory at/below it); escalation_K is the stagnation commit budget before the
# boy-scout nudge escalates to a one-time block. See references/dup-ratchet.md.
DEFAULT_DUP_RATCHET: dict[str, Any] = {
    "enabled": False,
    "floor_F": 0,
    "escalation_K": 10,
    "scope_paths": [],
    "review_artifact_path": "charness-artifacts/quality/dup-review.json",
    "gate_baseline_path": "charness-artifacts/quality/dup-ratchet-baseline.json",
}
DUP_RATCHET_KNOWN_KEYS = frozenset(DEFAULT_DUP_RATCHET.keys())
# Minimum accepted value per integer key (escalation_K >= 1 so the boy-scout arm
# cannot escalate at zero stagnation).
_DUP_RATCHET_INT_MINIMUMS = {"floor_F": 0, "escalation_K": 1}


def _dup_ratchet_defaults() -> dict[str, Any]:
    return {**DEFAULT_DUP_RATCHET, "scope_paths": list(DEFAULT_DUP_RATCHET["scope_paths"])}


def validate_dup_ratchet(value: Any, errors: list[str], warnings: list[str]) -> dict[str, Any] | None:
    """Validate the dup_ratchet adapter block.

    Returns None when absent; defaults are supplied by infer_quality_defaults.
    `enabled:false` (the default) makes the gate inert. `floor_F`/`escalation_K` are
    non-negative integers; `scope_paths` is a glob/path list; `review_artifact_path`
    / `gate_baseline_path` are non-empty paths. Unknown sub-keys land in warnings
    (precedent: validate_changed_line_mutation_gate).
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("dup_ratchet must be a mapping")
        return None
    validated = _dup_ratchet_defaults()
    for key, raw in value.items():
        if key not in DUP_RATCHET_KNOWN_KEYS:
            warnings.append(f"unknown dup_ratchet sub-key: {key}")
        elif key == "enabled":
            if isinstance(raw, bool):
                validated[key] = raw
            else:
                errors.append("dup_ratchet.enabled must be a boolean")
        elif key in _DUP_RATCHET_INT_MINIMUMS:
            minimum = _DUP_RATCHET_INT_MINIMUMS[key]
            if not isinstance(raw, int) or isinstance(raw, bool):
                errors.append(f"dup_ratchet.{key} must be an integer")
            elif raw < minimum:
                errors.append(f"dup_ratchet.{key} must be greater than or equal to {minimum}")
            else:
                validated[key] = raw
        elif key == "scope_paths":
            if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
                validated[key] = list(raw)
            else:
                errors.append("dup_ratchet.scope_paths must be a list of strings")
        elif key in {"review_artifact_path", "gate_baseline_path"}:
            if isinstance(raw, str) and raw:
                validated[key] = raw
            else:
                errors.append(f"dup_ratchet.{key} must be a non-empty string")
    return validated
