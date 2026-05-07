#!/usr/bin/env python3

"""Seed `.agents/worktree-adapter.yaml` for a charness consumer repo.

The worktree adapter declares how `charness worktree prepare` should make a
freshly-created git worktree usable, and which extra `charness worktree doctor`
checks should decide whether the worktree is ready before mutate-phase work.

This helper writes a portable starter template; the consumer repo edits the
prepare commands to match its actual package manager and hook tooling.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_TARGET = Path(".agents/worktree-adapter.yaml")
TEMPLATE = """\
# charness worktree adapter — declares how `charness worktree prepare` makes a
# freshly-created git worktree usable, and which extra `charness worktree doctor`
# checks decide whether the worktree is ready.
#
# Replace the example commands below with your repo's actual package manager
# and hook installer. argv lists must use block-style YAML (charness's repo-local
# loader does not parse inline `[a, b]` arrays).
version: 1

prepare:
  commands:
    # Install dependencies for this worktree. Pick one matching your repo:
    - id: install-deps
      description: "Install workspace dependencies for this worktree."
      timeout_seconds: 600
      argv:
        - pnpm
        - install
        - --frozen-lockfile
    # Re-run hook installation so any per-worktree absolute paths point at this
    # checkout's installed tools (lefthook bakes install-time absolute paths
    # into its hook shim; husky generates a worktree-relative `_/` directory).
    - id: install-hooks
      description: "Re-run hook manager install for this worktree."
      timeout_seconds: 60
      argv:
        - pnpm
        - exec
        - lefthook
        - install
  skip_if_doctor_passes: true

# Optional manifest-defined doctor checks layered on top of the canonical suite
# (git_common_dir, hooks_path, lefthook_shim, husky_dir). Remove this whole
# block if the canonical suite is enough.
# doctor:
#   checks:
#     - id: lefthook_self_check
#       description: "Confirm lefthook resolves from this worktree."
#       next_action_hint: "Run `charness worktree prepare` to install hooks."
#       timeout_seconds: 10
#       argv:
#         - pnpm
#         - exec
#         - lefthook
#         - version
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .agents/worktree-adapter.yaml.",
    )
    args = parser.parse_args()
    target = (args.repo_root / DEFAULT_TARGET).resolve()
    if target.is_file() and not args.force:
        print(f"{target} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {target.relative_to(args.repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
