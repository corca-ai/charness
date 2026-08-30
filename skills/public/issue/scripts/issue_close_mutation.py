"""Typed provider mutation and readback stages for issue close carriers."""

from __future__ import annotations

import json
from typing import Any


class CloseMutationError(RuntimeError):
    """A typed failure after the close carrier invoked a provider mutation."""

    def __init__(
        self,
        message: str,
        *,
        stage: str,
        comment_succeeded: bool,
        close_succeeded: bool,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.mutation_invoked = True
        self.comment_succeeded = comment_succeeded
        self.close_succeeded = close_succeeded


def _closed_readback(
    view_argv: list[str] | None,
    *,
    repo: str,
    number: int,
    run_backend: Any,
    require_identity: Any,
) -> dict[str, Any] | None:
    if view_argv is None:
        return None
    view_result = run_backend(view_argv)
    if view_result.returncode != 0:
        raise CloseMutationError(
            "close state verification failed after close command succeeded; "
            f"view_exit={view_result.returncode} view_stderr={view_result.stderr.strip()!r}",
            stage="post-close-readback",
            comment_succeeded=True,
            close_succeeded=True,
        )
    try:
        verified_state = json.loads(view_result.stdout)
    except Exception as exc:
        raise CloseMutationError(
            f"close state verification returned invalid JSON: {exc}",
            stage="post-close-readback",
            comment_succeeded=True,
            close_succeeded=True,
        ) from exc
    try:
        require_identity(
            verified_state,
            expected_repo=repo,
            expected_number=number,
            context="post-mutation issue readback",
        )
    except RuntimeError as exc:
        raise CloseMutationError(
            str(exc),
            stage="post-close-readback",
            comment_succeeded=True,
            close_succeeded=True,
        ) from exc
    if verified_state.get("state") != "CLOSED":
        raise CloseMutationError(
            f"close state verification failed: {repo}#{number} is {verified_state.get('state')!r}",
            stage="post-close-readback",
            comment_succeeded=True,
            close_succeeded=True,
        )
    return verified_state


def close_after_comment(
    close_argv: list[str],
    view_argv: list[str] | None,
    *,
    repo: str,
    number: int,
    run_backend: Any,
    require_identity: Any,
) -> dict[str, Any] | None:
    close_result = run_backend(close_argv)
    if close_result.returncode != 0:
        raise CloseMutationError(
            "close failed after comment landed; do not re-comment on retry. "
            f"comment_succeeded=True close_exit={close_result.returncode} "
            f"close_stderr={close_result.stderr.strip()!r}",
            stage="close",
            comment_succeeded=True,
            close_succeeded=False,
        )
    return _closed_readback(
        view_argv,
        repo=repo,
        number=number,
        run_backend=run_backend,
        require_identity=require_identity,
    )


def comment_close(
    comment_argv: list[str],
    close_argv: list[str],
    view_argv: list[str] | None,
    *,
    repo: str,
    number: int,
    run_backend: Any,
    require_identity: Any,
) -> dict[str, Any] | None:
    comment_result = run_backend(comment_argv)
    if comment_result.returncode != 0:
        raise CloseMutationError(
            f"comment failed: exit={comment_result.returncode} stderr={comment_result.stderr.strip()!r}",
            stage="comment",
            comment_succeeded=False,
            close_succeeded=False,
        )
    return close_after_comment(
        close_argv,
        view_argv,
        repo=repo,
        number=number,
        run_backend=run_backend,
        require_identity=require_identity,
    )
