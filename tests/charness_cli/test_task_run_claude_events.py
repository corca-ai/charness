"""Claude stream transport preserves report, failure, and command evidence."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.task_run import task_run_claude_events as events
from scripts.task_run import task_run_event_timing as timing
from scripts.task_run import task_run_execution as execution
from scripts.task_run import task_run_lane_signals as signals
from scripts.task_run import task_run_progress_rule as rule
from scripts.task_run import task_run_runtime as runtime


def _lines(*records: dict) -> str:
    return "\n".join(json.dumps(record) for record in records) + "\n"


def _assistant(*content: dict) -> dict:
    return {"type": "assistant", "message": {"content": list(content)}}


def _tool_result(tool_id: str, *, error: bool = False) -> dict:
    return {
        "type": "user",
        "message": {
            "content": [{"type": "tool_result", "tool_use_id": tool_id, "is_error": error}]
        },
    }


def test_terminal_report_wins_and_transport_keeps_session(tmp_path: Path) -> None:
    raw = _lines(
        {"type": "system", "subtype": "init", "session_id": "session-one"},
        _assistant({"type": "text", "text": "CONTRACT-READ\n"}),
        {
            "type": "result",
            "subtype": "success",
            "result": "VERIFY: docs checked",
            "session_id": "session-one",
        },
    )
    stdout, forensic = tmp_path / "stdout.log", tmp_path / "claude.events.log"
    stdout.write_text(raw)
    session = execution._retain_invocation_events("claude", stdout, forensic, None, None)
    assert session == "session-one"
    assert stdout.read_text() == "VERIFY: docs checked"
    assert forensic.read_text() == raw


def test_interrupted_stream_retains_partial_agent_text_without_tool_output() -> None:
    raw = _lines(
        _assistant(
            {"type": "text", "text": "CONTRACT-READ\n"},
            {"type": "tool_use", "name": "Bash", "id": "b1", "input": {"command": "true"}},
        ),
        _tool_result("b1"),
        _assistant({"type": "text", "text": "EDITING\n"}),
    )
    assert events.stdout_report(raw) == "CONTRACT-READ\nEDITING\n"
    assert signals.lane_progress(raw)["phases"] == ["CONTRACT-READ", "EDITING"]
    assert events.stdout_report("plain report") is None
    assert events.stdout_report("[]\n{bad\n{}\n") is None


def test_error_result_sets_typed_failure_even_with_zero_process_exit() -> None:
    result = {"exit_code": 0}
    events.apply_terminal_result(
        result,
        _lines(
            {
                "type": "result",
                "subtype": "error_max_turns",
                "is_error": True,
                "errors": ["budget exhausted"],
            }
        ),
    )
    assert result["exit_code"] == 1
    assert result["claude_result"]["subtype"] == "error_max_turns"
    assert result["claude_result"]["is_error"] is True
    assert result["stream_diagnostics"]["terminal"] == "failed"
    assert result["stream_diagnostics"]["terminal_reason"] == "error_max_turns"


def test_claude_commands_roundtrip_through_receive_stamps_and_timeline() -> None:
    start = _assistant(
        {"type": "text", "text": "TESTING\n"},
        {
            "type": "tool_use",
            "name": "Bash",
            "id": "b1",
            "input": {"command": "pytest tests/test_doc.py"},
        },
    )
    end = _tool_result("b1")
    durations = timing.CommandDurations()
    first = timing.stamp_event_line(json.dumps(start).encode(), "2026-10-25T00:00:00Z", durations)
    last = timing.stamp_event_line(json.dumps(end).encode(), "2026-10-25T00:00:03Z", durations)
    assert json.loads(last)[timing.DURATION_MS_FIELD] == 3000
    report = timing.command_timing(first.decode() + "\n" + last.decode())
    assert report["command_starts"] == 1
    assert report["longest_commands"] == [
        {"command": "pytest tests/test_doc.py", "duration_seconds": 3.0, "families": ["test"]}
    ]
    guard = rule.ProgressRule(window_seconds=10, fingerprint=lambda: "tree")
    guard.start(0)
    guard.on_event(start)
    assert guard._in_flight()
    guard.on_event(end)
    assert not guard._in_flight()
    assert guard._new_outcomes == 1


def test_successful_claude_edit_is_progress_but_refused_edit_is_not() -> None:
    guard = rule.ProgressRule(window_seconds=10, fingerprint=lambda: None)
    guard.start(0)
    guard.on_event(_assistant({"type": "tool_use", "name": "Edit", "id": "e1", "input": {}}))
    guard.on_event(_tool_result("e1", error=True))
    assert guard._new_outcomes == 0
    guard.on_event(_assistant({"type": "tool_use", "name": "Write", "id": "e2", "input": {}}))
    guard.on_event(_tool_result("e2"))
    assert guard._new_outcomes == 1


def test_claude_parent_auth_input_scrubs_unrelated_secrets_even_with_explicit_keep(
    tmp_path: Path, monkeypatch
) -> None:
    operator_home = tmp_path / "operator"
    monkeypatch.setattr(Path, "home", lambda: operator_home)
    monkeypatch.setenv(runtime.LANE_KEEP_SECRET_ENV, "GITHUB_TOKEN,OPENAI_API_KEY")
    worktree, execution_root = tmp_path / "lane", tmp_path / "runtime"
    payload = {"worktree_path": str(worktree)}
    parent_input = runtime.scrubbed_lane_env(
        payload,
        {
            "CHARNESS_RUNTIME_ROOT": str(execution_root),
            "GITHUB_TOKEN": "unrelated-github-fixture",
            "OPENAI_API_KEY": "unrelated-openai-fixture",
            "CLAUDE_CODE_OAUTH_TOKEN": "parent-proxy-input-fixture",
        },
        "claude",
    )
    assert "GITHUB_TOKEN" not in parent_input
    assert "OPENAI_API_KEY" not in parent_input
    assert parent_input["CLAUDE_CODE_OAUTH_TOKEN"] == "parent-proxy-input-fixture"
    assert Path(parent_input["HOME"]).is_relative_to(execution_root)
    assert payload["lane_env"]["scrubbed"] == ["GITHUB_TOKEN", "OPENAI_API_KEY"]
    assert payload["lane_env"]["kept_secret_names"] == ["CLAUDE_CODE_OAUTH_TOKEN"]


def test_claude_steer_resumes_observed_session_without_changing_safety_flags() -> None:
    from scripts.task_run.task_run_lane_runner import steered_lane_invocation

    original = ["bwrap", "--ro-bind", "/", "/", "--", "claude", "-p", "--settings", "private.json"]
    messages = [{"message_id": "s1", "queued_at": "now", "message": "finish docs"}]
    resumed, _, mode = steered_lane_invocation("claude", original, "task", messages, "session-a")
    assert mode == "session-resume"
    assert resumed == [*original, "--resume", "session-a"]
    again, _, _ = steered_lane_invocation("claude", resumed, "task", messages, "session-b")
    assert again == [*original, "--resume", "session-b"]
    assert original[-1] == "private.json"
