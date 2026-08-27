"""The fresh-eye contract owns reviewer result delivery, not just reviewer conduct.

Regression guard for #454: bounded reviewers ran correctly, kept a clean rail-1
boundary, and wrote complete final messages that never reached the parent,
because a named spawn selected a mailbox channel the parent had no tool to read.
The same differential was observed on 2026-06-20 and lost to lesson decay before
it reached a contract, so the rule is pinned here rather than left to prose that
ages out.

Delivery itself is a per-host live claim and is intentionally not asserted here;
these tests pin that the contract *states* the rule and keeps delivery separable
from boundary state.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_REVIEW = REPO_ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
ENVELOPE = REPO_ROOT / ".claude" / "agents" / "bounded-reviewer.md"


def _unwrapped(path: Path) -> str:
    """Read a prose surface with line wrapping and markdown emphasis collapsed.

    These guards pin what the contract *says*. A reflow that moves a phrase
    across a line break, or a change in which words carry bold, must not read as
    the clause going missing — that is maintenance tax with no safety gain.
    """
    text = path.read_text(encoding="utf-8").replace("*", "").replace("_", "")
    return re.sub(r"\s+", " ", text)


def _shared_review() -> str:
    return _unwrapped(SHARED_REVIEW)


def test_shared_reference_owns_a_result_delivery_section() -> None:
    assert "## Result Delivery" in _shared_review(), (
        "the shared fresh-eye reference is the canonical owner of the delivery rule; "
        "skills cite this section instead of restating it"
    )


def test_delivery_rule_names_the_unnamed_spawn_shape() -> None:
    text = _shared_review()
    assert "without a host addressing or team name" in text, (
        "the contract must state the one-shot spawn shape that returns findings to the caller"
    )


def test_spawn_acceptance_is_not_delivery_proof() -> None:
    text = _shared_review()
    assert "A spawned reviewer is not a received review." in text
    assert "spawn-accepted-no-delivery" in text, (
        "closeout must be able to record delivery failure as a typed state"
    )
    assert "findings-received" in text


def test_delivery_state_stays_separable_from_boundary_state() -> None:
    text = _shared_review()
    assert "Boundary clean and findings received are independent claims" in text, (
        "rail-1 boundary cleanliness and findings delivery must stay separable claims; "
        "collapsing them is the false-confidence failure this guard exists to stop"
    )


def test_blocked_path_probe_requires_findings_not_just_a_spawn() -> None:
    text = _shared_review()
    assert "The probe passes only when the reviewer's findings text reaches you." in text, (
        "an accepted-but-undelivered spawn must fail the availability probe"
    )


def test_do_not_list_forbids_named_one_shot_reviewer_spawns() -> None:
    text = _shared_review()
    tail = text.split("## Do Not", 1)
    assert len(tail) == 2, "the shared reference must keep its Do Not list"
    assert "host addressing or team name to a one-shot bounded reviewer" in tail[1]


def test_envelope_points_reviewers_at_the_delivery_owner() -> None:
    text = _unwrapped(ENVELOPE)
    assert "Result Delivery" in text, (
        "the reviewer envelope must cite the delivery owner rather than restating it"
    )
    assert "final assistant message" in text
