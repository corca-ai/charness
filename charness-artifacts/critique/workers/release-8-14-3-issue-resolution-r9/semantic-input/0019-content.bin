"""Interrupted-before-first-edit classification (#822).

An interrupted lane whose WIP checkpoint proved the worktree held no scoped
changes must report a known unchanged candidate, not `interrupted-mid-edit`.
Only a worktree that actually contains changes keeps the WIP shape.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run_state
from scripts.task_run.task_run_completion_next_step import _next_step


def _scope(*, changed: list[str] | None = None) -> dict:
    return {
        "verdict": task_run_state.PASS,
        "reason": "scope clean",
        "changed_paths": changed or [],
        "disallowed_paths": [],
        "candidate_carrier": {},
    }


def _skipped_commit() -> dict:
    return {
        "status": "skipped",
        "reason": "no scoped changes: no WIP candidate commit created",
        "changed_paths": [],
        "correctness_verified": False,
    }


def test_unchanged_interrupted_lane_is_known_before_edit() -> None:
    candidate, result_state = task_run_state._candidate_result_state(
        execution_state="interrupted",
        scope=_scope(),
        parent_progress={"blocking": False},
        candidate_commit=_skipped_commit(),
    )
    assert result_state == "interrupted"
    assert candidate["status"] == "absent"
    assert candidate["state"] == "interrupted-before-edit"
    assert candidate["state_known"] is True


def test_unchanged_timed_out_lane_is_known_before_edit() -> None:
    candidate, result_state = task_run_state._candidate_result_state(
        execution_state="timed-out",
        scope=_scope(),
        parent_progress={"blocking": False},
        candidate_commit=_skipped_commit(),
    )
    assert candidate["status"] == "absent"
    assert candidate["state"] == "timed-out-before-edit"
    assert candidate["state_known"] is True


def test_partial_edit_keeps_wip_mid_edit() -> None:
    candidate, _ = task_run_state._candidate_result_state(
        execution_state="interrupted",
        scope=_scope(changed=["gateway/lease.py"]),
        parent_progress={"blocking": False},
        candidate_commit={"status": "committed", "changed_paths": ["gateway/lease.py"]},
    )
    assert candidate["status"] == "wip"
    assert candidate["state"] == "interrupted-mid-edit"
    assert candidate["state_known"] is False


def test_failed_checkpoint_keeps_unknown_wip() -> None:
    candidate, _ = task_run_state._candidate_result_state(
        execution_state="interrupted",
        scope=_scope(),
        parent_progress={"blocking": False},
        candidate_commit={"status": "failed", "error": "commit refused"},
    )
    assert candidate["status"] == "wip"
    assert candidate["state"] == "interrupted-mid-edit"
    assert candidate["state_known"] is False


def test_before_edit_next_step_recommends_cleanup_not_salvage() -> None:
    step = _next_step(
        {"task_id": "lane-1"},
        resolved_target=Path("/tmp/lane"),
        candidate={"commit": _skipped_commit()},
        execution_status="interrupted",
        result_state="interrupted",
        blockers=["execution: interrupted"],
    )
    assert "clean up" in step
    assert "corrected scope" in step
    assert "WIP" not in step
    assert "mid-edit" not in step


def test_combined_timeout_and_interrupt_agree_on_timed_out() -> None:
    execution = {"exit_code": -15, "timed_out": True, "interrupted": True}
    assert task_run_state._abnormal_exit_state(execution) == "timed-out"
    assert (
        task_run_state._execution_state(execution, {"status": "delivered"})
        == "timed-out"
    )


def test_progress_stop_plus_negative_exit_splits_checkpoint_and_receipt() -> None:
    execution = {
        "exit_code": -15,
        "timed_out": False,
        "interrupted": False,
        "progress_stopped": "no EDITING and no scoped diff within 300s",
    }
    assert task_run_state._abnormal_exit_state(execution) == "interrupted"
    assert (
        task_run_state._execution_state(execution, {"status": "non-delivery"})
        == "failed"
    )


def test_progress_stopped_execution_is_failed() -> None:
    execution = {
        "exit_code": -15,
        "timed_out": False,
        "interrupted": False,
        "progress_stopped": "no EDITING and no scoped diff within 300s after CONTRACT-READ",
    }
    assert (
        task_run_state._execution_state(execution, {"status": "non-delivery"}) == "failed"
    )
