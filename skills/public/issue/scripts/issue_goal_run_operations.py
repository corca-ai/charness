"""Execute one validated Goal Run provider operation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

OUTCOMES = {
    "started",
    "no-write",
    "verified-write",
    "unverified-write",
    "partial-graph",
    "verified-read",
    "refused",
}


def _read_one(repo: str, number: int, backend: dict[str, Any], operation: str, *, read: Any) -> dict[str, Any]:
    issue = read.read_issue_with_comments(repo, number, backend=backend)["issue"]
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


def _expected_graph(
    result: dict[str, Any],
    operation: dict[str, Any],
    repo_root: Path,
    repo: str,
    parent: int,
    *,
    contract: Any,
    tracker: Any,
) -> dict[str, Any]:
    expected_file = operation.get("expected_child_file")
    if not isinstance(expected_file, str):
        return result
    path = contract.repo_file(repo_root, expected_file, context="expected_child_file")
    expected_source = tracker.load_expected_child_set(path, repo=repo, parent_number=parent)
    actual = sorted(child["number"] for child in result["children"])
    expected = expected_source["children"]
    result["expected_children"] = expected
    result["expected_children_source"] = expected_source
    result["missing_children"] = [number for number in expected if number not in actual]
    result["unexpected_children"] = [number for number in actual if number not in expected]
    if result["missing_children"] or result["unexpected_children"]:
        result.update(ok=False, status="graph-mismatch", next_action="reconcile-exact-child-identities")
    return result


def execute(
    operation: dict[str, Any],
    *,
    binding: dict[str, Any] | None,
    repo_root: Path,
    backend: dict[str, Any],
    repo: str,
    parent: int,
    contract: Any,
    read: Any,
    tracker: Any,
    observation: Any,
    guard: Any,
) -> dict[str, Any]:
    """Dispatch a validated operation using the provider dependencies supplied by the caller."""
    name = operation["operation"]
    target = operation["target"]
    if name in {"read-body", "read-state"}:
        return _read_one(repo, target["number"], backend, name, read=read)
    if name == "update-body":
        body_file = contract.repo_file(repo_root, operation["body_file"], context="body_file")
        if target["number"] == parent:
            assert binding is not None
            authorization_file = (
                contract.repo_file(
                    repo_root,
                    operation["amendment_authorization_file"],
                    context="amendment_authorization_file",
                )
                if operation.get("amendment_authorization_file") is not None
                else None
            )
            return tracker.update_issue_body(
                repo,
                target["number"],
                body_file,
                backend=backend,
                parent_amendment_validator=contract.BINDING.parent_body_validator(
                    binding,
                    repo=repo,
                    parent_number=parent,
                    guard=guard,
                    amendment_authorization_file=authorization_file,
                ),
            )
        return tracker.update_issue_body(
            repo,
            target["number"],
            body_file,
            backend=backend,
            expected_body_sha256=operation["observed_body_sha256"],
        )
    if name == "create-or-reuse-child":
        body_file = contract.repo_file(repo_root, operation["body_file"], context="body_file")
        body_sha = hashlib.sha256(body_file.read_bytes()).hexdigest()
        unresolved = observation.find_unresolved_create(
            repo_root=repo_root,
            observation_dir=Path(operation["observation_dir"]),
            repo=repo,
            parent_number=parent,
            work_item_key=target["work_item_key"],
            submitted_body_sha256=body_sha,
            exclude_attempt_id=operation["attempt_id"],
        )
        return tracker.create_or_reuse_child(
            repo,
            parent,
            target["work_item_key"],
            target["title"],
            body_file,
            backend=backend,
            prior_unresolved_observation=unresolved,
        )
    if name == "list-children":
        result = tracker.list_sub_issues(repo, parent, backend=backend)
        return _expected_graph(
            result,
            operation,
            repo_root,
            repo,
            parent,
            contract=contract,
            tracker=tracker,
        )
    if name in {"add-child", "remove-child"}:
        assert binding is not None
        metadata = operation.get("parent_metadata")
        if operation.get("amendment_entry") is None:
            item = contract.BINDING.work_item_for_target(
                binding, target["work_item_key"], metadata=metadata
            )
            if item["intent"] == "create":
                issue = read.read_issue_with_comments(
                    repo, target["sub_issue_number"], backend=backend
                )["issue"]
                contract.BINDING.require_issue_matches_item(
                    binding, key=item["key"], number=target["sub_issue_number"], issue=issue
                )
        mutate = tracker.add_sub_issue if name == "add-child" else tracker.remove_sub_issue
        return mutate(repo, parent, target["sub_issue_number"], backend=backend)
    if name == "record-observation":
        result = dict(operation["result"])
        result.setdefault("status", "local-only")
        result.setdefault("operation", name)
        result.setdefault("mutation_invoked", False)
        return result
    raise RuntimeError(f"unsupported Goal Run operation: {name}")


def normalise_result(result: dict[str, Any], operation: str) -> dict[str, Any]:
    result = dict(result)
    result.setdefault("operation", operation)
    result.setdefault("mutation_invoked", False)
    outcome = result.get("outcome")
    if outcome not in OUTCOMES:
        raise RuntimeError(f"provider result has unsupported outcome: {outcome!r}")
    if outcome == "verified-write" and not result["mutation_invoked"]:
        raise RuntimeError("verified-write requires mutation_invoked: true")
    return result
