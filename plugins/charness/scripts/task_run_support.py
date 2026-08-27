"""Git, scope, runtime, and receipt helpers for :mod:`task_run`."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime_bootstrap import runtime_root

PASS = "pass"
FAIL = "fail"
SCHEMA_VERSION = 1
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_SUSPICIOUS_RUNTIME_PARTS = frozenset(
    {".pytest_cache", ".ruff_cache", "__pycache__", ".coverage", "coverage", "pytest-tmp", "tmp"}
)


class TaskRunError(ValueError):
    """A task-run preflight input is not safe or resolvable."""


def _git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in _GIT_DISCOVERY_ENV}


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo_root, env=_git_env(), check=False,
        capture_output=True, text=True,
    )


def _git_output(repo_root: Path, *args: str) -> str:
    result = _git(repo_root, *args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise TaskRunError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _require_git_root(repo_root: Path) -> Path:
    repo_root = repo_root.expanduser().resolve()
    discovered = Path(_git_output(repo_root, "rev-parse", "--show-toplevel").strip()).resolve()
    if discovered != repo_root:
        raise TaskRunError(f"--repo-root must be the Git worktree root, not a subdirectory: {repo_root}")
    return repo_root


def _resolve_base_sha(repo_root: Path, base: str) -> str:
    if not base.strip():
        raise TaskRunError("--base is required and must resolve to a commit")
    result = _git(repo_root, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{base}^{{commit}}")
    sha = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        raise TaskRunError(result.stderr.strip() or f"ref is not resolvable: {base}")
    return sha


def _validate_branch(repo_root: Path, branch: str) -> str:
    if not branch or not _BRANCH_RE.fullmatch(branch) or ".." in branch or branch.endswith((".", "/")):
        raise TaskRunError(f"--branch is not a valid named branch: {branch!r}")
    result = _git(repo_root, "check-ref-format", "--branch", branch)
    if result.returncode != 0:
        raise TaskRunError(result.stderr.strip() or f"--branch is not a valid named branch: {branch}")
    return branch


def _normalize_scope(value: str) -> str:
    scope = value.strip()
    if scope.startswith("./"):
        scope = scope[2:]
    if not scope or scope.startswith("/") or "\\" in scope or any(
        part in {"", ".", ".."} for part in scope.split("/")
    ):
        raise TaskRunError(f"scope must be a repository-relative path: {value!r}")
    return scope


def normalize_scopes(scopes: Sequence[str]) -> list[str]:
    """Return one deterministic exact-path scope list."""
    if not scopes:
        raise TaskRunError("at least one --scope is required")
    return sorted({_normalize_scope(value) for value in scopes})


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


def _resolve_codex(value: str) -> str:
    if not value.strip():
        raise TaskRunError("--codex must name an executable")
    if "/" in value:
        candidate = Path(value).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise TaskRunError(f"Codex executable is not runnable: {value}")
        return str(candidate)
    resolved = shutil.which(value)
    if resolved is None:
        raise TaskRunError(f"Codex executable is not on PATH: {value}")
    return resolved


def _parse_nul_paths(output: str) -> list[str]:
    return sorted({entry for entry in output.split("\0") if entry})


def _collect_populations(repo_root: Path) -> dict[str, list[str]]:
    output = _git_output(
        repo_root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching", "-z"
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
    before: Mapping[str, Sequence[str]], after: Mapping[str, Sequence[str]], *, preflight: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for population in ("tracked", "untracked", "ignored"):
        before_set = set(before.get(population, ()))
        after_set = set(after.get(population, ()))
        added = sorted(after_set - before_set)
        removed = sorted(before_set - after_set)
        if preflight:
            verdict = PASS if population == "ignored" or not after_set else FAIL
            reason = "ignored entries are reported as baseline residue" if population == "ignored" else "fresh worktrees must start without tracked or untracked changes"
        elif population == "tracked":
            verdict, reason = PASS, "tracked changes are the task candidate and remain inspectable"
        elif population == "untracked":
            verdict = PASS
            reason = "new untracked files remain candidate changes; exact scope determines whether they are allowed" if added else "no new untracked files appeared during codex exec"
        else:
            verdict = "warn" if added else PASS
            reason = "new ignored files appeared; inspect the generated-file causes" if added else "no new ignored files appeared during codex exec"
        result[population] = {
            "before_count": len(before_set), "after_count": len(after_set), "added": added,
            "removed": removed, "paths": sorted(after_set), "verdict": verdict, "reason": reason,
        }
    return result


def _changed_paths(repo_root: Path, base_sha: str) -> list[str]:
    tracked = _parse_nul_paths(_git_output(repo_root, "diff", "--no-renames", "--name-only", "-z", base_sha, "--"))
    untracked = _parse_nul_paths(_git_output(repo_root, "ls-files", "--others", "--exclude-standard", "-z", "--"))
    return sorted(set(tracked) | set(untracked))


def _scope_result(repo_root: Path, base_sha: str, scopes: Sequence[str], require_change: bool) -> dict[str, Any]:
    changed = _changed_paths(repo_root, base_sha)
    disallowed = sorted(path for path in changed if path not in set(scopes))
    if disallowed:
        verdict, reason = FAIL, "candidate changes paths outside the exact declared scope"
    elif require_change and not changed:
        verdict, reason = FAIL, "the task required a change but the worktree is unchanged"
    else:
        verdict, reason = PASS, "all candidate changes are within the exact declared scope"
    return {"verdict": verdict, "reason": reason, "allowed_paths": list(scopes), "changed_paths": changed, "disallowed_paths": disallowed, "require_change": require_change}


def _path_cause(path: str) -> str:
    parts = set(Path(path).parts)
    if path.endswith(".pyc") or parts & _SUSPICIOUS_RUNTIME_PARTS:
        return "runtime/cache output appeared inside the worktree; inspect PYTHONPYCACHEPREFIX, pytest cache, coverage, and TMPDIR"
    if "node_modules" in parts:
        return "dependency/install output appeared inside the worktree; compare with the prepare step"
    return "the child command produced a file outside the tracked task candidate; inspect the captured Codex log"


def _generated_files(populations: Mapping[str, Any], scopes: Sequence[str]) -> list[dict[str, str]]:
    generated: list[dict[str, str]] = []
    allowed = set(scopes)
    for population in ("untracked", "ignored"):
        for path in populations[population].get("added", []):
            candidate = population == "untracked" and path in allowed
            generated.append({
                "population": population,
                "path": path,
                "classification": "candidate" if candidate else "diagnostic",
                "cause": "new candidate path is within the exact declared scope" if candidate else _path_cause(path),
            })
    return generated


def _task_id(branch: str, requested: str | None) -> str:
    raw = requested.strip() if requested else branch.replace("/", "-")
    return re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")[:96] or "task"


def _failure_payload(*, repo_root: Path | None, target_path: Path | None, task_id: str | None, error: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "event": "task-run", "status": FAIL, "phase": "preflight",
        "repo_root": str(repo_root) if repo_root is not None else None,
        "worktree_path": str(target_path) if target_path is not None else None,
        "task_id": task_id, "error": error,
        "next_step": "Fix the preflight error, then rerun task run from a clean parent with an unused worktree path.",
    }


def _runtime_preview(target_path: Path) -> Path:
    preview_env = os.environ.copy()
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        preview_env.pop(key, None)
    return runtime_root(target_path, preview_env)


def _execute_codex(
    command: Sequence[str], *, target_path: Path, configured_env: Mapping[str, str],
    stdout_log: Path, stderr_log: Path, timeout_seconds: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {"exit_code": None, "timed_out": False}
    try:
        with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open("w", encoding="utf-8") as stderr_handle:
            completed = subprocess.run(command, cwd=target_path, env=dict(configured_env), stdout=stdout_handle, stderr=stderr_handle, check=False, timeout=timeout_seconds, text=True)
            result["exit_code"] = completed.returncode
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
    except OSError as exc:
        result["exec_error"] = str(exc)
    return result


def _completion_evidence(
    *, target_path: Path, parent_root: Path, before_exec: Mapping[str, Sequence[str]],
    base_sha: str, scopes: Sequence[str], require_change: bool,
    parent_before: Mapping[str, Sequence[str]],
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    after_exec = _collect_populations(target_path)
    populations = _population_delta(before_exec, after_exec)
    scope = _scope_result(target_path, base_sha, scopes, require_change)
    parent_after = _collect_populations(parent_root)
    parent_unchanged = parent_after == parent_before
    evidence = {
        "after_exec": _snapshot_payload(after_exec), "populations": populations,
        "generated_files": _generated_files(populations, scopes), "scope": scope,
        "parent": {"unchanged": parent_unchanged, "before": _snapshot_payload(parent_before),
                    "after": _snapshot_payload(parent_after), "verdict": PASS if parent_unchanged else FAIL},
    }
    return evidence, scope, parent_unchanged
