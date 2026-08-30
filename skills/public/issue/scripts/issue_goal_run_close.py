"""Dedicated, guarded Goal Run parent close ingress."""

from __future__ import annotations

import json
import runpy
import tempfile
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


class TerminalMetadataError(RuntimeError):
    """A typed boundary failure after the immutable close receipt exists."""

    def __init__(self, message: str, *, update: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.update = update


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


def _terminal_metadata_body(body: str, terminal: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    metadata = GUARD.parse_goal_run_metadata(body, context="Goal Run parent body")
    if metadata is None:
        raise RuntimeError("target parent does not carry Goal Run metadata")
    terminal_path = terminal["path"]
    terminal_sha256 = terminal["payload"]["receipt_sha256"]
    existing_path = metadata.get("terminal_observation_path")
    existing_sha256 = metadata.get("terminal_observation_sha256")
    if (existing_path is None) != (existing_sha256 is None):
        raise RuntimeError("Goal Run terminal observation metadata is incomplete")
    if existing_path is not None and (
        existing_path != terminal_path or existing_sha256 != terminal_sha256
    ):
        raise RuntimeError("Goal Run terminal observation metadata already binds another receipt")
    if existing_path == terminal_path and existing_sha256 == terminal_sha256:
        return body, metadata
    updated = dict(metadata)
    updated["terminal_observation_path"] = terminal_path
    updated["terminal_observation_sha256"] = terminal_sha256
    matches = list(GUARD.BLOCK_RE.finditer(body))
    if len(matches) != 1:
        raise RuntimeError("Goal Run parent body has no uniquely replaceable metadata block")
    rendered = (
        "<!-- charness-goal-run:v1\n"
        + json.dumps(updated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n-->"
    )
    match = matches[0]
    return body[: match.start()] + rendered + body[match.end() :], updated


def _update_terminal_metadata(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    parent_body: str,
    terminal: dict[str, Any],
    backend: dict[str, Any],
) -> dict[str, Any]:
    desired_body, desired_metadata = _terminal_metadata_body(parent_body, terminal)
    if desired_body == parent_body:
        update = {
            "ok": True,
            "status": "already-current",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "operation": "update-body",
            "action": "already-current",
            "repo": repo,
            "number": parent_number,
        }
    else:
        observation_dir = repo_root / Path(terminal["path"]).parent
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=observation_dir,
            prefix=".terminal-metadata-",
            suffix=".md",
            delete=False,
        ) as handle:
            body_file = Path(handle.name)
            handle.write(desired_body)
        try:
            update = TRACKER.update_issue_body(repo, parent_number, body_file, backend=backend)
        finally:
            body_file.unlink(missing_ok=True)
    if update.get("ok") is not True or update.get("outcome") not in {"verified-read", "verified-write"}:
        raise TerminalMetadataError(
            "terminal observation exists but parent terminal metadata update was not verified: "
            f"{update.get('error') or update.get('outcome') or update.get('status')}",
            update=update,
        )
    if update.get("outcome") == "verified-write" and update.get("body_verified") is not True:
        raise TerminalMetadataError(
            "terminal observation exists but parent terminal metadata body readback was not verified",
            update=update,
        )
    readback = READ.read_issue_with_comments(repo, parent_number, backend=backend)["issue"]
    if readback.get("number") != parent_number:
        raise TerminalMetadataError(
            "parent metadata readback did not identify the requested parent", update=update
        )
    if readback.get("state") != "CLOSED":
        raise TerminalMetadataError(
            f"parent metadata readback changed the Goal Run state to {readback.get('state')!r}",
            update=update,
        )
    readback_body = readback.get("body")
    if not isinstance(readback_body, str):
        raise TerminalMetadataError("parent metadata readback did not return a string body", update=update)
    readback_metadata = GUARD.parse_goal_run_metadata(
        readback_body, context="post-metadata Goal Run parent body"
    )
    if readback_metadata is None or readback_metadata.get("terminal_observation_path") != terminal["path"] or readback_metadata.get("terminal_observation_sha256") != terminal["payload"]["receipt_sha256"]:
        raise TerminalMetadataError(
            "parent metadata readback did not bind the terminal observation receipt",
            update=update,
        )
    return {
        "update": update,
        "readback": {
            "repo": repo,
            "number": parent_number,
            "state": readback.get("state"),
            "body": readback_body,
            "terminal_observation_path": readback_metadata["terminal_observation_path"],
            "terminal_observation_sha256": readback_metadata["terminal_observation_sha256"],
        },
        "metadata": desired_metadata,
    }


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
    if parent.get("state") == "CLOSED":
        if not metadata.get("terminal_observation_path") or not metadata.get("terminal_observation_sha256"):
            raise RuntimeError(
                "parent is already CLOSED without terminal observation metadata; "
                "no re-close is permitted"
            )
        return {
            "already_closed": {
                "ok": True,
                "kind": "charness.goal-run-close/v1",
                "status": "already-closed",
                "outcome": "verified-read",
                "mutation_invoked": False,
                "repo": repo,
                "parent_number": parent_number,
                "selected_backend": backend,
                "terminal_metadata": {
                    "terminal_observation_path": metadata["terminal_observation_path"],
                    "terminal_observation_sha256": metadata["terminal_observation_sha256"],
                },
                "next_action": "retain-closed-parent-no-reclose",
            }
        }
    return {
        "parent": parent,
        "started": OBSERVATION.begin(
            repo_root=repo_root,
            observation_dir=Path(proof["observation_dir"]),
            attempt_id=proof["attempt_id"],
            draft_sha256=proof["draft_sha256"],
            binding_sha256=proof["binding_sha256"],
            repo=repo,
            parent_number=parent_number,
            operation="close-goal-run",
            target={"repo": repo, "number": parent_number},
            submitted_body_sha256=None,
            backend=backend,
        ),
    }


def command_close(args: Any, *, resolve_backend: Any, emit: Any) -> int:
    try:
        repo_root = args.repo_root.resolve()
        proof_path = CONTRACT.repo_file(repo_root, str(args.proof_file), context="proof_file")
        proof = CONTRACT.load_close_proof(
            proof_path, repo=args.repo, parent_number=args.number, repo_root=repo_root
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
    started = prepared["started"]
    comment_file = Path(proof["comment_path"])
    try:
        result = CLOSE.close_with_comment(
            args.repo,
            args.number,
            comment_file,
            repo_root=repo_root,
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
            "selected_backend": resolved["backend"],
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
            repo_root=repo_root,
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
    if result.get("ok") and result.get("outcome") == "verified-write":
        try:
            result["terminal_metadata"] = _update_terminal_metadata(
                repo_root=repo_root,
                repo=args.repo,
                parent_number=args.number,
                parent_body=parent.get("body"),
                terminal=terminal,
                backend=resolved["backend"],
            )
        except RuntimeError as exc:
            result = {
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
                    "update": exc.update if isinstance(exc, TerminalMetadataError) else None,
                    "error": str(exc),
                },
                "next_action": "repair-terminal-metadata-and-reread-closed-parent",
            }
    result.update(kind="charness.goal-run-close/v1", attempt_id=proof["attempt_id"])
    emit(result)
    return 0 if result["ok"] else 2
