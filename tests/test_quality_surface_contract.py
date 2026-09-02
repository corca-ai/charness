from __future__ import annotations

import pytest

from scripts.adapters.quality_surface_contract import (
    SurfaceContractError,
    validate_surface_contract_section,
)

VALID = [
    "## Surface Contract Review",
    "- semantic coverage: `partial` — browser geometry remains unexamined.",
    "- surface: utility shell",
    "- owner: route state",
    "- projections: URL, DOM, geometry",
    "- state scope: viewport",
    "- transitions: open, closed, narrow viewport",
    "- proof boundary: browser acceptance probe",
    "- unexamined axes: geometry on mobile",
    "## Current Gates",
]


def test_surface_contract_accepts_explicit_partial_coverage() -> None:
    validate_surface_contract_section(VALID)


def test_surface_contract_accepts_scaffold_not_in_scope_disposition() -> None:
    validate_surface_contract_section(
        [
            "## Surface Contract Review",
            "- semantic coverage: `not-in-scope` — no product surface was reviewed.",
            "- surface: no semantic surface in scope",
            "- owner: quality reviewer",
            "- projections: not assessed because no surface is in scope",
            "- state scope: not assessed because no surface is in scope",
            "- transitions: not assessed because no surface is in scope",
            "- proof boundary: scoped quality command only",
            "- unexamined axes: surface, owner, projections, state scope, transitions, proof boundary",
            "## Current Gates",
        ]
    )


def test_surface_contract_rejects_duplicate_sections() -> None:
    with pytest.raises(SurfaceContractError, match="repeats section"):
        validate_surface_contract_section(VALID + VALID)


def test_surface_contract_rejects_duplicate_fields() -> None:
    duplicate_field = VALID[:-1] + ["- proof boundary: second observer", VALID[-1]]
    with pytest.raises(SurfaceContractError, match="repeats `proof boundary`"):
        validate_surface_contract_section(duplicate_field)


def test_surface_contract_rejects_unknown_coverage_status() -> None:
    invalid_status = VALID.copy()
    invalid_status[1] = "- semantic coverage: `unknown` — the status is not allowed."
    with pytest.raises(SurfaceContractError, match="semantic coverage must start"):
        validate_surface_contract_section(invalid_status)


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda lines: [line for line in lines if not line.startswith("- proof boundary:")], "missing fields"),
        (
            lambda lines: [
                lines[0],
                "- semantic coverage: `partial` — TODO",
                *lines[2:],
            ],
            "must be explicit",
        ),
        (
            lambda lines: [
                line.replace("unexamined axes: geometry on mobile", "unexamined axes: none")
                for line in lines
            ],
            "must name the unproven axes",
        ),
    ],
)
def test_surface_contract_rejects_hidden_or_incomplete_coverage(mutation, message: str) -> None:
    with pytest.raises(SurfaceContractError, match=message):
        validate_surface_contract_section(mutation(VALID))
