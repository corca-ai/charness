#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
_RESOLVER_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"
sys.path[:0] = [str(REPO_ROOT), str(_RESOLVER_DIR)]

from resolve_adapter import load_adapter

from scripts.recent_lessons_lib import build_recent_lessons, pick_latest_retro_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    summary_rel = adapter["data"]["summary_path"]
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_path = repo_root / summary_rel
    source_path = (repo_root / args.source).resolve() if args.source else pick_latest_retro_markdown(output_dir, summary_path)
    digest = build_recent_lessons(source_path, repo_root=repo_root)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(digest.summary_text + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_path": str(summary_path.relative_to(repo_root)),
                "source_path": str(digest.source_path.relative_to(repo_root)),
                "section_counts": digest.section_counts,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
