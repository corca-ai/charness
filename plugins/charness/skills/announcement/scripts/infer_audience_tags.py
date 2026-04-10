#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def has_match(pattern: str, repo_root: Path) -> bool:
    result = subprocess.run(
        ["rg", "-n", pattern, "README.md", "docs", "scripts", "skills", "profiles"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def infer_tags(repo_root: Path) -> list[dict[str, str]]:
    tags: list[dict[str, str]] = []
    if has_match(r"user|usage|cli|command", repo_root):
        tags.append({"tag": "user", "reason": "docs or commands describe a human-usable surface."})
    if has_match(r"setup|deploy|operator|maintenance|doctor", repo_root):
        tags.append({"tag": "operator", "reason": "the repo exposes setup, maintenance, or operator-facing flows."})
    if has_match(r"test|ruff|pytest|scripts/run-quality|development", repo_root):
        tags.append({"tag": "developer", "reason": "the repo exposes direct source and validation workflows."})
    return tags


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    sys.stdout.write(json.dumps({"candidates": infer_tags(args.repo_root.resolve())}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
