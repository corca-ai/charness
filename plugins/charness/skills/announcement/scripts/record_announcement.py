#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--head-commit", required=True)
    parser.add_argument("--delivery-kind", default="none")
    parser.add_argument("--delivery-target", default="")
    parser.add_argument("--artifact-path", default="charness-artifacts/announcement/latest.md")
    parser.add_argument("--commits", nargs="*", default=[])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    state_dir = repo_root / ".charness" / "announcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    record_path = state_dir / "announcements.jsonl"
    record = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "head_commit": args.head_commit,
        "delivery_kind": args.delivery_kind,
        "delivery_target": args.delivery_target,
        "artifact_path": args.artifact_path,
        "commits": args.commits,
    }
    with record_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    sys.stdout.write(f"{record_path}\n")


if __name__ == "__main__":
    main()
