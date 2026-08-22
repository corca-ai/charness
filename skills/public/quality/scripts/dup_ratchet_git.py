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

import subprocess
from pathlib import Path


def _git_output(repo_root: Path, args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
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


def changed_worktree_paths(repo_root: Path) -> set[str] | None:
    """Repo-relative paths changed in the current worktree vs HEAD (staged plus
    unstaged tracked changes, plus untracked files), or ``None`` when git cannot
    answer. The hard-block member evidence uses this to say whether each
    blocked family member is part of the current change or a collateral clustering
    rotation among untouched files; ``None`` renders as unknown, never a guess."""
    rc_diff, diff_out = _git_output(repo_root, ["diff", "--name-only", "HEAD"])
    rc_untracked, untracked_out = _git_output(repo_root, ["ls-files", "--others", "--exclude-standard"])
    if rc_diff != 0 or rc_untracked != 0:
        return None
    return {line.strip() for line in [*diff_out.splitlines(), *untracked_out.splitlines()] if line.strip()}


def tracked_files(repo_root: Path) -> set[str] | None:
    """All git-tracked repo-relative paths, or ``None`` when git cannot answer.

    Used to size the population outside ``scope_paths`` honestly: a plain
    recursive filesystem walk would also count ``.git``, ``__pycache__``, and
    everything else this repo's own ``.gitignore`` already excludes from being
    "code" at all. ``None`` (not an empty set) on failure -- an unreadable
    population is unknown, never zero.
    """
    rc, out = _git_output(repo_root, ["ls-files"])
    if rc != 0:
        return None
    return {line.strip() for line in out.splitlines() if line.strip()}
