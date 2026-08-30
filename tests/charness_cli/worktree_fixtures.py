"""Shared committed repository seed for worktree CLI tests."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from tests.seed_cache import get_or_build

_SEED_NAME = "charness-cli-worktree-repo-seed"


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


def _build_worktree_seed(seed_root: Path) -> None:
    repo = seed_root / "repo"
    repo.mkdir()
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_EMAIL": "charness-tests@example.com",
            "GIT_AUTHOR_NAME": "Charness Tests",
            "GIT_COMMITTER_EMAIL": "charness-tests@example.com",
            "GIT_COMMITTER_NAME": "Charness Tests",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
    )
    _git(repo, "init", "--initial-branch=main", env=env)
    (repo / "README.md").write_bytes(b"seed\n")
    _git(repo, "add", "README.md", env=env)
    _git(repo, "commit", "-m", "seed", env=env)


def copy_worktree_seed(tmp_path: Path, name: str) -> Path:
    """Copy the immutable source-bound seed into a private test repository."""
    repo = tmp_path / name
    seed = get_or_build(_SEED_NAME, _build_worktree_seed)
    shutil.copytree(seed / "repo", repo)
    return repo
