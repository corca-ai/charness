"""Fixed-shape periodic status report: seeded stores render measured sections (#872)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.task_run import (
    task_run_friction,
    task_run_ledger,
    task_run_runtime,
    task_run_status_report,
    task_run_train_stats,
)


def _stamp(minutes_ago: float = 5) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()


def _seed(repo: Path) -> Path:
    runtime = task_run_runtime.task_runtime_root(repo)
    results = {
        "lane-a": {"status": "done", "branch": "lane-a", "result_kind": "completed"},
        "lane-b": {
            "status": "failed",
            "branch": "lane-b",
            "blocker": "boom",
            "result_kind": "completed",
        },
        "lane-c": {"status": "running", "branch": "lane-c"},
    }
    import os
    from datetime import datetime as _datetime

    done_at = _datetime.fromisoformat(_stamp(10).replace("Z", "+00:00")).timestamp()
    for task_id, record in results.items():
        path = task_run_runtime.task_result_path(runtime, task_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"task_id": task_id, **record}), encoding="utf-8")
        # Lane-a landed after its result; backdate mtimes so the done time
        # (mtime) precedes the landing records below.
        os.utime(path, (done_at, done_at))
    for index in range(2):
        task_run_train_stats.record_landing_for_repo(
            repo,
            base_sha="0" * 40,
            landed_sha=f"{index}" * 40,
            branches=["lane-a"],
            run_id=f"run-{index}",
            occurred_at=_stamp(4 - index),
        )
    task_run_friction.append_friction_event(
        runtime,
        "block",
        task_id="lane-b",
        facts={"blocker": "boom", "next_step": "retry lane-b"},
        occurred_at=_stamp(3),
    )
    task_run_friction.append_friction_event(
        runtime,
        "block",
        task_id="lane-c",
        facts={"blocker": "same boom"},
        occurred_at=_stamp(2),
    )
    task_run_friction.append_friction_event(
        runtime, "relaunch", task_id="lane-b", occurred_at=_stamp(1)
    )
    task_run_ledger.append_decision_event(
        repo,
        {
            "schema_version": 1,
            "event_id": "decision-1",
            "occurred_at": _stamp(2),
            "source": "decision-ledger",
            "event_kind": "contract-amendment",
            "facts": {"decision": "cap parallel lanes at two"},
        },
    )
    return runtime


def test_period_report_renders_every_section_measured(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    runtime = _seed(repo)

    report = task_run_status_report.render_period_status(
        runtime_path=runtime, repo_root=repo, window_hours=0.5
    )

    for heading in (
        "## Goals",
        "## Lane states",
        "## Friction",
        "## Improvements",
        "## Decisions",
        "## Next actions",
    ):
        assert heading in report
    assert "3 goal(s): 1 done, 1 failed, 1 running." in report
    assert "| lane-b | failed | lane-b | boom |" in report
    assert "3 friction event(s): 2 block, 1 relaunch; 1 repeated, 2 blocking." in report
    assert (
        "train: 2 landings in window (4.00/h; previous window 0 landings, 0.00/h); "
        "median queue wait 6.0m; waste 1/3 (33%)."
    ) in report
    assert "improvements found: cap parallel lanes at two." in report
    assert "contract-amendment" in report
    assert "needs the operator: none." in report
    assert "| retry lane-b | blocked | boom | lane-b |" in report
    assert "| land lane-b | waiting-for-landing | fast-forward on main | integrator |" in report
    assert "| finish lane-c | in-progress | terminal result | lane-c |" in report


def test_period_report_empty_state_has_fixed_line(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    runtime = task_run_runtime.task_runtime_root(repo)

    report = task_run_status_report.render_period_status(
        runtime_path=runtime, repo_root=repo, window_hours=0.5
    )

    assert "0 goal(s): no lanes recorded." in report
    assert "0 friction event(s): none; 0 repeated, 0 blocking." in report
    assert (
        "train: 0 landings in window (0.00/h; previous window 0 landings, 0.00/h); "
        "median queue wait n/a; waste 0/0 (n/a)."
    ) in report
    assert "improvements found: none." in report
    assert "| - | idle | no blocked, waiting, or running lanes | - |" in report


def test_period_report_rejects_non_positive_window(tmp_path: Path) -> None:
    import pytest

    with pytest.raises(ValueError, match="window_hours must be positive"):
        task_run_status_report.render_period_status(
            runtime_path=tmp_path, repo_root=tmp_path, window_hours=0
        )


def test_task_report_command_prints_markdown(tmp_path: Path, capsys) -> None:
    from tests.charness_cli.support import CLI, load_cli_module

    repo = tmp_path / "repo"
    repo.mkdir()
    _seed(repo)

    cli = load_cli_module("charness_task_report_cli", CLI)
    code = cli.cmd_task_report(
        argparse.Namespace(repo_root=repo, window="30m"),
    )

    assert code == 0
    out = capsys.readouterr().out
    assert out.startswith("# Period status: last 0.5h")
    assert "improvements found:" in out
