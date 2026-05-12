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
add_dependency = _scripts_control_plane_lib_module.add_dependency
load_manifests = _scripts_control_plane_lib_module.load_manifests
now_iso = _scripts_control_plane_lib_module.now_iso
upsert_lock = _scripts_control_plane_lib_module.upsert_lock
_scripts_install_provenance_lib_module = import_repo_module(__file__, "scripts.install_provenance_lib")
detect_install_provenance = _scripts_install_provenance_lib_module.detect_install_provenance
_scripts_upstream_release_lib_module = import_repo_module(__file__, "scripts.upstream_release_lib")
probe_release = _scripts_upstream_release_lib_module.probe_release

Payload = dict[str, object]
CommandList = list[Payload] | list[str]


def base_result(repo_root: Path, manifest: Payload, install_action: Payload, *, status: str, mode: str, commands: CommandList, detect: Payload | None = None, healthcheck: Payload | None = None, readiness: Payload | None = None) -> Payload:
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
    if readiness is not None:
        result["readiness"] = readiness
    return result


def capture_provenance(manifest: Payload) -> Payload:
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    return provenance


def persist_install_lock(repo_root: Path, manifest: Payload, install_action: Payload, *, status: str, mode: str, commands: list[Payload], detect: Payload, healthcheck: Payload, readiness: Payload, release: Payload | None, provenance: Payload) -> None:
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
            "readiness": readiness,
            "docs_url": install_action.get("docs_url"),
            "package_manager": provenance.get("install_method") if provenance.get("install_method") in {"npm", "cargo", "go"} else None,
            "package_name": provenance.get("package_name"),
            "notes": install_action.get("notes", []),
        },
    )


def readiness_after_successful_checks(repo_root: Path, manifest: Payload, detect_result: Payload, healthcheck_result: Payload) -> Payload:
    if detect_result["ok"] and healthcheck_result["ok"]:
        return lifecycle.evaluate_readiness(manifest, repo_root)
    return {
        "ok": False,
        "checks": [],
        "failed_checks": [],
    }


def passive_install_status(mode: str, detect_result: Payload, healthcheck_result: Payload, readiness_result: Payload) -> str:
    status = "noop" if mode == "none" else "manual"
    if not (detect_result["ok"] and healthcheck_result["ok"]):
        return status
    if readiness_result["ok"]:
        return "noop" if mode == "none" else "already-installed"
    return "installed-not-ready"


def install_one(repo_root: Path, manifest: Payload, *, execute: bool) -> Payload:
    disabled = lifecycle.disabled_by_cautilus_adapter(repo_root, manifest)
    if disabled is not None:
        install_action = manifest["lifecycle"]["install"]
        return base_result(
            repo_root,
            manifest,
            install_action,
            status="skipped",
            mode="disabled",
            commands=[],
            detect=lifecycle.disabled_check_payload(disabled),
            healthcheck=lifecycle.disabled_check_payload(disabled),
        ) | {
            "reason": disabled["reason"],
            "adapter_path": disabled["adapter_path"],
        }

    install_action = manifest["lifecycle"]["install"]
    mode = install_action["mode"]
    commands = install_action.get("commands", [])
    release = probe_release(manifest)
    provenance = capture_provenance(manifest)

    if mode in {"none", "manual"}:
        detect_result, healthcheck_result = lifecycle.detect_and_healthcheck(
            repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
        )
        readiness_result = readiness_after_successful_checks(repo_root, manifest, detect_result, healthcheck_result)
        status = passive_install_status(mode, detect_result, healthcheck_result, readiness_result)
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
                readiness=readiness_result,
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
            readiness=readiness_result,
        )
        return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)
    if not execute:
        result = base_result(repo_root, manifest, install_action, status="dry-run", mode=mode, commands=commands)
        return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)

    command_results = lifecycle.run_command_payloads(commands, repo_root)
    detect_result, healthcheck_result = lifecycle.detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed after install"
    )
    readiness_result = readiness_after_successful_checks(repo_root, manifest, detect_result, healthcheck_result)
    provenance = capture_provenance(manifest)
    command_ok = all(result["exit_code"] == 0 for result in command_results)
    if command_ok and detect_result["ok"] and healthcheck_result["ok"]:
        status = "installed" if readiness_result["ok"] else "installed-not-ready"
    else:
        status = "failed"
    persist_install_lock(
        repo_root,
        manifest,
        install_action,
        status=status,
        mode=mode,
        commands=command_results,
        detect=detect_result,
        healthcheck=healthcheck_result,
        readiness=readiness_result,
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
        readiness=readiness_result,
    )
    return lifecycle.attach_release_metadata(result, provenance=provenance, release=release)


_INSTALLED_STATUSES = {"installed", "already-installed"}
_FAILURE_STATUSES = {"failed", "installed-not-ready"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--add-dependency",
        action="store_true",
        help="Append successfully installed tool_ids to integrations/tools/dependencies.json",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    selected = lifecycle.select_by_tool_id(load_manifests(repo_root), args.tool_id)
    results = [install_one(repo_root, manifest, execute=args.execute) for manifest in selected]
    if args.add_dependency:
        for result in results:
            if result["status"] in _INSTALLED_STATUSES:
                result["dependency_added"] = add_dependency(repo_root, str(result["tool_id"]))
            else:
                result["dependency_added"] = False
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        lifecycle.print_tool_statuses(results)
    if lifecycle.has_any_status(results, status_key="status", statuses=_FAILURE_STATUSES):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
