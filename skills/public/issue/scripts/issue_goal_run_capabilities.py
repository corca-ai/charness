"""Goal Run operation catalogue and the backend capability report.

Split from `issue_goal_run_contract.py` (#773 follow-up): the contract module
owns file-backed input validation; this module owns which backend operations a
Goal Run needs and whether the selected backend declares them.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_goal_run_capabilities_backend")
CREATE = _load_local("issue_create", "issue_goal_run_capabilities_create")
READ = _load_local("issue_read", "issue_goal_run_capabilities_read")
CLOSE = _load_local("issue_close", "issue_goal_run_capabilities_close")
TRACKER = _load_local("issue_tracker", "issue_goal_run_capabilities_tracker")

OPERATIONS = (
    "read-body",
    "read-state",
    "update-body",
    "create-or-reuse-child",
    "list-children",
    "add-child",
    "remove-child",
    "record-observation",
    "close-goal-run",
)
BACKEND_REQUIREMENTS = {
    "read-body": ("view",),
    "read-state": ("view",),
    "update-body": ("view", "update"),
    "create-or-reuse-child": ("view", "discover_managed_issues", "create"),
    "list-children": ("list_sub_issues",),
    "add-child": ("list_sub_issues", "resolve_issue_id", "add_sub_issue"),
    "remove-child": ("list_sub_issues", "resolve_issue_id", "remove_sub_issue"),
    "record-observation": (),
    "close-goal-run": ("view", "list_sub_issues", "comment", "close", "update"),
}


def capability_report(
    backend: dict[str, Any], operations: list[str] | None = None, *, repo: str
) -> dict[str, Any]:
    requested = operations or list(OPERATIONS)
    required = sorted({name for operation in requested for name in BACKEND_REQUIREMENTS[operation]})
    probe_repo = repo
    probes: dict[str, Any] = {
        "create": lambda: BACKEND.resolve_op(
            backend,
            "create",
            CREATE.GH_CREATE_DEFAULT,
            CREATE.CREATE_PLACEHOLDERS,
            required=frozenset({"repo", "title", "body_file"}),
            repo=probe_repo,
            title="probe",
            body_file="/tmp/body",
        ),
        "view": lambda: BACKEND.resolve_op(
            backend,
            "view",
            READ.GH_READ_DEFAULT,
            READ.VIEW_PLACEHOLDERS,
            required=frozenset({"repo", "number", "json_fields"}),
            repo=probe_repo,
            number="1",
            json_fields="number,body,comments,state,url",
        ),
        "discover_managed_issues": lambda: BACKEND.resolve_op(
            backend,
            "discover_managed_issues",
            TRACKER.GH_DISCOVER_MANAGED_ISSUES_DEFAULT,
            TRACKER.DISCOVER_MANAGED_ISSUES_PLACEHOLDERS,
            required=frozenset({"repo"}),
            repo=probe_repo,
        ),
        "update": lambda: BACKEND.resolve_op(
            backend,
            "update",
            TRACKER.GH_UPDATE_DEFAULT,
            TRACKER.UPDATE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "body_file"}),
            repo=probe_repo,
            number="1",
            body_file="/tmp/body",
        ),
        "list_sub_issues": lambda: BACKEND.resolve_op(
            backend,
            "list_sub_issues",
            TRACKER.GH_LIST_SUB_ISSUES_DEFAULT,
            TRACKER.LIST_SUB_ISSUES_PLACEHOLDERS,
            required=frozenset({"repo", "number"}),
            repo=probe_repo,
            number="1",
        ),
        "resolve_issue_id": lambda: BACKEND.resolve_op(
            backend,
            "resolve_issue_id",
            TRACKER.GH_RESOLVE_ISSUE_ID_DEFAULT,
            TRACKER.RESOLVE_ISSUE_ID_PLACEHOLDERS,
            required=frozenset({"repo", "sub_issue_number"}),
            repo=probe_repo,
            sub_issue_number="2",
        ),
        "add_sub_issue": lambda: BACKEND.resolve_op(
            backend,
            "add_sub_issue",
            TRACKER.GH_ADD_SUB_ISSUE_DEFAULT,
            TRACKER.MUTATE_SUB_ISSUE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "sub_issue_id"}),
            repo=probe_repo,
            number="1",
            sub_issue_id="2",
            sub_issue_number="2",
        ),
        "remove_sub_issue": lambda: BACKEND.resolve_op(
            backend,
            "remove_sub_issue",
            TRACKER.GH_REMOVE_SUB_ISSUE_DEFAULT,
            TRACKER.MUTATE_SUB_ISSUE_PLACEHOLDERS,
            required=frozenset({"repo", "number", "sub_issue_id"}),
            repo=probe_repo,
            number="1",
            sub_issue_id="2",
            sub_issue_number="2",
        ),
        "comment": lambda: BACKEND.resolve_op(
            backend,
            "comment",
            CLOSE.GH_COMMENT_DEFAULT,
            CLOSE.COMMENT_PLACEHOLDERS,
            required=frozenset({"repo", "number", "body_file"}),
            repo=probe_repo,
            number="1",
            body_file="/tmp/body",
            reason="completed",
        ),
        "close": lambda: BACKEND.resolve_op(
            backend,
            "close",
            CLOSE.GH_CLOSE_DEFAULT,
            CLOSE.CLOSE_PLACEHOLDERS,
            required=frozenset({"repo", "number"}),
            repo=probe_repo,
            number="1",
            reason="completed",
        ),
    }
    declared = {name: BACKEND.op_is_declared(backend, name) for name in required}
    template_errors: dict[str, str] = {}
    for name in required:
        if not declared[name]:
            continue
        try:
            probes[name]()
        except RuntimeError as exc:
            template_errors[name] = str(exc)
    goal = {
        operation: operation == "record-observation"
        or all(
            declared.get(name, False) and name not in template_errors
            for name in BACKEND_REQUIREMENTS[operation]
        )
        for operation in requested
    }
    missing_backend = [name for name in required if not declared[name]]
    missing_goal = [name for name, available in goal.items() if not available]
    return {
        "ok": not missing_goal and not template_errors,
        "status": "ready" if not missing_goal and not template_errors else "capability-missing",
        "requested_operations": requested,
        "probe_repo": probe_repo,
        "operations": goal,
        "required_backend_operations": required,
        "missing_operations": missing_goal,
        "missing_backend_operations": missing_backend,
        "template_errors": template_errors,
        "outcome": "verified-read" if not missing_goal and not template_errors else "refused",
        "mutation_invoked": False,
    }
