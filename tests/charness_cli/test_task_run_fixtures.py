"""Shared subprocess and temporary-repository fixtures for task-run scenarios."""

from __future__ import annotations

import os
import shutil
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


def _build_repo_seed(seed_root: Path, *, ignored: bool) -> None:
    repo = seed_root / "repo"
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


def _repo_seed(*, ignored: bool) -> Path:
    from tests.seed_cache import get_or_build

    name = "task-run-ignored-repo-seed" if ignored else "task-run-repo-seed"
    return get_or_build(
        name,
        lambda seed_root: _build_repo_seed(seed_root, ignored=ignored),
    ) / "repo"


def _repo(tmp_path: Path, *, ignored: bool = False) -> Path:
    repo = tmp_path / "parent"
    shutil.copytree(_repo_seed(ignored=ignored), repo)
    return repo


def _commit(repo: Path, message: str, *paths: str) -> str:
    _git(repo, "add", "--", *paths)
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _codex(tmp_path: Path, body: str, *, deliver: bool = True) -> Path:
    executable = tmp_path / "codex"
    delivery = "printf 'task complete\\n'" if deliver else ""
    executable.write_text(f"#!/bin/sh\n{body}\n{delivery}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def _run(repo: Path, tmp_path: Path, executable: Path, **kwargs):
    scopes = kwargs.pop("scopes", ["module.py"])
    require_change = kwargs.pop("require_change", True)
    effort = kwargs.pop("effort", "medium")
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/task-run",
        base="HEAD",
        scopes=scopes,
        prompt="update the module",
        codex=os.fspath(executable),
        effort=effort,
        require_change=require_change,
        **kwargs,
    )
