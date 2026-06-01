from __future__ import annotations

import json
import re
import shlex
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts import codex_session_jsonl_audit

ISO_TS_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
GOAL_WINDOW_LINE = re.compile(r"^Host metric window:\s*(?P<body>.+)$", re.MULTILINE)


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


def _pick_codex_session_log(codex_root: Path) -> Path | None:
    sessions_root = codex_root / "sessions"
    if not sessions_root.is_dir():
        return None
    matches = sorted(sessions_root.glob("**/rollout-*.jsonl"))
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def _codex_session_audit_summary(path: Path, goal_window: dict[str, Any] | None = None) -> dict[str, Any]:
    audit = codex_session_jsonl_audit.audit_session_jsonl(
        path,
        top=20,
        started_at=(goal_window or {}).get("started_at"),
        completed_at=(goal_window or {}).get("completed_at"),
    )
    measured = audit.get("measured") if isinstance(audit.get("measured"), dict) else {}
    proxy = audit.get("proxy") if isinstance(audit.get("proxy"), dict) else {}
    return {
        "source": audit.get("source", {"kind": "session-jsonl", "path": str(path)}),
        "warnings": audit.get("warnings", []),
        "measured": {
            "total_events": measured.get("total_events", 0),
            "token_count_snapshots": measured.get("token_count_snapshots", 0),
            "context_compactions": measured.get("context_compactions", 0),
            "function_calls": measured.get("function_calls", 0),
            "custom_tool_calls": measured.get("custom_tool_calls", 0),
            "patch_applications": measured.get("patch_applications", 0),
            "subagent": measured.get("subagent", {}),
        },
        "proxy": {
            "repeated_broad_gates": proxy.get("repeated_broad_gates", {}),
            "repeated_vcs_commands": proxy.get("repeated_vcs_commands", {}),
        },
        "notes": audit.get("notes", []),
        "window_filter": audit.get("window_filter", {}),
    }


def _codex_metrics_from_signals(
    *,
    log_source: Path,
    session_log: Path | None,
    has_timestamp: bool,
    has_turn_id: bool,
    has_tool_call: bool,
    has_token_signal: bool,
    session_measured: dict[str, Any],
) -> dict[str, dict[str, str]]:
    session_token_snapshots = int(session_measured.get("token_count_snapshots") or 0)
    session_tool_calls = int(session_measured.get("function_calls") or 0) + int(
        session_measured.get("custom_tool_calls") or 0
    )
    token_source = str(session_log) if session_log is not None else str(log_source)
    tool_source = str(session_log) if session_tool_calls else str(log_source)
    return {
        "duration": metric(
            "derivable" if has_timestamp else "unavailable",
            source=str(log_source) if log_source.exists() else None,
            detail="timestamped runtime log lines exist" if has_timestamp else "No timestamped runtime lines found",
        ),
        "turn_count": metric(
            "derivable" if has_turn_id else "unavailable",
            source=str(log_source) if log_source.exists() else None,
            detail="turn.id markers exist in runtime logs" if has_turn_id else "No turn.id markers found",
        ),
        "token_count": metric(
            "available" if session_token_snapshots else "unavailable",
            source=token_source,
            detail=_codex_token_detail(session_token_snapshots, has_token_signal),
        ),
        "tool_call_count": metric(
            "derivable" if has_tool_call or session_tool_calls else "unavailable",
            source=tool_source,
            detail=_codex_tool_detail(session_tool_calls, has_tool_call),
        ),
    }


def _codex_token_detail(session_token_snapshots: int, has_token_signal: bool) -> str:
    if session_token_snapshots:
        return f"Codex session JSONL exposes {session_token_snapshots} token_count snapshot(s)"
    if has_token_signal:
        return "Token-like strings appeared only in ambiguous runtime text; no stable session JSONL token_count events found"
    return "Default inspected Codex logs did not expose stable token usage fields"


def _codex_tool_detail(session_tool_calls: int, has_tool_call: bool) -> str:
    if session_tool_calls:
        return f"Codex session JSONL exposes {session_tool_calls} function/custom tool call(s)"
    return "ToolCall lines exist in runtime logs" if has_tool_call else "No ToolCall lines found"


