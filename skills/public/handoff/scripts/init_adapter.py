#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def scaffold_adapter(repo_name: str) -> str:
    return "\n".join(
        [
            "version: 1",
            f"repo: {repo_name}",
            "language: en",
            "output_dir: skill-outputs/handoff",
            "preset_id: portable-defaults",
            "customized_from: portable-defaults",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".agents/handoff-adapter.yaml"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo_root / args.output
    if output.exists() and not args.force:
        raise SystemExit(f"Adapter already exists at {output}. Use --force to overwrite.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(scaffold_adapter(repo_root.name), encoding="utf-8")
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
