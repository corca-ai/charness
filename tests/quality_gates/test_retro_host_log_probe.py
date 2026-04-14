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
    assert codex["metrics"]["token_count"]["status"] == "unavailable"


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
