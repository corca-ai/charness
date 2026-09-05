#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.adapters.control_plane_lib")
load_manifests = _scripts_control_plane_lib_module.load_manifests
now_iso = _scripts_control_plane_lib_module.now_iso
read_lock = _scripts_control_plane_lib_module.read_lock
run_shell = _scripts_control_plane_lib_module.run_shell
upsert_lock = _scripts_control_plane_lib_module.upsert_lock
_scripts_control_plane_lifecycle_lib_module = import_repo_module(__file__, "scripts.adapters.control_plane_lifecycle_lib")
attach_release_metadata = _scripts_control_plane_lifecycle_lib_module.attach_release_metadata
command_result_payload = _scripts_control_plane_lifecycle_lib_module.command_result_payload
detect_and_healthcheck = _scripts_control_plane_lifecycle_lib_module.detect_and_healthcheck
evaluate_readiness = _scripts_control_plane_lifecycle_lib_module.evaluate_readiness
executable_action_missing_commands = (
    _scripts_control_plane_lifecycle_lib_module.executable_action_missing_commands
)
has_any_status = _scripts_control_plane_lifecycle_lib_module.has_any_status
print_update_advisories = _scripts_control_plane_lifecycle_lib_module.print_update_advisories
select_by_tool_id = _scripts_control_plane_lifecycle_lib_module.select_by_tool_id
_scripts_install_provenance_lib_module = import_repo_module(__file__, "scripts.install_provenance_lib")
detect_install_provenance = _scripts_install_provenance_lib_module.detect_install_provenance
package_manager_update_action = _scripts_install_provenance_lib_module.package_manager_update_action
_scripts_upstream_release_lib_module = import_repo_module(__file__, "scripts.upstream_release_lib")
observed_version_from_detect = _scripts_upstream_release_lib_module.observed_version_from_detect
probe_release = _scripts_upstream_release_lib_module.probe_release


def capture_provenance(manifest: dict[str, object]) -> dict[str, object]:
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    return provenance


def previous_observed_version(repo_root: Path, tool_id: str) -> str | None:
    try:
        prior_lock = read_lock(repo_root, tool_id)
    except (OSError, json.JSONDecodeError):
        prior_lock = None
    if not isinstance(prior_lock, dict):
        return None
    doctor = prior_lock.get("doctor")
    version = doctor.get("version") if isinstance(doctor, dict) else None
    observed = version.get("observed_version") if isinstance(version, dict) else None
    if isinstance(observed, str) and observed:
        return observed
    update = prior_lock.get("update")
    if isinstance(update, dict):
        return observed_version_from_detect(update.get("detect"))
    return None


def readiness_after_successful_checks(
    repo_root: Path,
    manifest: dict[str, object],
    detect_result: dict[str, object],
    healthcheck_result: dict[str, object],
) -> dict[str, object]:
    if detect_result["ok"] and healthcheck_result["ok"]:
        return evaluate_readiness(manifest, repo_root)
    return {"ok": False, "checks": [], "failed_checks": []}


def persist_update_lock(
    repo_root: Path,
    manifest: dict[str, object],
    *,
    release: dict[str, object] | None,
    provenance: dict[str, object],
    payload: dict[str, object],
) -> None:
    upsert_lock(repo_root, manifest, release=release, provenance=provenance, update=payload)


def update_payload(
    *,
    status: str,
    mode: str,
    commands: list[dict[str, object]],
    detect_result: dict[str, object],
    healthcheck_result: dict[str, object],
    readiness_result: dict[str, object],
    package_manager: object = None,
    package_name: object = None,
    version_transition: dict[str, object] | None = None,
) -> dict[str, object]:
    payload = {
        "updated_at": now_iso(),
        "update_status": status,
        "mode": mode,
        "commands": commands,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
        "package_manager": package_manager,
        "package_name": package_name,
    }
    if version_transition is not None:
        payload["version_transition"] = version_transition
    return payload


def _version_transition_changed(version_transition: dict[str, object] | None) -> bool | None:
    if not isinstance(version_transition, dict):
        return None
    from_version = version_transition.get("from")
    to_version = version_transition.get("to")
    if (
        isinstance(from_version, str)
        and from_version
        and isinstance(to_version, str)
        and to_version
    ):
        return from_version != to_version
    return None


