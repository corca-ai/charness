"""Read closeout carrier bodies and check manual-fallback comments.

This module owns the carrier-input seam: obtaining the body from a commit or
file, and checking whether a manual fallback posted that exact body as a
comment. Keeping those channel mechanics together leaves
``issue_verify_closeout.py`` focused on combining verifier floors into a
closeout verdict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_carrier_body(
    repo_root: Path,
    *,
    carrier: str,
    commit_ref: str | None,
    body_file: Path | None,
    run_process,
    timeout_seconds: int,
) -> str:
    """Read the body carried by a commit or an explicit body file."""
    if carrier == "direct-commit":
        if not commit_ref:
            raise RuntimeError("direct-commit carrier requires --commit-ref")
        result = run_process(
            ["git", "show", "-s", "--format=%B", commit_ref],
            cwd=repo_root,
            timeout_seconds=timeout_seconds,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"unable to read commit body for {commit_ref!r}: {result.stderr.strip()!r}"
            )
        return result.stdout
    if body_file is None:
        raise RuntimeError(f"{carrier} carrier requires --body-file")
    if not body_file.is_file():
        raise RuntimeError(f"carrier body file not found: {body_file}")
    return body_file.read_text(encoding="utf-8")


def manual_comment_found(body: str, state_payload: dict[str, Any]) -> bool:
    """Return whether backend state contains the exact manual fallback body."""
    expected = body.strip()
    comments = state_payload.get("comments")
    if not isinstance(comments, list):
        return False
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        comment_body = str(comment.get("body", "")).strip()
        if comment_body == expected:
            return True
    return False
