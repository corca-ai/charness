"""Same-worktree attempt loop for transient executor stalls (#829).

A retryable stall (typed by `classify_failure`, e.g. a model-stream idle
timeout) reruns the same prompt in the same worktree until the attempt
budget is spent; every attempt is recorded on `payload["attempts"]`.
Executor sessions are stateless, so each attempt starts a fresh agent
session; the lane worktree (files and lane-branch commits) is the resume
carrier that persists across attempts.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_runtime as _runtime  # noqa: E402
from scripts.task_run import task_run_state as _state  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

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
) -> dict[str, Any]:
    """Run the lane executor under its live progress guard, retrying stalls."""
    max_attempts = _env_attempts(MAX_ATTEMPTS_ENV, DEFAULT_MAX_ATTEMPTS)
    backoff = _progress._env_seconds(RETRY_BACKOFF_ENV, DEFAULT_RETRY_BACKOFF_SECONDS)
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
            "started_at": _support.utc_now_iso(),
            "failure_kind": failure["kind"],
            "retried": False,
        }
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
