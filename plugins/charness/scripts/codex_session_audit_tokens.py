from __future__ import annotations

import re
from typing import Any

INT_FIELD_RE = re.compile(r"\b(?P<key>[A-Za-z_]+)=(?:Some\()?(?P<value>\d+)")
BOOL_FIELD_RE = re.compile(r"\b(?P<key>[A-Za-z_]+)=(?P<value>true|false)")
TOKEN_KEYS = (
    "input_token_count",
    "output_token_count",
    "cached_token_count",
    "reasoning_token_count",
    "tool_token_count",
)


def token_summary(lines: list[Any], source_kind: str, source_path: str) -> dict[str, Any]:
    if source_kind != "sqlite":
        return unavailable(source_path, "TUI logs do not expose stable token snapshots.")
    completed: list[dict[str, int]] = []
    snapshots = []
    for line in lines:
        ints = {match.group("key"): int(match.group("value")) for match in INT_FIELD_RE.finditer(line.text)}
        bools = {match.group("key"): match.group("value") == "true" for match in BOOL_FIELD_RE.finditer(line.text)}
        if "event.kind=response.completed" in line.text and "input_token_count" in ints:
            completed.append({key: ints.get(key, 0) for key in TOKEN_KEYS})
        if "post sampling token usage" in line.text and "total_usage_tokens" in ints:
            snapshots.append(snapshot_payload(line.ts, ints, bools))
    if not completed and not snapshots:
        return unavailable(source_path, "No stable Codex token snapshot fields found.")
    return {
        "status": "available",
        "signal_class": "snapshot",
        "source": source_path,
        "interpretation": "Token fields are runtime/context snapshots or event aggregates, not proven full-session totals.",
        "response_completed_aggregate": aggregate_tokens(completed),
        "latest_context_snapshots": snapshots[-10:],
    }


def snapshot_payload(ts: str | None, ints: dict[str, int], bools: dict[str, bool]) -> dict[str, Any]:
    return {
        "timestamp": ts,
        "total_usage_tokens": ints.get("total_usage_tokens"),
        "estimated_token_count": ints.get("estimated_token_count"),
        "auto_compact_scope_tokens": ints.get("auto_compact_scope_tokens"),
        "auto_compact_scope_limit": ints.get("auto_compact_scope_limit"),
        "full_context_window_limit_reached": bools.get("full_context_window_limit_reached"),
        "needs_follow_up": bools.get("needs_follow_up"),
    }


def unavailable(source_path: str, detail: str) -> dict[str, str]:
    return {"status": "unavailable", "signal_class": "unavailable", "source": source_path, "detail": detail}


def aggregate_tokens(items: list[dict[str, int]]) -> dict[str, int]:
    return {key: sum(item.get(key, 0) for item in items) for key in TOKEN_KEYS} | {"events": len(items)}


def cost_signal_status(token_observations: dict[str, Any]) -> dict[str, list[str]]:
    snapshot = ["sqlite_runtime_token_snapshots"] if token_observations.get("signal_class") == "snapshot" else []
    unavailable_signals = ["full_tool_output_bytes", "session_token_total"]
    if token_observations.get("status") != "available":
        unavailable_signals.append("codex_token_snapshots")
    return {
        "measured": ["tool_calls", "turns_with_ids"],
        "proxy": ["command_chars", "line_chars", "requested_max_output_tokens", "repeated_command_families"],
        "snapshot": snapshot,
        "unavailable": unavailable_signals,
    }
