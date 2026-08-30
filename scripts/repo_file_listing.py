#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
from pathlib import Path

try:
    from scripts.repo_layout import support_dir
except ModuleNotFoundError:
    from repo_layout import support_dir


class RepoFileListingError(SystemExit):
    pass


class GeneratedMirrorAbsentError(Exception):
    """The generated plugin mirror is not on disk, so its scope is unestablished."""


class RepoFileSnapshot:
    """One operation's coherent Git-backed file population.

    Callers that derive several views of the same tree pass this object through
    instead of paying for an identical ``git ls-files`` at every helper layer.
    The cache is deliberately explicit and operation-scoped: a later operation
    that may follow a mutation creates a new snapshot.
    """

    def __init__(self, repo_root: Path, *, require_git: bool = False) -> None:
        self.repo_root = repo_root.resolve()
        self.require_git = require_git
        self._paths: dict[bool, list[Path] | None] = {}

    def list_files(self, *, include_untracked: bool = True) -> list[Path] | None:
        if include_untracked not in self._paths:
            self._paths[include_untracked] = git_list_repo_files(
                self.repo_root,
                include_untracked=include_untracked,
                require_git=self.require_git,
            )
        return self._paths[include_untracked]


def _listing_snapshot(
    repo_root: Path,
    *,
    require_git: bool,
    snapshot: RepoFileSnapshot | None,
) -> RepoFileSnapshot:
    if snapshot is None:
        return RepoFileSnapshot(repo_root, require_git=require_git)
    if snapshot.repo_root != repo_root.resolve():
        raise ValueError("repo file snapshot belongs to a different repository")
    if require_git and not snapshot.require_git:
        raise ValueError("required Git listing cannot use a fallback-capable snapshot")
    return snapshot


# `/plugins/` is gitignored on purpose (6e05e026e): it is derived, and
# `sync_root_plugin_manifests.py` rewrites it byte-identically. That makes the git
# listing the WRONG RULER for it -- `git ls-files --others --exclude-standard`
# honors .gitignore, so every detector scoping through `iter_matching_repo_files`
# saw zero mirror files while 1,045 sat on disk, and still printed "Validated".
GENERATED_MIRROR_DIRNAME = "plugins"