def probe_codex(home: Path, goal_window: dict[str, Any] | None = None) -> dict[str, Any]:
    codex_root = home / ".codex"
    history_path = codex_root / "history.jsonl"
    tui_log = codex_root / "log" / "codex-tui.log"
    sqlite_log = codex_root / "logs_2.sqlite"
    session_log = _goal_window_session_path(goal_window) or _pick_codex_session_log(codex_root)

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

    if not tui_log.exists() and not sqlite_log.exists() and session_log is None:
        result["metrics"] = {
            "duration": metric("unavailable", detail="No Codex runtime logs found"),
            "turn_count": metric("unavailable", detail="No Codex runtime logs found"),
            "token_count": metric("unavailable", detail="No Codex runtime logs found"),
            "tool_call_count": metric("unavailable", detail="No Codex runtime logs found"),
        }
        return result

    log_source = tui_log if tui_log.exists() else sqlite_log
    text = _read_text(log_source) if log_source.exists() and log_source.suffix != ".sqlite" else (
        _read_codex_sqlite_log(log_source) if log_source.exists() else ""
    )
    non_toolcall_lines = _codex_non_toolcall_lines(text)
    has_timestamp = any(ISO_TS_PREFIX.match(line) for line in non_toolcall_lines)
    has_turn_id = any("turn.id=" in line for line in non_toolcall_lines)
    has_tool_call = "ToolCall:" in text
    has_token_signal = any(
        marker in line
        for line in non_toolcall_lines
        for marker in ("tokenUsage/updated", "ThreadTokenUsageUpdated", "input_tokens", "output_tokens")
    )

    if log_source.exists():
        result["sources"].append(
            {
                "kind": "tui-log" if log_source == tui_log else "sqlite-log",
                "path": str(log_source),
                "status": "used",
            }
        )
    if sqlite_log.exists():
        result["sources"].append({"kind": "sqlite-log", "path": str(sqlite_log), "status": "available"})
    session_summary = _codex_session_audit_summary(session_log) if session_log is not None else None
    if session_summary is not None:
        result["sources"].append({"kind": "session-jsonl", "path": str(session_log), "status": "used"})
        result["session_audit"] = session_summary
        if goal_window and goal_window.get("status") == "parsed":
            result["goal_window_audit"] = _codex_session_audit_summary(session_log, goal_window)
    session_measured = session_summary.get("measured", {}) if isinstance(session_summary, dict) else {}
    result["metrics"] = _codex_metrics_from_signals(
        log_source=log_source,
        session_log=session_log,
        has_timestamp=has_timestamp,
        has_turn_id=has_turn_id,
        has_tool_call=has_tool_call,
        has_token_signal=has_token_signal,
        session_measured=session_measured,
    )
    return result


def parse_goal_metric_window(repo_root: Path, goal_path: Path | None) -> dict[str, Any]:
    if goal_path is None:
        return {"status": "not_requested"}
    path = goal_path.expanduser()
    if not path.is_absolute():
        path = repo_root / path
    if not path.is_file():
        return {"status": "missing", "path": str(path)}
    match = GOAL_WINDOW_LINE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        return {"status": "absent", "path": str(path)}
    fields = _parse_window_fields(match.group("body"))
    issues = [key for key in ("started_at", "completed_at", "codex_session_file") if key not in fields]
    if issues:
        return {"status": "invalid", "path": str(path), "missing": issues, "raw": match.group("body")}
    invalid_timestamps = [key for key in ("started_at", "completed_at") if _parse_window_ts(fields[key]) is None]
    if invalid_timestamps:
        return {
            "status": "invalid",
            "path": str(path),
            "invalid_timestamps": invalid_timestamps,
            "raw": match.group("body"),
        }
    session_file = _resolve_window_path(repo_root, fields["codex_session_file"])
    if not session_file.is_file():
        return {
            "status": "invalid",
            "path": str(path),
            "missing_session_file": str(session_file),
            "raw": match.group("body"),
        }
    fields["codex_session_file"] = str(session_file)
    return {"status": "parsed", "path": str(path), **fields}


def _parse_window_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in shlex.split(body):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def _resolve_window_path(repo_root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else repo_root / path


def _parse_window_ts(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _goal_window_session_path(goal_window: dict[str, Any] | None) -> Path | None:
    if not goal_window or goal_window.get("status") != "parsed":
        return None
    value = goal_window.get("codex_session_file")
    if not isinstance(value, str):
        return None
    path = Path(value)
    return path if path.is_file() else None


def build_payload(*, home: Path, repo_root: Path, goal_path: Path | None = None) -> dict[str, Any]:
    goal_window = parse_goal_metric_window(repo_root, goal_path)
    return {
        "schema_version": 1,
        "home": str(home),
        "repo_root": str(repo_root),
        "goal_metric_window": goal_window,
        "hosts": {
            "claude": probe_claude(home, repo_root),
            "codex": probe_codex(home, goal_window),
        },
    }
