"""Render a standardized, provider-safe goal-closeout metrics block.

Issue #282: goal closeouts hand-assembled measured-vs-proxy metric narration and
sometimes recorded provider CLI verification *commands* as literal strings, which
a provider-boundary scanner correctly rejects. This module turns the existing
``probe_host_logs.py`` payload (see ``host_log_probe_lib.build_payload``) into one
standardized markdown block, and renders broad-gate verification as *results*
(gate id, outcome, exact-state ref) rather than re-embedding the command that
produced them.

Provider safety is structural, not a filter: this renderer only emits measured
counts, aggregated activity-proxy family labels, and result attestations. It has
no field that carries a provider CLI invocation, so a closeout built from it
cannot re-advertise ``gh``/``acme github``/etc. command strings.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# Whether the signals below describe one goal window or the whole thread. Surfacing
# this verbatim stops an ``absent`` window from silently masquerading as a goal total.
_WINDOW_STATUS_NOTE = {
    "parsed": "applied — signals below are scoped to the recorded goal window",
    "absent": (
        "ABSENT — no `Host metric window:` line; signals below are thread-wide "
        "pressure, not a per-goal total"
    ),
    "missing": "goal artifact not found; signals below are thread-wide pressure, not a per-goal total",
    "invalid": "invalid window line; signals below are thread-wide pressure, not a per-goal total",
    "not_requested": (
        "not requested (no --goal-path); signals below are thread-wide pressure, "
        "not a per-goal total"
    ),
}


def _fmt_counter(value: Any) -> str:
    if isinstance(value, dict) and value:
        return ", ".join(f"{key}={count}" for key, count in value.items())
    return "none"


def _audit_or_none(host: dict[str, Any], key: str) -> dict[str, Any] | None:
    audit = host.get(key)
    return audit if isinstance(audit, dict) else None


def _last_event_at(audit: dict[str, Any]) -> datetime | None:
    value = audit.get("last_event_at")
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _select_measured_audit(hosts: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Pick the measured-block audit: goal-window scope first, then freshest session.

    A goal-window audit exists for at most one host (the window line names one
    session file). For the thread-wide fallback, the most recently active
    session wins (`last_event_at`), so a stale cross-host rollout is never
    presented as the run's measured block; a Codex-only host is unchanged.
    """
    codex = hosts.get("codex") or {}
    claude = hosts.get("claude") or {}
    if (audit := _audit_or_none(codex, "goal_window_audit")) is not None:
        return audit, "goal-window"
    if (audit := _audit_or_none(claude, "goal_window_audit")) is not None:
        return audit, "goal-window, claude session"
    codex_audit = _audit_or_none(codex, "session_audit")
    claude_audit = _audit_or_none(claude, "session_audit")
    if codex_audit is not None and claude_audit is not None:
        codex_ts = _last_event_at(codex_audit)
        claude_ts = _last_event_at(claude_audit)
        # Chronological compare (an undated audit loses); ties keep codex so a
        # codex-only host's rendering stays byte-stable.
        if claude_ts is not None and (codex_ts is None or claude_ts > codex_ts):
            return claude_audit, "thread-wide, claude session"
        return codex_audit, "thread-wide"
    if codex_audit is not None:
        return codex_audit, "thread-wide"
    if claude_audit is not None:
        return claude_audit, "thread-wide, claude session"
    return None, ""


def _safe_field(value: Any) -> str:
    """Collapse a result-attestation field to a single safe line.

    Attestations carry results, never commands, so newlines (which a pasted
    command block would introduce) are flattened rather than preserved.
    """
    return " ".join(str(value).split()) or "—"


def render_broad_gate_attestation(attestations: list[dict[str, Any]]) -> str:
    """Render exact-state broad-gate verification as results, not commands.

    Each attestation is ``{"gate": <id>, "outcome": <pass|fail|...>,
    "state_ref": <sha|tree-clean|...>}``. The structure deliberately has no
    ``command`` field: a closeout records *that a gate passed at an exact state*,
    not the provider/CLI invocation that ran it. This is the portable broad-gate
    attestation contract (issue #282 criterion 4); a host adapter supplies the
    exact-state ref it can prove (e.g. ``git rev-parse HEAD`` with a clean tree).
    """
    lines = ["### Broad-gate attestation (results, not commands)"]
    if not attestations:
        lines.append("- none recorded")
        return "\n".join(lines) + "\n"
    for attestation in attestations:
        gate = _safe_field(attestation.get("gate", ""))
        outcome = _safe_field(attestation.get("outcome", ""))
        state_ref = _safe_field(attestation.get("state_ref", ""))
        lines.append(f"- {gate}: {outcome} @ {state_ref}")
    return "\n".join(lines) + "\n"


def render_goal_metrics_block(
    payload: dict[str, Any],
    *,
    attestations: list[dict[str, Any]] | None = None,
) -> str:
    """Render the standardized measured-vs-proxy closeout block from a probe payload."""
    window = payload.get("goal_metric_window") or {}
    status = window.get("status", "not_requested")
    lines = [
        "## Goal Closeout Metrics",
        "",
        f"- Goal metric window: {status} — {_WINDOW_STATUS_NOTE.get(status, status)}",
    ]
    if status == "parsed":
        lines.append(f"  - window: {window.get('started_at')} -> {window.get('completed_at')}")

    hosts = payload.get("hosts") or {}
    audit, scope = _select_measured_audit(hosts)
    if audit is None:
        lines += [
            "",
            "### Measured (no session audit)",
            "- unavailable: no Codex or Claude session audit for this run",
        ]
    else:
        measured = audit.get("measured") or {}
        proxy = audit.get("proxy") or {}
        window_filter = audit.get("window_filter") or {}
        source = audit.get("source") or {}
        lines += ["", f"### Measured ({scope} scope)"]
        if source.get("host") == "claude":
            # Named provenance: a Claude-sourced measured block states the exact
            # session file it derives from. Codex-sourced output is unchanged.
            lines.append(f"- session: {_safe_field(source.get('path', ''))}")
        lines += [
            f"- token snapshots: {measured.get('token_count_snapshots', 0)} "
            "(point-in-time, not a cumulative total)",
            f"- function calls: {measured.get('function_calls', 0)}",
            f"- custom tool calls: {measured.get('custom_tool_calls', 0)}",
            f"- patch applications: {measured.get('patch_applications', 0)}",
            f"- context compactions: {measured.get('context_compactions', 0)}",
            f"- subagent spawn/wait/close: {_fmt_counter(measured.get('subagent'))}",
            "",
            "### Proxy (activity shape, not measured cost)",
            f"- repeated broad gates: {_fmt_counter(proxy.get('repeated_broad_gates'))}",
            f"- repeated VCS commands: {_fmt_counter(proxy.get('repeated_vcs_commands'))}",
        ]
        if window_filter:
            lines += [
                "",
                "### Window filter",
                f"- status: {window_filter.get('status')}; included "
                f"{window_filter.get('included_records')} of {window_filter.get('total_records')} records",
            ]

    claude = hosts.get("claude") or {}
    token_metric = (claude.get("metrics") or {}).get("token_count") or {}
    if token_metric:
        detail = token_metric.get("detail", "")
        suffix = f": {detail}" if detail else ""
        lines += [
            "",
            "### Token availability (Claude host)",
            f"- {token_metric.get('status', 'unavailable')}{suffix}",
        ]

    if attestations is not None:
        lines += ["", render_broad_gate_attestation(attestations).rstrip("\n")]

    return "\n".join(lines) + "\n"
