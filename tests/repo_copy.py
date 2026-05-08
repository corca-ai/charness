from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REPO_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".charness",
    ".venv",
    "node_modules",
    "history",
)


def _git_init_and_commit(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Codex Test"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "seed repo copy"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def seeded_charness_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    seed_root = tmp_path_factory.mktemp("charness-repo-seed")
    seed = seed_root / "repo"
    shutil.copytree(ROOT, seed, ignore=REPO_COPY_IGNORE)
    return seed


@pytest.fixture(scope="session")
def seeded_charness_git_repo(
    seeded_charness_repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    seed_root = tmp_path_factory.mktemp("charness-git-repo-seed")
    seed = seed_root / "repo"
    shutil.copytree(seeded_charness_repo, seed)
    _git_init_and_commit(seed)
    return seed


def clone_seeded_charness_repo(target_root: Path, seeded_repo: Path) -> Path:
    repo = target_root / "repo"
    shutil.copytree(seeded_repo, repo)
    return repo
