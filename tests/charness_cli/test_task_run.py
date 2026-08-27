from __future__ import annotations

import os
import subprocess
from pathlib import Path

from scripts import task_run


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path, *, ignored: bool = False) -> Path:
    repo = tmp_path / "parent"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    (repo / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    if ignored:
        (repo / ".gitignore").write_text("ignored-output.txt\n", encoding="utf-8")
        _git(repo, "add", "module.py", ".gitignore")
    else:
        _git(repo, "add", "module.py")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "seed",
    )
    return repo


def _codex(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "fake-codex"
    executable.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def _run(repo: Path, tmp_path: Path, executable: Path, **kwargs):
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/task-run",
        base="HEAD",
        scopes=["module.py"],
        prompt="update the module",
        codex=str(executable),
        require_change=True,
        **kwargs,
    )


def test_task_run_creates_named_lane_and_keeps_runtime_external(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["base_sha"] == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert payload["target_branch"] == "lane/task-run"
    assert payload["scope"]["disallowed_paths"] == []
    assert payload["parent"]["unchanged"] is True
    assert Path(payload["runtime_root"]).is_absolute()
    assert not Path(payload["runtime_root"]).is_relative_to(repo)
    assert not Path(payload["runtime_root"]).is_relative_to(payload["worktree_path"])
    assert (tmp_path / "lane" / "module.py").read_text(encoding="utf-8") == "VALUE = 2\n"


def test_task_run_reports_ignored_output_without_blocking_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path, ignored=True)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'diagnostic\\n' > ignored-output.txt",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["populations"]["untracked"]["verdict"] == "pass"
    assert payload["populations"]["ignored"]["verdict"] == "warn"
    assert payload["generated_files"][0]["population"] == "ignored"
    assert payload["warnings"]


def test_task_run_blocks_new_untracked_output_and_retains_lane(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'leak\\n' > leak.txt",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "failed"
    assert payload["scope"]["disallowed_paths"] == ["leak.txt"]
    assert "outside the exact declared scope" in payload["next_step"]
    assert (tmp_path / "lane" / "leak.txt").is_file()
    assert payload["parent"]["unchanged"] is True


def test_task_run_allows_new_scoped_candidate_file(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'def test_value(): pass\\n' > test_module.py",
    )

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/new-file",
        base="HEAD",
        scopes=["module.py", "test_module.py"],
        prompt="add the focused test",
        codex=str(executable),
        require_change=True,
    )

    assert payload["status"] == "completed", payload
    assert payload["scope"]["disallowed_paths"] == []
    assert payload["populations"]["untracked"]["verdict"] == "pass"
    assert payload["generated_files"] == [
        {
            "population": "untracked",
            "path": "test_module.py",
            "classification": "candidate",
            "cause": "new candidate path is within the exact declared scope",
        }
    ]


def test_task_run_refuses_dirty_parent_before_worktree_creation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "module.py").write_text("dirty\n", encoding="utf-8")
    executable = _codex(tmp_path, "exit 99")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "fail"
    assert "parent worktree must be clean" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_task_run_dry_run_has_no_worktree_or_runtime_side_effect(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 99")

    payload = _run(repo, tmp_path, executable, dry_run=True)

    assert payload["status"] == "pass"
    assert payload["dry_run"] is True
    assert not (tmp_path / "lane").exists()
    assert not Path(payload["runtime_root"]).exists()


def test_task_run_cli_accepts_repo_root_after_subcommand(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 3\\n' > module.py")
    result = subprocess.run(
        [
            os.fspath(Path(__file__).resolve().parents[2] / "charness"),
            "task",
            "run",
            "--repo-root",
            str(repo),
            "--path",
            str(tmp_path / "lane"),
            "--branch",
            "lane/cli",
            "--base",
            "HEAD",
            "--scope",
            "module.py",
            "--prompt",
            "noop",
            "--codex",
            str(executable),
        ],
        cwd=repo,
        env={**os.environ, "PYTHONPYCACHEPREFIX": str(tmp_path / "launcher-pycache")},
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "status: completed" in result.stdout
    assert (tmp_path / "lane" / "module.py").read_text(encoding="utf-8") == "VALUE = 3\n"


def test_task_status_reads_the_external_result_store(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 4\\n' > module.py")
    payload = _run(repo, tmp_path, executable, task_id="status-check")

    result_path = Path(payload["runtime_root"]) / "task-run" / "status-check" / "result.json"
    assert result_path.is_file()
    status = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[2] / "charness"), "task", "--repo-root", str(repo), "status", "status-check"],
        cwd=repo, check=False, capture_output=True, text=True,
    )
    assert status.returncode == 0
    assert "status: completed" in status.stdout
