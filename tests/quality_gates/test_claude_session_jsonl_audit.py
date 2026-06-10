from __future__ import annotations

import json
from pathlib import Path

from scripts import claude_session_jsonl_audit as audit_mod


def _assistant_record(*, timestamp: str, tool_uses: list[dict] | None = None, usage: bool = True) -> str:
    message: dict = {"role": "assistant"}
    if usage:
        message["usage"] = {"input_tokens": 10, "output_tokens": 5}
    if tool_uses is not None:
        message["content"] = [{"type": "tool_use", **item} for item in tool_uses]
    return json.dumps({"type": "assistant", "timestamp": timestamp, "message": message})


def _write_session(path: Path, lines: list[str]) -> Path:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_audit_counts_claude_session_signals(tmp_path: Path) -> None:
    session = _write_session(
        tmp_path / "session.jsonl",
        [
            json.dumps({"type": "user", "timestamp": "2026-06-10T01:00:00Z", "message": {"role": "user"}}),
            _assistant_record(
                timestamp="2026-06-10T01:00:05Z",
                tool_uses=[
                    {"name": "Bash", "input": {"command": "git status"}},
                    {"name": "Edit", "input": {"file_path": "x.py"}},
                    {"name": "Task", "input": {"prompt": "review"}},
                    {"name": "mcp__slack__send", "input": {}},
                ],
            ),
            json.dumps({"type": "summary", "isCompactSummary": True, "summary": "compacted"}),
            "not-json",
        ],
    )

    payload = audit_mod.audit_session_jsonl(session)

    measured = payload["measured"]
    assert measured["total_events"] == 3
    assert measured["token_count_snapshots"] == 1
    assert measured["function_calls"] == 3  # Bash + Edit + Task; mcp__ split out
    assert measured["custom_tool_calls"] == 1
    assert measured["custom_tool_names"] == {"mcp__slack__send": 1}
    assert measured["patch_applications"] == 1
    assert measured["context_compactions"] == 1
    assert measured["subagent"] == {"spawn": 1}
    assert payload["source"] == {"kind": "session-jsonl", "host": "claude", "path": str(session)}
    assert payload["warnings"] == ["1 malformed JSONL line(s) dropped"]
    assert payload["last_event_at"] == "2026-06-10T01:00:05Z"


def test_audit_applies_window_filter_to_claude_session(tmp_path: Path) -> None:
    session = _write_session(
        tmp_path / "session.jsonl",
        [
            _assistant_record(timestamp="2026-06-10T01:00:00Z", tool_uses=[{"name": "Bash", "input": {"command": "ls"}}]),
            _assistant_record(timestamp="2026-06-10T02:00:00Z", tool_uses=[{"name": "Read", "input": {}}]),
            _assistant_record(timestamp="2026-06-10T03:00:00Z", tool_uses=[{"name": "Write", "input": {}}]),
        ],
    )

    payload = audit_mod.audit_session_jsonl(
        session, started_at="2026-06-10T01:30:00Z", completed_at="2026-06-10T02:30:00Z"
    )

    assert payload["window_filter"]["status"] == "applied"
    assert payload["window_filter"]["included_records"] == 1
    assert payload["window_filter"]["excluded_before"] == 1
    assert payload["window_filter"]["excluded_after"] == 1
    assert payload["measured"]["function_calls"] == 1
    assert payload["measured"]["function_call_names"] == {"Read": 1}
    assert payload["last_event_at"] == "2026-06-10T02:00:00Z"


def test_audit_derives_repeated_command_proxies_from_bash_tool_uses(tmp_path: Path) -> None:
    git_status = [{"name": "Bash", "input": {"command": "git status"}}]
    pytest_run = [{"name": "Bash", "input": {"command": "pytest -q tests"}}]
    session = _write_session(
        tmp_path / "session.jsonl",
        [
            _assistant_record(timestamp=f"2026-06-10T01:00:0{i}Z", tool_uses=git_status + pytest_run)
            for i in range(3)
        ],
    )

    payload = audit_mod.audit_session_jsonl(session)

    assert payload["proxy"]["repeated_vcs_commands"] == {"git status": 3}
    assert payload["proxy"]["repeated_broad_gates"] == {"pytest": 3}


def test_audit_degrades_on_empty_or_undated_session(tmp_path: Path) -> None:
    session = _write_session(tmp_path / "session.jsonl", [json.dumps({"type": "mode", "mode": "default"})])

    payload = audit_mod.audit_session_jsonl(session)

    assert payload["measured"]["total_events"] == 1
    assert payload["measured"]["function_calls"] == 0
    assert payload["last_event_at"] is None
    assert payload["warnings"] == []
