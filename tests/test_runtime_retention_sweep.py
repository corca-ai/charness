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


def test_remove_tree_uses_zero_bytes_when_size_probe_fails(tmp_path, monkeypatch) -> None:
    candidate = _key(tmp_path) / "old-tree"
    candidate.mkdir()
    sweep = _sweep(tmp_path, dry_run=True)

    def _raise_oserror(_path: Path) -> int:
        raise OSError("size unavailable")

    monkeypatch.setattr(retention, "_tree_size_bytes", _raise_oserror)

    assert sweep._remove_tree(candidate, "expired") is True
    assert sweep.entries[-1]["action"] == "would-remove"
    assert sweep.entries[-1]["bytes"] == 0


def test_remove_tree_records_symlink_unlink_oserror(tmp_path: Path, monkeypatch) -> None:
    link = _key(tmp_path) / "old-link"
    target = link.parent / "target"
    target.write_text("keep target", encoding="utf-8")
    link.symlink_to(target)
    sweep = _sweep(tmp_path)
    original_unlink = Path.unlink

    def fail_link(path: Path, *args, **kwargs):
        if path == link:
            raise OSError("unlink denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_link)

    assert sweep._remove_tree(link, "expired") is False
    assert link.is_symlink()
    assert sweep.entries[-1]["action"] == "failed"
    assert "removal failed: unlink denied" in sweep.entries[-1]["reason"]


def test_sweep_lanes_uses_zero_finished_time_when_result_stat_fails(
    tmp_path: Path, monkeypatch
) -> None:
    key = _key(tmp_path)
    fallback_record = key / "task-run" / "fallback-time"
    newest_record = key / "task-run" / "newest"
    fallback_record.mkdir()
    newest_record.mkdir()
    fallback_result = fallback_record / "result.json"
    newest_result = newest_record / "result.json"
    payload = {"phase": "terminal", "status": "completed", "keep_worktree": True}
    for result in (fallback_result, newest_result):
        result.write_text(json.dumps(payload), encoding="utf-8")
    (fallback_record / "runtime").mkdir()
    newest_runtime = newest_record / "runtime"
    newest_runtime.mkdir()
    os.utime(newest_result, (2_000, 2_000))
    monkeypatch.setattr(retention, "KEPT_WORKTREE_LIMIT", 1)
    original_stat = Path.stat

    def fail_fallback_stat(path: Path, *args, **kwargs):
        if path == fallback_result:
            raise OSError("result stat unavailable")
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", fail_fallback_stat)

    sweep = _sweep(tmp_path)
    sweep.sweep_lanes()

    assert not (fallback_record / "runtime").exists()
    assert newest_runtime.is_dir()
    assert any(
        entry["path"] == str(fallback_record / "runtime")
        and "runtime expired with kept worktree" in entry["reason"]
        for entry in sweep.entries
    )
