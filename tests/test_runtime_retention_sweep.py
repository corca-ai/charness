"""Sweep-lane stale-exec tests: kept apart so the retention file stays under cap."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from scripts import runtime_bootstrap  # noqa: F401
from scripts.gates_support import runtime_root_retention as retention

_NOW = 1_800_000_000.0
_OLD = _NOW - 2 * 86400


def _key(tmp_path: Path) -> Path:
    """A `<base>/charness/runtime/<key>` tree `Sweep` accepts as a key root."""
    mine = tmp_path / "cache" / "charness" / "runtime" / "0000000000000001"
    (mine / "task-run").mkdir(parents=True, exist_ok=True)
    return mine


def _stale_record(tmp_path: Path, name: str = "lane-x") -> Path:
    record = _key(tmp_path) / "task-run" / name
    record.mkdir(parents=True, exist_ok=True)
    (record / "result.json").write_text(
        json.dumps({"runner_pid": 901, "phase": "exec", "status": "running"}),
        encoding="utf-8",
    )
    return record


def _age_old(path: Path) -> None:
    for entry in sorted(path.rglob("*")):
        os.utime(entry, (_OLD, _OLD))
    os.utime(path, (_OLD, _OLD))


def _sweep(tmp_path: Path, **kwargs) -> retention.Sweep:
    return retention.Sweep(_key(tmp_path), now=_NOW, **kwargs)


def _completed(stdout: str, returncode: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_sweep_reports_failed_stale_exec_entrypoint(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(retention, "run_process", lambda _c, **_k: _completed("", 1, "boom"))

    outcome = sweep._terminalize_stale_exec(record)

    assert outcome == {"transitioned": False, "reason": "entrypoint-failed"}
    assert any(entry["action"] == "failed" for entry in sweep.entries)


def test_sweep_reports_invalid_stale_exec_output(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(retention, "run_process", lambda _c, **_k: _completed("not json"))

    outcome = sweep._terminalize_stale_exec(record)

    assert outcome == {"transitioned": False, "reason": "invalid-entrypoint-output"}


def test_sweep_reports_malformed_entrypoint_output(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(
        retention, "run_process", lambda _c, **_k: _completed("{unclosed: 1")
    )

    outcome = sweep._terminalize_stale_exec(record)

    assert outcome == {"transitioned": False, "reason": "invalid-entrypoint-output"}
    assert any(entry["action"] == "failed" for entry in sweep.entries)


def test_sweep_records_terminalized_stale_exec(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    sweep = _sweep(tmp_path)
    stdout = json.dumps(
        {
            "transitioned": True,
            "log_entry": {
                "action": "terminalized",
                "reason": "r",
                "fields": {"status": "interrupted"},
            },
        }
    )
    monkeypatch.setattr(retention, "run_process", lambda _c, **_k: _completed(stdout))

    outcome = sweep._terminalize_stale_exec(record)

    assert outcome is not None and outcome["transitioned"] is True
    assert any(entry["action"] == "terminalized" for entry in sweep.entries)


def test_sweep_dry_run_marks_stale_exec_command(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    sweep = _sweep(tmp_path, dry_run=True)
    captured: dict = {}

    def _capture(command, **kwargs):
        captured["command"] = command
        return _completed(json.dumps({"transitioned": False}))

    monkeypatch.setattr(retention, "run_process", _capture)

    sweep._terminalize_stale_exec(record)

    assert "--dry-run" in captured["command"]


def test_sweep_lane_rereads_terminalized_records(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    (record / "runtime").mkdir()
    _age_old(record)
    sweep = _sweep(tmp_path)
    reads = iter(
        [
            {"phase": "exec", "runner_pid": 901, "status": "running"},
            {"phase": "terminal", "status": "completed"},
        ]
    )
    monkeypatch.setattr(sweep, "_lane_result", lambda _r: next(reads))
    monkeypatch.setattr(
        retention.Sweep,
        "_terminalize_stale_exec",
        lambda _s, _r: {"transitioned": False, "reason": "already-terminal"},
    )

    sweep.sweep_lane(record)

    assert not (record / "runtime").exists()
    assert any("finished lane (completed)" in e["reason"] for e in sweep.entries)


def test_sweep_lane_leaves_record_when_runner_not_confirmed_dead(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    (record / "runtime").mkdir()
    _age_old(record)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(
        retention.Sweep,
        "_terminalize_stale_exec",
        lambda _s, _r: {"transitioned": False, "reason": "runner-not-confirmed-dead"},
    )

    sweep.sweep_lane(record)

    assert (record / "runtime").exists()
    assert not any(e["action"] == "removed" for e in sweep.entries)


def test_sweep_lane_removes_idle_record_after_failed_terminalize(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    (record / "runtime").mkdir()
    _age_old(record)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(
        retention.Sweep,
        "_terminalize_stale_exec",
        lambda _s, _r: {"transitioned": False, "reason": "entrypoint-failed"},
    )

    sweep.sweep_lane(record)

    assert not (record / "runtime").exists()
    assert any("idle past the active window" in e["reason"] for e in sweep.entries)


def test_sweep_lane_ignores_artifact_free_idle_record(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    _age_old(record)
    sweep = _sweep(tmp_path)
    monkeypatch.setattr(
        retention.Sweep,
        "_terminalize_stale_exec",
        lambda _s, _r: {"transitioned": False, "reason": "entrypoint-failed"},
    )

    sweep.sweep_lane(record)

    assert (record / "result.json").exists()
    assert not any(e["action"] == "removed" for e in sweep.entries)


def test_sweep_lane_skips_fresh_nonterminal_records(tmp_path, monkeypatch) -> None:
    record = _stale_record(tmp_path)
    (record / "runtime").mkdir()
    now = _NOW
    os.utime(record / "result.json", (now, now))
    os.utime(record / "runtime", (now, now))
    os.utime(record, (now, now))
    sweep = _sweep(tmp_path)

    sweep.sweep_lane(record)

    assert (record / "runtime").exists()
    assert any("record is fresh" in e["reason"] for e in sweep.entries)
