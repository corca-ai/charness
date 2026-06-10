"""Record the goal-scoped `Host metric window:` evidence line.

Kept in its own module so ``goal_artifact_lib`` stays under its code-line limit.
The line is read back by ``scripts/host_log_probe_lib.GOAL_WINDOW_LINE``; this
module deliberately mirrors that reader's plain (non-fence-masked) search so the
artifact the probe scores is exactly the one this helper writes.
"""
from __future__ import annotations

import re
import shlex

_WINDOW_LINE = re.compile(r"^Host metric window:[^\n]*$", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_WINDOW_REQUIRED_KEYS = ("started_at", "completed_at")
# Exactly one per line; which one names the host that produced the session.
_WINDOW_SESSION_KEYS = ("codex_session_file", "claude_session_file")


def render_metric_window_line(
    *,
    started_at: str,
    completed_at: str,
    codex_session_file: str | None = None,
    claude_session_file: str | None = None,
) -> str:
    """Build the `Host metric window:` evidence line the host-log probe reads.

    Values are shell-quoted so a session-file path with spaces survives the
    probe's ``shlex.split`` parse. Empty fields are rejected so the probe never
    sees a half-written window it would only reject as ``invalid``; exactly one
    session-file key is required because the probe treats a dual-host window as
    ambiguous.
    """
    session_fields = {
        "codex_session_file": codex_session_file,
        "claude_session_file": claude_session_file,
    }
    provided = {label: value for label, value in session_fields.items() if value is not None and str(value).strip()}
    if len(provided) != 1:
        raise ValueError("exactly one of codex_session_file/claude_session_file must be non-empty")
    fields = {"started_at": started_at, "completed_at": completed_at, **provided}
    for label, value in fields.items():
        if value is None or not str(value).strip():
            raise ValueError(f"metric window field {label!r} must be non-empty")
    rendered = " ".join(f"{label}={shlex.quote(str(value).strip())}" for label, value in fields.items())
    return f"Host metric window: {rendered}"


def metric_window_attention(text: str) -> dict[str, str]:
    """Presence-only closeout signal: did the goal record a usable window?

    Returns ``recorded`` / ``incomplete`` / ``absent``. NON-BLOCKING by design:
    a host that legitimately lacks timestamps records the documented
    ``unavailable`` case instead, so this never gates the flip to complete. It
    exists only so a forgotten ``Host metric window:`` line is surfaced at
    flip-to-complete time rather than silently producing a thread-wide audit
    reported as a per-goal total.
    The probe (`host_log_probe_lib.parse_goal_metric_window`) still owns the real
    parse/validation; this is a cheap structural affordance, not a re-validator.
    """
    match = _WINDOW_LINE.search(text)
    if match is None:
        return {
            "status": "absent",
            "note": (
                "no `Host metric window:` line; long-goal host metrics will be "
                "reported thread-wide, not goal-scoped — record one with "
                "record_metric_window.py, or record `unavailable` when the host "
                "lacks timestamps"
            ),
        }
    missing = [key for key in _WINDOW_REQUIRED_KEYS if f"{key}=" not in match.group(0)]
    present_session_keys = [key for key in _WINDOW_SESSION_KEYS if f"{key}=" in match.group(0)]
    if not present_session_keys:
        missing.append("|".join(_WINDOW_SESSION_KEYS))
    if missing:
        return {
            "status": "incomplete",
            "note": "`Host metric window:` line is missing fields: " + ", ".join(missing),
        }
    if len(present_session_keys) > 1:
        # The probe rejects a dual-host window as ambiguous; surface that at
        # closeout attention instead of reading the line as recorded.
        return {
            "status": "incomplete",
            "note": "`Host metric window:` line names more than one session-file key: "
            + ", ".join(present_session_keys),
        }
    return {"status": "recorded"}


def record_metric_window(
    text: str,
    *,
    started_at: str,
    completed_at: str,
    codex_session_file: str | None = None,
    claude_session_file: str | None = None,
) -> str:
    """Insert or replace the `Host metric window:` line under `## Final Verification`.

    Idempotent: a second call with the same values returns identical text, and a
    call with new values replaces the existing line in place rather than stacking
    a second window the probe would have to disambiguate.
    """
    line = render_metric_window_line(
        started_at=started_at,
        completed_at=completed_at,
        codex_session_file=codex_session_file,
        claude_session_file=claude_session_file,
    )
    existing = _WINDOW_LINE.search(text)
    if existing is not None:
        return text[:existing.start()] + line + text[existing.end():]
    headings = list(_H2.finditer(text))
    for index, match in enumerate(headings):
        if match.group(1).strip() != "Final Verification":
            continue
        newline = text.find("\n", match.start())
        heading_line_end = len(text) if newline == -1 else newline + 1
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        existing_body = text[heading_line_end:section_end].strip("\n")
        body = f"{line}\n\n{existing_body}" if existing_body else line
        suffix = "\n" if section_end == len(text) else f"\n\n{text[section_end:]}"
        return f"{text[:heading_line_end]}\n{body}{suffix}"
    raise ValueError("artifact has no `## Final Verification` section")
