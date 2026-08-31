"""Git and linked-worktree state for bounded task runs."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.git_checkout import head_oid_from_files as _head_sha_from_checkout
from scripts.git_checkout import identity_from_files, layout_from_files, worktree_root_from_files
from scripts.git_status_snapshot import GitStatusError
from scripts.git_status_snapshot import parse as parse_git_status
from scripts.git_status_snapshot import status_args as git_status_args
from scripts.task_run_contract import (
    _BRANCH_RE,
    _GIT_DISCOVERY_ENV,
    FAIL,
    PASS,
    TaskRunError,
)

WIP_CANDIDATE_COMMIT_MESSAGE = (
    "task-run: WIP candidate — interrupted mid-edit — state unknown"
)


def _git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in _GIT_DISCOVERY_ENV}


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        env=_git_env(),
        check=False,
        capture_output=True,
        text=True,
    )


def _git_output(repo_root: Path, *args: str) -> str:
    result = _git(repo_root, *args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise TaskRunError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _repo_snapshot(repo_root: Path) -> dict[str, Any]:
    """Read immutable repository identity and topology from checkout files.

    The task lifecycle needs the same four scalar facts at its input boundary:
    the worktree root, the shared administration directory, the checkout's
    administration directory, and ``HEAD``.  Ordinary layouts already state
    them; ``rev-parse`` remains the fallback for redirected or packed layouts.
    """
    requested = repo_root.expanduser().resolve()
    identity = identity_from_files(requested)
    if identity is not None:
        if identity.repo_root != requested:
            raise TaskRunError(
                f"--repo-root must be the Git worktree root, not a subdirectory: {requested}"
            )
        return {
            "repo_root": identity.repo_root,
            "git_common_dir": identity.common_dir,
            "git_dir": identity.git_dir,
            "head": identity.head_oid,
        }
    values = _git_output(
        requested,
        "rev-parse",
        "--show-toplevel",
        "--git-common-dir",
        "--git-dir",
        "HEAD",
    ).splitlines()
    if len(values) != 4:
        raise TaskRunError("git rev-parse returned an incomplete repository snapshot")
    discovered = Path(values[0]).resolve()
    common = Path(values[1])
    if not common.is_absolute():
        common = discovered / common
    git_dir = Path(values[2])
    if not git_dir.is_absolute():
        git_dir = discovered / git_dir
    common = common.resolve()
    git_dir = git_dir.resolve()
    if discovered != requested:
        raise TaskRunError(
            f"--repo-root must be the Git worktree root, not a subdirectory: {requested}"
        )
    if not common.is_dir():
        raise TaskRunError(f"Git common directory is not a directory: {common}")
    if not git_dir.is_dir():
        raise TaskRunError(f"Git directory is not a directory: {git_dir}")
    return {
        "repo_root": discovered,
        "git_common_dir": common,
        "git_dir": git_dir,
        "head": values[3].strip(),
    }


def _commit_wip_candidate(repo_root: Path) -> dict[str, Any]:
    """Checkpoint all non-ignored lane output as an explicitly unverified WIP."""
    staged = _git(repo_root, "add", "--all", "--", ".")
    if staged.returncode != 0:
        detail = staged.stderr.strip() or staged.stdout.strip() or "git add failed"
        raise TaskRunError(f"git add failed: {detail}")

    committed = _git(
        repo_root,
        "-c",
        "user.email=charness-task-run@localhost",
        "-c",
        "user.name=charness task run",
        "commit",
        "--allow-empty",
        "--no-verify",
        "--message",
        WIP_CANDIDATE_COMMIT_MESSAGE,
    )
    if committed.returncode != 0:
        detail = committed.stderr.strip() or committed.stdout.strip() or "git commit failed"
        raise TaskRunError(f"git commit failed: {detail}")

    return {
        "status": "committed",
        "sha": _head_sha_from_checkout(repo_root)
        or _git_output(repo_root, "rev-parse", "HEAD").strip(),
        "message": WIP_CANDIDATE_COMMIT_MESSAGE,
        "correctness_verified": False,
    }


def _require_git_root(repo_root: Path) -> Path:
    repo_root = repo_root.expanduser().resolve()
    discovered = worktree_root_from_files(repo_root)
    if discovered is None:
        discovered = Path(_git_output(repo_root, "rev-parse", "--show-toplevel").strip()).resolve()
    if discovered != repo_root:
        raise TaskRunError(
            f"--repo-root must be the Git worktree root, not a subdirectory: {repo_root}"
        )
    return repo_root


def _resolve_base_sha(repo_root: Path, base: str) -> str:
    if not base.strip():
        raise TaskRunError("--base is required and must resolve to a commit")
    result = _git(
        repo_root,
        "rev-parse",
        "--verify",
        "--quiet",
        "--end-of-options",
        f"{base}^{{commit}}",
    )
    sha = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        raise TaskRunError(result.stderr.strip() or f"ref is not resolvable: {base}")
    return sha


def _git_common_dir(repo_root: Path) -> Path:
    """Writable Git administration root required for a linked worktree."""
    layout = layout_from_files(repo_root)
    if layout is not None:
        return layout.common_dir
    value = _git_output(repo_root, "rev-parse", "--git-common-dir").strip()
    common = Path(value)
    if not common.is_absolute():
        common = repo_root / common
    resolved = common.resolve()
    if not resolved.is_dir():
        raise TaskRunError(f"Git common directory is not a directory: {resolved}")
    return resolved


def _git_dir(repo_root: Path) -> Path:
    """Return the checkout-specific Git administration directory."""
    layout = layout_from_files(repo_root)
    if layout is not None:
        return layout.git_dir
    value = _git_output(repo_root, "rev-parse", "--git-dir").strip()
    git_dir = Path(value)
    if not git_dir.is_absolute():
        git_dir = repo_root / git_dir
    resolved = git_dir.resolve()
    if not resolved.is_dir():
        raise TaskRunError(f"Git directory is not a directory: {resolved}")
    return resolved


def _validate_branch(repo_root: Path, branch: str) -> str:
    if not branch or not _BRANCH_RE.fullmatch(branch) or ".." in branch or branch.endswith((".", "/")):
        raise TaskRunError(f"--branch is not a valid named branch: {branch!r}")
    result = _git(repo_root, "check-ref-format", "--branch", branch)
    if result.returncode != 0:
        raise TaskRunError(result.stderr.strip() or f"--branch is not a valid named branch: {branch}")
    return branch


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_worktree_path(repo_root: Path, target_path: Path) -> Path:
    target = target_path.expanduser().resolve()
    if target == repo_root or _is_inside(target, repo_root):
        raise TaskRunError(f"worktree path must be outside the repository: {target}")
    if target.exists() or target.is_symlink():
        raise TaskRunError(f"worktree path already exists: {target}")
    return target


def _parse_nul_paths(output: str) -> list[str]:
    return sorted({entry for entry in output.split("\0") if entry})


def _collect_populations(repo_root: Path) -> dict[str, list[str]]:
    """Worktree populations from the same porcelain-v2 snapshot as completion."""
    populations, _, _ = _collect_populations_with_metadata(repo_root)
    return populations


def _collect_populations_with_metadata(
    repo_root: Path,
) -> tuple[dict[str, list[str]], str | None, str | None]:
    """Read terminal worktree populations together with Git's branch snapshot."""
    output = _git_output(repo_root, *git_status_args(ignored=True))
    try:
        snapshot = parse_git_status(output.encode("utf-8", errors="surrogateescape"))
    except GitStatusError as exc:
        raise TaskRunError(str(exc)) from exc
    return snapshot.populations(), snapshot.head_oid, snapshot.branch


