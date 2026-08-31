"""Run one bounded Codex task in a clean, disposable Git worktree."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from runtime_bootstrap import import_repo_module
from scripts import task_run_completion as _completion
from scripts import task_run_support as _support
from scripts.task_run_git import _repo_snapshot
from scripts.task_run_plan import resolve_task_inputs as _resolve_task_inputs
from scripts.task_run_state import (
    _abnormal_exit_state,
    _candidate_result_state,
    _execution_state,
)

_worktree = import_repo_module(__file__, "scripts.worktree_create_lib")
_exec = import_repo_module(__file__, "scripts.worktree_exec_lib")

PASS = _support.PASS
FAIL = _support.FAIL
TaskRunError = _support.TaskRunError
_collect_populations = _support._collect_populations
_completion_evidence = _support._completion_evidence
_execute_codex = _support._execute_codex
_failure_payload = _support._failure_payload
_git = _support._git
_git_common_dir = _support._git_common_dir
_git_dir = _support._git_dir
_git_output = _support._git_output
_population_delta = _support._population_delta
_resolve_base_sha = _support._resolve_base_sha
_resolve_codex = _support._resolve_codex
_runtime_preview = _support._runtime_preview
_task_execution_runtime_root = _support.task_execution_runtime_root
_snapshot_payload = _support._snapshot_payload
_task_id = _support._task_id
_validate_branch = _support._validate_branch
_validate_worktree_path = _support._validate_worktree_path
_validate_lane_id = _support.validate_lane_id
build_codex_args = _support.build_codex_args
build_codex_command = _support.build_codex_command
normalize_scopes = _support.normalize_scopes


def _persist(payload: dict[str, Any], runtime_path: Path) -> None:
    _support.write_task_result(runtime_path, payload)


def _persist_completion(payload: dict[str, Any], runtime_path: Path) -> None:
    candidate = payload.get("candidate")
    if (
        payload.get("status") == "completed"
        and isinstance(candidate, dict)
        and candidate.get("status") == "validated"
        and not candidate.get("head_is_complete", True)
    ):
        if candidate.get("carrier_kind") == "worktree-only":
            payload["next_step"] = (
                f"Review the complete validated candidate in {payload['worktree_path']}; "
                "no lane commit exists, so lane HEAD is not the complete candidate."
            )
        else:
            payload["next_step"] = (
                f"Review the complete validated candidate in {payload['worktree_path']}; "
                "the lane HEAD commit is a proper subset of the complete candidate. "
                "Carry the committed_paths and dirty_paths before treating it as integrated."
            )
    _persist(payload, runtime_path)


def _checkout_own_dir(create_payload: dict[str, Any]) -> Path:
    """Validate the checkout-specific Git dir carried by worktree creation."""
    carrier = create_payload.get("_checkout")
    if not isinstance(carrier, dict):
        raise TaskRunError("worktree create payload is missing checkout metadata")
    raw = carrier.get("own_dir")
    if not isinstance(raw, str) or not raw or raw != raw.strip():
        raise TaskRunError("worktree create payload has malformed checkout own_dir")
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise TaskRunError("worktree create payload checkout own_dir must be absolute")
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise TaskRunError("worktree create payload has unusable checkout own_dir") from exc
    if not resolved.is_dir():
        raise TaskRunError(
            f"worktree create payload checkout own_dir is not an existing directory: {resolved}"
        )
    return resolved


def _terminal(
    payload: dict[str, Any],
    runtime_path: Path,
    *,
    status: str,
    next_step: str,
    error: str | None = None,
) -> dict[str, Any]:
    payload.update(
        {
            "status": status,
            "phase": "terminal",
            "approval_eligibility": "ineligible",
            "next_step": next_step,
        }
    )
    if error is not None:
        payload["error"] = error
    _persist(payload, runtime_path)
    return payload










def _complete_task(
    payload: dict[str, Any],
    *,
    runtime_path: Path,
    resolved_target: Path,
    resolved_repo: Path,
    before_exec: dict[str, list[str]],
    base_sha: str,
    scope_specs: list[dict[str, Any]],
    require_change: bool,
    parent_before: dict[str, list[str]],
    parent_before_head: str,
    stdout_log: Path,
    execution: dict[str, Any],
    started_at: float,
    candidate_commit: dict[str, Any] | None,
    target_head: str | None = None,
) -> dict[str, Any]:
    return _completion.complete_task(
        payload,
        runtime_path=runtime_path,
        resolved_target=resolved_target,
        resolved_repo=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scope_specs=scope_specs,
        require_change=require_change,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
        stdout_log=stdout_log,
        execution=execution,
        started_at=started_at,
        candidate_commit=candidate_commit,
        target_head=target_head,
        persist=_persist_completion,
        result_delivery=_support._result_delivery,
        completion_evidence=_completion_evidence,
        execution_state=_execution_state,
        candidate_result_state=_candidate_result_state,
        git=_git,
        git_output=_git_output,
        pass_value=PASS,
    )


def run_task(
    repo_root: Path,
    *,
    target_path: Path | None = None,
    branch: str | None = None,
    base: str | None = None,
    lane: str | None = None,
    scopes: Sequence[str],
    prompt: str,
    codex: str = "codex",
    effort: str | None = None,
    task_id: str | None = None,
    prepare: bool | None = None,
    require_change: bool | None = None,
    skip_prepare: bool = False,
    allow_no_change: bool = False,
    timeout_seconds: int = 3600,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create, run, and receipt one bounded Codex worktree task."""
    resolved_repo: Path | None = None
    resolved_target: Path | None = None
    try:
        repo_snapshot = _repo_snapshot(repo_root)
        resolved_repo = repo_snapshot["repo_root"]
        parent_before = _collect_populations(resolved_repo)
        parent_before_head = str(repo_snapshot["head"])
        if any(parent_before[population] for population in ("tracked", "untracked")):
            raise TaskRunError(
                "parent worktree must be clean before launching a task; "
                "checkpoint current changes or choose a clean named worktree"
            )
        resolved = _resolve_task_inputs(
            resolved_repo,
            target_path=target_path,
            branch=branch,
            base=base,
            lane=lane,
            scopes=scopes,
            prompt=prompt,
            codex=codex,
            effort=effort,
            task_id=task_id,
            prepare=prepare,
            require_change=require_change,
            skip_prepare=skip_prepare,
            allow_no_change=allow_no_change,
            timeout_seconds=timeout_seconds,
            repo_snapshot=repo_snapshot,
        )
    except (OSError, TaskRunError, subprocess.SubprocessError) as exc:
        return _failure_payload(
            repo_root=resolved_repo or repo_root.expanduser().resolve(),
            target_path=(resolved_target or target_path or Path.cwd()).expanduser().resolve(),
            task_id=task_id,
            error=str(exc),
        )

    resolved_lane = resolved["lane"]
    resolved_target = resolved["target_path"]
    resolved_branch = resolved["branch"]
    resolved_base = resolved["base"]
    base_sha = resolved["base_sha"]
    normalized_scopes = resolved["scopes"]
    codex_path = resolved["codex_path"]
    resolved_task_id = resolved["task_id"]
    runtime_path = resolved["runtime_path"]
    execution_runtime_path = _task_execution_runtime_root(runtime_path, resolved_task_id)
    resolved_prepare = resolved["prepare"]
    resolved_require_change = resolved["require_change"]
    payload: dict[str, Any] = {
        "schema_version": _support.SCHEMA_VERSION,
        "event": "task-run",
        "status": FAIL,
        "phase": "planned" if dry_run else "running",
        "approval_eligibility": "ineligible",
        "dry_run": dry_run,
        "task_id": resolved_task_id,
        "repo_root": str(resolved_repo),
        "worktree_path": str(resolved_target),
        "branch": resolved_branch,
        "base": resolved_base,
        "base_sha": base_sha,
        "git_common_dir": str(resolved["git_common_dir"]),
        "scopes": normalized_scopes,
        "scope_specs": resolved["scope_specs"],
        "codex": {
            "executable": codex_path,
            "model": _support.TASK_MODEL,
            "effort": resolved["effort"],
        },
        "runtime_root": str(runtime_path),
        "execution_runtime_root": str(execution_runtime_path),
        "result_path": str(_support.task_result_path(runtime_path, resolved_task_id)),
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
        "keep_worktree": True,
    }
    if resolved_lane is not None:
        payload["lane"] = resolved_lane
    if dry_run:
        payload["status"] = PASS
        payload["approval_eligibility"] = "not-applicable"
        payload["next_step"] = "Re-run without --dry-run to create the named worktree and execute Codex."
        payload["actions"] = [
            {"id": "create-worktree", "status": "planned"},
            {"id": "codex-exec", "status": "planned", "cwd": str(resolved_target)},
        ]
        return payload

    payload["status"] = "running"
    payload["phase"] = "create"
    _persist(payload, runtime_path)
    started_at = time.monotonic()
    try:
        resolved_target.parent.mkdir(parents=True, exist_ok=True)
        create_payload = _worktree.run_create(
            resolved_repo,
            target_path=resolved_target,
            branch=resolved_branch,
            base=base_sha,
            prepare=resolved_prepare,
        )
    except KeyboardInterrupt:
        return _terminal(
            payload,
            runtime_path,
            status="interrupted",
            next_step="Task creation was interrupted; inspect the target path before retrying with a fresh path.",
        )
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        return _terminal(
            payload,
            runtime_path,
            status="failed",
            error=str(exc),
            next_step="Task worktree creation failed; inspect the error and retry with a fresh path.",
        )

    payload["create"] = create_payload
    payload["created"] = bool(create_payload.get("created"))
    if not create_payload.get("created") or (
        resolved_prepare and create_payload.get("status") != PASS
    ):
        return _terminal(
            payload,
            runtime_path,
            status="failed",
            next_step=create_payload.get("next_step")
            or "Fix worktree creation/doctor, then rerun task run.",
        )

    try:
        git_worktree_dir = _checkout_own_dir(create_payload)
        configured_env = _exec.prepare_exec_environment(
            resolved_target,
            os.environ.copy(),
            runtime_root=execution_runtime_path,
        )
        command = build_codex_command(
            codex_path,
            effort=resolved["effort"],
            writable_dirs=[
                resolved["git_common_dir"],
                git_worktree_dir,
                execution_runtime_path,
            ],
        )
        payload["git_worktree_dir"] = str(git_worktree_dir)
        payload["codex"]["command"] = command

        scope_specs = resolved["scope_specs"]
        before_exec = _collect_populations(resolved_target)
        payload["before_exec"] = _snapshot_payload(before_exec)
        preflight_populations = _population_delta({}, before_exec, preflight=True)
        payload["preflight_populations"] = preflight_populations
        if any(
            preflight_populations[name]["verdict"] == FAIL
            for name in ("tracked", "untracked")
        ):
            return _terminal(
                payload,
                runtime_path,
                status="failed",
                next_step="The newly-created worktree was not clean before Codex; inspect it and use a fresh path.",
            )

        log_dir = runtime_path / "task-run" / resolved_task_id
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_log = log_dir / "codex.stdout.log"
        stderr_log = log_dir / "codex.stderr.log"
        payload["logs"] = {"stdout": str(stdout_log), "stderr": str(stderr_log)}
        payload["phase"] = "exec"
        _persist(payload, runtime_path)

        print(f"task run: executing Codex in {resolved_target}", file=sys.stderr)
        execution = _execute_codex(
            command,
            prompt=prompt,
            target_path=resolved_target,
            configured_env=configured_env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            timeout_seconds=timeout_seconds,
        )
        candidate_commit = None
        abnormal = _abnormal_exit_state(execution)
        if abnormal is not None:
            try:
                candidate_commit = _support._commit_wip_candidate(resolved_target)
            except (OSError, RuntimeError, TypeError, TaskRunError, subprocess.SubprocessError) as exc:
                payload["execution"] = {**execution, "status": abnormal}
                payload["candidate"] = {
                    "status": "wip",
                    "useful": False,
                    "changed_paths": [],
                    "state": "interrupted-mid-edit",
                    "state_known": False,
                    "commit": {
                        "status": "failed",
                        "error": str(exc),
                        "correctness_verified": False,
                    },
                }
                return _terminal(
                    payload,
                    runtime_path,
                    status=abnormal,
                    error=f"{abnormal} WIP candidate commit failed: {exc}",
                    next_step=(
                        f"The {abnormal} WIP checkpoint could not be committed; inspect and "
                        "recover the retained worktree manually."
                    ),
                )
        return _complete_task(
            payload,
            runtime_path=runtime_path,
            resolved_target=resolved_target,
            resolved_repo=resolved_repo,
            before_exec=before_exec,
            base_sha=base_sha,
            scope_specs=scope_specs,
            require_change=resolved_require_change,
            parent_before=parent_before,
            parent_before_head=parent_before_head,
            stdout_log=stdout_log,
            execution=execution,
            started_at=started_at,
            candidate_commit=candidate_commit,
            target_head=(
                str(candidate_commit["sha"])
                if candidate_commit is not None and candidate_commit.get("status") == "committed"
                else None
            ),
        )
    except KeyboardInterrupt:
        return _terminal(
            payload,
            runtime_path,
            status="interrupted",
            next_step="Task lifecycle was interrupted; inspect the retained worktree before retrying.",
        )
    except (OSError, RuntimeError, TypeError, TaskRunError, subprocess.SubprocessError) as exc:
        return _terminal(
            payload,
            runtime_path,
            status="failed",
            error=f"task lifecycle failed: {exc}",
            next_step="Inspect the retained worktree and lifecycle error, then retry with a fresh lane.",
        )


def task_status(repo_root: Path, task_id: str | None = None) -> dict[str, Any]:
    """Read the one external task-run result store without mutation."""
    resolved_repo = _support._require_git_root(repo_root)
    runtime_path = _support.task_runtime_root(resolved_repo)
    if task_id is not None:
        record = _support.read_task_result(runtime_path, task_id)
        if record is not None:
            return record
        return {
            "schema_version": _support.SCHEMA_VERSION,
            "event": "task-status",
            "repo_root": str(resolved_repo),
            "task_id": task_id,
            "status": "missing",
            "result_path": str(_support.task_result_path(runtime_path, task_id)),
        }
    return {
        "schema_version": _support.SCHEMA_VERSION,
        "event": "task-status-list",
        "repo_root": str(resolved_repo),
        "runtime_root": str(runtime_path),
        "tasks": _support.read_task_results(runtime_path),
    }
