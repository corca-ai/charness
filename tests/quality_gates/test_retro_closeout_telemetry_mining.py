"""Weekly closeout-telemetry mining (spec achieve-efficiency-improvements, E2a).

The weekly retro mines the local closeout-telemetry stream and routes RECURRING
waste to a filed issue — NOT the decaying recent-lessons digest (critique R1b).
The fixture asserts recurring waste is named AND dispositioned to the issue
branch; a digest-only disposition fails the test. The cross-repo non-claim must
appear in the output (mines this repo's stream only).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT, run_script

MINER_PATH = ROOT / "skills" / "public" / "retro" / "scripts" / "mine_closeout_telemetry.py"


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
        json.dumps({"event_type": "usage_episode", "outcome_status": "delivered"}),
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


def test_cli_over_seeded_stream(tmp_path: Path) -> None:
    stream = tmp_path / ".charness" / "usage-episodes" / "closeout_telemetry.jsonl"
    stream.parent.mkdir(parents=True, exist_ok=True)
    stream.write_text("\n".join(_gate_record("pytest -q", 200.0) for _ in range(3)) + "\n", encoding="utf-8")
    completed = run_script(str(MINER_PATH), "--repo-root", str(tmp_path))
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    gate = next(f for f in result["findings"] if f["kind"] == "gate_runtime")
    assert gate["disposition"] == "file-issue"
    assert gate["marker"] == "recurs:"
    assert result["stream_path"].endswith("closeout_telemetry.jsonl")
