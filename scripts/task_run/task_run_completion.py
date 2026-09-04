"""Finalize task-run receipts from execution and completion evidence."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.gates_support.runtime_root_retention import _rmtree_writable  # noqa: E402


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
    target_head: str | None = None,
    changed_line_gate: Callable[..., dict[str, Any]] | None = None,
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
        target_head=target_head,
    )
    carrier = scope.get("candidate_carrier", {})
    observed_head = carrier.get("observed_head_sha") if isinstance(carrier, Mapping) else None
    target_branch = carrier.get("observed_branch") if isinstance(carrier, Mapping) else None
    if target_branch is None and not observed_head:
        branch_result = git(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD")
        target_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    target_sha = observed_head or git_output(resolved_target, "rev-parse", "HEAD").strip()
    payload.update(
        {
            "phase": "terminal",
            "execution": execution,
            "result_delivery": delivery,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
            "target_sha": target_sha,
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

    blockers: list[str] = []
    if execution_status != "completed":
        blockers.append(f"execution: {execution_status}")
    if scope["verdict"] != pass_value:
        blockers.append(scope["reason"])
    if parent_progress["blocking"]:
        blockers.append("parent changed within the resolved candidate scope")

    # The changed-line gate runs where the claim is made. A lane whose candidate
    # the pre-push hook would refuse is useful but not done: the receipt says
    # `validated-partial-result`, names the unproven line, and the parent reads
    # at the receipt what it used to learn at the fourth refused push.
    gate = _changed_line_verdict(
        changed_line_gate,
        execution_status=execution_status,
        candidate=candidate,
        worktree=resolved_target,
        base_sha=base_sha,
        log_dir=stdout_log.parent,
    )
    payload["changed_line_gate"] = gate
    if gate.get("blocking"):
        blockers.append(str(gate.get("summary") or "changed-line gate refused the candidate"))
        if result_state == "completed":
            result_state = "validated-partial-result"

    payload["status"] = result_state
    payload["approval_eligibility"] = "eligible" if result_state == "completed" else "ineligible"

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
            f"Review the candidate in {resolved_target}; the typed result is approval-eligible."
        )
    persist(payload, runtime_path)
    retention = release_finished_lane(
        payload,
        resolved_repo=resolved_repo,
        resolved_target=resolved_target,
        record_dir=stdout_log.parent,
        git=git,
    )
    if retention is not None:
        payload["retention"] = retention
        payload["keep_worktree"] = retention.get("worktree") != "removed"
        if retention.get("worktree") == "removed":
            payload["next_step"] = (
                f"Review the candidate on branch {payload.get('target_branch')} at "
                f"{payload.get('target_sha')}; the typed result is approval-eligible and the "
                "lane worktree was released because that commit carries the whole candidate."
            )
        persist(payload, runtime_path)
    print(f"task run: {payload['status']} ({payload['task_id']})", file=sys.stderr)
    return payload


def release_finished_lane(
    payload: Mapping[str, Any],
    *,
    resolved_repo: Path,
    resolved_target: Path,
    record_dir: Path,
    git: Callable[..., Any],
) -> dict[str, Any] | None:
    """Drop a finished lane to `result.json` plus logs when its commit carries everything.

    A finished lane kept a 1.4 GB worktree and a 1.1 GB runtime beside a 60 KB
    receipt, 254 times over, and no rule reached them (#787). The candidate a
    parent integrates is the lane branch's commit; once `head_is_complete` says
    that commit IS the candidate, the worktree adds nothing the branch does not
    hold. A worktree-only or commit-plus-dirty candidate is retained: its dirty
    half exists nowhere else, and the retention sweep salvages it as a patch
    before it goes.
    """
    candidate = payload.get("candidate")
    if not isinstance(candidate, Mapping) or payload.get("status") != "completed":
        return None
    if not candidate.get("head_is_complete") or candidate.get("carrier_kind") != "commit-only":
        return {
            "worktree": "retained",
            "runtime": "retained",
            "reason": (
                f"carrier {candidate.get('carrier_kind')!r} is not carried whole by lane HEAD; "
                "the sweep salvages uncommitted edits before removing it"
            ),
        }
    retention: dict[str, Any] = {"worktree": "retained", "runtime": "retained"}
    removal = git(resolved_repo, "worktree", "remove", "--force", str(resolved_target))
    if removal.returncode != 0:
        retention["reason"] = f"git worktree remove failed: {removal.stderr.strip()[-300:]}"
        return retention
    retention["worktree"] = "removed"
    runtime_dir = record_dir / "runtime"
    if runtime_dir.is_dir():
        try:
            _rmtree_writable(runtime_dir)
            retention["runtime"] = "removed"
        except OSError as exc:
            retention["reason"] = f"runtime removal failed: {exc}"
    else:
        retention["runtime"] = "absent"
    retention["carrier"] = f"{payload.get('target_branch')}@{payload.get('target_sha')}"
    retention["kept"] = ["result.json", *sorted(p.name for p in record_dir.glob("*.log"))]
    return retention


def _changed_line_verdict(
    changed_line_gate: Callable[..., dict[str, Any]] | None,
    *,
    execution_status: str,
    candidate: Mapping[str, Any],
    worktree: Path,
    base_sha: str,
    log_dir: Path,
) -> dict[str, Any]:
    """Run the gate for a validated candidate; otherwise say why it did not run."""
    if changed_line_gate is None:
        return {
            "status": "not-run",
            "blocking": False,
            "reason": "no changed-line gate was supplied to completion",
            "summary": "changed-line gate not run: none supplied",
        }
    if execution_status != "completed" or not candidate.get("useful"):
        return {
            "status": "skipped",
            "blocking": False,
            "reason": (
                f"execution ended {execution_status} with candidate status "
                f"{candidate.get('status')!r}; there is no validated candidate to judge"
            ),
            "summary": "changed-line gate skipped: no validated candidate",
        }
    return changed_line_gate(worktree, base_sha=base_sha, log_dir=log_dir)
