"""Pure contracts for issue-native ``/goal #N`` pickup.

Amendment ownership lives in the adjacent ``goal_run_amendments`` module;
this contract re-exports its names so existing ``PICKUP.*`` callers keep
working.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from goal_dependency_edges import EDGE_KINDS, hard_dependencies, ready_frontier  # noqa: E402
from goal_run_amendments import (  # noqa: E402
    AMENDMENT_APPROVAL_FIELDS,
    AMENDMENT_FIELDS,
    AMENDMENT_KINDS,
    AMENDMENT_OPTIONAL_FIELDS,
    PickupError,
    amendment_items,
    dependency_overlays,
    effective_work_items,
    validate_amendments,
)

__all__ = [
    "AMENDMENT_APPROVAL_FIELDS",
    "AMENDMENT_FIELDS",
    "AMENDMENT_KINDS",
    "AMENDMENT_OPTIONAL_FIELDS",
    "EDGE_KINDS",
    "PickupError",
    "amendment_items",
    "dependency_overlays",
    "effective_work_items",
    "hard_dependencies",
    "ready_frontier",
    "validate_amendments",
]

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
PROGRESS_OPTIONAL_FIELDS = {"membership_sha256", "ready_keys"}
NEXT_FIELDS = {"key", "repo", "number", "url", "state"}
BODY_REVISION_FIELDS = {"key", "number", "body_sha256", "supersedes_sha256"}
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


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
        raise PickupError(
            "metadata-invalid", "Goal Run metadata names an unsupported binding schema"
        )
    identity = metadata["parent_identity"]
    if identity != {"repo": repo, "number": parent_number, "url": parent_url}:
        raise PickupError(
            "parent-mismatch", "Goal Run metadata parent identity differs from the provider read"
        )
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
            raise PickupError(
                "metadata-invalid", f"metadata.{field} must be a non-empty repo-relative path"
            )
    validate_amendments(metadata.get("amendments"), repo=repo)
    validate_body_revisions(metadata.get("body_revisions"))
    return dict(metadata)




def validate_body_revisions(value: Any) -> list[dict[str, Any]]:
    """Validate the parent-owned append-only Work Item body revision chain.

    One entry records one authorized managed-body mutation: the Work Item key
    and issue number it applied to, the submitted body's digest, and the live
    digest it superseded (the chain genesis when first recorded). Entries are
    written only by the validated update-body path, oldest first; closeout
    accepts a live body only when it descends from this chain (or from the
    binding's observed digest where one was recorded). Absent means no managed
    body was ever updated through the operation path, which preserves the
    historical marker-only behavior for untouched items.
    """
    if value is None:
        return []
    if not isinstance(value, list):
        raise PickupError("metadata-invalid", "metadata.body_revisions must be a list")
    result = []
    for index, entry in enumerate(value):
        context = f"metadata.body_revisions[{index}]"
        if not isinstance(entry, dict) or set(entry) != BODY_REVISION_FIELDS:
            raise PickupError("metadata-invalid", f"{context} has the wrong fields")
        key = entry["key"]
        if not isinstance(key, str) or not KEY_RE.fullmatch(key):
            raise PickupError("metadata-invalid", f"{context}.key is invalid")
        number = entry["number"]
        if type(number) is not int or number <= 0:
            raise PickupError("metadata-invalid", f"{context}.number must be a positive integer")
        _sha(entry["body_sha256"], f"{context}.body_sha256")
        supersedes = entry["supersedes_sha256"]
        if supersedes is not None:
            _sha(supersedes, f"{context}.supersedes_sha256")
        result.append(dict(entry))
    return result


def body_revision_digests(
    metadata: dict[str, Any] | None, *, key: str
) -> set[str]:
    """Every digest the authorized chain knows for one Work Item key."""
    if not metadata:
        return set()
    digests: set[str] = set()
    for entry in validate_body_revisions(metadata.get("body_revisions")):
        if entry["key"] == key:
            digests.add(entry["body_sha256"])
            if entry["supersedes_sha256"] is not None:
                digests.add(entry["supersedes_sha256"])
    return digests




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
        raise PickupError(
            "child-identity-mismatch",
            "progress.next repository differs from the Goal Run repository",
        )
    number = next_child["number"]
    if type(number) is not int or number <= 0:
        raise PickupError("progress-invalid", "progress.next.number must be a positive integer")
    expected_url = f"https://github.com/{repo}/issues/{number}"
    if next_child["url"] != expected_url:
        raise PickupError(
            "child-identity-mismatch", "progress.next URL does not match its repository and number"
        )
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
        raise PickupError(
            "progress-invalid", "parent execution cursor has the wrong shape", details=detail
        )
    if progress["schema"] != PROGRESS_SCHEMA:
        raise PickupError("progress-invalid", "parent execution cursor names an unsupported schema")
    if type(progress["revision"]) is not int or progress["revision"] <= 0:
        raise PickupError("progress-invalid", "parent execution cursor revision must be positive")
    for field in ("total", "completed", "open"):
        if type(progress[field]) is not int or progress[field] < 0:
            raise PickupError(
                "progress-invalid", f"progress.{field} must be a non-negative integer"
            )
    if progress["total"] <= 0 or progress["completed"] + progress["open"] != progress["total"]:
        raise PickupError("progress-invalid", "parent execution counts do not reconcile")
    # Membership is the provider's sub-issue graph; the cursor does not restate it.
    effective = effective_work_items(binding_items, metadata)
    _validate_progress_next(progress, effective, repo=repo)
    ready_keys = progress.get("ready_keys")
    if ready_keys is not None:
        if (
            not isinstance(ready_keys, list)
            or not ready_keys
            or any(not isinstance(k, str) or not KEY_RE.fullmatch(k) for k in ready_keys)
            or sorted(set(ready_keys)) != list(ready_keys)
        ):
            raise PickupError("progress-invalid", "progress.ready_keys must be a sorted unique key list")
        known = {item.get("key") for item in effective}
        unknown = sorted(set(ready_keys) - known)
        if unknown:
            raise PickupError(
                "graph-work-item-mismatch", f"progress.ready_keys names unknown items {unknown!r}"
            )
        if progress["open"] == 0:
            raise PickupError("progress-invalid", "a completed cursor cannot name a ready frontier")
        if progress["next"] is not None and progress["next"]["key"] not in ready_keys:
            raise PickupError(
                "progress-invalid", "progress.next must belong to the ready frontier"
            )
    return dict(progress)


def select_from_parent_progress(
    progress: dict[str, Any], binding_items: list[dict[str, Any]], *, repo: str
) -> dict[str, Any]:
    """Return the already-selected child without reading any child issue."""
    next_child = progress.get("next")
    if next_child is None:
        raise PickupError("all-children-closed", "the parent cursor has no remaining child")
    item = next(item for item in binding_items if item.get("key") == next_child["key"])
    ready_keys = progress.get("ready_keys")
    if ready_keys is None:
        ready_keys = [next_child["key"]]
    selected: dict[str, Any] = {
        "key": next_child["key"],
        "number": next_child["number"],
        "repo": repo,
        "rank": item["rank"],
        "dependencies": list(item.get("dependencies", [])),
        "title": next_child.get("title"),
        "selection_source": "parent-progress",
        "cursor_revision": progress["revision"],
    }
    if item.get("dependency_kinds") is not None:
        selected["dependency_kinds"] = dict(item["dependency_kinds"])
    return {
        "selected_child": selected,
        "ready_keys": list(ready_keys),
        "blocked": [],
        "invalid_open": [],
    }
