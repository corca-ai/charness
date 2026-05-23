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

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_worktree_adapter_lib import detect, render_template  # noqa: E402

DEFAULT_TARGET = Path(".agents/worktree-adapter.yaml")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .agents/worktree-adapter.yaml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be manifest to stdout instead of writing.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    detection = detect(repo_root)
    rendered = render_template(detection)
    if args.dry_run:
        sys.stdout.write(rendered)
        return 0
    target = (repo_root / DEFAULT_TARGET).resolve()
    if target.is_file() and not args.force:
        print(f"{target} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    print(f"wrote {target.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
