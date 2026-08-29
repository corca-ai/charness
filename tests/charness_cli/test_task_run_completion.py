"""The terminal `next_step` branches owned by `scripts/task_run_completion.py`.

`complete_task` takes every collaborator as a parameter, so the three-way
`next_step` split can be driven directly instead of through a real Codex lane.
The middle branch -- a candidate that is useful but NOT approval-eligible -- was
the one an operator would read after a partial lane, and it had never run.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts import task_run_completion


def _complete(tmp_path: Path, *, result_state: str, scope_verdict: str = "pass") -> dict[str, Any]:
    target = tmp_path / "worktree"
    target.mkdir()
    evidence = {"populations": {}}
    scope = {"verdict": scope_verdict, "reason": "scope drifted"}
    parent_progress = {"blocking": False, "classification": "no-parent-progress"}

    return task_run_completion.complete_task(
        {"task_id": "lane-1"},
        runtime_path=tmp_path / "runtime",
        resolved_target=target,
        resolved_repo=tmp_path / "repo",
        before_exec={},
        base_sha="0" * 40,
        scope_specs=[],
        require_change=False,
        parent_before={},
        parent_before_head="0" * 40,
        stdout_log=tmp_path / "stdout.log",
        execution={},
        started_at=0.0,
        persist=lambda _payload, _path: None,
        result_delivery=lambda _log: {"status": "delivered"},
        completion_evidence=lambda **_kwargs: (evidence, scope, parent_progress),
        execution_state=lambda _execution, _delivery: "completed",
        candidate_result_state=lambda **_kwargs: ({"status": result_state}, result_state),
        git=lambda *_args, **_kwargs: SimpleNamespace(returncode=1),
        git_output=lambda *_args, **_kwargs: "abc123\n",
        pass_value="pass",
    )


def test_a_validated_partial_result_is_named_useful_but_not_approval_eligible(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(tmp_path, result_state="validated-partial-result")

    assert payload["next_step"].endswith("it is useful but not approval-eligible.")
    assert payload["approval_eligibility"] == "ineligible"
    capsys.readouterr()


def test_a_completed_candidate_is_named_approval_eligible(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(tmp_path, result_state="completed")

    assert payload["next_step"].endswith("the typed result is approval-eligible.")
    assert payload["approval_eligibility"] == "eligible"
    capsys.readouterr()


def test_a_blocked_scope_names_the_blocker_instead_of_a_review_invitation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(tmp_path, result_state="completed", scope_verdict="fail")

    assert payload["next_step"] == (
        "Inspect the retained worktree, typed result, and captured logs; scope drifted."
    )
    capsys.readouterr()
