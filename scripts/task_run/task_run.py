"""Run one bounded Codex task in a clean, disposable Git worktree."""

from __future__ import annotations

import os
import subprocess
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

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.task_run import task_run_changed_line as _changed_line  # noqa: E402
from scripts.task_run import task_run_completion as _completion  # noqa: E402
from scripts.task_run import task_run_friction as _friction  # noqa: E402
from scripts.task_run import task_run_lane_options as _lane_options  # noqa: E402
from scripts.task_run import task_run_lane_runner as _lane_runner  # noqa: E402
from scripts.task_run import task_run_payload as _payload  # noqa: E402
from scripts.task_run import task_run_plan as _plan  # noqa: E402
from scripts.task_run import task_run_prelaunch as _prelaunch  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402
from scripts.task_run.task_run_git import _checkout_own_dir, _repo_snapshot  # noqa: E402
from scripts.task_run.task_run_state import (  # noqa: E402
    _abnormal_exit_state,
    _candidate_result_state,
    _execution_state,
    blocker_for_receipt,
    result_kind_for_status,
)

_worktree = import_repo_module(__file__, "scripts.worktree.worktree_create_lib")
_exec = import_repo_module(__file__, "scripts.worktree.worktree_exec_lib")

PASS = _support.PASS
FAIL = _support.FAIL
TaskRunError = _support.TaskRunError
_collect_populations = _support._collect_populations
_completion_evidence = _support._completion_evidence
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
build_muse_args = _support.build_muse_args
build_muse_command = _support.build_muse_command
normalize_scopes = _support.normalize_scopes




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
    payload["result_kind"] = result_kind_for_status(status).value
    payload["blocker"] = blocker_for_receipt(payload)
    _friction.append_terminal_friction(runtime_path, payload)
    _payload._persist(payload, runtime_path)
    return payload


