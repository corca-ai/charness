"""Managed-body identity and revision descent for Goal Run closeout.

A managed Work Item's prose may evolve through authorized updates; its
identity marker is forever, its bytes are not. This module owns both halves:
the marker that names a body, and the descent check that accepts an evolved
body only through the parent-owned revision chain (or the binding's observed
digest where one was recorded). Items with no recorded anchor keep the
historical marker-only behavior so runs established before the chain existed
stay closeable.
"""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path
from typing import Any

_LOCAL_IMPORT = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))
_load_local = _LOCAL_IMPORT["sibling_loader"](__file__)


def _load_achieve(name: str, alias: str) -> Any:
    return _LOCAL_IMPORT["load_achieve"](name, alias, caller_file=__file__)


PICKUP = _load_achieve("goal_run_pickup_contract", "issue_goal_run_body_chain_pickup")


def work_item_marker(key: str) -> str:
    return f"<!-- charness-work-item-key: {key} -->"


def require_marker(key: str, body: bytes | str, *, context: str) -> None:
    """A child's identity is its work-item marker, present exactly once."""
    text = body.decode("utf-8") if isinstance(body, bytes) else body
    if text.count(work_item_marker(key)) != 1:
        raise RuntimeError(f"{context} must carry the marker for Work Item {key!r} exactly once")


def _all_work_items(
    binding: dict[str, Any], metadata: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return PICKUP.effective_work_items(binding["approved_work_items"], metadata or {})


def _work_item_key_for_issue(
    binding: dict[str, Any],
    issue: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str | None:
    """Resolve one live issue to its approved Work Item key, if identifiable."""
    number = issue.get("number")
    for item in _all_work_items(binding, metadata):
        item_issue = item.get("issue")
        if isinstance(item_issue, dict) and item_issue.get("number") == number:
            key = item.get("key")
            if isinstance(key, str):
                return key
    body = issue.get("body")
    if isinstance(body, str):
        for item in _all_work_items(binding, metadata):
            key = item.get("key")
            if isinstance(key, str) and body.count(work_item_marker(key)) == 1:
                return key
    return None


def _accepted_body_digests(
    binding: dict[str, Any],
    key: str,
    metadata: dict[str, Any] | None = None,
) -> set[str]:
    """Digests a live body may descend from: chain first, observed as evidence."""
    accepted = PICKUP.body_revision_digests(metadata, key=key)
    for item in _all_work_items(binding, metadata):
        if item.get("key") != key:
            continue
        observed = item.get("observed")
        if isinstance(observed, dict):
            digest = observed.get("body_sha256")
            if isinstance(digest, str) and digest:
                accepted.add(digest)
    return accepted


def require_body_descent(
    binding: dict[str, Any],
    issues: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Accept an evolved managed body only through the authorized chain.

    A live body whose Work Item owns chain entries (or a binding observed
    digest) must digest-match one of them; anything else is an unrecorded
    replacement and refuses before any write.
    """
    for issue in issues:
        key = _work_item_key_for_issue(binding, issue, metadata)
        if key is None:
            continue
        accepted = _accepted_body_digests(binding, key, metadata)
        if not accepted:
            continue
        body = issue.get("body")
        if not isinstance(body, str):
            raise RuntimeError(
                f"Work Item {key!r} (#{issue.get('number')}) has no readable live body "
                "to verify against its authorized revision chain"
            )
        live = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if live not in accepted:
            raise RuntimeError(
                f"Work Item {key!r} (#{issue.get('number')}) live body does not descend "
                "from its authorized revision chain: unrecorded body replacement"
            )
