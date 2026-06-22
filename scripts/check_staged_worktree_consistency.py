#!/usr/bin/env python3
"""Pre-commit gate: a staged file must not also carry unstaged worktree edits.

Many pre-commit gates (validate_handoff_artifact, check-markdown, check_doc_links,
...) validate the WORKING TREE, not the staged index blob. If a file is staged and
then edited again, those gates validate the on-disk version while git commits the
stale staged blob -- a gate can pass on content that is not what lands. Observed:
a 71-line handoff committed past a 70-line cap because the validator read the
70-line worktree while the index still held the 71-line blob.

This gate fails when a staged path also has unstaged worktree modifications, so
"what the gates validate" == "what is committed". Set CHARNESS_ALLOW_PARTIAL_STAGE=1
to allow a deliberate partial (`git add -p`) commit.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ALLOW_ENV = "CHARNESS_ALLOW_PARTIAL_STAGE"


def _git_names(repo_root: Path, *args: str) -> set[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return {line for line in result.stdout.splitlines() if line}


def find_stale_staged(repo_root: Path) -> list[str]:
    """Paths that are staged (index != HEAD) AND have further unstaged worktree edits."""
    staged = _git_names(repo_root, "diff", "--cached", "--name-only", "--diff-filter=ACM")
    unstaged = _git_names(repo_root, "diff", "--name-only", "--diff-filter=ACM")
    return sorted(staged & unstaged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if os.environ.get(ALLOW_ENV):
        return 0

    stale = find_stale_staged(repo_root)
    if not stale:
        return 0

    sys.stderr.write(
        "staged files also have unstaged edits; pre-commit gates validate the\n"
        "working tree, so the staged (committed) blob is NOT what was checked.\n"
        "Re-stage so what is validated is what commits:\n"
        + "".join(f"  git add {path}\n" for path in stale)
        + f"(or set {ALLOW_ENV}=1 for a deliberate partial commit).\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
