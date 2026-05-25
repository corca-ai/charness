from __future__ import annotations

import json
import re
import shlex
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.codex_session_audit_sources import choose_source, source_status, tail_text_lines
from scripts.codex_session_audit_tokens import cost_signal_status, token_summary

TIMESTAMP_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
THREAD_RE = re.compile(r"\b(?:thread(?:\.id|_id)|conversation\.id)=(?:\"(?P<q>[0-9A-Za-z_-]+)\"|(?P<u>[0-9A-Za-z_-]+))")
TURN_RE = re.compile(r"\bturn(?:\.id|_id)=(?:\"(?P<q>[0-9A-Za-z_-]+)\"|(?P<u>[0-9A-Za-z_-]+))")
TOOL_RE = re.compile(r"ToolCall:\s+(?P<tool>[A-Za-z0-9_.-]+)\s*(?P<payload>.*)$", re.DOTALL)


@dataclass(frozen=True)
class AuditOptions:
    repo_root: Path
    home: Path
    source: str = "auto"
    thread_ids: tuple[str, ...] = ()
    list_threads: bool = False
    since: str | None = None
    top: int = 20
    max_auto_threads: int = 12
    max_command_len: int = 160
    max_tui_lines: int = 5000
    include_command_snippets: bool = False


@dataclass(frozen=True)
class LogLine:
    index: int
    ts: str | None
    text: str
    thread_id: str | None = None
    estimated_bytes: int | None = None


@dataclass
class ThreadStats:
    thread_id: str
    first_ts: str | None = None
    last_ts: str | None = None
    line_count: int = 0
    tool_call_count: int = 0
    repo_hits: int = 0


def audit(options: AuditOptions) -> dict[str, Any]:
    source_kind, source_path = choose_source(options.home, options.source)
    since = parse_since(options.since)
    requested = list(options.thread_ids)
    stats = build_stats(source_kind, source_path, options.repo_root, since, options.max_tui_lines)
    selected, excluded = select_threads(stats, requested, options.max_auto_threads)
    if options.list_threads:
        return thread_list_payload(stats, source_kind, source_path, options.top)
    lines = read_selected_lines(source_kind, source_path, since, selected, options.max_tui_lines)
    if requested:
        selected_set = set(selected)
        lines = [line for line in lines if selected_set & line_thread_ids(line)]
    return build_report(lines, stats, selected, excluded, requested, source_kind, source_path, options)


