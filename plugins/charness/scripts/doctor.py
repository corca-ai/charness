#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.control_plane_lib")
load_capabilities = _scripts_control_plane_lib_module.load_capabilities
now_iso = _scripts_control_plane_lib_module.now_iso
upsert_lock = _scripts_control_plane_lib_module.upsert_lock
_scripts_doctor_lib_module = import_repo_module(__file__, "scripts.doctor_lib")
inspect_capability_state = _scripts_doctor_lib_module.inspect_capability_state
_scripts_install_provenance_lib_module = import_repo_module(__file__, "scripts.install_provenance_lib")
detect_install_provenance = _scripts_install_provenance_lib_module.detect_install_provenance
_scripts_upstream_release_lib_module = import_repo_module(__file__, "scripts.upstream_release_lib")
probe_release = _scripts_upstream_release_lib_module.probe_release


def lock_safe_doctor_payload(payload: dict[str, object]) -> dict[str, object]:
    lock_payload = dict(payload)
    lock_payload.pop("install_route", None)
    lock_payload.pop("support_discovery", None)
    lock_payload.pop("previous_lock_present", None)
    lock_payload.pop("release", None)
    lock_payload.pop("provenance", None)
    lock_payload.pop("next_steps", None)
    support_sync = lock_payload.get("support_sync")
    if isinstance(support_sync, dict):
        lock_payload["support_sync"] = {
            "status": support_sync["status"],
            "expected_paths": support_sync["expected_paths"],
            "missing_paths": support_sync["missing_paths"],
        }
    return lock_payload


def inspect_manifest(
    repo_root: Path,
    manifest: dict[str, object],
    *,
    write: bool,
    skip_release_probe: bool,
) -> dict[str, object]:
    state = inspect_capability_state(repo_root, manifest)
    provenance_result = detect_install_provenance(manifest)
    provenance_result["checked_at"] = now_iso()
    payload = {
        "checked_at": now_iso(),
        **state,
        "provenance": provenance_result,
    }
    release = None if skip_release_probe else probe_release(manifest)
    if release is not None:
        payload["release"] = release
    if write:
        upsert_lock(
            repo_root,
            manifest,
            doctor=lock_safe_doctor_payload(payload),
            release=release,
            provenance=provenance_result,
        )
    return {**payload, "tool_id": manifest["tool_id"], "previous_lock_present": state["previous_lock_present"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--write-locks", action="store_true")
    parser.add_argument(
        "--skip-release-probe",
        action="store_true",
        help="Skip upstream release lookups while preserving local readiness and support checks.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    capabilities = load_capabilities(repo_root)
    selected = [capability for capability in capabilities if not args.tool_id or capability["tool_id"] in args.tool_id]
    results = [
        inspect_manifest(
            repo_root,
            capability,
            write=args.write_locks,
            skip_release_probe=args.skip_release_probe,
        )
        for capability in selected
    ]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['tool_id']}: {result['doctor_status']} ({result['support_state']})")

    if any(result["doctor_status"] in {"missing", "unhealthy", "not-ready", "version-mismatch", "support-missing"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
