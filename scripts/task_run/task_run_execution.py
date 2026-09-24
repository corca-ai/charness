"""Codex process control and result-delivery parsing."""

from __future__ import annotations

import importlib.util
import json
import math
import os
import shutil
import signal
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.core.subprocess_guard import render_display, run_monitored_phase
except ImportError:  # flat layout: the repo root is not on sys.path
    _repo_root = next(
        ancestor
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    from scripts.core.subprocess_guard import render_display, run_monitored_phase

_DESCENDANT_CLEANUP_SHELL = (
    'printf "%s\\n" "$$" > "$1"; shift; exec 3<&0; "$@" <&3 & '
    'child=$!; wait "$child"; status=$?; exit "$status"'
)

def _env_seconds(name: str, default: float) -> float:
    """Read one finite duration from the environment, or use its default."""
    try:
        value = float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default
    return value if math.isfinite(value) else default


def _tail_text(path: Path, limit: int = 64 * 1024) -> str:
    try:
        if not path.is_file():
            return ""
        return path.read_bytes()[-limit:].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _executor_unavailable_reason(
    result: dict[str, Any], stdout_log: Path, stderr_log: Path, executor: str
) -> None:
    from scripts.task_run import task_run_state

    logs = (stdout_log, stderr_log, stdout_log.with_name(f"{executor}.events.log"))
    transcript = "\n".join(_tail_text(path) for path in logs)
    reason = task_run_state.executor_unavailable_reason(result, transcript)
    if reason:
        result["executor_unavailable"] = reason


def _lane_stderr_text(stdout_log: Path, stderr_log: Path | None) -> str:
    """Read the conventional executor stderr transcript for phase parsing."""
    candidate = stderr_log
    if candidate is None and stdout_log.name.endswith(".stdout.log"):
        candidate = stdout_log.with_name(
            stdout_log.name[: -len(".stdout.log")] + ".stderr.log"
        )
    if candidate is None:
        return ""
    try:
        if candidate.is_file():
            return candidate.read_bytes()[-256 * 1024 :].decode("utf-8", errors="replace")
    except OSError:
        pass
    return ""


def _guard_phases(payload: Mapping[str, Any]) -> list[str]:
    guard = payload.get("progress_guard")
    phases = guard.get("last_phases") if isinstance(guard, Mapping) else None
    return [phase for phase in phases if isinstance(phase, str)] if isinstance(phases, list) else []


def _guard_stop_reason(payload: Mapping[str, Any]) -> str:
    guard = payload.get("progress_guard")
    reason = guard.get("stop_reason") if isinstance(guard, Mapping) else None
    return reason if isinstance(reason, str) else ""


def _command_with_normal_completion_cleanup(
    command: Sequence[str], configured_env: Mapping[str, str], group_path: Path
) -> Sequence[str]:
    if not command:
        return command
    executable = os.fspath(command[0])
    path = configured_env.get("PATH", os.defpath)
    available = os.access(executable, os.X_OK) if "/" in executable else shutil.which(executable, path=path)
    return [
        "sh",
        "-c",
        _DESCENDANT_CLEANUP_SHELL,
        "charness-task-run",
        str(group_path),
        *command,
    ] if available else command


def _kill_recorded_process_group(group_path: Path) -> None:
    try:
        group_id = int(group_path.read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return
    try:
        os.killpg(group_id, signal.SIGKILL)
    except ProcessLookupError:
        pass
    finally:
        group_path.unlink(missing_ok=True)


@contextmanager
def _redirect_stdio(stdin_handle, stdout_handle, stderr_handle):  # noqa: ANN001
    saved = [os.dup(fd) for fd in (0, 1, 2)]
    try:
        for fd, handle in zip((0, 1, 2), (stdin_handle, stdout_handle, stderr_handle)):
            os.dup2(handle.fileno(), fd)
        yield
    finally:
        for fd, saved_fd in zip((0, 1, 2), saved):
            os.dup2(saved_fd, fd)
            os.close(saved_fd)


def _execute_codex(
    command: Sequence[str],
    *,
    prompt: str,
    target_path: Path,
    configured_env: Mapping[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
    lane_watch: Any | None = None,
    executor: str = "codex",
) -> dict[str, Any]:
    result: dict[str, Any] = {"exit_code": None, "timed_out": False, "interrupted": False}
    group_path = stdout_log.with_suffix(".pgid")
    group_path.unlink(missing_ok=True)
    from scripts.task_run import task_run_lane_runner as _lane_runner

    current_command = list(command)
    current_prompt = prompt
    session_id = _command_session_id(current_command, executor)
    resume_path = "initial"
    delivered_batch: list[Mapping[str, Any]] = []
    event_log = stdout_log.with_name(f"{executor}.events.log")
    queue_path = stdout_log.parent / "steer.queue.jsonl"
    try:
        invocation = 0
        while True:
            last_message_path = _last_message_path(current_command, executor)
            if last_message_path is not None:
                last_message_path.unlink(missing_ok=True)
            result.update(
                _run_executor_invocation(
                    current_command,
                    current_prompt,
                    target_path=target_path,
                    configured_env=configured_env,
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                    timeout_seconds=timeout_seconds,
                    lane_watch=lane_watch,
                    executor=executor,
                    group_path=group_path,
                    append_stderr=bool(invocation),
                )
            )
            if executor == "codex":
                raw_output = _tail_text(stdout_log, limit=64 * 1024 * 1024)
                session_id = _codex_session_id(raw_output) or session_id
                if raw_output:
                    with event_log.open("a", encoding="utf-8") as handle:
                        handle.write(raw_output)
                        if not raw_output.endswith("\n"):
                            handle.write("\n")
                if last_message_path is not None and last_message_path.is_file():
                    stdout_log.write_text(last_message_path.read_text(encoding="utf-8"), encoding="utf-8")
            if (
                result["timed_out"]
                or result["interrupted"]
            ):
                break
            if lane_watch is not None and lane_watch.stop_reason is not None:
                result["progress_stopped"] = lane_watch.stop_reason
                break
            if (
                resume_path == "session-resume"
                and (result.get("exec_error") or result["exit_code"] not in (None, 0))
            ):
                if lane_watch is not None:
                    lane_watch.record_steer_delivery(delivered_batch, resume_path="relaunch-in-place")
                else:
                    _record_steer_delivery(queue_path, delivered_batch, "relaunch-in-place")
                result.pop("exec_error", None)
                current_command = list(command)
                resume_path = "relaunch-in-place"
                _append_steer_transcript(
                    stderr_log, delivered_batch, "relaunch-in-place"
                )
                invocation += 1
                continue
            pending = (
                lane_watch.pending_steers()
                if lane_watch is not None
                else [
                    item for item in _lane_runner.read_steer_queue(queue_path)
                    if not item.get("delivered_at")
                ]
            )
            if not pending:
                break
            delivered_batch = pending
            current_command, current_prompt, resume_path = _lane_runner.steered_lane_invocation(
                executor, current_command, current_prompt, pending, session_id
            )
            _append_steer_transcript(stderr_log, pending, resume_path)
            invocation += 1
            if lane_watch is not None:
                lane_watch.record_steer_delivery(pending, resume_path=resume_path)
            else:
                _record_steer_delivery(queue_path, pending, resume_path)
    except OSError as exc:
        result["exec_error"] = str(exc)
    _executor_unavailable_reason(result, stdout_log, stderr_log, executor)
    steer_messages = _lane_runner.read_steer_queue(queue_path)
    if steer_messages:
        result["steer_messages"] = steer_messages
    return result


def _run_executor_invocation(
    command: Sequence[str],
    prompt: str,
    *,
    target_path: Path,
    configured_env: Mapping[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
    lane_watch: Any | None,
    executor: str,
    group_path: Path,
    append_stderr: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {"exit_code": None, "timed_out": False, "interrupted": False}
    try:
        with (
            stdout_log.open("w", encoding="utf-8") as stdout_handle,
            stderr_log.open("a" if append_stderr else "w", encoding="utf-8") as stderr_handle,
            tempfile.TemporaryFile(mode="w+", encoding="utf-8") as prompt_handle,
        ):
            prompt_handle.write(prompt)
            prompt_handle.flush()
            prompt_handle.seek(0)
            terminal_stderr = os.fdopen(os.dup(2), "w", buffering=1, closefd=True)
            outcome = None
            try:
                if lane_watch is not None:
                    lane_watch.start(
                        emit=lambda phases, elapsed: print(
                            f"PROGRESS [{executor}] elapsed={elapsed:.1f}s "
                            f"phases={','.join(phases) if phases else 'none'}",
                            file=terminal_stderr,
                            flush=True,
                        ),
                        kill=lambda: _kill_recorded_process_group(group_path),
                    )
                with _redirect_stdio(prompt_handle, stdout_handle, stderr_handle):
                    outcome = run_monitored_phase(
                        _command_with_normal_completion_cleanup(
                            command, configured_env, group_path
                        ),
                        cwd=target_path,
                        phase=executor,
                        timeout_seconds=timeout_seconds,
                        display=render_display(command),
                        env=dict(configured_env),
                        capture=False,
                        stream=terminal_stderr,
                    )
            except KeyboardInterrupt:
                result["interrupted"] = True
            except OSError as exc:
                result["exec_error"] = str(exc)
            finally:
                if lane_watch is not None:
                    lane_watch.stop()
                terminal_stderr.close()
                _kill_recorded_process_group(group_path)
            if outcome is not None:
                result["timed_out"] = outcome.timed_out
                result["exit_code"] = None if outcome.timed_out else outcome.returncode
    except OSError as exc:
        result["exec_error"] = str(exc)
    return result


def _record_steer_delivery(
    queue_path: Path, messages: Sequence[Mapping[str, Any]], resume_path: str
) -> None:
    from scripts.task_run import task_run_lane_runner as _lane_runner
    from scripts.task_run.task_run_runtime import utc_now_iso

    stamp = utc_now_iso()
    for message in messages:
        _lane_runner.update_steer_queue(
            queue_path,
            {**message, "delivered_at": stamp, "disposition": "accepted", "resume_path": resume_path},
        )


def _command_session_id(command: Sequence[str], executor: str) -> str | None:
    if executor != "muse" or "--session-id" not in command:
        return None
    try:
        return str(command[command.index("--session-id") + 1])
    except (IndexError, ValueError):
        return None


def _last_message_path(command: Sequence[str], executor: str) -> Path | None:
    if executor != "codex" or "--output-last-message" not in command:
        return None
    try:
        return Path(command[command.index("--output-last-message") + 1])
    except (IndexError, ValueError):
        return None


def _codex_session_id(output: str) -> str | None:
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "thread.started":
            value = event.get("thread_id")
            if isinstance(value, str) and value:
                return value
    return None


def _append_steer_transcript(
    stderr_log: Path, messages: Sequence[Mapping[str, Any]], resume_path: str
) -> None:
    with stderr_log.open("a", encoding="utf-8") as handle:
        for message in messages:
            handle.write(
                f"STEER [{message['message_id']}] queued_at={message['queued_at']} "
                f"resume_path={resume_path}\n{message['message']}\n"
            )


_MAX_RESULT_TEXT_BYTES = 1024 * 1024
_REVIEW_SCAN_LIMIT_BYTES = 64 * 1024 * 1024
_BOUNDED_REVIEW_KIND = "charness.bounded_review.v1"

_REVIEWER_CONTRACT: Any | None = None


def run_self_review(payload: dict[str, Any]) -> dict[str, Any]:
    """Run a read-only Codex self-review and retain its non-approval findings."""
    from scripts.task_run import task_run_state, task_run_support, task_run_runtime
    from scripts.worktree import worktree_exec_lib

    prompt = str(payload.pop("_self_review_prompt", ""))
    candidate = payload.get("candidate")
    candidate = candidate if isinstance(candidate, Mapping) else {}
    changed_paths = candidate.get("changed_paths") or []
    persistence = payload.get("persistence")
    persistence = persistence if isinstance(persistence, Mapping) else {}
    policy = str(payload.get("self_review_policy", "never"))
    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list):
        scopes = []
    if not task_run_state.self_review_requested(policy, prompt, scopes, changed_paths, persistence):
        reason = "self-review is disabled for this invocation" if policy == "never" else "no irreversible-boundary signal; use --self-review to opt in"
        return task_run_state.self_review_block("not-requested", reason=reason)
    executor_info = payload.get("executor")
    executor_info = executor_info if isinstance(executor_info, Mapping) else {}
    if executor_info.get("kind") != "codex":
        return task_run_state.self_review_block(
            "unavailable-skip",
            reason="a read-only Codex reviewer is unavailable for the selected lane executor",
        )
    original_command = executor_info.get("command")
    if not isinstance(original_command, list) or not original_command:
        return task_run_state.self_review_block(
            "unavailable-skip", reason="the reviewer command is unavailable"
        )
    executable = str(original_command[0])
    if not os.access(executable, os.X_OK):
        return task_run_state.self_review_block(
            "unavailable-skip", reason=f"reviewer executable is unavailable: {executable}"
        )
    try:
        runtime_path = Path(str(payload["execution_runtime_root"]))
        worktree = Path(str(payload["worktree_path"]))
        review_root = runtime_path / "self-review"
        review_root.mkdir(parents=True, exist_ok=True)
        stdout_log, stderr_log = review_root / "codex.stdout.log", review_root / "codex.stderr.log"
        output_path = review_root / "codex.last-message.txt"
        command = task_run_runtime.build_codex_command(executable, effort="medium")
        command[command.index("--sandbox") + 1] = "read-only"
        command[-1:-1] = ["--json", "--output-last-message", str(output_path)]
        env = worktree_exec_lib.prepare_exec_environment(worktree, os.environ.copy(), runtime_root=runtime_path)
        env = task_run_support.scrubbed_lane_env(payload, env, "codex")
        result = _execute_codex(
            command, prompt=task_run_state.self_review_prompt(prompt, str(payload.get("base_sha", "")), changed_paths),
            target_path=worktree, configured_env=env, stdout_log=stdout_log, stderr_log=stderr_log,
            timeout_seconds=min(int(executor_info.get("timeout_seconds") or 300), 300), executor="codex",
        )
        return task_run_state.self_review_result(result, _tail_text(stdout_log, limit=1024 * 1024))
    except (OSError, RuntimeError, ValueError) as exc:
        return task_run_state.self_review_block(
            "unavailable-skip", reason=f"reviewer could not run: {exc}"
        )


def _bounded_result_shape(payload: dict[str, Any]) -> str:
    """Load the shared result contract in source and flat plugin checkouts."""
    global _REVIEWER_CONTRACT
    if _REVIEWER_CONTRACT is None:
        here = Path(__file__).resolve()
        candidates = [
            ancestor / "skills" / "shared" / "scripts" / "reviewer_result_contract.py"
            for ancestor in (here.parent, *here.parents)
        ]
        candidates.extend(
            ancestor / "shared" / "scripts" / "reviewer_result_contract.py"
            for ancestor in (here.parent, *here.parents)
        )
        contract_path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if contract_path is None:
            raise ImportError("shared reviewer_result_contract.py is unavailable")
        spec = importlib.util.spec_from_file_location(
            "charness_reviewer_result_contract", contract_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load reviewer result contract: {contract_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _REVIEWER_CONTRACT = module
    return _REVIEWER_CONTRACT.bounded_result_shape(payload)


def _extract_bounded_review(raw: bytes) -> tuple[dict[str, Any], str] | None:
    from scripts.task_run import task_run_state

    candidate = task_run_state.extract_structured_review(
        raw, kind=_BOUNDED_REVIEW_KIND, limit=_REVIEW_SCAN_LIMIT_BYTES
    )
    return (candidate, "text-json") if candidate is not None else None


def _reviewer_result_carrier(delivery: Mapping[str, Any]) -> dict[str, Any] | None:
    from scripts.task_run import task_run_state

    return task_run_state.reviewer_result_carrier(
        delivery, result_shape=_bounded_result_shape, extract=_extract_bounded_review
    )


def _result_delivery(stdout_log: Path) -> dict[str, Any]:
    try:
        raw = stdout_log.read_bytes() if stdout_log.is_file() else b""
    except OSError as exc:
        return {
            "status": "non-delivery",
            "bytes": None,
            "truncated": False,
            "text": "",
            "log": str(stdout_log),
            "structured_status": "unavailable",
            "delivery_error": str(exc),
            "delivery_error_type": type(exc).__name__,
        }
    delivered = bool(raw.strip())
    clipped = raw[:_MAX_RESULT_TEXT_BYTES]
    text = clipped.decode("utf-8", errors="replace")
    result: dict[str, Any] = {
        "status": "delivered" if delivered else "non-delivery",
        "bytes": len(raw),
        "truncated": len(raw) > len(clipped),
        "text": text,
        "log": str(stdout_log),
    }
    result["structured_status"] = "not-applicable"
    extracted = _extract_bounded_review(raw)
    if extracted is not None:
        result["reviewer_result"], result["reviewer_result_source"] = extracted
    if delivered and not result["truncated"]:
        try:
            structured = yaml.safe_load(text)
        except yaml.YAMLError:
            if "schema_version" in text:
                result["structured_status"] = "invalid"
        else:
            if isinstance(structured, Mapping) and "schema_version" in structured:
                try:
                    json.dumps(structured)
                except (TypeError, ValueError):
                    result["structured_status"] = "invalid"
                else:
                    result["structured_status"] = "valid"
                    result["structured"] = dict(structured)
    return result
