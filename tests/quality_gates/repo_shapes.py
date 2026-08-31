"""Frozen checkout shapes for tests.

A test that needs a Git story installs a named shape by copy. Git runs once
when the seed is built, not once per test. Unique tails (an extra dirty file,
a second commit, a remote) still speak Git; the shared prefix does not.
"""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Mapping
from pathlib import Path

from tests.seed_cache import get_or_build


def _file_digest(files: Mapping[str, str], *, message: str, branch: str, author_date: str | None) -> str:
    digest = hashlib.sha256()
    digest.update(branch.encode())
    digest.update(b"\0")
    digest.update(message.encode())
    digest.update(b"\0")
    digest.update((author_date or "").encode())
    digest.update(b"\0")
    for relative in sorted(files):
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(files[relative].encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:20]


def _committed_seed(
    files: Mapping[str, str],
    *,
    message: str,
    branch: str,
    author_date: str | None,
) -> Path:
    from tests.quality_gates.seeding_support import _install_empty_git_dir, git, write_text

    key = _file_digest(files, message=message, branch=branch, author_date=author_date)

    def build(seed_root: Path) -> None:
        repo = seed_root / "repo"
        repo.mkdir()
        _install_empty_git_dir(repo, branch=branch)
        for relative, contents in files.items():
            write_text(repo / relative, contents)
        extra: dict[str, str] = {}
        if author_date:
            extra["GIT_AUTHOR_DATE"] = author_date
            extra["GIT_COMMITTER_DATE"] = author_date
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message, env=extra or None)

    return get_or_build(f"shape-one-commit-{key}", build) / "repo"


def install_committed_repo(
    dest: Path,
    files: Mapping[str, str],
    *,
    message: str = "seed",
    branch: str = "main",
    author_date: str | None = None,
) -> Path:
    """Install a one-commit checkout with exactly ``files`` at HEAD.

    Same file set reuses one frozen seed. Test-time Git count is zero.
    """
    source = _committed_seed(files, message=message, branch=branch, author_date=author_date)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if any(dest.iterdir()):
            raise ValueError(f"refusing to install a checkout into a non-empty path: {dest}")
        dest.rmdir()
    shutil.copytree(source, dest)
    return dest
