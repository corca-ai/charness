#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

lifecycle = import_repo_module(__file__, "scripts.control_plane_lifecycle_lib")
support_sync = import_repo_module(__file__, "scripts.support_sync_lib")
_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.control_plane_lib")
load_manifests = _scripts_control_plane_lib_module.load_manifests
now_iso = _scripts_control_plane_lib_module.now_iso
upsert_lock = _scripts_control_plane_lib_module.upsert_lock

Payload = dict[str, object]


def sync_one(
    repo_root: Path,
    manifest: Payload,
    *,
    execute: bool,
    upstream_checkouts: dict[str, Path],
) -> Payload:
    support = manifest.get("support_skill_source")
    if not support:
        return {
            "tool_id": manifest["tool_id"],
            "status": "skipped",
            "reason": "integration has no support_skill_source",
        }

    state = support_sync.support_state_for_manifest(manifest)
    result = {
        "tool_id": manifest["tool_id"],
        "status": "dry-run" if not execute else "synced",
        "support_state": state,
        "intent_triggers": manifest.get("intent_triggers", []),
        "source_type": support["source_type"],
        "source_path": support["path"],
        "materialized_paths": [],
        "cache_path": None,
        "content_digest": None,
        "discovery_stub_path": None,
    }
    if execute:
        materialized = support_sync.materialize_support(
            repo_root,
            manifest,
            upstream_checkouts=upstream_checkouts,
        )
        result.update(materialized)
        if result["materialized_paths"]:
            result["discovery_stub_path"] = support_sync.write_discovery_stub(
                repo_root,
                manifest,
                support_skill_path=f"{result['materialized_paths'][0]}/SKILL.md",
            )
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
    upstream_checkouts = dict(support_sync.parse_upstream_checkout(value) for value in args.upstream_checkout)
    selected = lifecycle.select_by_tool_id(load_manifests(repo_root), args.tool_id)
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
        lifecycle.print_tool_statuses(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
