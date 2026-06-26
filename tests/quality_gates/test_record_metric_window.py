from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from runtime_bootstrap import import_repo_module
from scripts import host_log_probe_lib

ROOT = Path(__file__).resolve().parents[2]
_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)
_record_metric_window = import_repo_module(
    ROOT / "skills" / "public" / "achieve" / "scripts" / "record_metric_window.py",
    "skills.public.achieve.scripts.record_metric_window",
)


def run_record_metric_window(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["record_metric_window.py", *args])
    try:
        returncode = _record_metric_window.main()
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def _goal_text(window: str = "") -> str:
    return (
        "# Achieve Goal: demo\n\nStatus: active\n\n"
        "## Final Verification\n\n" + (window + "\n\n" if window else "") + "All slices verified.\n\n"
        "## Auto-Retro\n\nNothing surfaced.\n"
    )


def test_record_metric_window_inserts_under_final_verification() -> None:
    updated = gal.record_metric_window(
        _goal_text(),
        started_at="2026-06-03T00:00:00Z",
        completed_at="2026-06-03T03:42:00Z",
        codex_session_file="charness-artifacts/rollout.jsonl",
    )
    assert "## Final Verification\n\nHost metric window: started_at=2026-06-03T00:00:00Z" in updated
    assert "completed_at=2026-06-03T03:42:00Z" in updated
    assert "All slices verified." in updated  # existing body preserved
    assert "## Auto-Retro" in updated


def test_record_metric_window_is_idempotent_and_replaces_in_place() -> None:
    once = gal.record_metric_window(
        _goal_text(),
        started_at="2026-06-03T00:00:00Z",
        completed_at="2026-06-03T03:42:00Z",
        codex_session_file="r.jsonl",
    )
    twice = gal.record_metric_window(
        once,
        started_at="2026-06-03T00:00:00Z",
        completed_at="2026-06-03T03:42:00Z",
        codex_session_file="r.jsonl",
    )
    assert once == twice  # identical inputs -> identical text

    replaced = gal.record_metric_window(
        once,
        started_at="2026-06-03T01:00:00Z",
        completed_at="2026-06-03T04:00:00Z",
        codex_session_file="r.jsonl",
    )
    assert replaced.count("Host metric window:") == 1  # replaced, not stacked
    assert "started_at=2026-06-03T01:00:00Z" in replaced


def test_record_metric_window_rejects_empty_fields() -> None:
    with pytest.raises(ValueError):
        gal.record_metric_window(
            _goal_text(),
            started_at="2026-06-03T00:00:00Z",
            completed_at="",
            codex_session_file="r.jsonl",
        )


def test_record_metric_window_requires_final_verification_section() -> None:
    with pytest.raises(ValueError):
        gal.record_metric_window(
            "# Goal\n\nStatus: active\n\nNo final verification heading here.\n",
            started_at="2026-06-03T00:00:00Z",
            completed_at="2026-06-03T03:42:00Z",
            codex_session_file="r.jsonl",
        )


