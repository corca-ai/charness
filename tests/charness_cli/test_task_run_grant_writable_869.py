"""Per-lane writable grants for host-state dirs (#869)."""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run, task_run_lane_runner

from .test_task_run_fixtures import _codex, _repo


def _dry_run(repo: Path, tmp_path: Path, **kwargs) -> dict:
    executable = _codex(tmp_path, "exit 0")
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/grant-dry-run",
        base="HEAD",
        scopes=["module.py"],
        prompt="inspect the selected base",
        codex=str(executable),
        effort="medium",
        dry_run=True,
        **kwargs,
    )


def test_granted_dir_recorded_on_dry_run_receipt(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    granted = tmp_path / "host-state"
    granted.mkdir()

    payload = _dry_run(repo, tmp_path, grant_writable=[granted])

    assert payload["status"] == "pass", payload
    assert payload["granted_writable_dirs"] == [str(granted.resolve())]


def test_granted_dir_joins_codex_writable_dirs(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    granted = tmp_path / "host-state"
    granted.mkdir()
    payload = {"worktree_path": str(repo)}
    resolved = {
        "git_common_dir": repo,
        "granted_writable_dirs": [str(granted.resolve())],
    }

    writable = task_run_lane_runner.lane_writable_dirs(
        payload,
        resolved,
        repo,
        tmp_path / "runtime",
        executor="codex",
        worktree=repo,
    )

    assert str(granted.resolve()) in [str(path) for path in writable]
    assert payload["writable_dirs"] == [str(path) for path in writable]
    assert payload["granted_writable_dirs"] == [str(granted.resolve())]


def test_grant_reaches_the_codex_command(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    granted = tmp_path / "host-state"
    granted.mkdir()
    command = task_run_lane_runner.lane_command(
        executor="codex",
        executable="codex",
        effort="medium",
        prompt="inspect",
        execution_runtime_path=tmp_path / "runtime",
        writable_dirs=[granted],
        worktree=repo,
    )

    assert "--add-dir" in command
    assert str(granted) in command


def test_grant_covering_repo_root_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(repo, tmp_path, grant_writable=[repo])

    assert payload["status"] == "fail", payload
    assert "must not cover the repo root" in payload["error"]


def test_grant_covering_home_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(repo, tmp_path, grant_writable=[Path.home()])

    assert payload["status"] == "fail", payload
    assert "must not cover $HOME" in payload["error"]


def test_grant_of_slash_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(repo, tmp_path, grant_writable=["/"])

    assert payload["status"] == "fail", payload
    assert "must not grant /" in payload["error"]


def test_grant_with_muse_executor_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    granted = tmp_path / "host-state"
    granted.mkdir()

    payload = _dry_run(
        repo, tmp_path, grant_writable=[granted], executor="codex,muse"
    )

    assert payload["status"] == "fail", payload
    assert "--grant-writable needs the codex executor" in payload["error"]


def test_relative_grant_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(repo, tmp_path, grant_writable=["relative/dir"])

    assert payload["status"] == "fail", payload
    assert "must be an absolute directory" in payload["error"]


def test_grant_of_non_directory_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    afile = tmp_path / "not-a-dir.txt"
    afile.write_text("x", encoding="utf-8")

    payload = _dry_run(repo, tmp_path, grant_writable=[str(afile)])

    assert payload["status"] == "fail", payload
    assert "is not a directory" in payload["error"]


def test_fresh_exec_runs_lane_options_bootstrap_without_repo_root() -> None:
    import importlib.util
    import os
    import sys

    from scripts.task_run import task_run_lane_options
    from tests.module_eviction import evict_new_modules

    path = Path(task_run_lane_options.__file__)
    spec = importlib.util.spec_from_file_location("fresh_lane_options", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    saved = sys.path[:]
    root = str(path.resolve().parents[2])
    sys.path[:] = [entry for entry in saved if os.path.abspath(entry) != root]
    before = set(sys.modules)
    try:
        sys.modules["fresh_lane_options"] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
        evict_new_modules(before)
    assert module.resolve_granted_writable is not None


def test_grant_muse_refusal_without_executables(monkeypatch, tmp_path: Path) -> None:
    """Grant/executor refusal precedes PATH probing (#825).

    With no executor executable installed, --grant-writable with muse in the
    order must still report the grant refusal instead of a "not on PATH"
    error.
    """
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    repo = _repo(tmp_path)
    granted = tmp_path / "host-state"
    granted.mkdir()

    payload = _dry_run(
        repo, tmp_path, grant_writable=[granted], executor="codex,muse"
    )

    assert payload["status"] == "fail", payload
    assert "--grant-writable needs the codex executor" in payload["error"]
