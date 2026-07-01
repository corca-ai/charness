"""Deterministic unit coverage for two `claim_fidelity_lib` helpers, called
directly rather than through `validate_registry`.

Complements `test_claim_fidelity_specs.py`, which only reaches these helpers via
the full registry path and therefore never asserts their return values or the
whitespace-only trigger edge. Scope here is deliberately narrow: the empty-list
and duplicate rejections in `_validate_string_list`, and the on-demand trigger
requirement in `_validate_engagement`.
"""

from __future__ import annotations

import pytest

from scripts.claim_fidelity_lib import _validate_engagement, _validate_string_list
from scripts.public_skill_validation_lib import ValidationError

SPEC = "evals/cautilus/unit/spec.json"


# --- _validate_string_list: empty-list and duplicate rejection ---------------


def test_string_list_valid_returns_value() -> None:
    value = ["a.md", "b.md"]
    assert _validate_string_list(SPEC, "declaredReferences", value) == value


def test_string_list_empty_rejected() -> None:
    with pytest.raises(ValidationError, match="`declaredReferences` must be a non-empty string list"):
        _validate_string_list(SPEC, "declaredReferences", [])


def test_string_list_duplicate_rejected() -> None:
    with pytest.raises(ValidationError, match="`declaredReferences` has duplicate entries"):
        _validate_string_list(SPEC, "declaredReferences", ["a.md", "a.md"])


# --- _validate_engagement: on-demand trigger requirement ---------------------


def test_engagement_on_demand_with_trigger_returns_tuple() -> None:
    value = {"engagement": "on-demand", "rationale": "narrow", "trigger": "when X happens"}
    assert _validate_engagement(SPEC, "b.md", value) == ("on-demand", None)


def test_engagement_on_demand_missing_trigger_rejected() -> None:
    value = {"engagement": "on-demand", "rationale": "narrow"}
    with pytest.raises(ValidationError, match="on-demand reference b.md must record a trigger"):
        _validate_engagement(SPEC, "b.md", value)


def test_engagement_on_demand_whitespace_trigger_rejected() -> None:
    # A whitespace-only trigger is stripped to empty and must be rejected the
    # same as a missing one; the registry-level suite only exercises the
    # missing-key case, so this edge is unique coverage.
    value = {"engagement": "on-demand", "rationale": "narrow", "trigger": "   "}
    with pytest.raises(ValidationError, match="on-demand reference b.md must record a trigger"):
        _validate_engagement(SPEC, "b.md", value)
