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
sys.path.insert(0, str(REPO_ROOT))

from scripts.tool_recommendation_lib import recommendations_for_role


def _load_manifests(root: Path) -> list[dict[str, object]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / "integrations" / "tools").glob("*.json"))
        if path.name != "manifest.schema.json"
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--recommendation-role", default="validation")
    parser.add_argument("--next-skill-id", default="quality")
    parser.add_argument("--include-ready", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = {
        "recommendation_role": args.recommendation_role,
        "next_skill_id": args.next_skill_id,
        "tool_recommendations": recommendations_for_role(
            repo_root,
            _load_manifests(repo_root),
            recommendation_role=args.recommendation_role,
            next_skill_id=args.next_skill_id,
            only_blocking=not args.include_ready,
        ),
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
