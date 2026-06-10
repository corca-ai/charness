"""Audit a Claude Code project session JSONL directly.

The host-log probe previously had no Claude-format session auditor at all, so
on a Claude-host run the rendered measured block fell back to the newest Codex
rollout — a stale cross-host source presented as the run's cost. This module
reads ONE named Claude project session file (``~/.claude/projects/<dir>/<id>.jsonl``),
tolerates malformed lines with a counted warning, and emits the same
summary shape the probe records for Codex sessions (measured counts, proxy
signals, a window filter) so a Claude-host run can carry a scoped measured
block with named provenance.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from scripts.codex_session_audit_lib import command_family
from scripts.codex_session_jsonl_audit import (
    filter_records_for_window,
    iter_records,
    last_event_at,
    malformed_warnings,
    repeated_broad_gates,
    repeated_vcs_commands,
)

SCHEMA_VERSION = 1
_PATCH_TOOL_NAMES = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
_SUBAGENT_TOOL_NAMES = frozenset({"Task", "Agent"})
_MCP_TOOL_PREFIX = "mcp__"


def _iter_tool_uses(record: dict[str, Any]) -> list[dict[str, Any]]:
    message = record.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    return [item for item in content if isinstance(item, dict) and item.get("type") == "tool_use"]


def _has_usage_snapshot(record: dict[str, Any]) -> bool:
    message = record.get("message")
    return isinstance(message, dict) and isinstance(message.get("usage"), dict)


def _is_compaction(record: dict[str, Any]) -> bool:
    return bool(record.get("isCompactSummary")) or record.get("type") == "summary"


def _tool_use_family(name: str, item: dict[str, Any]) -> str:
    if name != "Bash":
        return name
    arguments = item.get("input")
    command = arguments.get("command") if isinstance(arguments, dict) else None
    # command_family splits shell text the same way the Codex auditor does, so
    # proxy families stay comparable across hosts.
    return command_family("exec_command", command if isinstance(command, str) else "")


def audit_session_jsonl(
    path: Path,
    *,
    top: int = 20,
    started_at: str | None = None,
    completed_at: str | None = None,
) -> dict[str, Any]:
    records, malformed = iter_records(path)
    records, window_filter = filter_records_for_window(records, started_at, completed_at)

    function_names: Counter[str] = Counter()
    custom_tool_names: Counter[str] = Counter()
    families: Counter[str] = Counter()
    token_snapshots = 0
    patch_applications = 0
    compactions = 0
    subagent_spawns = 0

    for record in records:
        if _has_usage_snapshot(record):
            token_snapshots += 1
        if _is_compaction(record):
            compactions += 1
        for item in _iter_tool_uses(record):
            name = str(item.get("name") or "unknown")
            families[_tool_use_family(name, item)] += 1
            if name in _SUBAGENT_TOOL_NAMES:
                subagent_spawns += 1
            if name in _PATCH_TOOL_NAMES:
                patch_applications += 1
            if name.startswith(_MCP_TOOL_PREFIX):
                custom_tool_names[name] += 1
            else:
                function_names[name] += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "source": {"kind": "session-jsonl", "host": "claude", "path": str(path)},
        "warnings": malformed_warnings(malformed),
        "notes": [
            "patch_applications counts Edit/Write/MultiEdit/NotebookEdit tool_use items; they also appear in function_calls, so the two fields overlap rather than add.",
            "subagent wait/close are not represented in Claude session logs; only spawns are counted.",
        ],
        "measured": {
            "total_events": len(records),
            "token_count_snapshots": token_snapshots,
            "function_calls": sum(function_names.values()),
            "function_call_names": dict(function_names.most_common(top)),
            "custom_tool_calls": sum(custom_tool_names.values()),
            "custom_tool_names": dict(custom_tool_names.most_common(top)),
            "patch_applications": patch_applications,
            "context_compactions": compactions,
            "subagent": {"spawn": subagent_spawns},
        },
        "proxy": {
            "note": "Activity proxies derived from command shape, not measured cost.",
            "repeated_broad_gates": repeated_broad_gates(families),
            "repeated_vcs_commands": repeated_vcs_commands(families),
        },
        "window_filter": window_filter,
        "last_event_at": last_event_at(records),
    }