def passive_update(
    repo_root: Path,
    manifest: dict[str, object],
    *,
    update_action: dict[str, object],
    mode: str,
    execute: bool,
    release: dict[str, object] | None,
    provenance: dict[str, object],
) -> dict[str, object]:
    detect_result, healthcheck_result = detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
    )
    readiness_result = readiness_after_successful_checks(repo_root, manifest, detect_result, healthcheck_result)
    status = "manual" if mode == "manual" else (
        "updated-not-ready" if detect_result["ok"] and healthcheck_result["ok"] and not readiness_result["ok"] else "noop"
    )
    if execute:
        persist_update_lock(
            repo_root,
            manifest,
            release=release,
            provenance=provenance,
            payload=update_payload(
                status=status,
                mode=mode,
                commands=[],
                detect_result=detect_result,
                healthcheck_result=healthcheck_result,
                readiness_result=readiness_result,
            ),
        )
    result = {
        "tool_id": manifest["tool_id"],
        "status": status,
        "mode": mode,
        "commands": [],
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
    }
    if mode == "manual":
        result |= {
            "docs_url": update_action.get("docs_url"),
            "install_url": update_action.get("install_url"),
            "notes": update_action.get("notes", []),
        }
    return attach_release_metadata(result, provenance=provenance, release=release)


def update_one(repo_root: Path, manifest: dict[str, object], *, execute: bool) -> dict[str, object]:
    configured_action = manifest["lifecycle"]["update"]
    provenance = capture_provenance(manifest)
    routed_action = package_manager_update_action(manifest, provenance) if configured_action["mode"] == "manual" else None
    update_action = routed_action or configured_action
    mode = update_action["mode"]
    release = probe_release(manifest)
    if mode == "manual":
        return passive_update(
            repo_root,
            manifest,
            update_action=update_action,
            mode=mode,
            execute=execute,
            release=release,
            provenance=provenance,
        )
    if executable_action_missing_commands(mode, update_action):
        return attach_release_metadata(
            {
                "tool_id": manifest["tool_id"],
                "status": "failed",
                "mode": mode,
                "commands": [],
            },
            provenance=provenance,
            release=release,
        )
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
    readiness_result = readiness_after_successful_checks(repo_root, manifest, detect_result, healthcheck_result)
    command_ok = all(result.exit_code == 0 for result in command_results)
    version_transition = {
        "from": previous_observed_version(repo_root, manifest["tool_id"]),
        "to": observed_version_from_detect(detect_result),
    }
    version_changed = _version_transition_changed(version_transition)
    if command_ok and detect_result["ok"] and healthcheck_result["ok"]:
        if readiness_result["ok"]:
            status = "refreshed" if version_changed is False else "updated"
        else:
            status = "refreshed-not-ready" if version_changed is False else "updated-not-ready"
    else:
        status = "failed"
    payload = update_payload(
        status=status,
        mode=mode,
        commands=[command_result_payload(result) for result in command_results],
        detect_result=detect_result,
        healthcheck_result=healthcheck_result,
        readiness_result=readiness_result,
        package_manager=update_action.get("package_manager"),
        package_name=update_action.get("package_name"),
        version_transition=version_transition,
    )
    persist_update_lock(repo_root, manifest, release=release, provenance=provenance, payload=payload)
    result = {
        "tool_id": manifest["tool_id"],
        "status": status,
        "mode": mode,
        "commands": payload["commands"],
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
        "package_manager": payload["package_manager"],
        "package_name": payload["package_name"],
        "version_transition": payload["version_transition"],
    }
    return attach_release_metadata(result, provenance=provenance, release=release)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    selected = select_by_tool_id(load_manifests(repo_root), args.tool_id)
    results = [update_one(repo_root, manifest, execute=args.execute) for manifest in selected]
    # Advisories stay on stderr (see print_update_advisories); stdout is the payload.
    print_update_advisories(results)
    # Unconditional YAML. The former human line was `tool_id: status [<from> -> <to>]
    # [healthcheck=<status>]`, all projected from `status`, `version_transition`, and
    # `healthcheck`, which every result already carries.
    emit_yaml(results)
    if has_any_status(results, status_key="status", statuses={"failed", "updated-not-ready", "refreshed-not-ready"}):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
