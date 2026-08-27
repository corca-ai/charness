"""Read-only tracker capability, backend, and exact-parent preflight."""

from __future__ import annotations

import argparse
from typing import Any


def _preflight_status(payload: dict[str, Any]) -> str:
    selected = payload["selected_backend"]
    if "found" not in selected:
        return "backend-probe-failed"
    if payload["ok"]:
        return "ready"
    if selected["found"]:
        return "found-but-not-authenticated-or-unhealthy"
    return "backend-binary-missing"


def run(
    args: argparse.Namespace,
    *,
    resolve_backend: Any,
    emit: Any,
    tracker: Any,
    backend_owner: Any,
    issue_reader: Any,
) -> int:
    try:
        resolved = resolve_backend(args.repo_root.resolve())
    except RuntimeError as exc:
        emit(
            {
                "kind": "charness.goal-run-bootstrap-preflight/v1",
                "ok": False,
                "status": "provider-selection-invalid",
                "outcome": "refused",
                "mutation_invoked": False,
                "repo": args.repo,
                "parent_number": args.number,
                "error": str(exc),
            }
        )
        return 2
    target_repo = str(resolved.get("target_repo") or args.repo)
    capability = tracker.tracker_capability_report(resolved["backend"], repo=target_repo)
    readiness = backend_owner.build_preflight_payload(resolved)
    selected = readiness.get("selected_backend") or {}
    projected_readiness = {
        "ok": bool(readiness.get("ok")),
        "status": _preflight_status(readiness)
        if isinstance(selected, dict)
        else "backend-probe-failed",
        "id": selected.get("id") if isinstance(selected, dict) else None,
        "binary": selected.get("binary") if isinstance(selected, dict) else None,
        "found": selected.get("found") if isinstance(selected, dict) else None,
        "auth_verified": bool(
            isinstance(selected, dict)
            and isinstance(selected.get("auth_status"), dict)
            and selected["auth_status"].get("exit_code") == 0
        ),
        "version_verified": bool(
            isinstance(selected, dict)
            and isinstance(selected.get("version"), dict)
            and selected["version"].get("exit_code") == 0
        ),
    }
    status = "ready"
    parent: dict[str, Any] | None = None
    error: str | None = None
    if not resolved["adapter_ok"]:
        status = "adapter-invalid"
    elif not capability["ok"]:
        status = "tracker-capability-missing"
    elif not readiness.get("ok"):
        status = "backend-unavailable"
    else:
        try:
            issue = issue_reader.read_issue_with_comments(
                target_repo, args.number, backend=resolved["backend"]
            )["issue"]
            parent = {
                "repo": target_repo,
                "number": issue["number"],
                "state": issue.get("state"),
                "url": issue.get("url"),
                "updated_at": issue.get("updatedAt"),
            }
        except RuntimeError as exc:
            status = "repository-or-parent-unverified"
            error = str(exc)
    result = {
        "kind": "charness.goal-run-bootstrap-preflight/v1",
        "ok": status == "ready",
        "status": status,
        "outcome": "verified-read" if status == "ready" else "refused",
        "mutation_invoked": False,
        "repo": target_repo,
        "parent_number": args.number,
        "backend_readiness": projected_readiness,
        "operations": capability["operations"],
        "missing_operations": capability["missing_operations"],
        "template_errors": capability.get("template_errors", {}),
        "parent": parent,
        "error": error or readiness.get("error"),
    }
    emit(result)
    return 0 if result["ok"] else 1
