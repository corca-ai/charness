from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .support import run_script

AUDIT_SCRIPT = "skills/public/retro/scripts/audit_codex_session.py"


def write_sqlite(home: Path) -> Path:
    path = home / ".codex" / "logs_2.sqlite"
    path.parent.mkdir(parents=True)
    connection = sqlite3.connect(path)
    connection.execute(
        "create table logs(id integer, ts integer, ts_nanos integer, feedback_log_body text, estimated_bytes integer, thread_id text)"
    )
    rows = [
        (
            1,
            1770000000,
            0,
            "event.kind=response.completed thread_id=thread-a input_token_count=10 output_token_count=5 "
            "cached_token_count=2 reasoning_token_count=1 tool_token_count=3",
            120,
            "thread-a",
        ),
        (
            2,
            1770000001,
            0,
            "post sampling token usage thread_id=thread-a turn_id=turn-a total_usage_tokens=100 "
            "estimated_token_count=80 auto_compact_scope_tokens=70 auto_compact_scope_limit=200 "
            "full_context_window_limit_reached=false needs_follow_up=false",
            150,
            "thread-a",
        ),
        (
            3,
            1770000002,
            0,
            '2026-02-02T00:00:02Z INFO thread.id=thread-a turn.id=turn-a ToolCall: exec_command '
            '{"cmd":"rg SECRET_TOKEN docs","max_output_tokens":20000}',
            190,
            "thread-a",
        ),
        (
            4,
            1770000003,
            0,
            '2026-02-02T00:00:03Z INFO thread.id=thread-b turn.id=turn-b ToolCall: exec_command {"cmd":"pytest"}',
            90,
            "thread-b",
        ),
        (
            5,
            "bad-ts",
            0,
            '2026-02-02T00:00:04Z INFO thread.id=thread-a turn.id=bad ToolCall: exec_command {"cmd":"should skip"}',
            90,
            "thread-a",
        ),
    ]
    connection.executemany("insert into logs values (?, ?, ?, ?, ?, ?)", rows)
    connection.commit()
    connection.close()
    return path


