from __future__ import annotations

import json
from pathlib import Path

from scripts import host_log_probe_lib

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
    assert payload["goal_metric_window"]["missing"] == ["codex_session_file|claude_session_file"]
    assert "goal_window_audit" not in payload["hosts"]["codex"]
    assert "goal_window_audit" not in payload["hosts"]["claude"]


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


def test_goal_metric_window_reports_missing_relative_goal_path(tmp_path: Path) -> None:
    payload = host_log_probe_lib.parse_goal_metric_window(tmp_path, Path("missing-goal.md"))

    assert payload == {"status": "missing", "path": str(tmp_path / "missing-goal.md")}


def test_goal_metric_window_reports_absent_window_from_relative_goal_path(tmp_path: Path) -> None:
    goal = tmp_path / "goal.md"
    goal.write_text("# Goal\n\nNo host metric window here.\n", encoding="utf-8")

    payload = host_log_probe_lib.parse_goal_metric_window(tmp_path, Path("goal.md"))

    assert payload == {"status": "absent", "path": str(goal)}


def test_goal_metric_window_ignores_malformed_field_parts(tmp_path: Path) -> None:
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-04-14T12:00:30Z ignored-token\n",
        encoding="utf-8",
    )

    payload = host_log_probe_lib.parse_goal_metric_window(tmp_path, goal)

    assert payload["status"] == "invalid"
    assert payload["missing"] == ["completed_at", "codex_session_file|claude_session_file"]


def test_goal_window_session_path_requires_string_value(tmp_path: Path) -> None:
    session = tmp_path / "rollout.jsonl"
    session.write_text("{}\n", encoding="utf-8")

    assert host_log_probe_lib._goal_window_session_path(
        {"status": "parsed", "codex_session_file": str(session)}
    ) == session
    assert host_log_probe_lib._goal_window_session_path(
        {"status": "parsed", "codex_session_file": 123}
    ) is None


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


def _claude_session_lines() -> str:
    return (
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": "2026-06-10T01:00:00Z",
                        "message": {
                            "role": "assistant",
                            "usage": {"input_tokens": 1, "output_tokens": 2},
                            "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}],
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": "2026-06-10T02:00:00Z",
                        "message": {
                            "role": "assistant",
                            "usage": {"input_tokens": 1, "output_tokens": 2},
                            "content": [{"type": "tool_use", "name": "Read", "input": {}}],
                        },
                    }
                ),
            ]
        )
        + "\n"
    )


