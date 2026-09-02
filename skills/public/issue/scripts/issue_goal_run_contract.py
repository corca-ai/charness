"""Contracts shared by the file-backed Goal Run provider commands."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
CAPABILITIES = _load_local("issue_goal_run_capabilities", "issue_goal_run_contract_capabilities")
# One backend object family for the contract and its capability report, so a
# caller that patches `CONTRACT.BACKEND` patches what the probes call.
BACKEND = CAPABILITIES.BACKEND
CREATE = CAPABILITIES.CREATE
READ = CAPABILITIES.READ
CLOSE = CAPABILITIES.CLOSE
TRACKER = CAPABILITIES.TRACKER
INPUT = _load_local("issue_goal_run_input", "issue_goal_run_contract_input")
CLOSE_CONTRACT = _load_local("issue_goal_run_close_contract", "issue_goal_run_contract_close_input")
BINDING = _load_local("issue_goal_run_binding", "issue_goal_run_contract_binding")

PLAN_KIND = "charness.goal-run-plan/v1"
OPERATION_KIND = "charness.goal-run-operation/v1"
OPERATIONS = CAPABILITIES.OPERATIONS
BACKEND_REQUIREMENTS = CAPABILITIES.BACKEND_REQUIREMENTS
capability_report = CAPABILITIES.capability_report
GoalRunInputError = INPUT.GoalRunInputError
GoalRunInputErrors = (GoalRunInputError, CLOSE_CONTRACT.GoalRunInputError)
OPERATION_IDENTITY_FIELDS = ("binding_path", "draft_sha256", "binding_sha256")
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


def operation_name(value: dict[str, Any]) -> Any:
    return value.get("operation")


def require_record_observation_identity(operation: dict[str, Any]) -> None:
    missing = [field for field in OPERATION_IDENTITY_FIELDS if not operation.get(field)]
    if missing:
        raise _error(
            "identity-required",
            "record-observation cannot read the parent metadata; explicit Goal Run "
            f"identities are required: {missing!r}",
        )


def _validate_amendment_input(value: dict[str, Any]) -> None:
    amendment = value.get("amendment")
    if amendment is None:
        return
    if value.get("operation") != "add-child":
        raise _error("schema-invalid", "amendment is only valid for add-child")
    if not isinstance(amendment, dict) or set(amendment) != {
        "rank",
        "dependencies",
        "reason",
        "approval",
    }:
        raise _error("schema-invalid", "amendment must carry rank, dependencies, reason, approval")


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
            "amendment",
            "parent_metadata",
            "result",
        },
        "operation",
    )
    _validate_amendment_input(value)
    if value.get("parent_metadata") is not None and not isinstance(value["parent_metadata"], dict):
        raise _error(
            "schema-invalid", "parent_metadata must be the parent's Goal Run metadata object"
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
    for field in ("draft_sha256", "binding_sha256"):
        if value.get(field) is not None:
            _sha(value[field], f"operation.{field}")
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


def validate_operation_binding(
    operation: dict[str, Any],
    repo_root: Path,
    *,
    parent_metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    try:
        return BINDING.validate_operation_binding(
            operation,
            repo_root,
            repo_file=repo_file,
            tracker=TRACKER,
            parent_metadata=parent_metadata,
        )
    except BINDING.BindingError as exc:
        raise _error(exc.code, str(exc)) from exc
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise _error("binding-mismatch", str(exc)) from exc
