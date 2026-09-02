"""Pure contracts for issue-native ``/goal #N`` pickup."""

from __future__ import annotations

import re
from typing import Any

OBJECTIVE_RE = re.compile(r"^/goal +#([1-9][0-9]*)$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
GOAL_RUN_SCHEMA = "charness.goal-binding/v1"
VERIFIED_BOOTSTRAP = "verified-target-roundtrip"
PROGRESS_SCHEMA = "charness.goal-progress/v1"
PROGRESS_FIELDS = {
    "schema",
    "revision",
    "total",
    "completed",
    "open",
    "next",
}
# Tolerated for pre-amendment parents; never required and never compared.
PROGRESS_OPTIONAL_FIELDS = {"membership_sha256"}
NEXT_FIELDS = {"key", "repo", "number", "url", "state"}
AMENDMENT_FIELDS = {"key", "repo", "number", "url", "rank", "dependencies", "reason", "approval"}
AMENDMENT_APPROVAL_FIELDS = {"response", "session_id", "observed_at"}
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class PickupError(ValueError):
    """Typed refusal that tells the operator which identity failed."""

    def __init__(self, code: str, message: str, *, details: Any = None) -> None:
        self.code = code
        self.details = details
        super().__init__(message)


def parse_objective(value: Any) -> int:
    if not isinstance(value, str):
        raise PickupError("objective-invalid", "objective must be text matching `/goal #N`")
    match = OBJECTIVE_RE.fullmatch(value.strip())
    if match is None:
        raise PickupError("objective-invalid", "objective must match `/goal #N` exactly")
    return int(match.group(1))


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise PickupError("metadata-invalid", f"{field} must be a lowercase SHA-256")
    return value


def validate_metadata(
    metadata: Any, *, repo: str, parent_number: int, parent_url: str
) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise PickupError("metadata-invalid", "Goal Run metadata must be an object")
    required = {
        "binding_schema",
        "binding_path",
        "binding_sha256",
        "draft_path",
        "draft_sha256",
        "initial_graph_sha256",
        "bootstrap_verification",
        "parent_identity",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise PickupError("metadata-incomplete", f"Goal Run metadata is missing {missing!r}")
    if metadata["binding_schema"] != GOAL_RUN_SCHEMA:
        raise PickupError("metadata-invalid", "Goal Run metadata names an unsupported binding schema")
    identity = metadata["parent_identity"]
    if identity != {"repo": repo, "number": parent_number, "url": parent_url}:
        raise PickupError("parent-mismatch", "Goal Run metadata parent identity differs from the provider read")
    if metadata["bootstrap_verification"] != VERIFIED_BOOTSTRAP:
        raise PickupError(
            "establishment-pending",
            "Goal Run establishment is not verified for `/goal` pickup",
            details={"bootstrap_verification": metadata["bootstrap_verification"]},
        )
    for field in (
        "binding_sha256",
        "draft_sha256",
        "initial_graph_sha256",
    ):
        _sha(metadata[field], f"metadata.{field}")
    for field in ("binding_path", "draft_path"):
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise PickupError("metadata-invalid", f"metadata.{field} must be a non-empty repo-relative path")
    validate_amendments(metadata.get("amendments"), repo=repo)
    return dict(metadata)


def validate_amendments(value: Any, *, repo: str) -> list[dict[str, Any]]:
    """Validate the parent-owned list of Work Items appended after binding.

    An amendment is the one sanctioned way to widen a live Goal Run. It names an
    existing issue, its rank and dependencies, the reason, and the operator's
    approval. The immutable binding is untouched; the parent records the change.
    """
    if value is None:
        return []
    if not isinstance(value, list):
        raise PickupError("metadata-invalid", "metadata.amendments must be a list")
    seen: set[str] = set()
    result = []
    for index, entry in enumerate(value):
        context = f"metadata.amendments[{index}]"
        if not isinstance(entry, dict) or set(entry) != AMENDMENT_FIELDS:
            raise PickupError("metadata-invalid", f"{context} has the wrong fields")
        key = entry["key"]
        if not isinstance(key, str) or not KEY_RE.fullmatch(key) or key in seen:
            raise PickupError("metadata-invalid", f"{context}.key is invalid or duplicated")
        seen.add(key)
        if not isinstance(entry["repo"], str) or entry["repo"].lower() != repo.lower():
            raise PickupError("metadata-invalid", f"{context}.repo differs from the Goal Run repository")
        number = entry["number"]
        if type(number) is not int or number <= 0:
            raise PickupError("metadata-invalid", f"{context}.number must be a positive integer")
        if entry["url"] != f"https://github.com/{repo}/issues/{number}":
            raise PickupError("metadata-invalid", f"{context}.url does not match its repository and number")
        if type(entry["rank"]) is not int or entry["rank"] <= 0:
            raise PickupError("metadata-invalid", f"{context}.rank must be positive")
        deps = entry["dependencies"]
        if not isinstance(deps, list) or any(not isinstance(d, str) or not KEY_RE.fullmatch(d) for d in deps):
            raise PickupError("metadata-invalid", f"{context}.dependencies are invalid")
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise PickupError("metadata-invalid", f"{context}.reason must be non-empty text")
        approval = entry["approval"]
        if not isinstance(approval, dict) or set(approval) != AMENDMENT_APPROVAL_FIELDS or any(
            not isinstance(approval[f], str) or not approval[f].strip() for f in approval
        ):
            raise PickupError("metadata-invalid", f"{context}.approval must record response, session_id, observed_at")
        result.append(dict(entry))
    return result


def amendment_items(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Project parent amendments into the Work Item shape pickup and close use."""
    return [
        {
            "key": entry["key"],
            "intent": "amended",
            "issue": {"repo": entry["repo"], "number": entry["number"], "url": entry["url"]},
            "dependencies": list(entry["dependencies"]),
            "rank": entry["rank"],
            "body_policy": "amended",
            "body_sha256": None,
            "observed": None,
        }
        for entry in (metadata.get("amendments") or [])
    ]


def effective_work_items(binding_items: list[dict[str, Any]], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Binding items plus parent amendments; keys must not collide."""
    items = list(binding_items)
    keys = {item.get("key") for item in items}
    for item in amendment_items(metadata):
        if item["key"] in keys:
            raise PickupError("metadata-invalid", f"amendment {item['key']!r} collides with an approved Work Item")
        keys.add(item["key"])
        items.append(item)
    return items


def _validate_progress_next(
    progress: dict[str, Any], binding_items: list[dict[str, Any]], *, repo: str
) -> None:
    next_child = progress["next"]
    if progress["open"] == 0:
        if next_child is not None:
            raise PickupError("progress-invalid", "a completed cursor cannot name a next child")
        return
    if not isinstance(next_child, dict) or set(next_child) != NEXT_FIELDS:
        raise PickupError("progress-invalid", "an open cursor must name exactly one next child")
    if not isinstance(next_child["key"], str) or not next_child["key"].strip():
        raise PickupError("progress-invalid", "progress.next.key must be non-empty text")
    if not isinstance(next_child["repo"], str) or not next_child["repo"].strip():
        raise PickupError("progress-invalid", "progress.next.repo must be non-empty text")
    if next_child["repo"].lower() != repo.lower():
        raise PickupError("child-identity-mismatch", "progress.next repository differs from the Goal Run repository")
    number = next_child["number"]
    if type(number) is not int or number <= 0:
        raise PickupError("progress-invalid", "progress.next.number must be a positive integer")
    expected_url = f"https://github.com/{repo}/issues/{number}"
    if next_child["url"] != expected_url:
        raise PickupError("child-identity-mismatch", "progress.next URL does not match its repository and number")
    if next_child["state"] != "OPEN":
        raise PickupError("progress-invalid", "progress.next must point to an OPEN child")
    keys = {item.get("key") for item in binding_items}
    if next_child["key"] not in keys:
        raise PickupError("graph-work-item-mismatch", "progress.next is not an approved Work Item")
    item = next(item for item in binding_items if item.get("key") == next_child["key"])
    expected_issue = item.get("issue")
    if isinstance(expected_issue, dict):
        if expected_issue.get("repo") != repo or expected_issue.get("number") != number:
            raise PickupError(
                "child-identity-mismatch",
                f"binding identity for {next_child['key']} differs from the parent cursor",
            )


def validate_progress(
    metadata: dict[str, Any],
    binding_items: list[dict[str, Any]],
    *,
    repo: str,
    parent_number: int,
) -> dict[str, Any]:
    """Validate the small parent-owned execution cursor.

    The cursor is deliberately separate from the immutable binding.  It is a
    navigation snapshot maintained by the one Goal Run updater, not a second
    approval record.  A missing cursor is a typed migration stop; pickup never
    silently falls back to a full child-graph scan.
    """
    progress = metadata.get("progress")
    if not isinstance(progress, dict):
        raise PickupError(
            "progress-sync-required",
            "Goal Run parent has no managed execution cursor; run explicit Goal Run progress sync",
        )
    extras = sorted(set(progress) - PROGRESS_FIELDS - PROGRESS_OPTIONAL_FIELDS)
    missing = sorted(PROGRESS_FIELDS - set(progress))
    if extras or missing:
        detail: dict[str, Any] = {}
        if extras:
            detail["unknown_fields"] = extras
        if missing:
            detail["missing_fields"] = missing
        raise PickupError("progress-invalid", "parent execution cursor has the wrong shape", details=detail)
    if progress["schema"] != PROGRESS_SCHEMA:
        raise PickupError("progress-invalid", "parent execution cursor names an unsupported schema")
    if type(progress["revision"]) is not int or progress["revision"] <= 0:
        raise PickupError("progress-invalid", "parent execution cursor revision must be positive")
    for field in ("total", "completed", "open"):
        if type(progress[field]) is not int or progress[field] < 0:
            raise PickupError("progress-invalid", f"progress.{field} must be a non-negative integer")
    if progress["total"] <= 0 or progress["completed"] + progress["open"] != progress["total"]:
        raise PickupError("progress-invalid", "parent execution counts do not reconcile")
    # Membership is the provider's sub-issue graph; the cursor does not restate it.
    _validate_progress_next(progress, effective_work_items(binding_items, metadata), repo=repo)
    return dict(progress)


def select_from_parent_progress(
    progress: dict[str, Any], binding_items: list[dict[str, Any]], *, repo: str
) -> dict[str, Any]:
    """Return the already-selected child without reading any child issue."""
    next_child = progress.get("next")
    if next_child is None:
        raise PickupError("all-children-closed", "the parent cursor has no remaining child")
    item = next(item for item in binding_items if item.get("key") == next_child["key"])
    return {
        "selected_child": {
            "key": next_child["key"],
            "number": next_child["number"],
            "repo": repo,
            "rank": item["rank"],
            "dependencies": list(item.get("dependencies", [])),
            "title": next_child.get("title"),
            "selection_source": "parent-progress",
            "cursor_revision": progress["revision"],
        },
        "blocked": [],
        "invalid_open": [],
    }
