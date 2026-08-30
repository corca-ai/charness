"""Contracts shared by the file-backed Goal Run provider commands."""

from __future__ import annotations

import hashlib
import json
import re
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](
    __file__
)
BACKEND = _load_local("issue_backend", "issue_goal_run_contract_backend")
CREATE = _load_local("issue_create", "issue_goal_run_contract_create")
READ = _load_local("issue_read", "issue_goal_run_contract_read")
CLOSE = _load_local("issue_close", "issue_goal_run_contract_close")
TRACKER = _load_local("issue_tracker", "issue_goal_run_contract_tracker")

PLAN_KIND = "charness.goal-run-plan/v1"
OPERATION_KIND = "charness.goal-run-operation/v1"
CLOSE_PROOF_KIND = "charness.goal-run-close-proof/v1"
FINAL_PROOF_INDEX_KIND = "charness.goal-run-final-proof-index/v1"
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
    "close-goal-run": ("view", "list_sub_issues", "comment", "close"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ATTEMPT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class GoalRunInputError(RuntimeError):
    """A typed refusal for a malformed or stale file-backed command input."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _error(code: str, message: str) -> GoalRunInputError:
    return GoalRunInputError(code, message)


def _read_json(path: Path, *, kind: str) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise _error("input-missing", f"Goal Run input file not found: {path}")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error("input-invalid", f"{path} is not canonical UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise _error("schema-invalid", f"{path} must contain a JSON object")
    if value.get("kind") != kind:
        raise _error("schema-unknown", f"{path} kind must be {kind}")
    return value, hashlib.sha256(raw).hexdigest()


def _fields(value: dict[str, Any], allowed: set[str], context: str) -> None:
    extras = sorted(set(value) - allowed)
    if extras:
        raise _error("schema-invalid", f"{context} contains unknown fields: {extras!r}")


def _positive(value: Any, context: str) -> int:
    if type(value) is not int or value <= 0:
        raise _error("identity-invalid", f"{context} must be a positive integer")
    return value


def _sha(value: Any, context: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise _error("identity-invalid", f"{context} must be 64 lowercase hexadecimal characters")
    return value


def _repo(value: Any, context: str) -> str:
    if not isinstance(value, str) or value.count("/") != 1 or not all(value.split("/")):
        raise _error("identity-invalid", f"{context} must be an owner/repo identity")
    return value


def _target(value: Any, *, repo: str, parent_number: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("schema-invalid", "operation target must be an object")
    _fields(value, {"repo", "number", "sub_issue_number", "work_item_key", "title"}, "target")
    if "repo" in value and _repo(value["repo"], "target.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "operation target repository differs from the requested repository")
    if "number" in value:
        _positive(value["number"], "target.number")
    if "sub_issue_number" in value:
        _positive(value["sub_issue_number"], "target.sub_issue_number")
    for field in ("work_item_key", "title"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            raise _error("schema-invalid", f"target.{field} must be non-empty text")
    return dict(value)


def load_plan(path: Path, *, repo: str, parent_number: int) -> dict[str, Any]:
    value, digest = _read_json(path, kind=PLAN_KIND)
    _fields(value, {"kind", "repo", "parent_number", "operations"}, "plan")
    if _repo(value.get("repo"), "plan.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "plan repository differs from the requested repository")
    if _positive(value.get("parent_number"), "plan.parent_number") != parent_number:
        raise _error("parent-mismatch", "plan parent differs from the requested parent")
    operations = value.get("operations", list(OPERATIONS))
    if not isinstance(operations, list) or not operations or any(
        not isinstance(item, str) or item not in OPERATIONS for item in operations
    ):
        raise _error("schema-invalid", f"plan.operations must contain only {list(OPERATIONS)!r}")
    if len(operations) != len(set(operations)):
        raise _error("schema-invalid", "plan.operations contains duplicates")
    return {"path": str(path), "sha256": digest, "repo": repo, "parent_number": parent_number, "operations": operations}


def repo_file(repo_root: Path, value: Any, *, context: str, must_exist: bool = True) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise _error("path-invalid", f"{context} must be a repository-contained path")
    root = repo_root.resolve()
    candidate = (Path(value) if Path(value).is_absolute() else root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise _error("path-invalid", f"{context} escapes the repository root") from exc
    if must_exist and not candidate.is_file():
        raise _error("input-missing", f"{context} file not found: {candidate}")
    return candidate


def _bound_json_file(
    repo_root: Path,
    value: Any,
    declared_sha256: Any,
    *,
    kind: str,
    context: str,
) -> tuple[Path, dict[str, Any], str]:
    """Load a repo-contained JSON input only when its complete bytes are bound."""
    path = repo_file(repo_root, value, context=f"{context}_file")
    expected = _sha(declared_sha256, f"{context}_sha256")
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise _error(
            "input-stale",
            f"{context} bytes do not match its declared SHA-256: expected {expected}, got {actual}",
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error("input-invalid", f"{context} is not canonical UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise _error("schema-invalid", f"{context} must contain a JSON object")
    if payload.get("kind") != kind:
        raise _error("schema-unknown", f"{context}.kind must be {kind}")
    return path, payload, actual


def _issue_identity(value: Any, *, repo: str, parent_number: int, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("schema-invalid", f"{context} must be an object")
    _fields(value, {"repo", "number"}, context)
    identity_repo = _repo(value.get("repo"), f"{context}.repo")
    number = _positive(value.get("number"), f"{context}.number")
    if identity_repo.lower() != repo.lower():
        raise _error("parent-mismatch", f"{context} repository differs from the Goal Run repository")
    return {"repo": identity_repo, "number": number}


def load_final_proof_index(
    path: Path,
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
    sha256: str,
) -> dict[str, Any]:
    """Validate the separately bound closeout index before provider selection."""
    path, value, digest = _bound_json_file(
        repo_root,
        str(path),
        sha256,
        kind=FINAL_PROOF_INDEX_KIND,
        context="final_proof_index",
    )
    _fields(
        value,
        {
            "kind",
            "repo",
            "parent_number",
            "draft_sha256",
            "binding_sha256",
            "expected_children",
            "parent_obligation",
        },
        "final proof index",
    )
    if _repo(value.get("repo"), "final proof index.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "final proof index repository differs from the requested repository")
    if _positive(value.get("parent_number"), "final proof index.parent_number") != parent_number:
        raise _error("parent-mismatch", "final proof index parent differs from the requested parent")
    if _sha(value.get("draft_sha256"), "final proof index.draft_sha256") != draft_sha256:
        raise _error("input-stale", "final proof index draft hash differs from the close proof")
    if _sha(value.get("binding_sha256"), "final proof index.binding_sha256") != binding_sha256:
        raise _error("input-stale", "final proof index binding hash differs from the close proof")

    raw_children = value.get("expected_children")
    if not isinstance(raw_children, list):
        raise _error("proof-incomplete", "final proof index must list expected_children")
    children: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for index, child in enumerate(raw_children):
        identity = _issue_identity(
            child,
            repo=repo,
            parent_number=parent_number,
            context=f"final proof index.expected_children[{index}]",
        )
        if identity["number"] == parent_number:
            raise _error(
                "parent-mismatch",
                f"final proof index.expected_children[{index}] must identify a child, not the Goal Run parent",
            )
        key = (identity["repo"].lower(), identity["number"])
        if key in seen:
            raise _error("proof-incomplete", "final proof index repeats an expected child identity")
        seen.add(key)
        children.append(identity)

    parent_obligation = _issue_identity(
        value.get("parent_obligation"),
        repo=repo,
        parent_number=parent_number,
        context="final proof index.parent_obligation",
    )
    if parent_obligation["number"] != parent_number:
        raise _error("parent-mismatch", "final proof index parent_obligation must identify the Goal Run parent")
    return {
        "path": str(path),
        "sha256": digest,
        "kind": FINAL_PROOF_INDEX_KIND,
        "repo": repo,
        "parent_number": parent_number,
        "draft_sha256": draft_sha256,
        "binding_sha256": binding_sha256,
        "expected_children": children,
        "parent_obligation": parent_obligation,
    }


def load_operation(path: Path, *, repo: str, parent_number: int) -> dict[str, Any]:
    value, digest = _read_json(path, kind=OPERATION_KIND)
    _fields(
        value,
        {
            "kind", "repo", "parent_number", "operation", "attempt_id", "draft_sha256",
            "binding_sha256", "observation_dir", "target", "body_file", "expected_child_file", "result",
        },
        "operation",
    )
    if _repo(value.get("repo"), "operation.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "operation repository differs from the requested repository")
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
    if operation == "create-or-reuse-child" and not {"work_item_key", "title"}.issubset(target):
        raise _error("schema-invalid", "create-or-reuse-child target requires work_item_key and title")
    if operation in {"add-child", "remove-child"} and "sub_issue_number" not in target:
        raise _error("schema-invalid", f"{operation} target requires sub_issue_number")
    if operation in {"add-child", "remove-child"} and "work_item_key" not in target:
        raise _error("schema-invalid", f"{operation} target requires work_item_key")
    if operation == "record-observation" and not isinstance(value.get("result"), dict):
        raise _error("schema-invalid", "record-observation requires a result object")
    return {**value, "path": str(path), "sha256": digest, "target": target, "operation": operation}


def _validate_close_proof_children(value: Any, *, repo: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise _error("proof-incomplete", "close proof must list every linked child")
    seen_children: set[tuple[str, int]] = set()
    for index, child in enumerate(value):
        if not isinstance(child, dict):
            raise _error("proof-incomplete", f"close proof child {index} is not an object")
        _fields(child, {"repo", "number", "evidence"}, f"close proof child {index}")
        child_repo = _repo(child.get("repo"), f"close proof child {index}.repo")
        if child_repo.lower() != repo.lower():
            raise _error("parent-mismatch", f"close proof child {index} has a foreign repository")
        child_number = _positive(child.get("number"), f"close proof child {index}.number")
        child_key = (child_repo.lower(), child_number)
        if child_key in seen_children:
            raise _error("proof-incomplete", "close proof repeats a child identity")
        seen_children.add(child_key)
        evidence = child.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"kind", "identity"}:
            raise _error(
                "proof-incomplete",
                f"close proof child {index} needs issue-owned evidence identity",
            )
        if evidence.get("kind") not in {
            "issue-owned-closeout/v1",
            "verified-successor-deferral/v1",
        }:
            raise _error(
                "proof-incomplete",
                f"close proof child {index} has an unsupported evidence kind",
            )
        if not isinstance(evidence.get("identity"), str) or not evidence["identity"].strip():
            raise _error(
                "proof-incomplete",
                f"close proof child {index} evidence identity is empty",
            )
    return value


def _validate_close_proof_fields(
    value: dict[str, Any], *, repo: str, parent_number: int
) -> list[dict[str, Any]]:
    _fields(
        value,
        {
            "kind", "repo", "parent_number", "attempt_id", "draft_sha256", "binding_sha256",
            "observation_dir", "comment_file", "classification", "reason", "manual_target_declaration",
            "whole_system_proof", "children", "comment_sha256", "final_proof_index_file",
            "final_proof_index_sha256",
        },
        "close proof",
    )
    if _repo(value.get("repo"), "close proof.repo").lower() != repo.lower():
        raise _error("parent-mismatch", "close proof repository differs from the requested repository")
    if _positive(value.get("parent_number"), "close proof.parent_number") != parent_number:
        raise _error("parent-mismatch", "close proof parent differs from the requested parent")
    if not isinstance(value.get("attempt_id"), str) or not ATTEMPT_RE.fullmatch(value["attempt_id"]):
        raise _error("identity-invalid", "close proof.attempt_id has unsupported syntax")
    _sha(value.get("draft_sha256"), "close proof.draft_sha256")
    _sha(value.get("binding_sha256"), "close proof.binding_sha256")
    if not isinstance(value.get("observation_dir"), str) or not value["observation_dir"].strip():
        raise _error("path-invalid", "close proof.observation_dir must be non-empty text")
    if not isinstance(value.get("comment_file"), str) or not value["comment_file"].strip():
        raise _error("input-missing", "close proof requires comment_file")
    _sha(value.get("comment_sha256"), "close proof.comment_sha256")
    if not isinstance(value.get("final_proof_index_file"), str) or not value["final_proof_index_file"].strip():
        raise _error("input-missing", "close proof requires final_proof_index_file")
    _sha(value.get("final_proof_index_sha256"), "close proof.final_proof_index_sha256")
    if value.get("whole_system_proof") is not True:
        raise _error("proof-incomplete", "close proof must assert whole_system_proof: true")
    return _validate_close_proof_children(value.get("children"), repo=repo)


def _validate_bound_close_inputs(
    value: dict[str, Any],
    result: dict[str, Any],
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    children: list[dict[str, Any]],
) -> None:
    root = repo_root.resolve()
    proof_path = repo_file(root, result["path"], context="proof_file")
    if proof_path != Path(result["path"]).resolve():
        raise _error("path-invalid", "close proof must be contained by the repository root")
    comment_path = repo_file(root, value["comment_file"], context="close proof comment_file")
    try:
        comment_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise _error("input-invalid", "close proof comment_file is not valid UTF-8 text") from exc
    comment_digest = hashlib.sha256(comment_path.read_bytes()).hexdigest()
    if comment_digest != value["comment_sha256"]:
        raise _error(
            "input-stale",
            "close proof comment bytes do not match its declared SHA-256: "
            f"expected {value['comment_sha256']}, got {comment_digest}",
        )
    observation_dir = repo_file(
        root, value["observation_dir"], context="close proof observation_dir", must_exist=False
    )
    if observation_dir.exists() and not observation_dir.is_dir():
        raise _error("path-invalid", "close proof observation_dir must name a directory")
    index_path = repo_file(
        root, value["final_proof_index_file"], context="close proof final_proof_index_file"
    )
    final_index = load_final_proof_index(
        index_path,
        repo_root=root,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=value["draft_sha256"],
        binding_sha256=value["binding_sha256"],
        sha256=value["final_proof_index_sha256"],
    )
    proof_children = sorted(
        ({"repo": child["repo"], "number": child["number"]} for child in children),
        key=lambda child: (child["repo"].lower(), child["number"]),
    )
    if proof_children != sorted(
        final_index["expected_children"],
        key=lambda child: (child["repo"].lower(), child["number"]),
    ):
        raise _error(
            "evidence-mismatch",
            "close proof children do not match the separately bound final proof index",
        )
    result.update(
        comment_path=str(comment_path),
        observation_dir_path=str(observation_dir),
        final_proof_index=final_index,
    )


def load_close_proof(
    path: Path,
    *,
    repo: str,
    parent_number: int,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    value, digest = _read_json(path, kind=CLOSE_PROOF_KIND)
    children = _validate_close_proof_fields(value, repo=repo, parent_number=parent_number)
    result: dict[str, Any] = {**value, "path": str(path), "sha256": digest}
    if repo_root is not None:
        _validate_bound_close_inputs(
            value,
            result,
            repo_root=repo_root,
            repo=repo,
            parent_number=parent_number,
            children=children,
        )
    return result


def capability_report(
    backend: dict[str, Any], operations: list[str] | None = None, *, repo: str
) -> dict[str, Any]:
    requested = operations or list(OPERATIONS)
    required = sorted({name for operation in requested for name in BACKEND_REQUIREMENTS[operation]})
    probe_repo = repo
    probes: dict[str, Any] = {
        "create": lambda: BACKEND.resolve_op(backend, "create", CREATE.GH_CREATE_DEFAULT, CREATE.CREATE_PLACEHOLDERS, required=frozenset({"repo", "title", "body_file"}), repo=probe_repo, title="probe", body_file="/tmp/body"),
        "view": lambda: BACKEND.resolve_op(backend, "view", READ.GH_READ_DEFAULT, READ.VIEW_PLACEHOLDERS, required=frozenset({"repo", "number", "json_fields"}), repo=probe_repo, number="1", json_fields="number,body,comments,state,url"),
        "discover_managed_issues": lambda: BACKEND.resolve_op(backend, "discover_managed_issues", TRACKER.GH_DISCOVER_MANAGED_ISSUES_DEFAULT, TRACKER.DISCOVER_MANAGED_ISSUES_PLACEHOLDERS, required=frozenset({"repo"}), repo=probe_repo),
        "update": lambda: BACKEND.resolve_op(backend, "update", TRACKER.GH_UPDATE_DEFAULT, TRACKER.UPDATE_PLACEHOLDERS, required=frozenset({"repo", "number", "body_file"}), repo=probe_repo, number="1", body_file="/tmp/body"),
        "list_sub_issues": lambda: BACKEND.resolve_op(backend, "list_sub_issues", TRACKER.GH_LIST_SUB_ISSUES_DEFAULT, TRACKER.LIST_SUB_ISSUES_PLACEHOLDERS, required=frozenset({"repo", "number"}), repo=probe_repo, number="1"),
        "resolve_issue_id": lambda: BACKEND.resolve_op(backend, "resolve_issue_id", TRACKER.GH_RESOLVE_ISSUE_ID_DEFAULT, TRACKER.RESOLVE_ISSUE_ID_PLACEHOLDERS, required=frozenset({"repo", "sub_issue_number"}), repo=probe_repo, sub_issue_number="2"),
        "add_sub_issue": lambda: BACKEND.resolve_op(backend, "add_sub_issue", TRACKER.GH_ADD_SUB_ISSUE_DEFAULT, TRACKER.MUTATE_SUB_ISSUE_PLACEHOLDERS, required=frozenset({"repo", "number", "sub_issue_id"}), repo=probe_repo, number="1", sub_issue_id="2", sub_issue_number="2"),
        "remove_sub_issue": lambda: BACKEND.resolve_op(backend, "remove_sub_issue", TRACKER.GH_REMOVE_SUB_ISSUE_DEFAULT, TRACKER.MUTATE_SUB_ISSUE_PLACEHOLDERS, required=frozenset({"repo", "number", "sub_issue_id"}), repo=probe_repo, number="1", sub_issue_id="2", sub_issue_number="2"),
        "comment": lambda: BACKEND.resolve_op(backend, "comment", CLOSE.GH_COMMENT_DEFAULT, CLOSE.COMMENT_PLACEHOLDERS, required=frozenset({"repo", "number", "body_file"}), repo=probe_repo, number="1", body_file="/tmp/body", reason="completed"),
        "close": lambda: BACKEND.resolve_op(backend, "close", CLOSE.GH_CLOSE_DEFAULT, CLOSE.CLOSE_PLACEHOLDERS, required=frozenset({"repo", "number"}), repo=probe_repo, number="1", reason="completed"),
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
        or all(declared.get(name, False) and name not in template_errors for name in BACKEND_REQUIREMENTS[operation])
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
