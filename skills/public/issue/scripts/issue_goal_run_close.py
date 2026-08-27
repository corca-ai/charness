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
    repo: str, proof: dict[str, Any], live_children: list[dict[str, Any]], backend: dict[str, Any]
) -> None:
    live_numbers = {child["number"] for child in live_children}
    proof_numbers = {child["number"] for child in proof["children"]}
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


def command_close(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        proof = CONTRACT.load_close_proof(
            args.proof_file.resolve(), repo=args.repo, parent_number=args.number
        )
    except CONTRACT.GoalRunInputError as exc:
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
    try:
        # Close is the one place that intentionally reads the full graph. Reuse
        # this exact parent read for metadata validation and for the carrier's
        # pre-mutation identity check; a readiness probe plus a second parent read
        # added latency without adding a distinct observation.
        parent = READ.read_issue_with_comments(
            args.repo, args.number, backend=resolved["backend"]
        )["issue"]
        metadata = GUARD.parse_goal_run_metadata(parent.get("body"), context="Goal Run parent body")
        if metadata is None:
            raise RuntimeError("target parent does not carry Goal Run metadata")
        if metadata.get("binding_sha256") != proof["binding_sha256"]:
            raise RuntimeError("close proof binding hash does not match parent metadata")
        if metadata.get("draft_sha256") != proof["draft_sha256"]:
            raise RuntimeError("close proof draft hash does not match parent metadata")
        graph = TRACKER.list_sub_issues(args.repo, args.number, backend=resolved["backend"])
        _verify_children(args.repo, proof, graph["children"], resolved["backend"])
        if parent.get("state") == "CLOSED":
            result = {
                "ok": True,
                "kind": "charness.goal-run-close/v1",
                "status": "already-closed",
                "outcome": "verified-read",
                "mutation_invoked": False,
                "repo": args.repo,
                "parent_number": args.number,
                "next_action": "retain-closed-parent-no-reclose",
            }
            emit(result)
            return 0
        comment_file = CONTRACT.repo_file(
            args.repo_root.resolve(), proof["comment_file"], context="close proof comment_file"
        )
        started = OBSERVATION.begin(
            repo_root=args.repo_root.resolve(),
            observation_dir=Path(proof["observation_dir"]),
            attempt_id=proof["attempt_id"],
            draft_sha256=proof["draft_sha256"],
            binding_sha256=proof["binding_sha256"],
            repo=args.repo,
            parent_number=args.number,
            operation="close-goal-run",
            target={"repo": args.repo, "number": args.number},
            submitted_body_sha256=None,
            backend=resolved["backend"],
        )
    except RuntimeError as exc:
        emit(_refusal("close-refused", str(exc), repo=args.repo, parent=args.number))
        return 2
    try:
        result = CLOSE.close_with_comment(
            args.repo,
            args.number,
            comment_file,
            repo_root=args.repo_root.resolve(),
            classification=proof.get("classification", "feature"),
            backend=resolved["backend"],
            reason=proof.get("reason", "completed"),
            manual_target_declaration=proof.get("manual_target_declaration"),
            goal_run_authorized=True,
            preflight_state=parent,
        )
        result = {
            **result,
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "operation": "close-goal-run",
        }
    except RuntimeError as exc:
        text = str(exc)
        invoked = "after comment landed" in text or "after close command succeeded" in text
        result = {
            **_refusal("close-unverified" if invoked else "close-refused", text, repo=args.repo, parent=args.number),
            "mutation_invoked": invoked,
            "operation": "close-goal-run",
        }
    try:
        terminal = OBSERVATION.finish(
            repo_root=args.repo_root.resolve(),
            observation_dir=Path(proof["observation_dir"]),
            attempt_id=proof["attempt_id"],
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
            **_refusal("observation-unverified", str(exc), repo=args.repo, parent=args.number),
            "mutation_invoked": bool(result.get("mutation_invoked")),
            "started_observation": started,
        }
    result.update(kind="charness.goal-run-close/v1", attempt_id=proof["attempt_id"])
    emit(result)
    return 0 if result["ok"] else 2
