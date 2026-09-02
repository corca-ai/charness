"""Shared ownership rules for critique artifacts and append-only round records."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_artifact_run_scope = import_repo_module(__file__, "scripts.artifacts.artifact_run_scope")
safe_repo_relative_path = _artifact_run_scope.safe_repo_relative_path
_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
DEFAULT_CRITIQUE_ROOT = _quality_universes.DEFAULT_ARTIFACT_ROOTS["critique"]

CRITIQUE_ARTIFACT_PREFIX = f"{DEFAULT_CRITIQUE_ROOT}/"
CRITIQUE_ROUNDS_PREFIX = f"{DEFAULT_CRITIQUE_ROOT}/rounds/"


def is_critique_round_record(relpath: str, *, rounds_prefix: str = CRITIQUE_ROUNDS_PREFIX) -> bool:
    """Whether a normalized repo-relative path belongs to round evidence."""

    return relpath.startswith(rounds_prefix) and relpath.endswith(".md")


def candidate_paths(
    repo_root: Path,
    paths: Sequence[str],
    *,
    all_artifacts: bool,
    packet_checker: Callable[[Path], bool],
    artifact_prefix: str = CRITIQUE_ARTIFACT_PREFIX,
    universe_files: Sequence[Path] | None = None,
) -> list[Path]:
    """Select final critique records, excluding packets and round evidence."""

    prefix = artifact_prefix.rstrip("/") + "/"
    rounds_prefix = f"{prefix}rounds/"
    raw_paths = (
        sorted(universe_files)
        if all_artifacts and universe_files is not None
        else sorted((repo_root / prefix).glob("*.md"))
        if all_artifacts
        else paths
    )
    candidates: list[Path] = []
    for raw in raw_paths:
        normalized = safe_repo_relative_path(
            raw.relative_to(repo_root).as_posix() if isinstance(raw, Path) else str(raw)
        )
        if normalized is None or not normalized.startswith(prefix):
            continue
        if is_critique_round_record(normalized, rounds_prefix=rounds_prefix):
            continue
        path = repo_root / normalized
        # Changed-path mode receives every changed artifact, including JSON/YAML
        # packets and worker receipts. Those are evidence inputs, not Markdown
        # critique records; sending them through the prose validator creates a
        # false failure and teaches callers to delete valid evidence.
        if path.suffix.lower() != ".md":
            continue
        if path.is_file() and not packet_checker(path):
            candidates.append(path)
    return sorted(candidates)
