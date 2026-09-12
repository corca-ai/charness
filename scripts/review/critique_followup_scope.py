"""Adapter-declared producer scope checks for critique follow-up packets."""

from __future__ import annotations

import hashlib
from typing import Any, Callable


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
        value = line[2:]
        value = value.split("  (DELETED", 1)[0]
        if value and not value.startswith("("):
            paths.append(value)
    return paths


def follow_up_scope_receipt(
    *,
    adapter: dict[str, Any],
    sections: list[dict[str, Any]],
    selected_paths: list[str],
    error: Callable[..., Exception],
) -> dict[str, Any]:
    """Verify and record how every follow-up section was narrowed."""
    declarations = (adapter.get("data", {}) or {}).get("follow_up_scope", [])
    if not isinstance(declarations, list):
        raise error(
            "follow-up-scope-unbound",
            "follow_up_scope must be a list of per-section declarations",
        )
    by_id = {
        item.get("section_id"): item
        for item in declarations
        if isinstance(item, dict) and isinstance(item.get("section_id"), str)
    }
    expected_ids = {
        section.get("id") for section in sections if isinstance(section.get("id"), str)
    }
    if set(by_id) != expected_ids:
        raise error(
            "follow-up-scope-unbound",
            "follow_up_scope must declare every packet section exactly once",
            details={
                "declared_section_ids": sorted(by_id),
                "packet_section_ids": sorted(expected_ids),
                "missing_section_ids": sorted(expected_ids - set(by_id)),
                "unexpected_section_ids": sorted(set(by_id) - expected_ids),
            },
        )

    selected = sorted(set(selected_paths))
    receipts: list[dict[str, Any]] = []
    for section in sections:
        section_id = section["id"]
        declaration = by_id[section_id]
        mode = declaration.get("mode")
        if mode not in {"selected-paths", "static"}:
            raise error(
                "follow-up-scope-unbound",
                f"follow-up_scope mode is invalid for section `{section_id}`",
                details={"section_id": section_id, "mode": mode},
            )
        content = section.get("content") if isinstance(section.get("content"), str) else ""
        path_set_digest = None
        if mode == "selected-paths":
            if declaration.get("path_binding") != "exact-path-manifest":
                raise error(
                    "follow-up-producer-out-of-scope",
                    f"follow-up producer section `{section_id}` has no exact path binding",
                )
            manifest_paths = _manifest_paths(content)
            if manifest_paths is None or sorted(set(manifest_paths)) != selected:
                raise error(
                    "follow-up-producer-out-of-scope",
                    f"follow-up producer section `{section_id}` path manifest is not exact",
                    details={
                        "section_id": section_id,
                        "expected_paths": selected,
                        "actual_paths": sorted(set(manifest_paths or [])),
                    },
                )
            path_set_digest = _path_set_digest(selected)
        receipts.append(
            {
                "section_id": section_id,
                "mode": mode,
                "binding": declaration.get("binding"),
                "path_binding": declaration.get("path_binding"),
                "selected_path_count": len(selected),
                "path_set_sha256": path_set_digest,
                "status": "verified",
                "path_check": "exact-manifest" if mode == "selected-paths" else "not-applicable",
            }
        )
    return {
        "kind": "charness.follow_up_scope_receipt.v1",
        "status": "verified",
        "selected_paths": selected,
        "sections": receipts,
        "contract": (
            "Adapter-declared follow-up scope; selected-path sections must expose every "
            "identity-bound path, and static sections must declare that they are not path-bearing."
        ),
    }
