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
# Only these spellings turn the bypass ON. "0"/"false"/"no"/"off"/"" -- the
# spellings an operator uses to turn it OFF -- must keep the gate running.
TRUE_VALUES = {"1", "true", "yes", "on"}
# No --diff-filter. The first cut used ACM, which hid a path staged and then
# DELETED on disk -- exactly the case worktree-walking validators skip entirely,
# so the staged blob shipped unchecked. Widening it to ACMRD fixed that one letter
# and left T (typechange: file <-> symlink) and U (unmerged) hidden by the same
# mechanism. An allowlist of status letters is the wrong shape for a gate whose
# question is "does this path appear on BOTH sides": every letter git can report
# is a real difference, so the intersection is the filter.


def allow_partial_stage() -> bool:
    """True only for an explicit truthy spelling of the bypass env var."""
    return os.environ.get(ALLOW_ENV, "").strip().lower() in TRUE_VALUES


def _git_names(repo_root: Path, *args: str) -> set[str]:
    """Path names from one git query, or `RuntimeError` if git could not answer.

    An empty set from a failed git is indistinguishable from "nothing staged", so
    returning it would render a clean verdict over a scope that was never read.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # git absent, cwd unusable
        raise RuntimeError(f"git {' '.join(args)}: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return {line for line in result.stdout.splitlines() if line}


def find_stale_staged(repo_root: Path) -> list[str]:
    """Paths that are staged (index != HEAD) AND have further unstaged worktree edits."""
    staged = _git_names(repo_root, "diff", "--cached", "--name-only")
    unstaged = _git_names(repo_root, "diff", "--name-only")
    return sorted(staged & unstaged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if allow_partial_stage():
        # Announced, not silent — the sibling gate at this boundary prints its own
        # `allowed` line so a deliberate bypass is acknowledged rather than hidden
        # behind a pass that looks identical to a clean run.
        sys.stderr.write(f"staged-worktree-consistency: explicitly allowed ({ALLOW_ENV})\n")
        return 0

    try:
        stale = find_stale_staged(repo_root)
    except RuntimeError as exc:
        # The sibling gate at this boundary (check_staged_reversion) reports an
        # explicit UNESTABLISHED verdict with a remedy; a bare traceback blocks
        # the same commit while telling the operator nothing.
        sys.stderr.write(
            f"UNESTABLISHED: could not read the index/worktree diff: {exc}\n"
            "This gate reports no verdict rather than a clean one. If this is a\n"
            "dubious-ownership checkout, run:\n"
            f"  git config --global --add safe.directory {repo_root}\n"
        )
        return 1
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