def _prepare_exec_logs_and_prompt(
    payload: dict[str, Any],
    resolved: Mapping[str, Any],
    prompt: str,
    lane_prompt: str,
    runtime_path: Path,
    resolved_task_id: str,
    resolved_executor: str,
) -> tuple[dict[str, Any] | None, Path, Path, str]:
    """Create exec logs and run prelaunch gates; terminal payload first on block."""
    log_dir = runtime_path / "task-run" / resolved_task_id
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = log_dir / f"{resolved_executor}.stdout.log"
    stderr_log = log_dir / f"{resolved_executor}.stderr.log"
    payload["logs"] = {"stdout": str(stdout_log), "stderr": str(stderr_log)}
    prelaunch_blocker = _prelaunch.run_prelaunch_gates(payload, resolved, prompt)
    _payload._persist(payload, runtime_path)
    if prelaunch_blocker:
        return _terminal(
            payload, runtime_path, status="premise-blocked", next_step=prelaunch_blocker,
            error=prelaunch_blocker,
        ), stdout_log, stderr_log, lane_prompt
    return None, stdout_log, stderr_log, _prelaunch.acceptance_skeleton_prompt(lane_prompt, payload)


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
    report_only: bool = False,
    parent_before: dict[str, list[str]],
    parent_before_head: str,
    stdout_log: Path,
    stderr_log: Path | None = None,
    execution: dict[str, Any],
    started_at: float,
    candidate_commit: dict[str, Any] | None,
    target_head: str | None = None,
    self_review_prompt: str = "",
) -> dict[str, Any]:
    payload["_self_review_prompt"] = self_review_prompt
    return _completion.complete_task(
        payload,
        runtime_path=runtime_path,
        resolved_target=resolved_target,
        resolved_repo=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scope_specs=scope_specs,
        require_change=require_change,
        report_only=report_only,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        execution=execution,
        started_at=started_at,
        candidate_commit=candidate_commit,
        target_head=target_head,
        changed_line_gate=_changed_line.run_changed_line_gate,
        persist=_payload._persist_completion,
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
    executor: str | None = None,
    effort: str | None = None,
    task_id: str | None = None,
    prepare: bool | None = None,
    require_change: bool | None = None,
    skip_prepare: bool = False,
    allow_no_change: bool = False,
    timeout_seconds: int = 3600,
    dry_run: bool = False,
    report_only: bool = False,
    no_progress_seconds: float | None = None,
    self_review_policy: str = "auto",
    prelaunch: Mapping[str, Any] | None = None,
    rules_files: Sequence[str | Path] = (),
    grant_writable: Sequence[str | Path] = (),
) -> dict[str, Any]:
    """Create, run, and receipt one bounded Codex worktree task."""
    resolved_repo: Path | None = None
    resolved_target: Path | None = None
    try:
        if self_review_policy not in ("auto", "always"):
            raise TaskRunError("self_review_policy must be auto or always")
        repo_snapshot = _repo_snapshot(repo_root)
        resolved_repo = repo_snapshot["repo_root"]
        parent_before = _collect_populations(resolved_repo)
        parent_before_head = str(repo_snapshot["head"])
        if any(parent_before[population] for population in ("tracked", "untracked")):
            raise TaskRunError(
                "parent worktree must be clean before launching a task; "
                "checkpoint current changes or choose a clean named worktree"
            )
        # Launch-option refusals (grant/executor compat, rules files) precede
        # executor PATH probing so a bad flag reports itself even when no
        # executor executable is installed (#825). The keys land on `resolved`
        # via merge; resolve_task_inputs never sets them.
        early_launch_options: dict[str, Any] = {}
        _lane_options.resolve_launch_options(
            early_launch_options,
            resolved_repo,
            rules_files,
            grant_writable,
            executor=executor,
        )
        resolved = _plan.resolve_task_inputs(
            resolved_repo,
            target_path=target_path,
            branch=branch,
            base=base,
            lane=lane,
            scopes=scopes,
            prompt=prompt,
            codex=codex,
            executor=executor,
            effort=effort,
            task_id=task_id,
            prepare=prepare,
            require_change=require_change,
            skip_prepare=skip_prepare,
            allow_no_change=allow_no_change,
            timeout_seconds=timeout_seconds,
            repo_snapshot=repo_snapshot,
            report_only=report_only,
            no_progress_seconds=no_progress_seconds,
            prelaunch=prelaunch,
        )
        resolved.update(early_launch_options)
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
    resolved_executor = resolved["executor"]
    executor_order, executor_paths = resolved["executor_order"], resolved["executor_paths"]
    resolved_task_id = resolved["task_id"]
    runtime_path = resolved["runtime_path"]
    execution_runtime_path = _task_execution_runtime_root(runtime_path, resolved_task_id)
    resolved_prepare = resolved["prepare"]
    resolved_require_change = resolved["require_change"]
    resolved_report_only = resolved["report_only"]
    payload: dict[str, Any] = {
        "schema_version": _support.SCHEMA_VERSION, "event": "task-run",
        "status": FAIL, "phase": "planned" if dry_run else "running",
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
        "scope_warnings": resolved.get("scope_warnings", []),
        "executor_order": list(executor_order),
        "runtime_root": str(runtime_path),
        "execution_runtime_root": str(execution_runtime_path),
        "result_path": str(_support.task_result_path(runtime_path, resolved_task_id)),
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
        "report_only": resolved_report_only,
        "self_review_policy": self_review_policy,
        "no_progress_seconds": resolved.get("no_progress_seconds"),
        "prelaunch_plan": resolved["prelaunch"],
        "keep_worktree": True,
        "runner_pid": os.getpid(), "timestamps": {"launched_at": _support.utc_now_iso()},
        "timings_ms": {},
    }
    _lane_runner.record_lane_runner(
        payload,
        executor=resolved_executor,
        executable=codex_path,
        effort=resolved["effort"],
        timeout_seconds=timeout_seconds,
    )
    if resolved_lane is not None:
        payload["lane"] = resolved_lane
    _lane_options.record_launch_options(payload, resolved)
    if dry_run:
        _lane_options.plan_dry_run(
            payload, resolved, resolved_executor, resolved_target, PASS
        )
        return payload

    payload["status"] = "running"
    started_at = _payload._mark_phase(payload, "create", "create_started_at")
    _payload._persist(payload, runtime_path)
    try:
        resolved_target.parent.mkdir(parents=True, exist_ok=True)
        create_payload = _worktree.run_create(
            resolved_repo,
            target_path=resolved_target,
            branch=resolved_branch,
            base=base_sha,
            prepare=resolved_prepare,
            # Lanes of one repo share one installed-dependency cache under the
            # repo's runtime root, not the lane's private execution root (#792).
            dependency_cache_root=runtime_path / _worktree._doctor_lib.DEPENDENCY_CACHE_DIR_NAME,
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

    _support.record_create(payload, create_payload)
    _payload._record_timing(payload, "create", started_at)
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
        configured_env = _support.scrubbed_lane_env(
            payload,
            _exec.prepare_exec_environment(
                resolved_target,
                os.environ.copy(),
                runtime_root=execution_runtime_path,
            ),
            resolved_executor,
        )
        writable_dirs, lane_prompt, command = _lane_runner.prepare_lane_execution(
            payload,
            resolved,
            git_worktree_dir,
            execution_runtime_path,
            prompt=prompt,
            require_change=resolved_require_change,
            scopes=normalized_scopes,
            executor=resolved_executor,
            executable=codex_path,
            effort=resolved["effort"],
            worktree=resolved_target,
        )
        payload["git_worktree_dir"] = str(git_worktree_dir)
        payload["executor"]["command"] = command

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
                next_step=f"The newly-created worktree was not clean before {resolved_executor}; inspect it and use a fresh path.",
            )

        blocked, stdout_log, stderr_log, lane_prompt = _prepare_exec_logs_and_prompt(
            payload, resolved, prompt, lane_prompt, runtime_path,
            resolved_task_id, resolved_executor,
        )
        if blocked is not None:
            return blocked
        exec_started_at = _payload._mark_phase(payload, "exec", "exec_started_at")
        execution = _progress._execute_watched_lane(
            payload,
            command,
            lane_prompt=lane_prompt,
            resolved_target=resolved_target,
            configured_env=configured_env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            timeout_seconds=timeout_seconds,
            require_change=resolved_require_change,
            base_sha=base_sha,
            scope_specs=scope_specs,
            executor=resolved_executor,
            runtime_path=runtime_path,
            no_progress_seconds=resolved.get("no_progress_seconds"),
            executor_order=executor_order,
            executor_paths=executor_paths,
            fallback_context={
                **resolved,
                "git_worktree_dir": git_worktree_dir,
                "execution_runtime_path": execution_runtime_path,
                "prompt": prompt,
            },
            persist=_payload._persist,
        )
        stdout_log, stderr_log = (
            Path(payload["logs"][key]) for key in ("stdout", "stderr")
        )
        _payload._record_timing(payload, "exec", exec_started_at)
        candidate_commit = None
        abnormal = _abnormal_exit_state(execution)
        if abnormal is not None and abnormal != "executor-unavailable":
            try:
                candidate_commit = _lane_runner._checkpoint_interrupted_lane(
                    resolved_target, base_sha, scope_specs
                )
            # One line on purpose: an except tuple split across lines leaves each
            # continuation line without statement coverage, and mutants placed
            # there read as scope gaps no test can cover (#825).
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
            report_only=resolved_report_only,
            parent_before=parent_before,
            parent_before_head=parent_before_head,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            execution=execution,
            started_at=started_at,
            self_review_prompt=prompt,
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


task_status = _support.task_status
