"""Same-worktree attempt loop for transient executor stalls (#829).

A retryable stall (typed by `classify_failure`, e.g. a model-stream idle
timeout) reruns the same prompt in the same worktree until the attempt
budget is spent; every attempt is recorded on `payload["attempts"]`.
Executor (agent-runner) sessions are stateless, so each attempt starts a
fresh agent session; the lane worktree (files and lane-branch commits) is
the resume state -- the candidate carrier -- that persists across attempts.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_lane_runner as _lane_runner  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_runtime as _runtime  # noqa: E402
from scripts.task_run import task_run_state as _state  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

_exec = import_repo_module(__file__, "scripts.worktree.worktree_exec_lib")

#: Total executor runs per lane: the first attempt plus up to two
#: same-worktree retries by default.
MAX_ATTEMPTS_ENV = "CHARNESS_TASK_RUN_MAX_ATTEMPTS"
RETRY_BACKOFF_ENV = "CHARNESS_TASK_RUN_RETRY_BACKOFF_SECONDS"
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_RETRY_BACKOFF_SECONDS = 30.0


def _env_attempts(name: str, default: int) -> int:
    """A tuned attempt budget from the environment, at least one attempt."""
    try:
        value = int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default
    return value if value >= 1 else default


def _persist_live(runtime_path: Path | None, payload: dict[str, Any]) -> None:
    """Publish the running receipt; a failed write never fails the lane."""
    if runtime_path is None:
        return
    try:
        _runtime.write_task_result(runtime_path, payload)
    except OSError:
        pass


def _rotate_attempt_logs(stdout_log: Path, stderr_log: Path, attempt: int) -> dict[str, str]:
    """Rotate a spent attempt's logs aside so the retry starts clean transcripts."""
    rotated = {}
    for log in (stdout_log, stderr_log):
        target = log.with_name(f"{log.stem}.attempt{attempt}{log.suffix}")
        try:
            if log.is_file():
                log.rename(target)
                rotated[log.name] = str(target)
        except OSError:
            continue
    return rotated


def _execute_watched_lane(
    payload: dict[str, Any],
    command: list[str],
    *,
    lane_prompt: str,
    resolved_target: Path,
    configured_env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
    require_change: bool,
    base_sha: str,
    scope_specs: list[dict[str, Any]],
    executor: str = "codex",
    runtime_path: Path | None = None,
    no_progress_seconds: float | None = None,
    executor_order: Sequence[str] | None = None,
    executor_paths: Mapping[str, str] | None = None,
    fallback_context: Mapping[str, Any] | None = None,
    persist: Callable[[dict[str, Any], Path], Any] | None = None,
) -> dict[str, Any]:
    """Run the lane executor under its live progress guard, retrying stalls."""
    if executor_order is not None and len(executor_order) > 1:
        if executor_paths is None or fallback_context is None or runtime_path is None or persist is None:
            raise ValueError("ordered executor fallback is missing its preparation context")
        return _execute_ordered_lane(
            payload,
            command,
            executor_order=executor_order,
            executor_paths=executor_paths,
            fallback_context=fallback_context,
            lane_prompt=lane_prompt,
            resolved_target=resolved_target,
            configured_env=configured_env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            timeout_seconds=timeout_seconds,
            require_change=require_change,
            base_sha=base_sha,
            scope_specs=scope_specs,
            executor=executor,
            runtime_path=runtime_path,
            no_progress_seconds=no_progress_seconds,
            persist=persist,
        )
    max_attempts = _env_attempts(MAX_ATTEMPTS_ENV, DEFAULT_MAX_ATTEMPTS)
    backoff = _progress._env_seconds(RETRY_BACKOFF_ENV, DEFAULT_RETRY_BACKOFF_SECONDS)
    if persist is not None and runtime_path is not None:
        persist(payload, runtime_path)
    print(f"task run: executing {executor} in {resolved_target}", file=sys.stderr)
    attempts: list[dict[str, Any]] = []
    attempt = 0
    execution: dict[str, Any] = {"exit_code": None, "timed_out": False, "interrupted": False}
    while True:
        attempt += 1

        def observe(snapshot: dict[str, Any], attempt: int = attempt) -> None:
            payload["live"] = {**snapshot, "attempt": attempt, "watched": True}
            _persist_live(runtime_path, payload)

        lane_watch = _progress.build_progress_watch(
            require_change=require_change,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            worktree=resolved_target,
            base_sha=base_sha,
            scope_specs=scope_specs,
            observe=observe,
            budget_override=no_progress_seconds,
        )
        execution = _execution._execute_codex(
            command,
            prompt=lane_prompt,
            target_path=resolved_target,
            configured_env=configured_env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            timeout_seconds=timeout_seconds,
            lane_watch=lane_watch,
            executor=executor,
        )
        if lane_watch is not None:
            payload["progress_guard"] = lane_watch.receipt()
        failure = _state.classify_failure(
            execution, stderr_text=_progress._lane_stderr_text(stdout_log, stderr_log)
        )
        record: dict[str, Any] = {
            "attempt": attempt,
            "executor": executor,
            "started_at": _support.utc_now_iso(),
            "failure_kind": failure["kind"],
            "retried": False,
            "logs": {"stdout": str(stdout_log), "stderr": str(stderr_log)},
        }
        if failure.get("retry_after") is not None:
            record["retry_after"] = failure["retry_after"]
        if failure["retryable"] and attempt < max_attempts:
            record["retried"] = True
            record["logs"] = _rotate_attempt_logs(stdout_log, stderr_log, attempt)
            attempts.append(record)
            time.sleep(backoff if backoff > 0 else 0)
            continue
        attempts.append(record)
        break
    payload["attempts"] = attempts
    if "live" not in payload:
        payload["live"] = {"watched": False, "attempt": attempt, "phase": None}
    return execution


