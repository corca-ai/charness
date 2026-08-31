from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


def _ensure_scripts_package() -> None:
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "scripts" / "git_checkout.py").is_file():
            root = str(candidate)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


_ensure_scripts_package()
from scripts.git_checkout import discoverable as _git_metadata_is_discoverable  # noqa: E402


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
