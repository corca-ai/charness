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


def _codex(tmp_path: Path, body: str, *, deliver: bool = True) -> Path:
    executable = tmp_path / "fake-codex"
    delivery = "printf 'task complete\\n'" if deliver else ""
    executable.write_text(f"#!/bin/sh\n{body}\n{delivery}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def _run(repo: Path, tmp_path: Path, executable: Path, **kwargs):
    scopes = kwargs.pop("scopes", ["module.py"])
    require_change = kwargs.pop("require_change", True)
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/task-run",
        base="HEAD",
        scopes=scopes,
        prompt="update the module",
        codex=str(executable),
        require_change=require_change,
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
    assert "outside the declared scope" in payload["next_step"]
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
            "cause": "new candidate path is within the declared scope",
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


def test_directory_scope_includes_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.py")
    _git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "add package")
    executable = _codex(tmp_path, "printf 'CHILD = 1\\n' > pkg/child.py")

    payload = _run(repo, tmp_path, executable, scopes=["pkg"])

    assert payload["status"] == "completed", payload
    assert payload["scope"]["specs"] == [{"path": "pkg", "kind": "directory"}]
    assert payload["scope"]["changed_paths"] == ["pkg/child.py"]


def test_absent_scope_remains_exact_when_command_creates_a_directory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "mkdir newdir\nprintf 'VALUE = 1\\n' > newdir/item.py")

    payload = _run(repo, tmp_path, executable, scopes=["newdir"])

    assert payload["status"] == "failed"
    assert payload["scope"]["specs"] == [{"path": "newdir", "kind": "exact"}]
    assert payload["scope"]["disallowed_paths"] == ["newdir/item.py"]


def test_disjoint_parent_progress_is_reported_without_failing_lane(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'parent\\n' > {repo / 'notes.txt'}",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["parent"]["progress"]["classification"] == "concurrent-parent-progress"
    assert payload["parent"]["progress"]["paths"] == ["notes.txt"]
    assert payload["parent"]["progress"]["overlap_paths"] == []
    assert "parent made disjoint progress" in payload["warnings"][-1]


def test_overlapping_parent_progress_is_a_writer_conflict(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'parent\\n' > {repo / 'module.py'}",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["parent"]["progress"]["classification"] == "writer-conflict"
    assert payload["parent"]["progress"]["overlap_paths"] == ["module.py"]


def test_parent_ignored_residue_is_not_writer_progress(tmp_path: Path) -> None:
    repo = _repo(tmp_path, ignored=True)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'cache\\n' > {repo / 'ignored-output.txt'}",
    )

    payload = _run(repo, tmp_path, executable)

    progress = payload["parent"]["progress"]
    assert payload["status"] == "completed", payload
    assert progress["classification"] == "normal"
    assert progress["ignored"]["added"] == ["ignored-output.txt"]


def test_timeout_with_scoped_candidate_is_validated_partial_result(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py\nsleep 5")

    payload = _run(repo, tmp_path, executable, timeout_seconds=1)

    assert payload["status"] == "validated-partial-result"
    assert payload["execution"]["status"] == "timed-out"
    assert payload["candidate"]["useful"] is True
    assert payload["approval_eligibility"] == "ineligible"


def test_non_delivery_with_scoped_candidate_is_validated_partial_result(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py", deliver=False)

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "validated-partial-result"
    assert payload["execution"]["status"] == "non-delivery"
    assert payload["result_delivery"]["bytes"] == 0


def test_running_result_is_visible_to_the_child(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "grep '\"status\": \"running\"' \"$CHARNESS_RUNTIME_ROOT/task-run/running-check/result.json\" > running.txt\nprintf 'VALUE = 2\\n' > module.py",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="running-check",
        scopes=["module.py", "running.txt"],
    )

    assert payload["status"] == "completed", payload
    assert (tmp_path / "lane/running.txt").read_text(encoding="utf-8").strip() == '"status": "running",'


def test_interruption_is_a_distinct_terminal_state(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")
    monkeypatch.setattr(
        task_run,
        "_execute_codex",
        lambda *_args, **_kwargs: {
            "exit_code": None,
            "timed_out": False,
            "interrupted": True,
        },
    )

    payload = _run(repo, tmp_path, executable, require_change=False)

    assert payload["status"] == "interrupted"
    assert payload["execution"]["status"] == "interrupted"
    assert payload["phase"] == "terminal"
