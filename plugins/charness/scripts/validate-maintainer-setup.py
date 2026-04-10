#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


class ValidationError(Exception):
    pass


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def resolve_hookspath(repo_root: Path, configured: str) -> Path:
    path = Path(configured)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    expected_hook = repo_root / ".githooks" / "pre-push"
    if not expected_hook.exists():
        print("No checked-in pre-push hook to validate.")
        return 0

    worktree = run_git(repo_root, "rev-parse", "--is-inside-work-tree")
    if worktree.returncode != 0 or worktree.stdout.strip() != "true":
        print("Repo is not a git worktree; maintainer hook validation skipped.")
        return 0

    configured = run_git(repo_root, "config", "--get", "core.hooksPath")
    if configured.returncode != 0 or not configured.stdout.strip():
        raise ValidationError(
            "checked-in `.githooks/pre-push` is not active in this clone; run `./scripts/install-git-hooks.sh`"
        )

    configured_path = resolve_hookspath(repo_root, configured.stdout.strip())
    expected_dir = (repo_root / ".githooks").resolve()
    if configured_path != expected_dir:
        raise ValidationError(
            f"core.hooksPath points to `{configured.stdout.strip()}` instead of repo-owned `.githooks`; "
            "run `./scripts/install-git-hooks.sh`"
        )

    print(f"Validated maintainer hook setup via {expected_dir}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
