"""Backend-routed GitHub parent-body and real sub-issue operations."""

from __future__ import annotations

import json
import re
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

GOAL_RUN_MARKER_RE = re.compile(r"<!--\s*charness-goal-run:(?P<version>[^\s]+)")
GOAL_RUN_BLOCK_RE = re.compile(
    r"<!-- charness-goal-run:v1\s*\n(?P<payload>\{.*?\})\s*\n-->", re.DOTALL
)
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
_exact_reusable_match = DISCOVERY._exact_reusable_match
list_sub_issues = RELATIONSHIPS.list_sub_issues
_resolve_issue_id = RELATIONSHIPS._resolve_issue_id
add_sub_issue = RELATIONSHIPS.add_sub_issue
remove_sub_issue = RELATIONSHIPS.remove_sub_issue

GOAL_RUN_IMMUTABLE_FIELDS = (
    "binding_schema",
    "binding_path",
    "binding_sha256",
    "draft_path",
    "draft_sha256",
    "initial_graph_sha256",
)
GOAL_RUN_TERMINAL_FIELDS = (
    "terminal_observation_path",
    "terminal_observation_sha256",
)


def _goal_run_block(body: str, *, context: str) -> dict[str, Any] | None:
    markers = list(GOAL_RUN_MARKER_RE.finditer(body))
    matches = list(GOAL_RUN_BLOCK_RE.finditer(body))
    if not markers:
        return None
    versions = [match.group("version") for match in markers]
    unsupported = sorted(set(versions) - {"v1"})
    if unsupported:
        raise RuntimeError(
            f"{context} has unsupported Goal Run metadata version(s): {unsupported!r}"
        )
    if len(markers) != 1 or len(matches) != 1:
        raise RuntimeError(f"{context} has duplicate or malformed Goal Run metadata")
    try:
        payload = json.loads(matches[0].group("payload"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{context} Goal Run metadata is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{context} Goal Run metadata must be a JSON object")
    return payload


def _guard_goal_run_metadata(
    current_body: str, desired_body: str, *, terminal_metadata_update: bool = False
) -> None:
    current = _goal_run_block(current_body, context="current body")
    desired = _goal_run_block(desired_body, context="desired body")
    if current is not None and desired is None:
        raise RuntimeError("tracker update refused to strip Goal Run metadata")
    if current is None or desired is None:
        return
    changed = [
        field for field in GOAL_RUN_IMMUTABLE_FIELDS if current.get(field) != desired.get(field)
    ]
    if changed:
        raise RuntimeError(
            f"tracker update refused to alter immutable Goal Run identity fields: {changed!r}"
        )
    missing = object()
    terminal_changed = [
        field
        for field in GOAL_RUN_TERMINAL_FIELDS
        if current.get(field, missing) != desired.get(field, missing)
    ]
    if terminal_changed and not terminal_metadata_update:
        raise RuntimeError(
            "tracker update refused to alter terminal Goal Run metadata outside the "
            f"dedicated close ingress: {terminal_changed!r}"
        )


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
    reusable = _exact_reusable_match(before, title=title, body_text=body_text)
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
            "with the requested title and byte-identical body"
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
    created = _exact_reusable_match(after, title=title, body_text=body_text)
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
) -> dict[str, Any]:
    if not body_file.is_file():
        raise RuntimeError(f"tracker body file not found: {body_file}")
    before = VERIFY_CREATE.verify_created_issue(
        repo, number, body_file=body_file, backend=backend, include_body=True
    )
    current_body = before.pop("body")
    desired_body = body_file.read_text(encoding="utf-8")
    _guard_goal_run_metadata(
        current_body,
        desired_body,
        terminal_metadata_update=terminal_metadata_update,
    )
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
