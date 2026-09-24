#!/usr/bin/env python3
"""Derive a task run's state from the result of executing it.

Pure derivation: nothing here runs a child, touches a worktree, or persists a
record. It answers one question -- given what the execution and scope observed,
what state is this run in -- so the answer can be read and reviewed without
following the orchestration around it.

`_execution_state` and `_abnormal_exit_state` both run the one
`_abnormal_child_state` order: the former layers the delivery question after
it, the latter skips delivery, which is not yet answered where it is called.
Sharing the helper (instead of repeating the predicates) is what stops the
WIP checkpoint and the reported status from naming two different things about
one run. Separating them across modules would put that invariant across a
boundary no reader crosses by accident.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_support as _support  # noqa: E402

PASS = _support.PASS
TaskRunError = _support.TaskRunError


class ResultKind(str, Enum):
    """Stable public outcomes for task-run receipts and command exit codes."""

    SUCCESS = "success"
    FAILED = "failed"
    PREMISE_BLOCKED = "premise-blocked"
    VALIDATED_PARTIAL = "validated-partial"
    EXECUTOR_UNAVAILABLE = "executor-unavailable"
    COMPLETED_NEEDS_REVIEW = "completed-needs-review"


RESULT_EXIT_CODES = {
    ResultKind.SUCCESS: 0,
    ResultKind.FAILED: 1,
    ResultKind.PREMISE_BLOCKED: 2,
    ResultKind.VALIDATED_PARTIAL: 3,
    ResultKind.EXECUTOR_UNAVAILABLE: 4,
    ResultKind.COMPLETED_NEEDS_REVIEW: 5,
}

_RESULT_KIND_BY_STATUS = {
    "completed": ResultKind.SUCCESS,
    "pass": ResultKind.SUCCESS,
    "failed": ResultKind.FAILED,
    "fail": ResultKind.FAILED,
    "premise-blocked": ResultKind.PREMISE_BLOCKED,
    "validated-partial-result": ResultKind.VALIDATED_PARTIAL,
    "executor-unavailable": ResultKind.EXECUTOR_UNAVAILABLE,
    "completed-needs-review": ResultKind.COMPLETED_NEEDS_REVIEW,
}


def result_kind_for_status(status: object) -> ResultKind:
    """Map a lane status to the frozen public result vocabulary."""
    if not isinstance(status, str):
        return ResultKind.FAILED
    return _RESULT_KIND_BY_STATUS.get(status, ResultKind.FAILED)


def result_kind_for_receipt(receipt: object) -> ResultKind:
    """Read a typed result kind, falling back to legacy status receipts."""
    if not isinstance(receipt, Mapping):
        return ResultKind.FAILED
    explicit = receipt.get("result_kind")
    if explicit is not None:
        try:
            return ResultKind(explicit)
        except (TypeError, ValueError):
            return ResultKind.FAILED
    return result_kind_for_status(receipt.get("status"))


def exit_code_for_result_kind(kind: ResultKind | str) -> int:
    """Return the unique command exit code assigned to a result kind."""
    return RESULT_EXIT_CODES[ResultKind(kind)]


def blocker_for_receipt(receipt: Mapping[str, Any]) -> str | None:
    """Return the primary stable blocker, preserving the most specific fact."""
    blocker = receipt.get("blocker")
    if isinstance(blocker, str) and blocker.strip():
        return blocker.strip()
    progress = receipt.get("lane_progress")
    if isinstance(progress, Mapping):
        blocker = progress.get("blocker")
        if isinstance(blocker, str) and blocker.strip():
            return blocker.strip()
    blockers = receipt.get("blockers")
    if isinstance(blockers, list):
        first = next(
            (item.strip() for item in blockers if isinstance(item, str) and item.strip()),
            None,
        )
        if first is not None:
            return first
    error = receipt.get("error")
    return error.strip() if isinstance(error, str) and error.strip() else None


#: Post-execution states whose worktree holds work no one has typed yet. A timeout
#: was the only one preserved, but the issue that asked for it named "timeout AND
#: any abnormal child exit": a signal and a non-zero exit leave the same untyped
#: pile, and the parent then triages it by hand or re-runs the whole lane.
_ABNORMAL_EXIT_STATES = ("timed-out", "interrupted", "failed")

#: Finished lanes whose agent work exists but the gates cannot approve: the
#: orchestrator merges or re-scopes them instead of relaunching (#829). This
#: is an agent-outcome/gate-outcome split, never approval: eligibility still
#: requires a clean `completed`.
NEEDS_REVIEW_STATE = "completed-needs-review"


#: Typed executor/infra failure kinds carried on the receipt's `failure`
#: field so a poller reads the cause without forensics (#829). Only the
#: transient model-stream stall is retryable.
FAILURE_KINDS = (
    "none",
    "executor-unavailable",
    "model-stream-idle",
    "timed-out",
    "interrupted",
    "executor-error",
    "delivery-failed",
)
_RETRYABLE_FAILURES = frozenset({"model-stream-idle"})


def _abnormal_child_state(execution: dict[str, Any]) -> str | None:
    """The one abnormal-exit predicate order every state question shares.

    `_abnormal_exit_state` (asked before delivery, for the WIP checkpoint)
    and `_execution_state` (asked after delivery, for the receipt) both run
    this order, so the checkpoint and the reported status cannot name two
    different states for one run. `progress_stopped` stays outside it: a
    guard kill is an explicitly identified cause, layered before the flag
    checks rather than inferred from them.
    """
    if execution["timed_out"]:
        return "timed-out"
    if execution["interrupted"] or (
        execution["exit_code"] is not None and execution["exit_code"] < 0
    ):
        return "interrupted"
    if isinstance(execution.get("executor_unavailable"), Mapping):
        return "executor-unavailable"
    if execution.get("exec_error") or execution["exit_code"] is None:
        return "failed"
    if execution["exit_code"] != 0:
        return "failed"
    return None


def _execution_state(execution: dict[str, Any], delivery: dict[str, Any]) -> str:
    if execution.get("progress_stopped"):
        return "failed"
    abnormal = _abnormal_child_state(execution)
    if abnormal is not None:
        return abnormal
    if delivery["status"] == "non-delivery":
        return "non-delivery"
    return "completed"


def _idle_stall_line(stderr_text: str) -> str | None:
    """First transcript line naming a transient model-stream stall, if any.

    An "agent loop failed" line counts only alongside idle wording, so a
    fatal loop error (auth, config) fails fast instead of burning retries.
    """
    for line in stderr_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if "model stream idle" in lowered or (
            "agent loop failed" in lowered and "idle" in lowered
        ):
            return stripped[:300]
    return None


def executor_unavailable_reason(
    execution: Mapping[str, Any], transcript: str
) -> dict[str, str | None] | None:
    """Recognize a failed quota refusal and retain its nearest retry hint."""
    if execution.get("timed_out") or execution.get("interrupted"):
        return None
    if not (execution.get("exec_error") or execution.get("exit_code") != 0):
        return None
    markers = ("usage limit", "usage limits", "out of quota", "quota exceeded", "quota limit")
    retry_patterns = (
        r"\btry again\s+(?:at|after|on|in)\s+(.+)$",
        r"\b(?:retry|available again|resets?)\s+(?:at|after|on|in|until)\s+(.+)$",
        r"\buntil\s+(.+)$",
    )
    lines = transcript.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or not any(marker in stripped.lower() for marker in markers):
            continue
        retry_text = " ".join(
            candidate.strip() for candidate in lines[index : index + 3] if candidate.strip()
        )
        retry_after = next(
            (
                match.group(1).strip().rstrip(" .") or None
                for pattern in retry_patterns
                if (match := re.search(pattern, retry_text, flags=re.IGNORECASE))
            ),
            None,
        )
        return {"message": stripped[:300], "retry_after": retry_after}
    return None


def classify_failure(
    execution: Mapping[str, Any] | dict[str, Any],
    *,
    stderr_text: str = "",
    delivery: Mapping[str, Any] | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Typed executor/infra failure for the receipt, from the executor's own reason (#829).

    Tolerant of sparse inputs (tests and lifecycle paths pass partial
    execution records): unknown shapes read as `executor-error`, never crash.
    """
    execution = execution if isinstance(execution, Mapping) else {}
    delivery = delivery if isinstance(delivery, Mapping) else {}
    if execution.get("timed_out"):
        return {"kind": "timed-out", "retryable": False, "message": "lane exceeded its timeout"}
    if execution.get("interrupted") or (
        isinstance(execution.get("exit_code"), int) and execution["exit_code"] < 0
    ):
        return {"kind": "interrupted", "retryable": False, "message": "lane was interrupted"}
    unavailable = execution.get("executor_unavailable")
    if isinstance(unavailable, Mapping):
        return {
            "kind": "executor-unavailable",
            "retryable": False,
            "message": str(unavailable.get("message") or "executor usage limit reached")[:300],
            "retry_after": unavailable.get("retry_after"),
        }
    idle = _idle_stall_line(stderr_text or "")
    exit_code = execution.get("exit_code")
    abnormal_exit = exit_code is None or (isinstance(exit_code, int) and exit_code != 0)
    if idle is not None and abnormal_exit and not execution.get("exec_error"):
        return {"kind": "model-stream-idle", "retryable": True, "message": idle}
    if execution.get("exec_error") or exit_code is None:
        detail = execution.get("exec_error") or "executor exit code is unknown"
        return {"kind": "executor-error", "retryable": False, "message": str(detail)[:300]}
    if isinstance(exit_code, int) and exit_code != 0:
        return {
            "kind": "executor-error",
            "retryable": False,
            "message": f"executor exited with code {exit_code}",
        }
    if delivery.get("status") == "non-delivery" or delivery.get("delivery_error"):
        detail = delivery.get("delivery_error") or "executor produced no result delivery"
        return {"kind": "delivery-failed", "retryable": False, "message": str(detail)[:300]}
    return {"kind": "none", "retryable": False, "message": ""}


