from __future__ import annotations

import subprocess
from pathlib import Path


class GitFileListingError(RuntimeError):
    pass


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def visible_repo_files(repo_root: Path, *, require_git: bool = False, context: str = "git file listing") -> set[Path] | None:
    command = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
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
