#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_manifests, now_iso, upsert_lock
from scripts.control_plane_lifecycle_lib import (
    attach_release_metadata,
    detect_and_healthcheck,
    run_command_payloads,
)
from scripts.install_provenance_lib import detect_install_provenance
from scripts.upstream_release_lib import probe_release


def render_repo_followup(repo_root: Path, install_action: dict[str, object]) -> dict[str, object] | None:
    repo_followup = install_action.get("repo_followup")
    if not isinstance(repo_followup, dict):
        return None
    command_template = repo_followup.get("command_template")
    if not isinstance(command_template, str) or not command_template:
        return None
    rendered_command = command_template.format(repo_root=str(repo_root))
    return {
        "summary": repo_followup.get("summary"),
        "command_template": command_template,
        "rendered_command": rendered_command,
        "docs_url": repo_followup.get("docs_url"),
        "when": repo_followup.get("when"),
        "optional": repo_followup.get("optional", False),
    }


def base_result(
    repo_root: Path,
    manifest: dict[str, object],
    install_action: dict[str, object],
    *,
    status: str,
    mode: str,
    commands: list[dict[str, object]] | list[str],
    detect: dict[str, object] | None = None,
    healthcheck: dict[str, object] | None = None,
) -> dict[str, object]:
    result = {
        "tool_id": manifest["tool_id"],
        "status": status,
        "mode": mode,
        "docs_url": install_action.get("docs_url"),
        "install_url": install_action.get("install_url"),
        "repo_followup": render_repo_followup(repo_root, install_action),
        "notes": install_action.get("notes", []),
        "commands": commands,
    }
    if detect is not None:
        result["detect"] = detect
    if healthcheck is not None:
        result["healthcheck"] = healthcheck
    return result


def capture_provenance(manifest: dict[str, object]) -> dict[str, object]:
    provenance = detect_install_provenance(manifest)
    provenance["checked_at"] = now_iso()
    return provenance


def persist_install_lock(
    repo_root: Path,
    manifest: dict[str, object],
    install_action: dict[str, object],
    *,
    status: str,
    mode: str,
    commands: list[dict[str, object]],
    detect: dict[str, object],
    healthcheck: dict[str, object],
    release: dict[str, object] | None,
    provenance: dict[str, object],
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


def finish_nonexecuting_install(
    repo_root: Path,
    manifest: dict[str, object],
    install_action: dict[str, object],
    *,
    mode: str,
    status: str,
    release: dict[str, object] | None,
    provenance: dict[str, object],
) -> dict[str, object]:
    detect_result, healthcheck_result = detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
    )
    if status == "manual":
        status = "already-installed" if detect_result["ok"] and healthcheck_result["ok"] else "manual"
    persistable = {
        "status": status,
        "mode": mode,
        "commands": [],
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "release": release,
        "provenance": provenance,
    }
    return {
        "status": status,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "persistable": persistable,
    }


def install_one(repo_root: Path, manifest: dict[str, object], *, execute: bool) -> dict[str, object]:
    install_action = manifest["lifecycle"]["install"]
    mode = install_action["mode"]
    commands = install_action.get("commands", [])
    release = probe_release(manifest)
    provenance = capture_provenance(manifest)

    if mode in {"none", "manual"}:
        outcome = finish_nonexecuting_install(
            repo_root,
            manifest,
            install_action,
            mode=mode,
            status="noop" if mode == "none" else "manual",
            release=release,
            provenance=provenance,
        )
        if execute:
            persist_install_lock(
                repo_root,
                manifest,
                install_action,
                **outcome["persistable"],
            )
        result = base_result(
            repo_root,
            manifest,
            install_action,
            status=outcome["status"],
            mode=mode,
            commands=[],
            detect=outcome["detect"],
            healthcheck=outcome["healthcheck"],
        )
        return attach_release_metadata(result, provenance=provenance, release=release)
    if not execute:
        result = base_result(repo_root, manifest, install_action, status="dry-run", mode=mode, commands=commands)
        return attach_release_metadata(result, provenance=provenance, release=release)

    command_results = run_command_payloads(commands, repo_root)
    detect_result, healthcheck_result = detect_and_healthcheck(
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
    results = [install_one(repo_root, manifest, execute=args.execute) for manifest in selected]
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
