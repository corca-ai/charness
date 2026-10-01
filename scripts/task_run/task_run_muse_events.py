"""Muse `--json` event consumers for task-run lanes (#886).

`muse exec --json` streams machine-readable JSONL on stdout: `run.output.delta`
events carry the agent's streamed text in order, `task.lifecycle.status`
events carry model-stream retry progress, and one terminal `run_terminal`
event carries the final report (or the failure reason). Without `--json` the
lane stdout stays empty until the run ends, so a timed-out lane receipted no
phases and its stderr retries preserved no cause.

Shapes below are measured against Muse binary `1.4.1-R4503.1`; every accessor
tolerates unknown envelopes so a newer binary degrades to unobserved fields,
never to a crash.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

#: Intermediate agent-text chunks, in stream order. One marker line may span
#: several chunks, so consumers concatenate before splitting into lines.
_DELTA_PAYLOAD_TYPE = "run.output.delta"

#: Model-stream progress, including `retry_scheduled` phases with
#: `external_attempt` facets (`attempt`, `max_attempts`, `error_kind`).
_STATUS_PAYLOAD_TYPE = "task.lifecycle.status"

#: Terminal envelope kinds; the payload's `kind` is `run_terminal`.
_TERMINAL_PAYLOAD_PREFIX = "run.terminal."

#: Legacy/non-JSON retry notice on stderr (`muse: ` prefix optional).
_RETRY_LINE_RE = re.compile(
    r"retrying\s+.+\s+in\s+\d+ms\s+\(attempt\s+(\d+)/(\d+)\)",
    re.IGNORECASE,
)

#: Terminal failure line on stderr, carrying the actionable cause.
_FAILED_LINE_RE = re.compile(r"^run ended with Failed:\s*(.+)$")


#: Envelope markers the diagnostics rollup selects before JSON parsing, so a
#: long lane's full events log scans in linear time without parsing noise.
_STATUS_MARKER = '"task.lifecycle.status"'
_TERMINAL_MARKER = '"run.terminal.'
_FAILED_TASK_MARKER = '"task.lifecycle.failed"'
_DELTA_MARKER = '"run.output.delta"'
_ENVELOPE_MARKER = '"payload_type"'


def _iter_muse_events(text: str, only: tuple[str, ...] = ()):
    """Yield `(payload_type, payload)` for each muse JSONL envelope in order.

    `only` prefilters raw lines by substring so the diagnostics rollup reads
    a full events log without parsing every envelope.
    """
    for line in text.splitlines():
        if only and not any(marker in line for marker in only):
            continue
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        # A `{`-starting line that parses is a JSON object by construction.
        payload_type = event.get("payload_type")
        payload = event.get("payload")
        if isinstance(payload_type, str) and isinstance(payload, Mapping):
            yield payload_type, payload


def has_muse_events(text: str) -> bool:
    """Whether the transcript holds any muse `--json` envelope."""
    return next(_iter_muse_events(text, only=(_ENVELOPE_MARKER,)), None) is not None


def accumulated_agent_text(text: str) -> str:
    """Ordered agent text concatenated from `run.output.delta` chunks.

    Streaming splits marker lines across chunks, so phase parsing reads this
    accumulation rather than any single chunk.
    """
    chunks: list[str] = []
    for payload_type, payload in _iter_muse_events(text, only=(_DELTA_MARKER,)):
        if payload_type != _DELTA_PAYLOAD_TYPE:
            continue
        chunk = payload.get("text")
        if isinstance(chunk, str) and chunk:
            chunks.append(chunk)
    return "".join(chunks)


def terminal_event(text: str) -> dict[str, Any] | None:
    """The last `run_terminal` payload, or None when the run never terminated."""
    terminal: dict[str, Any] | None = None
    for payload_type, payload in _iter_muse_events(text, only=(_TERMINAL_MARKER,)):
        if payload_type.startswith(_TERMINAL_PAYLOAD_PREFIX) and payload.get("kind") == "run_terminal":
            terminal = dict(payload)
    return terminal


def muse_stdout_report(text: str) -> str | None:
    """The terminal report text, separate from its JSONL transport.

    The completed terminal `text` wins; without it (timeout, kill, failure)
    the streamed delta accumulation is the partial report; None means the
    transcript holds no muse events at all and the caller must leave stdout
    untouched (plain-text lanes).
    """
    if not has_muse_events(text):
        return None
    terminal = terminal_event(text)
    if terminal is not None:
        report = terminal.get("text")
        if isinstance(report, str) and report.strip():
            return report
    return accumulated_agent_text(text)


def _external_attempt_facet(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    event = payload.get("event")
    details = event.get("details") if isinstance(event, Mapping) else None
    facets = details.get("facets") if isinstance(details, Mapping) else None
    if not isinstance(facets, list):
        return None
    for facet in facets:
        if isinstance(facet, Mapping) and facet.get("kind") == "external_attempt":
            return dict(facet)
    return None


def _failed_task_reason(text: str) -> str | None:
    """The `task.lifecycle.failed` reason, the structured failure cause."""
    reason: str | None = None
    for payload_type, payload in _iter_muse_events(text, only=(_FAILED_TASK_MARKER,)):
        if payload_type != "task.lifecycle.failed":
            continue
        event = payload.get("event")
        candidate = event.get("reason") if isinstance(event, Mapping) else None
        if isinstance(candidate, str) and candidate.strip():
            reason = candidate.strip()
    return reason


def _roll_up_status(events_text: str) -> dict[str, Any]:
    """Lane-cumulative retry progress from structured status events."""
    rollup: dict[str, Any] = {
        "retries": 0,
        "last_phase": None,
        "last_error_kind": None,
        "last_attempt": None,
        "last_max_attempts": None,
        "last_message": None,
        "from_events": False,
    }
    for payload_type, payload in _iter_muse_events(events_text, only=(_STATUS_MARKER,)):
        if payload_type != _STATUS_PAYLOAD_TYPE:
            continue
        rollup["from_events"] = True
        event = payload.get("event")
        if not isinstance(event, Mapping):
            continue
        details = event.get("details")
        phase = details.get("phase") if isinstance(details, Mapping) else None
        if isinstance(phase, str) and phase:
            rollup["last_phase"] = phase
            if phase == "retry_scheduled":
                rollup["retries"] += 1
        message = event.get("message")
        if isinstance(message, str) and message.strip():
            rollup["last_message"] = message.strip()[:300]
        _roll_up_attempt(rollup, payload, phase)
    return rollup


def _roll_up_attempt(
    rollup: dict[str, Any], payload: Mapping[str, Any], phase: object
) -> None:
    """Fold one status event's `external_attempt` facet into the rollup."""
    facet = _external_attempt_facet(payload)
    if facet is None:
        return
    error_kind = facet.get("error_kind")
    # `error_kind` is an outcome token, not a failure proof: a succeeded
    # stream reports `stream_succeeded` here. Only a non-success outcome
    # names the last stream error.
    if (
        isinstance(error_kind, str)
        and error_kind
        and error_kind != "stream_succeeded"
        and phase != "stream_succeeded"
    ):
        rollup["last_error_kind"] = error_kind
    attempt = facet.get("attempt")
    if isinstance(attempt, int) and not isinstance(attempt, bool):
        rollup["last_attempt"] = attempt
    max_attempts = facet.get("max_attempts")
    if isinstance(max_attempts, int) and not isinstance(max_attempts, bool):
        rollup["last_max_attempts"] = max_attempts


