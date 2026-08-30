"""Close-only retry after an earlier bound issue comment succeeded."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def close_after_verified_comment(
    repo: str,
    number: int,
    body_file: Path,
    *,
    repo_root: Path,
    classification: str,
    backend: dict[str, Any],
    prepare: Any,
    mutation: Any,
    run_backend: Any,
    require_identity: Any,
    reason: str = "completed",
    manual_target_declaration: str | None = None,
    preflight_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prepared = prepare(
        repo,
        number,
        body_file,
        repo_root=repo_root,
        classification=classification,
        backend=backend,
        reason=reason,
        manual_target_declaration=manual_target_declaration,
        goal_run_authorized=True,
        preflight_state=preflight_state,
    )
    verified_state = mutation.close_after_comment(
        prepared["close_argv"],
        prepared["view_argv"],
        repo=repo,
        number=number,
        run_backend=run_backend,
        require_identity=require_identity,
    )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": None,
        "close_argv": prepared["close_argv"],
        "view_argv": prepared["view_argv"],
        "preflight_state": prepared["preflight_state"],
        "verified_state": verified_state,
        "reason": reason,
        "closeout_authorization": prepared["authorization"],
        "comment_reused": True,
    }
