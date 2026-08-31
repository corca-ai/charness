"""Shared committed repository seed for worktree CLI tests."""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.seed_cache import get_or_build

_SEED_NAME = "charness-cli-worktree-repo-seed"


def _build_worktree_seed(seed_root: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    install_committed_repo(
        seed_root / "repo",
        {"README.md": "seed\n"},
        message="seed",
        branch="main",
    )


def copy_worktree_seed(tmp_path: Path, name: str) -> Path:
    """Copy the immutable source-bound seed into a private test repository."""
    repo = tmp_path / name
    seed = get_or_build(_SEED_NAME, _build_worktree_seed)
    shutil.copytree(seed / "repo", repo)
    return repo
