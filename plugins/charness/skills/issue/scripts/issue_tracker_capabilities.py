"""Exact capability closure for Goal Run issue-provider bootstrap."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_tracker_capabilities_backend")
CREATE = _load_local("issue_create", "issue_tracker_capabilities_create")
VERIFY_CREATE = _load_local("issue_create_verify", "issue_tracker_capabilities_verify")
DISCOVERY = _load_local("issue_tracker_discovery")
RELATIONSHIPS = _load_local("issue_tracker_relationships")
resolve_op = BACKEND.resolve_op
op_is_declared = BACKEND.op_is_declared

BOOTSTRAP_OPERATIONS = (
    "create",
    "view",
    "discover_managed_issues",
    "update",
    "list_sub_issues",
    "resolve_issue_id",
    "add_sub_issue",
    "remove_sub_issue",
)
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
GH_DISCOVER_MANAGED_ISSUES_DEFAULT = DISCOVERY.GH_DISCOVER_MANAGED_ISSUES_DEFAULT
DISCOVER_MANAGED_ISSUES_PLACEHOLDERS = DISCOVERY.DISCOVER_MANAGED_ISSUES_PLACEHOLDERS
GH_LIST_SUB_ISSUES_DEFAULT = RELATIONSHIPS.GH_LIST_SUB_ISSUES_DEFAULT
LIST_SUB_ISSUES_PLACEHOLDERS = RELATIONSHIPS.LIST_SUB_ISSUES_PLACEHOLDERS
GH_RESOLVE_ISSUE_ID_DEFAULT = RELATIONSHIPS.GH_RESOLVE_ISSUE_ID_DEFAULT
RESOLVE_ISSUE_ID_PLACEHOLDERS = RELATIONSHIPS.RESOLVE_ISSUE_ID_PLACEHOLDERS
GH_ADD_SUB_ISSUE_DEFAULT = RELATIONSHIPS.GH_ADD_SUB_ISSUE_DEFAULT
GH_REMOVE_SUB_ISSUE_DEFAULT = RELATIONSHIPS.GH_REMOVE_SUB_ISSUE_DEFAULT
MUTATE_SUB_ISSUE_PLACEHOLDERS = RELATIONSHIPS.MUTATE_SUB_ISSUE_PLACEHOLDERS


def tracker_capability_report(backend: dict[str, Any]) -> dict[str, Any]:
    declared = {op: op_is_declared(backend, op) for op in BOOTSTRAP_OPERATIONS}
    missing = [op for op, available in declared.items() if not available]
    template_errors: dict[str, str] = {}
    probes = {
        "create": lambda: resolve_op(
            backend,
            "create",
            CREATE.GH_CREATE_DEFAULT,
            CREATE.CREATE_PLACEHOLDERS,
            required=frozenset({"repo", "title", "body_file"}),
            repo="owner/repo",
            title="probe",
            body_file="/tmp/probe",
        ),
        "view": lambda: resolve_op(
            backend,
            "view",
            VERIFY_CREATE.GH_VIEW_BODY_DEFAULT,
            VERIFY_CREATE.VIEW_PLACEHOLDERS,
            required=frozenset({"repo", "number", "json_fields"}),
            repo="owner/repo",
            number="1",
            json_fields="number,body,url",
        ),
        "discover_managed_issues": lambda: resolve_op(
            backend,
            "discover_managed_issues",
            GH_DISCOVER_MANAGED_ISSUES_DEFAULT,
            DISCOVER_MANAGED_ISSUES_PLACEHOLDERS,
            required=frozenset({"repo"}),
            repo="owner/repo",
        ),
        "update": lambda: resolve_op(
            backend,
            "update",
            GH_UPDATE_DEFAULT,
            UPDATE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "body_file"}),
            repo="owner/repo",
            number="1",
            body_file="/tmp/probe",
        ),
        "list_sub_issues": lambda: resolve_op(
            backend,
            "list_sub_issues",
            GH_LIST_SUB_ISSUES_DEFAULT,
            LIST_SUB_ISSUES_PLACEHOLDERS,
            required=frozenset({"repo", "number"}),
            repo="owner/repo",
            number="1",
        ),
        "resolve_issue_id": lambda: resolve_op(
            backend,
            "resolve_issue_id",
            GH_RESOLVE_ISSUE_ID_DEFAULT,
            RESOLVE_ISSUE_ID_PLACEHOLDERS,
            required=frozenset({"repo", "sub_issue_number"}),
            repo="owner/repo",
            sub_issue_number="2",
        ),
        "add_sub_issue": lambda: resolve_op(
            backend,
            "add_sub_issue",
            GH_ADD_SUB_ISSUE_DEFAULT,
            MUTATE_SUB_ISSUE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "sub_issue_id"}),
            repo="owner/repo",
            number="1",
            sub_issue_id="2",
            sub_issue_number="2",
        ),
        "remove_sub_issue": lambda: resolve_op(
            backend,
            "remove_sub_issue",
            GH_REMOVE_SUB_ISSUE_DEFAULT,
            MUTATE_SUB_ISSUE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "sub_issue_id"}),
            repo="owner/repo",
            number="1",
            sub_issue_id="2",
            sub_issue_number="2",
        ),
    }
    for operation, render in probes.items():
        if not declared[operation]:
            continue
        try:
            render()
        except RuntimeError as exc:
            template_errors[operation] = str(exc)
    return {
        "ok": not missing and not template_errors,
        "status": "ready" if not missing and not template_errors else "tracker-capability-missing",
        "operations": declared,
        "missing_operations": missing,
        "template_errors": template_errors,
        "outcome": "verified-read",
        "mutation_invoked": False,
    }