def parse_since(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = parse_ts(value)
    if parsed is None:
        raise ValueError(f"Invalid --since timestamp: {value}")
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def thread_ids_from_text(text: str) -> set[str]:
    return {match.group("q") or match.group("u") for match in THREAD_RE.finditer(text)}


def turn_ids_from_text(text: str) -> set[str]:
    return {match.group("q") or match.group("u") for match in TURN_RE.finditer(text)}


def line_thread_ids(line: LogLine) -> set[str]:
    ids = thread_ids_from_text(line.text)
    if line.thread_id:
        ids.add(line.thread_id)
    return ids


def build_stats(source_kind: str, source_path: Path, repo_root: Path, since: datetime | None, max_tui_lines: int) -> dict[str, ThreadStats]:
    if source_kind == "sqlite":
        return sqlite_thread_stats(source_path, repo_root, since)
    return line_thread_stats(read_tui(source_path, since, max_tui_lines), repo_root)


def sqlite_thread_stats(path: Path, repo_root: Path, since: datetime | None) -> dict[str, ThreadStats]:
    if not path.exists():
        return {}
    rows = sqlite_rows(path, since=since, thread_filter=None, bodies=False)
    repo_text = repo_root.resolve().as_posix()
    stats: dict[str, ThreadStats] = {}
    for row in rows:
        thread_id = row["thread_id"]
        if not thread_id:
            continue
        item = stats.setdefault(thread_id, ThreadStats(thread_id=thread_id))
        item.line_count += 1
        item.tool_call_count += 1 if "ToolCall:" in row["body"] else 0
        item.repo_hits += 1 if repo_text in row["body"] else 0
        item.first_ts = item.first_ts or row["ts"]
        item.last_ts = row["ts"] or item.last_ts
    return stats


def line_thread_stats(lines: list[LogLine], repo_root: Path) -> dict[str, ThreadStats]:
    repo_text = repo_root.resolve().as_posix()
    stats: dict[str, ThreadStats] = {}
    for line in lines:
        for thread_id in line_thread_ids(line):
            item = stats.setdefault(thread_id, ThreadStats(thread_id=thread_id))
            item.line_count += 1
            item.tool_call_count += 1 if "ToolCall:" in line.text else 0
            item.repo_hits += 1 if repo_text in line.text else 0
            item.first_ts = item.first_ts or line.ts
            item.last_ts = line.ts or item.last_ts
    return stats


def sqlite_rows(path: Path, *, since: datetime | None, thread_filter: set[str] | None, bodies: bool) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    connection = sqlite3.connect(path)
    try:
        where = "feedback_log_body is not null"
        params: list[Any] = []
        if thread_filter:
            where += f" and thread_id in ({','.join('?' for _ in thread_filter)})"
            params.extend(sorted(thread_filter))
        rows = connection.execute(
            "select id, ts, ts_nanos, feedback_log_body, estimated_bytes, thread_id "
            f"from logs where {where} order by id",
            tuple(params),
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        connection.close()
    result = []
    for row_id, ts_sec, ts_nanos, body, estimated_bytes, thread_id in rows:
        if not isinstance(body, str):
            continue
        try:
            ts_dt = datetime.fromtimestamp(float(ts_sec) + float(ts_nanos) / 1_000_000_000, tz=timezone.utc)
        except (TypeError, ValueError, OverflowError):
            continue
        if since is not None and ts_dt < since:
            continue
        result.append(
            {
                "id": int(row_id),
                "ts": ts_dt.isoformat().replace("+00:00", "Z"),
                "body": body if bodies else body[:1000],
                "estimated_bytes": int(estimated_bytes) if estimated_bytes is not None else None,
                "thread_id": str(thread_id) if thread_id else None,
            }
        )
    return result


def read_selected_lines(source_kind: str, source_path: Path, since: datetime | None, selected: list[str], max_tui_lines: int) -> list[LogLine]:
    if source_kind == "sqlite":
        selected_filter = set(selected) if selected else None
        return [
            LogLine(item["id"], item["ts"], item["body"].replace("\n", "\\n"), item["thread_id"], item["estimated_bytes"])
            for item in sqlite_rows(source_path, since=since, thread_filter=selected_filter, bodies=True)
        ]
    lines = read_tui(source_path, since, max_tui_lines)
    if not selected:
        return lines
    selected_set = set(selected)
    return [line for line in lines if selected_set & line_thread_ids(line)]


def read_tui(path: Path, since: datetime | None, max_lines: int) -> list[LogLine]:
    if not path.exists():
        return []
    result = []
    for index, text in tail_text_lines(path, max_lines):
        ts_text = (TIMESTAMP_RE.match(text) or {}).group("ts") if TIMESTAMP_RE.match(text) else None
        ts = parse_ts(ts_text)
        if since is not None and ts is not None and ts < since:
            continue
        result.append(LogLine(index=index, ts=ts_text, text=text))
    return result


def select_threads(stats: dict[str, ThreadStats], requested: list[str], max_auto_threads: int) -> tuple[list[str], list[str]]:
    if requested:
        selected = list(dict.fromkeys(requested))
        excluded = sorted(thread_id for thread_id in stats if thread_id not in selected)
        return selected, excluded
    candidates = [item for item in stats.values() if item.repo_hits > 0] or list(stats.values())
    candidates.sort(key=lambda item: (item.last_ts or "", item.tool_call_count), reverse=True)
    if max_auto_threads > 0:
        candidates = candidates[:max_auto_threads]
    selected = [item.thread_id for item in candidates]
    return selected, sorted(thread_id for thread_id in stats if thread_id not in set(selected))


def build_report(lines: list[LogLine], stats: dict[str, ThreadStats], selected: list[str], excluded: list[str], requested: list[str], source_kind: str, source_path: Path, options: AuditOptions) -> dict[str, Any]:
    missing = [thread_id for thread_id in requested if thread_id not in stats]
    tool_calls = [parsed for line in lines if (parsed := parse_tool_call(line, options))]
    phases = Counter(item["phase"] for item in tool_calls)
    families = Counter(item["family"] for item in tool_calls)
    token_observations = token_summary(lines, source_kind, str(source_path))
    status = report_status(source_kind, source_path, requested, missing)
    confidence = "high" if requested and not missing else "low"
    waste = [] if status != "ok" else waste_candidates(phases, families, tool_calls, requested)
    signals = cost_signal_status(token_observations)
    if status != "ok":
        signals["measured"] = []
        signals["proxy"] = []
    return {
        "schema_version": 1,
        "status": status,
        "source": {"kind": source_kind, "path": str(source_path), "status": source_status(source_kind, source_path)},
        "selection": {
            "thread_ids": selected,
            "thread_ids_requested": requested,
            "missing_thread_ids": missing,
            "excluded_thread_count": len(excluded),
            "selection_confidence": confidence,
            "selection_notes": selection_notes(requested, missing),
            "since": options.since,
            "max_auto_threads": options.max_auto_threads,
        },
        "window": window(lines),
        "counts": {"log_lines": len(lines), "turns_with_ids": count_turns(lines), "tool_calls": len(tool_calls)},
        "cost_signal_status": signals,
        "token_observations": token_observations,
        "phase_counts": dict(phases.most_common()),
        "repeated_command_families": [{"family": key, "count": value} for key, value in families.most_common(options.top) if value > 1],
        "largest_proxy_cost_tool_calls": largest_proxy_calls(tool_calls, options.top),
        "largest_requested_max_output_tokens": max_output_requests(tool_calls, options.top),
        "waste_candidates": waste,
        "suggested_segments_to_inspect": suggest_segments(phases, families, tool_calls),
    }


def report_status(source_kind: str, source_path: Path, requested: list[str], missing: list[str]) -> str:
    if not source_path.exists():
        return "source_missing"
    if source_status(source_kind, source_path) == "unreadable":
        return "source_unreadable"
    if requested and len(missing) == len(requested):
        return "no_matching_threads"
    return "ok"


def selection_notes(requested: list[str], missing: list[str]) -> list[str]:
    notes = []
    if not requested:
        notes.append("Auto-selection is a bounded repo-hit heuristic. Use --thread-id or --since for session scope.")
    if missing:
        notes.append("Some requested thread ids were not found in the selected source.")
    return notes


def parse_tool_call(line: LogLine, options: AuditOptions) -> dict[str, Any] | None:
    match = TOOL_RE.search(line.text)
    if not match:
        return None
    tool = match.group("tool")
    parsed = parse_json_prefix(match.group("payload").strip())
    command = summarize_payload(tool, parsed, match.group("payload").strip())
    return {
        "line": line.index,
        "timestamp": line.ts,
        "tool": tool,
        "phase": classify_phase(tool, command),
        "family": command_family(tool, command),
        "command": truncate(command, options.max_command_len) if options.include_command_snippets else "",
        "command_snippet_included": options.include_command_snippets,
        "command_chars": len(command),
        "line_chars": len(line.text),
        "estimated_bytes": line.estimated_bytes,
        "requested_max_output_tokens": parsed.get("max_output_tokens") if isinstance(parsed, dict) else None,
    }


def parse_json_prefix(text: str) -> Any:
    if not text.startswith("{"):
        return None
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[: index + 1])
                except json.JSONDecodeError:
                    return None
    return None


def summarize_payload(tool: str, parsed: Any, payload: str) -> str:
    if isinstance(parsed, dict):
        if tool == "exec_command":
            return str(parsed.get("cmd") or "")
        if tool == "write_stdin":
            return f"write_stdin session_id={parsed.get('session_id')}"
        if "cmd" in parsed:
            return str(parsed.get("cmd") or "")
        return json.dumps(parsed, sort_keys=True)
    return payload.splitlines()[0] if payload else ""


def command_family(tool: str, command: str) -> str:
    if tool != "exec_command":
        return tool
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    if not parts:
        return "exec_command"
    if parts[:2] == ["uv", "run"] and len(parts) > 2:
        return "uv run " + parts[2]
    if parts[0] == "git" and len(parts) > 1:
        return "git " + parts[1]
    return parts[0]


def classify_phase(tool: str, command: str) -> str:
    lower = f"{tool} {command}".lower()
    if tool == "apply_patch" or "apply_patch" in lower:
        return "implementation"
    if any(token in lower for token in ("spawn_agent", "wait_agent", "multi_agent")):
        return "delegation"
    if any(token in lower for token in ("pytest", "ruff", "typecheck", "diff --check", "py_compile", " run build")):
        return "verification"
    if any(token in lower for token in ("git add", "git commit", "git status", "git log", "git rev-parse")):
        return "vcs"
    if any(token in lower for token in ("gh issue", "review", "critique", "triage", "plan")):
        return "triage"
    if any(token in lower for token in ("uvicorn", "vite", "tail -f", "nohup", "server")):
        return "runtime"
    if any(token in lower for token in (" sed ", " rg ", " find ", " nl ", " cat ", " ls ", "docs/handoff", "skill.md")):
        return "exploration"
    return "other"


def largest_proxy_calls(tool_calls: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    return sorted(tool_calls, key=lambda item: item["line_chars"], reverse=True)[:top]


def max_output_requests(tool_calls: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    items = [item for item in tool_calls if isinstance(item.get("requested_max_output_tokens"), int)]
    return sorted(items, key=lambda item: item["requested_max_output_tokens"], reverse=True)[:top]


def waste_candidates(phases: Counter[str], families: Counter[str], tool_calls: list[dict[str, Any]], requested: list[str]) -> list[dict[str, Any]]:
    candidates = []
    if not requested:
        candidates.append({"kind": "broad_auto_selection", "phase": "triage", "evidence": "No explicit --thread-id was provided."})
    for family, count in families.most_common(5):
        if count >= 3:
            phase = next((item["phase"] for item in tool_calls if item["family"] == family), "other")
            candidates.append({"kind": "repeated_command_family", "family": family, "count": count, "phase": phase})
    for phase, count in phases.most_common(3):
        if count >= 3:
            candidates.append({"kind": "phase_hotspot", "phase": phase, "count": count})
    return candidates[:10]


def suggest_segments(phases: Counter[str], families: Counter[str], tool_calls: list[dict[str, Any]]) -> list[str]:
    out = []
    if families:
        family, count = families.most_common(1)[0]
        out.append(f"Review repeated `{family}` calls ({count}) against the phase-aware triage lock.")
    if phases:
        phase, count = phases.most_common(1)[0]
        out.append(f"Inspect phase `{phase}` ({count} tool calls) before calling it waste.")
    if tool_calls:
        out.append(f"Inspect line {largest_proxy_calls(tool_calls, 1)[0]['line']} as the largest proxy-cost tool call.")
    return out


def count_turns(lines: list[LogLine]) -> int:
    return len({turn for line in lines for turn in turn_ids_from_text(line.text)})


def window(lines: list[LogLine]) -> dict[str, str | None]:
    timestamps = [line.ts for line in lines if line.ts]
    return {"first_ts": timestamps[0] if timestamps else None, "last_ts": timestamps[-1] if timestamps else None}


def thread_list_payload(stats: dict[str, ThreadStats], source_kind: str, source_path: Path, top: int) -> dict[str, Any]:
    items = sorted(stats.values(), key=lambda item: (item.last_ts or "", item.tool_call_count), reverse=True)
    return {"schema_version": 1, "source": {"kind": source_kind, "path": str(source_path)}, "threads": [item.__dict__ for item in items[:top]]}


def truncate(value: str, limit: int) -> str:
    text = " ".join(value.split())
    return text if len(text) <= limit else text[: max(0, limit - 3)] + "..."


def render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Codex Session Efficiency Audit", "", f"Source: `{payload['source']['kind']}`", f"Status: `{payload['status']}`"]
    lines.append(f"Selection Confidence: `{payload['selection']['selection_confidence']}`")
    lines.append(f"Tool Calls: {payload['counts']['tool_calls']}")
    lines.extend(["", "## Phase Counts"])
    lines.extend(f"- {phase}: {count}" for phase, count in payload.get("phase_counts", {}).items())
    lines.extend(["", "## Repeated Command Families"])
    lines.extend(f"- `{item['family']}`: {item['count']}" for item in payload.get("repeated_command_families", [])[:10])
    lines.extend(["", "## Waste Candidates"])
    lines.extend(f"- {item['kind']}: phase={item.get('phase', 'unknown')}" for item in payload.get("waste_candidates", [])[:10])
    lines.append("")
    lines.append("Note: this audit provides evidence pointers, not waste conclusions.")
    return "\n".join(lines)
