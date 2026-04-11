#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_manifests, now_iso, run_check, run_shell, upsert_lock
from scripts.install_provenance_lib import detect_install_provenance, package_manager_update_action
from scripts.upstream_release_lib import probe_release


def failed_healthcheck(manifest: dict[str, object], *, reason: str) -> dict[str, object]:
    return {
        "ok": False,
        "results": [],
        "failure_details": [reason],
        "failure_hint": manifest["checks"]["healthcheck"].get("failure_hint"),
    }


def attach_metadata(
    result: dict[str, object],
    *,
    provenance: dict[str, object],
    release: dict[str, object] | None,
) -> dict[str, object]:
    result["provenance"] = provenance
    if release is not None:
        result["release"] = release
    return result


def update_one(repo_root: Path, manifest: dict[str, object], *, execute: bool) -> dict[str, object]:
    configured_action = manifest["lifecycle"]["update"]
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    routed_action = package_manager_update_action(manifest, provenance) if configured_action["mode"] == "manual" else None
    update_action = routed_action or configured_action
    mode = update_action["mode"]
    release = probe_release(manifest)
    if mode == "none":
        return attach_metadata(
            {"tool_id": manifest["tool_id"], "status": "noop", "mode": mode},
            provenance=provenance,
            release=release,
        )
    if mode == "manual":
        detect_result = run_check(manifest["checks"]["detect"], repo_root)
        healthcheck_result = (
            run_check(manifest["checks"]["healthcheck"], repo_root)
            if detect_result["ok"]
            else failed_healthcheck(manifest, reason="detect failed; healthcheck skipped")
        )
        result = {
            "tool_id": manifest["tool_id"],
            "status": "manual",
            "mode": mode,
            "docs_url": update_action.get("docs_url"),
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
        return attach_metadata(result, provenance=provenance, release=release)
    if not execute:
        return attach_metadata(
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
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck_result = (
        run_check(manifest["checks"]["healthcheck"], repo_root)
        if detect_result["ok"]
        else failed_healthcheck(manifest, reason="detect failed after update")
    )
    status = "updated" if all(result.exit_code == 0 for result in command_results) and detect_result["ok"] and healthcheck_result["ok"] else "failed"
    payload = {
        "updated_at": now_iso(),
        "update_status": status,
        "mode": mode,
        "commands": [
            {
                "command": result.command,
                "exit_code": result.exit_code,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
            for result in command_results
        ],
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
    return attach_metadata(result, provenance=provenance, release=release)


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
