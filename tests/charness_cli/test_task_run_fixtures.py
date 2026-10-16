"""Shared subprocess and temporary-repository fixtures for task-run scenarios."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from scripts.task_run import task_run
from tests.quality_gates.repo_shapes import install_committed_repo


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path, *, ignored: bool = False) -> Path:
    files = {"module.py": "VALUE = 1\n"}
    if ignored:
        files[".gitignore"] = "ignored-output.txt\n"
    return install_committed_repo(tmp_path / "parent", files)


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


def _codex(
    tmp_path: Path,
    body: str,
    *,
    deliver: bool = True,
    last_message: str | None = None,
) -> Path:
    executable = tmp_path / "codex"
    report = (
        last_message
        if last_message is not None
        else "task complete\n" if deliver else None
    )
    output = ""
    if report is not None:
        output = (
            "if [ -n \"$output_path\" ]; then printf '%s' "
            f"{shlex.quote(report)} > \"$output_path\"; fi"
        )
    executable.write_text(
        "#!/bin/sh\n"
        "output_path=\n"
        "want_output_path=0\n"
        "for argument do\n"
        "  if [ \"$want_output_path\" = 1 ]; then output_path=$argument; want_output_path=0; "
        "elif [ \"$argument\" = '--output-last-message' ]; then want_output_path=1; fi\n"
        "done\n"
        f"{body}\n{output}\n",
        encoding="utf-8",
    )
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
