from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitFileListingError(RuntimeError):
    pass


@dataclass(frozen=True)
class VisibleRepoFilesSnapshot:
    """One caller-owned view of the repo's git-visible files.

    The snapshot is deliberately not cached here: a mutable checkout must be
    re-read by its next operation. Callers that perform several related scans
    may capture once and pass this value through each scan explicitly.
    """

    files: set[Path] | None


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def _git_metadata_is_discoverable(repo_root: Path) -> bool:
    """Admit the same local Git discovery boundary as ``repo_file_listing``.

    A missing or empty ``.git`` is not a repository. Asking Git only confirms
    that, so the probe has no information value.
    """
    if any(os.environ.get(name) for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")):
        return True
    root = repo_root.resolve()
    if not root.is_dir():
        return False
    if (root / "HEAD").is_file() and (root / "objects").is_dir() and (root / "refs").is_dir():
        return True
    for candidate in (root, *root.parents):
        marker = candidate / ".git"
        if marker.is_file():
            try:
                if marker.read_text(encoding="utf-8").lstrip().startswith("gitdir:"):
                    return True
            except OSError:
                continue
        elif marker.is_dir() and (marker / "HEAD").is_file():
            if (marker / "objects").is_dir() or (marker / "commondir").is_file():
                return True
    return False


def visible_repo_files(
    repo_root: Path,
    *,
    require_git: bool = False,
    context: str = "git file listing",
    snapshot: VisibleRepoFilesSnapshot | None = None,
) -> set[Path] | None:
    if snapshot is not None:
        return snapshot.files
    command = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
    if not _git_metadata_is_discoverable(repo_root):
        if require_git:
            raise GitFileListingError(
                f"{context} failed\n"
                f"command: {' '.join(command)}\n"
                "exit_code: 128\n"
                "STDOUT:\n\n"
                "STDERR:\nnot a git repository (Git discovery preflight)"
            )
        return None
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        if require_git:
            raise GitFileListingError(
                f"{context} failed\n"
                f"command: {' '.join(command)}\n"
                f"exit_code: {result.returncode}\n"
                f"STDOUT:\n{_decode_output(result.stdout)}\n"
                f"STDERR:\n{_decode_output(result.stderr)}"
            )
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def capture_visible_repo_files(
    repo_root: Path, *, require_git: bool = False, context: str = "git file listing"
) -> VisibleRepoFilesSnapshot:
    """Capture one operation-scoped inventory without retaining global state."""
    return VisibleRepoFilesSnapshot(
        visible_repo_files(repo_root, require_git=require_git, context=context)
    )
