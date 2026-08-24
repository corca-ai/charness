"""Lifecycle semantics shared by goal-artifact readers.

This boundary owns status interpretation, not readiness composition. A status
line is prose in the artifact, so callers need one answer for its lifecycle
token and for which shaping/pursuit floors apply. The module uses only the
standard library so the exported skill can load it standalone.
"""
from __future__ import annotations

import re

# A missing, mis-cased, or annotated status remains shaping until a recognised
# non-shaping token explicitly proves that the scope was already set.
NON_SHAPING_STATUSES = frozenset({"active", "blocked", "complete", "superseded"})
TERMINAL_STATUSES = frozenset({"complete", "superseded"})

_STATUS_TOKEN = re.compile(
    r"^\s*(?P<token>[A-Za-z][A-Za-z0-9_-]*)(?=$|\s|[^\w/])",
    re.ASCII,
)


def is_shaping_status(status: str | None) -> bool:
    """Whether shaping floors still apply; unknown values fail closed."""
    return (status or "").strip().lower() not in NON_SHAPING_STATUSES


def status_token(status: str | None) -> str:
    """Return the leading lifecycle token from an annotated status value."""
    match = _STATUS_TOKEN.match(status or "")
    return match.group("token").lower() if match else ""


def is_terminal_status(status: str | None) -> bool:
    """Whether a goal is historical and cannot be pursued again."""
    return status_token(status) in TERMINAL_STATUSES


def assess(status: str | None) -> dict[str, object]:
    """Derive the lifecycle decisions consumed by readiness composition."""
    token = status_token(status)
    shaping = is_shaping_status(status)
    terminal = token in TERMINAL_STATUSES
    return {
        "status": status,
        "status_token": token,
        "terminal": terminal,
        "pursuit_allowed": not terminal,
        "shaping_floor_applies": shaping,
        "hollow_evaluation_applies": not terminal and (shaping or token == "active"),
        "terminal_reason": (
            f"terminal status {token!r} is historical and cannot be activated"
            if terminal
            else ""
        ),
    }
