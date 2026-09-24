"""Changed-line probes for runtime, task-run, and pytest retention helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from scripts.gates_support import standing_pytest_basetemp as basetemp
from scripts.task_run import (
    task_run_completion_next_step,
    task_run_lane_runner,
    task_run_ledger,
    task_run_lesson_injection,
    task_run_payload,
    task_run_plan,
    task_run_test_cache,
)


def test_stale_entry_root_lstat_failure_keeps_unknown_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "unreadable"
    original = Path.lstat

    def fail_root(path: Path, *args: object, **kwargs: object):
        if path == root:
            raise OSError("entry disappeared")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", fail_root)
    assert basetemp.stale_entry_roots(root, 1.0) == []


def test_stale_entry_root_refuses_linked_worktree(tmp_path: Path) -> None:
    worktree = tmp_path / "linked"
    worktree.mkdir()
    (worktree / ".git").write_text("gitdir: ../main/.git/worktrees/linked", encoding="utf-8")

    assert basetemp.stale_entry_roots(worktree, 1.0) == []


def test_stale_entry_root_iterdir_failure_keeps_unreadable_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "unreadable-children"
    root.mkdir()
    original = Path.iterdir

    def fail_root(path: Path):
        if path == root:
            raise OSError("children unavailable")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", fail_root)
    assert basetemp.stale_entry_roots(root, 1.0) == []


def test_stale_entry_roots_return_oldest_complete_directory(tmp_path: Path) -> None:
    root = tmp_path / "root"
    stale = root / "old"
    stale.mkdir(parents=True)
    stale_stamp = 1.0
    stale_cutoff = 2.0
    os.utime(stale, (stale_stamp, stale_stamp))

    assert basetemp.stale_entry_roots(root, stale_cutoff) == [stale]


def test_idle_key_prune_returns_empty_when_run_glob_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = tmp_path / "pytest-tmp" / "key"
    key.mkdir(parents=True)
    original = Path.glob

    def fail_key(path: Path, pattern: str):
        if path == key:
            raise OSError("run list unavailable")
        return original(path, pattern)

    monkeypatch.setattr(Path, "glob", fail_key)
    assert basetemp._prune_idle_key_entries(key, 1.0) == []


def test_idle_key_prune_skips_non_directory_run_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = tmp_path / "pytest-tmp" / "key"
    key.mkdir(parents=True)
    run_match = key / "pytest-of-user" / "charness-run-1"
    run_match.parent.mkdir()
    run_match.write_text("not a run directory", encoding="utf-8")
    monkeypatch.setattr(Path, "glob", lambda path, _pattern: [run_match] if path == key else [])
    monkeypatch.setattr(basetemp, "stale_entry_roots", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        basetemp,
        "_basetemp_is_active",
        lambda _run: pytest.fail("a non-directory run must be skipped"),
    )

    assert basetemp._prune_idle_key_entries(key, 1.0) == []
    assert run_match.is_file()


def test_idle_key_prune_omits_tree_when_removal_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = tmp_path / "pytest-tmp" / "key"
    entry = key / "pytest-of-user" / "old"
    entry.mkdir(parents=True)
    monkeypatch.setattr(basetemp, "stale_entry_roots", lambda *_args, **_kwargs: [entry])
    monkeypatch.setattr(
        basetemp.shutil,
        "rmtree",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("busy")),
    )
    log: list[str] = []

    assert basetemp._prune_idle_key_entries(key, 1.0, log=log.append) == []
    assert entry.is_dir()
    assert log == []


def test_idle_key_prune_logs_successful_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = tmp_path / "pytest-tmp" / "key"
    entry = key / "pytest-of-user" / "old"
    entry.mkdir(parents=True)
    monkeypatch.setattr(basetemp, "stale_entry_roots", lambda *_args, **_kwargs: [entry])
    log: list[str] = []

    assert basetemp._prune_idle_key_entries(key, 1.0, log=log.append) == [entry]
    assert not entry.exists()
    assert log == [f"removed idle pytest temp entry {entry} (0 MiB)"]


@pytest.mark.parametrize(
    "module",
    [task_run_ledger, task_run_payload, task_run_lesson_injection, task_run_test_cache],
    ids=["ledger", "payload", "lesson-injection", "test-cache"],
)
def test_task_run_bootstrap_adds_repository_root(module, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "path", [])

    module._load_repo_runtime_bootstrap()

    repo_root = Path(module.__file__).resolve().parents[2]
    assert str(repo_root) in sys.path


def test_plan_rejects_nonpositive_lane_size_estimate() -> None:
    result = task_run_plan._lane_size_hygiene("Lane size: 0 minutes; 1 commit unit")

    assert result["status"] == "invalid"
    assert result["warning"] == "lane size estimates must use positive minutes and commit units."


def test_completion_timeout_without_commit_recommends_retained_worktree(
    tmp_path: Path,
) -> None:
    next_step = task_run_completion_next_step._next_step(
        {},
        resolved_target=tmp_path,
        candidate={"state": "incomplete", "state_known": True},
        execution_status="timed-out",
        result_state="timed-out",
        blockers=[],
    )

    assert next_step == (
        f"Inspect the retained worktree in {tmp_path}; candidate_state=incomplete; "
        "state_known=true; result_kind=unrecorded; approval_eligibility=unrecorded."
    )


def test_steer_queue_read_oserror_returns_empty_queue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    queue = tmp_path / "steer.queue.jsonl"
    original = Path.read_text

    def fail_queue(path: Path, *args: object, **kwargs: object):
        if path == queue:
            raise OSError("queue unavailable")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_queue)
    assert task_run_lane_runner.read_steer_queue(queue) == []


def test_steered_invocation_relaunches_in_place_without_session(tmp_path: Path) -> None:
    command = ["muse", "--prompt-file", str(tmp_path / "prompt.md")]
    messages = [{"message_id": "m-1", "queued_at": "now", "message": "Keep scope."}]

    actual_command, prompt, resume_path = task_run_lane_runner.steered_lane_invocation(
        "muse", command, "Original prompt.", messages, None
    )

    assert actual_command == command
    assert "Keep scope." in prompt
    assert resume_path == "relaunch-in-place"


def test_read_steer_queue_skips_malformed_lines(tmp_path: Path) -> None:
    import json

    queue = tmp_path / "steer.queue.jsonl"
    queue.write_text(
        "{not json\n"
        + json.dumps(
            {
                "kind": "charness.task_steer.v1",
                "message_id": "m-9",
                "task_id": "lane-9",
                "message": "Kept.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = task_run_lane_runner.read_steer_queue(queue)

    assert [record["message_id"] for record in records] == ["m-9"]


def test_steered_invocation_rewrites_prompt_file_for_muse_session(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Original prompt.", encoding="utf-8")
    command = ["muse", "--prompt-file", str(prompt_file)]
    messages = [{"message_id": "m-1", "queued_at": "now", "message": "Keep scope."}]

    actual_command, prompt, resume_path = task_run_lane_runner.steered_lane_invocation(
        "muse", command, "Original prompt.", messages, "session-9"
    )

    assert resume_path == "session-resume"
    assert actual_command == command
    assert prompt_file.read_text(encoding="utf-8") == prompt
    assert "Keep scope." in prompt


def test_friction_direct_execution_runs_bootstrap(tmp_path: Path) -> None:
    import subprocess

    repo = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/task_run/task_run_friction.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0


def test_idle_key_prune_protects_failed_run(tmp_path: Path) -> None:
    key = tmp_path / "pytest-tmp" / "key"
    run = key / "pytest-of-user" / "charness-run-1"
    run.mkdir(parents=True)
    (run / basetemp._FAILED_BASETEMP_MARKER).write_text("failed\n", encoding="utf-8")

    assert basetemp._prune_idle_key_entries(key, 1.0) == []
    assert run.is_dir()
