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

from scripts.task_run import task_run_completion, task_run_git
from tests.quality_gates.repo_shapes import install_committed_repo


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
        f"Inspect the retained candidate in {tmp_path / 'worktree'}, typed result, "
        "and captured logs; scope drifted."
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
        f"Inspect the retained candidate in {tmp_path / 'worktree'}, typed result, "
        "and captured logs; changed-line gate blocked (exit 1): scripts/x.py lines 7."
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


# --- release_finished_lane (#787) ------------------------------------------------


def _released(tmp_path: Path, *, candidate: dict[str, Any], status: str = "completed", git=None, runtime: bool = True):
    record = tmp_path / "record"
    record.mkdir(parents=True, exist_ok=True)
    if runtime:
        (record / "runtime").mkdir(exist_ok=True)
        (record / "runtime" / "x").write_text("x", encoding="utf-8")
    (record / "codex.stdout.log").write_text("", encoding="utf-8")
    payload = {"status": status, "candidate": candidate, "target_branch": "task/lane", "target_sha": "abc"}
    return task_run_completion.release_finished_lane(
        payload,
        resolved_repo=tmp_path / "repo",
        resolved_target=tmp_path / "worktree",
        record_dir=record,
        git=git or (lambda *_a, **_k: SimpleNamespace(returncode=0, stderr="")),
    ), record


def test_only_a_completed_commit_only_lane_is_released(tmp_path: Path) -> None:
    complete = {"carrier_kind": "commit-only", "head_is_complete": True}
    partial, _ = _released(tmp_path, candidate=complete, status="validated-partial-result")
    assert partial is not None and partial["worktree"] == "removed"
    retained, _ = _released(tmp_path, candidate={"carrier_kind": "worktree-only", "head_is_complete": False})
    assert retained["worktree"] == "retained" and "keep_worktree stays true" in retained["reason"]
    released, record = _released(tmp_path, candidate=complete)
    assert released == {
        "worktree": "removed",
        "runtime": "removed",
        "carrier": "task/lane@abc",
        "kept": ["result.json", "codex.stdout.log"],
    }
    assert not (record / "runtime").exists()


def test_a_failed_worktree_removal_retains_with_the_git_error(tmp_path: Path) -> None:
    complete = {"carrier_kind": "commit-only", "head_is_complete": True}
    failing = lambda *_a, **_k: SimpleNamespace(returncode=128, stderr="fatal: locked")  # noqa: E731
    retained, record = _released(tmp_path, candidate=complete, git=failing)
    assert retained["worktree"] == "retained"
    assert "fatal: locked" in retained["reason"]
    assert (record / "runtime").is_dir()


def test_persist_incomplete_candidate_commits_dirty_and_untracked(tmp_path: Path) -> None:
    worktree = install_committed_repo(tmp_path / "lane", {"module.py": "VALUE = 1\n"})
    (worktree / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    (worktree / "new.py").write_text("NEW = 1\n", encoding="utf-8")

    snapshot = task_run_completion.persist_incomplete_candidate(
        worktree,
        git=task_run_git._git,
        git_output=task_run_git._git_output,
    )

    assert snapshot["status"] == "committed"
    assert snapshot["message"] == task_run_git.PERSIST_CANDIDATE_COMMIT_MESSAGE
    show = task_run_git._git_output(worktree, "show", f"{snapshot['sha']}:new.py")
    assert show == "NEW = 1\n"
    porcelain = task_run_git._git_output(worktree, "status", "--porcelain")
    assert porcelain.strip() == ""


def test_a_committed_persist_marks_head_complete_when_carrier_refresh_fails(
    tmp_path: Path, monkeypatch
) -> None:
    worktree = install_committed_repo(tmp_path / "lane", {"module.py": "VALUE = 1\n"})
    (worktree / "module.py").write_text("VALUE = 2\n", encoding="utf-8")

    def boom(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise task_run_completion.TaskRunError("carrier refresh failed")

    def _git_without_worktree_remove(cwd: Path, *args: str) -> Any:
        if args[:2] == ("worktree", "remove"):
            return SimpleNamespace(returncode=128, stderr="not a linked worktree")
        return task_run_git._git(cwd, *args)

    monkeypatch.setattr(task_run_completion, "_candidate_carrier", boom)
    payload = task_run_completion.complete_task(
        {"task_id": "lane-1", "target_branch": "lane/task-run"},
        runtime_path=tmp_path / "runtime",
        resolved_target=worktree,
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
        completion_evidence=lambda **_kwargs: (
            {"populations": {}},
            {"verdict": "pass", "reason": ""},
            {"blocking": False, "classification": "no-parent-progress"},
        ),
        execution_state=lambda _execution, _delivery: "completed",
        candidate_result_state=lambda **_kwargs: (
            {
                "status": "validated",
                "useful": True,
                "head_is_complete": False,
                "carrier_kind": "worktree-only",
            },
            "completed",
        ),
        candidate_commit=None,
        git=_git_without_worktree_remove,
        git_output=task_run_git._git_output,
        pass_value="pass",
    )

    assert payload["candidate"]["persist"]["status"] == "committed"
    assert payload["candidate"]["head_is_complete"] is True
    assert payload["candidate"]["carrier_kind"] == "commit-only"
    assert "no lane commit exists" not in payload["next_step"]


def test_a_failed_runtime_removal_and_an_absent_runtime_are_both_named(tmp_path: Path, monkeypatch) -> None:
    complete = {"carrier_kind": "commit-only", "head_is_complete": True}

    def refuse(_path: Path) -> None:
        raise OSError("busy")

    monkeypatch.setattr(task_run_completion, "_rmtree_writable", refuse)
    failed, _ = _released(tmp_path, candidate=complete)
    assert failed["worktree"] == "removed" and failed["runtime"] == "retained"
    assert "busy" in failed["reason"]
    absent, _ = _released(tmp_path / "absent", candidate=complete, runtime=False)
    assert absent["runtime"] == "absent"
