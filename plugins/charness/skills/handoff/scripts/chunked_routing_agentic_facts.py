from __future__ import annotations

from typing import Any


def _basis_string_tokens(basis: object) -> set[str]:
    if not isinstance(basis, list):
        return set()
    return {token for token in basis if isinstance(token, str)}


def merge_policy_fact(
    *,
    label: str,
    source_ids: list[int],
    basis: object,
    valid_basis: set[str],
    broad_tokens: set[str],
    allowed_broad: set[str],
) -> dict[str, Any]:
    basis_tokens = _basis_string_tokens(basis)
    unknown_basis = sorted(token for token in basis_tokens if token not in valid_basis)
    broad_basis = (basis_tokens & broad_tokens) - allowed_broad
    broad_only_overlap = bool(len(source_ids) > 1 and basis_tokens and basis_tokens <= broad_basis)
    return {
        "label": label,
        "source_ids": source_ids,
        "basis_boundary_tokens": sorted(basis_tokens),
        "unknown_basis_boundary_tokens": unknown_basis,
        "broad_boundary_tokens": sorted(broad_basis),
        "broad_only_overlap": broad_only_overlap,
        "script_role": "facts-only",
        "non_clearance": (
            "false means no broad-only warning from this policy, not safe-to-merge; "
            "agent judges semantic fit, urgency, dependency, and operator value"
        ),
        "unknown_tokens_mean": "policy has no opinion",
    }
