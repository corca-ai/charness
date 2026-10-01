"""Read-only Codex self-review runner for task-run lanes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()


def run_self_review(payload: dict[str, Any]) -> dict[str, Any]:
    """Run a read-only Codex self-review and retain its non-approval findings."""
    from scripts.task_run import task_run_execution as _execution
    from scripts.task_run import task_run_runtime, task_run_state, task_run_support
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
        result = _execution._execute_codex(
            command, prompt=task_run_state.self_review_prompt(prompt, str(payload.get("base_sha", "")), changed_paths),
            target_path=worktree, configured_env=env, stdout_log=stdout_log, stderr_log=stderr_log,
            timeout_seconds=min(int(executor_info.get("timeout_seconds") or 300), 300), executor="codex",
        )
        return task_run_state.self_review_result(result, _execution._tail_text(stdout_log, limit=1024 * 1024))
    except (OSError, RuntimeError, ValueError) as exc:
        return task_run_state.self_review_block(
            "unavailable-skip", reason=f"reviewer could not run: {exc}"
        )
