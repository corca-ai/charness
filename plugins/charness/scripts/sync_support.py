#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import (
    load_manifests,
    materialize_support,
    now_iso,
    upsert_lock,
)
from scripts.support_sync_lib import parse_upstream_checkout, support_state_for_manifest


def sync_one(
    repo_root: Path,
    manifest: dict[str, object],
    *,
    execute: bool,
    upstream_checkouts: dict[str, Path],
) -> dict[str, object]:
    support = manifest.get("support_skill_source")
    if not support:
        return {
            "tool_id": manifest["tool_id"],
            "status": "skipped",
            "reason": "integration has no support_skill_source",
        }

    state = support_state_for_manifest(manifest)
    result = {
        "tool_id": manifest["tool_id"],
        "status": "dry-run" if not execute else "synced",
        "support_state": state,
        "source_type": support["source_type"],
        "source_path": support["path"],
        "materialized_paths": [],
        "cache_path": None,
        "content_digest": None,
    }
    if execute:
        materialized = materialize_support(
            repo_root,
            manifest,
            upstream_checkouts=upstream_checkouts,
        )
        result.update(materialized)
        upsert_lock(
            repo_root,
            manifest,
            support={
                "synced_at": now_iso(),
                "support_state": state,
                "source_type": support["source_type"],
                "source_path": support["path"],
                "ref": support.get("ref"),
                "cache_path": result["cache_path"],
                "content_digest": result["content_digest"],
                "materialized_paths": result["materialized_paths"],
            },
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--upstream-checkout", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    upstream_checkouts = dict(parse_upstream_checkout(value) for value in args.upstream_checkout)
    manifests = load_manifests(repo_root)
    selected = [manifest for manifest in manifests if not args.tool_id or manifest["tool_id"] in args.tool_id]
    results = [
        sync_one(
            repo_root,
            manifest,
            execute=args.execute,
            upstream_checkouts=upstream_checkouts,
        )
        for manifest in selected
    ]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['tool_id']}: {result['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