def _terminal_cause(events_text: str) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """The terminal envelope, name, and structured failure reason, if any."""
    terminal = terminal_event(events_text)
    terminal_name: str | None = None
    terminal_reason: str | None = None
    if terminal is not None:
        name = terminal.get("terminal")
        terminal_name = name if isinstance(name, str) and name else None
        reason = terminal.get("reason")
        if isinstance(reason, str) and reason.strip():
            terminal_reason = reason.strip()[:500]
    if terminal_reason is None:
        failed_reason = _failed_task_reason(events_text)
        if failed_reason is not None:
            terminal_reason = failed_reason[:500]
    return terminal, terminal_name, terminal_reason


def _stderr_signals(stderr_text: str) -> tuple[int, str | None]:
    """Retry count and terminal-failure cause from stderr notices."""
    stderr_failed_reason: str | None = None
    stderr_retries = 0
    for line in stderr_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _RETRY_LINE_RE.search(stripped):
            stderr_retries += 1
            continue
        failed = _FAILED_LINE_RE.match(stripped)
        if failed and failed.group(1).strip():
            stderr_failed_reason = failed.group(1).strip()[:500]
    return stderr_retries, stderr_failed_reason


def stream_diagnostics(events_text: str, stderr_text: str = "") -> dict[str, Any]:
    """Lane-cumulative model-stream retry/failure diagnostics for the receipt.

    Structured status events are authoritative when present; stderr retry
    notices are the fallback for transcripts without them. The retry count is
    the best observation across both signals (a tail cut can age either one
    out), never their sum. `cause_status` is `provided` when Muse named an
    actionable cause (terminal reason or stream error kind),
    `unavailable-upstream` when retries or a failure exist with no cause, and
    `not-applicable` for a clean run with nothing to explain.
    """
    rollup = _roll_up_status(events_text)
    terminal, terminal_name, terminal_reason = _terminal_cause(events_text)
    stderr_retries, stderr_failed_reason = _stderr_signals(stderr_text)
    retries = max(rollup["retries"], stderr_retries)
    last_message = rollup["last_message"]
    if last_message is None and stderr_retries and not rollup["from_events"]:
        last_message = "muse stream retries observed on stderr without structured events"
    if terminal_reason is None:
        terminal_reason = stderr_failed_reason
    if terminal_reason is not None or rollup["last_error_kind"] is not None:
        cause_status = "provided"
    elif retries > 0 or terminal_name == "failed":
        cause_status = "unavailable-upstream"
    else:
        cause_status = "not-applicable"
    return {
        "source": (
            "events"
            if rollup["from_events"] or terminal is not None
            else "stderr"
            if stderr_retries or stderr_failed_reason
            else "none"
        ),
        "retries": retries,
        "last_phase": rollup["last_phase"],
        "last_error_kind": rollup["last_error_kind"],
        "last_attempt": rollup["last_attempt"],
        "last_max_attempts": rollup["last_max_attempts"],
        "last_message": last_message,
        "terminal": terminal_name,
        "terminal_reason": terminal_reason,
        "cause_status": cause_status,
    }
