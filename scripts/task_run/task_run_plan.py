"""Resolve task-run shorthand and explicit preflight inputs."""

from __future__ import annotations

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

from scripts.task_run.task_run_contract import (  # noqa: E402
    TASK_EXECUTOR_DEFAULT,
    TASK_EXECUTORS,
    TaskRunError,
)
from scripts.task_run.task_run_git import (  # noqa: E402
    _git_common_dir,
    _resolve_base_sha,
    _validate_branch,
    _validate_worktree_path,
)
from scripts.task_run.task_run_runtime import (  # noqa: E402
    _resolve_codex,
    _runtime_preview,
    _task_id,
    build_codex_args,
    build_muse_args,
    resolve_executor_executable,
    validate_lane_id,
)
from scripts.task_run.task_run_scope import normalize_scopes, resolve_scope_specs  # noqa: E402


def _resolve_require_change(
    *,
    require_change: bool | None,
    allow_no_change: bool,
    report_only: bool,
    default: bool,
) -> bool:
    """Whether the lane must change at least one path (#827).

    Report-only lanes never require a change. Otherwise shorthand lanes
    require one unless `--allow-no-change` opts out, while explicit lanes
    require one only when `--require-change` is passed.
    """
    if report_only and require_change:
        raise TaskRunError(
            "--report-only cannot be used with --require-change; "
            "a report-only lane must leave the worktree unchanged"
        )
    if report_only:
        return False
    if require_change is None:
        return default and not allow_no_change
    return bool(require_change) and not allow_no_change


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
    executor: str | None = None,
    effort: str | None = None,
    task_id: str | None,
    prepare: bool | None,
    require_change: bool | None,
    skip_prepare: bool,
    allow_no_change: bool,
    timeout_seconds: int,
    repo_snapshot: Mapping[str, Any] | None = None,
    report_only: bool = False,
) -> dict[str, Any]:
    if prepare and skip_prepare:
        raise TaskRunError("--prepare and --skip-prepare cannot be used together")
    if require_change and allow_no_change:
        raise TaskRunError("--require-change and --allow-no-change cannot be used together")
    resolved_executor = executor or TASK_EXECUTOR_DEFAULT
    if resolved_executor not in TASK_EXECUTORS:
        allowed_executors = ", ".join(TASK_EXECUTORS)
        raise TaskRunError(f"--executor must be one of: {allowed_executors}")
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
        resolved_require_change = _resolve_require_change(
            require_change=require_change,
            allow_no_change=allow_no_change,
            report_only=report_only,
            default=True,
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
        resolved_require_change = _resolve_require_change(
            require_change=require_change,
            allow_no_change=allow_no_change,
            report_only=report_only,
            default=False,
        )
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
    if resolved_executor == "codex" and codex == "codex":
        codex_path = _resolve_codex(codex)
    else:
        executable_name = codex if codex != "codex" else resolved_executor
        codex_path = resolve_executor_executable(
            executable_name, executor=resolved_executor
        )
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise TaskRunError("--timeout-seconds must be a positive integer")
    if lane is None:
        resolved_task_id = _task_id(resolved_branch, task_id)
        runtime_path = _runtime_preview(resolved_repo)
    if resolved_executor == "muse":
        # Validate the muse effort preset; the real prompt file and worktree
        # are written at execution time, these paths only exercise validation.
        build_muse_args(
            effort=effort, prompt_file=Path("prompt.md"), worktree=Path("worktree")
        )
    else:
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
        "executor": resolved_executor,
        "effort": effort,
        "task_id": resolved_task_id,
        "runtime_path": runtime_path,
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
        "report_only": report_only,
    }
