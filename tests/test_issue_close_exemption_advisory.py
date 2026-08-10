"""D36 — the floor-exemption advisory has a single carrier-neutral owner in
``issue_closeout_rung1_floors`` and is re-exported through
``issue_verify_closeout`` / ``issue_close_comment_floor``.

Per-branch falsifiability: the exempt arm surfaces exactly one advisory line, the
non-exempt arm surfaces none, the commit-msg ``numbers``/``source`` variant names
the close it applies to, and the historical ``close-with-comment`` call form
(classification only) stays byte-identical so that carrier's output does not move.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_ISSUE_SCRIPTS = _ROOT / "skills" / "public" / "issue" / "scripts"

# The exact string the close-with-comment carrier emits. This carrier calls the
# advisory with a classification only, so its output must not drift by accident.
#
# It DID move once, deliberately: the tail used to read "(only source preservation
# still applies)", which stopped being true when the AI-provenance and HOTL floors lost
# their classification gate and began applying to every classification. Byte-stability
# guards against accidental drift, not against correcting an advisory that misreports
# which floors ran.
_QUESTION_ADVISORY = (
    "REVIEW: classification 'question' exempts this close from the "
    "behavioral-verdict and resolution-critique floors (source preservation, "
    "AI-provenance and HOTL disposition still apply); confirm the classification is "
    "correct before treating this issue as resolved (advisory only, never blocks)."
)


def _load(name: str):
    path = _ISSUE_SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"advisory_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_lives_in_the_rung1_floor_module() -> None:
    floors = _load("issue_closeout_rung1_floors")
    assert callable(floors.review_advisory_for_classification)
    assert floors.FLOOR_EXEMPT_CLASSIFICATIONS == ("question", "decision-needed")


def test_exempt_classification_surfaces_single_advisory() -> None:
    floors = _load("issue_closeout_rung1_floors")
    for classification in ("question", "decision-needed"):
        lines = floors.review_advisory_for_classification(classification)
        assert len(lines) == 1
        assert lines[0].startswith(f"REVIEW: classification '{classification}'")


def test_nonexempt_classification_surfaces_nothing() -> None:
    floors = _load("issue_closeout_rung1_floors")
    for classification in ("bug", "feature", "deferred-work"):
        assert floors.review_advisory_for_classification(classification) == []


def test_close_with_comment_call_form_is_byte_identical() -> None:
    # classification-only (numbers=None): the historical form the close-with-comment
    # carrier uses must not move a byte, so that carrier's output is unchanged.
    floors = _load("issue_closeout_rung1_floors")
    assert floors.review_advisory_for_classification("question") == [_QUESTION_ADVISORY]


def test_commit_msg_variant_names_numbers_and_staged_source() -> None:
    floors = _load("issue_closeout_rung1_floors")
    lines = floors.review_advisory_for_classification(
        "decision-needed", numbers=[42], source="charness-artifacts/issue/2026-07-04-x.md"
    )
    assert len(lines) == 1
    assert "#42" in lines[0]
    assert "charness-artifacts/issue/2026-07-04-x.md" in lines[0]


def test_commit_msg_variant_bare_keyword_uses_default_scope() -> None:
    floors = _load("issue_closeout_rung1_floors")
    lines = floors.review_advisory_for_classification("question", numbers=[10, 11], source=None)
    assert len(lines) == 1
    assert "#10, #11" in lines[0]
    assert "commit-message close keyword" in lines[0]


def test_both_carriers_reexport_the_owner_with_identical_output() -> None:
    # Single owner: the advisory name is present on both re-export surfaces
    # (wiring works) and all three produce identical output for the same input,
    # so there is no duplicated advisory body that could drift between carriers.
    # (runpy/importlib load each module file fresh, so assert output-equivalence
    # rather than object identity across the independently-loaded instances.)
    floors = _load("issue_closeout_rung1_floors")
    verify = _load("issue_verify_closeout")
    floor = _load("issue_close_comment_floor")
    for classification in ("question", "decision-needed", "bug"):
        expected = floors.review_advisory_for_classification(classification, numbers=[7], source=None)
        assert verify.review_advisory_for_classification(classification, numbers=[7], source=None) == expected
        assert floor.review_advisory_for_classification(classification, numbers=[7], source=None) == expected
    assert verify.FLOOR_EXEMPT_CLASSIFICATIONS == floors.FLOOR_EXEMPT_CLASSIFICATIONS


# `consolidated` renders a SECOND, separately-worded branch. The sentence the slice
# just repaired ("only source preservation still applies") went false on the question
# branch; nothing pinned the consolidated one, so the same drift could recur there
# with every test green.
_CONSOLIDATED_ADVISORY = (
    "REVIEW: classification 'consolidated' skips the behavioral-verdict and "
    "resolution-critique floors, and refuses a HOTL entry outright as a repair claim "
    "(source preservation and AI-provenance still apply, and it owes its own "
    "`Consolidated into:` destination floor instead); confirm the classification is "
    "correct before treating this issue as resolved (advisory only, never blocks)."
)


def test_consolidated_branch_is_byte_pinned_too() -> None:
    floors = _load("issue_closeout_rung1_floors")
    lines = floors.review_advisory_for_classification("consolidated")
    assert lines == [_CONSOLIDATED_ADVISORY]
