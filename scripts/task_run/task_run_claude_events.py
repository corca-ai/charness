"""Claude Code stream-json consumers: reports, sessions, and tool boundaries.

Assistant messages carry complete content blocks, user messages carry tool
results, and the terminal result carries the final report. Raw events remain
separate from the delivered report, including on an interrupted invocation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


def iter_events(text: str):
    """Yield recognized stream-json envelopes, ignoring damaged lines."""
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") in {
            "system",
            "assistant",
            "user",
            "result",
            "stream_event",
        }:
            yield event


def content_blocks(event: Mapping[str, Any]):
    """Content blocks from a complete assistant or user message."""
    message = event.get("message")
    blocks = message.get("content") if isinstance(message, Mapping) else None
    if isinstance(blocks, list):
        yield from (block for block in blocks if isinstance(block, Mapping))


def agent_text(event: Mapping[str, Any]) -> str:
    """Text from one complete assistant message, excluding tool output."""
    if event.get("type") != "assistant":
        return ""
    return "".join(
        block["text"]
        for block in content_blocks(event)
        if block.get("type") == "text" and isinstance(block.get("text"), str)
    )


def terminal_event(text: str) -> dict[str, Any] | None:
    """The last result envelope in this invocation."""
    return next(
        (event for event in reversed(list(iter_events(text))) if event.get("type") == "result"),
        None,
    )


def stdout_report(text: str) -> str | None:
    """Terminal report, or complete assistant text when interrupted."""
    events = list(iter_events(text))
    if not events:
        return None
    terminal = next((event for event in reversed(events) if event.get("type") == "result"), None)
    if terminal is not None and isinstance(terminal.get("result"), str):
        return terminal["result"]
    return "".join(agent_text(event) for event in events)


def session_id(text: str) -> str | None:
    """The latest session identity reported by the provider."""
    return next(
        (
            event["session_id"]
            for event in reversed(list(iter_events(text)))
            if isinstance(event.get("session_id"), str) and event["session_id"]
        ),
        None,
    )


def retain_events(stdout_log: Path, event_log: Path) -> str | None:
    """Separate JSONL evidence and the consumer's final report."""
    from scripts.task_run import task_run_evidence as evidence

    raw = evidence._tail_text(stdout_log, limit=64 * 1024 * 1024)
    report = stdout_report(raw)
    if report is None:
        return None
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(raw)
        if not raw.endswith("\n"):
            handle.write("\n")
    stdout_log.write_text(report, encoding="utf-8")
    return session_id(raw)


def apply_terminal_result(result: dict[str, Any], raw: str) -> None:
    """A provider error remains a failure even if the CLI exits zero.

    Only bounded outcome tokens enter diagnostics; arbitrary provider error
    content remains in the private raw events log.
    """
    terminal = terminal_event(raw)
    if terminal is None:
        return
    subtype = str(terminal.get("subtype") or "unknown")[:80]
    failed = bool(terminal.get("is_error")) or subtype.startswith("error_")
    result["claude_result"] = {"subtype": subtype, "is_error": failed}
    result["stream_diagnostics"] = {
        "terminal": "failed" if failed else "completed",
        "terminal_reason": subtype if failed else None,
        "retries": 0,
        "cause_status": "provided" if failed else "not-applicable",
    }
    if failed and result.get("exit_code") == 0:
        result["exit_code"] = 1


def command_key(event: Mapping[str, Any], bash_tasks: set[str]) -> tuple[str | None, str | None]:
    """Match a Bash invocation to its later tool result."""
    for block in content_blocks(event):
        if block.get("type") == "tool_use" and block.get("name") == "Bash":
            key = str(block.get("id"))
            bash_tasks.add(key)
            return key, "start"
        if block.get("type") == "tool_result" and str(block.get("tool_use_id")) in bash_tasks:
            return str(block["tool_use_id"]), "end"
    return None, None


def feed_timeline(timeline: Any, at: datetime | None, event: Mapping[str, Any]) -> None:
    """Feed Claude command boundaries and text into the shared timing state."""
    timeline._phase_text(at, agent_text(event) + "\n")
    for block in content_blocks(event):
        if (
            event.get("type") == "assistant"
            and block.get("type") == "tool_use"
            and block.get("name") == "Bash"
        ):
            key = str(block.get("id"))
            details = block.get("input")
            command = details.get("command") if isinstance(details, Mapping) else None
            timeline._bash_tasks.add(key)
            timeline._start(key, at, command if isinstance(command, str) else None)
        elif event.get("type") == "user" and block.get("type") == "tool_result":
            key = str(block.get("tool_use_id"))
            if key not in timeline._bash_tasks:
                continue
            entry = timeline.commands[key]
            entry["completed"] = at
            entry["done"] = True
            if timeline._on_complete is not None:
                timeline._on_complete(entry["command"], 1 if block.get("is_error") else 0)


def apply_executor_result(
    result: dict[str, Any], executor: str, event_log: Path, offset: int
) -> None:
    """Apply only this invocation window's Claude terminal outcome."""
    if executor != "claude":
        return
    from scripts.task_run import task_run_evidence as evidence

    apply_terminal_result(
        result,
        evidence._tail_text(
            event_log,
            limit=64 * 1024 * 1024,
            window=evidence._log_window(event_log, offset),
        ),
    )
