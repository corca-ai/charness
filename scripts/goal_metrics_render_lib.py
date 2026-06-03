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
cannot re-advertise ``gh``/``ceal github``/etc. command strings.
"""
from __future__ import annotations

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


def _select_codex_audit(codex: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Prefer the goal-window-scoped audit; fall back to the thread-wide audit."""
    if isinstance(codex.get("goal_window_audit"), dict):
        return codex["goal_window_audit"], "goal-window"
    if isinstance(codex.get("session_audit"), dict):
        return codex["session_audit"], "thread-wide"
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
    codex = hosts.get("codex") or {}
    audit, scope = _select_codex_audit(codex)
    if audit is None:
        lines += [
            "",
            "### Measured (Codex session)",
            "- unavailable: no Codex session audit for this run",
        ]
    else:
        measured = audit.get("measured") or {}
        proxy = audit.get("proxy") or {}
        window_filter = audit.get("window_filter") or {}
        lines += [
            "",
            f"### Measured ({scope} scope)",
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
