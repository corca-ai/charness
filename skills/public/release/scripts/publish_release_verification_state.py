"""Reconcile local release claims with the distinct-channel observation."""

from __future__ import annotations

from typing import Any


def _distinct_channel_established(record: dict[str, Any]) -> bool:
    """Return whether the recorded observer established its distinctness.

    ``confirmed`` is the observer's status, not proof that the observer was
    distinct.  Configured adapter probes need an evaluated same-proxy guard;
    the built-in unauthenticated HTTP observer has a different transport and
    does not carry that guard field.
    """
    if record.get("status") != "confirmed":
        return False
    if record.get("channel") == "adapter-probe":
        return record.get("same_proxy_guard") == "evaluated"
    return record.get("same_proxy_guard") in (None, "evaluated")


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
    if isinstance(record, dict) and _distinct_channel_established(record):
        return "verified"
    payload["public_release_verification"] = "unproven"
    payload["public_release_verification_reason"] = (
        "backend visibility passed, but the required distinct-channel readback "
        f"was `{record.get('status', 'missing')}` without established distinctness"
    )
    return "unproven"
