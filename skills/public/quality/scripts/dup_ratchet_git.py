#!/usr/bin/env python3
"""Boy-scout dup-ratchet — git stagnation seams (item 5, FD5).

Extracted from ``dup_ratchet_lib.py`` (module-length split). These are the pure git
queries the boy-scout arm needs, kept SEPARATE from the policy so ``evaluate`` stays
injectable: the policy takes the stagnation distance as a plain value and never shells
out. ``check_dup_ratchet`` resolves the overlay anchor, its ancestry, and the commit
distance through here before calling ``evaluate``.

Stagnation is measured from git, not a stored counter or self-SHA (FD5): the anchor is
the commit that last touched the overlay; stagnation = ``rev-list --count
<anchor>..HEAD``. An anchor that is not an ancestor of HEAD (rebase/squash/force-push
orphaned it) is reported so the caller softens the boy-scout arm to advisory; it never
blocks on a phantom.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from scripts.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from subprocess_guard import run_process


def _ensure_scripts_package() -> None:
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "scripts" / "git_checkout.py").is_file():
            root = str(candidate)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


_ensure_scripts_package()
from scripts.git_checkout import discoverable as _git_metadata_is_discoverable  # noqa: E402
from scripts.git_status_snapshot import GitStatusError  # noqa: E402
from scripts.git_status_snapshot import parse as parse_git_status  # noqa: E402
from scripts.git_status_snapshot import status_args as git_status_args  # noqa: E402
from scripts.repo_file_listing import RepoFileSnapshot  # noqa: E402


def _git_output(repo_root: Path, args: list[str]) -> tuple[int, str]:
    if not _git_metadata_is_discoverable(repo_root):
        return 1, ""
    try:
        result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def resolve_anchor(repo_root: Path, review_artifact_rel: str, head: str = "HEAD") -> str | None:
    """The commit that last touched the overlay (``git log -1 --format=%H``). The
    anchor advancing (an overlay edit, e.g. lowering the ceiling) resets stagnation."""
    rc, out = _git_output(repo_root, ["log", "-1", "--format=%H", head, "--", review_artifact_rel])
    if rc != 0 or not out:
        return None
    return out.splitlines()[0].strip() or None


def anchor_is_ancestor(repo_root: Path, anchor: str | None, head: str = "HEAD") -> bool:
    if not anchor:
        return False
    rc, _ = _git_output(repo_root, ["merge-base", "--is-ancestor", anchor, head])
    return rc == 0


def stagnation_commits(repo_root: Path, anchor: str | None, head: str = "HEAD") -> int | None:
    """Commits over ``<anchor>..<head>`` (FD5). ``None`` when the anchor is unknown
    or git cannot answer — the caller degrades the boy-scout arm to advisory."""
    if not anchor:
        return None
    rc, out = _git_output(repo_root, ["rev-list", "--count", f"{anchor}..{head}"])
    if rc != 0:
        return None
    try:
        return int(out.strip())
    except ValueError:
        return None


def _anchor_progress(
    repo_root: Path, anchor: str | None, head: str = "HEAD"
) -> tuple[bool, int | None]:
    """Resolve ancestry and distance in one revision walk.

    ``merge-base --is-ancestor`` followed by ``rev-list --count`` walked the
    same pair of revisions twice.  The left/right counts of a symmetric
    revision range contain both answers: an ancestor has no left-only commits,
    while the right-only count is exactly ``anchor..head``.  An unrelated or
    reversed anchor has left-only commits and therefore remains advisory, just
    as the two old probes reported it.
    """
    if not anchor:
        return False, None
    rc, out = _git_output(
        repo_root,
        ["rev-list", "--left-right", "--count", f"{anchor}...{head}"],
    )
    if rc != 0:
        return False, None
    fields = out.split()
    if len(fields) != 2:
        return False, None
    try:
        left_only, right_only = (int(field) for field in fields)
    except ValueError:
        return False, None
    return left_only == 0, right_only if left_only == 0 else None


def _status_changed_paths(repo_root: Path) -> set[str] | None:
    """Dirty destination paths from the shared porcelain-v2 snapshot."""
    rc, out = _git_output(repo_root, list(git_status_args()))
    if rc != 0:
        return None
    try:
        snapshot = parse_git_status(out.encode("utf-8", errors="surrogateescape"))
    except GitStatusError:
        return None
    return set(snapshot.dirty_destination_paths())


class GitSnapshot:
    """Facts read once for one duplicate-ratchet check operation."""

    __slots__ = (
        "anchor",
        "anchor_is_ancestor",
        "stagnation",
        "tracked_paths",
        "changed_paths",
        "_changed_paths_loaded",
    )

    def __init__(
        self,
        *,
        anchor: str | None,
        anchor_is_ancestor: bool,
        stagnation: int | None,
        tracked_paths: frozenset[str] | None,
        changed_paths: frozenset[str] | None,
        changed_paths_loaded: bool,
    ) -> None:
        self.anchor = anchor
        self.anchor_is_ancestor = anchor_is_ancestor
        self.stagnation = stagnation
        self.tracked_paths = tracked_paths
        self.changed_paths = changed_paths
        self._changed_paths_loaded = changed_paths_loaded

    def load_changed_paths(self, repo_root: Path) -> frozenset[str] | None:
        """Load the evidence-only worktree set once, after verdict facts exist."""
        if not self._changed_paths_loaded:
            changed = _status_changed_paths(repo_root)
            self.changed_paths = frozenset(changed) if changed is not None else None
            self._changed_paths_loaded = True
        return self.changed_paths


def snapshot(
    repo_root: Path,
    review_artifact_rel: str,
    head: str = "HEAD",
    *,
    include_stagnation: bool = True,
    include_changed_paths: bool = True,
) -> GitSnapshot:
    """Collect all Git facts consumed by one gate evaluation.

    The operation uses one anchor lookup, one combined ancestry/distance walk,
    and one tracked-population lookup.  Changed paths are loaded lazily when a
    hard-block verdict needs member evidence, so clean/advisory runs do not pay
    for an evidence-only query. ``include_stagnation`` keeps ``--stagnation``'s
    injected-test contract: those tests never need an overlay anchor query,
    while still receiving the same population and change facts used by the
    evidence and scope arms.
    """
    if include_stagnation:
        anchor = resolve_anchor(repo_root, review_artifact_rel, head)
        is_ancestor, stagnation = _anchor_progress(repo_root, anchor, head)
    else:
        anchor, is_ancestor, stagnation = None, False, None
    tracked = tracked_files(repo_root)
    changed = _status_changed_paths(repo_root) if include_changed_paths else None
    return GitSnapshot(
        anchor=anchor,
        anchor_is_ancestor=is_ancestor,
        stagnation=stagnation,
        tracked_paths=frozenset(tracked) if tracked is not None else None,
        changed_paths=frozenset(changed) if changed is not None else None,
        changed_paths_loaded=include_changed_paths,
    )


def gate_snapshot(
    repo_root: Path,
    review_artifact_rel: str,
    stagnation_override: int | None = None,
    head: str = "HEAD",
) -> tuple[GitSnapshot, int | None, str | None, bool]:
    """Return the operation snapshot plus the policy-ready stagnation tuple."""
    facts = snapshot(
        repo_root,
        review_artifact_rel,
        head,
        include_stagnation=stagnation_override is None,
        include_changed_paths=False,
    )
    if stagnation_override is not None:
        return facts, stagnation_override, "<injected>", True
    return facts, facts.stagnation, facts.anchor, facts.anchor_is_ancestor


def changed_worktree_paths(repo_root: Path) -> set[str] | None:
    """Repo-relative paths changed in the current worktree vs HEAD (staged plus
    unstaged tracked changes, plus untracked files), or ``None`` when git cannot
    answer. The hard-block member evidence uses this to say whether each
    blocked family member is part of the current change or a collateral clustering
    rotation among untouched files; ``None`` renders as unknown, never a guess."""
    return _status_changed_paths(repo_root)


def tracked_files(repo_root: Path) -> set[str] | None:
    """All git-tracked repo-relative paths, or ``None`` when git cannot answer.

    Used to size the population outside ``scope_paths`` honestly: a plain
    recursive filesystem walk would also count ``.git``, ``__pycache__``, and
    everything else this repo's own ``.gitignore`` already excludes from being
    "code" at all. ``None`` (not an empty set) on failure -- an unreadable
    population is unknown, never zero.
    """
    listed = RepoFileSnapshot(repo_root).list_files(include_untracked=False)
    if listed is None:
        return None
    return {path.relative_to(repo_root).as_posix() for path in listed}
