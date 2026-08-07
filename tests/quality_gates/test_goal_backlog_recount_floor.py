"""The backlog-recount floor: a goal must record what it claims and what it does not.

The defect this closes is that `--pursue-ready` -- the surface deciding a goal may
activate -- validated headings, placeholders and closeout-plan fields, so a goal whose
scope contradicted the tracker passed it cleanly. The floor cannot catch what the
contract never asks for.

Two properties carry the design and both are pinned here rather than argued in prose.
PRESENCE-ONLY: the floor never grades WHICH issues a goal claims, because that judgement
is the operator's and a floor grading it would be a new false-verdict surface inside the
tool built to stop them. GRANDFATHERED BY THE GOAL'S OWN `Created:` DATE, failing CLOSED
on a missing or malformed one: nineteen historical artifacts predate the rule, and a
floor that reddens the whole corpus is a floor that gets disarmed rather than obeyed.
"""
from __future__ import annotations

import sys

from .support import ROOT

sys.path.insert(0, str(ROOT / "skills/public/achieve/scripts"))

import goal_artifact_backlog as backlog  # noqa: E402

PRE_RULE = "Status: draft\nCreated: 2026-08-07\n\n## Goal\n\nsomething\n"
IN_SCOPE = "Status: draft\nCreated: 2026-08-08\n\n## Goal\n\nsomething\n"
FILLED = IN_SCOPE + (
    "\n## Backlog Recount\n\n"
    "- Counted: 28 open issues on 2026-08-08\n"
    "- Claims: #530, #554\n"
    "- Not claimed: #519 — different question\n"
)


def test_a_pre_rule_goal_is_grandfathered_and_says_so() -> None:
    """The report must not read as a satisfied floor.

    A bare `{"applies": False, "ok": True}` is the exact look-alike this goal family
    exists to remove: it renders as a pass to anyone scanning `ok`. The shared grammar's
    disclosing helper states that the floor was NOT EVALUATED and why.
    """
    report = backlog.check(PRE_RULE)

    assert report["applies"] is False
    assert report["ok"] is True
    assert report["evaluated"] is False
    assert "grandfathered off (not satisfied)" in report["reason"]


def test_a_missing_created_date_fails_closed() -> None:
    """An artifact with no parseable `Created:` is COVERED, not exempt.

    Failing open here would make the floor removable by deleting one line -- a gate whose
    bypass is easier than its compliance.
    """
    assert backlog.applies("Status: draft\n\n## Goal\n\nno created line\n") is True
    assert backlog.applies("Status: draft\nCreated: not-a-date\n") is True


def test_an_in_scope_goal_without_the_section_is_refused() -> None:
    report = backlog.check(IN_SCOPE)

    assert report["ok"] is False
    assert report["missing_fields"] == list(backlog.REQUIRED_FIELDS)
    assert "recount the tracker" in report["reason"]


def test_a_filled_section_passes() -> None:
    report = backlog.check(FILLED)

    assert report["ok"] is True
    assert report["missing_fields"] == []


def test_an_empty_field_value_is_refused_exactly_like_an_absent_one() -> None:
    """The look-alike case, which is the whole reason the floor exists.

    `Claims:` with nothing after it tells a reader precisely as much as no line at all,
    while LOOKING like the section was filled in. If the floor accepted it, satisfying
    the floor would be easier than doing the work it asks for.
    """
    empty = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims:\n- Not claimed: none\n"
    report = backlog.check(empty)

    assert report["ok"] is False
    assert report["missing_fields"] == ["Claims"]


def test_none_is_an_acceptable_answer_but_must_be_written() -> None:
    """A goal may genuinely claim nothing tracked. The floor is presence, not volume."""
    nothing = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 0 open issues\n- Claims: none\n- Not claimed: none\n"

    assert backlog.check(nothing)["ok"] is True


def test_the_floor_never_grades_which_issues_were_claimed() -> None:
    """PRESENCE-ONLY, pinned as a property rather than trusted to the docstring.

    Two goals with contradictory claim splits over the same tracker both pass. That is
    correct and deliberate: the floor makes the reasoning visible so a human or reviewer
    can grade it, and a floor that tried to decide "should this goal have claimed that
    one" would be asserting a verdict nothing can establish from the artifact.
    """
    one = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims: #530\n- Not claimed: #554\n"
    other = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims: #554\n- Not claimed: #530\n"

    assert backlog.check(one)["ok"] is True
    assert backlog.check(other)["ok"] is True


def test_the_shipped_template_carries_the_section_and_its_placeholders() -> None:
    """A floor the scaffold cannot satisfy is a floor every new goal trips blind."""
    template = (ROOT / "skills/public/achieve/scripts/goal_artifact_template.md").read_text(encoding="utf-8")

    assert f"## {backlog.SECTION}" in template
    for field in backlog.REQUIRED_FIELDS:
        assert f"- {field}: To be filled by the achieve Before-phase" in template, field


def test_this_repos_own_active_goal_satisfies_the_floor_it_ships() -> None:
    """Dogfood, and the reason the rule date is what it is.

    The goal that introduced this floor is deliberately IN SCOPE of it. A rule whose
    author's own artifact escapes it is a rule nobody has run, and the floor's first real
    use is what caught this goal's shaping count (25) already disagreeing with the live
    tracker (28).
    """
    goal = ROOT / "charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md"
    text = goal.read_text(encoding="utf-8")

    assert backlog.applies(text) is True, "the rule date must cover the goal that ships the rule"
    assert backlog.check(text)["ok"] is True
