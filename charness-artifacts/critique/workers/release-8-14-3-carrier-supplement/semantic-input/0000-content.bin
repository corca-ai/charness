"""Candidate-carrier ownership for bounded task runs.

Split from ``task_run_git`` under the module length cap: this module owns
which lane tree carries the complete validated candidate, including the
lane-owned change attribution that excludes merged-in target content.
"""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_git as _git_owner  # noqa: E402


def _lane_owned_paths(repo_root: Path, base_sha: str, head: str) -> list[str]:
    """Paths the lane itself changed, excluding merged-in target content (#875).

    A lane that merges the target branch mid-task would otherwise report
    every merged-in path as its own change. Walk the first-parent chain
    (the lane's own line): a merge-free chain reuses the single base diff,
    while a merge contributes only paths where the result differs from
    every merged parent -- main-side content taken verbatim drops out,
    but a lane edit inside the merge resolution stays.
    """
    chain = _git_owner._git_output(
        repo_root,
        "rev-list",
        "--first-parent",
        "--reverse",
        "--parents",
        f"{base_sha}..{head}",
    ).splitlines()
    entries = [line.split() for line in chain if line.strip()]
    if all(len(parts) == 2 for parts in entries):
        return _git_owner._diff_paths(repo_root, base_sha, head)
    owned: set[str] = set()
    for parts in entries:
        commit, parents = parts[0], parts[1:]
        if len(parents) < 2:
            owned.update(_git_owner._diff_paths(repo_root, f"{commit}^", commit))
        else:
            merged = [
                set(_git_owner._diff_paths(repo_root, parent, commit))
                for parent in parents[1:]
            ]
            owned.update(set.intersection(*merged))
    return sorted(owned)


def _digest_frame(digest: Any, value: bytes) -> None:
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def _candidate_content_digest(repo_root: Path, base_sha: str, changed_paths: Sequence[str]) -> str:
    digest = hashlib.sha256()
    _digest_frame(digest, b"charness.task-run.candidate.v1")
    _digest_frame(digest, base_sha.encode("ascii"))
    for path in changed_paths:
        _digest_frame(digest, os.fsencode(path))
        candidate_path = repo_root / path
        try:
            metadata = candidate_path.lstat()
        except FileNotFoundError:
            _digest_frame(digest, b"missing")
            continue
        _digest_frame(digest, str(stat.S_IMODE(metadata.st_mode)).encode("ascii"))
        if stat.S_ISLNK(metadata.st_mode):
            _digest_frame(digest, b"symlink")
            _digest_frame(digest, os.fsencode(os.readlink(candidate_path)))
        elif stat.S_ISREG(metadata.st_mode):
            _digest_frame(digest, b"file")
            _digest_frame(digest, candidate_path.read_bytes())
        else:
            _digest_frame(digest, b"special")
            _digest_frame(digest, str(metadata.st_size).encode("ascii"))
    return digest.hexdigest()


def _candidate_carrier(
    repo_root: Path,
    base_sha: str,
    populations: Mapping[str, Sequence[str]] | None = None,
    head: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Describe which lane tree carries the complete validated candidate."""
    head = (
        head
        or _git_owner._head_sha_from_checkout(repo_root)
        or _git_owner._git_output(repo_root, "rev-parse", "HEAD").strip()
    )
    # ANCESTRY, not inequality. `head != base_sha` answers "did HEAD move", which is a
    # different question from "does HEAD carry the base-to-worktree candidate". A lane
    # that amends its own base, or resets to an ancestor, leaves a clean tree at a
    # SIBLING commit -- and the inequality test called that `commit-only` with
    # `head_is_complete: true`, which invites the parent to cherry-pick a commit that
    # replays against the wrong parent instead of carrying the validated candidate.
    # Equality already establishes ancestry.  Most worktree-only task runs use
    # ``base=HEAD`` and used to pay for a merge-base subprocess before asking
    # Git for the same tracked diff twice below.
    base_is_ancestor = head == base_sha or _git_owner._is_ancestor(repo_root, base_sha, head)
    has_commit = head != base_sha and base_is_ancestor
    committed_paths = _lane_owned_paths(repo_root, base_sha, head) if has_commit else []
    # Porcelain status is the one coherent snapshot of the current worktree
    # population.  Its tracked and untracked paths are exactly the dirty
    # populations needed below; asking Git separately for `diff HEAD` and
    # `ls-files --others` only re-reads that same boundary.
    current_populations = populations or _git_owner._collect_populations(repo_root)
    untracked_paths = list(current_populations["untracked"])
    working_tree_paths = sorted(set(current_populations["tracked"]) | set(untracked_paths))
    if head == base_sha:
        # The two tracked views are identical when HEAD is the selected base;
        # status is the complete candidate view, so no separate diff or
        # untracked listing is necessary.
        changed_paths = working_tree_paths
        dirty_paths = list(working_tree_paths)
    else:
        dirty_paths = working_tree_paths
        if has_commit and not dirty_paths:
            # A clean descendant HEAD is exactly the committed candidate already
            # read above. Re-running the same base diff cannot add information.
            changed_paths = list(committed_paths)
        elif not has_commit:
            changed_paths = sorted(
                set(_git_owner._diff_paths(repo_root, base_sha)) | set(untracked_paths)
            )
        else:
            # A lane commit plus later worktree edits can cancel relative to
            # the selected base; the dirty status must not widen the
            # base-relative scope, and merged-in target content must not
            # count as lane changes (#875).
            worktree_vs_base = set(_git_owner._diff_paths(repo_root, base_sha))
            dirty_vs_head = set(_git_owner._diff_paths(repo_root, head))
            changed_paths = sorted(
                (worktree_vs_base & (set(committed_paths) | dirty_vs_head))
                | set(untracked_paths)
            )
    if not has_commit:
        carrier_kind = "worktree-only"
    elif dirty_paths:
        carrier_kind = "commit-plus-dirty"
    else:
        carrier_kind = "commit-only"
    return {
        "changed_paths": changed_paths,
        "carrier_kind": carrier_kind,
        "committed_paths": committed_paths,
        "dirty_paths": dirty_paths,
        "head_sha": head if has_commit else None,
        # Published even when it is True, because its FALSE case is otherwise
        # invisible: a lane that amended its base has a clean tree at a sibling
        # commit, and without this the receipt reads exactly like a lane that never
        # committed at all. A parent that sees `observed_head` differ from the base
        # while this is False knows a commit exists and does not carry the candidate.
        "base_is_ancestor_of_head": base_is_ancestor,
        "observed_head_sha": head,
        "observed_branch": branch,
        "head_is_complete": has_commit and not dirty_paths,
        "content_digest": _candidate_content_digest(repo_root, base_sha, changed_paths),
    }
