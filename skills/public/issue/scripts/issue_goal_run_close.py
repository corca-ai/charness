"""Dedicated, guarded Goal Run parent close ingress."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](
    __file__
)
CONTRACT = _load_local("issue_goal_run_contract")
READ = _load_local("issue_read", "issue_goal_run_close_read")
TRACKER = _load_local("issue_tracker", "issue_goal_run_close_tracker")
OBSERVATION = _load_local("issue_tracker_observation", "issue_goal_run_close_observation")
CLOSE = _load_local("issue_close", "issue_goal_run_close_backend")
GUARD = _load_local("issue_goal_run_guard")
TERMINAL = _load_local("issue_goal_run_terminal", "issue_goal_run_close_terminal")
RECOVERY = _load_local("issue_goal_run_close_recovery", "issue_goal_run_close_recovery_plan")
CLOSE_MUTATION_ERROR = CLOSE.CloseMutationError


def _refusal(code: str, message: str, *, repo: str, parent: int) -> dict[str, Any]:
    return {
        "ok": False,
        "kind": "charness.goal-run-close/v1",
        "status": code,
        "outcome": "refused",
        "mutation_invoked": False,
        "repo": repo,
        "parent_number": parent,
        "error_code": code,
        "error": message,
        "next_action": "repair-close-proof-or-return-to-goal-lifecycle-owner",
    }


def _evidence_is_live(issue: dict[str, Any], evidence: dict[str, Any]) -> bool:
    comments = issue.get("comments")
    if not isinstance(comments, list):
        return False
    identity = evidence["identity"]
    return any(isinstance(comment, dict) and comment.get("url") == identity for comment in comments)


def _verify_children(
    repo: str,
    proof: dict[str, Any],
    expected_children: list[dict[str, Any]],
    live_children: list[dict[str, Any]],
    backend: dict[str, Any],
) -> None:
    live_numbers = {child["number"] for child in live_children}
    proof_numbers = {child["number"] for child in proof["children"]}
    expected_numbers = {child["number"] for child in expected_children}
    if proof_numbers != expected_numbers:
        raise RuntimeError(
            "close proof child identities differ from the separately bound final proof index"
        )
    if live_numbers != proof_numbers:
        raise RuntimeError(
            f"close proof child identities differ from live graph: "
            f"missing={sorted(live_numbers - proof_numbers)!r} "
            f"unexpected={sorted(proof_numbers - live_numbers)!r}"
        )
    for entry in proof["children"]:
        live = next(child for child in live_children if child["number"] == entry["number"])
        if live.get("state") != "CLOSED":
            raise RuntimeError(f"linked child {repo}#{entry['number']} is not CLOSED")
        issue = READ.read_issue_with_comments(repo, entry["number"], backend=backend)["issue"]
        if issue.get("state") != "CLOSED":
            raise RuntimeError(f"child {repo}#{entry['number']} state readback is not CLOSED")
        if not _evidence_is_live(issue, entry["evidence"]):
            raise RuntimeError(
                f"child {repo}#{entry['number']} evidence identity is not present in issue-owned comments"
            )


def _prepare_close(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    proof: dict[str, Any],
    backend: dict[str, Any],
) -> dict[str, Any]:
    """Read the live parent/graph and create the pre-mutation observation."""
    parent = READ.read_issue_with_comments(repo, parent_number, backend=backend)["issue"]
    metadata = GUARD.parse_goal_run_metadata(parent.get("body"), context="Goal Run parent body")
    if metadata is None:
        raise RuntimeError("target parent does not carry Goal Run metadata")
    if metadata.get("binding_sha256") != proof["binding_sha256"]:
        raise RuntimeError("close proof binding hash does not match parent metadata")
    if metadata.get("draft_sha256") != proof["draft_sha256"]:
        raise RuntimeError("close proof draft hash does not match parent metadata")
    parent_identity = metadata.get("parent_identity")
    if parent_identity is not None:
        if not isinstance(parent_identity, dict) or not isinstance(parent_identity.get("repo"), str):
            raise RuntimeError("Goal Run parent metadata identity is malformed")
        if (
            parent_identity["repo"].lower() != repo.lower()
            or parent_identity.get("number") != parent_number
        ):
            raise RuntimeError("Goal Run parent metadata identity does not match the requested parent")
    graph = TRACKER.list_sub_issues(repo, parent_number, backend=backend)
    _verify_children(
        repo,
        proof,
        proof["final_proof_index"]["expected_children"],
        graph["children"],
        backend,
    )
    return RECOVERY.plan(
        repo_root=repo_root,
        repo=repo,
        parent_number=parent_number,
        parent=parent,
        metadata=metadata,
        proof=proof,
        backend=backend,
        observation=OBSERVATION,
        terminal_contract=TERMINAL,
    )


def _mutation_result(
    carrier: dict[str, Any], *, operation: str, backend: dict[str, Any]
) -> dict[str, Any]:
    return {
        **carrier,
        "ok": True,
        "status": "verified-write",
        "outcome": "verified-write",
        "mutation_invoked": True,
        "comment_succeeded": True,
        "close_succeeded": True,
        "operation": operation,
        "selected_backend": backend,
    }


def _metadata_failure(result: dict[str, Any], exc: RuntimeError) -> dict[str, Any]:
    return {
        **result,
        "ok": False,
        "status": "metadata-unverified",
        "outcome": "unverified-write",
        "mutation_invoked": True,
        "error": (
            "Goal Run close is verified and its terminal observation exists, "
            f"but terminal metadata was not verified: {exc}"
        ),
        "terminal_metadata": {
            "ok": False,
            "update": exc.update if isinstance(exc, TERMINAL.TerminalMetadataError) else None,
            "error": str(exc),
        },
        "next_action": "retry-goal-run-close-to-repair-terminal-metadata",
    }


def command_close(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        repo_root = args.repo_root.resolve()
        proof_path = CONTRACT.repo_file(repo_root, str(args.proof_file), context="proof_file")
        proof = CONTRACT.load_close_proof(
            proof_path, repo=args.repo, parent_number=args.number, repo_root=repo_root
        )
    except CONTRACT.GoalRunInputErrors as exc:
        emit(_refusal(exc.code, str(exc), repo=args.repo, parent=args.number))
        return 2
    try:
        resolved = resolve_backend(args.repo_root.resolve(), target_repo=args.repo)
    except RuntimeError as exc:
        emit(_refusal("provider-selection-invalid", str(exc), repo=args.repo, parent=args.number))
        return 2
    if not resolved.get("adapter_ok"):
        emit(_refusal("adapter-invalid", "issue adapter is invalid", repo=args.repo, parent=args.number))
        return 2
    capability = CONTRACT.capability_report(
        resolved["backend"], ["close-goal-run"], repo=args.repo
    )
    if not capability["ok"]:
        result = _refusal(
            "capability-missing",
            "Goal Run close backend capability closure is incomplete",
            repo=args.repo,
            parent=args.number,
        )
        result["capability"] = capability
        emit(result)
        return 2
    try:
        prepared = _prepare_close(
            repo_root=repo_root,
            repo=args.repo,
            parent_number=args.number,
            proof=proof,
            backend=resolved["backend"],
        )
    except RuntimeError as exc:
        emit(_refusal("close-refused", str(exc), repo=args.repo, parent=args.number))
        return 2
    if "already_closed" in prepared:
        emit(prepared["already_closed"])
        return 0
    parent = prepared["parent"]
    comment_file = Path(proof["comment_path"])
    if prepared.get("recovery"):
        result = prepared["result"]
        terminal = prepared["terminal"]
    else:
        started = prepared["started"]
        operation = "resume-goal-run-close" if prepared["mode"] == "resume" else "close-goal-run"
        try:
            close_fn = (
                CLOSE.close_after_verified_comment
                if prepared["mode"] == "resume"
                else CLOSE.close_with_comment
            )
            carrier = close_fn(
                args.repo,
                args.number,
                comment_file,
                repo_root=repo_root,
                classification=proof.get("classification", "feature"),
                backend=resolved["backend"],
                reason=proof.get("reason", "completed"),
                manual_target_declaration=proof.get("manual_target_declaration"),
                **({} if prepared["mode"] == "resume" else {"goal_run_authorized": True}),
                preflight_state=parent,
            )
            result = _mutation_result(carrier, operation=operation, backend=resolved["backend"])
        except CLOSE_MUTATION_ERROR as exc:
            result = {
                **_refusal("close-unverified", str(exc), repo=args.repo, parent=args.number),
                "outcome": "unverified-write",
                "mutation_invoked": True,
                "operation": operation,
                "stage": exc.stage,
                "comment_succeeded": exc.comment_succeeded,
                "close_succeeded": exc.close_succeeded,
            }
        except RuntimeError as exc:
            result = {
                **_refusal("close-refused", str(exc), repo=args.repo, parent=args.number),
                "operation": operation,
            }
        try:
            terminal = OBSERVATION.finish(
                repo_root=repo_root,
                observation_dir=Path(proof["observation_dir"]),
                attempt_id=proof["attempt_id"],
                started=started,
                result=result,
            )
        except RuntimeError as exc:
            invoked = bool(result.get("mutation_invoked"))
            result = {
                **_refusal("observation-unverified", str(exc), repo=args.repo, parent=args.number),
                "outcome": "unverified-write" if invoked else "refused",
                "mutation_invoked": invoked,
                "started_observation": started,
            }
            terminal = None
    if terminal is not None:
        result["observation"] = {
            "started_path": terminal["payload"]["started_path"],
            "started_sha256": terminal["payload"]["started_sha256"],
            "terminal_path": terminal["path"],
            "terminal_sha256": terminal["payload"]["receipt_sha256"],
        }
    if result.get("ok") and terminal is not None:
        try:
            terminal_metadata = TERMINAL.update_metadata(
                repo_root=repo_root,
                repo=args.repo,
                parent_number=args.number,
                parent_body=parent.get("body"),
                terminal=terminal,
                backend=resolved["backend"],
                tracker=TRACKER,
                read=READ,
                guard=GUARD,
            )
            result["terminal_metadata"] = terminal_metadata
            if prepared.get("recovery"):
                update = terminal_metadata["update"]
                result.update(
                    status="recovered-terminal-metadata",
                    outcome=update["outcome"],
                    mutation_invoked=bool(update.get("mutation_invoked")),
                )
        except RuntimeError as exc:
            result = _metadata_failure(result, exc)
    result.update(kind="charness.goal-run-close/v1", attempt_id=proof["attempt_id"])
    emit(result)
    return 0 if result["ok"] else 2
