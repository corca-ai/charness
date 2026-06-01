from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

AUDIT_SCRIPT = "skills/public/retro/scripts/audit_codex_session.py"


def _exec(cmd: str) -> dict:
    return {"type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": cmd})}}


def write_rollout(home: Path, session_id: str) -> Path:
    path = home / ".codex" / "sessions" / "2026" / "05" / "26" / f"rollout-2026-05-26T00-00-00-{session_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {"type": "session_meta", "payload": {"type": "session_meta"}},
        _exec("git status"),
        _exec("git status"),
        _exec("git status"),
        _exec("pytest -q"),
        _exec("pytest -q"),
        _exec("pytest -q"),
        {"type": "response_item", "payload": {"type": "function_call", "name": "update_plan", "arguments": "{}"}},
        {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "apply_patch", "input": "*** Begin Patch"}},
        {"type": "event_msg", "payload": {"type": "patch_apply_end", "success": True}},
        {"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "t1"}},
        {"type": "event_msg", "payload": {"type": "context_compacted"}},
        {"type": "compacted", "payload": {}},
        {"type": "event_msg", "payload": {"type": "token_count", "rate_limits": {"primary": {"used_percent": 42.0}}}},
    ]
    lines = [json.dumps(record) for record in records]
    lines.insert(5, "{not valid json")  # malformed line must be tolerated and counted
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_session_jsonl_audit_counts_and_separates(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_rollout(home, "abc123de")

    result = run_script(AUDIT_SCRIPT, "--home", str(home), "--session-id", "abc123de", "--format", "json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    measured = payload["measured"]
    assert measured["function_calls"] == 7  # 3 git status + 3 pytest + 1 update_plan
    assert measured["patch_applications"] == 1
    assert measured["task_completions"] == 1
    assert measured["context_compactions"] == 2  # event_msg + top-level compacted
    assert measured["goal_or_plan_updates"] == 1
    assert measured["custom_tool_calls"] == 1

    assert payload["proxy"]["repeated_broad_gates"].get("pytest") == 3
    assert payload["proxy"]["repeated_vcs_commands"].get("git status") == 3
    assert payload["snapshots"]["last_rate_limits"]["primary"]["used_percent"] == 42.0
    assert payload["warnings"] == ["1 malformed JSONL line(s) dropped"]


def test_session_jsonl_audit_filters_goal_window(tmp_path: Path) -> None:
    home = tmp_path / "home"
    path = home / ".codex" / "sessions" / "2026" / "05" / "26" / "rollout-2026-05-26T00-00-00-window.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {"timestamp": "2026-05-26T00:00:00Z", **_exec("git status")},
        {"timestamp": "2026-05-26T00:01:00Z", **_exec("pytest -q")},
        {"timestamp": "2026-05-26T00:02:00Z", **_exec("git diff")},
        _exec("git log"),
    ]
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

    result = run_script(
        AUDIT_SCRIPT,
        "--home",
        str(home),
        "--session-file",
        str(path),
        "--started-at",
        "2026-05-26T00:00:30Z",
        "--completed-at",
        "2026-05-26T00:01:30Z",
        "--format",
        "json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["measured"]["function_calls"] == 1
    assert payload["proxy"]["repeated_vcs_commands"] == {}
    assert payload["window_filter"] == {
        "status": "applied",
        "started_at": "2026-05-26T00:00:30Z",
        "completed_at": "2026-05-26T00:01:30Z",
        "total_records": 4,
        "included_records": 1,
        "excluded_before": 1,
        "excluded_after": 1,
        "undated_records": 1,
    }


def test_session_jsonl_audit_rejects_invalid_window_timestamp(tmp_path: Path) -> None:
    home = tmp_path / "home"
    path = home / ".codex" / "sessions" / "2026" / "05" / "26" / "rollout-2026-05-26T00-00-00-window.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"timestamp": "2026-05-26T00:01:00Z", **_exec("pytest -q")}) + "\n", encoding="utf-8")

    result = run_script(
        AUDIT_SCRIPT,
        "--home",
        str(home),
        "--session-file",
        str(path),
        "--started-at",
        "not-a-time",
        "--format",
        "json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["measured"]["function_calls"] == 0
    assert payload["window_filter"] == {
        "status": "invalid",
        "started_at": "not-a-time",
        "completed_at": None,
        "invalid_bounds": ["started_at"],
        "total_records": 1,
        "included_records": 0,
        "undated_records": 0,
    }


def test_session_jsonl_audit_missing_session_returns_2(tmp_path: Path) -> None:
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    result = run_script(AUDIT_SCRIPT, "--home", str(home), "--session-id", "nope", "--format", "json")
    assert result.returncode == 2
    assert "No Codex rollout JSONL found" in result.stdout