def test_recorded_window_is_read_as_parsed_by_the_probe(tmp_path: Path) -> None:
    # End-to-end: recording the line flips the probe from `absent` to `parsed`.
    session_file = tmp_path / "rollout.jsonl"
    session_file.write_text('{"timestamp":"2026-06-03T01:00:00Z","type":"event_msg"}\n', encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(_goal_text(), encoding="utf-8")

    before = host_log_probe_lib.parse_goal_metric_window(tmp_path, Path("goal.md"))
    assert before["status"] == "absent"

    goal.write_text(
        gal.record_metric_window(
            goal.read_text(encoding="utf-8"),
            started_at="2026-06-03T00:00:00Z",
            completed_at="2026-06-03T03:42:00Z",
            codex_session_file=str(session_file),
        ),
        encoding="utf-8",
    )
    after = host_log_probe_lib.parse_goal_metric_window(tmp_path, Path("goal.md"))
    assert after["status"] == "parsed"
    assert after["codex_session_file"] == str(session_file)


def test_metric_window_attention_classifies_recorded_incomplete_absent() -> None:
    recorded = gal.record_metric_window(
        _goal_text(),
        started_at="2026-06-03T00:00:00Z",
        completed_at="2026-06-03T03:42:00Z",
        codex_session_file="r.jsonl",
    )
    assert gal.metric_window_attention(recorded)["status"] == "recorded"
    assert gal.metric_window_attention(_goal_text())["status"] == "absent"
    incomplete = _goal_text(window="Host metric window: started_at=2026-06-03T00:00:00Z")
    assert gal.metric_window_attention(incomplete)["status"] == "incomplete"


def test_absent_window_is_surfaced_at_closeout_but_never_gates_the_flip(tmp_path: Path) -> None:
    # The recurrence #282 reported was a silent absent window. The closeout must
    # SURFACE it without blocking, because a host lacking timestamps legitimately
    # records `unavailable`. Differential check: adding the window line changes
    # only the attention signal, never report["ok"].
    without_window = _goal_text()
    with_window = gal.record_metric_window(
        without_window,
        started_at="2026-06-03T00:00:00Z",
        completed_at="2026-06-03T03:42:00Z",
        codex_session_file="r.jsonl",
    )
    report_absent = gal.check_complete_evidence(tmp_path, without_window)
    report_recorded = gal.check_complete_evidence(tmp_path, with_window)

    assert report_absent["metric_window"]["status"] == "absent"
    assert report_recorded["metric_window"]["status"] == "recorded"
    # the window signal is non-blocking: it does not change the gate verdict
    assert report_absent["ok"] == report_recorded["ok"]


def test_record_metric_window_cli_updates_artifact(tmp_path: Path, monkeypatch, capsys) -> None:
    session_file = tmp_path / "rollout.jsonl"
    session_file.write_text("{}\n", encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(_goal_text(), encoding="utf-8")

    result = run_record_metric_window(
        monkeypatch,
        capsys,
        "--goal-path",
        str(goal),
        "--started-at",
        "2026-06-03T00:00:00Z",
        "--completed-at",
        "2026-06-03T03:42:00Z",
        "--codex-session-file",
        str(session_file),
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["action"] == "updated"
    assert "Host metric window:" in goal.read_text(encoding="utf-8")


def test_record_metric_window_accepts_claude_session_source(tmp_path, monkeypatch, capsys) -> None:
    session = tmp_path / "claude-session.jsonl"
    session.write_text("{}\n", encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(_goal_text(), encoding="utf-8")

    result = run_record_metric_window(
        monkeypatch,
        capsys,
        "--goal-path",
        str(goal),
        "--started-at",
        "2026-06-10T08:50:14Z",
        "--completed-at",
        "2026-06-10T12:50:14Z",
        "--claude-session-file",
        str(session),
    )
    assert result.returncode == 0, result.stderr
    text = goal.read_text(encoding="utf-8")
    assert f"claude_session_file={session}" in text
    assert "codex_session_file=" not in text
    assert gal.metric_window_attention(text)["status"] == "recorded"


def test_record_metric_window_rejects_both_session_sources(tmp_path, monkeypatch, capsys) -> None:
    goal = tmp_path / "goal.md"
    goal.write_text(_goal_text(), encoding="utf-8")

    result = run_record_metric_window(
        monkeypatch,
        capsys,
        "--goal-path",
        str(goal),
        "--started-at",
        "2026-06-10T08:50:14Z",
        "--completed-at",
        "2026-06-10T12:50:14Z",
        "--codex-session-file",
        "a.jsonl",
        "--claude-session-file",
        "b.jsonl",
    )
    assert result.returncode != 0
    assert "not allowed with" in result.stderr


def test_record_metric_window_rejects_missing_session_source(tmp_path, monkeypatch, capsys) -> None:
    goal = tmp_path / "goal.md"
    goal.write_text(_goal_text(), encoding="utf-8")

    result = run_record_metric_window(
        monkeypatch,
        capsys,
        "--goal-path",
        str(goal),
        "--started-at",
        "2026-06-10T08:50:14Z",
        "--completed-at",
        "2026-06-10T12:50:14Z",
    )
    assert result.returncode != 0
    assert "is required" in result.stderr


def test_render_metric_window_line_requires_exactly_one_session_source() -> None:
    import pytest

    with pytest.raises(ValueError, match="exactly one"):
        gal.render_metric_window_line(
            started_at="2026-06-10T08:50:14Z",
            completed_at="2026-06-10T12:50:14Z",
        )
    with pytest.raises(ValueError, match="exactly one"):
        gal.render_metric_window_line(
            started_at="2026-06-10T08:50:14Z",
            completed_at="2026-06-10T12:50:14Z",
            codex_session_file="a.jsonl",
            claude_session_file="b.jsonl",
        )


def test_metric_window_attention_flags_dual_host_line_as_incomplete() -> None:
    dual = (
        "## Final Verification\n\nHost metric window: started_at=2026-06-10T08:00:00Z "
        "completed_at=2026-06-10T09:00:00Z codex_session_file=a.jsonl claude_session_file=b.jsonl\n"
    )
    attention = gal.metric_window_attention(dual)
    assert attention["status"] == "incomplete"
    assert "more than one session-file key" in attention["note"]
