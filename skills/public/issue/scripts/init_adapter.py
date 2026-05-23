#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """version: 1
default_org: corca-ai
remote_name: origin
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root where the issue adapter should be written")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing adapter file")
    args = parser.parse_args()

    adapter_path = args.repo_root.resolve() / ".agents" / "issue-adapter.yaml"
    if adapter_path.exists() and not args.force:
        print(f"{adapter_path} already exists")
        return 0
    adapter_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_path.write_text(TEMPLATE, encoding="utf-8")
    print(f"Wrote {adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
