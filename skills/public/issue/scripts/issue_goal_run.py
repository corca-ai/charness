"""Adapter-routed, file-backed Goal Run provider operations."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
CONTRACT = _load_local("issue_goal_run_contract")
BACKEND = CONTRACT.BACKEND
READ = _load_local("issue_read", "issue_goal_run_read")
TRACKER = _load_local("issue_tracker", "issue_goal_run_tracker")
OBSERVATION = _load_local("issue_tracker_observation", "issue_goal_run_observation")
GUARD = _load_local("issue_goal_run_guard", "issue_goal_run_apply_guard")
OPERATIONS = _load_local("issue_goal_run_operations")


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
    summary = READ.normalise_sub_issues_summary(issue)
    result = {
        "repo": repo,
        "number": issue.get("number", number),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "url": issue.get("url"),
        "updated_at": issue.get("updatedAt"),
        "body": body,
        "comment_count": len(issue.get("comments", []))
        if isinstance(issue.get("comments"), list)
        else None,
    }
    if summary is not None:
        result["sub_issues_summary"] = summary
    return result


def _read_parent_metadata(
    repo: str, parent_number: int, *, backend: dict[str, Any]
) -> dict[str, Any] | None:
    """Read the parent's managed metadata; ``None`` means the body has no block yet."""
    try:
        issue = READ.read_issue_with_comments(repo, parent_number, backend=backend)["issue"]
        return GUARD.parse_goal_run_metadata(issue.get("body"), context="Goal Run parent body")
    except RuntimeError as exc:
        raise RuntimeError(f"could not read Goal Run parent identity: {exc}") from exc


def _is_metadata_bootstrap(operation: dict[str, Any], parent_number: int) -> bool:
    """The one operation allowed on a parent with no block: install the first block.

    A blockless parent has no identity to resolve, so every other operation is
    refused as ``parent-unverified``. A parent ``update-body`` that carries all
    three identities itself is the bootstrap write; the binding is then loaded
    from the operation's own identity and the desired body's block is validated
    against it before any provider mutation. This keeps establishment on the one
    file-backed provider surface instead of a second command for the first write.
    """
    return (
        operation["operation"] == "update-body"
        and operation["target"].get("number") == parent_number
        and all(
            operation.get(field) is not None
            for field in CONTRACT.OPERATION_IDENTITY_FIELDS
        )
    )


def _read_graph(repo: str, parent_number: int, backend: dict[str, Any]) -> dict[str, Any]:
    parent_read = READ.read_issue_with_comments(
        repo, parent_number, backend=backend, include_sub_issues_summary=True
    )
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
    capability = CONTRACT.capability_report(resolved["backend"], operations, repo=repo)
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
        result.update(
            ok=False, status="capability-missing", outcome="refused", mutation_invoked=False
        )
        result["error"] = (
            "requested Goal Run operation is not fully declared by the selected backend"
        )
        return result
    if not readiness.get("ok"):
        result.update(
            ok=False, status="backend-unavailable", outcome="refused", mutation_invoked=False
        )
        result["error"] = readiness.get("error") or "selected backend is unavailable"
        return result
    if read_parent:
        try:
            parent = READ.read_issue_with_comments(
                repo, parent_number, backend=resolved["backend"]
            )["issue"]
            result["parent"] = _parent_summary(parent, repo=repo, number=parent_number)
        except RuntimeError as exc:
            result.update(
                ok=False, status="parent-unverified", outcome="refused", mutation_invoked=False
            )
            result["error"] = str(exc)
            return result
    result.update(ok=True, status="ready", outcome="verified-read", mutation_invoked=False)
    return result


