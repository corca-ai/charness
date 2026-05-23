#!/usr/bin/env python3
"""Bootstrap a `.agents/critique-adapter.yaml` skeleton for a repo.

Creates a no-section adapter so the file exists in canonical shape.
Operators add `packet_sections` entries when they want the
prepare-packet contract to fire.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SKELETON = """version: 1
repo: CHANGE_ME
language: en
output_dir: charness-artifacts/critique
# Declare sections to opt into the critique prepare-packet contract.
# Without any entry, critique runs unchanged.
# See skills/public/critique/references/adapter-contract.md.
packet_sections: []
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize critique adapter skeleton")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root to scaffold the critique adapter into")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing adapter file")
    args = parser.parse_args()
    target = args.repo_root.resolve() / ".agents" / "critique-adapter.yaml"
    if target.exists() and not args.force:
        print(f"adapter already exists at {target}; pass --force to overwrite")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SKELETON, encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
