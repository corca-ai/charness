#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.control_plane_lib")
load_manifests = _scripts_control_plane_lib_module.load_manifests
now_iso = _scripts_control_plane_lib_module.now_iso
run_shell = _scripts_control_plane_lib_module.run_shell
upsert_lock = _scripts_control_plane_lib_module.upsert_lock
_scripts_control_plane_lifecycle_lib_module = import_repo_module(__file__, "scripts.control_plane_lifecycle_lib")
attach_release_metadata = _scripts_control_plane_lifecycle_lib_module.attach_release_metadata
command_result_payload = _scripts_control_plane_lifecycle_lib_module.command_result_payload
detect_and_healthcheck = _scripts_control_plane_lifecycle_lib_module.detect_and_healthcheck
has_any_status = _scripts_control_plane_lifecycle_lib_module.has_any_status
print_tool_statuses = _scripts_control_plane_lifecycle_lib_module.print_tool_statuses
select_by_tool_id = _scripts_control_plane_lifecycle_lib_module.select_by_tool_id
_scripts_install_provenance_lib_module = import_repo_module(__file__, "scripts.install_provenance_lib")
detect_install_provenance = _scripts_install_provenance_lib_module.detect_install_provenance
package_manager_update_action = _scripts_install_provenance_lib_module.package_manager_update_action
_scripts_upstream_release_lib_module = import_repo_module(__file__, "scripts.upstream_release_lib")
probe_release = _scripts_upstream_release_lib_module.probe_release


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
    selected = select_by_tool_id(load_manifests(repo_root), args.tool_id)
    results = [update_one(repo_root, manifest, execute=args.execute) for manifest in selected]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_tool_statuses(results)
    if has_any_status(results, status_key="status", statuses={"failed"}):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
