"""Frozen task-run result kinds, receipt fields, and CLI exit behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.task_run import task_run, task_run_events, task_run_payload, task_run_state
from tests.charness_cli.support import CLI, load_cli_module
from tests.charness_cli.test_task_run_completion import _complete
from tests.script_main import run_loaded_script_main


def test_result_kinds_have_one_exit_code_each() -> None:
    assert task_run_state.RESULT_EXIT_CODES == {
        task_run_state.ResultKind.SUCCESS: 0,
        task_run_state.ResultKind.FAILED: 1,
        task_run_state.ResultKind.PREMISE_BLOCKED: 2,
        task_run_state.ResultKind.VALIDATED_PARTIAL: 3,
        task_run_state.ResultKind.EXECUTOR_UNAVAILABLE: 4,
        task_run_state.ResultKind.COMPLETED_NEEDS_REVIEW: 5,
    }
    assert len(set(task_run_state.RESULT_EXIT_CODES.values())) == len(task_run_state.ResultKind)
    assert (
        task_run_state.result_kind_for_status("premise-blocked")
        is task_run_state.ResultKind.PREMISE_BLOCKED
    )
    assert (
        task_run_state.result_kind_for_status("executor-unavailable")
        is task_run_state.ResultKind.EXECUTOR_UNAVAILABLE
    )
    assert (
        task_run_state.result_kind_for_status("completed-needs-review")
        is task_run_state.ResultKind.COMPLETED_NEEDS_REVIEW
    )


def test_completion_receipt_emits_kind_and_stable_blocker_separately(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(tmp_path, candidate_kind="dirty", scope_verdict="fail")

    assert payload["status"] == "validated-partial-result"
    assert payload["result_kind"] == "validated-partial"
    assert payload["blocker"] == "scope drifted"
    assert "scope drifted" in payload["blockers"]
    assert payload["candidate"]["persist"]["status"] == "committed"
    assert payload["candidate"]["persist"]["after_block"] is True
    assert payload["candidate"]["persist"]["correctness_verified"] is False
    assert payload["approval_eligibility"] == "ineligible"
    assert "persistence=committed" in payload["next_step"]
    assert "correctness unverified" in payload["next_step"]
    assert "approval_eligibility=ineligible" in payload["next_step"]
    capsys.readouterr()


def test_terminal_receipt_persists_kind_and_blocker_before_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocker = "requested behavior has no verified owner"
    persisted: list[dict[str, object]] = []
    monkeypatch.setattr(
        task_run_payload,
        "_persist",
        lambda payload, _path: persisted.append(dict(payload)),
    )
    payload = {"lane_progress": {"blocker": blocker}}

    result = task_run._terminal(
        payload,
        tmp_path / "result.json",
        status="premise-blocked",
        next_step="Inspect the declared blocker before retrying.",
    )

    assert result["result_kind"] == "premise-blocked"
    assert result["blocker"] == blocker
    assert persisted == [result]


@pytest.mark.parametrize(
    ("status", "result_kind", "exit_code"),
    [
        ("completed", "success", 0),
        ("failed", "failed", 1),
        ("validated-partial-result", "validated-partial", 3),
        ("executor-unavailable", "executor-unavailable", 4),
    ],
)
def test_task_run_cli_maps_other_terminal_kinds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    result_kind: str,
    exit_code: int,
) -> None:
    result = _run_task_cli_with_receipt(
        tmp_path,
        monkeypatch,
        {
            "status": status,
            "approval_eligibility": "eligible" if status == "completed" else "ineligible",
        },
    )

    assert result.returncode == exit_code
    assert yaml.safe_load(result.stdout)["result_kind"] == result_kind


def _run_task_cli_with_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, receipt: dict[str, object]
):
    module = load_cli_module(f"charness_task_run_exit_{receipt.get('result_kind')}", CLI)

    class FakeTaskRun:
        @staticmethod
        def run_task(*_args: object, **_kwargs: object) -> dict[str, object]:
            return dict(receipt)

    import scripts.cli.cmd_task as task_payload

    monkeypatch.setattr(task_payload, "_load_task_run_lib", lambda _args: FakeTaskRun)
    return run_loaded_script_main(
        str(CLI),
        module,
        "task",
        "run",
        "--repo-root",
        str(tmp_path),
        "--lane",
        "fixture-lane",
        "--scope",
        "module.py",
        "--prompt",
        "fixture",
        "--effort",
        "medium",
    )


def test_premise_blocked_fixture_exits_two_and_keeps_blocker_in_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocker = "premise is false: the requested behavior has no active consumer"
    result = _run_task_cli_with_receipt(
        tmp_path,
        monkeypatch,
        {
            "status": "premise-blocked",
            "blocker": blocker,
            "approval_eligibility": "ineligible",
        },
    )

    assert result.returncode == 2
    receipt = yaml.safe_load(result.stdout)
    assert receipt["result_kind"] == "premise-blocked"
    assert receipt["blocker"] == blocker


def test_completed_needs_review_fixture_exits_five(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _run_task_cli_with_receipt(
        tmp_path,
        monkeypatch,
        {
            "status": "completed-needs-review",
            "blocker": "review the persistence-risk finding",
            "approval_eligibility": "ineligible",
        },
    )

    assert result.returncode == 5
    receipt = yaml.safe_load(result.stdout)
    assert receipt["result_kind"] == "completed-needs-review"


def test_task_run_help_documents_all_six_codes() -> None:
    module = load_cli_module("charness_task_run_exit_help", CLI)
    result = run_loaded_script_main(str(CLI), module, "task", "run", "--help")

    assert result.returncode == 0
    for mapping in (
        "0 success",
        "1 failed",
        "2 premise-blocked",
        "3 validated-partial",
        "4 executor-unavailable",
        "5 completed-needs-review",
    ):
        assert mapping in result.stdout


@pytest.mark.parametrize(
    ("source", "event_kind"),
    [
        ("decision-ledger", "contract-amendment"),
        ("decision-ledger", "vocabulary-closure"),
        ("decision-ledger", "design-approval"),
        ("friction-log", "block"),
        ("friction-log", "relaunch"),
        ("friction-log", "conflict-resolution"),
        ("friction-log", "premise-failure"),
    ],
)
def test_event_schema_v1_accepts_each_frozen_producer_kind(source: str, event_kind: str) -> None:
    event = {
        "schema_version": 1,
        "event_id": "event-1",
        "occurred_at": "2026-09-24T12:00:00Z",
        "source": source,
        "event_kind": event_kind,
        "facts": {"reason": "fixture", "attempt": 2},
    }

    assert task_run_events.validate_event(event) == event


@pytest.mark.parametrize(
    "event",
    [
        None,
        {"schema_version": 2},
        {
            "schema_version": 1,
            "event_id": "event-1",
            "occurred_at": "2026-09-24T12:00:00+09:00",
            "source": "friction-log",
            "event_kind": "block",
            "facts": {},
        },
        {
            "schema_version": 1,
            "event_id": "event-1",
            "occurred_at": "2026-09-24T12:00:00Z",
            "source": "friction-log",
            "event_kind": "design-approval",
            "facts": {},
        },
        {
            "schema_version": 1,
            "event_id": "event-1",
            "occurred_at": "2026-09-24T12:00:00Z",
            "source": "friction-log",
            "event_kind": "block",
            "facts": {"bad": float("nan")},
        },
    ],
)
def test_event_schema_v1_rejects_malformed_events(event: object) -> None:
    with pytest.raises(task_run_events.EventSchemaError):
        task_run_events.validate_event(event)
