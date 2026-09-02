"""The `consolidated` disposition: a close that claims nothing, and cannot claim more.

Consolidating a backlog MOVES issues; it does not fix them. The reason this needed
a sixth classification rather than an existing one is that both existing branches
cost the closeout floor its meaning: the resolution branch demands
`Implementation:` and `Prevention:`, so satisfying it means writing sentences that
are not true, and the exempt branch would misclassify the issue while opening a
path where any inconvenient bug reaches the light floor by relabelling.

So the tests below are mostly about what this disposition must REFUSE. The
load-bearing one is the contradiction check: without it, twenty issues close as
"moved" while the carrier quietly asserts they were fixed.
"""
from __future__ import annotations

import runpy
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/issue/scripts"

consolidated = runpy.run_path(str(_SCRIPTS / "issue_consolidated_closeout.py"))
_LEDGER = runpy.run_path(str(_SCRIPTS / "issue_closeout_classification_ledger.py"))


class _Ledger:
    """The ledger table as an attribute holder, matching what the module expects."""

    CLASSIFICATION_FIELDS = _LEDGER["CLASSIFICATION_FIELDS"]

# Modules this file is the standing coverage for, declared as quoted repo-relative
# paths so `suggest_mutation_coverage_command` can MAP them. The mapper reads
# textual references, and these tests build their paths from a variable
# (`_SCRIPTS / "x.py"`), which matches none of its patterns -- so the changed-line
# coverage gate reported these files unmapped and then blocked on lines this suite
# actually covers. Declaring the mapping is better than making the loader uglier to
# be greppable.
_COVERS = (
    "skills/public/issue/scripts/issue_consolidated_closeout.py",
    "skills/public/issue/scripts/issue_closeout_classification_ledger.py",
    "skills/public/issue/scripts/issue_verify_closeout_body.py",
)



def evaluate(text, **kwargs):
    """Always pass the ledger: the claim set is DERIVED from it, not hand-listed."""
    kwargs.setdefault("ledger", _Ledger)
    return consolidated["evaluate"](text, **kwargs)
missing_ledger_fields = runpy.run_path(str(_SCRIPTS / "issue_verify_closeout_body.py"))[
    "_missing_ledger_fields"
]
KNOWN_CLASSIFICATIONS = runpy.run_path(str(_SCRIPTS / "audit_brief.py"))["KNOWN_CLASSIFICATIONS"]
# The rung-1 floors and their classification gates moved out of the body reader when
# it hit its length gate; the body module now owns field parsing only.
FLOOR_EXEMPT = runpy.run_path(str(_SCRIPTS / "issue_closeout_rung1_floors.py"))[
    "FLOOR_EXEMPT_CLASSIFICATIONS"
]

_GOOD = "Classification: consolidated\nJtbd: fold the prompt-surface cluster\nConsolidated into: #600\n"


# --- the classification's place in the two sets ------------------------------


def test_consolidated_is_a_known_classification() -> None:
    assert "consolidated" in KNOWN_CLASSIFICATIONS


def test_consolidated_is_NOT_floor_exempt() -> None:
    """It swaps the resolution floor for its own; it does not escape one.

    If it were exempt, relabelling an inconvenient bug `consolidated` would reach
    the light floor by changing one word — which is the whole reason the exempt
    classifications were rejected for this job.
    """
    assert "consolidated" not in FLOOR_EXEMPT


# --- what it requires ---------------------------------------------------------


def test_a_well_formed_consolidated_close_passes():
    assert evaluate(_GOOD)["ok"] is True
    assert evaluate(_GOOD)["destinations"] == [600]
    assert missing_ledger_fields(_GOOD, "consolidated") == []


def test_a_close_that_names_no_destination_is_refused() -> None:
    """A consolidation with no destination is a close that says nothing at all."""
    report = evaluate("Jtbd: tidy the backlog\n")
    assert report["ok"] is False
    assert "Consolidated into" in report["problems"][0]


def test_the_destination_field_has_exactly_one_owner() -> None:
    """Presence is reported once, not once per owner.

    The requirements list and this module both used to own the field, so a missing
    destination reported twice. Two owners of one rule is how they drift.
    """
    missing = missing_ledger_fields("Jtbd: x\n", "consolidated")
    assert len([m for m in missing if "Consolidated into" in m or m == "consolidated_into"]) == 1
    assert missing == ["consolidated_into"]


def test_two_destinations_are_refused() -> None:
    """An issue that went to two places has no single owner, and neither
    destination can be checked for it."""
    report = evaluate("Consolidated into: #600 and #601\n")
    assert report["ok"] is False
    assert report["destinations"] == [600, 601]
    assert "exactly one destination" in report["problems"][0]


