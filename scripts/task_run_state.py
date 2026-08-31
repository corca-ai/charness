#!/usr/bin/env python3
"""Derive a task run's state from the result of executing it.

Pure derivation: nothing here runs a child, touches a worktree, or persists a
record. It answers one question -- given what the execution and scope observed,
what state is this run in -- so the answer can be read and reviewed without
following the orchestration around it.

`_execution_state` and `_abnormal_exit_state` are split out TOGETHER on purpose,
and the second one's own comment says why: it repeats the first's predicate order
minus the delivery question, and keeping the two orders identical is what stops
the WIP checkpoint and the reported status from naming two different things about
one run. Separating them across modules would put that invariant across a
boundary no reader crosses by accident.
"""
from __future__ import annotations

from typing import Any

from scripts import task_run_support as _support

PASS = _support.PASS
TaskRunError = _support.TaskRunError


#: Post-execution states whose worktree holds work no one has typed yet. A timeout
#: was the only one preserved, but the issue that asked for it named "timeout AND
#: any abnormal child exit": a signal and a non-zero exit leave the same untyped
#: pile, and the parent then triages it by hand or re-runs the whole lane.
_ABNORMAL_EXIT_STATES = ("timed-out", "interrupted", "failed")


def _execution_state(execution: dict[str, Any], delivery: dict[str, Any]) -> str:
    if execution["interrupted"] or (
        execution["exit_code"] is not None and execution["exit_code"] < 0
    ):
        return "interrupted"
    if execution["timed_out"]:
        return "timed-out"
    if execution.get("exec_error") or execution["exit_code"] is None:
        return "failed"
    if execution["exit_code"] != 0:
        return "failed"
    if delivery["status"] == "non-delivery":
        return "non-delivery"
    return "completed"


def _abnormal_exit_state(execution: dict[str, Any]) -> str | None:
    """The abnormal post-execution state, or None when the child exited normally.

    Deliberately the same predicate order as `_execution_state`, minus the delivery
    question, which is not yet answered where this is called. Keeping the order
    identical is what stops the WIP checkpoint and the reported status from naming
    two different things about one run.
    """
    if execution["timed_out"]:
        return "timed-out"
    if execution["interrupted"] or (
        execution["exit_code"] is not None and execution["exit_code"] < 0
    ):
        return "interrupted"
    if execution.get("exec_error") or execution["exit_code"] is None:
        return "failed"
    if execution["exit_code"] != 0:
        return "failed"
    return None


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
        **scope["candidate_carrier"],
    }
    if execution_state in _ABNORMAL_EXIT_STATES:
        if candidate_commit is None:
            raise TaskRunError(f"{execution_state} task is missing its WIP candidate commit")
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
    if not candidate_valid or parent_progress["blocking"]:
        return candidate, "failed"
    return candidate, execution_state
