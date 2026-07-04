"""D36 — the floor-exemption advisory has a single carrier-neutral owner in
``issue_verify_closeout_body`` and is re-exported through
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

# The exact string the close-with-comment carrier emitted before D36 moved the
# owner. This carrier calls the advisory with a classification only, so its
# output must not change.
_HISTORICAL_QUESTION_ADVISORY = (
    "REVIEW: classification 'question' exempts this close from the "
    "behavioral-verdict and resolution-critique floors (only source preservation still "
    "applies); confirm the classification is correct before treating this issue as "
    "resolved (advisory only, never blocks)."
)


def _load(name: str):
    path = _ISSUE_SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"d36_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_lives_in_body_module() -> None:
    body = _load("issue_verify_closeout_body")
    assert callable(body.review_advisory_for_classification)
    assert body.FLOOR_EXEMPT_CLASSIFICATIONS == ("question", "decision-needed")


def test_exempt_classification_surfaces_single_advisory() -> None:
    body = _load("issue_verify_closeout_body")
    for classification in ("question", "decision-needed"):
        lines = body.review_advisory_for_classification(classification)
        assert len(lines) == 1
        assert lines[0].startswith(f"REVIEW: classification '{classification}'")


def test_nonexempt_classification_surfaces_nothing() -> None:
    body = _load("issue_verify_closeout_body")
    for classification in ("bug", "feature", "deferred-work"):
        assert body.review_advisory_for_classification(classification) == []


def test_close_with_comment_call_form_is_byte_identical() -> None:
    # classification-only (numbers=None): the historical form the close-with-comment
    # carrier uses must not move a byte, so that carrier's output is unchanged.
    body = _load("issue_verify_closeout_body")
    assert body.review_advisory_for_classification("question") == [_HISTORICAL_QUESTION_ADVISORY]


def test_commit_msg_variant_names_numbers_and_staged_source() -> None:
    body = _load("issue_verify_closeout_body")
    lines = body.review_advisory_for_classification(
        "decision-needed", numbers=[42], source="charness-artifacts/issue/2026-07-04-x.md"
    )
    assert len(lines) == 1
    assert "#42" in lines[0]
    assert "charness-artifacts/issue/2026-07-04-x.md" in lines[0]


def test_commit_msg_variant_bare_keyword_uses_default_scope() -> None:
    body = _load("issue_verify_closeout_body")
    lines = body.review_advisory_for_classification("question", numbers=[10, 11], source=None)
    assert len(lines) == 1
    assert "#10, #11" in lines[0]
    assert "commit-message close keyword" in lines[0]


def test_both_carriers_reexport_the_owner_with_identical_output() -> None:
    # Single owner: the advisory name is present on both re-export surfaces
    # (wiring works) and all three produce identical output for the same input,
    # so there is no duplicated advisory body that could drift between carriers.
    # (runpy/importlib load each module file fresh, so assert output-equivalence
    # rather than object identity across the independently-loaded instances.)
    body = _load("issue_verify_closeout_body")
    verify = _load("issue_verify_closeout")
    floor = _load("issue_close_comment_floor")
    for classification in ("question", "decision-needed", "bug"):
        expected = body.review_advisory_for_classification(classification, numbers=[7], source=None)
        assert verify.review_advisory_for_classification(classification, numbers=[7], source=None) == expected
        assert floor.review_advisory_for_classification(classification, numbers=[7], source=None) == expected
    assert verify.FLOOR_EXEMPT_CLASSIFICATIONS == body.FLOOR_EXEMPT_CLASSIFICATIONS
