"""Backend-routed GitHub parent-body and real sub-issue operations."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_tracker_backend")
VERIFY_CREATE = _load_local("issue_create_verify", "issue_tracker_verify")
CREATE = _load_local("issue_create", "issue_tracker_create")
DISCOVERY = _load_local("issue_tracker_discovery")
RELATIONSHIPS = _load_local("issue_tracker_relationships")
OUTCOME = _load_local("issue_tracker_outcome")
CAPABILITIES = _load_local("issue_tracker_capabilities")
GOAL_METADATA = _load_local("issue_tracker_goal_metadata")

run_backend = BACKEND.run_backend
resolve_op = BACKEND.resolve_op
op_is_declared = BACKEND.op_is_declared

GH_UPDATE_DEFAULT = [
    "issue",
    "edit",
    "{number}",
    "--repo",
    "{repo}",
    "--body-file",
    "{body_file}",
]
UPDATE_PLACEHOLDERS = frozenset({"repo", "number", "body_file"})

BOOTSTRAP_OPERATIONS = CAPABILITIES.BOOTSTRAP_OPERATIONS
tracker_capability_report = CAPABILITIES.tracker_capability_report
GH_DISCOVER_MANAGED_ISSUES_DEFAULT = DISCOVERY.GH_DISCOVER_MANAGED_ISSUES_DEFAULT
DISCOVER_MANAGED_ISSUES_PLACEHOLDERS = DISCOVERY.DISCOVER_MANAGED_ISSUES_PLACEHOLDERS
GH_LIST_SUB_ISSUES_DEFAULT = RELATIONSHIPS.GH_LIST_SUB_ISSUES_DEFAULT
LIST_SUB_ISSUES_PLACEHOLDERS = RELATIONSHIPS.LIST_SUB_ISSUES_PLACEHOLDERS
GH_RESOLVE_ISSUE_ID_DEFAULT = RELATIONSHIPS.GH_RESOLVE_ISSUE_ID_DEFAULT
RESOLVE_ISSUE_ID_PLACEHOLDERS = RELATIONSHIPS.RESOLVE_ISSUE_ID_PLACEHOLDERS
GH_ADD_SUB_ISSUE_DEFAULT = RELATIONSHIPS.GH_ADD_SUB_ISSUE_DEFAULT
GH_REMOVE_SUB_ISSUE_DEFAULT = RELATIONSHIPS.GH_REMOVE_SUB_ISSUE_DEFAULT
MUTATE_SUB_ISSUE_PLACEHOLDERS = RELATIONSHIPS.MUTATE_SUB_ISSUE_PLACEHOLDERS
unverified_mutation = OUTCOME.unverified_mutation
work_item_key_marker = DISCOVERY.work_item_key_marker
load_expected_child_set = DISCOVERY.load_expected_child_set
discover_managed_issues = DISCOVERY.discover_managed_issues
list_sub_issues = RELATIONSHIPS.list_sub_issues
_resolve_issue_id = RELATIONSHIPS._resolve_issue_id
add_sub_issue = RELATIONSHIPS.add_sub_issue
remove_sub_issue = RELATIONSHIPS.remove_sub_issue


def _marker_reusable_match(
    discovery: dict[str, Any], *, work_item_key: str, title: str
) -> dict[str, Any] | None:
    """Reuse a child by its stable marker and title, not by mutable prose."""
    matches = discovery["matches"]
    if len(matches) != 1:
        return None
    match = matches[0]
    if match["title"] != title or match["body"].count(work_item_key_marker(work_item_key)) != 1:
        return None
    return match


def create_or_reuse_child(
    repo: str,
    parent_number: int,
    work_item_key: str,
    title: str,
    body_file: Path,
    *,
    backend: dict[str, Any],
    prior_unresolved_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not body_file.is_file():
        raise RuntimeError(f"tracker body file not found: {body_file}")
    body_text = body_file.read_text(encoding="utf-8")
    marker = work_item_key_marker(work_item_key)
    if body_text.count(marker) != 1:
        raise RuntimeError(
            f"create-or-reuse body must contain its exact work item key marker once: {marker}"
        )

    before = discover_managed_issues(repo, work_item_key, backend=backend)
    reusable = _marker_reusable_match(before, work_item_key=work_item_key, title=title)
    if reusable is not None:
        return {
            "ok": True,
            "status": "already-exists",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "action": "reused",
            "repo": repo,
            "parent_number": parent_number,
            "work_item_key": work_item_key,
            "number": reusable["number"],
            "url": reusable["url"],
            "body_verified": True,
            "discovery": before,
        }
    if before["count"]:
        raise RuntimeError(
            "work item key is already present but does not identify exactly one issue "
            "with the requested title and stable marker"
        )
    if prior_unresolved_observation is not None:
        raise RuntimeError(
            "create refused because a prior matching provider attempt remains unresolved; "
            f"resolve observation {prior_unresolved_observation.get('started_path')!r} "
            "through exact discovery or operator disposition before retry"
        )

    create_result: dict[str, Any] | None = None
    create_error: CREATE.IssueMutationError | None = None
    try:
        create_result = CREATE.create_issue(
            repo, title, body_file, backend=backend, skip_readback=False
        )
    except CREATE.IssueMutationError as exc:
        create_error = exc

    direct_number = create_result.get("number") if create_result is not None else None
    direct_url = create_result.get("url") if create_result is not None else None
    direct_verified = bool(
        create_result
        and create_result.get("ok") is True
        and create_result.get("repo", "").casefold() == repo.casefold()
        and type(direct_number) is int
        and direct_number > 0
        and isinstance(direct_url, str)
        and direct_url
        and create_result.get("body_verified") is True
    )
    if direct_verified:
        return {
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "action": "created",
            "repo": repo,
            "parent_number": parent_number,
            "work_item_key": work_item_key,
            "number": direct_number,
            "url": direct_url,
            "body_verified": True,
            "before": before,
            "readback": create_result,
        }

    try:
        after = discover_managed_issues(repo, work_item_key, backend=backend)
    except RuntimeError as exc:
        return unverified_mutation(
            "create-child",
            repo=repo,
            parent_number=parent_number,
            work_item_key=work_item_key,
            before=before,
            error=f"post-create discovery failed: {exc}",
            exit_code=create_error.exit_code if create_error else None,
        )
    created = _marker_reusable_match(after, work_item_key=work_item_key, title=title)
    if created is None:
        detail = (
            str(create_error)
            if create_error is not None
            else "provider create did not yield one exactly discoverable managed issue"
        )
        return unverified_mutation(
            "create-child",
            repo=repo,
            parent_number=parent_number,
            work_item_key=work_item_key,
            before=before,
            error=detail,
            exit_code=create_error.exit_code if create_error else None,
            unresolved_targets=after["matches"],
            provider_return=create_result,
        )

    return {
        "ok": True,
        "status": "verified-write",
        "outcome": "verified-write",
        "mutation_invoked": True,
        "action": "created-recovered",
        "repo": repo,
        "parent_number": parent_number,
        "work_item_key": work_item_key,
        "number": created["number"],
        "url": created["url"],
        "body_verified": True,
        "before": before,
        "readback": after,
    }


def update_issue_body(
    repo: str,
    number: int,
    body_file: Path,
    *,
    backend: dict[str, Any],
    terminal_metadata_update: bool = False,
    expected_body_sha256: str | None = None,
    pre_write_validator: Any | None = None,
    parent_amendment_validator: Any | None = None,
) -> dict[str, Any]:
    # expected_body_sha256 is retained for primitive tracker callers. Goal Run
    # operations deliberately omit it and bind updates to marker/parent identity.
    if not body_file.is_file():
        raise RuntimeError(f"tracker body file not found: {body_file}")
    before = VERIFY_CREATE.verify_created_issue(
        repo, number, body_file=body_file, backend=backend, include_body=True
    )
    current_body = before.pop("body")
    current_body_sha256 = hashlib.sha256(current_body.encode("utf-8")).hexdigest()
    before["body_sha256"] = current_body_sha256
    if expected_body_sha256 is not None and current_body_sha256 != expected_body_sha256:
        raise RuntimeError(
            "tracker body update refused because the live pre-write body digest differs "
            f"from the bound observed digest: expected {expected_body_sha256}, got {current_body_sha256}"
        )
    desired_body = body_file.read_text(encoding="utf-8")
    GOAL_METADATA.guard_goal_run_metadata(
        current_body,
        desired_body,
        terminal_metadata_update=terminal_metadata_update,
        allow_human_amendment=parent_amendment_validator is not None,
    )
    if pre_write_validator is not None:
        pre_write_validator(current_body, desired_body)
    if parent_amendment_validator is not None:
        parent_amendment_validator(current_body, desired_body)
    if before["body_verified"] is True:
        return {
            "ok": True,
            "status": "already-current",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "operation": "update-body",
            "action": "already-current",
            "repo": repo,
            "number": number,
            "url": before["url"],
            "body_verified": True,
            "before": before,
            "single_updater_assumption": True,
        }
    argv = resolve_op(
        backend,
        "update",
        GH_UPDATE_DEFAULT,
        UPDATE_PLACEHOLDERS,
        required=frozenset({"repo", "number", "body_file"}),
        repo=repo,
        number=str(number),
        body_file=str(body_file),
    )
    result = run_backend(argv)
    if result.returncode != 0:
        return unverified_mutation(
            "update-body",
            repo=repo,
            parent_number=number,
            error=f"provider command failed: {result.stderr.strip()!r}",
            before=before,
            exit_code=result.returncode,
        )
    try:
        readback = VERIFY_CREATE.verify_created_issue(
            repo, number, body_file=body_file, backend=backend
        )
    except RuntimeError as exc:
        return unverified_mutation(
            "update-body", repo=repo, parent_number=number, error=str(exc), before=before
        )
    if readback["body_verified"] is not True:
        return unverified_mutation(
            "update-body",
            repo=repo,
            parent_number=number,
            error="tracker body update readback was not byte-identical",
            before=before,
        )
    return {
        "ok": True,
        "status": "verified-write",
        "outcome": "verified-write",
        "mutation_invoked": True,
        "operation": "update-body",
        "action": "updated",
        "repo": repo,
        "number": number,
        "url": readback["url"],
        "body_verified": True,
        "before": before,
        "single_updater_assumption": True,
    }