def command_preflight(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        plan = CONTRACT.load_plan(
            args.plan_file.resolve(), repo=args.repo, parent_number=args.number
        )
    except CONTRACT.GoalRunInputError as exc:
        emit(_refusal(exc.code, str(exc), repo=args.repo, parent_number=args.number))
        return 2
    try:
        resolved = resolve_backend(args.repo_root.resolve(), target_repo=args.repo)
    except RuntimeError as exc:
        emit(
            _refusal(
                "provider-selection-invalid", str(exc), repo=args.repo, parent_number=args.number
            )
        )
        return 2
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
    try:
        resolved = resolve_backend(args.repo_root.resolve(), target_repo=args.repo)
    except RuntimeError as exc:
        result = _refusal(
            "provider-selection-invalid", str(exc), repo=args.repo, parent_number=args.number
        )
        emit(result)
        return 2
    if not resolved.get("adapter_ok"):
        result = _refusal(
            "adapter-invalid", "issue adapter is invalid", repo=args.repo, parent_number=args.number
        )
    else:
        try:
            result = _read_graph(args.repo, args.number, resolved["backend"])
        except RuntimeError as exc:
            result = _refusal(
                "readback-failed", str(exc), repo=args.repo, parent_number=args.number
            )
    result["selected_backend"] = resolved.get("backend")
    emit(result)
    return 0 if result["ok"] else 2


def command_apply(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        operation = CONTRACT.load_operation(
            args.operation_file.resolve(), repo=args.repo, parent_number=args.number
        )
    except CONTRACT.GoalRunInputError as exc:
        emit(_refusal(exc.code, str(exc), repo=args.repo, parent_number=args.number))
        return 2
    name = operation["operation"]
    if name == "record-observation":
        # This operation is deliberately provider-free. It records a local fact and
        # must not make a remote readiness probe just because it shares the file
        # envelope with remote operations.
        backend = {"id": "local"}
        try:
            CONTRACT.require_record_observation_identity(operation)
        except CONTRACT.GoalRunInputError as exc:
            emit(_refusal(exc.code, str(exc), repo=args.repo, parent_number=args.number))
            return 2
        binding = None
        metadata_bootstrap = False
    else:
        try:
            resolved = resolve_backend(args.repo_root.resolve(), target_repo=args.repo)
        except RuntimeError as exc:
            emit(
                _refusal(
                    "provider-selection-invalid",
                    str(exc),
                    repo=args.repo,
                    parent_number=args.number,
                )
            )
            return 2
        if not resolved.get("adapter_ok"):
            result = _refusal(
                "adapter-invalid",
                "issue adapter is invalid",
                repo=args.repo,
                parent_number=args.number,
            )
            result["selected_backend"] = resolved.get("backend")
            emit(result)
            return 2
        backend = resolved["backend"]
        try:
            parent_metadata = _read_parent_metadata(args.repo, args.number, backend=backend)
            metadata_bootstrap = parent_metadata is None
            if metadata_bootstrap and not _is_metadata_bootstrap(operation, args.number):
                raise RuntimeError("Goal Run parent body has no managed metadata identity")
            binding = CONTRACT.validate_operation_binding(
                operation,
                args.repo_root.resolve(),
                parent_metadata=parent_metadata,
            )
        except (CONTRACT.GoalRunInputError, RuntimeError) as exc:
            code = exc.code if isinstance(exc, CONTRACT.GoalRunInputError) else "parent-unverified"
            result = _refusal(code, str(exc), repo=args.repo, parent_number=args.number)
            result["selected_backend"] = backend
            emit(result)
            return 2
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
            # Goal Run Work Item prose is not an operation identity; closeout
            # comments use this separate field for terminal proof.
            submitted_body_sha256=None,
            backend=backend,
        )
    except (RuntimeError, OSError) as exc:
        result = _refusal(
            "observation-refused", str(exc), repo=args.repo, parent_number=args.number
        )
        result["selected_backend"] = backend
        emit(result)
        return 2
    try:
        result = OPERATIONS.normalise_result(
            OPERATIONS.execute(
                operation,
                binding=binding,
                repo_root=args.repo_root.resolve(),
                backend=backend,
                repo=args.repo,
                parent=args.number,
                contract=CONTRACT,
                read=READ,
                tracker=TRACKER,
                observation=OBSERVATION,
                guard=GUARD,
            ),
            name,
        )
    except (RuntimeError, OSError) as exc:
        result = _refusal("provider-refused", str(exc), repo=args.repo, parent_number=args.number)
    result["selected_backend"] = backend
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
            **_refusal(
                "observation-unverified", str(exc), repo=args.repo, parent_number=args.number
            ),
            "mutation_invoked": bool(result.get("mutation_invoked")),
            "started_observation": started,
            "selected_backend": backend,
        }
    result.update(kind="charness.goal-run-apply/v1", attempt_id=operation["attempt_id"])
    if name != "record-observation" and metadata_bootstrap:
        result["parent_metadata_bootstrap"] = True
    emit(result)
    return 0 if result["ok"] else 2
