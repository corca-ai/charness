"""The terminal `next_step` branches owned by `scripts/task_run/task_run_completion.py`.

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

from scripts.task_run import task_run_completion


def _complete(
    tmp_path: Path,
    *,
    result_state: str,
    scope_verdict: str = "pass",
    candidate: dict[str, Any] | None = None,
    changed_line_gate: Any = None,
    execution_state: str = "completed",
) -> dict[str, Any]:
    target = tmp_path / "worktree"
    target.mkdir(exist_ok=True)
    evidence = {"populations": {}}
    scope = {"verdict": scope_verdict, "reason": "scope drifted"}
    parent_progress = {"blocking": False, "classification": "no-parent-progress"}
    resolved_candidate = candidate if candidate is not None else {"status": result_state}

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
        execution_state=lambda _execution, _delivery: execution_state,
        candidate_result_state=lambda **_kwargs: (resolved_candidate, result_state),
        candidate_commit=None,
        git=lambda *_args, **_kwargs: SimpleNamespace(returncode=1),
        git_output=lambda *_args, **_kwargs: "abc123\n",
        pass_value="pass",
        changed_line_gate=changed_line_gate,
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


def test_without_a_gate_the_receipt_says_the_gate_was_not_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(tmp_path, result_state="completed")

    assert payload["changed_line_gate"]["status"] == "not-run"
    assert payload["changed_line_gate"]["blocking"] is False
    assert payload["status"] == "completed"
    capsys.readouterr()


def test_a_changed_line_refusal_demotes_a_completed_lane_and_names_the_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[dict[str, Any]] = []

    def refusing_gate(worktree: Path, *, base_sha: str, log_dir: Path) -> dict[str, Any]:
        calls.append({"worktree": worktree, "base_sha": base_sha, "log_dir": log_dir})
        return {
            "status": "blocked",
            "blocking": True,
            "blocking_detail": {"scripts/x.py": {"changed_and_missing": [7]}},
            "summary": "changed-line gate blocked (exit 1): scripts/x.py lines 7",
        }

    payload = _complete(
        tmp_path,
        result_state="completed",
        candidate={"status": "validated", "useful": True},
        changed_line_gate=refusing_gate,
    )

    assert calls == [
        {"worktree": tmp_path / "worktree", "base_sha": "0" * 40, "log_dir": tmp_path}
    ]
    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["blocking_detail"] == {
        "scripts/x.py": {"changed_and_missing": [7]}
    }
    assert payload["next_step"] == (
        "Inspect the retained worktree, typed result, and captured logs; "
        "changed-line gate blocked (exit 1): scripts/x.py lines 7."
    )
    capsys.readouterr()


def test_the_gate_is_skipped_when_there_is_no_validated_candidate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def exploding_gate(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise AssertionError("the gate must not run for an absent candidate")

    payload = _complete(
        tmp_path,
        result_state="completed",
        candidate={"status": "absent", "useful": False},
        changed_line_gate=exploding_gate,
    )

    assert payload["changed_line_gate"]["status"] == "skipped"
    assert "no validated candidate" in payload["changed_line_gate"]["reason"]
    assert payload["status"] == "completed"
    capsys.readouterr()
