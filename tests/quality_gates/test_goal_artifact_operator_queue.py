from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_OPERATOR_QUEUE = (
    Path(__file__).resolve().parents[2]
    / "skills/public/achieve/scripts/goal_artifact_operator_queue.py"
)
_spec = importlib.util.spec_from_file_location("goal_artifact_operator_queue", _OPERATOR_QUEUE)
oq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oq)


def test_operator_queue_loader_fails_when_grammar_helper_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(oq.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)

    with pytest.raises(ImportError, match="goal_artifact_floor_grammar.py not found"):
        oq._load_floor_grammar()


def test_operator_queue_invalid_created_date_still_applies() -> None:
    assert oq.applies("Created: 2026-99-99\n") is True


def test_operator_queue_created_swap_is_a_tested_behavior_change() -> None:
    """S2 divergence-preservation proof: the strict->permissive Created-parse swap
    is a DELIBERATE behavior change, not a no-op. The old strict parser ignored a
    prefixed/list/lowercase `Created:` line (read None -> floor fired); the shared
    permissive parser now reads it and grandfathers a pre-rule goal. These inputs
    are exactly where strict and permissive diverge, so this pins the new behavior
    that the plain-form locked tests cannot see."""
    pre_rule = "2026-01-01"  # < RULE_DATE 2026-06-17
    for line in (f"> Created: {pre_rule}\n", f"- Created: {pre_rule}\n", f"created: {pre_rule}\n"):
        assert oq.applies(line) is False, line  # now grandfathered (strict would have fired)
    # Plain forms unchanged: pre-rule grandfathered, on/after rule date in scope.
    assert oq.applies(f"Created: {pre_rule}\n") is False
    assert oq.applies("Created: 2026-06-17\n") is True


def _names_target_shape(reason: str) -> bool:
    """A describe-first rejection names the satisfying forms, not just the violation."""
    return "none — <reason>" in reason and "Decision:" in reason


def test_operator_queue_blank_heading_body_fails() -> None:
    result = oq.check("Created: 2026-06-17\n\n## Operator Decision Queue")

    assert result["applies"] is True
    assert result["ok"] is False
    assert "blank" in result["reason"]
    assert _names_target_shape(result["reason"])  # describe-first: shows the target


def test_operator_queue_scaffold_body_fails_and_names_target() -> None:
    scaffold = (
        "Created: 2026-06-17\n\n## Operator Decision Queue\n\n"
        "Record decisions, confirmations, credential actions, manual proof steps,\n"
        "and external-boundary approvals.\n"
    )
    result = oq.check(scaffold)

    assert result["applies"] is True
    assert result["ok"] is False
    assert "scaffold" in result["reason"]
    assert _names_target_shape(result["reason"])  # describe-first: shows the target


def test_operator_queue_unrecognized_body_fails_with_actionable_reason() -> None:
    result = oq.check("Created: 2026-06-17\n\n## Operator Decision Queue\n\nNeeds follow-up.\n")

    assert result["applies"] is True
    assert result["ok"] is False
    assert _names_target_shape(result["reason"])  # describe-first: shows the target


def test_operator_queue_ignores_a_fenced_example_decision() -> None:
    """S16 (audit 2026-07-28): the section body was sliced out of the RAW text
    using offsets found on the fence-masked copy, so an illustrative
    `- Decision:` inside a code fence satisfied the floor as if the author had
    recorded a real operator decision."""
    text = (
        "Created: 2026-07-01\nStatus: complete\n\n## Operator Decision Queue\n\n"
        "```\n- Decision: this is only an EXAMPLE inside a fence\n```\n"
    )
    result = oq.check(text)

    assert result["applies"] is True
    assert result["ok"] is False
    assert _names_target_shape(result["reason"])


def test_operator_queue_control_real_decision_beside_a_fence_still_passes() -> None:
    """Control (false-refusal guard): a real `- Decision:` line still satisfies
    the floor even when the section also carries a fenced example."""
    text = (
        "Created: 2026-07-01\nStatus: complete\n\n## Operator Decision Queue\n\n"
        "```\n- Decision: illustrative shape only\n```\n\n"
        "- Decision: operator confirmed the production credential rotation\n"
    )
    result = oq.check(text)

    assert result["applies"] is True
    assert result["ok"] is True
    assert result["reason"] == "queue disposition recorded"


def test_operator_queue_out_of_scope_result_is_not_reported_as_a_pass() -> None:
    """S15 (audit 2026-07-28): a self-declared `Created:` line decides whether the
    complete-state floor runs at all, and the old out-of-scope result
    (`{'applies': False, 'ok': True, 'reason': 'pre-rule goal'}`) read like a
    satisfied floor. Grandfathering stays (the checked-in corpus is majority
    pre-rule), but the result must disclose that it never ran."""
    result = oq.check("Created: 2020-01-01\nStatus: complete\n")

    assert result["applies"] is False
    assert result["evaluated"] is False
    assert result["created"] == "2020-01-01"
    assert result["rule_date"] == oq.RULE_DATE.isoformat()
    assert "not evaluated" in result["reason"]
    assert "self-declared" in result["reason"]


def test_operator_queue_out_of_scope_control_stays_non_blocking() -> None:
    """Control: disclosure must not become a refusal — a grandfathered goal with
    no queue section still leaves the caller's report ok."""
    report = {"ok": True}
    oq.apply_operator_queue_floor(report, "Created: 2020-01-01\nStatus: complete\n")

    assert report["ok"] is True
    assert report["operator_decision_queue"]["applies"] is False
