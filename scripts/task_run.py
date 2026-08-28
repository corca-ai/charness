"""Run one bounded Codex task in a clean, disposable Git worktree.

This is the execution half of the ``charness task`` surface.  ``run_task`` keeps
the orchestration small; Git, scope, runtime, and receipt calculations live in
``task_run_support`` so the public wrapper remains easy to audit.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime_bootstrap import import_repo_module

_worktree = import_repo_module(__file__, "scripts.worktree_create_lib")
_exec = import_repo_module(__file__, "scripts.worktree_exec_lib")
try:
    from scripts import task_run_support as _support
except ModuleNotFoundError:
    import task_run_support as _support

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


def _execution_state(execution: dict[str, Any], delivery: dict[str, Any]) -> str:
    if execution["interrupted"] or (
        execution["exit_code"] is not None and execution["exit_code"] < 0
    ):
        return "interrupted"
    if execution["timed_out"]:
        return "timed-out"
    if execution.get("exec_error") or execution["exit_code"] is None:
        return "failed"
    if execution["exit_code"] != 0:
        return "failed"
    if delivery["status"] == "non-delivery":
        return "non-delivery"
    return "completed"


def _candidate_result_state(
    *,
    execution_state: str,
    scope: dict[str, Any],
    parent_progress: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    changed_paths = scope["changed_paths"]
    candidate_valid = scope["verdict"] == PASS
    candidate_useful = candidate_valid and bool(changed_paths)
    candidate = {
        "status": (
            "validated"
            if candidate_useful
            else "absent"
            if candidate_valid
            else "invalid"
        ),
        "useful": candidate_useful,
        "changed_paths": changed_paths,
    }
    if candidate_valid and execution_state == "completed" and not parent_progress["blocking"]:
        return candidate, "completed"
    if candidate_useful:
        return candidate, "validated-partial-result"
    if not candidate_valid or parent_progress["blocking"]:
        return candidate, "failed"
    return candidate, execution_state


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
) -> dict[str, Any]:
    delivery = _support._result_delivery(stdout_log)
    evidence, scope, parent_progress = _completion_evidence(
        target_path=resolved_target,
        parent_root=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scope_specs=scope_specs,
        require_change=require_change,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
    )
    target_branch = (
        _git_output(
            resolved_target,
            "symbolic-ref",
            "--quiet",
            "--short",
            "HEAD",
        ).strip()
        if _git(
            resolved_target,
            "symbolic-ref",
            "--quiet",
            "--short",
            "HEAD",
        ).returncode
        == 0
        else None
    )
    payload.update(
        {
            "phase": "terminal",
            "execution": execution,
            "result_delivery": delivery,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
            "target_sha": _git_output(resolved_target, "rev-parse", "HEAD").strip(),
            "target_branch": target_branch,
            **evidence,
        }
    )
    structured = delivery.get("structured")
    if (
        isinstance(structured, Mapping)
        and structured.get("schema_version") == "charness.reviewer_lifecycle.v1"
    ):
        payload["reviewer_lifecycle"] = structured

    execution_status = _execution_state(execution, delivery)
    payload["execution"]["status"] = execution_status
    candidate, result_state = _candidate_result_state(
        execution_state=execution_status,
        scope=scope,
        parent_progress=parent_progress,
    )
    payload["candidate"] = candidate
    payload["status"] = result_state
    payload["approval_eligibility"] = (
        "eligible" if result_state == "completed" else "ineligible"
    )

    blockers: list[str] = []
    if execution_status != "completed":
        blockers.append(f"execution: {execution_status}")
    if scope["verdict"] != PASS:
        blockers.append(scope["reason"])
    if parent_progress["blocking"]:
        blockers.append("parent changed within the resolved candidate scope")

    warnings = [
        f"{population}: {data['reason']}"
        for population, data in evidence["populations"].items()
        if data.get("verdict") == "warn"
    ]
    if parent_progress["classification"] == "concurrent-parent-progress":
        warnings.append("parent made disjoint progress while the task ran")
    if warnings:
        payload["warnings"] = warnings

    if blockers:
        payload["next_step"] = (
            "Inspect the retained worktree, typed result, and captured logs; "
            + "; ".join(blockers)
            + "."
        )
    elif result_state == "validated-partial-result":
        payload["next_step"] = (
            f"Review the validated candidate in {resolved_target}; "
            "it is useful but not approval-eligible."
        )
    else:
        payload["next_step"] = (
            f"Review the candidate in {resolved_target}; "
            "the typed result is approval-eligible."
        )
    _persist(payload, runtime_path)
    print(f"task run: {payload['status']} ({payload['task_id']})", file=sys.stderr)
    return payload


def _resolve_task_inputs(
    resolved_repo: Path,
    *,
    target_path: Path | None,
    branch: str | None,
    base: str | None,
    lane: str | None,
    scopes: Sequence[str],
    prompt: str,
    codex: str,
    codex_args: Sequence[str],
    effort: str | None,
    task_id: str | None,
    prepare: bool | None,
    require_change: bool | None,
    skip_prepare: bool,
    allow_no_change: bool,
    timeout_seconds: int,
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
        resolved_lane = _validate_lane_id(lane)
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
    normalized_scopes = normalize_scopes(scopes)
    scope_specs = _support.resolve_scope_specs(resolved_repo, normalized_scopes)
    if not prompt.strip():
        raise TaskRunError("--prompt or --prompt-file must contain non-empty instructions")
    if effort is None and lane is not None:
        raise TaskRunError("shorthand task runs require the orchestrator-selected --effort")
    base_sha = _resolve_base_sha(resolved_repo, resolved_base)
    git_common_dir = _git_common_dir(resolved_repo)
    codex_path = _resolve_codex(codex)
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise TaskRunError("--timeout-seconds must be a positive integer")
    if lane is None:
        resolved_task_id = _task_id(resolved_branch, task_id)
        runtime_path = _runtime_preview(resolved_repo)
    command = build_codex_command(
        codex_path,
        prompt,
        effort=effort,
        writable_dirs=[git_common_dir],
        extra=codex_args,
    )
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
        "command": command,
        "codex_args": list(codex_args),
        "effort": effort,
        "task_id": resolved_task_id,
        "runtime_path": runtime_path,
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
    }


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
    codex_args: Sequence[str] = (),
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
        resolved_repo = _support._require_git_root(repo_root)
        parent_before = _collect_populations(resolved_repo)
        parent_before_head = _git_output(resolved_repo, "rev-parse", "HEAD").strip()
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
            codex_args=codex_args,
            effort=effort,
            task_id=task_id,
            prepare=prepare,
            require_change=require_change,
            skip_prepare=skip_prepare,
            allow_no_change=allow_no_change,
            timeout_seconds=timeout_seconds,
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
    command = resolved["command"]
    resolved_task_id = resolved["task_id"]
    runtime_path = resolved["runtime_path"]
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
        "codex": {"executable": codex_path, "command": command[:-1] + ["<prompt>"]},
        "runtime_root": str(runtime_path),
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
            base=resolved_base,
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

    git_worktree_dir = _git_dir(resolved_target)
    command = build_codex_command(
        codex_path,
        prompt,
        effort=resolved["effort"],
        writable_dirs=[resolved["git_common_dir"], git_worktree_dir],
        extra=resolved["codex_args"],
    )
    payload["git_worktree_dir"] = str(git_worktree_dir)
    payload["codex"]["command"] = command[:-1] + ["<prompt>"]

    scope_specs = resolved["scope_specs"]
    before_exec = _collect_populations(resolved_target)
    payload["before_exec"] = _snapshot_payload(before_exec)
    preflight_populations = _population_delta({}, before_exec, preflight=True)
    payload["preflight_populations"] = preflight_populations
    if any(preflight_populations[name]["verdict"] == FAIL for name in ("tracked", "untracked")):
        return _terminal(
            payload,
            runtime_path,
            status="failed",
            next_step="The newly-created worktree was not clean before Codex; inspect it and use a fresh path.",
        )

    child_env = os.environ.copy()
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        child_env.pop(key, None)
    child_env["CHARNESS_RUNTIME_ROOT"] = str(runtime_path)
    configured_env = _exec.prepare_exec_environment(resolved_target, child_env)
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
        target_path=resolved_target,
        configured_env=configured_env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=timeout_seconds,
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


def main() -> int:
    """Standalone diagnostic entrypoint; the canonical surface is ``charness task run``."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--lane")
    parser.add_argument("--path", dest="target_path", type=Path)
    parser.add_argument("--branch")
    parser.add_argument("--base")
    parser.add_argument(
        "--scope",
        action="append",
        required=True,
        help="Repository-relative path or quoted glob; globs must match before launch.",
    )
    prompt = parser.add_mutually_exclusive_group(required=True)
    prompt.add_argument("--prompt")
    prompt.add_argument("--prompt-file", type=Path)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--effort", help="Orchestrator-selected effort: medium, xhigh, or max.")
    parser.add_argument("--codex-arg", action="append", default=[])
    parser.add_argument("--task-id", help="Optional receipt/log identifier for explicit runs; shorthand derives it from --lane.")
    parser.add_argument("--prepare", action="store_true", default=None)
    parser.add_argument("--require-change", action="store_true", default=None)
    parser.add_argument("--skip-prepare", action="store_true")
    parser.add_argument("--allow-no-change", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prompt_text = args.prompt
    if args.prompt_file is not None:
        prompt_text = args.prompt_file.read_text(encoding="utf-8")
    payload = run_task(
        args.repo_root,
        target_path=args.target_path,
        branch=args.branch,
        base=args.base,
        lane=args.lane,
        scopes=args.scope,
        prompt=prompt_text or "",
        codex=args.codex,
        codex_args=args.codex_arg,
        effort=args.effort,
        task_id=args.task_id,
        prepare=args.prepare,
        require_change=args.require_change,
        skip_prepare=args.skip_prepare,
        allow_no_change=args.allow_no_change,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    from yaml_output import emit_yaml

    emit_yaml(payload)
    return 0 if payload.get("approval_eligibility") == "eligible" or payload.get("status") == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
