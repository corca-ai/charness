#!/usr/bin/env python3

"""Seed `.agents/usage-episodes-adapter.yaml` for a product repo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_TARGET = Path(".agents/usage-episodes-adapter.yaml")
TEMPLATE = """\
# charness usage-episodes adapter: validate privacy-bounded H-LAM/T product
# usage episodes emitted by this repo. Runtime JSONL is generated local state
# under .charness/ and should not be committed except curated fixtures.
#
# Schemas and validator ship with the Charness/plugin usage-episodes integration.
# Validate from a Charness checkout or plugin install against this product repo.
version: 1
repo: my-product
enabled: true
storage_path: .charness/usage-episodes
events:
  - usage_episode
privacy:
  raw_prompt: false
  raw_transcript: false
  user_identity: host-owned
  policy_ref: docs/privacy.md
rotation:
  max_files: 10
  max_size_mb: 10
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .agents/usage-episodes-adapter.yaml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be manifest to stdout instead of writing.",
    )
    args = parser.parse_args()
    if args.dry_run:
        sys.stdout.write(TEMPLATE)
        return 0
    repo_root = args.repo_root.resolve()
    target = repo_root / DEFAULT_TARGET
    if target.is_file() and not args.force:
        print(f"{target} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {target.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
