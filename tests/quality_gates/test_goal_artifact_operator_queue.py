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