def _snapshot_payload(snapshot: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    return {key: {"count": len(paths), "paths": list(paths)} for key, paths in snapshot.items()}


def _population_delta(
    before: Mapping[str, Sequence[str]],
    after: Mapping[str, Sequence[str]],
    *,
    preflight: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for population in ("tracked", "untracked", "ignored"):
        before_set = set(before.get(population, ()))
        after_set = set(after.get(population, ()))
        added = sorted(after_set - before_set)
        removed = sorted(before_set - after_set)
        if preflight:
            verdict = PASS if population == "ignored" or not after_set else FAIL
            reason = (
                "ignored entries are reported as baseline residue"
                if population == "ignored"
                else "fresh worktrees must start without tracked or untracked changes"
            )
        elif population == "tracked":
            verdict, reason = PASS, "tracked changes are the task candidate and remain inspectable"
        elif population == "untracked":
            verdict = PASS
            reason = (
                "new untracked files remain candidate changes; exact scope determines whether they are allowed"
                if added
                else "no new untracked files appeared during codex exec"
            )
        else:
            verdict = "warn" if added else PASS
            reason = (
                "new ignored files appeared; inspect the generated-file causes"
                if added
                else "no new ignored files appeared during codex exec"
            )
        result[population] = {
            "before_count": len(before_set),
            "after_count": len(after_set),
            "added": added,
            "removed": removed,
            "paths": sorted(after_set),
            "verdict": verdict,
            "reason": reason,
        }
    return result


def _changed_paths(repo_root: Path, base_sha: str) -> list[str]:
    return sorted(set(_diff_paths(repo_root, base_sha)) | set(_untracked_paths(repo_root)))


def _diff_paths(repo_root: Path, *revisions: str) -> list[str]:
    return _parse_nul_paths(
        _git_output(
            repo_root,
            "diff",
            "--no-renames",
            "--name-only",
            "-z",
            *revisions,
            "--",
        )
    )


def _untracked_paths(repo_root: Path) -> list[str]:
    return _parse_nul_paths(
        _git_output(repo_root, "ls-files", "--others", "--exclude-standard", "-z", "--")
    )


def _digest_frame(digest: Any, value: bytes) -> None:
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def _candidate_content_digest(
    repo_root: Path, base_sha: str, changed_paths: Sequence[str]
) -> str:
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


def _is_ancestor(repo_root: Path, base_sha: str, head: str) -> bool:
    """True when `base_sha` is reachable from `head`, so HEAD can carry base-to-HEAD."""
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", base_sha, head],
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def _candidate_carrier(
    repo_root: Path,
    base_sha: str,
    populations: Mapping[str, Sequence[str]] | None = None,
    head: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Describe which lane tree carries the complete validated candidate."""
    head = head or _head_sha_from_checkout(repo_root) or _git_output(repo_root, "rev-parse", "HEAD").strip()
    # ANCESTRY, not inequality. `head != base_sha` answers "did HEAD move", which is a
    # different question from "does HEAD carry the base-to-worktree candidate". A lane
    # that amends its own base, or resets to an ancestor, leaves a clean tree at a
    # SIBLING commit -- and the inequality test called that `commit-only` with
    # `head_is_complete: true`, which invites the parent to cherry-pick a commit that
    # replays against the wrong parent instead of carrying the validated candidate.
    # Equality already establishes ancestry.  Most worktree-only task runs use
    # ``base=HEAD`` and used to pay for a merge-base subprocess before asking
    # Git for the same tracked diff twice below.
    base_is_ancestor = head == base_sha or _is_ancestor(repo_root, base_sha, head)
    has_commit = head != base_sha and base_is_ancestor
    committed_paths = _diff_paths(repo_root, base_sha, head) if has_commit else []
    # Porcelain status is the one coherent snapshot of the current worktree
    # population.  Its tracked and untracked paths are exactly the dirty
    # populations needed below; asking Git separately for `diff HEAD` and
    # `ls-files --others` only re-reads that same boundary.  Keep the
    # base-relative diff below because status cannot answer whether a path was
    # restored to the selected base after a lane commit.
    current_populations = populations or _collect_populations(repo_root)
    untracked_paths = list(current_populations["untracked"])
    working_tree_paths = sorted(
        set(current_populations["tracked"]) | set(untracked_paths)
    )
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
        else:
            changed_paths = sorted(
                set(_diff_paths(repo_root, base_sha)) | set(untracked_paths)
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
