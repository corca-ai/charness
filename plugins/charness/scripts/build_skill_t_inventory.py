#!/usr/bin/env python3
"""CLI entry for the Leg 1 Skill-T mechanism inventory builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.skill_t_inventory_lib import (  # noqa: E402
        build_inventory,
        write_inventory,
    )

    paths = write_inventory(repo_root, args.output_dir)
    payload = build_inventory(repo_root)
    summary = {
        "json_path": str(paths["json"].relative_to(repo_root)),
        "markdown_path": str(paths["markdown"].relative_to(repo_root)),
        "skill_count": len(payload["skills"]),
        "tier_c_populated_skills": [
            row["skill_id"]
            for row in payload["skills"]
            if row["tier_c_events"]["status"] == "populated"
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
