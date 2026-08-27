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
    "membership_sha256",
    "next",
}
NEXT_FIELDS = {"key", "repo", "number", "url", "state"}


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
        "current_membership_sha256",
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
        "current_membership_sha256",
    ):
        _sha(metadata[field], f"metadata.{field}")
    for field in ("binding_path", "draft_path"):
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise PickupError("metadata-invalid", f"metadata.{field} must be a non-empty repo-relative path")
    return dict(metadata)


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
    extras = sorted(set(progress) - PROGRESS_FIELDS)
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
    _sha(progress["membership_sha256"], "progress.membership_sha256")
    if progress["membership_sha256"] != metadata["current_membership_sha256"]:
        raise PickupError(
            "progress-stale",
            "parent execution cursor does not name the current membership revision",
        )
    _validate_progress_next(progress, binding_items, repo=repo)
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
