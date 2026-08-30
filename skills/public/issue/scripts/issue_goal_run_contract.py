"""Contracts shared by the file-backed Goal Run provider commands."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_goal_run_contract_backend")
CREATE = _load_local("issue_create", "issue_goal_run_contract_create")
READ = _load_local("issue_read", "issue_goal_run_contract_read")
CLOSE = _load_local("issue_close", "issue_goal_run_contract_close")
TRACKER = _load_local("issue_tracker", "issue_goal_run_contract_tracker")
INPUT = _load_local("issue_goal_run_input", "issue_goal_run_contract_input")
CLOSE_CONTRACT = _load_local("issue_goal_run_close_contract", "issue_goal_run_contract_close_input")
BINDING = _load_local("issue_goal_run_binding", "issue_goal_run_contract_binding")

PLAN_KIND = "charness.goal-run-plan/v1"
OPERATION_KIND = "charness.goal-run-operation/v1"
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
GoalRunInputError = INPUT.GoalRunInputError
GoalRunInputErrors = (GoalRunInputError, CLOSE_CONTRACT.GoalRunInputError)
ATTEMPT_RE = INPUT.ATTEMPT_RE
_error = INPUT.error
_read_json = INPUT.read_json
_fields = INPUT.fields
_positive = INPUT.positive
_sha = INPUT.sha
_repo = INPUT.repo
repo_file = INPUT.repo_file


def _target(value: Any, *, repo: str, parent_number: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("schema-invalid", "operation target must be an object")
    _fields(value, {"repo", "number", "sub_issue_number", "work_item_key", "title"}, "target")
    if "repo" in value and _repo(value["repo"], "target.repo").lower() != repo.lower():
        raise _error(
            "parent-mismatch", "operation target repository differs from the requested repository"
        )
    if "number" in value:
        _positive(value["number"], "target.number")
    if "sub_issue_number" in value:
        _positive(value["sub_issue_number"], "target.sub_issue_number")
    for field in ("work_item_key", "title"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            raise _error("schema-invalid", f"target.{field} must be non-empty text")
    return dict(value)


def _validate_bound_inputs(
    value: dict[str, Any], operation: str, target: dict[str, Any], *, parent_number: int
) -> None:
    if operation == "create-or-reuse-child" and not {"work_item_key", "title"}.issubset(target):
        raise _error(
            "schema-invalid", "create-or-reuse-child target requires work_item_key and title"
        )
    if operation in {"add-child", "remove-child"}:
        if "sub_issue_number" not in target:
            raise _error("schema-invalid", f"{operation} target requires sub_issue_number")
        if "work_item_key" not in target:
            raise _error("schema-invalid", f"{operation} target requires work_item_key")
    if operation == "update-body":
        is_parent = target["number"] == parent_number
        if is_parent and "work_item_key" in target:
            raise _error(
                "schema-invalid", "parent update target must not pretend to be a Work Item"
            )
        if not is_parent and "work_item_key" not in target:
            raise _error("schema-invalid", "child update target requires work_item_key")
        authorization_file = value.get("amendment_authorization_file")
        if authorization_file is not None:
            if not is_parent:
                raise _error(
                    "schema-invalid",
                    "amendment_authorization_file is only valid for the Goal Run parent",
                )
            if not isinstance(authorization_file, str) or not authorization_file.strip():
                raise _error(
                    "path-invalid",
                    "amendment_authorization_file must be a repository-contained path",
                )
    elif "amendment_authorization_file" in value:
        raise _error(
            "schema-invalid",
            "amendment_authorization_file is only valid for update-body",
        )
    bound = {"update-body", "create-or-reuse-child", "list-children", "add-child", "remove-child"}
    if operation in bound and (
        not isinstance(value.get("binding_path"), str) or not value["binding_path"].strip()
    ):
        raise _error("input-missing", f"{operation} requires binding_path")
    if operation == "list-children" and not isinstance(value.get("expected_child_file"), str):
        raise _error(
            "input-missing", "list-children requires expected_child_file for binding enforcement"
        )


def load_plan(path: Path, *, repo: str, parent_number: int) -> dict[str, Any]:
    value, digest = _read_json(path, kind=PLAN_KIND)
    _fields(value, {"kind", "repo", "parent_number", "operations"}, "plan")
    if _repo(value.get("repo"), "plan.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "plan repository differs from the requested repository")
    if _positive(value.get("parent_number"), "plan.parent_number") != parent_number:
        raise _error("parent-mismatch", "plan parent differs from the requested parent")
    operations = value.get("operations", list(OPERATIONS))
    if (
        not isinstance(operations, list)
        or not operations
        or any(not isinstance(item, str) or item not in OPERATIONS for item in operations)
    ):
        raise _error("schema-invalid", f"plan.operations must contain only {list(OPERATIONS)!r}")
    if len(operations) != len(set(operations)):
        raise _error("schema-invalid", "plan.operations contains duplicates")
    return {
        "path": str(path),
        "sha256": digest,
        "repo": repo,
        "parent_number": parent_number,
        "operations": operations,
    }


def load_operation(path: Path, *, repo: str, parent_number: int) -> dict[str, Any]:
    value, digest = _read_json(path, kind=OPERATION_KIND)
    _fields(
        value,
        {
            "kind",
            "repo",
            "parent_number",
            "operation",
            "attempt_id",
            "draft_sha256",
            "binding_sha256",
            "binding_path",
            "observation_dir",
            "target",
            "body_file",
            "expected_child_file",
            "amendment_authorization_file",
            "result",
        },
        "operation",
    )
    if _repo(value.get("repo"), "operation.repo").lower() != repo.lower():
        raise _error(
            "parent-mismatch", "operation repository differs from the requested repository"
        )
    if _positive(value.get("parent_number"), "operation.parent_number") != parent_number:
        raise _error("parent-mismatch", "operation parent differs from the requested parent")
    operation = value.get("operation")
    if operation not in OPERATIONS or operation == "close-goal-run":
        raise _error("operation-invalid", "goal-run-apply accepts one non-close provider operation")
    attempt_id = value.get("attempt_id")
    if not isinstance(attempt_id, str) or not ATTEMPT_RE.fullmatch(attempt_id):
        raise _error("identity-invalid", "operation.attempt_id has unsupported syntax")
    _sha(value.get("draft_sha256"), "operation.draft_sha256")
    _sha(value.get("binding_sha256"), "operation.binding_sha256")
    if not isinstance(value.get("observation_dir"), str) or not value["observation_dir"].strip():
        raise _error("path-invalid", "operation.observation_dir must be non-empty text")
    target = _target(value.get("target", {}), repo=repo, parent_number=parent_number)
    if operation in {"read-body", "read-state", "update-body"} and "number" not in target:
        raise _error("schema-invalid", f"{operation} target requires number")
    if operation == "list-children" and "number" in target and target["number"] != parent_number:
        raise _error("parent-mismatch", "list-children target must be the Goal Run parent")
    body_file = value.get("body_file")
    if operation in {"update-body", "create-or-reuse-child"} and not isinstance(body_file, str):
        raise _error("input-missing", f"{operation} requires body_file")
    _validate_bound_inputs(value, operation, target, parent_number=parent_number)
    if operation == "record-observation" and not isinstance(value.get("result"), dict):
        raise _error("schema-invalid", "record-observation requires a result object")
    return {**value, "path": str(path), "sha256": digest, "target": target, "operation": operation}


load_close_proof = CLOSE_CONTRACT.load_close_proof
load_final_proof_index = CLOSE_CONTRACT.load_final_proof_index


def validate_operation_binding(operation: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    try:
        return BINDING.validate_operation_binding(
            operation, repo_root, repo_file=repo_file, tracker=TRACKER
        )
    except BINDING.BindingError as exc:
        raise _error(exc.code, str(exc)) from exc
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise _error("binding-mismatch", str(exc)) from exc


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
