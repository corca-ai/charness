"""Brief critique: the read-only Codex precheck behind prelaunch gates."""

from __future__ import annotations

import json
import os
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
    BRIEF_CRITIQUE_TIMEOUT_SECONDS,
)


def _brief_critique_prompt(
    brief: str,
    checks: Sequence[Mapping[str, Any]],
    *,
    lane_executor: str | None = None,
    lane_executable: str | None = None,
) -> str:
    role = "You are a read-only preflight reviewer for a task lane, not the lane executor. "
    if lane_executor:
        carrier = f"The lane itself will execute on the {lane_executor!r} carrier"
        if lane_executable:
            carrier += f", whose executable the task runtime already validated at {lane_executable!r}"
        else:
            carrier += ", whose availability the task runtime already validated"
        carrier += (
            "; your own Codex-only tool context says nothing about that carrier's "
            "availability, so never report the lane executor as unavailable because "
            "you lack its tools. "
        )
        role += carrier
    return (
        role
        + "Review this task brief read-only against repository code and available provider docs. "
        "Use this fresh context; treat style as advisory. Set premise_failure true only when a central factual premise makes the task "
        "invalid; one blocked item never sets it. Check each premise independently. Return one JSON object with "
        "premise_failure (boolean), premise_failure_reason, findings, and premise_checks "
        "(array of objects with id, kind: success or premise-blocked, and evidence). "
        "Do not edit files.\n\nTASK BRIEF:\n"
        + brief
        + "\n\nPREMISES:\n"
        + json.dumps(list(checks), ensure_ascii=False)
    )


def _lane_carrier_facts(
    payload: Mapping[str, Any], resolved: Mapping[str, Any]
) -> tuple[str | None, str | None]:
    """The selected lane carrier and its validated executable, when known."""
    lane_executor = resolved.get("executor")
    lane_executor = lane_executor if isinstance(lane_executor, str) else None
    paths = resolved.get("executor_paths")
    lane_executable = (
        paths.get(lane_executor)
        if isinstance(paths, Mapping) and lane_executor is not None
        else None
    )
    if not isinstance(lane_executable, str):
        block = payload.get("executor")
        lane_executable = (
            block.get("executable") if isinstance(block, Mapping) else None
        )
    return lane_executor, lane_executable if isinstance(lane_executable, str) else None


def _run_brief_critique(
    *, payload: dict[str, Any], resolved: Mapping[str, Any], prompt: str,
    premise_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    from scripts.runtime_bootstrap import import_repo_module
    from scripts.task_run import task_run_execution as execution
    from scripts.task_run import task_run_support as support
    from scripts.task_run.task_run_runtime import (
        _resolve_codex,
        build_codex_command,
    )

    exec_lib = import_repo_module(__file__, "scripts.worktree.worktree_exec_lib")

    executable = _resolve_codex("codex")
    command = build_codex_command(executable, effort="medium")
    command[command.index("--sandbox") + 1] = "read-only"
    task_root = Path(resolved["runtime_path"]) / "task-run" / str(payload["task_id"])
    stdout_log, stderr_log = task_root / "brief-critique.stdout.log", task_root / "brief-critique.stderr.log"
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    target = Path(resolved["target_path"])
    execution_root = Path(payload["execution_runtime_root"])
    configured_env = support.scrubbed_lane_env(
        payload,
        exec_lib.prepare_exec_environment(
            target, os.environ.copy(), runtime_root=execution_root
        ),
        "codex",
    )
    lane_executor, lane_executable = _lane_carrier_facts(payload, resolved)
    outcome = execution._execute_codex(
        command,
        prompt=_brief_critique_prompt(
            prompt,
            premise_checks,
            lane_executor=lane_executor,
            lane_executable=lane_executable,
        ),
        target_path=target,
        configured_env=configured_env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=BRIEF_CRITIQUE_TIMEOUT_SECONDS,
    )
    try:
        parsed = json.loads(stdout_log.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        parsed = None
    if outcome.get("exit_code") != 0 or not isinstance(parsed, Mapping):
        return {
            "status": "timed-out" if outcome.get("timed_out") else "unavailable",
            "error": str(outcome.get("exec_error") or "review returned no JSON result")[:300],
        }
    return {
        "status": "completed",
        "premise_failure": parsed.get("premise_failure") is True,
        "premise_failure_reason": str(parsed.get("premise_failure_reason") or "")[:500],
        "findings": parsed.get("findings"),
        "premise_checks": parsed.get("premise_checks"),
    }
