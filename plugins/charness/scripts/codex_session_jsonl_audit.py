"""Audit a Codex session rollout JSONL directly.

The sqlite/tui audit path in ``codex_session_audit_lib`` can see only a tail of a
long session, which undercounts work. When a session id or rollout file is
supplied, this module reads the full rollout JSONL instead, tolerates malformed
lines with a counted warning, and separates measured counts, point-in-time
snapshots, and proxy signals so the retro does not present a snapshot as a total.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.codex_session_audit_lib import classify_phase, command_family

SCHEMA_VERSION = 1
_SUBAGENT_TOKENS = ("spawn_agent", "wait_agent", "close_agent", "multi_agent")
_GATE_REPEAT_THRESHOLD = 3
_VCS_REPEAT_THRESHOLD = 3


def resolve_session_path(home: Path, *, session_id: str | None, session_file: str | None) -> Path | None:
    """Resolve a rollout JSONL from an explicit file or a session-id substring."""
    if session_file:
        candidate = Path(session_file).expanduser()
        return candidate if candidate.is_file() else None
    sessions_root = home / ".codex" / "sessions"
    if not sessions_root.is_dir():
        return None
    matches = sorted(sessions_root.glob("**/rollout-*.jsonl"))
    if session_id:
        matches = [path for path in matches if session_id in path.name]
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def _exec_command_text(payload: dict[str, Any]) -> str:
    raw = payload.get("arguments")
    if not isinstance(raw, str):
        return ""
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return ""
    cmd = parsed.get("cmd") if isinstance(parsed, dict) else None
    if isinstance(cmd, list):
        return " ".join(str(part) for part in cmd)
    return cmd if isinstance(cmd, str) else ""


def _iter_records(path: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except ValueError:
                malformed += 1
                continue
            if isinstance(parsed, dict):
                records.append(parsed)
            else:
                malformed += 1
    return records, malformed


def _payload(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else record


def audit_session_jsonl(path: Path, *, top: int = 20) -> dict[str, Any]:
    records, malformed = _iter_records(path)

    event_types: Counter[str] = Counter()
    subtypes: Counter[str] = Counter()
    function_names: Counter[str] = Counter()
    custom_tool_names: Counter[str] = Counter()
    families: Counter[str] = Counter()
    phases: Counter[str] = Counter()
    subagent = Counter({"spawn": 0, "wait": 0, "close": 0})
    last_token_snapshot: dict[str, Any] | None = None

    for record in records:
        top_type = str(record.get("type") or "unknown")
        event_types[top_type] += 1
        payload = _payload(record)
        subtype = payload.get("type") if isinstance(payload, dict) else None
        if isinstance(subtype, str):
            subtypes[f"{top_type}/{subtype}"] += 1
        if subtype == "function_call":
            name = str(payload.get("name") or "unknown")
            function_names[name] += 1
            command = _exec_command_text(payload)
            families[command_family(name, command)] += 1
            phases[classify_phase(name, command)] += 1
            lowered = f"{name} {command}".lower()
            for token, key in (("spawn_agent", "spawn"), ("wait_agent", "wait"), ("close_agent", "close")):
                if token in lowered:
                    subagent[key] += 1
        elif subtype == "custom_tool_call":
            custom_tool_names[str(payload.get("name") or "unknown")] += 1
        elif subtype == "token_count":
            last_token_snapshot = payload.get("rate_limits") if isinstance(payload.get("rate_limits"), dict) else last_token_snapshot

    measured = {
        "total_events": len(records),
        "event_types": dict(event_types.most_common()),
        "subtypes": dict(subtypes.most_common()),
        "function_calls": sum(function_names.values()),
        "function_call_names": dict(function_names.most_common(top)),
        "custom_tool_calls": sum(custom_tool_names.values()),
        "custom_tool_names": dict(custom_tool_names.most_common(top)),
        "patch_applications": subtypes.get("event_msg/patch_apply_end", 0),
        "task_completions": subtypes.get("event_msg/task_complete", 0),
        "context_compactions": subtypes.get("event_msg/context_compacted", 0) + event_types.get("compacted", 0),
        "token_count_snapshots": subtypes.get("event_msg/token_count", 0),
        "goal_or_plan_updates": function_names.get("update_plan", 0),
        "subagent": dict(subagent),
    }
    snapshots = {
        "note": "Point-in-time values; not cumulative totals.",
        "last_rate_limits": last_token_snapshot,
    }
    proxy = {
        "note": "Activity proxies derived from command shape, not measured cost.",
        "command_families": dict(families.most_common(top)),
        "phases": dict(phases.most_common()),
        "repeated_broad_gates": _repeated_broad_gates(families),
        "repeated_vcs_commands": _repeated_vcs_commands(families),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "source": {"kind": "session-jsonl", "path": str(path)},
        "warnings": _warnings(malformed),
        "notes": [
            "patch_applications counts patch_apply_end events; those patches also appear in custom_tool_calls as apply_patch, so the two fields overlap rather than add.",
        ],
        "measured": measured,
        "snapshots": snapshots,
        "proxy": proxy,
    }


def _repeated_broad_gates(families: Counter[str]) -> dict[str, int]:
    gate_tokens = ("pytest", "ruff", "mypy", "pyright", "eslint", "tsc", "check", "build", "test", "lint", "make")
    return {
        family: count
        for family, count in families.items()
        if count >= _GATE_REPEAT_THRESHOLD and any(token in family.lower() for token in gate_tokens)
    }


def _repeated_vcs_commands(families: Counter[str]) -> dict[str, int]:
    return {
        family: count
        for family, count in families.items()
        if count >= _VCS_REPEAT_THRESHOLD and family.startswith("git ")
    }


def _warnings(malformed: int) -> list[str]:
    if malformed:
        return [f"{malformed} malformed JSONL line(s) skipped"]
    return []


def render_markdown(payload: dict[str, Any]) -> str:
    measured = payload["measured"]
    lines = [
        f"# Codex Session Audit ({payload['source']['path']})",
        "",
        "## Measured",
        f"- total events: {measured['total_events']}",
        f"- function calls: {measured['function_calls']}",
        f"- custom tool calls: {measured['custom_tool_calls']}",
        f"- patch applications: {measured['patch_applications']}",
        f"- task completions: {measured['task_completions']}",
        f"- context compactions: {measured['context_compactions']}",
        f"- goal/plan updates: {measured['goal_or_plan_updates']}",
        f"- subagent spawn/wait/close: {measured['subagent']}",
        "",
        "## Proxy",
        f"- repeated broad gates: {payload['proxy']['repeated_broad_gates'] or 'none'}",
        f"- repeated vcs commands: {payload['proxy']['repeated_vcs_commands'] or 'none'}",
    ]
    if payload["warnings"]:
        lines += ["", "## Warnings", *(f"- {warning}" for warning in payload["warnings"])]
    return "\n".join(lines) + "\n"
