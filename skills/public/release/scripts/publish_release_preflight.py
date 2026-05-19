from __future__ import annotations

from pathlib import Path
from typing import Callable

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"


def validate_critique_artifact_arg(
    repo_root: Path,
    artifact: str | None,
    *,
    run_command: Callable,
) -> str | None:
    if artifact is None:
        return None
    relpath = Path(artifact)
    if relpath.is_absolute() or any(part in ("", ".", "..") for part in relpath.parts):
        raise SystemExit("--critique-artifact must be a normalized repo-relative path")
    normalized = relpath.as_posix()
    if not normalized.startswith(CRITIQUE_ARTIFACT_PREFIX) or relpath.suffix != ".md":
        raise SystemExit("--critique-artifact must point at a critique markdown artifact")
    resolved = (repo_root / relpath).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise SystemExit("--critique-artifact must stay inside the repo root") from exc
    if not resolved.is_file():
        raise SystemExit(f"--critique-artifact does not exist: {normalized}")
    tracked = run_command(["git", "ls-files", "--error-unmatch", normalized], cwd=repo_root, check=False)
    if tracked.returncode != 0:
        raise SystemExit(f"--critique-artifact must be tracked before release: {normalized}")
    return normalized


def safe_real_host_payload(repo_root: Path, repo_paths: list[str], *, build_payload: Callable) -> dict:
    try:
        return build_payload(repo_root, repo_paths)
    except Exception as exc:  # pragma: no cover - fallback only
        return {
            "required": False,
            "changed_paths": repo_paths,
            "surface_hits": [],
            "path_hits": [],
            "checklist": [],
            "reason": f"Real-host/public verification probe could not run: {exc}",
        }
