"""Weekly closeout-telemetry mining (spec achieve-efficiency-improvements, E2a).

The retro mines the local closeout-telemetry stream and routes RECURRING
waste to a filed issue — NOT the decaying recent-lessons digest (critique R1b).
The fixture asserts recurring waste is named AND dispositioned to the issue
branch; a digest-only disposition fails the test. The cross-repo non-claim must
appear in the output (mines this repo's stream only).
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import yaml

from .support import ROOT, run_script

MINER_PATH = ROOT / "skills" / "public" / "retro" / "scripts" / "mine_closeout_telemetry.py"
PLUGIN_MINER_PATH = ROOT / "plugins" / "charness" / "skills" / "retro" / "scripts" / "mine_closeout_telemetry.py"


def _load_miner():
    spec = importlib.util.spec_from_file_location("mine_closeout_telemetry_under_test", MINER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gate_record(command: str, elapsed: float, over: bool = False) -> str:
    return json.dumps(
        {
            "event_type": "closeout_telemetry",
            "gate_runtime": {
                "budget_seconds": 120.0,
                "over_budget": [
                    {"phase": "verify", "command": command, "elapsed_seconds": elapsed,
                     "budget_seconds": 120.0, "over_budget": True}
                ],
            },
            "over_slice": {"trailing_artifact_only_run": 4 if over else 0, "threshold": 3, "over": over},
            "slice_churn": {"base": "origin/main", "commits": 1, "artifact_only_commits": 0, "artifact_only_ratio": 0.0},
        }
    )


def _detail_gate_record(status: str, timestamp: str, command: str, elapsed: object, over: bool = False) -> str:
    record = json.loads(_gate_record(command, elapsed, over=over))
    record.update({"schema_version": 1, "status": status, "timestamp": timestamp})
    return json.dumps(record)


def test_recurring_gate_routes_to_filed_issue_not_digest() -> None:
    miner = _load_miner()
    lines = [_gate_record("pytest -q", 200.0) for _ in range(3)]
    result = miner.mine(lines, recur_min=2)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    # Recurring waste is named and routes to a filed issue.
    assert gate["recurring"] is True
    assert gate["marker"] == "recurs:"
    assert gate["disposition"] == "file-issue"
    assert gate["occurrences"] == 3
    # R1b teeth: never the decaying digest.
    assert gate["disposition"] != "recent-lessons"
    assert "file issue" in result["disposition_summary"]
    assert "digest" in result["disposition_summary"]


def test_one_off_gate_is_watch_not_issue() -> None:
    miner = _load_miner()
    result = miner.mine([_gate_record("ruff check", 130.0)], recur_min=2)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["recurring"] is False
    assert gate["disposition"] == "watch"
    assert gate["marker"] == ""
    assert result["recurring_count"] == 0


def test_over_slice_recurrence_routes_to_issue() -> None:
    miner = _load_miner()
    lines = [_gate_record("pytest", 50.0, over=True) for _ in range(2)]
    result = miner.mine(lines, recur_min=2)
    over_slice = next(f for f in result["findings"] if f["kind"] == "over_slice")
    assert over_slice["recurring"] is True
    assert over_slice["disposition"] == "file-issue"
    assert over_slice["occurrences"] == 2


def test_recur_min_floor_is_two() -> None:
    miner = _load_miner()
    # recur_min < 2 is clamped to 2: a single occurrence is never "recurring".
    result = miner.mine([_gate_record("pytest", 200.0)], recur_min=1)
    assert result["recur_min"] == 2
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["recurring"] is False


def test_malformed_and_foreign_lines_ignored() -> None:
    miner = _load_miner()
    lines = [
        "not json",
        "",
        json.dumps({"event_type": "other_record", "outcome_status": "delivered"}),
        _gate_record("pytest", 200.0),
        _gate_record("pytest", 210.0),
    ]
    result = miner.mine(lines, recur_min=2)
    assert result["records_examined"] == 2  # only the two closeout_telemetry records
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["recurring"] is True


def test_cross_repo_non_claim_present() -> None:
    miner = _load_miner()
    result = miner.mine([], recur_min=2)
    assert "this repo's local" in result["cross_repo_claim"]
    assert result["records_examined"] == 0
    assert result["recurring_count"] == 0


def test_non_numeric_elapsed_seconds_is_tolerated() -> None:
    # float("slow") raises -> the except guard keeps aggregating (count still increments).
    miner = _load_miner()
    rec = json.dumps(
        {
            "event_type": "closeout_telemetry",
            "gate_runtime": {
                "budget_seconds": 120.0,
                "over_budget": [
                    {"phase": "verify", "command": "pytest", "elapsed_seconds": "slow", "over_budget": True}
                ],
            },
            "over_slice": {"over": False, "threshold": 3, "trailing_artifact_only_run": 0},
            "slice_churn": {},
        }
    )
    result = miner.mine([rec, rec], recur_min=2)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["occurrences"] == 2
    assert gate["peak_elapsed_seconds"] is None  # no numeric seconds were collected


def test_default_miner_preserves_nonfinite_elapsed_behavior() -> None:
    miner = _load_miner()
    record = json.loads(_detail_gate_record("completed", "2026-06-13T01:00:00Z", "pytest -q", "Infinity"))
    result = miner.mine([json.dumps(record)])
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert math.isinf(gate["peak_elapsed_seconds"])


def test_read_lines_missing_stream_returns_empty(tmp_path: Path) -> None:
    # A repo with no telemetry stream degrades to [] (OSError guard), never raises.
    miner = _load_miner()
    assert miner._read_lines(tmp_path, miner.DEFAULT_STREAM_PATH) == []


def test_detail_read_lines_unreadable_stream_is_typed(monkeypatch, tmp_path: Path) -> None:
    miner = _load_miner()

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("fixture unreadable")

    monkeypatch.setattr(Path, "read_text", raise_permission_error)
    assert miner._read_lines_for_detail(tmp_path, miner.DEFAULT_STREAM_PATH) == ([], "unreadable")


def test_cli_over_seeded_stream(tmp_path: Path) -> None:
    stream = tmp_path / ".charness" / "closeout-telemetry" / "records.jsonl"
    stream.parent.mkdir(parents=True, exist_ok=True)
    stream.write_text("\n".join(_gate_record("pytest -q", 200.0) for _ in range(3)) + "\n", encoding="utf-8")
    completed = run_script(str(MINER_PATH), "--repo-root", str(tmp_path))
    assert completed.returncode == 0, completed.stderr
    result = yaml.safe_load(completed.stdout)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["disposition"] == "file-issue"
    assert gate["marker"] == "recurs:"
    assert result["stream_path"].endswith("records.jsonl")
    assert "detail" not in result


def test_detail_cli_audits_population_and_summarizes_entries(tmp_path: Path) -> None:
    stream = tmp_path / ".charness" / "closeout-telemetry" / "records.jsonl"
    stream.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "",
        "not json",
        json.dumps(["not", "a", "record"]),
        json.dumps({"event_type": "other_record"}),
        json.dumps({"event_type": "closeout_telemetry", "schema_version": 2}),
        _detail_gate_record("completed", "2026-06-13T01:00:00Z", "pytest -q", 200.0),
        _detail_gate_record("failed", "2026-06-13T02:00:00Z", "pytest -q", 220.0),
        _detail_gate_record("blocked", "2026-06-13T03:00:00Z", "pytest -q", "NaN", over=True),
    ]
    stream.write_text("\n".join(lines) + "\n", encoding="utf-8")
    completed = run_script(str(MINER_PATH), "--repo-root", str(tmp_path), "--detail")
    assert completed.returncode == 0, completed.stderr
    result = yaml.safe_load(completed.stdout)
    detail = result["detail"]
    population = detail["population"]
    assert detail["stream_read"] == {"status": "present"}
    assert population["physical_lines"] == 8
    assert population["blank_lines"] == 1
    assert population["malformed_lines"] == 2
    assert population["foreign_event_lines"] == 1
    assert population["unsupported_schema_lines"] == 1
    assert population["retained_records"] == 3
    assert population["window_start"] == "2026-06-13T01:00:00Z"
    assert population["window_end"] == "2026-06-13T03:00:00Z"
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    receipt = gate["detail"]
    assert receipt["matching_records"] == 3
    assert receipt["matching_entries"] == 3
    assert receipt["record_status_counts"] == {"blocked": 1, "completed": 1, "failed": 1}
    assert receipt["elapsed_seconds"] == {
        "numeric_observations": 2,
        "excluded_elapsed_values": 1,
        "total_seconds": 420.0,
        "mean_seconds": 210.0,
        "median_seconds": 210.0,
        "min_seconds": 200.0,
        "max_seconds": 220.0,
        "budget_seconds": 120.0,
        "budget_seconds_values": [120.0],
        "paired_observations": 2,
        "excess_seconds": None,
    }
    assert "suite pass/fail" in detail["non_claims"][0]
    assert "over_slice" in detail["unit_separation"]


def test_detail_missing_stream_is_not_an_empty_clean_result(tmp_path: Path) -> None:
    completed = run_script(str(MINER_PATH), "--repo-root", str(tmp_path), "--detail")
    assert completed.returncode == 0, completed.stderr
    result = yaml.safe_load(completed.stdout)
    assert result["detail"]["stream_read"] == {"status": "missing"}
    assert result["detail"]["population"]["retained_records"] == 0
    assert result["detail"]["population"]["scope"].endswith("unknown")


def test_detail_recur_min_uses_only_retained_schema_records(tmp_path: Path) -> None:
    stream = tmp_path / ".charness" / "closeout-telemetry" / "records.jsonl"
    stream.parent.mkdir(parents=True, exist_ok=True)
    unsupported = json.loads(_detail_gate_record("completed", "2026-06-13T00:00:00Z", "pytest -q", 200.0))
    unsupported["schema_version"] = 2
    lines = [
        json.dumps(unsupported),
        _detail_gate_record("completed", "2026-06-13T01:00:00Z", "pytest -q", 200.0),
        _detail_gate_record("completed", "2026-06-13T02:00:00Z", "pytest -q", 200.0),
    ]
    stream.write_text("\n".join(lines) + "\n", encoding="utf-8")
    completed = run_script(
        str(MINER_PATH), "--repo-root", str(tmp_path), "--detail", "--recur-min", "3"
    )
    assert completed.returncode == 0, completed.stderr
    result = yaml.safe_load(completed.stdout)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert result["recur_min"] == 3
    assert gate["occurrences"] == 2
    assert gate["recurring"] is False
    assert result["detail"]["population"]["unsupported_schema_lines"] == 1


def test_detail_counts_parent_status_once_for_multiple_matching_entries() -> None:
    miner = _load_miner()
    record = json.loads(_detail_gate_record("failed", "2026-06-13T01:00:00Z", "pytest -q", 200.0))
    record["gate_runtime"]["over_budget"].append(
        {"phase": "verify", "command": "pytest -q", "elapsed_seconds": 220.0,
         "budget_seconds": 120.0, "over_budget": True}
    )
    result = miner.mine_detailed([json.dumps(record)])
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    receipt = gate["detail"]
    assert receipt["matching_records"] == 1
    assert receipt["matching_entries"] == 2
    assert receipt["record_status_counts"] == {"failed": 1}
    assert receipt["elapsed_seconds"]["paired_observations"] == 2
    assert receipt["elapsed_seconds"]["excess_seconds"] == 180.0


def test_detail_rejects_nonfinite_peak_and_preserves_elapsed_budget_pairing() -> None:
    miner = _load_miner()
    record = json.loads(_detail_gate_record("completed", "2026-06-13T01:00:00Z", "pytest -q", "Infinity"))
    record["gate_runtime"]["over_budget"].extend(
        [
            {"phase": "verify", "command": "pytest -q", "elapsed_seconds": 200.0,
             "over_budget": True},
            {"phase": "verify", "command": "pytest -q", "elapsed_seconds": 220.0,
             "budget_seconds": 120.0, "over_budget": True},
        ]
    )
    result = miner.mine_detailed([json.dumps(record)])
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    receipt = gate["detail"]["elapsed_seconds"]
    assert gate["peak_elapsed_seconds"] == 220.0
    assert receipt["numeric_observations"] == 2
    assert receipt["excluded_elapsed_values"] == 1
    assert receipt["paired_observations"] == 1
    assert receipt["budget_seconds_values"] == [120.0]
    assert receipt["excess_seconds"] is None


def test_source_and_plugin_miner_mirrors_are_identical() -> None:
    assert MINER_PATH.read_bytes() == PLUGIN_MINER_PATH.read_bytes()
