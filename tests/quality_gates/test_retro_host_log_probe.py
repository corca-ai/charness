from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_host_log_probe_reports_claude_and_codex_metric_availability(tmp_path: Path) -> None:
    home = tmp_path / "home"
    claude_project = home / ".claude" / "projects" / "demo-project"
    claude_project.mkdir(parents=True)
    (home / ".claude" / "history.jsonl").write_text('{"sessionId":"s","type":"user"}\n', encoding="utf-8")
    (claude_project / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "user",
                        "timestamp": "2026-04-14T12:00:00Z",
                        "message": {"role": "user", "content": "hi"},
                    }
                ),
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": "2026-04-14T12:00:05Z",
                        "message": {
                            "role": "assistant",
                            "usage": {
                                "input_tokens": 12,
                                "output_tokens": 34,
                                "cache_creation_input_tokens": 0,
                                "cache_read_input_tokens": 0,
                            },
                            "content": [{"type": "tool_use", "name": "bash"}],
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    codex_log_dir = home / ".codex" / "log"
    codex_log_dir.mkdir(parents=True)
    (home / ".codex" / "history.jsonl").write_text('{"session_id":"s","text":"prompt"}\n', encoding="utf-8")
    (home / ".codex" / "logs_2.sqlite").write_text("", encoding="utf-8")
    codex_session_dir = home / ".codex" / "sessions" / "2026" / "04" / "14"
    codex_session_dir.mkdir(parents=True)
    (codex_session_dir / "rollout-2026-04-14T12-00-00-demo.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-04-14T12:01:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 10,
                                    "cached_input_tokens": 4,
                                    "output_tokens": 2,
                                    "reasoning_output_tokens": 1,
                                    "total_tokens": 12,
                                }
                            },
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-04-14T12:01:01Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "pytest tests"}),
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (codex_log_dir / "codex-tui.log").write_text(
        "\n".join(
            [
                "2026-04-14T12:01:00.000000Z INFO session_loop:turn{turn.id=turn-1}: started",
                "2026-04-14T12:01:02.000000Z INFO codex_core::stream_events_utils: ToolCall: exec_command {\"cmd\":\"pwd\"}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/retro/scripts/probe_host_logs.py", "--home", str(home))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    claude = payload["hosts"]["claude"]
    assert claude["metrics"]["token_count"]["status"] == "available"
    assert claude["metrics"]["tool_call_count"]["status"] == "derivable"
    assert claude["metrics"]["duration"]["status"] == "derivable"
    assert claude["metrics"]["turn_count"]["status"] == "derivable"

    codex = payload["hosts"]["codex"]
    assert codex["metrics"]["duration"]["status"] == "derivable"
    assert codex["metrics"]["turn_count"]["status"] == "derivable"
    assert codex["metrics"]["tool_call_count"]["status"] == "derivable"
    assert codex["metrics"]["token_count"]["status"] == "available"
    assert codex["session_audit"]["measured"]["token_count_snapshots"] == 1
    assert codex["session_audit"]["measured"]["function_calls"] == 1


def test_host_log_probe_reads_goal_metric_window(tmp_path: Path) -> None:
    home = tmp_path / "home"
    session_dir = home / ".codex" / "sessions" / "2026" / "04" / "14"
    session_dir.mkdir(parents=True)
    session_file = session_dir / "rollout-2026-04-14T12-00-00-window.jsonl"
    session_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-04-14T12:00:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "git status"}),
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-04-14T12:01:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "pytest -q"}),
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-04-14T12:00:30Z "
        f"completed_at=2026-04-14T12:01:30Z codex_session_file={session_file}\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/probe_host_logs.py",
        "--home",
        str(home),
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["goal_metric_window"]["status"] == "parsed"
    scoped = payload["hosts"]["codex"]["goal_window_audit"]
    assert scoped["measured"]["function_calls"] == 1
    assert scoped["window_filter"]["included_records"] == 1
    assert scoped["window_filter"]["excluded_before"] == 1


def test_host_log_probe_rejects_goal_window_without_session_file(tmp_path: Path) -> None:
    home = tmp_path / "home"
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-04-14T12:00:30Z completed_at=2026-04-14T12:01:30Z\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/probe_host_logs.py",
        "--home",
        str(home),
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["goal_metric_window"]["status"] == "invalid"
    assert payload["goal_metric_window"]["missing"] == ["codex_session_file"]
    assert "goal_window_audit" not in payload["hosts"]["codex"]


def test_host_log_probe_rejects_goal_window_with_missing_session_file(tmp_path: Path) -> None:
    home = tmp_path / "home"
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-04-14T12:00:30Z "
        "completed_at=2026-04-14T12:01:30Z codex_session_file=missing.jsonl\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/probe_host_logs.py",
        "--home",
        str(home),
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["goal_metric_window"]["status"] == "invalid"
    assert payload["goal_metric_window"]["missing_session_file"] == str(tmp_path / "missing.jsonl")
    assert "goal_window_audit" not in payload["hosts"]["codex"]


def test_host_log_probe_rejects_goal_window_with_invalid_timestamp(tmp_path: Path) -> None:
    home = tmp_path / "home"
    session_file = tmp_path / "rollout.jsonl"
    session_file.write_text("{}\n", encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(
        f"Host metric window: started_at=not-a-time completed_at=2026-04-14T12:01:30Z codex_session_file={session_file}\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/probe_host_logs.py",
        "--home",
        str(home),
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["goal_metric_window"]["status"] == "invalid"
    assert payload["goal_metric_window"]["invalid_timestamps"] == ["started_at"]
    assert "goal_window_audit" not in payload["hosts"]["codex"]


def test_host_log_probe_degrades_honestly_when_logs_are_missing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()

    result = run_script("skills/public/retro/scripts/probe_host_logs.py", "--home", str(home))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    for host_id in ("claude", "codex"):
        metrics = payload["hosts"][host_id]["metrics"]
        for metric_name in ("duration", "turn_count", "token_count", "tool_call_count"):
            assert metrics[metric_name]["status"] == "unavailable"
