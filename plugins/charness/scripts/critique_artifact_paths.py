"""Shared ownership rules for critique artifacts and append-only round records."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from runtime_bootstrap import import_repo_module

_artifact_run_scope = import_repo_module(__file__, "scripts.artifact_run_scope")
safe_repo_relative_path = _artifact_run_scope.safe_repo_relative_path

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
CRITIQUE_ROUNDS_PREFIX = "charness-artifacts/critique/rounds/"


def is_critique_round_record(relpath: str) -> bool:
    """Whether a normalized repo-relative path belongs to round evidence."""

    return relpath.startswith(CRITIQUE_ROUNDS_PREFIX) and relpath.endswith(".md")


def candidate_paths(
    repo_root: Path,
    paths: Sequence[str],
    *,
    all_artifacts: bool,
    packet_checker: Callable[[Path], bool],
) -> list[Path]:
    """Select final critique records, excluding packets and round evidence."""

    raw_paths = sorted((repo_root / CRITIQUE_ARTIFACT_PREFIX).glob("*.md")) if all_artifacts else paths
    candidates: list[Path] = []
    for raw in raw_paths:
        normalized = safe_repo_relative_path(
            raw.relative_to(repo_root).as_posix() if isinstance(raw, Path) else str(raw)
        )
        if normalized is None or not normalized.startswith(CRITIQUE_ARTIFACT_PREFIX):
            continue
        if is_critique_round_record(normalized):
            continue
        path = repo_root / normalized
        if path.is_file() and not packet_checker(path):
            candidates.append(path)
    return sorted(candidates)
