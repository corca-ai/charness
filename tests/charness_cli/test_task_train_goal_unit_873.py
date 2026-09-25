from __future__ import annotations

import argparse
from pathlib import Path

import pytest

import scripts.cli.cmd_goal as cmd_goal
import scripts.cli.cmd_task as cmd_task
import scripts.cli.cmd_train as cmd_train
import scripts.cli.cmd_worktree as cmd_worktree
from scripts.cli import bootstrap as _bootstrap


def test_cmd_train_stats_invalid_window_raises(tmp_path: Path) -> None:
    args = argparse.Namespace(window="bogus!!", profile=None)
    with pytest.raises(cmd_train.CharnessError):
        cmd_train.cmd_train_stats(args, tmp_path)


def test_project_runtime_response_release_and_staleness() -> None:
    payload = {
        "checkout": {"repo_root": "/r", "pulled": True, "extra": "drop"},
        "latest_release_check": {"status": "ok", "latest_tag": "v1"},
        "session_staleness": {"status": "s", "message": "m", "affected": ["a"]},
    }
    response = cmd_task.project_runtime_response(payload, event="update")
    assert response["latest_release_check"] == {"status": "ok", "latest_tag": "v1"}
    assert response["session_staleness"]["affected_count"] == 1
    assert response["checkout"] == {"repo_root": "/r", "pulled": True}


def test_cmd_task_run_prompt_file_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cmd_task, "_load_task_run_lib", lambda args: object())
    args = argparse.Namespace(
        detach=False,
        prompt="hi",
        prompt_file=tmp_path / "missing.txt",
        repo_root=tmp_path,
    )
    with pytest.raises(cmd_task.CharnessError, match="could not read"):
        cmd_task.cmd_task_run(args)


class _AuditLib:
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

    def __init__(self, audit_status: str, prune_status: str = "pass") -> None:
        self.audit_status = audit_status
        self.prune_status = prune_status

    def run_audit(self, target, **kwargs):
        return {"status": self.audit_status}

    def run_prune(self, target):
        return {"status": self.prune_status, "remaining_after_prune": {}}


def _audit_args(prune: bool) -> argparse.Namespace:
    return argparse.Namespace(stale_days=7, doctor=False, prune=prune)


def test_cmd_worktree_audit_warn_branch(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(cmd_worktree, "_load_worktree_audit_lib", lambda args: _AuditLib("warn"))
    monkeypatch.setattr(cmd_worktree, "_resolve_worktree_target", lambda args: tmp_path)
    assert cmd_worktree.cmd_worktree_audit(_audit_args(False)) == 1


def test_cmd_worktree_audit_else_and_prune_failure(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(cmd_worktree, "_load_worktree_audit_lib", lambda args: _AuditLib("fail"))
    monkeypatch.setattr(cmd_worktree, "_resolve_worktree_target", lambda args: tmp_path)
    assert cmd_worktree.cmd_worktree_audit(_audit_args(False)) == 2
    monkeypatch.setattr(
        cmd_worktree,
        "_load_worktree_audit_lib",
        lambda args: _AuditLib("pass", prune_status="fail"),
    )
    assert cmd_worktree.cmd_worktree_audit(_audit_args(True)) == 2


def test_cmd_worktree_create_warn_branch(monkeypatch, tmp_path: Path, capsys) -> None:
    class _CreateLib:
        PASS = "pass"
        WARN = "warn"

        def run_create(self, target, **kwargs):
            return {"status": "warn"}

    monkeypatch.setattr(cmd_worktree, "_load_worktree_create_lib", lambda args: _CreateLib())
    monkeypatch.setattr(cmd_worktree, "_resolve_worktree_target", lambda args: tmp_path)
    args = argparse.Namespace(
        path=None,
        branch=None,
        base=None,
        detach=False,
        prepare=False,
        dry_run=False,
        force=False,
        ephemeral=False,
        owned=False,
    )
    assert cmd_worktree.cmd_worktree_create(args) == 1


def _helper_checkout(root: Path) -> Path:
    helper = root / "skills" / "public" / "achieve" / "scripts" / "goal_run_pickup.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("# helper\n", encoding="utf-8")
    return root


def test_resolve_goal_helper_checkout_branch(monkeypatch, tmp_path: Path) -> None:
    checkout = _helper_checkout(tmp_path / "checkout")
    monkeypatch.setattr(cmd_goal, "ensure_checkout", lambda *a, **k: None)
    args = argparse.Namespace(charness_checkout=checkout, home_root=tmp_path)
    assert cmd_goal._resolve_goal_run_helper_repo_root(args) == checkout


def test_resolve_goal_helper_embedded_branch(monkeypatch, tmp_path: Path) -> None:
    embedded = _helper_checkout(tmp_path / "embedded")
    monkeypatch.setattr(cmd_goal, "ensure_checkout", lambda *a, **k: None)
    monkeypatch.setattr(_bootstrap, "EMBEDDED_REPO_ROOT", embedded)
    try:
        args = argparse.Namespace(charness_checkout=None, home_root=tmp_path)
        assert cmd_goal._resolve_goal_run_helper_repo_root(args) == embedded
    finally:
        monkeypatch.undo()


def test_resolve_goal_helper_else_branch(monkeypatch, tmp_path: Path) -> None:
    managed = _helper_checkout(tmp_path / "managed")
    monkeypatch.setattr(cmd_goal, "ensure_checkout", lambda *a, **k: None)
    monkeypatch.setattr(_bootstrap, "EMBEDDED_REPO_ROOT", None)
    monkeypatch.setattr(cmd_goal, "resolve_repo_root", lambda home, target: (managed, True))
    args = argparse.Namespace(
        charness_checkout=None, home_root=tmp_path, repo_url="https://example.test/r"
    )
    assert cmd_goal._resolve_goal_run_helper_repo_root(args) == managed


def test_goal_run_script_args_shapes(tmp_path: Path) -> None:
    args = argparse.Namespace(objective="/goal #1")
    assert cmd_goal._goal_run_script_args(args, tmp_path) == [
        "--repo-root",
        str(tmp_path),
        "--objective",
        "/goal #1",
    ]


def test_cmd_goal_run_malformed_helper_payload(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(cmd_goal, "_resolve_goal_run_helper_repo_root", lambda args: tmp_path)
    monkeypatch.setattr(cmd_goal, "resolve_repo_python", lambda root: "python3")
    emitted: dict[str, object] = {}

    class _Result:
        stdout = "{unclosed: [}"
        stderr = ""
        returncode = 0

    monkeypatch.setattr(cmd_goal, "run", lambda argv, cwd: _Result())
    monkeypatch.setattr(cmd_goal, "emit_yaml", lambda payload: emitted.update(payload))
    args = argparse.Namespace(objective="/goal #1", repo_root=tmp_path)
    assert cmd_goal.cmd_goal_run(args) == 0
    assert emitted == {"helper_stdout": "{unclosed: [}"}
