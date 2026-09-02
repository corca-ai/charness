from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module
from scripts.evidence import host_log_probe_lib

from .support import ROOT

probe = import_repo_module(
    ROOT / "skills/public/retro/scripts/probe_host_logs.py",
    "skills.public.retro.scripts.probe_host_logs",
)


def run_probe(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["probe_host_logs.py", *args])
    returncode = probe.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_host_log_probe_reports_generic_claude_and_codex_metrics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    home = tmp_path / "home"
    claude_project = home / ".claude" / "projects" / "demo-project"
    claude_project.mkdir(parents=True)
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
                            "usage": {"input_tokens": 12, "output_tokens": 34},
                            "content": [{"type": "tool_use", "name": "bash"}],
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    codex_log = home / ".codex" / "log"
    codex_log.mkdir(parents=True)
    (codex_log / "codex-tui.log").write_text(
        "2026-04-14T12:01:00.000000Z INFO turn.id=turn-1\n"
        "2026-04-14T12:01:02.000000Z INFO ToolCall: exec_command\n",
        encoding="utf-8",
    )
    session = home / ".codex" / "sessions" / "2026" / "04" / "14"
    session.mkdir(parents=True)
    (session / "rollout-2026-04-14T12-00-00-demo.jsonl").write_text(
        json.dumps(
            {
                "timestamp": "2026-04-14T12:01:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"input_tokens": 1}},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_probe(monkeypatch, capsys, "--home", str(home), "--repo-root", str(tmp_path))

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["hosts"]["claude"]["metrics"]["token_count"]["status"] == "available"
    assert payload["hosts"]["codex"]["metrics"]["duration"]["status"] == "derivable"
    assert "goal_metric_window" not in payload
    assert "goal_lineage" not in payload


def test_host_log_probe_reports_unavailable_when_logs_are_missing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    home = tmp_path / "home"
    home.mkdir()

    result = run_probe(monkeypatch, capsys, "--home", str(home))

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    for host in ("claude", "codex"):
        for name in ("duration", "turn_count", "token_count", "tool_call_count"):
            assert payload["hosts"][host]["metrics"][name]["status"] == "unavailable"


def test_named_missing_claude_session_is_not_replaced(tmp_path: Path, monkeypatch, capsys) -> None:
    home = tmp_path / "home"
    project = home / ".claude" / "projects" / "demo-project"
    project.mkdir(parents=True)
    (project / "other.jsonl").write_text(
        json.dumps({"type": "assistant", "timestamp": "2026-06-10T01:00:00Z"}) + "\n",
        encoding="utf-8",
    )

    result = run_probe(
        monkeypatch,
        capsys,
        "--home",
        str(home),
        "--claude-session-file",
        str(project / "missing.jsonl"),
    )

    payload = yaml.safe_load(result.stdout)
    claude = payload["hosts"]["claude"]
    assert "session_audit" not in claude
    assert "Named Claude session file not found" in claude["metrics"]["token_count"]["detail"]


def test_host_log_probe_payload_is_stable_and_has_no_goal_specific_consumer(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    first = run_probe(monkeypatch, capsys, "--home", str(home), "--repo-root", str(tmp_path))
    second = run_probe(monkeypatch, capsys, "--home", str(home), "--repo-root", str(tmp_path))

    assert first.stdout == second.stdout
    assert "\nhosts:\n  " in first.stdout
    assert "goal_window" not in first.stdout
    assert "goal_lineage" not in first.stdout


def test_probe_library_keeps_generic_named_session_input(tmp_path: Path) -> None:
    payload = host_log_probe_lib.build_payload(
        home=tmp_path / "home",
        repo_root=tmp_path,
        claude_session_file=tmp_path / "missing.jsonl",
    )

    assert "goal_metric_window" not in payload
    assert "goal_lineage" not in payload
    assert "Named Claude session file not found" in payload["hosts"]["claude"]["metrics"]["duration"]["detail"]
