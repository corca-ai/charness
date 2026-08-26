#!/usr/bin/env python3
"""Build the Codex-only context fragment used after explicit compaction.

This module deliberately assembles instructions; it does not open a rollout,
parse a transcript, write a receipt, or claim that the model followed the
fragment. The model still owns the recovery read and the delta decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Codex's source code gives compaction its own SessionStart source. Do not attach
# recovery to `resume`: a user-resumed session is not necessarily post-compact.
RECOVERY_SOURCES = frozenset({"compact"})
_IDENTITY_FIELDS = ("session_id", "transcript_path")
MISSING_IDENTITY_REASON = "missing-identity"


@dataclass(frozen=True)
class RecoveryContext:
    """Structured result; canonical model prose is rendered by the router."""

    state: str
    session_id: str | None = None
    transcript_path: str | None = None
    reason: str | None = None


def _session_identity(payload: dict[str, Any]) -> tuple[str, str] | None:
    """Return the host-selected rollout identity without touching the rollout."""
    session_id = payload.get("session_id")
    transcript_path = payload.get("transcript_path")
    if not (
        isinstance(session_id, str)
        and session_id.strip()
        and isinstance(transcript_path, str)
        and transcript_path.strip()
    ):
        return None
    # strip() is only a blankness check. The hook must preserve the exact host
    # values because a trailing space can be part of a path or identifier.
    return session_id, transcript_path


def _not_established(reason: str) -> RecoveryContext:
    return RecoveryContext(state="not-established", reason=reason)


def build_recovery_context(payload: dict[str, Any] | None = None) -> RecoveryContext:
    """Return the Codex recovery fragment for a compact SessionStart."""
    if not isinstance(payload, dict) or payload.get("source") not in RECOVERY_SOURCES:
        return ""
    identity = _session_identity(payload)
    if identity is None:
        return _not_established(MISSING_IDENTITY_REASON)
    session_id, transcript_path = identity
    return RecoveryContext(
        state="ready",
        session_id=session_id,
        transcript_path=transcript_path,
    )
