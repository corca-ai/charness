#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

lifecycle = import_repo_module(__file__, "scripts.control_plane_lifecycle_lib")
_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.control_plane_lib")
load_manifests = _scripts_control_plane_lib_module.load_manifests
now_iso = _scripts_control_plane_lib_module.now_iso
upsert_lock = _scripts_control_plane_lib_module.upsert_lock
_scripts_install_provenance_lib_module = import_repo_module(__file__, "scripts.install_provenance_lib")
detect_install_provenance = _scripts_install_provenance_lib_module.detect_install_provenance
_scripts_upstream_release_lib_module = import_repo_module(__file__, "scripts.upstream_release_lib")
probe_release = _scripts_upstream_release_lib_module.probe_release

Payload = dict[str, object]
CommandList = list[Payload] | list[str]


def base_result(
    repo_root: Path,
    manifest: Payload,
    install_action: Payload,
    *,
    status: str,
    mode: str,
    commands: CommandList,
    detect: Payload | None = None,
    healthcheck: Payload | None = None,
) -> Payload:
    result = {
        "tool_id": manifest["tool_id"],
        "status": status,
        "mode": mode,
        "docs_url": install_action.get("docs_url"),
        "install_url": install_action.get("install_url"),
        "repo_followup": lifecycle.render_repo_followup(repo_root, install_action),
        "notes": install_action.get("notes", []),
        "commands": commands,
    }
    if detect is not None:
        result["detect"] = detect
    if healthcheck is not None:
        result["healthcheck"] = healthcheck
    return result


def capture_provenance(manifest: Payload) -> Payload:
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    return provenance


def persist_install_lock(
    repo_root: Path,
    manifest: Payload,
    install_action: Payload,
    *,
    status: str,
    mode: str,
    commands: list[Payload],
    detect: Payload,
    healthcheck: Payload,
    release: Payload | None,
    provenance: Payload,
) -> None:
    upsert_lock(
        repo_root,
        manifest,
        release=release,
        provenance=provenance,
        install={
            "installed_at": now_iso(),
            "install_status": status,
            "mode": mode,
            "commands": commands,
            "detect": detect,
            "healthcheck": healthcheck,
            "docs_url": install_action.get("docs_url"),
            "package_manager": provenance.get("install_method") if provenance.get("install_method") in {"brew", "npm", "cargo", "go"} else None,
            "package_name": provenance.get("package_name"),
            "notes": install_action.get("notes", []),
        },
    )


def install_one(repo_root: Path, manifest: Payload, *, execute: bool) -> Payload:
    install_action = manifest["lifecycle"]["install"]
    mode = install_action["mode"]
    commands = install_action.get("commands", [])
    release = probe_release(manifest)
    provenance = capture_provenance(manifest)

    if mode in {"none", "manual"}:
        detect_result, healthcheck_result = lifecycle.detect_and_healthcheck(
            repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
        )
        status = "noop" if mode == "none" else "manual"
        if status == "manual" and detect_result["ok"] and healthcheck_result["ok"]:
            status = "already-installed"
        if execute:
            persist_install_lock(
                repo_root,
                manifest,
                install_action,
                status=status,
                mode=mode,
                commands=[],
                detect=detect_result,
                healthcheck=healthcheck_result,
                release=release,
                provenance=provenance,
            )
        result = base_result(
            repo_root,
            manifest,
            install_action,
            status=status,
            mode=mode,
            commands=[],
            detect=detect_result,
            healthcheck=healthcheck_result,
        )
        return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)
    if not execute:
        result = base_result(repo_root, manifest, install_action, status="dry-run", mode=mode, commands=commands)
        return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)

    command_results = lifecycle.run_command_payloads(commands, repo_root)
    detect_result, healthcheck_result = lifecycle.detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed after install"
    )
    provenance = capture_provenance(manifest)
    status = (
        "installed"
        if all(result["exit_code"] == 0 for result in command_results) and detect_result["ok"] and healthcheck_result["ok"]
        else "failed"
    )
    persist_install_lock(
        repo_root,
        manifest,
        install_action,
        status=status,
        mode=mode,
        commands=command_results,
        detect=detect_result,
        healthcheck=healthcheck_result,
        release=release,
        provenance=provenance,
    )
    result = base_result(
        repo_root,
        manifest,
        install_action,
        status=status,
        mode=mode,
        commands=command_results,
        detect=detect_result,
        healthcheck=healthcheck_result,
    )
    return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    selected = lifecycle.select_by_tool_id(load_manifests(repo_root), args.tool_id)
    results = [install_one(repo_root, manifest, execute=args.execute) for manifest in selected]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        lifecycle.print_tool_statuses(results)
    if lifecycle.has_any_status(results, status_key="status", statuses={"failed"}):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
