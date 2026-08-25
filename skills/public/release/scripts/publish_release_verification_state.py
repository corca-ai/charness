"""Reconcile local release claims with the distinct-channel observation."""

from __future__ import annotations

from typing import Any


def reconcile_public_release_verification(payload: dict[str, Any]) -> str:
    """Do not leave a backend-only `verified` claim after public readback.

    The rung-1 floor still permits a typed non-confirmation to proceed to
    closeout, but that disposition cannot coexist with a public `verified`
    claim. This downgrades the claim without blocking recovery or issue-close
    policy, keeping the irreversible boundary honest.
    """
    if payload.get("public_release_verification") != "verified":
        return str(payload.get("public_release_verification", ""))
    record = payload.get("distinct_channel_verification") or {}
    if record.get("status") == "confirmed":
        return "verified"
    payload["public_release_verification"] = "unproven"
    payload["public_release_verification_reason"] = (
        "backend visibility passed, but the required distinct-channel readback "
        f"was `{record.get('status', 'missing')}`"
    )
    return "unproven"
