"""The changed-line gate's exit-code ORDERING rule, tested where the rule is written.

`scripts/gates_support/changed_line_verdict_codes.py` says "ORDER IS THE CONTRACT", and until this
file existed that contract was only exercised end-to-end through subprocess runs of
the gate — which is how the ordering shipped inverted once. Inverting `blocking` and
`fg_warning`, or `fg_warning` and `unanalyzed`, is a one-line edit whose consequence
is a push that stops being refused; this asserts each boundary directly.

It also gives the module a standing test at all: `suggest_mutation_coverage_command`
maps a changed pool file to tests that textually reference it, and a verdict-logic
module no test names is a changed pool file the pre-push lane reports as unanalyzed
— the blind spot this whole slice exists to make visible.
"""
from __future__ import annotations

from pathlib import Path

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]

codes = load_module("changed_line_verdict_codes", ROOT / "scripts" / "gates_support" / "changed_line_verdict_codes.py")


def test_the_four_bytes_are_distinct() -> None:
    """They are only useful as DIFFERENT answers; collapsing two is the defect."""
    assert len({0, 1, codes.REFUSED_EXIT, codes.UNESTABLISHED_EXIT, codes.PARTIAL_EXIT}) == 5


def test_a_real_blocker_outranks_every_scope_caveat() -> None:
    """An uncovered changed line is the actionable answer; a scope caveat must never
    downgrade it to a non-blocking byte."""
    assert codes._verdict_exit_code(["scripts/a.py"], None, []) == 1
    assert codes._verdict_exit_code(["scripts/a.py"], "FALSE GREEN", []) == 1
    assert codes._verdict_exit_code(["scripts/a.py"], None, ["scripts/b.py"]) == 1
    assert codes._verdict_exit_code(["scripts/a.py"], "FALSE GREEN", ["scripts/b.py"]) == 1


def test_an_untrustworthy_tree_outranks_a_partial_scope() -> None:
    """The boundary the first cut inverted, asserted at the level it is decided.

    3 is REFUSABLE at push time (`--refuse-unestablished`); 4 is deliberately not. So
    when both hold, answering 4 turns a push this lane used to STOP into one it waves
    through — a policy change nobody decided, shipped under a defect repair.
    """
    both = codes._verdict_exit_code([], "FALSE GREEN", ["scripts/b.py"])

    assert both == codes.UNESTABLISHED_EXIT
    assert both != codes.PARTIAL_EXIT


def test_each_cause_alone_still_gets_its_own_byte() -> None:
    """The discriminating control. Without it the test above would be satisfied by a
    function that returned 3 for everything."""
    assert codes._verdict_exit_code([], "FALSE GREEN", []) == codes.UNESTABLISHED_EXIT
    assert codes._verdict_exit_code([], None, ["scripts/b.py"]) == codes.PARTIAL_EXIT
    assert codes._verdict_exit_code([], None, []) == 0
