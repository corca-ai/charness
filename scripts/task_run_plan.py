"""Resolve task-run shorthand and explicit preflight inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.task_run_contract import TaskRunError
from scripts.task_run_git import (
    _git_common_dir,
    _resolve_base_sha,
    _validate_branch,
    _validate_worktree_path,
)
from scripts.task_run_runtime import (
    _resolve_codex,
    _runtime_preview,
    _task_id,
    build_codex_args,
    validate_lane_id,
)
from scripts.task_run_scope import normalize_scopes, resolve_scope_specs


def resolve_task_inputs(
    resolved_repo: Path,
    *,
    target_path: Path | None,
    branch: str | None,
    base: str | None,
    lane: str | None,
    scopes: Sequence[str],
    prompt: str,
    codex: str,
    effort: str | None,
    task_id: str | None,
    prepare: bool | None,
    require_change: bool | None,
    skip_prepare: bool,
    allow_no_change: bool,
    timeout_seconds: int,
    repo_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if prepare and skip_prepare:
        raise TaskRunError("--prepare and --skip-prepare cannot be used together")
    if require_change and allow_no_change:
        raise TaskRunError("--require-change and --allow-no-change cannot be used together")
    if lane is not None:
        if any(value is not None for value in (target_path, branch, base)):
            raise TaskRunError(
                "--lane cannot be combined with --path, --branch, or --base; "
                "choose shorthand or the fully explicit form"
            )
        if task_id is not None:
            raise TaskRunError("--task-id is derived from --lane; omit it in shorthand mode")
        resolved_lane = validate_lane_id(lane)
        runtime_path = _runtime_preview(resolved_repo)
        resolved_task_id = resolved_lane
        resolved_branch = _validate_branch(resolved_repo, f"task/{resolved_lane}")
        resolved_target = _validate_worktree_path(
            resolved_repo, runtime_path / "task-run" / resolved_task_id / "worktree"
        )
        resolved_base = "HEAD"
        resolved_prepare = not skip_prepare if prepare is None else prepare
        resolved_require_change = (
            not allow_no_change if require_change is None else require_change
        )
    else:
        if any(value is None for value in (target_path, branch, base)):
            raise TaskRunError(
                "explicit task runs require --path, --branch, and --base; "
                "otherwise pass --lane <id>"
            )
        resolved_lane = None
        resolved_target = _validate_worktree_path(resolved_repo, target_path)
        resolved_branch = _validate_branch(resolved_repo, branch)
        resolved_base = base
        resolved_prepare = bool(prepare) and not skip_prepare
        resolved_require_change = bool(require_change) and not allow_no_change
    if not prompt.strip():
        raise TaskRunError("--prompt or --prompt-file must contain non-empty instructions")
    if effort is None:
        raise TaskRunError("task runs require the orchestrator-selected --effort")
    if repo_snapshot is not None and resolved_base == "HEAD":
        base_sha = str(repo_snapshot["head"])
    else:
        base_sha = _resolve_base_sha(resolved_repo, resolved_base)
    normalized_scopes = normalize_scopes(scopes)
    scope_specs = resolve_scope_specs(resolved_repo, normalized_scopes, base_sha)
    git_common_dir = (
        Path(repo_snapshot["git_common_dir"])
        if repo_snapshot is not None
        else _git_common_dir(resolved_repo)
    )
    codex_path = _resolve_codex(codex)
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise TaskRunError("--timeout-seconds must be a positive integer")
    if lane is None:
        resolved_task_id = _task_id(resolved_branch, task_id)
        runtime_path = _runtime_preview(resolved_repo)
    build_codex_args(effort=effort)
    return {
        "lane": resolved_lane,
        "target_path": resolved_target,
        "branch": resolved_branch,
        "base": resolved_base,
        "base_sha": base_sha,
        "git_common_dir": git_common_dir,
        "scopes": normalized_scopes,
        "scope_specs": scope_specs,
        "codex_path": codex_path,
        "effort": effort,
        "task_id": resolved_task_id,
        "runtime_path": runtime_path,
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
    }