def test_a_self_reference_is_refused() -> None:
    report = evaluate("Consolidated into: #555\n", self_number=555)
    assert report["ok"] is False
    assert "evaporates the work" in report["problems"][0]


def test_the_field_tolerates_the_decoration_carriers_actually_use() -> None:
    for line in (
        "Consolidated into: #600",
        "- Consolidated into: #600",
        "- **Consolidated into:** #600",
        "  * `Consolidated into`: #600",
        "consolidated into: #600",
    ):
        assert evaluate(line + "\n")["destinations"] == [600], line


def test_an_anchor_is_not_matched_inside_a_longer_number() -> None:
    assert evaluate("Consolidated into: #6001\n")["destinations"] == [6001]


# --- what it refuses: the laundering path -------------------------------------


def test_a_carrier_that_claims_a_repair_is_refused() -> None:
    """The load-bearing refusal. Allowing both readings is how cheap closes get
    bought at the price of what a close MEANS in this repo."""
    for field in (
        "Implementation: rewrote the resolver",
        "Resolution brief: what we delivered",
        "Prevention: a new gate",
        "Behavior #600: verified against the hosted run",
        # A probe record ASSERTS the repair was measured, which is the one thing a
        # consolidated close -- a move, not a fix -- may not say.
        "Probe record #600: charness-artifacts/probe/x.md",
    ):
        report = evaluate(_GOOD + field + "\n")
        assert report["ok"] is False, field
        assert "claims nothing about the defect" in report["problems"][-1], field


def test_the_refusal_names_every_claim_it_found() -> None:
    report = evaluate(_GOOD + "Implementation: x\nPrevention: y\n")
    assert set(report["repair_claims"]) == {"implementation", "prevention"}


def test_a_body_merely_MENTIONING_a_repair_word_is_not_a_claim() -> None:
    """Only a FIELD is a claim; prose is not, or the refusal would fire on any
    close that explains why it is not a repair."""
    report = evaluate(
        _GOOD + "The destination issue will decide the implementation and prevention.\n"
    )
    assert report["ok"] is True


# --- what it deliberately does NOT check --------------------------------------


def test_backend_facts_are_named_as_unchecked_rather_than_asserted() -> None:
    """Asserting a tracker fact from the body would be the false-verdict shape
    this whole lane exists to remove, so the report says what it did not check."""
    unchecked = " ".join(evaluate(_GOOD)["not_checked_here"])
    for fact in ("is OPEN at close time", "contains this issue's number", "no chains"):
        assert fact in unchecked
    assert evaluate(_GOOD)["required_close_reason"] == "not planned"


def test_the_resolution_floors_are_unchanged_for_other_classifications() -> None:
    """Adding a branch must not loosen the branch beside it."""
    assert missing_ledger_fields("Jtbd: x\n", "bug") == [
        "root_cause",
        "debug_artifact",
        "siblings",
        "prevention",
    ]
    assert missing_ledger_fields("Jtbd: x\n", "feature") == [
        "boundary",
        "resolution_brief",
        "implementation",
        "prevention",
    ]


# --- round-1 repairs: the classification must actually be REACHABLE -----------

VERIFY = runpy.run_path(str(_SCRIPTS / "issue_verify_closeout.py"))


def test_consolidated_is_accepted_by_the_carrier_that_actually_runs() -> None:
    """A classification absent from the verifier's tuple is not a sixth
    classification -- it is a RuntimeError.

    Bounded review found `consolidated` added to `KNOWN_CLASSIFICATIONS` and the
    ledger table while every live carrier still refused it, so the only path that
    worked was the commit hook inferring `bug` and demanding the very repair claims
    this disposition exists to forbid.
    """
    assert "consolidated" in VERIFY["CLASSIFICATIONS"]


def test_the_commit_message_reader_recognizes_it_rather_than_inferring_bug() -> None:
    """The stale alternation did not fail loudly; it fell through to a `bug` default."""
    check = runpy.run_path(
        str(Path(__file__).resolve().parents[2] / "scripts/gates/check_issue_closeout_commit_msg.py")
    )
    match = check["_CLASSIFICATION_RE"].search("Classification: consolidated\n")
    assert match is not None
    assert match.group("classification") == "consolidated"


# --- round-1 repairs: the refusals that were unwired or evadable --------------


def test_the_self_reference_check_fires_on_the_WIRED_path() -> None:
    """It previously passed `self_number=None`, so it only worked in a direct call."""
    body = "Closes #555\n\nJtbd: fold it\nConsolidated into: #555\n"
    problems = missing_ledger_fields(body, "consolidated")
    assert any("same carrier is closing" in p for p in problems)