def test_codex_audit_sqlite_filters_threads_and_reports_snapshots(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_sqlite(home)

    result = run_script(
        AUDIT_SCRIPT,
        "--home",
        str(home),
        "--source",
        "auto",
        "--thread-id",
        "thread-a",
        "--format",
        "json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["source"]["kind"] == "sqlite"
    assert payload["source"]["status"] == "used"
    assert payload["selection"]["selection_confidence"] == "high"
    assert payload["selection"]["missing_thread_ids"] == []
    assert payload["counts"]["tool_calls"] == 1
    assert payload["token_observations"]["signal_class"] == "snapshot"
    assert "sqlite_runtime_token_snapshots" in payload["cost_signal_status"]["snapshot"]
    assert "session_total" not in result.stdout
    assert "SECRET_TOKEN" not in result.stdout
    assert payload["largest_requested_max_output_tokens"][0]["requested_max_output_tokens"] == 20000


def test_codex_audit_lists_threads_and_marks_missing_thread_ids(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_sqlite(home)

    listed = run_script(AUDIT_SCRIPT, "--home", str(home), "--list-threads", "--format", "json")
    assert listed.returncode == 0, listed.stderr
    payload = json.loads(listed.stdout)
    assert [item["thread_id"] for item in payload["threads"][:2]] == ["thread-b", "thread-a"]

    missing = run_script(AUDIT_SCRIPT, "--home", str(home), "--thread-id", "missing", "--format", "json")
    assert missing.returncode == 0, missing.stderr
    missing_payload = json.loads(missing.stdout)
    assert missing_payload["status"] == "no_matching_threads"
    assert missing_payload["selection"]["missing_thread_ids"] == ["missing"]
    assert missing_payload["selection"]["selection_confidence"] == "low"
    assert missing_payload["counts"]["tool_calls"] == 0


def test_codex_audit_tui_fallback_since_and_snippet_safety(tmp_path: Path) -> None:
    home = tmp_path / "home"
    log_path = home / ".codex" / "log" / "codex-tui.log"
    log_path.parent.mkdir(parents=True)
    log_path.write_text(
        "\n".join(
            [
                '2026-02-01T00:00:00Z INFO thread.id=old turn.id=old ToolCall: exec_command {"cmd":"ls SECRET_TOKEN"}',
                '2026-02-02T00:00:00Z INFO thread.id=thread-t turn.id=turn-t ToolCall: exec_command {"cmd":"pytest tests"}',
                '2026-02-02T00:00:01Z INFO thread.id=thread-u turn.id=turn-u ToolCall: exec_command {"cmd":"rg docs"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        AUDIT_SCRIPT,
        "--home",
        str(home),
        "--source",
        "tui",
        "--since",
        "2026-02-02T00:00:00Z",
        "--max-auto-threads",
        "1",
        "--format",
        "json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source"]["kind"] == "tui"
    assert payload["selection"]["thread_ids"] == ["thread-u"]
    assert payload["selection"]["excluded_thread_count"] == 1
    assert payload["counts"]["tool_calls"] == 1
    assert payload["token_observations"]["signal_class"] == "unavailable"
    assert "SECRET_TOKEN" not in result.stdout

    snippets = run_script(
        AUDIT_SCRIPT,
        "--home",
        str(home),
        "--source",
        "tui",
        "--include-command-snippets",
        "--max-command-len",
        "8",
    )
    assert snippets.returncode == 0, snippets.stderr
    snippet_payload = json.loads(snippets.stdout)
    commands = [item["command"] for item in snippet_payload["largest_proxy_cost_tool_calls"]]
    assert commands and commands[0].endswith("...")
    assert len(commands[0]) <= 8


def test_codex_audit_markdown_invalid_since_and_missing_source(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_sqlite(home)

    markdown = run_script(AUDIT_SCRIPT, "--home", str(home), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    assert "# Codex Session Efficiency Audit" in markdown.stdout
    assert "evidence pointers" in markdown.stdout

    invalid = run_script(AUDIT_SCRIPT, "--home", str(home), "--since", "not-a-date")
    assert invalid.returncode == 2
    assert "Invalid --since timestamp" in invalid.stdout

    missing = run_script(AUDIT_SCRIPT, "--home", str(tmp_path / "missing-home"), "--source", "sqlite")
    assert missing.returncode == 0, missing.stderr
    missing_payload = json.loads(missing.stdout)
    assert missing_payload["status"] == "source_missing"
    assert missing_payload["waste_candidates"] == []


def test_codex_audit_auto_skips_unreadable_sqlite_for_tui(tmp_path: Path) -> None:
    home = tmp_path / "home"
    sqlite_path = home / ".codex" / "logs_2.sqlite"
    sqlite_path.parent.mkdir(parents=True)
    sqlite_path.write_text("not sqlite", encoding="utf-8")
    log_path = home / ".codex" / "log" / "codex-tui.log"
    log_path.parent.mkdir(parents=True)
    log_path.write_text(
        '2026-02-02T00:00:00Z INFO thread.id=thread-t turn.id=turn-t ToolCall: exec_command {"cmd":"pytest"}\n',
        encoding="utf-8",
    )

    auto = run_script(AUDIT_SCRIPT, "--home", str(home), "--source", "auto")
    assert auto.returncode == 0, auto.stderr
    auto_payload = json.loads(auto.stdout)
    assert auto_payload["source"]["kind"] == "tui"
    assert auto_payload["status"] == "ok"

    explicit = run_script(AUDIT_SCRIPT, "--home", str(home), "--source", "sqlite")
    assert explicit.returncode == 0, explicit.stderr
    explicit_payload = json.loads(explicit.stdout)
    assert explicit_payload["source"]["status"] == "unreadable"
    assert explicit_payload["status"] == "source_unreadable"


def test_codex_audit_rejects_schema_drifted_sqlite(tmp_path: Path) -> None:
    home = tmp_path / "home"
    path = home / ".codex" / "logs_2.sqlite"
    path.parent.mkdir(parents=True)
    connection = sqlite3.connect(path)
    connection.execute("create table logs(id integer, feedback_log_body text)")
    connection.commit()
    connection.close()

    result = run_script(AUDIT_SCRIPT, "--home", str(home), "--source", "sqlite")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source"]["status"] == "unreadable"
    assert payload["status"] == "source_unreadable"
    assert payload["waste_candidates"] == []
