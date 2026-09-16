"""Execute one validated Goal Run provider operation."""

from __future__ import annotations

import hashlib
import json
import tempfile
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


def _read_one(
    repo: str, number: int, backend: dict[str, Any], operation: str, *, read: Any
) -> dict[str, Any]:
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
        result["body"] = body
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
        result.update(
            ok=False, status="graph-mismatch", next_action="reconcile-exact-child-identities"
        )
    return result


def _render_revision_body(
    current_parent_body: str, entry: dict[str, Any], *, guard: Any
) -> tuple[str, bool]:
    """Append one body revision to the parent metadata block, idempotently.

    Returns the desired parent body and whether it differs. The human prose is
    untouched, so the parent-body validator accepts the change without an
    amendment authorization receipt.
    """
    metadata = guard.parse_goal_run_metadata(current_parent_body, context="Goal Run parent body")
    if metadata is None:
        raise RuntimeError("target parent does not carry Goal Run metadata")
    revisions = list(metadata.get("body_revisions") or [])
    for revision in revisions:
        if (
            revision.get("key") == entry["key"]
            and revision.get("number") == entry["number"]
            and revision.get("body_sha256") == entry["body_sha256"]
        ):
            # Retry-safe: this authorized digest is already the recorded state
            # for the item, so re-recording would only grow the chain.
            return current_parent_body, False
    updated = dict(metadata)
    updated["body_revisions"] = [*revisions, entry]
    # parse_goal_run_metadata above already refused anything but exactly one
    # metadata block, so the match below always exists; no second guard here.
    match = next(iter(guard.BLOCK_RE.finditer(current_parent_body)))
    rendered = (
        "<!-- charness-goal-run:v1\n"
        + json.dumps(updated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n-->"
    )
    return current_parent_body[: match.start()] + rendered + current_parent_body[match.end() :], True


def _record_body_revision(
    *,
    repo_root: Path,
    repo: str,
    parent: int,
    key: str,
    number: int,
    submitted_sha256: str,
    supersedes_sha256: str,
    backend: dict[str, Any],
    binding: dict[str, Any],
    contract: Any,
    read: Any,
    tracker: Any,
    guard: Any,
) -> dict[str, Any]:
    """Record-first revision write: the parent chain entry lands before the child body.

    Ordering is the safety property. If the parent record fails, the child is
    never written, so the live body still descends from the existing chain. If
    the child write fails afterwards, the chain holds one unused authorized
    entry, which closeout harmlessly ignores. A concurrent parent modification
    refuses here via the pre-write digest instead of silently dropping a
    sibling revision.
    """
    entry = {
        "key": key,
        "number": number,
        "body_sha256": submitted_sha256,
        "supersedes_sha256": supersedes_sha256,
    }
    parent_issue = read.read_issue_with_comments(repo, parent, backend=backend)["issue"]
    current_parent_body = parent_issue.get("body")
    if not isinstance(current_parent_body, str):
        raise RuntimeError("Goal Run parent body readback did not return a string body")
    parent_sha256 = hashlib.sha256(current_parent_body.encode("utf-8")).hexdigest()
    desired_parent_body, changed = _render_revision_body(current_parent_body, entry, guard=guard)
    if not changed:
        return {"entry": entry, "recorded": False}
    assert binding is not None
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=repo_root,
        prefix=".body-revision-",
        suffix=".md",
        delete=False,
    ) as handle:
        parent_body_file = Path(handle.name)
        handle.write(desired_parent_body)
    try:
        update = tracker.update_issue_body(
            repo,
            parent,
            parent_body_file,
            backend=backend,
            expected_body_sha256=parent_sha256,
            parent_amendment_validator=contract.BINDING.parent_body_validator(
                binding,
                repo=repo,
                parent_number=parent,
                guard=guard,
            ),
        )
    finally:
        parent_body_file.unlink(missing_ok=True)
    if update.get("ok") is not True:
        raise RuntimeError(
            "managed body revision was not recorded on the parent: "
            f"{update.get('error') or update.get('outcome') or update.get('status')}"
        )
    return {"entry": entry, "recorded": True}


def _update_managed_body(
    operation: dict[str, Any],
    *,
    repo_root: Path,
    repo: str,
    parent: int,
    body_file: Path,
    backend: dict[str, Any],
    binding: dict[str, Any] | None,
    contract: Any,
    read: Any,
    tracker: Any,
    guard: Any,
) -> dict[str, Any]:
    """Authorized managed-body update: record the revision, then write the child."""
    target = operation["target"]
    submitted_sha256 = hashlib.sha256(body_file.read_bytes()).hexdigest()
    live_child = read.read_issue_with_comments(repo, target["number"], backend=backend)["issue"]
    live_child_body = live_child.get("body")
    if not isinstance(live_child_body, str):
        raise RuntimeError("managed child body readback did not return a string body")
    supersedes_sha256 = hashlib.sha256(live_child_body.encode("utf-8")).hexdigest()
    record = _record_body_revision(
        repo_root=repo_root,
        repo=repo,
        parent=parent,
        key=target["work_item_key"],
        number=target["number"],
        submitted_sha256=submitted_sha256,
        supersedes_sha256=supersedes_sha256,
        backend=backend,
        binding=binding,
        contract=contract,
        read=read,
        tracker=tracker,
        guard=guard,
    )
    # Compare-and-swap on the digest read before recording: a concurrent child
    # edit in between refuses here instead of being silently overwritten under
    # a recorded supersession edge that never happened. The unused chain entry
    # stays harmless, and closeout fails closed on the unrecorded live body.
    result = tracker.update_issue_body(
        repo,
        target["number"],
        body_file,
        backend=backend,
        expected_body_sha256=supersedes_sha256,
    )
    result = dict(result)
    result["body_revision"] = record["entry"]
    result["body_revision_recorded"] = record["recorded"]
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
        return _update_managed_body(
            operation,
            repo_root=repo_root,
            repo=repo,
            parent=parent,
            body_file=body_file,
            backend=backend,
            binding=binding,
            contract=contract,
            read=read,
            tracker=tracker,
            guard=guard,
        )
    if name == "create-or-reuse-child":
        body_file = contract.repo_file(repo_root, operation["body_file"], context="body_file")
        unresolved = observation.find_unresolved_create(
            repo_root=repo_root,
            observation_dir=Path(operation["observation_dir"]),
            repo=repo,
            parent_number=parent,
            work_item_key=target["work_item_key"],
            submitted_body_sha256=None,
            exclude_attempt_id=operation["attempt_id"],
            # Goal Run create recovery is marker/issue identity based.
            compare_submitted_body=False,
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
