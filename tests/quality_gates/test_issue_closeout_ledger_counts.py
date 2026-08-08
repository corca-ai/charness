"""A consolidation ledger states its POPULATION and its REMOVALS separately.

Measured frequency, not supposition: closeout ledger arithmetic was the blocking
resolution-critique finding in THREE of four consecutive closeouts, always the
same way — the owner counted among the things consolidated.

The floor is narrow by construction, because the goal that owns this repair
forbids a gate an operator would learn to ignore. It never checks arithmetic, and
it fires only on a counting claim. Most of what follows pins what it must NOT
refuse.
"""
from __future__ import annotations

import runpy
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "skills/public/issue/scripts"

evaluate = runpy.run_path(str(_SCRIPTS / "issue_closeout_ledger_counts.py"))["evaluate"]

#: The phrasing that actually blocked three closeouts.
_BLOCKED = "decision: consolidated. proof: gate green. four implementations, three consolidated"
#: The same finding stated as two numbers.
_REPAIRED = (
    "decision: consolidate. proof: gate green. population: 4 implementations; "
    "removed: 2 private copies; the owner and one exempt caller stayed"
)


def test_refuses_the_phrasing_that_blocked_three_closeouts() -> None:
    report = evaluate(_BLOCKED)
    assert report["applies"] is True
    assert report["ok"] is False
    assert "separating population from removals" in report["reason"]


def test_accepts_the_same_finding_stated_as_two_numbers() -> None:
    report = evaluate(_REPAIRED)
    assert report["applies"] is True
    assert report["ok"] is True
    assert (report["population"], report["removed"]) == ("4", "2")


def test_it_does_not_check_the_arithmetic() -> None:
    """Deliberate non-goal, pinned so nobody 'improves' it into a prose parser.

    `population: 4; removed: 9` is nonsense and passes. Judging an arithmetic
    claim written in English is exactly the gate an operator learns to ignore;
    the shape rule makes the ambiguity unwritable instead.
    """
    assert evaluate("consolidated 9. population: 4; removed: 9")["ok"] is True


# --- what it must NOT refuse ------------------------------------------------


def test_a_ledger_with_no_counting_claim_is_not_applicable() -> None:
    report = evaluate("decision: no siblings found; proof: repo-wide grep, zero hits")
    assert report["applies"] is False
    assert report["ok"] is True
    assert "no counting claim" in report["reason"]


def test_a_consolidation_verb_without_a_number_is_not_a_counting_claim() -> None:
    """One sibling, consolidated. There is no population arithmetic to separate."""
    assert evaluate("decision: consolidated the duplicate; proof: gate green")["applies"] is False


def test_a_number_far_from_the_verb_is_not_one_claim() -> None:
    """Bounded span: a count in one sentence and a verb three later is not a claim."""
    text = (
        "decision: keep. proof: 4 tests cover it. "
        "Nothing about this needed to be consolidated at all."
    )
    assert evaluate(text)["applies"] is False


def test_empty_and_missing_values_are_not_applicable() -> None:
    for value in (None, "", "   "):
        report = evaluate(value)
        assert report["applies"] is False
        assert report["ok"] is True


# --- the two halves are genuinely two halves --------------------------------


def test_one_label_cannot_satisfy_both_halves() -> None:
    """The label sets are disjoint, so `removed: 2` alone is still a refusal.

    Without this the floor could be satisfied by restating one number twice —
    which is the single-number failure it exists to prevent, wearing a label.
    """
    only_removed = evaluate("consolidated 3 of them. removed: 2")
    assert only_removed["ok"] is False
    assert only_removed["population"] is None
    assert only_removed["removed"] == "2"

    only_population = evaluate("consolidated 3 of them. population: 4")
    assert only_population["ok"] is False
    assert only_population["population"] == "4"
    assert only_population["removed"] is None


def test_an_unlabeled_count_is_refused_even_when_both_numbers_are_present() -> None:
    """`removed 2 of the 4 copies` has both facts and still cannot be read safely.

    The point is not that the numbers exist; it is that a reader can tell which
    is which without subtracting.
    """
    assert evaluate("decision: consolidate; proof: green. removed 2 of the 4 copies")["ok"] is False


# --- the call site ----------------------------------------------------------


def test_the_bug_ledger_call_site_reports_the_missing_field() -> None:
    loader = runpy.run_path(str(_SCRIPTS / "issue_local_import.py"))["sibling_loader"]
    body = loader(str(_SCRIPTS / "issue_verify_closeout_body.py"))("issue_verify_closeout_body")
    template = (
        "Closes #1\n\n"
        "Classification: bug\n"
        "JTBD: the thing\n"
        "Root cause: the cause\n"
        "Debug artifact: charness-artifacts/debug/x.md\n"
        "Prevention: a gate\n"
        "Siblings: {siblings}\n"
    )
    blocked = body._missing_ledger_fields(template.format(siblings=_BLOCKED), "bug")
    assert "siblings_separate_population_and_removal_counts" in blocked
    repaired = body._missing_ledger_fields(template.format(siblings=_REPAIRED), "bug")
    assert repaired == [], repaired