def test_host_log_probe_emits_claude_single_session_audit(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    session = project / "current.jsonl"
    session.write_text(_claude_session_lines(), encoding="utf-8")

    result = run_script("skills/public/retro/scripts/probe_host_logs.py", "--home", str(home))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    audit = payload["hosts"]["claude"]["session_audit"]
    assert audit["source"] == {"kind": "session-jsonl", "host": "claude", "path": str(session)}
    assert audit["measured"]["total_events"] == 2
    assert audit["measured"]["function_calls"] == 2
    assert audit["last_event_at"] == "2026-06-10T02:00:00Z"


def test_host_log_probe_scopes_goal_window_to_claude_session(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    session = project / "current.jsonl"
    session.write_text(_claude_session_lines(), encoding="utf-8")
    # A stale Codex rollout exists; the claude-keyed window must not produce a
    # codex goal_window_audit from it (the misattribution class under repair).
    stale_codex = home / ".codex" / "sessions" / "2026" / "06" / "05"
    stale_codex.mkdir(parents=True)
    (stale_codex / "rollout-2026-06-05T16-00-00-stale.jsonl").write_text(
        json.dumps({"timestamp": "2026-06-05T16:00:00Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": "{}"}})
        + "\n",
        encoding="utf-8",
    )
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-06-10T01:30:00Z "
        f"completed_at=2026-06-10T02:30:00Z claude_session_file={session}\n",
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
    assert payload["goal_metric_window"]["session_host"] == "claude"
    assert payload["goal_metric_window"]["claude_session_file"] == str(session)
    scoped = payload["hosts"]["claude"]["goal_window_audit"]
    assert scoped["measured"]["function_calls"] == 1
    assert scoped["window_filter"]["included_records"] == 1
    assert scoped["window_filter"]["excluded_before"] == 1
    assert "goal_window_audit" not in payload["hosts"]["codex"]


def test_host_log_probe_rejects_goal_window_naming_both_hosts(tmp_path: Path) -> None:
    session = tmp_path / "session.jsonl"
    session.write_text("{}\n", encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-06-10T01:00:00Z completed_at=2026-06-10T02:00:00Z "
        f"codex_session_file={session} claude_session_file={session}\n",
        encoding="utf-8",
    )

    payload = host_log_probe_lib.parse_goal_metric_window(tmp_path, goal)

    assert payload["status"] == "invalid"
    assert payload["ambiguous_session_file"] == ["codex_session_file", "claude_session_file"]


def test_host_log_probe_never_substitutes_a_missing_named_claude_session(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    (project / "other.jsonl").write_text(_claude_session_lines(), encoding="utf-8")

    result = run_script(
        "skills/public/retro/scripts/probe_host_logs.py",
        "--home",
        str(home),
        "--claude-session-file",
        str(project / "missing.jsonl"),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    claude = payload["hosts"]["claude"]
    assert "session_audit" not in claude
    assert claude["metrics"]["token_count"]["status"] == "unavailable"
    assert "Named Claude session file not found" in claude["metrics"]["token_count"]["detail"]


def test_host_log_probe_existing_codex_window_round_trips_unchanged(tmp_path: Path) -> None:
    session = tmp_path / "rollout.jsonl"
    session.write_text("{}\n", encoding="utf-8")
    goal = tmp_path / "goal.md"
    goal.write_text(
        "Host metric window: started_at=2026-06-10T01:00:00Z "
        f"completed_at=2026-06-10T02:00:00Z codex_session_file={session}\n",
        encoding="utf-8",
    )

    payload = host_log_probe_lib.parse_goal_metric_window(tmp_path, goal)

    assert payload["status"] == "parsed"
    assert payload["session_host"] == "codex"
    assert payload["codex_session_file"] == str(session)


def test_probe_to_render_keeps_fresh_codex_over_stale_claude(tmp_path: Path) -> None:
    # Integration pin for the freshest-session fallback: synthetic render
    # fixtures masked a dropped last_event_at in the codex summary, so this
    # goes probe -> render with BOTH hosts populated.
    from scripts import goal_metrics_render_lib

    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    stale_claude = json.dumps(
        {
            "type": "assistant",
            "timestamp": "2026-06-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "content": [{"type": "tool_use", "name": "Read", "input": {}}],
            },
        }
    )
    (project / "stale.jsonl").write_text(stale_claude + "\n", encoding="utf-8")
    codex_dir = home / ".codex" / "sessions" / "2026" / "06" / "10"
    codex_dir.mkdir(parents=True)
    fresh_codex = json.dumps(
        {
            "timestamp": "2026-06-10T12:00:00Z",
            "type": "response_item",
            "payload": {"type": "function_call", "name": "exec_command", "arguments": "{}"},
        }
    )
    (codex_dir / "rollout-2026-06-10T12-00-00-fresh.jsonl").write_text(fresh_codex + "\n", encoding="utf-8")

    payload = host_log_probe_lib.build_payload(home=home, repo_root=tmp_path)
    block = goal_metrics_render_lib.render_goal_metrics_block(payload)

    assert payload["hosts"]["codex"]["session_audit"]["last_event_at"] == "2026-06-10T12:00:00Z"
    assert "### Measured (thread-wide scope)" in block
    assert "thread-wide, claude session" not in block


def test_probe_to_render_prefers_fresh_claude_over_stale_codex(tmp_path: Path) -> None:
    from scripts import goal_metrics_render_lib

    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    (project / "fresh.jsonl").write_text(_claude_session_lines(), encoding="utf-8")
    codex_dir = home / ".codex" / "sessions" / "2026" / "06" / "01"
    codex_dir.mkdir(parents=True)
    stale_codex = json.dumps(
        {
            "timestamp": "2026-06-01T00:00:00Z",
            "type": "response_item",
            "payload": {"type": "function_call", "name": "exec_command", "arguments": "{}"},
        }
    )
    (codex_dir / "rollout-2026-06-01T00-00-00-stale.jsonl").write_text(stale_codex + "\n", encoding="utf-8")

    payload = host_log_probe_lib.build_payload(home=home, repo_root=tmp_path)
    block = goal_metrics_render_lib.render_goal_metrics_block(payload)

    assert "### Measured (thread-wide, claude session scope)" in block
    assert "- session: " in block
