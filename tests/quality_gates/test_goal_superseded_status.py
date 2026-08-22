"""The non-complete terminal status for the achieve contract (#691).

A goal that ends without completing -- folded into a successor, overtaken, or
abandoned with its remainder handed on -- previously had only bad options: stay
`active` forever, or claim a `complete` it never earned. Both lie to the next
session, and the second lies in the direction that loses work. `corca-ai/ceal`
had already routed around it: its own drift checker accepts `superseded` and the
repo carries goals in that state, so the repo-local gate and the upstream
contract disagreed about what a legal status is -- with the permissive side in
daily use.

The risk in the fix is the fix itself. A terminal status that skips the closeout
floor and asks for nothing in return loses the same work more quietly: a
finished-looking artifact, no successor, no reason. So these tests are mostly
about what `superseded` COSTS.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from .support import ROOT

_ACHIEVE = ROOT / "skills" / "public" / "achieve" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _ACHIEVE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def goal_lib():
    return _load("goal_artifact_lib")


@pytest.fixture(scope="module")
def pursue():
    return _load("goal_artifact_pursue")


def test_superseded_is_a_legal_status(goal_lib) -> None:
    """Pins that the status EXISTS. Without it the behavioural tests below stay
    green against a tree where it was never added, because they call the record
    checker directly and never go through status validation."""
    assert "superseded" in goal_lib.VALID_STATUSES


def test_superseded_is_terminal_so_in_flight_floors_do_not_grade_it(pursue) -> None:
    """Terminal in exactly the sense the predicate means -- nobody is expected to
    repair the record -- even though it is not complete. Leaving it out would
    grade an ended goal against floors whose purpose is to fire on a goal still in
    flight."""
    assert pursue.is_terminal_status("superseded") is True
    assert pursue.is_terminal_status("active") is False


def test_an_annotated_superseded_status_is_still_terminal(pursue) -> None:
    """The repo's house style annotates terminal statuses. A bare equality test
    silently disarms the skip, which is the defect `status_token` already exists
    to prevent for `complete`."""
    assert pursue.is_terminal_status("SUPERSEDED (2026-08-22) — folded into the successor") is True


def test_superseded_is_not_a_shaping_status(pursue) -> None:
    """Shaping floors (backlog recount, closeout binding plan) apply to a goal
    whose scope is still being decided. An ended one is not that."""
    assert pursue.is_shaping_status("superseded") is False


# --------------------------------------------------------------------------- #
# What the status costs
# --------------------------------------------------------------------------- #


def test_superseded_without_a_successor_record_is_refused(goal_lib) -> None:
    """THE guard that keeps this from being an escape hatch. Without it, adding
    the status would let a goal be abandoned with no account of where its
    remainder went -- losing the work more quietly than the lie it replaces."""
    report = goal_lib.check_superseded_record("Status: superseded\n")

    assert report["ok"] is False
    assert "Superseded by:" in report["reason"]


def test_a_punctuation_placeholder_is_not_a_successor_record(goal_lib) -> None:
    """`Superseded by: —` is a filled-looking empty field. The closeout-plan and
    backlog floors both learned this class already; inheriting the lesson is
    cheaper than re-learning it on a third surface."""
    report = goal_lib.check_superseded_record("Superseded by: —\n")

    assert report["ok"] is False
    assert "substantive" in report["reason"]


def test_a_named_successor_satisfies_the_record(goal_lib) -> None:
    report = goal_lib.check_superseded_record(
        "Superseded by: charness-artifacts/goals/2026-09-01-next.md — carried slices B and A\n"
    )

    assert report["ok"] is True


def test_an_explicit_none_satisfies_the_record(goal_lib) -> None:
    """Accepting this is the point, not a loophole: a goal genuinely abandoned
    with nothing downstream should say so out loud rather than be unable to
    close. The floor asks for an ANSWER, not for a successor to exist."""
    report = goal_lib.check_superseded_record(
        "- `Superseded by:` none — remainder dropped; the tracked issues carry it\n"
    )

    assert report["ok"] is True


def test_a_fenced_example_does_not_satisfy_the_record(goal_lib) -> None:
    """The reference documents the line inside a fenced block, and a goal that
    QUOTES the canonical form must not have the quotation read as its own claim.
    This repo has shipped that exact defect on an adjacent floor."""
    text = "Status: superseded\n\n```markdown\nSuperseded by: some/goal.md\n```\n"

    assert goal_lib.check_superseded_record(text)["ok"] is False


# --------------------------------------------------------------------------- #
# The writer refuses the flip, so the record cannot be added afterwards
# --------------------------------------------------------------------------- #


def test_upsert_refuses_to_flip_a_goal_superseded_without_the_record(
    goal_lib, tmp_path: Path
) -> None:
    """Checked at the WRITE, matching how `complete` is guarded. A validator that
    only complains after the fact leaves a window where the artifact already
    reads as terminal."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text("# Demo\n\nStatus: active\n", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
        )

    assert "superseded" in str(excinfo.value)


def test_upsert_allows_the_flip_once_the_record_is_present(goal_lib, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text(
        "# Demo\n\nStatus: active\n\nSuperseded by: charness-artifacts/goals/2026-09-01-next.md\n",
        encoding="utf-8",
    )

    goal_lib.upsert_goal(
        repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
    )

    assert "Status: superseded" in path.read_text(encoding="utf-8")
