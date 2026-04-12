#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.simple_skill_adapter_lib import load_simple_adapter


def load_adapter(repo_root: Path) -> dict[str, object]:
    return load_simple_adapter(
        repo_root,
        skill_id="init-repo",
        artifact_filename="init-repo.md",
        default_output_dir="skill-outputs/init-repo",
        missing_warnings=(
            "No init-repo adapter found. Using default durable artifact location.",
            "Create .agents/init-repo-adapter.yaml to move the artifact path or record preset provenance.",
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    sys.stdout.write(json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
