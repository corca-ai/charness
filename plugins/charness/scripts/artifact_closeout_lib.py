from __future__ import annotations

from typing import Any


def artifact_closeout_status(
    *,
    artifact_paths: list[str],
    semantic_content_changed: bool,
    reason: str,
    unchanged_reason: str | None = None,
    requires_repo_closeout: bool | None = None,
    commit_recommended: bool | None = None,
) -> dict[str, Any]:
    requires_closeout = semantic_content_changed if requires_repo_closeout is None else requires_repo_closeout
    recommends_commit = requires_closeout if commit_recommended is None else commit_recommended
    return {
        "artifact_paths": artifact_paths,
        "semantic_content_changed": semantic_content_changed,
        "requires_repo_closeout": requires_closeout,
        "commit_recommended": recommends_commit,
        "closeout_reason": reason if semantic_content_changed else (unchanged_reason or "artifact content unchanged"),
    }