def test_a_public_fix_keyword_is_a_repair_claim() -> None:
    """GitHub renders `Fixes #N` on the issue timeline. A consolidation must use the
    neutral `Closes`, or the tracker asserts the repair the body refuses."""
    body = "Fixes #555\n\nJtbd: x\nConsolidated into: #600\n"
    assert any("claims nothing about the defect" in p for p in missing_ledger_fields(body, "consolidated"))
    neutral = "Closes #555\n\nJtbd: x\nConsolidated into: #600\n"
    assert missing_ledger_fields(neutral, "consolidated") == []


def test_colon_form_repair_keywords_are_claims_too() -> None:
    """GitHub's colon spelling must have the same consolidated verdict."""
    for keyword in ("Fixes: #555", "Resolves: #555"):
        body = f"{keyword}\n\nJtbd: x\nConsolidated into: #600\n"
        assert any("claims nothing about the defect" in p for p in missing_ledger_fields(body, "consolidated")), keyword

    neutral = "Closes: #555\n\nJtbd: x\nConsolidated into: #600\n"
    assert missing_ledger_fields(neutral, "consolidated") == []


def test_a_multi_anchor_behavior_line_cannot_evade_the_refusal() -> None:
    """The first grammar required `#\\d+` immediately before the colon, so
    `Behavior #600, #601:` slipped past it while matching the real floor's grammar."""
    body = "Closes #555\n\nJtbd: x\nConsolidated into: #600\nBehavior #600, #601: verified\n"
    assert any("claims nothing" in p for p in missing_ledger_fields(body, "consolidated"))


def test_the_claim_set_is_about_asserting_a_REPAIR_not_about_floor_membership() -> None:
    """Two revisions got this wrong in opposite directions.

    A hand-list under-refused; deriving from the whole resolution rows over-refused,
    because `Root cause:`, `Siblings:` and `Boundary:` are diagnostic or scoping — an
    unfixed issue can carry all three. Only an assertion that something was BUILT is
    a repair claim.
    """
    for claiming in ("Implementation: x", "Prevention: y", "Resolution brief: z"):
        body = f"Closes #555\n\nJtbd: x\nConsolidated into: #600\n{claiming}\n"
        assert any("claims nothing" in p for p in missing_ledger_fields(body, "consolidated")), claiming


def test_fenced_content_neither_satisfies_nor_refuses() -> None:
    """Every other body reader in this package strips fences; this one did not."""
    fenced_dest = "Closes #555\n\nJtbd: x\n\n```\nConsolidated into: #600\n```\n"
    assert "consolidated_into" in missing_ledger_fields(fenced_dest, "consolidated")

    pasted_log = "Closes #555\n\nJtbd: x\nConsolidated into: #600\n\n```\nImplementation: from a log\n```\n"
    assert missing_ledger_fields(pasted_log, "consolidated") == []


def test_a_second_destination_field_is_a_contradiction_not_an_ignored_line() -> None:
    """`.search` read only the first field, so the arity rule's own case passed."""
    body = "Closes #555\n\nJtbd: x\nConsolidated into: #600\nConsolidated into: #700\n"
    assert any("exactly one destination" in p for p in missing_ledger_fields(body, "consolidated"))


# --- round-1 repairs: legibility and immutability -----------------------------


def test_a_consolidated_close_prints_the_review_advisory() -> None:
    """It skips one MORE floor than `question` does; printing nothing made it
    strictly stealthier than the classifications it was designed to avoid."""
    body_mod = runpy.run_path(str(_SCRIPTS / "issue_closeout_rung1_floors.py"))
    advisory = body_mod["review_advisory_for_classification"]("consolidated")
    assert advisory and "AI-provenance" in advisory[0]
    assert body_mod["review_advisory_for_classification"]("bug") == []


def test_the_requirements_row_cannot_be_mutated_by_a_caller() -> None:
    """It is a proof surface's floor; handing out the live list lets one append
    reshape four classifications at once."""
    ledger = runpy.run_path(str(_SCRIPTS / "issue_closeout_classification_ledger.py"))
    row = ledger["classification_requirements"]("question")
    row.append(("injected", ("injected",)))
    assert ledger["classification_requirements"]("question") != row


# --- round-2 repairs ----------------------------------------------------------


def test_an_auto_closing_carrier_is_refused_because_github_renders_completed() -> None:
    """The close-reason floor was only half real: `issue_close` enforces it, but the
    PRIMARY path is GitHub auto-closing from a keyword, where no reason argv exists.
    Refusing `Fixes`/`Resolves` was not enough — the neutral `Closes` the module
    recommends produces the same public `completed` event."""
    body = "Closes #555\n\nJtbd: x\nConsolidated into: #600\n"
    for carrier in ("direct-commit", "pr-body"):
        problems = missing_ledger_fields(body, "consolidated", carrier=carrier)
        assert any("auto-closes" in p for p in problems), carrier
        assert any("close-with-comment" in p for p in problems), carrier
    assert missing_ledger_fields(body, "consolidated", carrier="manual-fallback") == []


