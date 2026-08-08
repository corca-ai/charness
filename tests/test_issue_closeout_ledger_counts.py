"""The sibling-search ledger's counting floor.

This module shipped with no standing test at all, so the changed-line coverage
gate reported it as NOT ANALYZED and refused to call the run complete — the
honest verdict, and the reason it is covered here rather than waved through.

The floor's own contract, from its module docstring: it never checks the
ARITHMETIC. `four implementations, three consolidated` may or may not be wrong,
and deciding that from English is how a gate earns a route-around. It checks that
the two facts were stated as two labelled numbers, which the writer controls and
a reviewer can verify at a glance. These tests hold it to exactly that line.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MODULE = ROOT / "skills/public/issue/scripts/issue_closeout_ledger_counts.py"


def _load():
    spec = importlib.util.spec_from_file_location("issue_closeout_ledger_counts_under_test", _MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


counts = _load()


def _substantive(value: str) -> bool:
    return bool(value.strip()) and value.strip().upper() not in {"TBD", "TODO"}


def test_no_counting_claim_is_reported_as_not_applicable_never_as_a_pass() -> None:
    result = counts.evaluate("Searched the adapter modules; found no other call site.")

    assert result["applies"] is False
    assert result["ok"] is True
    # The distinction this floor exists to keep visible: nothing was counted, so
    # nothing was checked. That is not the same as a clean count.
    assert "not applicable" in result["reason"]


def test_an_absent_ledger_is_not_this_floors_refusal() -> None:
    # The caller owns "the field is missing"; reporting it here too would name
    # one defect as two.
    for empty in (None, "", "   "):
        assert counts.evaluate(empty)["applies"] is False


def test_the_one_sentence_two_number_shape_is_refused() -> None:
    """The measured defect: the owner counted among the things consolidated.

    A reader cannot tell whether `three consolidated` means three were removed,
    or three were folded into a survivor that is one of them.
    """
    result = counts.evaluate("Found four implementations, three consolidated into the owner.")

    assert result["applies"] is True
    assert result["ok"] is False
    assert result["reason"]


def test_two_labelled_counts_satisfy_the_floor() -> None:
    result = counts.evaluate(
        "Sibling search: population: 4, removed: 2. Decision: fold the two private "
        "copies into the owner. Proof: the gate is green with both call sites deleted."
    )

    assert result["applies"] is True
    assert result["ok"] is True
    assert result["population"] == "4"
    assert result["removed"] == "2"


def test_number_words_are_accepted_in_the_labels_too() -> None:
    """Round-1 review of the floor: accepting `four` as a counting CLAIM while
    demanding `4` in the LABEL refused an author who had done the right thing,
    for a reason with no motivation behind it."""
    result = counts.evaluate(
        "Sibling search: population: four, removed: two. Decision: keep the owner. "
        "Proof: both copies deleted and the suite is green."
    )

    assert result["ok"] is True
    assert result["population"] == "four"
    assert result["removed"] == "two"


def test_the_floor_does_not_check_the_arithmetic() -> None:
    """Its docstring promises this, and a floor that quietly started checking it
    would be the un-ignorable gate the owning goal forbids."""
    impossible = "Sibling search: population: 2, removed: 9. Decision: x. Proof: y."

    assert counts.evaluate(impossible)["ok"] is True


def test_missing_fields_reports_every_failed_rule_not_just_the_first() -> None:
    value = "Found four implementations, three consolidated."
    missing = counts.missing_sibling_ledger_fields(value, substantive=_substantive)

    assert "siblings_decision_and_proof" in missing
    assert "siblings_separate_population_and_removal_counts" in missing


def test_a_complete_ledger_reports_nothing_missing() -> None:
    value = (
        "Sibling search: population: 4, removed: 2. Decision: fold the private copies "
        "into the owner. Proof: the broad gate is green with both deleted."
    )

    assert counts.missing_sibling_ledger_fields(value, substantive=_substantive) == []


def test_a_placeholder_is_left_to_the_callers_missing_field_check() -> None:
    # `TBD` is non-empty, so a truthiness check would report it here AND at the
    # caller, naming one defect twice.
    assert counts.missing_sibling_ledger_fields("TBD", substantive=_substantive) == []


def test_the_counting_finding_explains_itself_on_the_blocking_surface() -> None:
    """The carrier that can stop a commit had nothing to say.

    The library built a full diagnosis and its only consumer read `["ok"]` and
    dropped it, so an author stopped at the pre-commit boundary got one
    unexplained snake_case token. This returns the real reason for that finding
    and the static description for every other.
    """
    reason = counts.rule_reason(
        "Found four implementations, three consolidated.",
        "siblings_separate_population_and_removal_counts",
    )

    assert reason
    assert reason != "siblings_separate_population_and_removal_counts"
    assert len(reason) > 40, "the blocking surface should carry the diagnosis, not a token"


def test_a_satisfied_counting_ledger_has_no_finding_to_describe() -> None:
    assert (
        counts.rule_reason(
            "Sibling search: population: 4, removed: 2. Decision: x. Proof: y.",
            "siblings_separate_population_and_removal_counts",
        )
        is None
    )


def test_other_findings_fall_back_to_their_static_description() -> None:
    described = counts.rule_reason("anything", "siblings_decision_and_proof")

    assert described == counts.SIBLING_RULE_DESCRIPTIONS["siblings_decision_and_proof"]
    assert counts.rule_reason("anything", "not_a_known_finding") is None
