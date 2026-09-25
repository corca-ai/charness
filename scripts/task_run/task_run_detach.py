"""Detached lane launch and lane waiting for `charness task`.

A blocking foreground `task run` keeps the orchestrating agent's turn busy,
so agents detach it and poll. A detached lane notifies nobody when it ends.
`launch_detached` returns once the carrier has started (or fast-fails with
the task-run exit code), and `wait_for_tasks` blocks until named lanes reach
a terminal status so a host background job's own completion notification
carries the lane verdict.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

TERMINAL_PHASE = "terminal"
# A persisted record in one of these phases claims nothing about carrier
# start: the lane may still be creating its worktree or sitting in prelaunch.
_UNSTARTED_PHASES = frozenset({"planned", "running", "preflight"})

LAUNCH_POLL_SECONDS = 2.0
LAUNCH_TIMEOUT_SECONDS = 600.0
# A dead launcher may have just written its terminal record; a live one may
# be between worktree creation and its first persist. Both settle quickly.
LAUNCH_SETTLE_SECONDS = 10.0
WAIT_POLL_SECONDS = 5.0


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core import subprocess_guard as _guard  # noqa: E402
from scripts.task_run import task_run_runtime as _runtime  # noqa: E402
from scripts.task_run import task_run_state as _state  # noqa: E402
from scripts.task_run.task_run_contract import _TASK_ID_RE, TaskRunError  # noqa: E402


def preview_task_id(
    lane: str | None, branch: str | None, task_id: str | None
) -> str:
    """Derive the task id the foreground run would use, without side effects."""
    if lane is not None:
        return _runtime.validate_lane_id(lane)
    if branch is None:
        raise ValueError("explicit task runs need --branch for --detach")
    return _runtime._task_id(branch, task_id)


def result_paths(repo_root: Path, task_id: str) -> tuple[Path, Path]:
    """Return the (runtime path, result path) the lane record will use."""
    if not _TASK_ID_RE.fullmatch(task_id):
        raise ValueError(f"invalid task id: {task_id!r}")
    runtime_path = _runtime.task_runtime_root(repo_root)
    return runtime_path, _runtime.task_result_path(runtime_path, task_id)


def is_terminal(payload: Mapping[str, Any] | None) -> bool:
    return isinstance(payload, Mapping) and payload.get("phase") == TERMINAL_PHASE


def carrier_started(payload: Mapping[str, Any] | None) -> bool:
    """A persisted record proves the carrier started only past prelaunch.

    Worktree creation and prelaunch gates persist `running` records before
    the executor spawns; those must not read as launched. The executor's
    first log file (created at spawn, before any transcript line) or a
    phase past create/prelaunch is the start signal.
    """
    if not isinstance(payload, Mapping):
        return False
    if is_terminal(payload):
        return True
    logs = payload.get("logs")
    if isinstance(logs, Mapping):
        for key in ("stdout", "stderr"):
            value = logs.get(key)
            if isinstance(value, str) and value and Path(value).exists():
                return True
    return payload.get("phase") not in _UNSTARTED_PHASES


def receipt_exit_code(payload: Mapping[str, Any]) -> int:
    return _state.exit_code_for_result_kind(_state.result_kind_for_receipt(payload))


def entry_command() -> list[str]:
    """The `charness` entry this process runs as, for detached re-invocation."""
    argv0 = sys.argv[0]
    candidate = Path(argv0)
    if candidate.name == argv0 and shutil.which(argv0) is not None:
        return [str(Path(shutil.which(argv0)))]
    return [str(candidate.resolve())]


def _flag(values: Sequence[Any] | None) -> list[str]:
    return [str(value) for value in values or ()]


def _target_argv(args: argparse.Namespace) -> list[str]:
    """Lane shorthand vs explicit path/branch/base selection."""
    if args.lane is not None:
        return ["--lane", args.lane]
    argv = ["--path", str(args.path), "--branch", args.branch]
    if args.base is not None:
        argv += ["--base", args.base]
    if args.task_id is not None:
        argv += ["--task-id", args.task_id]
    return argv


def _prompt_argv(args: argparse.Namespace) -> list[str]:
    """Scope, prompt source, and executor selection."""
    argv: list[str] = []
    for scope in _flag(args.scope):
        argv += ["--scope", scope]
    if args.prompt is not None:
        argv += ["--prompt", args.prompt]
    else:
        argv += ["--prompt-file", str(args.prompt_file)]
    return argv + ["--executor", args.executor, "--effort", args.effort]


def _mode_argv(args: argparse.Namespace) -> list[str]:
    """Execution-mode flags the child must reproduce exactly."""
    argv: list[str] = []
    for flag in (
        ("prepare", "--prepare"),
        ("skip_prepare", "--skip-prepare"),
        ("allow_no_change", "--allow-no-change"),
        ("report_only", "--report-only"),
        ("critical_lane", "--critical-lane"),
    ):
        if getattr(args, flag[0], False):
            argv.append(flag[1])
    if getattr(args, "self_review_policy", "auto") == "always":
        argv.append("--self-review")
    if args.acceptance_skeleton is not None:
        argv += ["--acceptance-skeleton", args.acceptance_skeleton]
    for check in args.premise_check or []:
        argv += ["--premise-check", *check]
    if args.timeout_seconds != 3600:
        argv += ["--timeout-seconds", str(args.timeout_seconds)]
    if args.no_progress_seconds is not None:
        argv += ["--no-progress-seconds", str(args.no_progress_seconds)]
    return argv


def _option_argv(args: argparse.Namespace) -> list[str]:
    """Lane options and harness routing flags."""
    argv: list[str] = []
    for rules_file in _flag(args.rules_file):
        argv += ["--rules-file", rules_file]
    for granted in _flag(args.grant_writable):
        argv += ["--grant-writable", granted]
    if getattr(args, "charness_checkout", None) is not None:
        argv += ["--charness-checkout", str(args.charness_checkout)]
    home_root = getattr(args, "home_root", None)
    if home_root is not None:
        argv += ["--home-root", str(home_root)]
    return argv


def child_argv(entry: Sequence[str], args: argparse.Namespace) -> list[str]:
    """Rebuild the foreground `task run` argv the detached child executes.

    `--detach` itself is dropped (the child runs foreground); `--dry-run`
    with `--detach` is refused by the caller, never silently downgraded.
    """
    return (
        [*entry, "task", "run", "--repo-root", str(args.repo_root)]
        + _target_argv(args)
        + _prompt_argv(args)
        + _mode_argv(args)
        + _option_argv(args)
    )


def read_record(runtime_path: Path, task_id: str) -> dict[str, Any] | None:
    try:
        return _runtime.read_task_result(runtime_path, task_id)
    except (OSError, ValueError):
        return None


def wait_for_launch(
    runtime_path: Path,
    task_id: str,
    child: Any,
    *,
    poll_seconds: float = LAUNCH_POLL_SECONDS,
    timeout_seconds: float = LAUNCH_TIMEOUT_SECONDS,
    settle_seconds: float = LAUNCH_SETTLE_SECONDS,
    now: Any = time.monotonic,
    sleep: Any = time.sleep,
) -> dict[str, Any]:
    """Block until the detached lane starts, fails fast, or the wait times out.

    Returns a launch outcome; `exit_code` is 0 only after the carrier-start
    signal, otherwise the finished lane's task-run exit code (or 1 when the
    launcher died or the wait timed out before any signal).
    """
    deadline = now() + timeout_seconds
    while True:
        payload = read_record(runtime_path, task_id)
        if is_terminal(payload):
            assert payload is not None
            return {
                "launched": False,
                "task_id": task_id,
                "status": payload.get("status"),
                "result_path": str(_runtime.task_result_path(runtime_path, task_id)),
                "exit_code": receipt_exit_code(payload),
            }
        if carrier_started(payload):
            return {
                "launched": True,
                "task_id": task_id,
                "status": payload.get("status") if payload else None,
                "result_path": str(_runtime.task_result_path(runtime_path, task_id)),
                "exit_code": 0,
            }
        if child.poll() is not None:
            sleep(settle_seconds)
            payload = read_record(runtime_path, task_id)
            if is_terminal(payload):
                assert payload is not None
                return {
                    "launched": False,
                    "task_id": task_id,
                    "status": payload.get("status"),
                    "result_path": str(
                        _runtime.task_result_path(runtime_path, task_id)
                    ),
                    "exit_code": receipt_exit_code(payload),
                }
            if carrier_started(payload):
                return {
                    "launched": True,
                    "task_id": task_id,
                    "status": payload.get("status") if payload else None,
                    "result_path": str(
                        _runtime.task_result_path(runtime_path, task_id)
                    ),
                    "exit_code": 0,
                }
            code = child.returncode
            return {
                "launched": False,
                "task_id": task_id,
                "status": None,
                "result_path": str(_runtime.task_result_path(runtime_path, task_id)),
                "exit_code": int(code) if isinstance(code, int) and code != 0 else 1,
            }
        if now() >= deadline:
            return {
                "launched": False,
                "task_id": task_id,
                "status": payload.get("status") if payload else None,
                "result_path": str(_runtime.task_result_path(runtime_path, task_id)),
                "exit_code": 1,
                "error": (
                    "timed out waiting for the carrier start signal; the lane "
                    "may still be launching — use `task wait` on the task id"
                ),
            }
        sleep(poll_seconds)


def wait_for_tasks(
    runtime_path: Path,
    task_ids: Sequence[str],
    *,
    wait_any: bool = False,
    timeout_seconds: float = 0,
    poll_seconds: float = WAIT_POLL_SECONDS,
    now: Any = time.monotonic,
    sleep: Any = time.sleep,
) -> dict[str, Any]:
    """Block until all (or with `wait_any`, the first) named lanes end.

    An already-terminal lane returns on the first poll. `exit_code` is 0
    when every finished lane succeeded, else the first non-successful
    finished lane's task-run exit code in CLI order.
    """
    deadline = None if not timeout_seconds or timeout_seconds <= 0 else now() + timeout_seconds
    finished: list[dict[str, Any]] = []
    pending: list[str] = list(task_ids)
    while pending:
        still_pending: list[str] = []
        for task_id in pending:
            payload = read_record(runtime_path, task_id)
            if is_terminal(payload):
                assert payload is not None
                finished.append(
                    {
                        "task_id": task_id,
                        "status": payload.get("status"),
                        "exit_code": receipt_exit_code(payload),
                    }
                )
            else:
                still_pending.append(task_id)
        pending = still_pending
        if not pending or (wait_any and finished):
            break
        if deadline is not None and now() >= deadline:
            return {
                "finished": finished,
                "pending": pending,
                "exit_code": 1,
                "error": f"timed out waiting for terminal status: {', '.join(pending)}",
            }
        sleep(poll_seconds)
    exit_code = 0
    for entry in finished:
        if entry["exit_code"] != 0:
            exit_code = entry["exit_code"]
            break
    return {"finished": finished, "pending": pending, "exit_code": exit_code}


def launch_log_path(runtime_path: Path, task_id: str) -> Path:
    return runtime_path / "task-run" / task_id / "launch.log"


def describe_launch(outcome: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_id": outcome.get("task_id"),
        "result_path": outcome.get("result_path"),
        "launched": outcome.get("launched"),
        "status": outcome.get("status"),
        **({"error": outcome["error"]} if outcome.get("error") else {}),
    }


def launch_detached_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Launch a lane detached; (report payload, exit code) for the CLI wrapper.

    Raises TaskRunError for flag combinations no child should ever see.
    """
    if args.dry_run:
        raise TaskRunError(
            "--detach cannot be combined with --dry-run: "
            "a dry run launches nothing to detach from"
        )
    if args.lane is not None and args.task_id is not None:
        raise TaskRunError("--task-id is derived from --lane; omit it in shorthand mode")
    try:
        task_id = preview_task_id(args.lane, args.branch, args.task_id)
    except ValueError as exc:
        raise TaskRunError(str(exc)) from exc
    repo_root = args.repo_root.resolve()
    runtime_path, _result_path = result_paths(repo_root, task_id)
    child = _guard.spawn_detached(
        child_argv(entry_command(), args), log_path=launch_log_path(runtime_path, task_id)
    )
    outcome = wait_for_launch(runtime_path, task_id, child)
    return describe_launch(outcome), outcome["exit_code"]


def wait_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Wait for named lanes; (report payload, exit code) for the CLI wrapper."""
    runtime_path = _runtime.task_runtime_root(args.repo_root.resolve())
    outcome = wait_for_tasks(
        runtime_path,
        args.task_ids,
        wait_any=args.any,
        timeout_seconds=args.timeout_seconds,
    )
    return (
        {
            "finished": outcome["finished"],
            "pending": outcome["pending"],
            **({"error": outcome["error"]} if outcome.get("error") else {}),
        },
        outcome["exit_code"],
    )


# NOTE: the `task run --detach` / `task wait` parser blocks stay inline in
# the root `charness` entry on purpose. A copied entry script must build its
# parser with zero sibling imports (see
# test_direct_entry_copy_nacks_unknown_task_from_real_checkout), so parser
# construction cannot live in a feature module; only the command payloads
# (below) do, loaded lazily at command time.
