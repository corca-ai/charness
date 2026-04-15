#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_manifests, now_iso, run_shell, upsert_lock
from scripts.control_plane_lifecycle_lib import (
    attach_release_metadata,
    command_result_payload,
    detect_and_healthcheck,
)
from scripts.install_provenance_lib import detect_install_provenance, package_manager_update_action
from scripts.upstream_release_lib import probe_release


def update_one(repo_root: Path, manifest: dict[str, object], *, execute: bool) -> dict[str, object]:
    configured_action = manifest["lifecycle"]["update"]
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    routed_action = package_manager_update_action(manifest, provenance) if configured_action["mode"] == "manual" else None
    update_action = routed_action or configured_action
    mode = update_action["mode"]
    release = probe_release(manifest)
    if mode == "none":
        return attach_release_metadata(
            {"tool_id": manifest["tool_id"], "status": "noop", "mode": mode},
            provenance=provenance,
            release=release,
        )
    if mode == "manual":
        detect_result, healthcheck_result = detect_and_healthcheck(
            repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
        )
        result = {
            "tool_id": manifest["tool_id"],
            "status": "manual",
            "mode": mode,
            "docs_url": update_action.get("docs_url"),
            "install_url": update_action.get("install_url"),
            "notes": update_action.get("notes", []),
            "commands": [],
            "detect": detect_result,
            "healthcheck": healthcheck_result,
        }
        if execute:
            upsert_lock(
                repo_root,
                manifest,
                release=release,
                provenance=provenance,
                update={
                    "updated_at": now_iso(),
                    "update_status": "manual",
                    "mode": mode,
                    "commands": [],
                    "detect": detect_result,
                    "healthcheck": healthcheck_result,
                    "package_manager": None,
                    "package_name": None,
                },
            )
        return attach_release_metadata(result, provenance=provenance, release=release)
    if not execute:
        return attach_release_metadata(
            {
                "tool_id": manifest["tool_id"],
                "status": "dry-run",
                "mode": mode,
                "commands": update_action.get("commands", []),
                "package_manager": update_action.get("package_manager"),
                "package_name": update_action.get("package_name"),
            },
            provenance=provenance,
            release=release,
        )

    command_results = [run_shell(command, repo_root) for command in update_action.get("commands", [])]
    detect_result, healthcheck_result = detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed after update"
    )
    status = "updated" if all(result.exit_code == 0 for result in command_results) and detect_result["ok"] and healthcheck_result["ok"] else "failed"
    payload = {
        "updated_at": now_iso(),
        "update_status": status,
        "mode": mode,
        "commands": [command_result_payload(result) for result in command_results],
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "package_manager": update_action.get("package_manager"),
        "package_name": update_action.get("package_name"),
    }
    upsert_lock(repo_root, manifest, release=release, provenance=provenance, update=payload)
    result = {
        "tool_id": manifest["tool_id"],
        "status": status,
        "mode": mode,
        "commands": payload["commands"],
        "package_manager": payload["package_manager"],
        "package_name": payload["package_name"],
    }
    return attach_release_metadata(result, provenance=provenance, release=release)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifests = load_manifests(repo_root)
    selected = [manifest for manifest in manifests if not args.tool_id or manifest["tool_id"] in args.tool_id]
    results = [update_one(repo_root, manifest, execute=args.execute) for manifest in selected]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['tool_id']}: {result['status']}")
    if any(result["status"] == "failed" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
