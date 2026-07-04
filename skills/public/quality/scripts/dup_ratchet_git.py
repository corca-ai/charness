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