def _prepare_fallback_executor(
    payload: dict[str, Any],
    executor: str,
    executable: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the next runner command while retaining the current lane candidate."""
    resolved = context
    if executor == "muse":
        payload.pop("codex", None)
        payload.pop("writable_dirs", None)
    else:
        payload.pop("workspace", None)
    _lane_runner.record_lane_runner(
        payload,
        executor=executor,
        executable=executable,
        effort=context["effort"],
        timeout_seconds=context["timeout_seconds"],
    )
    next_resolved = {**resolved, "executor": executor, "codex_path": executable}
    configured_env = _support.scrubbed_lane_env(
        payload,
        _exec.prepare_exec_environment(
            context["target_path"],
            os.environ.copy(),
            runtime_root=context["execution_runtime_path"],
        ),
        executor,
    )
    _writable_dirs, lane_prompt, command = _lane_runner.prepare_lane_execution(
        payload,
        next_resolved,
        context["git_worktree_dir"],
        context["execution_runtime_path"],
        prompt=context["prompt"],
        require_change=context["require_change"],
        scopes=context["scopes"],
        executor=executor,
        executable=executable,
        effort=context["effort"],
        worktree=context["target_path"],
    )
    payload["executor"]["command"] = command
    return {
        "executor": executor,
        "command": command,
        "lane_prompt": lane_prompt,
        "configured_env": configured_env,
    }


def _execute_ordered_lane(
    payload: dict[str, Any],
    command: list[str],
    *,
    executor_order: Sequence[str],
    executor_paths: Mapping[str, str],
    fallback_context: Mapping[str, Any],
    lane_prompt: str,
    resolved_target: Path,
    configured_env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
    require_change: bool,
    base_sha: str,
    scope_specs: list[dict[str, Any]],
    executor: str,
    runtime_path: Path,
    no_progress_seconds: float | None,
    persist: Callable[[dict[str, Any], Path], Any],
) -> dict[str, Any]:
    """Try the next executor only when the current attempt proves a quota limit."""
    attempt_history: list[dict[str, Any]] = []
    execution: dict[str, Any] = {}
    current_command, current_prompt, current_env = command, lane_prompt, configured_env
    current_stdout, current_stderr, current_executor = stdout_log, stderr_log, executor
    log_dir = stdout_log.parent
    for index, candidate in enumerate(executor_order):
        if index:
            print(
                f"task run: {current_executor} unavailable; trying {candidate}",
                file=sys.stderr,
            )
            prepared = _prepare_fallback_executor(
                payload, candidate, executor_paths[candidate], fallback_context
            )
            current_executor = prepared["executor"]
            current_command = prepared["command"]
            current_prompt = prepared["lane_prompt"]
            current_env = prepared["configured_env"]
            current_stdout = log_dir / f"{current_executor}.stdout.log"
            current_stderr = log_dir / f"{current_executor}.stderr.log"
        payload["logs"] = {
            "stdout": str(current_stdout),
            "stderr": str(current_stderr),
        }
        persist(payload, runtime_path)
        print(
            f"task run: executing {current_executor} in {resolved_target}",
            file=sys.stderr,
        )
        execution = _execute_watched_lane(
            payload,
            current_command,
            lane_prompt=current_prompt,
            resolved_target=resolved_target,
            configured_env=current_env,
            stdout_log=current_stdout,
            stderr_log=current_stderr,
            timeout_seconds=timeout_seconds,
            require_change=require_change,
            base_sha=base_sha,
            scope_specs=scope_specs,
            executor=current_executor,
            runtime_path=runtime_path,
            no_progress_seconds=no_progress_seconds,
        )
        attempt_history.extend(payload.get("attempts", []))
        payload["attempts"] = attempt_history
        failure = _state.classify_failure(
            execution,
            stderr_text=_progress._lane_stderr_text(current_stdout, current_stderr),
        )
        if failure["kind"] != "executor-unavailable":
            break
    return execution
