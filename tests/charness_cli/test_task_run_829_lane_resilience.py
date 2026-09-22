"""Lane resilience for task runs (#829).

A transient model-stream stall must retry in the same worktree with every
attempt recorded; every receipt must name its typed failure; a finished
lane whose gates cannot approve must read as needs-review (merge, not
relaunch); watched lanes must publish a cheap live snapshot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.task_run import task_run_attempts as attempts
from scripts.task_run import task_run_git, task_run_scope
from scripts.task_run import task_run_progress as prog
from scripts.task_run import task_run_state as state
from tests.charness_cli.test_task_run_fixtures import _repo

IDLE_LINE = "agent loop failed: model failed: model stream idle timeout after 180000ms"


def test_classify_failure_names_idle_stall_retryable() -> None:
    failure = state.classify_failure(
        {"exit_code": 1, "timed_out": False, "interrupted": False},
        stderr_text=f"\n   \nreads\n{IDLE_LINE}\n",
        delivery={"status": "non-delivery"},
    )
    assert failure["kind"] == "model-stream-idle"
    assert failure["retryable"] is True
    assert "idle" in failure["message"]


def test_bare_loop_failure_fails_fast_without_retry() -> None:
    failure = state.classify_failure(
        {"exit_code": 1, "timed_out": False, "interrupted": False},
        stderr_text="agent loop failed: bad auth\n",
        delivery={"status": "non-delivery"},
    )
    assert failure["kind"] == "executor-error"
    assert failure["retryable"] is False
    idle_loop = state.classify_failure(
        {"exit_code": 1, "timed_out": False, "interrupted": False},
        stderr_text="agent loop failed: idle timeout after 180s\n",
        delivery={"status": "non-delivery"},
    )
    assert idle_loop["kind"] == "model-stream-idle"
    assert idle_loop["retryable"] is True


def test_classify_failure_kinds_cover_timeout_interrupt_executor_delivery() -> None:
    assert state.classify_failure({"timed_out": True}, stderr_text="")["kind"] == "timed-out"
    assert (
        state.classify_failure({"interrupted": True}, stderr_text="")["kind"] == "interrupted"
    )
    assert (
        state.classify_failure({"exec_error": "boom"}, stderr_text="")["kind"]
        == "executor-error"
    )
    assert (
        state.classify_failure(
            {"exit_code": 0, "timed_out": False, "interrupted": False},
            stderr_text="",
            delivery={"status": "non-delivery"},
        )["kind"]
        == "delivery-failed"
    )
    assert (
        state.classify_failure(
            {"exit_code": 0, "timed_out": False, "interrupted": False},
            stderr_text="",
            delivery={"status": "delivered"},
        )["kind"]
        == "none"
    )


def test_classify_failure_survives_sparse_inputs() -> None:
    assert state.classify_failure({}, stderr_text="")["kind"] == "executor-error"
    assert state.classify_failure({}, stderr_text="", delivery=None)["kind"] == "executor-error"
    assert (
        state.classify_failure({"exit_code": -9}, stderr_text="")["kind"] == "interrupted"
    )
    assert (
        state.classify_failure(
            {"exit_code": 0, "timed_out": False, "interrupted": False},
            stderr_text="",
            delivery={"status": "delivered", "delivery_error": "short read"},
        )["kind"]
        == "delivery-failed"
    )


def test_review_reasons_name_parent_progress() -> None:
    assert state.review_reasons(
        scope={"disallowed_paths": []}, parent_progress={"blocking": True}
    ) == ["parent-progress"]


def test_needs_review_next_step_names_merge_not_relaunch(tmp_path: Path) -> None:
    from scripts.task_run.task_run_completion_next_step import _next_step

    assert "relaunch" in _next_step(
        {"target_branch": "lane/x", "target_sha": "abc"},
        resolved_target=tmp_path,
        candidate={"head_is_complete": True},
        execution_status="completed",
        result_state="completed-needs-review",
        blockers=[],
    )


def test_finished_out_of_scope_lane_needs_review_not_failed() -> None:
    scope = {
        "verdict": "disallowed",
        "changed_paths": ["module.py"],
        "disallowed_paths": ["helper.py"],
        "candidate_carrier": {},
    }
    candidate, result_state = state._candidate_result_state(
        execution_state="completed",
        scope=scope,
        parent_progress={"blocking": False},
    )
    assert result_state == state.NEEDS_REVIEW_STATE == "completed-needs-review"
    assert candidate["disallowed_paths"] == ["helper.py"]
    assert state.review_reasons(scope=scope, parent_progress={"blocking": False}) == [
        "out-of-scope-paths"
    ]


def test_clean_completed_lane_is_unchanged() -> None:
    scope = {
        "verdict": "pass",
        "changed_paths": ["module.py"],
        "disallowed_paths": [],
        "candidate_carrier": {},
    }
    _, result_state = state._candidate_result_state(
        execution_state="completed",
        scope=scope,
        parent_progress={"blocking": False},
    )
    assert result_state == "completed"


def _lane_args(tmp_path: Path) -> dict[str, Any]:
    repo = _repo(tmp_path)
    base_sha = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    return {
        "lane_prompt": "Do the work.",
        "resolved_target": repo,
        "configured_env": {},
        "stdout_log": tmp_path / "muse.stdout.log",
        "stderr_log": tmp_path / "muse.stderr.log",
        "timeout_seconds": 60,
        "require_change": False,
        "base_sha": base_sha,
        "scope_specs": specs,
    }


def test_idle_stall_retries_in_place_with_attempts_recorded(
    tmp_path: Path, monkeypatch: Any
) -> None:
    monkeypatch.setenv(attempts.MAX_ATTEMPTS_ENV, "3")
    monkeypatch.setenv(attempts.RETRY_BACKOFF_ENV, "0")
    calls: list[int] = []

    def fake_execute(
        command: Any, **kwargs: Any
    ) -> dict[str, Any]:
        calls.append(1)
        stderr_log = kwargs["stderr_log"]
        if len(calls) < 3:
            stderr_log.write_text(f"work\n{IDLE_LINE}\n", encoding="utf-8")
            return {"exit_code": 1, "timed_out": False, "interrupted": False}
        stderr_log.write_text("done\n", encoding="utf-8")
        return {"exit_code": 0, "timed_out": False, "interrupted": False}

    monkeypatch.setattr(attempts._execution, "_execute_codex", fake_execute)
    payload: dict[str, Any] = {}
    execution = attempts._execute_watched_lane(payload, ["muse", "exec"], **_lane_args(tmp_path))
    assert execution["exit_code"] == 0
    assert [entry["failure_kind"] for entry in payload["attempts"]] == [
        "model-stream-idle",
        "model-stream-idle",
        "none",
    ]
    assert [entry["retried"] for entry in payload["attempts"]] == [True, True, False]
    assert payload["attempts"][0]["logs"]
    assert len(calls) == 3
    assert (tmp_path / "muse.stderr.attempt1.log").exists()


def test_attempt_budget_falls_back_on_bad_env(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setenv(attempts.MAX_ATTEMPTS_ENV, "bogus")
    assert attempts._env_attempts(attempts.MAX_ATTEMPTS_ENV, 3) == 3
    monkeypatch.setenv(attempts.MAX_ATTEMPTS_ENV, "0")
    assert attempts._env_attempts(attempts.MAX_ATTEMPTS_ENV, 3) == 3


def test_rotate_logs_survives_rename_failures(tmp_path: Path, monkeypatch: Any) -> None:
    log = tmp_path / "muse.stderr.log"
    log.write_text("x\n", encoding="utf-8")

    def refuse(self: Path, target: Path) -> None:
        raise OSError("busy")

    monkeypatch.setattr(Path, "rename", refuse)
    assert attempts._rotate_attempt_logs(tmp_path / "missing.stdout.log", log, 1) == {}


def _run_bare_module(tmp_path: Path, rel: str, attr: str) -> None:
    """Import one lane script in a fresh interpreter with no repo root on sys.path."""
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[2]
    code = (
        "import runpy, sys; "
        "sys.path[:] = [p for p in sys.path if 'charness' not in p]; "
        f"m = runpy.run_path({str(root / rel)!r}); "
        f"assert {attr!r} in m, sorted(m)"
    )
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_standalone_lane_modules_import_without_repo_root_on_path(tmp_path: Path) -> None:
    _run_bare_module(tmp_path, "scripts/task_run/task_run_attempts.py", "MAX_ATTEMPTS_ENV")
    _run_bare_module(tmp_path, "scripts/task_run/task_run_retention.py", "release_finished_lane")


def test_non_retryable_failure_runs_once(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setenv(attempts.MAX_ATTEMPTS_ENV, "3")
    monkeypatch.setenv(attempts.RETRY_BACKOFF_ENV, "0")
    calls: list[int] = []

    def fake_execute(command: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append(1)
        return {"exit_code": 1, "timed_out": False, "interrupted": False}

    monkeypatch.setattr(attempts._execution, "_execute_codex", fake_execute)
    payload: dict[str, Any] = {}
    execution = attempts._execute_watched_lane(payload, ["muse", "exec"], **_lane_args(tmp_path))
    assert execution["exit_code"] == 1
    assert len(payload["attempts"]) == 1
    assert payload["attempts"][0]["failure_kind"] == "executor-error"
    assert payload["attempts"][0]["retried"] is False
    assert len(calls) == 1


def test_persist_live_writes_and_swallows_errors(tmp_path: Path, monkeypatch: Any) -> None:
    attempts._persist_live(None, {"task_id": "t"})
    payload = {"task_id": "live-1", "live": {"phase": None}}
    attempts._persist_live(tmp_path, payload)
    assert (tmp_path / "task-run" / "live-1" / "result.json").is_file()

    def refuse(_runtime_path: Path, _result: Any) -> Path:
        raise OSError("busy")

    monkeypatch.setattr(attempts._runtime, "write_task_result", refuse)
    attempts._persist_live(tmp_path, payload)


def test_snapshot_is_unknown_for_an_unobservable_worktree(tmp_path: Path) -> None:
    watch = prog.LaneProgressWatch(
        stdout_log=tmp_path / "muse.stdout.log",
        stderr_log=tmp_path / "muse.stderr.log",
        worktree=tmp_path / "missing",
        base_sha="0" * 40,
        scope_specs=[],
        budget_seconds=0.0,
        poll_seconds=15.0,
    )
    snapshot = watch.snapshot(5.0)
    assert snapshot["files_changed"] is None
    assert snapshot["files_changed"] is None
    assert snapshot["seconds_since_log_growth"] is None


def test_failed_observe_and_unreadable_logs_never_kill_the_watch(
    tmp_path: Path, monkeypatch: Any
) -> None:
    def _boom(_snapshot: dict[str, Any]) -> None:
        raise RuntimeError("observer down")

    repo = _repo(tmp_path)
    base_sha = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    watch = prog.LaneProgressWatch(
        stdout_log=tmp_path / "muse.stdout.log",
        stderr_log=tmp_path / "muse.stderr.log",
        worktree=repo,
        base_sha=base_sha,
        scope_specs=specs,
        budget_seconds=0.0,
        poll_seconds=15.0,
        observe=_boom,
    )
    assert watch.tick(1000.0) is None

    def _refuse_stat(self: Path) -> Any:
        raise OSError("unreadable")

    monkeypatch.setattr(Path, "stat", _refuse_stat)
    assert watch.tick(2000.0) is None


def test_watch_snapshot_reports_phase_and_worktree_truth(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    base_sha = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    seen: list[dict[str, Any]] = []
    watch = prog.LaneProgressWatch(
        stdout_log=tmp_path / "muse.stdout.log",
        stderr_log=tmp_path / "muse.stderr.log",
        worktree=repo,
        base_sha=base_sha,
        scope_specs=specs,
        budget_seconds=0.0,
        poll_seconds=15.0,
        observe=seen.append,
    )
    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    assert watch.tick(1000.0) is None
    snapshot = watch.snapshot(1000.0)
    assert snapshot["phase"] == "CONTRACT-READ"
    assert snapshot["files_changed"] == 0
    assert snapshot["commits"] == 0
    assert snapshot["last_commit_subject"] is None
    assert snapshot["seconds_since_log_growth"] == 0.0
    assert seen and seen[-1]["phase"] == "CONTRACT-READ"
