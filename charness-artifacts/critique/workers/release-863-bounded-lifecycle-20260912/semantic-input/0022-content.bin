"""Consumer-side validation for a narrowed critique follow-up packet."""

from __future__ import annotations

import hashlib
from typing import Any


def _path_set_digest(paths: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(set(paths))).encode("utf-8")).hexdigest()


def _manifest_paths(content: str) -> list[str] | None:
    lines = content.splitlines()
    try:
        start = lines.index("Exact reviewed-path manifest:") + 1
    except ValueError:
        return None
    paths: list[str] = []
    for line in lines[start:]:
        if not line:
            break
        if not line.startswith("- "):
            return None
        value = line[2:].split("  (DELETED", 1)[0]
        if value and not value.startswith("("):
            paths.append(value)
    return paths


def refuse_if_unbound(
    support: Any,
    packet: dict[str, Any],
    reviewed_paths: list[str],
) -> None:
    """Refuse a narrowed packet whose producer scope receipt is unproven."""
    follow_up = packet.get("follow_up")
    if not isinstance(follow_up, dict):
        return
    receipt = packet.get("follow_up_scope")
    if not isinstance(receipt, dict) or receipt.get("status") != "verified":
        raise support.RunReviewError(
            "follow-up-scope-unbound",
            "follow-up packet has no verified producer-scope receipt",
        )
    selected = receipt.get("selected_paths")
    if sorted(selected or []) != sorted(reviewed_paths):
        raise support.RunReviewError(
            "follow-up-scope-mismatch",
            "follow-up producer-scope receipt does not match packet identity paths",
            details={"receipt_paths": selected, "identity_paths": reviewed_paths},
        )
    by_id = {
        item.get("section_id"): item
        for item in receipt.get("sections", [])
        if isinstance(item, dict) and isinstance(item.get("section_id"), str)
    }
    sections = packet.get("sections") if isinstance(packet.get("sections"), list) else []
    expected_ids = {section.get("id") for section in sections if isinstance(section, dict)}
    if set(by_id) != expected_ids or any(item.get("status") != "verified" for item in by_id.values()):
        raise support.RunReviewError(
            "follow-up-scope-unbound",
            "follow-up producer-scope receipt does not cover every packet section",
        )
    for section in sections:
        if not isinstance(section, dict) or by_id[section.get("id")].get("mode") != "selected-paths":
            continue
        receipt_section = by_id[section.get("id")]
        if receipt_section.get("path_binding") != "exact-path-manifest":
            raise support.RunReviewError(
                "follow-up-producer-out-of-scope",
                f"follow-up producer section `{section.get('id')}` has no exact path binding",
            )
        manifest_paths = _manifest_paths(section.get("content") or "")
        actual_paths = sorted(set(manifest_paths or []))
        if actual_paths != sorted(set(reviewed_paths)):
            raise support.RunReviewError(
                "follow-up-producer-out-of-scope",
                f"follow-up producer section `{section.get('id')}` path manifest is not exact",
                details={"expected_paths": reviewed_paths, "actual_paths": actual_paths},
            )
        if receipt_section.get("path_set_sha256") != _path_set_digest(reviewed_paths):
            raise support.RunReviewError(
                "follow-up-scope-mismatch",
                f"follow-up producer section `{section.get('id')}` path digest does not match",
            )
