"""Deliberate absence — the adapter's vocabulary for "this field is missing on purpose".

Absence alone cannot carry intent. `field not in raw` reads identically whether the
operator never set the field or deliberately cut it, so a generator that defaults on
absence refills both cases. That is the #481 loss: a repo that had removed
`coverage_floor_policy` (because it uses neither lefthook nor CI) got it back on the
next bootstrap, pointing at files that do not exist.

`deliberately_absent` makes the second case sayable, and it carries the rationale in
the SAME place as the signal. That pairing is the point: the rationale used to live in
a YAML comment, which is the one part of the file a re-serializer cannot keep, so the
only record of the intent died in the same pass that overrode it.

    deliberately_absent:
      coverage_floor_policy: this repo uses neither lefthook nor CI
      security_commands: no repo-owned security helper exists here

An adapter without the field behaves exactly as it did before it existed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Fields that describe the adapter itself rather than an optional repo surface.
# Declaring one of these absent would not express a customization, it would produce
# an adapter that cannot be resolved — so it is refused rather than honored.
STRUCTURAL_FIELDS = frozenset(
    "version repo language output_dir preset_id customized_from deliberately_absent".split()
)

FIELD = "deliberately_absent"


def absence_path_parts(field: str) -> tuple[str, ...]:
    return tuple(part for part in field.split(".") if part)


def nested_path_is_set(data: dict[str, Any], field: str) -> bool:
    current: Any = data
    for part in absence_path_parts(field):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def remove_nested_absences(data: dict[str, Any], declared: dict[str, str]) -> None:
    """Remove declared dotted leaves after permissive policy merges refill them."""
    for field in declared:
        parts = absence_path_parts(field)
        if len(parts) < 2:
            continue
        current: Any = data
        for part in parts[:-1]:
            if not isinstance(current, dict):
                break
            current = current.get(part)
        if isinstance(current, dict):
            current.pop(parts[-1], None)


def load_deliberately_absent(
    raw: dict[str, Any], adapter_path: Path, known_fields: set[str] | None = None
) -> tuple[dict[str, str], list[str]]:
    """Validate and return the adapter's declared deliberate absences, plus warnings.

    Raises ValueError with a repair instruction; the caller re-raises it as the
    bootstrap's own validation error type.
    """
    if FIELD not in raw:
        return {}, []
    declared = raw.get(FIELD)
    if not isinstance(declared, dict):
        raise ValueError(
            f"{adapter_path}: `{FIELD}` must be a mapping of field name to the reason it is "
            f"absent (got {type(declared).__name__}). Repair the adapter before rerunning bootstrap."
        )
    errors: list[str] = []
    honored: dict[str, str] = {}
    for field, reason in declared.items():
        if not isinstance(field, str) or not field.strip():
            errors.append(f"field name {field!r} is not a non-empty string")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"`{field}` has no reason; a deliberate absence must say why, or a later "
                "reader cannot tell it from an oversight"
            )
            continue
        parts = absence_path_parts(field)
        root = parts[0] if parts else field
        if root in STRUCTURAL_FIELDS:
            errors.append(f"`{field}` is structural and cannot be declared absent")
            continue
        if nested_path_is_set(raw, field):
            errors.append(
                f"`{field}` is declared absent but is also set in this adapter; remove one "
                "of the two so the intent is unambiguous"
            )
            continue
        honored[field] = reason.strip()
    if errors:
        rendered = "; ".join(errors)
        raise ValueError(
            f"{adapter_path}: invalid `{FIELD}`; {rendered}. Repair the adapter before rerunning bootstrap."
        )
    # A misspelled field name is honored as a silent no-op: the declaration looks
    # right in the file and the real field keeps getting refilled forever, which is
    # the exact confusion this vocabulary exists to end. It stays a warning rather
    # than an error because declaring a consumer-owned field absent is legal.
    warnings: list[str] = []
    if known_fields:
        unrecognized = sorted(field for field in honored if field not in known_fields)
        if unrecognized:
            warnings.append(
                f"`{FIELD}` names {len(unrecognized)} field(s) this bootstrap does not "
                f"generate: {', '.join(unrecognized)}. If one is a typo, the field it was "
                "meant to name is still being refilled from defaults."
            )
    return honored, warnings
