"""Staged-tree analysis target for changed-line gates.

The release lane must prove the tree it is about to commit, but the
changed-line trust machinery only attested committed ranges (``base..HEAD``):
any uncommitted pool change refused the run, so a first commit of pool
changes could never earn its own receipt. The rest of the pipeline was
already worktree-based — the suggester discovers ``base -> worktree`` and
the freshness fingerprint is content-based precisely to stay stable across
the pre-commit→commit boundary — leaving the consumer's trust gate as the
one committed-only link.

``:staged:`` names the staged index tree (``git write-tree``) as the analyzed
head. The anti-false-green invariant is preserved, not relaxed: instead of
"analyzed head == HEAD and the worktree is clean", a staged run requires
"the worktree's pool bytes == the analyzed tree's pool bytes". Staged-only
dirt is IN the analyzed tree; unstaged or untracked pool changes are
invisible to it and refuse (or warn under ``--allow-dirty``) exactly as
uncommitted changes did for ``HEAD``.
"""

from __future__ import annotations

import re
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.git_status_snapshot import (  # noqa: E402
    GitStatusError,
    GitStatusSnapshot,
)
from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.worktree.checkout_view import CheckoutView, GitCheckout  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

#: Analyzed-head spelling for "the staged index tree". A literal git ref can
#: never collide with it: rev-parse rejects the leading colon.
STAGED_HEAD = ":staged:"

_GIT_OID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def resolve_staged_tree(repo_root: Path) -> str | None:
    """Materialize the staged index as a tree SHA, or None when git cannot."""
    try:
        result = run_process(["git", "write-tree"], cwd=repo_root, timeout_seconds=None)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    tree = result.stdout.strip()
    return tree if _GIT_OID_RE.fullmatch(tree) else None


def staged_invisible_from_snapshot(
    snapshot: GitStatusSnapshot, eligible: set[str]
) -> list[str]:
    """Eligible pool files the staged tree cannot see.

    Pure over one status snapshot: staged-only dirt is IN the analyzed tree
    and stays out of this list, while worktree-vs-index differences,
    untracked files, and unmerged entries are invisible to index analysis.
    Anything unparseable fails closed into the list.
    """
    invisible: set[str] = set()
    for record in snapshot.records:
        if record.kind == "ignored":
            continue
        if record.kind in {"untracked", "unmerged"}:
            invisible.add(record.path)
            continue
        xy = record.xy
        if len(xy) != 2 or record.kind not in {"ordinary", "rename"} or xy[1] != ".":
            invisible.add(record.path)
            if record.orig_path:
                invisible.add(record.orig_path)
    return sorted(path for path in invisible if path in eligible)


def staged_invisible_pool_changes(
    repo_root: Path,
    eligible: set[str],
    *,
    checkout: CheckoutView | None = None,
) -> list[str] | None:
    """Staged-invisible pool files, or None when the worktree cannot be read."""
    try:
        snapshot = (checkout or GitCheckout(repo_root)).status()
    except (GitStatusError, OSError):
        return None
    return staged_invisible_from_snapshot(snapshot, eligible)


def staged_dirty_refusal(uncommitted: list[str], tree: str) -> str:
    """Refuse-fast message for the staged-invisible case.

    The remedy names staging, not committing: these bytes are one ``git add``
    away from an analyzable tree, and no commit is required to earn the
    verdict.
    """
    return (
        f"REFUSING to run: {len(uncommitted)} mutation-pool file(s) differ between the "
        f"worktree and the staged index, so the staged tree `{tree[:12]}` cannot see them "
        f"({', '.join(uncommitted)}). A clean verdict would be a FALSE GREEN for them and "
        "is indistinguishable from a real green to the reader. Stage those files "
        "(`git add`) and re-run for a staged-tree verdict, or pass --allow-dirty for an "
        "explicitly ADVISORY read that records itself as unverified."
    )


def staged_false_green_message(uncommitted: list[str], tree: str) -> str:
    """The advisory (``--allow-dirty``) wording for a staged-invisible pool."""
    return (
        f"analyzed tree is the staged index `{tree[:12]}` but {len(uncommitted)} "
        "mutation-pool file(s) have worktree changes outside the index excluded from "
        f"the analysis ({', '.join(uncommitted)}); those changes are NOT analyzed, so a "
        "clean changed-line verdict is a FALSE GREEN for them. Stage them and re-run "
        "before trusting this result."
    )
