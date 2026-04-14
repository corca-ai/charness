from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

ISO_TS_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def metric(status: str, *, source: str | None = None, detail: str | None = None) -> dict[str, str]:
    payload = {"status": status}
    if source is not None:
        payload["source"] = source
    if detail is not None:
        payload["detail"] = detail
    return payload


def _claude_project_dir_name(repo_root: Path) -> str:
    return "-" + repo_root.resolve().as_posix().strip("/").replace("/", "-")


def _pick_claude_project_log(project_root: Path, repo_root: Path) -> Path | None:
    preferred_dir = project_root / _claude_project_dir_name(repo_root)
    preferred_paths = sorted(preferred_dir.glob("*.jsonl"))
    if preferred_paths:
        return max(preferred_paths, key=lambda path: path.stat().st_mtime)
    project_paths = sorted(project_root.glob("*/*.jsonl"))
    if not project_paths:
        return None
    return max(project_paths, key=lambda path: path.stat().st_mtime)


def probe_claude(home: Path, repo_root: Path) -> dict[str, Any]:
    claude_root = home / ".claude"
    history_path = claude_root / "history.jsonl"
    latest_project = _pick_claude_project_log(claude_root / "projects", repo_root)

    result: dict[str, Any] = {
        "detected": claude_root.exists(),
        "sources": [],
        "metrics": {},
    }
    if history_path.exists():
        result["sources"].append(
            {
                "kind": "history",
                "path": str(history_path),
                "status": "ignored",
                "reason": "thin-history",
            }
        )
    if latest_project is None:
        result["metrics"] = {
            "duration": metric("unavailable", detail="No Claude project JSONL found"),
            "turn_count": metric("unavailable", detail="No Claude project JSONL found"),
            "token_count": metric("unavailable", detail="No Claude project JSONL found"),
            "tool_call_count": metric("unavailable", detail="No Claude project JSONL found"),
        }
        return result

    has_usage = False
    has_token_fields = False
    has_tool_use = False
    has_timestamp = False
    has_user_or_assistant = False
    with latest_project.open(encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            if isinstance(payload.get("timestamp"), str):
                has_timestamp = True
            if payload.get("type") in {"user", "assistant"}:
                has_user_or_assistant = True
            message = payload.get("message")
            if isinstance(message, dict):
                usage = message.get("usage")
                if isinstance(usage, dict):
                    has_usage = True
                    if all(field in usage for field in ("input_tokens", "output_tokens")):
                        has_token_fields = True
                content = message.get("content")
                if isinstance(content, list):
                    has_tool_use = has_tool_use or any(
                        isinstance(item, dict) and item.get("type") == "tool_use" for item in content
                    )

    result["sources"].append({"kind": "project-jsonl", "path": str(latest_project), "status": "used"})
    result["metrics"] = {
        "duration": metric(
            "derivable" if has_timestamp else "unavailable",
            source=str(latest_project),
            detail="timestamped session events exist" if has_timestamp else "No timestamps found",
        ),
        "turn_count": metric(
            "derivable" if has_user_or_assistant and has_timestamp else "unavailable",
            source=str(latest_project),
            detail=(
                "user/assistant events exist but require pairing heuristics"
                if has_user_or_assistant and has_timestamp
                else "Stable turn boundary not found"
            ),
        ),
        "token_count": metric(
            "available" if has_usage and has_token_fields else "unavailable",
            source=str(latest_project),
            detail=(
                "message.usage.input_tokens/output_tokens present"
                if has_usage and has_token_fields
                else "No assistant usage token fields found"
            ),
        ),
        "tool_call_count": metric(
            "derivable" if has_tool_use else "unavailable",
            source=str(latest_project),
            detail="message.content includes tool_use items" if has_tool_use else "No tool_use items found",
        ),
    }
    return result


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_codex_sqlite_log(path: Path) -> str:
    try:
        connection = sqlite3.connect(path)
    except sqlite3.Error:
        return ""
    try:
        rows = connection.execute(
            "select feedback_log_body from logs where feedback_log_body is not null order by id desc limit 400"
        ).fetchall()
    except sqlite3.Error:
        return ""
    finally:
        connection.close()
    return "\n".join(reversed([row[0] for row in rows if isinstance(row[0], str)]))


def _codex_non_toolcall_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if "ToolCall:" not in line]


def probe_codex(home: Path) -> dict[str, Any]:
    codex_root = home / ".codex"
    history_path = codex_root / "history.jsonl"
    tui_log = codex_root / "log" / "codex-tui.log"
    sqlite_log = codex_root / "logs_2.sqlite"

    result: dict[str, Any] = {
        "detected": codex_root.exists(),
        "sources": [],
        "metrics": {},
    }
    if history_path.exists():
        result["sources"].append(
            {
                "kind": "history",
                "path": str(history_path),
                "status": "ignored",
                "reason": "thin-history",
            }
        )

    if not tui_log.exists() and not sqlite_log.exists():
        result["metrics"] = {
            "duration": metric("unavailable", detail="No Codex runtime logs found"),
            "turn_count": metric("unavailable", detail="No Codex runtime logs found"),
            "token_count": metric("unavailable", detail="No Codex runtime logs found"),
            "tool_call_count": metric("unavailable", detail="No Codex runtime logs found"),
        }
        return result

    log_source = tui_log if tui_log.exists() else sqlite_log
    text = _read_text(log_source) if log_source.suffix != ".sqlite" else _read_codex_sqlite_log(log_source)
    non_toolcall_lines = _codex_non_toolcall_lines(text)
    has_timestamp = any(ISO_TS_PREFIX.match(line) for line in non_toolcall_lines)
    has_turn_id = any("turn.id=" in line for line in non_toolcall_lines)
    has_tool_call = "ToolCall:" in text
    has_token_signal = any(
        marker in line
        for line in non_toolcall_lines
        for marker in ("tokenUsage/updated", "ThreadTokenUsageUpdated", "input_tokens", "output_tokens")
    )

    result["sources"].append(
        {
            "kind": "tui-log" if log_source == tui_log else "sqlite-log",
            "path": str(log_source),
            "status": "used",
        }
    )
    if sqlite_log.exists():
        result["sources"].append({"kind": "sqlite-log", "path": str(sqlite_log), "status": "available"})

    result["metrics"] = {
        "duration": metric(
            "derivable" if has_timestamp else "unavailable",
            source=str(log_source),
            detail="timestamped runtime log lines exist" if has_timestamp else "No timestamped runtime lines found",
        ),
        "turn_count": metric(
            "derivable" if has_turn_id else "unavailable",
            source=str(log_source),
            detail="turn.id markers exist in runtime logs" if has_turn_id else "No turn.id markers found",
        ),
        "token_count": metric(
            "unavailable",
            source=str(log_source),
            detail=(
                "Token-like strings appeared only in ambiguous runtime text; no stable default log signal proven"
                if has_token_signal
                else "Default inspected Codex logs did not expose stable token usage fields"
            ),
        ),
        "tool_call_count": metric(
            "derivable" if has_tool_call else "unavailable",
            source=str(log_source),
            detail="ToolCall lines exist in runtime logs" if has_tool_call else "No ToolCall lines found",
        ),
    }
    return result


def build_payload(*, home: Path, repo_root: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "home": str(home),
        "repo_root": str(repo_root),
        "hosts": {
            "claude": probe_claude(home, repo_root),
            "codex": probe_codex(home),
        },
    }
