#!/usr/bin/env python3

"""Seed `.agents/worktree-adapter.yaml` for a charness consumer repo.

The worktree adapter declares how `charness worktree prepare` should make a
freshly-created git worktree usable, and which extra `charness worktree doctor`
checks should decide whether the worktree is ready before mutate-phase work.

This helper detects the consumer repo's package manager and hook system, then
writes a starter template matched to that stack. Detection lives in
`seed_worktree_adapter_lib.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_adapter_cli_lib import run_seed_adapter  # noqa: E402
from seed_worktree_adapter_lib import detect, render_template  # noqa: E402

DEFAULT_TARGET = Path(".agents/worktree-adapter.yaml")


def main() -> int:
    return run_seed_adapter(
        description=__doc__,
        repo_root_help="Repo root whose worktree adapter should be seeded",
        target=DEFAULT_TARGET,
        force_help="Overwrite an existing .agents/worktree-adapter.yaml.",
        render=lambda repo_root: render_template(detect(repo_root)),
    )


if __name__ == "__main__":
    sys.exit(main())
