"""Adapter-routed, file-backed Goal Run provider operations."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](
    __file__
)
CONTRACT = _load_local("issue_goal_run_contract")
BACKEND = CONTRACT.BACKEND
READ = _load_local("issue_read", "issue_goal_run_read")
TRACKER = _load_local("issue_tracker", "issue_goal_run_tracker")
OBSERVATION = _load_local("issue_tracker_observation", "issue_goal_run_observation")

OBSERVATION_KIND = "charness.goal-run-observation/v1"
OUTCOMES = {"started", "no-write", "verified-write", "unverified-write", "partial-graph", "verified-read", "refused"}


def _refusal(code: str, message: str, *, repo: str, parent_number: int) -> dict[str, Any]:
    return {
        "ok": False,
        "kind": "charness.goal-run-provider/v1",
        "status": code,
        "outcome": "refused",
        "mutation_invoked": False,
        "repo": repo,
        "parent_number": parent_number,
        "error_code": code,
        "error": message,
        "next_action": "repair-input-or-provider-readiness-before-retry",
    }


def _parent_summary(issue: dict[str, Any], *, repo: str, number: int) -> dict[str, Any]:
    body = issue.get("body")
    return {
        "repo": repo,
        "number": issue.get("number", number),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "url": issue.get("url"),
        "updated_at": issue.get("updatedAt"),
        "body": body,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest() if isinstance(body, str) else None,
        "comment_count": len(issue.get("comments", [])) if isinstance(issue.get("comments"), list) else None,
    }


def _read_graph(repo: str, parent_number: int, backend: dict[str, Any]) -> dict[str, Any]:
    parent_read = READ.read_issue_with_comments(repo, parent_number, backend=backend)
    parent = _parent_summary(parent_read["issue"], repo=repo, number=parent_number)
    graph = TRACKER.list_sub_issues(repo, parent_number, backend=backend)
    return {
        "ok": True,
        "kind": "charness.goal-run-read/v1",
        "status": "verified-read",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "repo": repo,
        "parent_number": parent_number,
        "parent": parent,
        "children": graph["children"],
        "graph": graph,
    }


def _preflight(
    *,
    repo: str,
    parent_number: int,
    operations: list[str],
    resolved: dict[str, Any],
    read_parent: bool = True,
) -> dict[str, Any]:
    capability = CONTRACT.capability_report(resolved["backend"], operations)
    readiness = BACKEND.build_preflight_payload(resolved)
    result: dict[str, Any] = {
        "repo": repo,
        "parent_number": parent_number,
        "backend_readiness": readiness,
        "capability": capability,
        "parent": None,
        "error": None,
    }
    if not resolved.get("adapter_ok"):
        result.update(ok=False, status="adapter-invalid", outcome="refused", mutation_invoked=False)
        result["error"] = "issue adapter is invalid"
        return result
    if not capability["ok"]:
        result.update(ok=False, status="capability-missing", outcome="refused", mutation_invoked=False)
        result["error"] = "requested Goal Run operation is not fully declared by the selected backend"
        return result
    if not readiness.get("ok"):
        result.update(ok=False, status="backend-unavailable", outcome="refused", mutation_invoked=False)
        result["error"] = readiness.get("error") or "selected backend is unavailable"
        return result
    if read_parent:
        try:
            parent = READ.read_issue_with_comments(repo, parent_number, backend=resolved["backend"])["issue"]
            result["parent"] = _parent_summary(parent, repo=repo, number=parent_number)
        except RuntimeError as exc:
            result.update(ok=False, status="parent-unverified", outcome="refused", mutation_invoked=False)
            result["error"] = str(exc)
            return result
    result.update(ok=True, status="ready", outcome="verified-read", mutation_invoked=False)
    return result


def command_preflight(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        plan = CONTRACT.load_plan(args.plan_file.resolve(), repo=args.repo, parent_number=args.number)
    except CONTRACT.GoalRunInputError as exc:
        emit(_refusal(exc.code, str(exc), repo=args.repo, parent_number=args.number))
        return 2
    resolved = resolve_backend(args.repo_root.resolve())
    result = _preflight(
        repo=args.repo,
        parent_number=args.number,
        operations=plan["operations"],
        resolved=resolved,
    )
    result.update(
        kind="charness.goal-run-preflight/v1",
        plan={"path": plan["path"], "sha256": plan["sha256"], "operations": plan["operations"]},
    )
    emit(result)
    return 0 if result["ok"] else 1


def command_read(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    resolved = resolve_backend(args.repo_root.resolve())
    if not resolved.get("adapter_ok"):
        result = _refusal("adapter-invalid", "issue adapter is invalid", repo=args.repo, parent_number=args.number)
    else:
        preflight = _preflight(
            repo=args.repo,
            parent_number=args.number,
            operations=["read-body", "read-state", "list-children"],
            resolved=resolved,
        )
        if not preflight["ok"]:
            result = {"kind": "charness.goal-run-read/v1", **preflight}
        else:
            try:
                result = _read_graph(args.repo, args.number, resolved["backend"])
            except RuntimeError as exc:
                result = _refusal("readback-failed", str(exc), repo=args.repo, parent_number=args.number)
    result["selected_backend"] = resolved.get("backend")
    emit(result)
    return 0 if result["ok"] else 2


def _read_one(repo: str, number: int, backend: dict[str, Any], operation: str) -> dict[str, Any]:
    read = READ.read_issue_with_comments(repo, number, backend=backend)
    issue = read["issue"]
    result: dict[str, Any] = {
        "ok": True,
        "status": "verified-read",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "operation": operation,
        "repo": repo,
        "number": number,
        "state": issue.get("state"),
        "url": issue.get("url"),
    }
    if operation == "read-body":
        body = issue.get("body")
        if not isinstance(body, str):
            raise RuntimeError("Goal Run body readback did not return a string body")
        result.update(body=body, body_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest())
    return result


def _expected_graph(result: dict[str, Any], operation: dict[str, Any], repo_root: Path, repo: str, parent: int) -> dict[str, Any]:
    expected_file = operation.get("expected_child_file")
    if not isinstance(expected_file, str):
        return result
    path = CONTRACT.repo_file(repo_root, expected_file, context="expected_child_file")
    expected_source = TRACKER.load_expected_child_set(path, repo=repo, parent_number=parent)
    actual = sorted(child["number"] for child in result["children"])
    expected = expected_source["children"]
    result["expected_children"] = expected
    result["expected_children_source"] = expected_source
    result["missing_children"] = [number for number in expected if number not in actual]
    result["unexpected_children"] = [number for number in actual if number not in expected]
    if result["missing_children"] or result["unexpected_children"]:
        result.update(ok=False, status="graph-mismatch", next_action="reconcile-exact-child-identities")
    return result


def _execute(operation: dict[str, Any], *, repo_root: Path, backend: dict[str, Any], repo: str, parent: int) -> dict[str, Any]:
    name = operation["operation"]
    target = operation["target"]
    if name in {"read-body", "read-state"}:
        return _read_one(repo, target["number"], backend, name)
    if name == "update-body":
        body_file = CONTRACT.repo_file(repo_root, operation["body_file"], context="body_file")
        return TRACKER.update_issue_body(repo, target["number"], body_file, backend=backend)
    if name == "create-or-reuse-child":
        body_file = CONTRACT.repo_file(repo_root, operation["body_file"], context="body_file")
        body_sha = hashlib.sha256(body_file.read_bytes()).hexdigest()
        unresolved = OBSERVATION.find_unresolved_create(
            repo_root=repo_root,
            observation_dir=Path(operation["observation_dir"]),
            repo=repo,
            parent_number=parent,
            work_item_key=target["work_item_key"],
            submitted_body_sha256=body_sha,
            exclude_attempt_id=operation["attempt_id"],
        )
        return TRACKER.create_or_reuse_child(
            repo,
            parent,
            target["work_item_key"],
            target["title"],
            body_file,
            backend=backend,
            prior_unresolved_observation=unresolved,
        )
    if name == "list-children":
        result = TRACKER.list_sub_issues(repo, parent, backend=backend)
        return _expected_graph(result, operation, repo_root, repo, parent)
    if name == "add-child":
        return TRACKER.add_sub_issue(repo, parent, target["sub_issue_number"], backend=backend)
    if name == "remove-child":
        return TRACKER.remove_sub_issue(repo, parent, target["sub_issue_number"], backend=backend)
    if name == "record-observation":
        result = dict(operation["result"])
        result.setdefault("status", "local-only")
        result.setdefault("operation", name)
        result.setdefault("mutation_invoked", False)
        return result
    raise RuntimeError(f"unsupported Goal Run operation: {name}")


def _normalise_result(result: dict[str, Any], operation: str) -> dict[str, Any]:
    result = dict(result)
    result.setdefault("operation", operation)
    result.setdefault("mutation_invoked", False)
    outcome = result.get("outcome")
    if outcome not in OUTCOMES:
        raise RuntimeError(f"provider result has unsupported outcome: {outcome!r}")
    if outcome == "verified-write" and not result["mutation_invoked"]:
        raise RuntimeError("verified-write requires mutation_invoked: true")
    return result


def command_apply(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        operation = CONTRACT.load_operation(
            args.operation_file.resolve(), repo=args.repo, parent_number=args.number
        )
    except CONTRACT.GoalRunInputError as exc:
        emit(_refusal(exc.code, str(exc), repo=args.repo, parent_number=args.number))
        return 2
    resolved = resolve_backend(args.repo_root.resolve())
    name = operation["operation"]
    if name == "record-observation":
        preflight = {"ok": True, "status": "local-only", "outcome": "verified-read", "mutation_invoked": False}
    else:
        preflight = _preflight(
            repo=args.repo,
            parent_number=args.number,
            operations=[name],
            resolved=resolved,
        )
    if not preflight["ok"]:
        result = {"kind": "charness.goal-run-apply/v1", **preflight}
        result["selected_backend"] = resolved.get("backend")
        emit(result)
        return 2
    body_path = None
    if isinstance(operation.get("body_file"), str):
        body_path = CONTRACT.repo_file(args.repo_root.resolve(), operation["body_file"], context="body_file")
    try:
        started = OBSERVATION.begin(
            repo_root=args.repo_root.resolve(),
            observation_dir=Path(operation["observation_dir"]),
            attempt_id=operation["attempt_id"],
            draft_sha256=operation["draft_sha256"],
            binding_sha256=operation["binding_sha256"],
            repo=args.repo,
            parent_number=args.number,
            operation=name,
            target=operation["target"],
            submitted_body_sha256=hashlib.sha256(body_path.read_bytes()).hexdigest() if body_path else None,
            backend=resolved.get("backend", {}),
        )
    except (RuntimeError, OSError) as exc:
        result = _refusal("observation-refused", str(exc), repo=args.repo, parent_number=args.number)
        result["selected_backend"] = resolved.get("backend")
        emit(result)
        return 2
    try:
        result = _normalise_result(
            _execute(operation, repo_root=args.repo_root.resolve(), backend=resolved["backend"], repo=args.repo, parent=args.number),
            name,
        )
    except RuntimeError as exc:
        result = _refusal("provider-refused", str(exc), repo=args.repo, parent_number=args.number)
    result["selected_backend"] = resolved.get("backend")
    try:
        terminal = OBSERVATION.finish(
            repo_root=args.repo_root.resolve(),
            observation_dir=Path(operation["observation_dir"]),
            attempt_id=operation["attempt_id"],
            started=started,
            result=result,
        )
        result["observation"] = {
            "started_path": started["path"],
            "started_sha256": started["payload"]["receipt_sha256"],
            "terminal_path": terminal["path"],
            "terminal_sha256": terminal["payload"]["receipt_sha256"],
        }
    except RuntimeError as exc:
        result = {
            **_refusal("observation-unverified", str(exc), repo=args.repo, parent_number=args.number),
            "mutation_invoked": bool(result.get("mutation_invoked")),
            "started_observation": started,
            "selected_backend": resolved.get("backend"),
        }
    result.update(kind="charness.goal-run-apply/v1", attempt_id=operation["attempt_id"])
    emit(result)
    return 0 if result["ok"] else 2
