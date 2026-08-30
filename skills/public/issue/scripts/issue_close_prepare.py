"""Pre-mutation preparation shared by first close and close-only retry."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def prepare(
    repo: str,
    number: int,
    body_file: Path,
    *,
    repo_root: Path,
    classification: str,
    backend: dict[str, Any],
    reason: str,
    manual_target_declaration: str | None,
    goal_run_authorized: bool,
    preflight_state: dict[str, Any] | None,
    evaluate: Any,
    resolve_commands: Any,
    read_preflight: Any,
    check_target: Any,
    format_failure: Any,
    guard_body: Any,
    refuse_reason: Any,
) -> dict[str, Any]:
    refuse_reason(classification, reason)
    if not body_file.is_file():
        raise RuntimeError(f"close-comment body file not found: {body_file}")
    body = body_file.read_text(encoding="utf-8")
    if not goal_run_authorized:
        guard_body(body, context="close carrier")
    floor_report = evaluate(
        repo,
        number,
        body,
        repo_root=repo_root,
        classification=classification,
        backend=backend,
        reason=reason,
        manual_target_declaration=manual_target_declaration,
    )
    if not floor_report["ok"]:
        raise RuntimeError(format_failure(floor_report))
    comment_argv, close_argv, view_argv = resolve_commands(
        backend, repo=repo, number=number, body_file=body_file, reason=reason
    )
    if view_argv is not None:
        preflight_state = read_preflight(
            view_argv, repo=repo, number=number, existing=preflight_state
        )
    check_target(
        repo=repo,
        number=number,
        backend=backend,
        authorized=goal_run_authorized,
    )
    return {
        "floor_report": floor_report,
        "authorization": floor_report["closeout_authorization"],
        "comment_argv": comment_argv,
        "close_argv": close_argv,
        "view_argv": view_argv,
        "preflight_state": preflight_state,
    }
