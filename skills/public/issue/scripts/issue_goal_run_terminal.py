"""Terminal receipt validation and parent metadata convergence."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any


class TerminalMetadataError(RuntimeError):
    """A typed boundary failure after an immutable close receipt exists."""

    def __init__(self, message: str, *, update: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.update = update


def _same_parent(value: Any, *, repo: str, number: int) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("repo"), str)
        and value["repo"].casefold() == repo.casefold()
        and value.get("number") == number
    )


def _close_attempt_result(
    attempt: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not isinstance(attempt.get("terminal"), dict):
        raise RuntimeError("Goal Run close attempt has no valid terminal observation")
    started = attempt["started"]["payload"]
    terminal = attempt["terminal"]["payload"]
    result = terminal.get("result")
    operation = started.get("operation")
    if (
        operation not in {"close-goal-run", "resume-goal-run-close"}
        or not _same_parent(started.get("parent"), repo=repo, number=parent_number)
        or started.get("draft_sha256") != draft_sha256
        or started.get("binding_sha256") != binding_sha256
        or not isinstance(result, dict)
        or result.get("operation") != operation
        or result.get("comment_succeeded") is not True
        or result.get("close_succeeded") is not True
        or terminal.get("mutation_invoked") is not True
        or terminal.get("outcome") != result.get("outcome")
    ):
        raise RuntimeError("terminal observation does not bind a completed Goal Run close command")
    return started, terminal, result


def validate_verified_close_attempt(
    attempt: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
) -> None:
    _, terminal, result = _close_attempt_result(
        attempt,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=draft_sha256,
        binding_sha256=binding_sha256,
    )
    if result.get("ok") is not True or terminal.get("outcome") != "verified-write":
        raise RuntimeError("terminal observation does not bind a verified Goal Run close")


def validate_recoverable_close_attempt(
    attempt: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
) -> None:
    _, terminal, result = _close_attempt_result(
        attempt,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=draft_sha256,
        binding_sha256=binding_sha256,
    )
    verified = result.get("ok") is True and terminal.get("outcome") == "verified-write"
    recovered_readback = (
        result.get("ok") is False
        and result.get("stage") == "post-close-readback"
        and terminal.get("outcome") == "unverified-write"
    )
    if not (verified or recovered_readback):
        raise RuntimeError("terminal observation is not recoverable as a completed close command")


def _metadata_body(
    body: str,
    terminal: dict[str, Any],
    *,
    guard: Any,
) -> tuple[str, dict[str, Any]]:
    metadata = guard.parse_goal_run_metadata(body, context="Goal Run parent body")
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
    matches = list(guard.BLOCK_RE.finditer(body))
    if len(matches) != 1:
        raise RuntimeError("Goal Run parent body has no uniquely replaceable metadata block")
    rendered = (
        "<!-- charness-goal-run:v1\n"
        + json.dumps(updated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n-->"
    )
    match = matches[0]
    return body[: match.start()] + rendered + body[match.end() :], updated


def update_metadata(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    parent_body: str,
    terminal: dict[str, Any],
    backend: dict[str, Any],
    tracker: Any,
    read: Any,
    guard: Any,
) -> dict[str, Any]:
    desired_body, desired_metadata = _metadata_body(parent_body, terminal, guard=guard)
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
            update = tracker.update_issue_body(
                repo,
                parent_number,
                body_file,
                backend=backend,
                terminal_metadata_update=True,
            )
        finally:
            body_file.unlink(missing_ok=True)
    if update.get("ok") is not True or update.get("outcome") not in {
        "verified-read",
        "verified-write",
    }:
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
    readback = read.read_issue_with_comments(repo, parent_number, backend=backend)["issue"]
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
        raise TerminalMetadataError(
            "parent metadata readback did not return a string body", update=update
        )
    readback_metadata = guard.parse_goal_run_metadata(
        readback_body, context="post-metadata Goal Run parent body"
    )
    if (
        readback_metadata is None
        or readback_metadata.get("terminal_observation_path") != terminal["path"]
        or readback_metadata.get("terminal_observation_sha256")
        != terminal["payload"]["receipt_sha256"]
    ):
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


def validate_metadata_receipt(
    *,
    repo_root: Path,
    observation_dir: Path,
    metadata: dict[str, Any],
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
    comment_sha256: str,
    observation: Any,
) -> dict[str, Any]:
    path = metadata.get("terminal_observation_path")
    digest = metadata.get("terminal_observation_sha256")
    if not isinstance(path, str) or not isinstance(digest, str):
        raise RuntimeError("Goal Run terminal observation metadata is incomplete")
    expected_dir = (repo_root / observation_dir).resolve()
    terminal_path = (repo_root / path).resolve()
    try:
        terminal_path.relative_to(expected_dir)
    except ValueError as exc:
        raise RuntimeError("terminal observation metadata escapes the bound observation directory") from exc
    suffix = ".terminal.json"
    if not terminal_path.name.endswith(suffix):
        raise RuntimeError("terminal observation metadata does not name a terminal receipt")
    attempt_id = terminal_path.name.removesuffix(suffix)
    attempt = observation.read_attempt(
        repo_root=repo_root,
        observation_dir=observation_dir,
        attempt_id=attempt_id,
    )
    if attempt is None or attempt["terminal"]["path"] != path:
        raise RuntimeError("terminal observation metadata does not resolve to a valid receipt pair")
    started = attempt["started"]["payload"]
    terminal = attempt["terminal"]["payload"]
    result = terminal.get("result")
    operation = started.get("operation")
    if (
        terminal.get("receipt_sha256") != digest
        or not isinstance(result, dict)
        or started.get("submitted_body_sha256") != comment_sha256
    ):
        raise RuntimeError("terminal observation receipt does not bind a verified Goal Run close")
    if operation in {"close-goal-run", "resume-goal-run-close"}:
        validate_verified_close_attempt(
            attempt,
            repo=repo,
            parent_number=parent_number,
            draft_sha256=draft_sha256,
            binding_sha256=binding_sha256,
        )
        return attempt
    if (
        operation != "recover-goal-run-close"
        or not _same_parent(started.get("parent"), repo=repo, number=parent_number)
        or started.get("draft_sha256") != draft_sha256
        or started.get("binding_sha256") != binding_sha256
        or result.get("operation") != operation
        or result.get("ok") is not True
        or terminal.get("outcome") != "verified-read"
        or terminal.get("mutation_invoked") is not False
    ):
        raise RuntimeError("terminal observation receipt does not bind a verified close recovery")
    prior = result.get("prior_terminal")
    if not isinstance(prior, dict) or not isinstance(prior.get("path"), str):
        raise RuntimeError("close recovery does not bind its prior verified close receipt")
    prior_name = Path(prior["path"]).name
    if not prior_name.endswith(".terminal.json"):
        raise RuntimeError("close recovery prior receipt path is invalid")
    prior_attempt = observation.read_attempt(
        repo_root=repo_root,
        observation_dir=observation_dir,
        attempt_id=prior_name.removesuffix(".terminal.json"),
    )
    if (
        prior_attempt is None
        or prior_attempt["terminal"]["path"] != prior["path"]
        or prior_attempt["terminal"]["payload"].get("receipt_sha256")
        != prior.get("payload", {}).get("receipt_sha256")
        or prior_attempt["started"]["payload"].get("submitted_body_sha256")
        != started.get("submitted_body_sha256")
    ):
        raise RuntimeError("close recovery prior receipt does not match immutable observations")
    validate_recoverable_close_attempt(
        prior_attempt,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=draft_sha256,
        binding_sha256=binding_sha256,
    )
    return attempt