def test_colon_form_neutral_keyword_is_still_an_auto_close() -> None:
    body = "Closes: #555\n\nJtbd: x\nConsolidated into: #600\n"
    problems = missing_ledger_fields(body, "consolidated", carrier="direct-commit")
    assert any("auto-closes" in problem for problem in problems)


def test_a_present_field_naming_no_anchor_is_refused() -> None:
    """The seam between the two owners: the row checks a substantive STRING and the
    module was told to stay silent about absence, so `Consolidated into: the umbrella
    issue` satisfied both and the one required fact went unrequired."""
    body = "Closes #555\n\nJtbd: x\nConsolidated into: the umbrella issue\n"
    assert any("names no issue anchor" in p for p in missing_ledger_fields(body, "consolidated"))


def test_the_self_reference_check_covers_every_issue_the_carrier_closes() -> None:
    """One carrier closing twenty issues into an umbrella is the intended shape, and
    comparing only the first number let the destination be one of the other nineteen."""
    body = "Closes #100, #119\n\nJtbd: x\nConsolidated into: #119\n"
    assert any("same carrier is closing" in p for p in missing_ledger_fields(body, "consolidated"))


def test_manual_carrier_uses_its_invoked_number_for_self_reference() -> None:
    """Manual close comments have no useful close keyword to infer this identity."""
    body = "Jtbd: x\nConsolidated into: #119\n"
    problems = missing_ledger_fields(
        body, "consolidated", carrier="manual-fallback", invoked_numbers=(119,)
    )
    assert any("same carrier is closing" in problem for problem in problems)


def test_a_fenced_fix_keyword_is_still_a_claim() -> None:
    """Fence stripping is right for FIELD reads and wrong for the close keyword:
    GitHub parses raw commit text and treats backticks as literal, so a fenced
    `Fixes #N` still auto-closes with a public "fixed" event."""
    body = "Closes #555\n\nJtbd: x\nConsolidated into: #600\n\n```\nFixes #555\n```\n"
    assert any("claims nothing" in p for p in missing_ledger_fields(body, "consolidated"))


def test_diagnostic_and_scoping_fields_are_not_repair_claims() -> None:
    """Deriving the claim set from the whole resolution rows over-refused.
    Consolidating a cluster IS a sibling-search operation, so naming the siblings is
    the most natural sentence an honest consolidation writes."""
    for field in ("Siblings: #601 same class, moving here", "Root cause: unknown", "Boundary: x"):
        body = f"Closes #555\n\nJtbd: x\nConsolidated into: #600\n{field}\n"
        assert missing_ledger_fields(body, "consolidated") == [], field


def test_the_line_grammar_claims_are_actually_reachable() -> None:
    """`HOTL #N:` and `Critique #N:` carry a target before the colon, so no plain
    field pattern could see them — while a comment asserted they were covered."""
    for field in ("HOTL #600: verified", "Critique #600: a/b.md", "Behavior #600, #601: ok"):
        body = f"Closes #555\n\nJtbd: x\nConsolidated into: #600\n{field}\n"
        assert any("claims nothing" in p for p in missing_ledger_fields(body, "consolidated")), field


def test_close_with_comment_refuses_a_consolidated_close_with_the_wrong_reason(tmp_path) -> None:
    """The reason floor must REFUSE, not silently correct.

    A caller that asked for `completed` on a consolidation has a contradiction to
    resolve, not a default to inherit — and the refusal has to raise before any
    backend call, or a closing comment posts publicly with no close behind it.
    """
    import pytest

    close_mod = runpy.run_path(str(_SCRIPTS / "issue_close.py"))
    body = tmp_path / "body.md"
    body.write_text("Closes #555\n\nJtbd: x\nConsolidated into: #600\n", encoding="utf-8")

    with pytest.raises(RuntimeError) as excinfo:
        close_mod["close_with_comment"](
            repo="o/r",
            number=555,
            body_file=body,
            repo_root=tmp_path,
            classification="consolidated",
            reason="completed",
        )
    message = str(excinfo.value)
    assert "not planned" in message
    assert "claims nothing about the defect" in message


def test_the_reason_floor_does_not_touch_other_classifications(tmp_path) -> None:
    """It must refuse on the reason, not on the file — so a `bug` close with the
    default reason gets past this check and fails later for its own reasons."""
    import pytest

    close_mod = runpy.run_path(str(_SCRIPTS / "issue_close.py"))
    missing = tmp_path / "absent.md"

    with pytest.raises(RuntimeError) as excinfo:
        close_mod["close_with_comment"](
            repo="o/r",
            number=555,
            body_file=missing,
            repo_root=tmp_path,
            classification="bug",
            reason="completed",
        )
    assert "body file not found" in str(excinfo.value)