def review_reasons(
    *,
    scope: Mapping[str, Any] | dict[str, Any],
    parent_progress: Mapping[str, Any] | dict[str, Any],
    persistence: Mapping[str, Any] | dict[str, Any] | None = None,
) -> list[str]:
    """Why a finished lane needs operator review instead of a relaunch (#829)."""
    reasons = []
    if isinstance(scope, Mapping) and scope.get("disallowed_paths"):
        reasons.append("out-of-scope-paths")
    if isinstance(parent_progress, Mapping) and parent_progress.get("blocking"):
        reasons.append("parent-progress")
    if isinstance(persistence, Mapping) and persistence.get("blocking"):
        reasons.append("persistence-risk")
    return reasons


def apply_persistence_state(
    result_state: str, persistence: Mapping[str, Any] | dict[str, Any] | None
) -> str:
    """A finished lane that discards persisted data is needs-review, never clean (#830)."""
    if (
        isinstance(persistence, Mapping)
        and persistence.get("blocking")
        and result_state in ("completed", "validated-partial-result")
    ):
        return NEEDS_REVIEW_STATE
    return result_state


def _abnormal_exit_state(execution: dict[str, Any]) -> str | None:
    """The abnormal post-execution state, or None when the child exited normally.

    The shared `_abnormal_child_state` order, minus the delivery question,
    which is not yet answered where this is called.
    """
    return _abnormal_child_state(execution)


