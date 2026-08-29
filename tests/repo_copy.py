from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REPO_COPY_EXCLUDE_NAMES = (
    ".git",
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

#: The Cargo target directory is 1.4 GB on a built checkout -- 87% of everything the
#: seed carries -- and all but 3.8 MB of it is build intermediates (`target/debug` at
#: 1.1 GB, `target/release/deps` at 230 MB) that no test reads.
#:
#: The binary itself CANNOT be dropped with them. `native_gate_lib.resolve_native_core`
#: prefers the dev tree, and a copy that has `native/repograph/Cargo.toml` but no built
#: binary makes it run `cargo build` INSIDE the test copy, which is far worse than the
#: copy it saved. So the rule keeps exactly `target/release/repograph` and drops the
#: rest, path-anchored rather than by basename: `deps`, `build`, and `debug` are ordinary
#: directory names elsewhere in a tree, and an `ignore_patterns` on those names would
#: silently delete unrelated directories from the fixture.
_NATIVE_TARGET = "native/repograph/target"
_NATIVE_BINARY_NAME = "repograph"


def repo_copy_ignore_for(source_root: Path):
    """Build the copytree `ignore` callable for a copy rooted at `source_root`."""

    resolved_root = source_root.resolve()

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set(REPO_COPY_IGNORE(directory, names))
        try:
            relative = Path(directory).resolve().relative_to(resolved_root).as_posix()
        except ValueError:
            return ignored
        if relative == _NATIVE_TARGET:
            ignored.update(name for name in names if name != "release")
        elif relative == f"{_NATIVE_TARGET}/release":
            ignored.update(name for name in names if name != _NATIVE_BINARY_NAME)
        return ignored

    return ignore


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
    # symlinks=True to mirror `cp -a`: the tree contains a deliberately
    # dangling symlink fixture (native/repograph/fixtures/links), and a
    # following copy raises ENOENT the moment the cp fast path fails.
    shutil.copytree(source, destination, symlinks=True)


def _git_init_and_commit(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
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
        shutil.copytree(ROOT, staging / "repo", ignore=repo_copy_ignore_for(ROOT), symlinks=True)

    return get_or_build("charness-repo-seed", build) / "repo"


@pytest.fixture(scope="session")
def seeded_charness_git_repo(
    seeded_charness_repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    from tests.seed_cache import get_or_build

    def build(staging: Path) -> None:
        seed = staging / "repo"
        shutil.copytree(seeded_charness_repo, seed, symlinks=True)
        _git_init_and_commit(seed)

    return get_or_build("charness-git-repo-seed", build) / "repo"


def clone_seeded_charness_repo(target_root: Path, seeded_repo: Path) -> Path:
    repo = target_root / "repo"
    _clone_tree(seeded_repo, repo)
    return repo
