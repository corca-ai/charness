"""The single release-owned route for refreshing changed-line coverage."""

from __future__ import annotations

import shlex
from pathlib import Path

RELEASE_SCRIPT = "scripts/mutation/release_changed_line_coverage.py"


def release_refresh_command(repo_root: Path, base_sha: str) -> str:
    """Return the copyable release producer command for this range."""
    return (
        f"python3 {RELEASE_SCRIPT} "
        f"--repo-root {shlex.quote(str(repo_root))} "
        f"--base-sha {shlex.quote(base_sha)}"
    )


def resume_route(repo_root: Path, base_sha: str) -> str:
    """Return the one route back to a usable changed-line verdict."""
    return (
        "Run the release-owned changed-line producer to refresh the focused corpus "
        f"and render the verdict: {release_refresh_command(repo_root, base_sha)}."
    )


def resume_fields(repo_root: Path, base_sha: str) -> dict[str, str]:
    """Return structured, copyable recovery fields for a skipped consumer run."""
    return {
        "resume_command": release_refresh_command(repo_root, base_sha),
        "resume_route": resume_route(repo_root, base_sha),
    }
