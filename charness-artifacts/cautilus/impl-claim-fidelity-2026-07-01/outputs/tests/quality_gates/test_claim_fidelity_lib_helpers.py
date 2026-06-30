"""Direct unit coverage for `claim_fidelity_lib` private validators.

These call `_validate_string_list` and `_validate_engagement` directly, with no
registry or filesystem scaffolding. That is the deliberate non-overlap with
`test_claim_fidelity_specs.py`, which reaches the same helpers only through the
full `validate_registry` path: the registry-level suite never builds an empty or
duplicated string list, never exercises a whitespace-only on-demand trigger, and
never asserts the helpers' return values. This file pins those branches.
"""

from __future__ import annotations

import pytest

from scripts.claim_fidelity_lib import _validate_engagement, _validate_string_list
from scripts.public_skill_validation_lib import ValidationError

SPEC = "evals/cautilus/x-claim-fidelity/spec.json"


# --- _validate_string_list ---------------------------------------------------


def test_string_list_empty_rejected() -> None:
    with pytest.raises(ValidationError, match="`declaredReferences` must be a non-empty string list"):
        _validate_string_list(SPEC, "declaredReferences", [])


def test_string_list_duplicate_rejected() -> None:
    with pytest.raises(ValidationError, match="`declaredReferences` has duplicate entries"):
        _validate_string_list(SPEC, "declaredReferences", ["a.md", "a.md"])


def test_string_list_valid_returns_value() -> None:
    # Anchors the positive branch so the rejection cases above are meaningful:
    # a distinct, non-empty string list passes through unchanged.
    value = ["a.md", "b.md"]
    assert _validate_string_list(SPEC, "declaredReferences", value) == value


# --- _validate_engagement: on-demand trigger-required rule --------------------


def test_on_demand_missing_trigger_rejected() -> None:
    value = {"engagement": "on-demand", "rationale": "narrow"}
    with pytest.raises(ValidationError, match="on-demand reference ref.md must record a trigger"):
        _validate_engagement(SPEC, "ref.md", value)


def test_on_demand_blank_trigger_rejected() -> None:
    # A whitespace-only trigger is as absent as a missing key: the `or ""`/strip
    # branch must still reject it. The registry-level suite never reaches this.
    value = {"engagement": "on-demand", "rationale": "narrow", "trigger": "   "}
    with pytest.raises(ValidationError, match="on-demand reference ref.md must record a trigger"):
        _validate_engagement(SPEC, "ref.md", value)


def test_on_demand_with_trigger_returns_engagement() -> None:
    # Positive control: a present trigger makes the rule pass and the helper
    # returns the engagement literal it validated.
    value = {"engagement": "on-demand", "rationale": "narrow", "trigger": "when X"}
    assert _validate_engagement(SPEC, "ref.md", value) == "on-demand"
