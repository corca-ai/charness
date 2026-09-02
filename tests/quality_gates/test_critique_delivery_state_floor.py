"""The `Delivery state` floor: a reviewer that ran is not a reviewer that delivered.

Behavioural cover for `scripts/critique_reviewer_evidence.validate_delivery_state`.
The failure this floor exists to stop: bounded reviewers ran correctly, kept a
clean rail-1 boundary, wrote complete final messages, and delivered nothing the
parent could read, because the spawn call shape routed them to a mailbox channel
the parent had no tool to open. A closeout could still record
`Fresh-eye satisfaction: parent-delegated` with clean tier evidence and assert
exactly that false confidence.

Enforced for artifacts dated on/after `DELIVERY_STATE_RULE_DATE` (2026-07-26),
the same `RULE_DATE = landing_day + 1` shape the fresh-eye and boundary-ownership
floors use. An undatable artifact is NOT fail-open: it is enforced like
post-cutoff unless its filename is one of the named legacy exceptions.

These run in-process rather than through the CLI. The behaviour under test is
ordinary domain logic (which values a floor accepts), not a packaging, exit-code,
or stderr-protocol contract, so it does not need a delivery-boundary crossing —
the test-side process-boundary policy puts this on the in-process side. The
floor's *wiring* into the validator run is separately covered by the
full-artifact fixtures in `test_critique_skill.py` and by the live-corpus sweep.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from scripts.review.critique_reviewer_evidence import (
    DELIVERY_STATE_RULE_DATE,
    validate_delivery_state,
)
from scripts.review.validate_critique_artifacts import (
    BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS,
    ValidationError,
    _opens_with_typed_value,
    _section_field_map,
)

POST_CUTOFF = DELIVERY_STATE_RULE_DATE
PRE_CUTOFF = date(2026, 7, 20)

_TIER_BLOCK = """## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none
- Host exposure state: host-defaulted
- Application state: no host signal exposed
"""


def _artifact_text(delivery: str | None) -> str:
    """A reviewer-tier block whose only variable is the delivery-state line."""
    text = _TIER_BLOCK
    if delivery is not None:
        text += f"- Delivery state: {delivery}\n"
    return text


def _check(
    delivery: str | None, *, observed_date: date | None, name: str = "2026-07-26-demo.md"
) -> None:
    validate_delivery_state(
        Path(name),
        _artifact_text(delivery),
        observed_date,
        section_field_map=_section_field_map,
        opens_with_typed_value=_opens_with_typed_value,
        legacy_undatable=BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS,
    )


def test_missing_delivery_state_is_rejected_post_cutoff() -> None:
    with pytest.raises(ValidationError) as excinfo:
        _check(None, observed_date=POST_CUTOFF)

    message = str(excinfo.value)
    assert "has no `Delivery state:` line" in message
    # The message must teach the distinction, not merely name a missing field.
    assert "says nothing about whether the findings ever" in message
    assert "findings-received" in message
    assert "spawn-accepted-no-delivery" in message


def test_untyped_delivery_state_value_is_rejected() -> None:
    with pytest.raises(ValidationError) as excinfo:
        _check("the review came back fine", observed_date=POST_CUTOFF)

    assert "does not open with one of" in str(excinfo.value)


def test_unedited_todo_after_typed_value_is_rejected() -> None:
    """A scaffolded stub that kept its TODO is not a real record."""
    with pytest.raises(ValidationError) as excinfo:
        _check("findings-received TODO confirm", observed_date=POST_CUTOFF)

    assert "still carries an unedited `todo`" in str(excinfo.value)


def test_bare_no_delivery_without_a_signal_is_rejected() -> None:
    """Recording a delivery failure without naming the channel loses the cause."""
    with pytest.raises(ValidationError) as excinfo:
        _check("spawn-accepted-no-delivery", observed_date=POST_CUTOFF)

    assert "must name the concrete channel or host signal" in str(excinfo.value)


@pytest.mark.parametrize(
    "delivery",
    [
        "findings-received",
        "spawn-accepted-no-delivery mailbox channel, host exposes no message-reading tool",
        "spawn-accepted-no-delivery: host returned a spawn id and never a result",
    ],
)
def test_real_delivery_records_are_accepted(delivery: str) -> None:
    _check(delivery, observed_date=POST_CUTOFF)


def test_pre_cutoff_artifact_is_grandfathered() -> None:
    """The floor must not retroactively invalidate the existing corpus."""
    _check(None, observed_date=PRE_CUTOFF)


def test_undatable_artifact_is_not_fail_open() -> None:
    """No parseable date must not become a permanent dodge."""
    with pytest.raises(ValidationError):
        _check(None, observed_date=None, name="undated-demo.md")


def test_named_legacy_undatable_artifact_is_grandfathered() -> None:
    legacy = sorted(BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS)[0]
    _check(None, observed_date=None, name=legacy)


@pytest.mark.parametrize(
    "delivery",
    [
        "**spawn-accepted-no-delivery**",
        "`spawn-accepted-no-delivery`",
        "  spawn-accepted-no-delivery  ",
        "- spawn-accepted-no-delivery",
    ],
)
def test_markup_cannot_smuggle_a_no_delivery_record_past_the_signal_requirement(
    delivery: str,
) -> None:
    """Release-critique finding: the typed check strips leading markup, so testing
    the raw string for the signal requirement let a bolded or backticked value
    satisfy the type and then skip the "name the channel" rule entirely — a typed
    delivery failure with no recorded cause, which is the ceremony this floor
    exists to prevent. Both checks must normalize identically.
    """
    with pytest.raises(ValidationError) as excinfo:
        _check(delivery, observed_date=POST_CUTOFF)

    assert "must name the concrete channel or host signal" in str(excinfo.value)


def test_marked_up_no_delivery_with_a_real_signal_still_passes() -> None:
    """The normalization must not over-reach into rejecting a real record."""
    _check(
        "**spawn-accepted-no-delivery** mailbox channel, no reader tool", observed_date=POST_CUTOFF
    )


def test_transcript_recovery_is_not_recordable_as_a_clean_delivery() -> None:
    """Recovery is a delivery FAILURE that happened to be salvageable.

    The reviewer-result helper makes transcript recovery easy, which is exactly
    why it needs its own typed value: folded into `findings-received`, the
    diagnostic path becomes indistinguishable from a clean inline delivery and
    the spawn-shape discipline erodes with nothing to catch it.
    """
    with pytest.raises(ValidationError) as excinfo:
        _check("findings-recovered-from-transcript", observed_date=POST_CUTOFF)

    assert "must name the concrete channel or host signal" in str(excinfo.value)


def test_transcript_recovery_with_a_named_signal_is_accepted() -> None:
    _check(
        "findings-recovered-from-transcript named spawn routed to an unreadable mailbox",
        observed_date=POST_CUTOFF,
    )


def test_recovered_is_not_swallowed_by_the_received_prefix() -> None:
    """`findings-received` must not shadow `findings-recovered-from-transcript`."""
    with pytest.raises(ValidationError):
        _check("findings-recovered-from-transcript", observed_date=POST_CUTOFF)
    _check("findings-received", observed_date=POST_CUTOFF)
