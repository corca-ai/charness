"""Finalize task-run receipts from execution and completion evidence."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping


def complete_task(
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
    persist: Callable[[dict[str, Any], Path], None],
    result_delivery: Callable[[Path], dict[str, Any]],
    completion_evidence: Callable[..., tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    execution_state: Callable[[dict[str, Any], dict[str, Any]], str],
    candidate_result_state: Callable[..., tuple[dict[str, Any], str]],
    candidate_commit: dict[str, Any] | None,
    git: Callable[..., Any],
    git_output: Callable[..., str],
    pass_value: str,
) -> dict[str, Any]:
    delivery = result_delivery(stdout_log)
    evidence, scope, parent_progress = completion_evidence(
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
        git_output(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
        if git(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD").returncode == 0
        else None
    )
    payload.update(
        {
            "phase": "terminal",
            "execution": execution,
            "result_delivery": delivery,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
            "target_sha": git_output(resolved_target, "rev-parse", "HEAD").strip(),
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

    execution_status = execution_state(execution, delivery)
    payload["execution"]["status"] = execution_status
    candidate, result_state = candidate_result_state(
        execution_state=execution_status,
        scope=scope,
        parent_progress=parent_progress,
        candidate_commit=candidate_commit,
    )
    payload["candidate"] = candidate
    payload["status"] = result_state
    payload["approval_eligibility"] = "eligible" if result_state == "completed" else "ineligible"

    blockers: list[str] = []
    if execution_status != "completed":
        blockers.append(f"execution: {execution_status}")
    if scope["verdict"] != pass_value:
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

    if execution_status == "timed-out":
        payload["next_step"] = (
            f"Review the committed WIP candidate in {resolved_target}; "
            "interrupted mid-edit — state unknown; the commit is not a correctness claim"
            + (f"; {'; '.join(blockers)}." if blockers else ".")
        )
    elif blockers:
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
    persist(payload, runtime_path)
    print(f"task run: {payload['status']} ({payload['task_id']})", file=sys.stderr)
    return payload