def iter_generated_mirror_files(repo_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    """Scope over the generated plugin mirror, which git deliberately cannot see.

    Raises ``GeneratedMirrorAbsentError`` when the mirror is not on disk rather
    than returning ``[]``. An empty list here would be indistinguishable from a
    mirror that legitimately contains no matching file, and that collapse is the
    whole defect: a caller cannot tell "I examined the mirror and found nothing"
    from "there was no mirror to examine." The producer is unconditional, so
    absence is never a legitimate discovered-empty family -- it means nobody ran
    `scripts/sync_root_plugin_manifests.py`.
    """
    mirror_root = repo_root / GENERATED_MIRROR_DIRNAME
    if not mirror_root.is_dir():
        raise GeneratedMirrorAbsentError(
            f"generated plugin mirror is absent at {mirror_root}; "
            "run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` first"
        )
    matches: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            matches.append(path)
    return sorted(matches)


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def _git_metadata_is_discoverable(repo_root: Path) -> bool:
    """Return whether Git could discover a work-tree from ``repo_root``.

    A large class of callers deliberately supports a plain fixture directory:
    ``git_list_repo_files`` used to launch Git there, receive its predictable
    "not a repository" refusal, and only then take the documented filesystem
    fallback.  That probe has no information value.  Check the same local
    discovery boundary that Git walks first, while preserving the two cases
    where the environment can redirect discovery outside that boundary.

    This is intentionally only an admission check.  A discoverable ``.git``
    can still be malformed or inaccessible, so the real Git call below remains
    the authority and keeps its existing failure contract.
    """
    if any(os.environ.get(name) for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")):
        return True
    root = repo_root.resolve()
    if not root.is_dir():
        return False
    if (
        (root / "HEAD").is_file()
        and (root / "objects").is_dir()
        and (root / "refs").is_dir()
    ):
        return True
    for candidate in (root, *root.parents):
        marker = candidate / ".git"
        if marker.is_file():
            try:
                if marker.read_text(encoding="utf-8").lstrip().startswith("gitdir:"):
                    return True
            except OSError:
                continue
        elif marker.is_dir() and (marker / "HEAD").is_file():
            # Empty `.git` directories are common in shared temporary roots and
            # are not Git repositories.  Requiring the object store (or a
            # linked common directory) avoids paying a process for that known
            # non-repository marker while still admitting ordinary worktrees.
            if (marker / "objects").is_dir() or (marker / "commondir").is_file():
                return True
    return False


def git_list_repo_files(
    repo_root: Path,
    *,
    include_untracked: bool = True,
    require_git: bool = False,
) -> list[Path] | None:
    args = ["git", "ls-files", "-z", "--cached"]
    if include_untracked:
        args.extend(["--others", "--exclude-standard"])
    if not _git_metadata_is_discoverable(repo_root):
        if require_git:
            raise RepoFileListingError(
                "repo file listing failed\n"
                f"command: {' '.join(args)}\n"
                "exit_code: 128\n"
                "STDOUT:\n\n"
                "STDERR:\nnot a git repository (Git discovery preflight)"
            )
        return None
    result = subprocess.run(
        args,
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        if require_git:
            raise RepoFileListingError(
                "repo file listing failed\n"
                f"command: {' '.join(args)}\n"
                f"exit_code: {result.returncode}\n"
                f"STDOUT:\n{_decode_output(result.stdout)}\n"
                f"STDERR:\n{_decode_output(result.stderr)}"
            )
        return None
    return sorted(repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel)


def iter_repo_files(
    repo_root: Path,
    *,
    include_untracked: bool = True,
    require_git: bool = False,
    snapshot: RepoFileSnapshot | None = None,
) -> list[Path]:
    listing = _listing_snapshot(
        repo_root, require_git=require_git, snapshot=snapshot
    )
    paths = listing.list_files(include_untracked=include_untracked)
    if paths is not None:
        return [path for path in paths if path.is_file()]

    candidates: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_file():
            candidates.append(path)
    return sorted(candidates)


_SUPPORT_PATTERN_PREFIX = "skills/support/"


def _split_support_patterns(patterns: tuple[str, ...]) -> tuple[list[str], list[str]]:
    standard: list[str] = []
    support: list[str] = []
    for pattern in patterns:
        if pattern.startswith(_SUPPORT_PATTERN_PREFIX):
            support.append(pattern.removeprefix(_SUPPORT_PATTERN_PREFIX))
        else:
            standard.append(pattern)
    return standard, support


def iter_matching_repo_files(
    repo_root: Path,
    patterns: tuple[str, ...],
    *,
    include_untracked: bool = True,
    require_git: bool = False,
    snapshot: RepoFileSnapshot | None = None,
) -> list[Path]:
    standard_patterns, support_subpatterns = _split_support_patterns(patterns)
    support_root = support_dir(repo_root)
    support_is_external = support_root != (repo_root / "skills" / "support").resolve()
    if not support_is_external:
        standard_patterns.extend(_SUPPORT_PATTERN_PREFIX + sub for sub in support_subpatterns)
        support_subpatterns = []

    matches: list[Path] = []
    seen: set[Path] = set()

    listing = _listing_snapshot(
        repo_root, require_git=require_git, snapshot=snapshot
    )
    git_paths = listing.list_files(include_untracked=include_untracked)
    if git_paths is not None:
        allowed = {path for path in git_paths if path.is_file()}
        for pattern in standard_patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path not in allowed or path in seen:
                    continue
                seen.add(path)
                matches.append(path)
    else:
        for pattern in standard_patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                matches.append(path)

    for sub in support_subpatterns:
        for path in support_root.glob(sub):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            matches.append(path)

    return sorted(matches)
