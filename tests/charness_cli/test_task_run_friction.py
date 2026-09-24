"""Task-run friction logging, recurrence escalation, and prompt reinjection."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.task_run import (
    task_run,
    task_run_friction,
    task_run_lane_runner,
    task_run_prelaunch,
)


def _events(runtime_path: Path) -> list[dict[str, object]]:
    path = task_run_friction.friction_log_path(runtime_path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_block_terminalization_appends_frozen_friction_event(tmp_path: Path) -> None:
    runtime_path = tmp_path / "runtime"
    payload = {"task_id": "blocked-lane", "status": "running", "phase": "exec"}

    terminal = task_run._terminal(
        payload,
        runtime_path,
        status="failed",
        next_step="Inspect the retained worktree before retrying.",
    )

    assert terminal["status"] == "failed"
    [event] = _events(runtime_path)
    assert event["schema_version"] == 1
    assert event["source"] == "friction-log"
    assert event["event_kind"] == "block"
    assert event["facts"]["task_id"] == "blocked-lane"


def test_second_same_kind_premise_failure_escalates_within_window(tmp_path: Path) -> None:
    runtime_path = tmp_path / "runtime"
    first = task_run_friction.append_friction_event(
        runtime_path,
        "premise-failure",
        task_id="wi-6-attempt-1",
        facts={"premise": "lesson ledger lacks scope tags"},
        occurred_at="2026-09-10T00:00:00Z",
    )
    second = task_run_friction.append_friction_event(
        runtime_path,
        "premise-failure",
        task_id="wi-7-attempt-1",
        facts={"premise": "review lifecycle belongs to critique"},
        occurred_at="2026-09-24T00:00:00Z",
    )

    assert first is not None
    assert second is not None
    assert second["facts"]["escalation"] == "repair the pattern, don't reshape the command"
    assert second["facts"]["matching_event_ids"] == [first["event_id"]]


def test_premise_failure_and_scope_refusal_append_events(tmp_path: Path) -> None:
    runtime_path = tmp_path / "runtime"
    resolved = {
        "runtime_path": runtime_path,
        "target_path": tmp_path,
        "prelaunch": {
            "enabled": True,
            "critical_lane": False,
            "acceptance_skeleton": None,
            "premise_checks": [],
        },
    }
    blocker = task_run_prelaunch.run_prelaunch_gates(
        {"task_id": "premise-lane"},
        resolved,
        "brief",
        brief_critic=lambda **_kwargs: {
            "status": "completed",
            "premise_failure": True,
            "premise_failure_reason": "owner is outside the declared contract",
        },
    )
    assert blocker == "owner is outside the declared contract"

    lane_payload = {"task_id": "scope-lane", "runtime_root": str(runtime_path)}
    lane_blockers: list[str] = []
    task_run_lane_runner.apply_lane_receipt(
        lane_payload,
        lane_blockers,
        delivery={
            "text": "BLOCKED: scope mismatch - real owner scripts/owner.py is outside declared scope - edit its owning module.\n"
        },
        require_change=True,
        scope={"changed_paths": [], "disallowed_paths": []},
    )

    assert [event["event_kind"] for event in _events(runtime_path)] == [
        "premise-failure",
        "block",
    ]


def test_execution_relaunch_and_writer_conflict_are_recorded(tmp_path: Path) -> None:
    runtime_path = tmp_path / "runtime"
    task_run_friction.append_execution_friction(
        runtime_path,
        task_id="execution-lane",
        relaunch_count=1,
        execution_error="executor transport closed",
    )
    task_run_friction.append_completion_friction(
        runtime_path,
        task_id="conflict-lane",
        blockers=["parent changed inside candidate scope"],
        parent_classification="writer-conflict",
    )

    events = _events(runtime_path)
    assert [event["event_kind"] for event in events] == [
        "relaunch",
        "block",
        "conflict-resolution",
    ]
    assert events[-1]["facts"]["resolution"] == "operator-needed"


def test_improvements_line_and_retro_cadence_are_documented() -> None:
    docs = Path("docs/agent-task-runs.md").read_text(encoding="utf-8")

    assert "after every five lane" in docs
    assert "improvements found: <concise items>" in docs
    assert "improvements found: none" in docs


def test_unreadable_store_and_foreign_lines_never_change_lane_semantics(
    tmp_path: Path,
) -> None:
    blocker = tmp_path / "blocker-file"
    blocker.write_text("not a directory", encoding="utf-8")
    assert (
        task_run_friction.append_friction_event(blocker, "block", task_id="t1")
        is None
    )

    runtime_path = tmp_path / "runtime"
    log_path = task_run_friction.friction_log_path(runtime_path)
    log_path.parent.mkdir(parents=True)
    log_path.write_text("not json\n", encoding="utf-8")
    assert (
        task_run_friction.append_friction_event(runtime_path, "block", task_id="t2")
        is None
    )

    foreign = {
        "schema_version": 1,
        "event_id": "foreign-1",
        "occurred_at": "2026-09-24T00:00:00Z",
        "source": "decision-ledger",
        "event_kind": "design-approval",
        "facts": {},
    }
    log_path.write_text(json.dumps(foreign) + "\n", encoding="utf-8")
    assert (
        task_run_friction.append_friction_event(runtime_path, "block", task_id="t3")
        is None
    )


def test_terminal_success_writes_nothing_and_premise_blocked_writes_block(
    tmp_path: Path,
) -> None:
    runtime_path = tmp_path / "runtime"
    assert (
        task_run_friction.append_terminal_friction(
            runtime_path, {"task_id": "s", "status": "completed"}
        )
        is None
    )
    assert not task_run_friction.friction_log_path(runtime_path).exists()

    task_run_friction.append_terminal_friction(
        runtime_path, {"task_id": "p", "status": "premise-blocked"}
    )
    [event] = _events(runtime_path)
    assert event["event_kind"] == "block"
    assert event["facts"]["task_id"] == "p"


def test_pointer_file_is_read_for_each_built_lane_prompt(tmp_path: Path) -> None:
    pointer_file = tmp_path / task_run_lane_runner.ORCHESTRATION_POINTERS_RELATIVE_PATH
    pointer_file.parent.mkdir(parents=True)
    pointer_file.write_text("Principles: docs/design-north-star.md", encoding="utf-8")

    first = task_run_lane_runner.build_lane_prompt(
        "continue the orchestration",
        require_change=False,
        scopes=[],
        lesson_injection_block="Injected lessons",
        orchestration_pointer_file=pointer_file,
    )
    pointer_file.write_text("DAG: plan.yaml; handoff: handoff.md", encoding="utf-8")
    resumed = task_run_lane_runner.build_lane_prompt(
        "continue after compaction",
        require_change=False,
        scopes=[],
        lesson_injection_block="Injected lessons",
        orchestration_pointer_file=pointer_file,
    )

    assert "Injected lessons" in first
    assert "Principles: docs/design-north-star.md" in first
    assert "DAG: plan.yaml; handoff: handoff.md" in resumed
    assert "Orchestration pointers (re-injected for this lane):" in resumed
