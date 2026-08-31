from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


def _ensure_scripts_package() -> None:
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "scripts" / "git_checkout.py").is_file():
            root = str(candidate)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


_ensure_scripts_package()
from scripts.repo_file_listing import RepoFileListingError, RepoFileSnapshot  # noqa: E402


class GitFileListingError(RuntimeError):
    pass


@dataclass(frozen=True)
class VisibleRepoFilesSnapshot:
    """One caller-owned view of the repo's git-visible files.

    The snapshot is deliberately not cached here: a mutable checkout must be
    re-read by its next operation. Callers that perform several related scans
    may capture once and pass this value through each scan explicitly.
    """

    files: set[Path] | None


def visible_repo_files(
    repo_root: Path,
    *,
    require_git: bool = False,
    context: str = "git file listing",
    snapshot: VisibleRepoFilesSnapshot | None = None,
) -> set[Path] | None:
    if snapshot is not None:
        return snapshot.files
    try:
        paths = RepoFileSnapshot(repo_root, require_git=require_git).list_files(
            include_untracked=True
        )
    except RepoFileListingError as exc:
        raise GitFileListingError(
            str(exc).replace("repo file listing failed", f"{context} failed", 1)
        ) from exc
    return None if paths is None else set(paths)


def capture_visible_repo_files(
    repo_root: Path, *, require_git: bool = False, context: str = "git file listing"
) -> VisibleRepoFilesSnapshot:
    """Capture one operation-scoped inventory without retaining global state."""
    return VisibleRepoFilesSnapshot(
        visible_repo_files(repo_root, require_git=require_git, context=context)
    )
