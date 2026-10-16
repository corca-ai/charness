"""Read-only Codex self-review runner for task-run lanes."""

from __future__ import annotations

import json
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
    from scripts.task_run import task_run_runtime, task_run_support
    from scripts.worktree import worktree_exec_lib

    prompt = str(payload.pop("_self_review_prompt", ""))
    candidate = payload.get("candidate")
    candidate = candidate if isinstance(candidate, Mapping) else {}
    changed_paths = candidate.get("changed_paths") or []
    policy = str(payload.get("self_review_policy", "never"))
    if policy != "always":
        return self_review_block(
            "not-requested", reason="self-review is disabled for this invocation"
        )
    executor_info = payload.get("executor")
    executor_info = executor_info if isinstance(executor_info, Mapping) else {}
    if executor_info.get("kind") != "codex":
        return self_review_block(
            "unavailable-skip",
            reason="a read-only Codex reviewer is unavailable for the selected lane executor",
        )
    original_command = executor_info.get("command")
    if not isinstance(original_command, list) or not original_command:
        return self_review_block(
            "unavailable-skip", reason="the reviewer command is unavailable"
        )
    executable = str(original_command[0])
    if not os.access(executable, os.X_OK):
        return self_review_block(
            "unavailable-skip", reason=f"reviewer executable is unavailable: {executable}"
        )
    try:
        runtime_path = Path(str(payload["execution_runtime_root"]))
        worktree = Path(str(payload["worktree_path"]))
        review_root = runtime_path / "self-review"
        review_root.mkdir(parents=True, exist_ok=True)
        stdout_log, stderr_log = review_root / "codex.stdout.log", review_root / "codex.stderr.log"
        output_path = review_root / "codex.last-message.txt"
        schema_path = review_root / "self-review.schema.json"
        schema_path.write_text(json.dumps(self_review_schema()), encoding="utf-8")
        command = task_run_runtime.build_codex_command(executable, effort="medium")
        command[command.index("--sandbox") + 1] = "read-only"
        command[-1:-1] = [
            "--json", "--output-schema", str(schema_path),
            "--output-last-message", str(output_path),
        ]
        env = worktree_exec_lib.prepare_exec_environment(worktree, os.environ.copy(), runtime_root=runtime_path)
        env = task_run_support.scrubbed_lane_env(payload, env, "codex")
        result = _execution._execute_codex(
            command, prompt=self_review_prompt(prompt, str(payload.get("base_sha", "")), changed_paths),
            target_path=worktree, configured_env=env, stdout_log=stdout_log, stderr_log=stderr_log,
            timeout_seconds=min(int(executor_info.get("timeout_seconds") or 300), 300), executor="codex",
        )
        return self_review_result(result, _execution._tail_text(stdout_log, limit=1024 * 1024))
    except (OSError, RuntimeError, ValueError) as exc:
        return self_review_block(
            "unavailable-skip", reason=f"reviewer could not run: {exc}"
        )


SELF_REVIEW_DISPOSITIONS = ("fixed", "deferred", "disputed")
SELF_REVIEW_STATES = ("not-requested", "findings-received", "unavailable-skip")
_SELF_REVIEW_KIND = "charness.task_self_review.v1"
_SELF_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": [_SELF_REVIEW_KIND]},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "disposition": {"type": "string", "enum": list(SELF_REVIEW_DISPOSITIONS)},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "disposition", "evidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["kind", "findings"],
    "additionalProperties": False,
}


def self_review_block(
    state: str,
    *,
    findings: object = (),
    reason: str | None = None,
) -> dict[str, Any]:
    """Normalize self-review findings without turning a skip into a pass."""
    if state not in SELF_REVIEW_STATES:
        raise ValueError(f"unknown self-review state: {state}")
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in SELF_REVIEW_DISPOSITIONS}
    if state == "findings-received":
        if not isinstance(findings, (list, tuple)):
            raise ValueError("self-review findings must be a list")
        for item in findings:
            if not isinstance(item, Mapping) or item.get("disposition") not in grouped:
                raise ValueError("self-review finding needs fixed, deferred, or disputed disposition")
            summary, disposition = item.get("summary"), item["disposition"]
            if not isinstance(summary, str) or not summary.strip():
                raise ValueError("self-review finding summary must be non-empty")
            finding: dict[str, Any] = {"summary": summary.strip(), "disposition": disposition}
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not all(isinstance(value, str) for value in evidence):
                raise ValueError("self-review finding evidence must be a list of strings")
            finding["evidence"] = [value for value in evidence if value.strip()]
            grouped[disposition].append(finding)
    return {
        "kind": _SELF_REVIEW_KIND,
        "state": state,
        "findings": grouped,
        **({"reason": reason.strip()} if reason and reason.strip() else {}),
        "non_claim": "Self-review is not independent review or proof."
        if state == "findings-received"
        else "Self-review was not performed; this result is not review-passed.",
    }


def self_review_prompt(prompt: str, base_sha: str, changed_paths: list[str]) -> str:
    return (
        f"Fresh-context self-review only. Do not edit or run mutating commands. Inspect diff from {base_sha} "
        f"for {json.dumps(changed_paths)} against this request:\n{prompt}\n"
        "Return only JSON matching this schema: "
        f"{json.dumps(_SELF_REVIEW_SCHEMA, separators=(',', ':'))}. "
        "Every finding includes summary, disposition, and evidence as an array of strings; use [] when there is no evidence. "
        "Fixed means addressed, deferred means valid and unresolved, disputed means inapplicable. "
        "No findings does not claim independent review passed."
    )


def self_review_schema() -> dict[str, Any]:
    """Return the canonical constrained-output schema for the self-reviewer."""
    return json.loads(json.dumps(_SELF_REVIEW_SCHEMA))


def self_review_result(execution: Mapping[str, Any], text: str) -> dict[str, Any]:
    from scripts.task_run import task_run_state

    if execution.get("timed_out") or execution.get("exec_error") or execution.get("exit_code") != 0:
        reason = execution.get("exec_error") or (
            "reviewer timed out"
            if execution.get("timed_out")
            else f"reviewer exited with code {execution.get('exit_code')}"
        )
        return self_review_block("unavailable-skip", reason=f"reviewer did not return findings: {reason}")
    review = task_run_state.extract_structured_review(
        text.encode("utf-8"), kind=_SELF_REVIEW_KIND, limit=1024 * 1024
    )
    if review is None:
        return self_review_block("unavailable-skip", reason="reviewer did not return a self-review result")
    try:
        return self_review_block("findings-received", findings=review.get("findings"))
    except ValueError as exc:
        return self_review_block("unavailable-skip", reason=f"reviewer result was invalid: {exc}")
