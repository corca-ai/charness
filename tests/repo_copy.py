from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REPO_COPY_EXCLUDE_NAMES = (
    ".git",
    ".cautilus",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".charness",
    "charness-artifacts",
    ".venv",
    "node_modules",
    "reports",
    "history",
)
REPO_COPY_IGNORE = shutil.ignore_patterns(*REPO_COPY_EXCLUDE_NAMES)


def _clone_tree(source: Path, destination: Path) -> None:
    try:
        subprocess.run(
            ["cp", "-a", "--reflink=auto", str(source), str(destination)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return
    except (OSError, subprocess.SubprocessError):
        pass
    shutil.copytree(source, destination)


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
    from tests.seed_cache import get_or_build

    def build(staging: Path) -> None:
        shutil.copytree(ROOT, staging / "repo", ignore=REPO_COPY_IGNORE)

    return get_or_build("charness-repo-seed", build) / "repo"


@pytest.fixture(scope="session")
def seeded_charness_git_repo(
    seeded_charness_repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    from tests.seed_cache import get_or_build

    def build(staging: Path) -> None:
        seed = staging / "repo"
        shutil.copytree(seeded_charness_repo, seed)
        _git_init_and_commit(seed)

    return get_or_build("charness-git-repo-seed", build) / "repo"


def clone_seeded_charness_repo(target_root: Path, seeded_repo: Path) -> Path:
    repo = target_root / "repo"
    _clone_tree(seeded_repo, repo)
    return repo
