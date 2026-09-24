"""Task-run report economy and decision-ledger links."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.task_run import task_run_events, task_run_evidence, task_run_ledger, task_run_plan
from tests.charness_cli.test_task_run_fixtures import _codex, _repo, _run


def _decision_event(event_id: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "event_id": event_id,
        "occurred_at": "2026-09-24T12:00:00Z",
        "source": "decision-ledger",
        "event_kind": "contract-amendment",
        "facts": {"decision": "keep provider closeout authoritative"},
    }


def test_task_result_returns_short_summary_and_complete_report_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(task_run_plan, "_runtime_preview", lambda _repo: tmp_path / "runtime")
    repo = _repo(tmp_path)
    report = "full-report-line\n" * 70000
    executable = _codex(
        tmp_path,
        "python3 -c 'import sys; sys.stdout.write(\"full-report-line\\n\" * 70000)'",
        deliver=False,
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="long-report",
        require_change=None,
        report_only=True,
    )

    summary = payload["summary"]
    assert set(summary) == {
        "branch_head",
        "verdict",
        "decisions_needing_confirmation",
    }
    assert summary["branch_head"] == {
        "branch": payload["target_branch"],
        "head": payload["target_sha"],
    }
    assert summary["verdict"] == payload["result_kind"]
    assert len(payload["result_delivery"]["text"]) < 500
    assert json.loads(payload["result_delivery"]["text"]) == summary

    artifact = payload["result_delivery"]["full_report"]
    report_path = Path(artifact["path"])
    assert artifact["complete"] is True
    assert artifact["bytes"] == len(report.encode("utf-8"))
    assert report_path.read_text(encoding="utf-8") == report
    assert payload["status"] == "completed"


def test_task_result_links_the_v1_decision_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(task_run_plan, "_runtime_preview", lambda _repo: tmp_path / "runtime")
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "true")

    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="ledger-link",
        require_change=None,
        report_only=True,
    )

    link = payload["decision_ledger"]
    assert link == {
        "path": "charness-artifacts/task-run/decision-ledger.jsonl",
        "event_schema_version": 1,
        "exists": False,
    }


def test_decision_ledger_appends_unique_v1_events_and_returns_existing_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg-cache"))
    repo = _repo(tmp_path)
    event = {
        "schema_version": 1,
        "event_id": "decision-1",
        "occurred_at": "2026-09-24T12:00:00Z",
        "source": "decision-ledger",
        "event_kind": "contract-amendment",
        "facts": {"decision": "keep provider closeout authoritative"},
    }

    link = task_run_ledger.append_decision_event(repo, event)

    assert link == {
        "path": "charness-artifacts/task-run/decision-ledger.jsonl",
        "event_schema_version": 1,
        "exists": True,
    }
    ledger_path = repo / link["path"]
    assert ledger_path.read_text(encoding="utf-8") == json.dumps(
        event, ensure_ascii=False, separators=(",", ":")
    ) + "\n"
    assert task_run_ledger.read_decision_events(repo) == [event]
    with pytest.raises(ValueError, match="already exists"):
        task_run_ledger.append_decision_event(repo, event)


def test_persist_full_report_records_clipping_error(tmp_path: Path) -> None:
    delivery: dict[str, object] = {
        "text": "clipped-report",
        "bytes": 10**9,
        "truncated": True,
    }
    artifact = task_run_evidence._persist_full_report(
        delivery, tmp_path / "full-report.log"
    )

    assert artifact["complete"] is not True
    assert artifact["error"] == "source report was clipped before persistence"


def test_persist_full_report_reports_unwritable_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise(_self: object, _data: bytes) -> None:
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "write_bytes", _raise)
    artifact = task_run_evidence._persist_full_report(
        {"text": "report"}, tmp_path / "full-report.log"
    )

    assert artifact == {
        "path": str(tmp_path / "full-report.log"),
        "bytes": None,
        "complete": False,
        "error": "disk unavailable",
    }


def test_report_delivery_blockers_surface_unsaved_full_report() -> None:
    delivery: dict[str, object] = {
        "status": "delivered",
        "text": "report",
        "full_report": {"error": "disk unavailable"},
    }

    blockers = task_run_evidence._report_delivery_blockers(
        delivery, report_only=True
    )

    assert blockers == ["full report could not be saved: disk unavailable"]


def test_decision_ledger_rejects_foreign_source_events(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    foreign = dict(_decision_event("foreign-1"))
    foreign["source"] = "friction-log"
    foreign["event_kind"] = "block"

    with pytest.raises(task_run_events.EventSchemaError, match="only source="):
        task_run_ledger.append_decision_event(repo, foreign)


def test_decision_ledger_rejects_invalid_and_foreign_lines(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    path = repo / task_run_ledger.LEDGER_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    assert task_run_ledger.read_decision_events(repo) == []

    path.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid event at line 1"):
        task_run_ledger.append_decision_event(repo, _decision_event("x-1"))
    with pytest.raises(ValueError, match="invalid event at line 1"):
        task_run_ledger.read_decision_events(repo)

    foreign = dict(_decision_event("foreign-2"))
    foreign["source"] = "friction-log"
    foreign["event_kind"] = "block"
    path.write_text(
        json.dumps(foreign, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="foreign event at line 1"):
        task_run_ledger.append_decision_event(repo, _decision_event("x-2"))
    with pytest.raises(ValueError, match="foreign event at line 1"):
        task_run_ledger.read_decision_events(repo)
