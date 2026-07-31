#!/usr/bin/env python3
"""One human-readable shape for the skill-surface gate reports.

Every one of these gates prints the same skeleton — a `<label>: <status>` header,
one line per checked row, and a remediation paragraph only when the run is
blocked — while the row wording and the remediation text stay each gate's own.
Rendering that skeleton in each gate meant the shape drifted independently and
the duplicate ratchet kept re-flagging it; the callers keep their strings and
hand over the assembly."""
from __future__ import annotations

from collections.abc import Iterable


def render_gate_report(
    label: str,
    status: str,
    row_lines: Iterable[str],
    *,
    blocked_message: str,
    blocked: bool | None = None,
) -> str:
    """`<label>: <status>` + the caller's row lines + remediation when blocked.

    `blocked` defaults to `status == "blocked"`. Pass it explicitly when the
    caller's vocabulary differs: a string compare would silently drop the
    remediation paragraph for a status this module does not recognize, printing a
    failure with no way out."""
    lines = [f"{label}: {status}", *row_lines]
    if blocked is None:
        blocked = status == "blocked"
    if blocked:
        lines.append(blocked_message)
    return "\n".join(lines)
