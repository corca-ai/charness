"""Parent-owned post-binding changes for issue-native Goal Runs.

``add-child`` appends one Work Item (legacy entries without ``kind`` keep
working). ``dependency-amendment`` replaces the full edge list of an
existing key with the operator approval recorded. The immutable binding is
untouched; the parent records the change.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from goal_dependency_edges import validate_edge_kinds  # noqa: E402

KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
AMENDMENT_FIELDS = {"key", "repo", "number", "url", "rank", "dependencies", "reason", "approval"}
AMENDMENT_KINDS = {"add-child", "dependency-amendment"}
AMENDMENT_OPTIONAL_FIELDS = {"kind", "dependency_kinds"}
AMENDMENT_APPROVAL_FIELDS = {"response", "session_id", "observed_at"}


class PickupError(ValueError):
    """Typed refusal that tells the operator which identity failed."""

    def __init__(self, code: str, message: str, *, details: Any = None) -> None:
        self.code = code
        self.details = details
        super().__init__(message)


def _validate_reason_approval(entry: dict[str, Any], context: str) -> None:
    if not isinstance(entry["reason"], str) or not entry["reason"].strip():
        raise PickupError("metadata-invalid", f"{context}.reason must be non-empty text")
    approval = entry["approval"]
    if (
        not isinstance(approval, dict)
        or set(approval) != AMENDMENT_APPROVAL_FIELDS
        or any(not isinstance(approval[f], str) or not approval[f].strip() for f in approval)
    ):
        raise PickupError(
            "metadata-invalid",
            f"{context}.approval must record response, session_id, observed_at",
        )


def _check_dependencies(deps: Any, key: str, context: str) -> list[str]:
    if not isinstance(deps, list) or any(
        not isinstance(d, str) or not KEY_RE.fullmatch(d) for d in deps
    ):
        raise PickupError("metadata-invalid", f"{context}.dependencies are invalid")
    if deps != sorted(set(deps)) or key in deps:
        raise PickupError("metadata-invalid", f"{context}.dependencies are not canonical")
    return list(deps)


def _validate_add_child_entry(entry: dict[str, Any], repo: str, context: str) -> dict[str, Any]:
    for field in ("repo", "number", "url", "rank"):
        if field not in entry:
            raise PickupError("metadata-invalid", f"{context} is missing {field!r}")
    if not isinstance(entry["repo"], str) or entry["repo"].lower() != repo.lower():
        raise PickupError(
            "metadata-invalid", f"{context}.repo differs from the Goal Run repository"
        )
    number = entry["number"]
    if type(number) is not int or number <= 0:
        raise PickupError("metadata-invalid", f"{context}.number must be a positive integer")
    if entry["url"] != f"https://github.com/{repo}/issues/{number}":
        raise PickupError(
            "metadata-invalid", f"{context}.url does not match its repository and number"
        )
    if type(entry["rank"]) is not int or entry["rank"] <= 0:
        raise PickupError("metadata-invalid", f"{context}.rank must be positive")
    return {"kind": "add-child", **dict(entry)}


def _validate_overlay_entry(entry: dict[str, Any], seen: set[str], context: str) -> dict[str, Any]:
    # The allowed-field check above already refuses repo/number/url/rank on an
    # overlay; only the duplicate-edge check remains here.
    key = entry["key"]
    if key in seen:
        raise PickupError("metadata-invalid", f"{context}.key has a duplicate overlay")
    seen.add(key)
    return {"kind": "dependency-amendment", **dict(entry)}


def validate_amendments(value: Any, *, repo: str) -> list[dict[str, Any]]:
    """Validate the parent-owned list of post-binding changes."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise PickupError("metadata-invalid", "metadata.amendments must be a list")
    seen: set[str] = set()
    seen_overlay: set[str] = set()
    result = []
    for index, entry in enumerate(value):
        context = f"metadata.amendments[{index}]"
        if not isinstance(entry, dict):
            raise PickupError("metadata-invalid", f"{context} must be an object")
        kind = entry.get("kind", "add-child")
        if kind not in AMENDMENT_KINDS:
            raise PickupError("metadata-invalid", f"{context}.kind names an unknown amendment")
        allowed = set(AMENDMENT_FIELDS) | AMENDMENT_OPTIONAL_FIELDS
        if kind == "dependency-amendment":
            allowed = {"key", "dependencies", "reason", "approval"} | AMENDMENT_OPTIONAL_FIELDS
        if set(entry) - allowed or not {"key", "dependencies", "reason", "approval"}.issubset(entry):
            raise PickupError("metadata-invalid", f"{context} has the wrong fields")
        key = entry["key"]
        if not isinstance(key, str) or not KEY_RE.fullmatch(key):
            raise PickupError("metadata-invalid", f"{context}.key is invalid")
        deps = _check_dependencies(entry["dependencies"], key, context)
        validate_edge_kinds(
            entry.get("dependency_kinds"), deps, context=context, error=PickupError, code="metadata-invalid"
        )
        _validate_reason_approval(entry, context)
        if kind == "dependency-amendment":
            result.append(_validate_overlay_entry(entry, seen_overlay, context))
            continue
        if key in seen:
            raise PickupError("metadata-invalid", f"{context}.key is invalid or duplicated")
        seen.add(key)
        result.append(_validate_add_child_entry(entry, repo, context))
    return result


def dependency_overlays(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Operator-approved edge replacements for existing keys, oldest first."""
    overlays = []
    for entry in metadata.get("amendments") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("kind", "add-child") != "dependency-amendment":
            continue
        overlay: dict[str, Any] = {
            "key": entry["key"],
            "dependencies": list(entry["dependencies"]),
        }
        if entry.get("dependency_kinds") is not None:
            overlay["dependency_kinds"] = dict(entry["dependency_kinds"])
        overlays.append(overlay)
    return overlays


def amendment_items(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Project parent add-child amendments into the Work Item shape pickup and close use."""
    projected = []
    for entry in metadata.get("amendments") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("kind", "add-child") != "add-child":
            continue
        item: dict[str, Any] = {
            "key": entry["key"],
            "intent": "amended",
            "issue": {"repo": entry["repo"], "number": entry["number"], "url": entry["url"]},
            "dependencies": list(entry["dependencies"]),
            "rank": entry["rank"],
            "observed": None,
        }
        if entry.get("dependency_kinds") is not None:
            item["dependency_kinds"] = dict(entry["dependency_kinds"])
        projected.append(item)
    return projected


def effective_work_items(
    binding_items: list[dict[str, Any]], metadata: dict[str, Any]
) -> list[dict[str, Any]]:
    """Binding items with dependency overlays applied, plus parent add-child items."""
    items = [dict(item) for item in binding_items]
    by_key = {item.get("key"): item for item in items}
    for overlay in dependency_overlays(metadata):
        target = by_key.get(overlay["key"])
        if target is None:
            raise PickupError(
                "metadata-invalid",
                f"dependency amendment {overlay['key']!r} names an unknown Work Item",
            )
        target["dependencies"] = list(overlay["dependencies"])
        if "dependency_kinds" in overlay:
            target["dependency_kinds"] = dict(overlay["dependency_kinds"])
        elif "dependency_kinds" in target:
            del target["dependency_kinds"]
    keys = set(by_key)
    for item in amendment_items(metadata):
        if item["key"] in keys:
            raise PickupError(
                "metadata-invalid", f"amendment {item['key']!r} collides with an approved Work Item"
            )
        keys.add(item["key"])
        items.append(item)
    return items
