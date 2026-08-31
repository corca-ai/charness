"""Facts the checkout files already state.

Asking Git whether a directory is a repository, or which SHA HEAD names, has
no information value when ``.git`` already answers. Consumers project
discoverability, local layout, and HEAD from this owner.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

DISCOVERY_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")
# Index redirection is not repo discovery, but on-disk HEAD is no longer the
# default checkout Git would use.
FILE_HEAD_ENV = (*DISCOVERY_ENV, "GIT_INDEX_FILE")
_GIT_OID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def discovery_redirected(*, names: tuple[str, ...] = DISCOVERY_ENV) -> bool:
    return any(os.environ.get(name) for name in names)


def git_dir_at(repo_root: Path) -> Path | None:
    """Administration directory at ``repo_root/.git``, or None if absent/empty."""
    marker = repo_root / ".git"
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8")
        except OSError:
            return None
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("gitdir:"):
                git_dir = Path(stripped.split(":", 1)[1].strip())
                return git_dir if git_dir.is_absolute() else repo_root / git_dir
        return None
    if (
        marker.is_dir()
        and (marker / "HEAD").is_file()
        and ((marker / "objects").is_dir() or (marker / "commondir").is_file())
    ):
        return marker
    return None


def _is_bare(root: Path) -> bool:
    return (root / "HEAD").is_file() and (root / "objects").is_dir() and (root / "refs").is_dir()


def discoverable(repo_root: Path) -> bool:
    """Whether Git could discover a work-tree or bare repo from ``repo_root``."""
    if discovery_redirected():
        return True
    try:
        root = repo_root.resolve()
    except OSError:
        return False
    if not root.is_dir():
        return False
    if _is_bare(root):
        return True
    return any(git_dir_at(candidate) is not None for candidate in (root, *root.parents))


def local_checkout(repo_root: Path) -> bool:
    """Ordinary on-disk checkout at this root. Env redirect still belongs to Git."""
    return not discovery_redirected() and git_dir_at(repo_root) is not None


def head_oid_from_files(repo_root: Path) -> str | None:
    """HEAD object id from Git files when discovery is local."""
    if discovery_redirected(names=FILE_HEAD_ENV):
        return None
    git_dir = git_dir_at(repo_root)
    if git_dir is None:
        return None
    try:
        text = (git_dir / "HEAD").read_text(encoding="ascii").strip()
        if _GIT_OID_RE.fullmatch(text):
            return text
        if text.startswith("ref: "):
            sha = (git_dir / text[5:]).read_text(encoding="ascii").strip()
            if _GIT_OID_RE.fullmatch(sha):
                return sha
    except OSError:
        return None
    return None
