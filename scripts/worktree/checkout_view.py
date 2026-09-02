"""Status and listing of one checkout.

Consumers that need dirty paths or the file population talk to this port.
Merge-base, gitlink, ``show``, and ``%B`` stay Git: those are object-store
questions, not a worktree view.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple, Protocol


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.git_status_snapshot import GitStatusError, GitStatusSnapshot  # noqa: E402
from scripts.core.git_status_snapshot import capture as capture_status  # noqa: E402
from scripts.core.repo_file_listing import RepoFileSnapshot  # noqa: E402


class WorktreeMoment(NamedTuple):
    """One checkout observation: dirty populations plus the checked-out HEAD.

    Parent-before, target-before, parent-after, and target-after are four
    moments. This type names one of them. It does not collapse them.
    """

    populations: dict[str, list[str]]
    head_oid: str | None
    branch: str | None


def moment_from_status(snapshot: GitStatusSnapshot) -> WorktreeMoment:
    return WorktreeMoment(snapshot.populations(), snapshot.head_oid, snapshot.branch)


class CheckoutView(Protocol):
    repo_root: Path

    def status(
        self,
        *,
        ignored: bool = False,
        branch: bool = True,
        untracked: str = "all",
        no_renames: bool = False,
    ) -> GitStatusSnapshot: ...

    def list_files(self, *, include_untracked: bool = True) -> list[Path] | None: ...


class GitCheckout:
    """Live worktree: one status per flag set, listing via ``RepoFileSnapshot``."""

    def __init__(self, repo_root: Path, *, require_git: bool = False) -> None:
        self.repo_root = repo_root.resolve()
        self.require_git = require_git
        self._listing = RepoFileSnapshot(self.repo_root, require_git=require_git)
        self._status: dict[tuple[bool, bool, str, bool], GitStatusSnapshot] = {}

    def status(
        self,
        *,
        ignored: bool = False,
        branch: bool = True,
        untracked: str = "all",
        no_renames: bool = False,
    ) -> GitStatusSnapshot:
        key = (ignored, branch, untracked, no_renames)
        if key not in self._status:
            self._status[key] = capture_status(
                self.repo_root,
                ignored=ignored,
                branch=branch,
                untracked=untracked,
                no_renames=no_renames,
            )
        return self._status[key]

    def list_files(self, *, include_untracked: bool = True) -> list[Path] | None:
        return self._listing.list_files(include_untracked=include_untracked)


class FactsCheckout:
    """Injected status and file population. No ``.git``."""

    def __init__(
        self,
        repo_root: Path,
        *,
        status: GitStatusSnapshot | None = None,
        files: list[Path] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self._status = status
        self._files = files

    def status(
        self,
        *,
        ignored: bool = False,
        branch: bool = True,
        untracked: str = "all",
        no_renames: bool = False,
    ) -> GitStatusSnapshot:
        _ = (ignored, branch, untracked, no_renames)
        if self._status is None:
            raise GitStatusError("facts checkout has no status snapshot")
        return self._status

    def list_files(self, *, include_untracked: bool = True) -> list[Path] | None:
        _ = include_untracked
        return self._files


def path_is_tracked(checkout: CheckoutView, relative: str) -> bool | None:
    """Whether ``relative`` is in the tracked population, or None if unlisted."""
    files = checkout.list_files(include_untracked=False)
    if files is None:
        return None
    wanted = Path(relative).as_posix()
    for path in files:
        try:
            if path.relative_to(checkout.repo_root).as_posix() == wanted:
                return True
        except ValueError:
            continue
    return False
