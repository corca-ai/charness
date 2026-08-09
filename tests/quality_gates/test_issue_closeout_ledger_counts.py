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


# --- round-2 repairs -------------------------------------------------------


def test_a_sentence_final_count_is_still_a_counting_claim() -> None:
    """Counts sit at sentence ends, and the first cut excluded every one.

    Round-1's fix for `file.py:12` / `2026-08-08` excluded a numeral followed by
    ANY `.`, which silently swallowed `bundled 3.` — the exact ambiguity the floor
    exists to refuse, written with the authoring reference's own verb.
    """
    assert evaluate("decision: bundle; proof: green. Four sibling sites; bundled 3.")["ok"] is False


def test_removal_labels_stay_in_step_with_the_trigger_verbs() -> None:
    """Widening the trigger without the labels refuses a CORRECT ledger.

    `Population: 4 call sites; pruned: 2` is two facts, two labels, no
    subtraction — exactly what the floor asks for — and it was refused, telling
    the author to state a number they had already stated.
    """
    for verb, label in (
        ("prune", "pruned"), ("retire", "retired"), ("drop", "dropped"),
        ("eliminate", "eliminated"), ("absorb", "absorbed"), ("subsume", "subsumed"),
    ):
        text = f"decision: {verb}; proof: scan. population: 4 call sites; {label}: 2"
        assert evaluate(text)["ok"] is True, label
    # ...and the noun form of the canonical label, which also failed.
    assert evaluate("decision: c; proof: g. consolidated 3. population: 4; removals: 2")["ok"] is True


def test_inflected_verbs_the_shared_suffix_set_could_not_reach() -> None:
    """`dropped` was invisible — the round-1 failure sentence, one verb swapped."""
    for text in (
        "decision: d; proof: g. four sibling sites, dropped two",
        "decision: d; proof: g. four sibling sites, deduplicated two",
        "decision: d; proof: g. removals of 2 from the 4 call sites",
    ):
        assert evaluate(text)["applies"] is True, text


def test_ordinary_prose_using_those_words_is_not_a_consolidation_claim() -> None:
    """Widening a trigger over-matches if the forms are not enumerated.

    Both of these ledgers assert ZERO consolidation and were refused.
    """
    for text in (
        "decision: intentional boundary; proof: scan. 3 of the 5 matches are inline code comments",
        "decision: follow-up outside the slice; proof: scan. 2 of them are drop-in copies",
        "decision: none; proof: rg across 3 folders found no other call sites",
    ):
        assert evaluate(text)["applies"] is False, text


def test_the_clause_boundary_bounds_the_span_without_a_character_cap() -> None:
    """The cap was a FITTED constant; the clause boundary is the real bound.

    `{0,80}` had no contract behind it, so a count separated from its verb by 81
    characters slipped a floor built to refuse exactly that ambiguity. Removing it
    widens the trigger, which fails CLOSED here: a wider match means the floor
    APPLIES more often, never that it passes more often. What must still bound the
    span is the clause — a verb in one sentence and a number in the next are not a
    counting claim.
    """
    near = "consolidated the shims, and 3 of them were private copies"
    far = "consolidated the shims " + "x" * 90 + " and 3 were private"
    assert evaluate(near)["applies"] is True
    assert evaluate(far)["applies"] is True, "a fitted 80-char cap must not decide this"

    for separated in (
        "consolidated the shims. There were 3 private copies elsewhere",
        "consolidated the shims; 3 unrelated tests were renamed",
        "consolidated the shims\nThe suite has 3 remaining fixtures",
    ):
        assert evaluate(separated)["applies"] is False, separated


def test_a_synonym_the_comment_named_is_actually_carried_by_the_code() -> None:
    """`unif*` was named as a known miss in a comment and never added.

    So `Four implementations, three unified.` passed the floor while its synonym
    `three consolidated.` was refused — the floor's own ambiguity, slipping the
    floor. A defect a comment records and the code does not carry is the same
    shape as a record nobody re-read.
    """
    assert evaluate("Four implementations, three unified.")["applies"] is True
    assert evaluate("Four implementations, three unified.")["ok"] is False
    assert evaluate("Population: 4 implementations; unified: 2")["ok"] is True


def test_a_placeholder_siblings_field_is_one_defect_not_two() -> None:
    """`Siblings: TBD` is a MISSING field; the caller already reports it."""
    loader = runpy.run_path(str(_SCRIPTS / "issue_local_import.py"))["sibling_loader"]
    body = loader(str(_SCRIPTS / "issue_verify_closeout_body.py"))("issue_verify_closeout_body")
    missing = body._missing_ledger_fields(
        "Closes #1\n\nClassification: bug\nJTBD: x\nRoot cause: y\n"
        "Debug artifact: a/b.md\nPrevention: z\nSiblings: TBD\n",
        "bug",
    )
    assert "siblings" in missing
    assert "siblings_decision_and_proof" not in missing


def test_every_finding_id_the_owner_emits_has_an_author_facing_description() -> None:
    """The drift the round-1 repair fixed, now PINNED.

    Round 2: the stale copy was repaired but the blindness that allowed it was
    not. A third rule id added without a description silently regresses BOTH
    repaired consumers at once — the shape producer omits it, and the blocking
    carrier prints it with no explanation.
    """
    mod = runpy.run_path(str(_SCRIPTS / "issue_closeout_ledger_counts.py"))
    described = set(mod["SIBLING_RULE_DESCRIPTIONS"])
    emitted = set(mod["missing_sibling_ledger_fields"]("consolidated 3 of them"))
    assert emitted <= described, sorted(emitted - described)
    assert mod["missing_sibling_ledger_fields"]("population: 4; removed: 2. decision: c; proof: g") == []
    for finding_id in described:
        assert mod["rule_reason"]("consolidated 3 of them", finding_id)
