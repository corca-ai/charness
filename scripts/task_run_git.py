"""Git and linked-worktree state for bounded task runs."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

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
        "sha": _git_output(repo_root, "rev-parse", "HEAD").strip(),
        "message": WIP_CANDIDATE_COMMIT_MESSAGE,
        "correctness_verified": False,
    }


def _require_git_root(repo_root: Path) -> Path:
    repo_root = repo_root.expanduser().resolve()
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
    output = _git_output(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "-z",
    )
    populations: dict[str, list[str]] = {"tracked": [], "untracked": [], "ignored": []}
    records = output.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 3:
            raise TaskRunError(f"unexpected git status record: {record!r}")
        status, path = record[:2], record[3:]
        if status == "??":
            populations["untracked"].append(path)
        elif status == "!!":
            populations["ignored"].append(path)
        else:
            populations["tracked"].append(path)
        if status[0] in {"R", "C"} and index < len(records) and records[index]:
            populations["tracked"].append(records[index])
            index += 1
    return {key: sorted(set(paths)) for key, paths in populations.items()}


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
    tracked = _parse_nul_paths(
        _git_output(repo_root, "diff", "--no-renames", "--name-only", "-z", base_sha, "--")
    )
    untracked = _parse_nul_paths(
        _git_output(repo_root, "ls-files", "--others", "--exclude-standard", "-z", "--")
    )
    return sorted(set(tracked) | set(untracked))
