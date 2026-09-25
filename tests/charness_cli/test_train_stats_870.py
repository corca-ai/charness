"""Merge-train throughput stats: landings, queue wait, waste (#870)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.task_run import task_run_train_stats as stats
from scripts.task_run.task_run_runtime import task_runtime_root
from scripts.task_run.task_run_train_core import validate_verify_profile

NOW = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone.utc)


def _runtime(tmp_path: Path) -> Path:
    return task_runtime_root(tmp_path)


def _seed_result(runtime: Path, task_id: str, branch: str, status: str, done_iso: str) -> None:
    path = runtime / "task-run" / task_id / "result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "branch": branch,
                "status": status,
                "phase": "terminal",
            }
        ),
        encoding="utf-8",
    )
    epoch = datetime.fromisoformat(done_iso.replace("Z", "+00:00")).timestamp()
    os.utime(path, (epoch, epoch))


def _seed_landing(
    runtime: Path,
    occurred_at: str,
    branches: list[str],
    landed_sha: str = "abc123",
) -> None:
    path = runtime / "train" / "landings.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "schema_version": stats.LANDING_SCHEMA,
                    "occurred_at": occurred_at,
                    "base_sha": "base000",
                    "landed_sha": landed_sha,
                    "branches": branches,
                    "run_id": "run-1",
                }
            )
            + "\n"
        )


def _seed_standard(runtime: Path) -> None:
    _seed_landing(runtime, "2026-09-25T10:00:00Z", ["lane-a", "lane-b"])
    _seed_landing(runtime, "2026-09-25T11:00:00Z", ["lane-c"])
    _seed_result(runtime, "lane-a", "lane-a", "completed", "2026-09-25T09:30:00Z")
    _seed_result(runtime, "lane-b", "lane-b", "completed", "2026-09-25T09:45:00Z")
    _seed_result(runtime, "lane-c", "lane-c", "failed", "2026-09-25T10:30:00Z")
    _seed_result(runtime, "lane-d", "lane-d", "completed", "2026-09-25T10:00:00Z")


def test_stats_derives_rate_median_waste_and_waiting(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    _seed_standard(runtime)

    payload = stats.train_stats_for_repo(tmp_path, window_hours=3.0, now=NOW)

    assert payload["lands_in_window"] == 2
    assert payload["landings_per_hour"] == pytest.approx(2 / 3)
    assert payload["median_queue_wait_minutes"] == pytest.approx(30.0)
    assert payload["lanes_joined"] == 3
    assert payload["lanes_waiting"] == ["lane-d"]
    assert payload["launched"] == 4
    assert payload["wasted"] == 1
    assert payload["waste_rate"] == pytest.approx(0.25)
    assert payload["loosening"] is None


def test_stats_counts_missing_status_as_waste(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    _seed_result(runtime, "lane-x", "lane-x", "", "2026-09-25T10:00:00Z")

    payload = stats.train_stats_for_repo(tmp_path, window_hours=3.0, now=NOW)

    assert payload["launched"] == 1
    assert payload["wasted"] == 1
    assert payload["waste_rate"] == pytest.approx(1.0)
    assert payload["lanes_waiting"] == ["lane-x"]


def test_stats_matches_refs_prefixed_branches(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    _seed_landing(runtime, "2026-09-25T10:00:00Z", ["refs/heads/lane-a"])
    _seed_result(runtime, "lane-a", "lane-a", "completed", "2026-09-25T09:30:00Z")

    payload = stats.train_stats_for_repo(tmp_path, window_hours=3.0, now=NOW)

    assert payload["lanes_joined"] == 1
    assert payload["lanes_waiting"] == []


def test_stats_skips_malformed_landing_lines(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    _seed_landing(runtime, "2026-09-25T10:00:00Z", ["lane-a"])
    path = runtime / "train" / "landings.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write("not json\n")

    assert len(stats.read_landings(runtime)) == 1


def test_stats_empty_runtime_reports_zeros(tmp_path: Path) -> None:
    payload = stats.train_stats_for_repo(tmp_path, window_hours=3.0, now=NOW)

    assert payload["lands_in_window"] == 0
    assert payload["landings_per_hour"] == 0.0
    assert payload["median_queue_wait_minutes"] is None
    assert payload["waste_rate"] == 0.0
    with pytest.raises(ValueError, match="positive"):
        stats.train_stats_for_repo(tmp_path, window_hours=0.0, now=NOW)


def test_record_landing_appends_and_reads_back(tmp_path: Path) -> None:
    record = stats.record_landing_for_repo(
        tmp_path,
        base_sha="base000",
        landed_sha="abc123",
        branches=["lane-a"],
        run_id="run-9",
        occurred_at="2026-09-25T10:00:00Z",
    )

    assert record is not None and record["landed_sha"] == "abc123"
    assert len(stats.read_landings(_runtime(tmp_path))) == 1


def test_parse_window_shapes() -> None:
    assert stats.parse_window("30m") == pytest.approx(0.5)
    assert stats.parse_window("3h") == pytest.approx(3.0)
    assert stats.parse_window("1d") == pytest.approx(24.0)
    assert stats.parse_window("2") == pytest.approx(2.0)
    for bad in ("", "0h", "-3h", "soon", "3x"):
        with pytest.raises(ValueError):
            stats.parse_window(bad)


def test_loosening_threshold_ok_and_reasons(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    _seed_standard(runtime)
    payload = stats.train_stats_for_repo(tmp_path, window_hours=3.0, now=NOW)

    strict = {
        "min_lands": 2,
        "min_landings_per_hour": 0.5,
        "max_queue_wait_minutes": 60.0,
        "require_no_waste": True,
    }
    refused = stats.evaluate_loosening(payload, strict)
    assert refused["ok"] is False
    assert any("wasted" in reason for reason in refused["reasons"])

    relaxed = dict(strict, require_no_waste=False)
    assert stats.evaluate_loosening(payload, relaxed) == {"ok": True, "reasons": []}

    starved = dict(relaxed, min_lands=9)
    assert stats.evaluate_loosening(payload, starved)["ok"] is False


def test_profile_accepts_and_rejects_loosening() -> None:
    good = {
        "version": 1,
        "commands": [{"id": "c", "argv": ["x"]}],
        "loosening": {
            "min_lands": 4,
            "min_landings_per_hour": 3.0,
            "max_queue_wait_minutes": 30.0,
            "require_no_waste": True,
        },
    }
    assert validate_verify_profile(good) == []
    bad = {
        "version": 1,
        "commands": [{"id": "c", "argv": ["x"]}],
        "loosening": {"min_lands": -1, "bogus": True, "require_no_waste": "yes"},
    }
    errors = validate_verify_profile(bad)
    assert any("must not be negative" in error for error in errors)
    assert any("unknown keys" in error for error in errors)
    assert any("must be a boolean" in error for error in errors)


def test_train_stats_cli_reports_payload(tmp_path: Path, monkeypatch) -> None:
    import argparse

    from tests.charness_cli.support import CLI, load_cli_module

    runtime = _runtime(tmp_path)
    # The CLI reads the wall clock, so fixed seeds rot out of the trailing
    # window as the day advances: seed relative to now to stay deterministic.
    moment = datetime.now(timezone.utc).replace(microsecond=0)
    _seed_landing(
        runtime,
        (moment - timedelta(hours=2)).isoformat().replace("+00:00", "Z"),
        ["lane-a"],
    )
    _seed_landing(
        runtime,
        (moment - timedelta(minutes=30)).isoformat().replace("+00:00", "Z"),
        ["lane-b"],
    )
    cli = load_cli_module("charness_train_stats_cli", CLI)
    # Payloads live in scripts/cli after #873: patch the feature namespace
    # the shim dispatches to, not the root entry.
    import scripts.cli.cmd_train as train_payload
    import scripts.task_run.task_run_train as train_lib

    monkeypatch.setattr(train_payload, "_load_train_lib", lambda _args: train_lib)
    monkeypatch.setattr(train_payload, "_resolve_worktree_target", lambda _args: tmp_path)
    emitted: list[dict] = []
    monkeypatch.setattr(train_payload, "emit_yaml", emitted.append)

    code = cli.cmd_train(
        argparse.Namespace(stats=True, branches=[], window="3h", repo_root=tmp_path, profile=None)
    )

    assert code == 0
    assert emitted[-1]["lands_in_window"] == 2


def test_train_cli_refuses_branches_with_stats_and_empty_queue() -> None:
    import argparse

    from scripts.cli.bootstrap import CharnessError
    from tests.charness_cli.support import CLI, load_cli_module

    # Guards live in scripts/cli/cmd_train.py after #873, so they raise the
    # tree error class, not the entry fallback copy.
    cli = load_cli_module("charness_train_guards_cli", CLI)
    with pytest.raises(CharnessError, match="takes no branches"):
        cli.cmd_train(argparse.Namespace(stats=True, branches=["lane-a"], repo_root=Path(".")))
    with pytest.raises(CharnessError, match="at least one branch"):
        cli.cmd_train(argparse.Namespace(stats=False, branches=[], repo_root=Path(".")))