def _checkpoint_found_no_changes(
    candidate: dict[str, Any], candidate_commit: dict[str, Any]
) -> bool:
    """Whether the WIP checkpoint proved the worktree held no scoped changes.

    A skipped checkpoint plus an empty scope verdict means the lane was
    stopped before its first edit (#822): there is no partial code to salvage,
    so the candidate reports a known unchanged state instead of
    `interrupted-mid-edit`. A failed checkpoint is genuinely unknown and keeps
    the WIP shape.
    """
    return (
        candidate_commit.get("status") == "skipped"
        and not candidate.get("changed_paths")
        and not candidate.get("disallowed_paths")
    )


def _candidate_result_state(
    *,
    execution_state: str,
    scope: dict[str, Any],
    parent_progress: dict[str, Any],
    candidate_commit: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    changed_paths = scope["changed_paths"]
    candidate_valid = scope["verdict"] == PASS
    candidate_useful = candidate_valid and bool(changed_paths)
    candidate = {
        "status": "validated" if candidate_useful else "absent" if candidate_valid else "invalid",
        "useful": candidate_useful,
        "changed_paths": changed_paths,
        "disallowed_paths": list(scope.get("disallowed_paths", ())),
        **scope["candidate_carrier"],
    }
    if execution_state == "executor-unavailable":
        candidate["status"] = "absent"
        return candidate, execution_state
    if execution_state in _ABNORMAL_EXIT_STATES:
        if candidate_commit is None:
            raise TaskRunError(f"{execution_state} task is missing its WIP candidate commit")
        if _checkpoint_found_no_changes(candidate, candidate_commit):
            candidate.update(
                {
                    "status": "absent",
                    "state": f"{execution_state}-before-edit",
                    "state_known": True,
                    "commit": candidate_commit,
                }
            )
            return candidate, execution_state
        candidate.update(
            {
                "status": "wip",
                "state": "interrupted-mid-edit",
                "state_known": False,
                "commit": candidate_commit,
            }
        )
        return candidate, execution_state
    if candidate_valid and execution_state == "completed" and not parent_progress["blocking"]:
        return candidate, "completed"
    if candidate_useful:
        return candidate, "validated-partial-result"
    if (
        execution_state == "completed"
        and (changed_paths or scope.get("disallowed_paths"))
        and (not candidate_valid or parent_progress["blocking"])
    ):
        return candidate, NEEDS_REVIEW_STATE
    if not candidate_valid or parent_progress["blocking"]:
        return candidate, "failed"
    return candidate, execution_state
