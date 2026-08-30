"""Idempotent close/recovery selection from immutable provider attempts."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plan(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    parent: dict[str, Any],
    metadata: dict[str, Any],
    proof: dict[str, Any],
    backend: dict[str, Any],
    observation: Any,
    terminal_contract: Any,
) -> dict[str, Any]:
    observation_dir = Path(proof["observation_dir"])
    prior = observation.find_close_attempts(
        repo_root=repo_root,
        observation_dir=observation_dir,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=proof["draft_sha256"],
        binding_sha256=proof["binding_sha256"],
        exclude_attempt_id=proof["attempt_id"],
    )
    if parent.get("state") == "CLOSED" and metadata.get("terminal_observation_path"):
        receipt = terminal_contract.validate_metadata_receipt(
            repo_root=repo_root,
            observation_dir=observation_dir,
            metadata=metadata,
            repo=repo,
            parent_number=parent_number,
            draft_sha256=proof["draft_sha256"],
            binding_sha256=proof["binding_sha256"],
            comment_sha256=proof["comment_sha256"],
            observation=observation,
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
                    "receipt": receipt["terminal"],
                },
                "next_action": "retain-closed-parent-no-reclose",
            }
        }
    if parent.get("state") == "CLOSED":
        return _closed_recovery(
            repo_root=repo_root,
            repo=repo,
            parent_number=parent_number,
            parent=parent,
            proof=proof,
            backend=backend,
            observation=observation,
            terminal_contract=terminal_contract,
            observation_dir=observation_dir,
            prior=prior,
        )
    return _open_plan(
        repo_root=repo_root,
        repo=repo,
        parent_number=parent_number,
        parent=parent,
        proof=proof,
        backend=backend,
        observation=observation,
        observation_dir=observation_dir,
        prior=prior,
    )


def _closed_recovery(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    parent: dict[str, Any],
    proof: dict[str, Any],
    backend: dict[str, Any],
    observation: Any,
    terminal_contract: Any,
    observation_dir: Path,
    prior: list[dict[str, Any]],
) -> dict[str, Any]:
    mutations = _mutation_lineage(prior, comment_sha256=proof["comment_sha256"])
    recoverable: list[dict[str, Any]] = []
    for attempt in mutations:
        try:
            terminal_contract.validate_recoverable_close_attempt(
                attempt,
                repo=repo,
                parent_number=parent_number,
                draft_sha256=proof["draft_sha256"],
                binding_sha256=proof["binding_sha256"],
            )
        except RuntimeError:
            continue
        recoverable.append(attempt)
    if len(recoverable) != 1:
        raise RuntimeError(
            "parent is CLOSED without verified terminal metadata and does not have "
            "exactly one recoverable bound close receipt"
        )
    started = _begin(
        repo_root=repo_root,
        repo=repo,
        parent_number=parent_number,
        proof=proof,
        backend=backend,
        observation=observation,
        observation_dir=observation_dir,
        operation="recover-goal-run-close",
    )
    result = {
        "ok": True,
        "status": "closed-parent-recovered",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "operation": "recover-goal-run-close",
        "repo": repo,
        "parent_number": parent_number,
        "prior_terminal": recoverable[0]["terminal"],
    }
    terminal = observation.finish(
        repo_root=repo_root,
        observation_dir=observation_dir,
        attempt_id=proof["attempt_id"],
        started=started,
        result=result,
    )
    return {"parent": parent, "result": result, "terminal": terminal, "recovery": True}


def _open_plan(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    parent: dict[str, Any],
    proof: dict[str, Any],
    backend: dict[str, Any],
    observation: Any,
    observation_dir: Path,
    prior: list[dict[str, Any]],
) -> dict[str, Any]:
    mutations = _mutation_lineage(prior, comment_sha256=proof["comment_sha256"])
    if any(
        attempt["terminal"]["payload"]["result"].get("close_succeeded") is not False
        for attempt in mutations
    ):
        raise RuntimeError(
            "a prior bound close mutation remains unresolved and cannot be retried without disposition"
        )
    operation = "resume-goal-run-close" if mutations else "close-goal-run"
    return {
        "parent": parent,
        "mode": "resume" if mutations else "close",
        "prior_terminal": mutations[-1]["terminal"] if mutations else None,
        "started": _begin(
            repo_root=repo_root,
            repo=repo,
            parent_number=parent_number,
            proof=proof,
            backend=backend,
            observation=observation,
            observation_dir=observation_dir,
            operation=operation,
        ),
    }


def _mutation_lineage(
    prior: list[dict[str, Any]], *, comment_sha256: str
) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []
    for attempt in prior:
        terminal_ref = attempt.get("terminal")
        if not isinstance(terminal_ref, dict):
            raise RuntimeError(
                "a prior Goal Run close started without a valid terminal observation; "
                "explicit disposition is required before retry"
            )
        started = attempt["started"]["payload"]
        terminal = terminal_ref["payload"]
        result = terminal.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("a prior Goal Run close terminal result is malformed")
        if terminal.get("mutation_invoked") is not True:
            continue
        if started.get("submitted_body_sha256") != comment_sha256:
            raise RuntimeError(
                "a prior Goal Run close mutation used different comment bytes; "
                "explicit changed-input disposition is required"
            )
        if (
            result.get("operation") != started.get("operation")
            or result.get("comment_succeeded") is not True
            or type(result.get("close_succeeded")) is not bool
        ):
            raise RuntimeError(
                "a prior bound close mutation remains unresolved and cannot be retried without disposition"
            )
        mutations.append(attempt)
    anchors = [
        attempt
        for attempt in mutations
        if attempt["started"]["payload"].get("operation") == "close-goal-run"
    ]
    if mutations and len(anchors) != 1:
        raise RuntimeError(
            "prior Goal Run close mutations do not form one verified comment lineage"
        )
    return mutations


def _begin(
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    proof: dict[str, Any],
    backend: dict[str, Any],
    observation: Any,
    observation_dir: Path,
    operation: str,
) -> dict[str, Any]:
    return observation.begin(
        repo_root=repo_root,
        observation_dir=observation_dir,
        attempt_id=proof["attempt_id"],
        draft_sha256=proof["draft_sha256"],
        binding_sha256=proof["binding_sha256"],
        repo=repo,
        parent_number=parent_number,
        operation=operation,
        target={"repo": repo, "number": parent_number},
        submitted_body_sha256=proof["comment_sha256"],
        backend=backend,
    )
