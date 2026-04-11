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
from scripts.upstream_release_lib import probe_release


def failed_healthcheck(manifest: dict[str, object], *, reason: str) -> dict[str, object]:
    return {
        "ok": False,
        "results": [],
        "failure_details": [reason],
        "failure_hint": manifest["checks"]["healthcheck"].get("failure_hint"),
    }


def detect_and_healthcheck(repo_root: Path, manifest: dict[str, object], *, failure_reason: str) -> tuple[dict[str, object], dict[str, object]]:
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck_result = (
        run_check(manifest["checks"]["healthcheck"], repo_root)
        if detect_result["ok"]
        else failed_healthcheck(manifest, reason=failure_reason)
    )
    return detect_result, healthcheck_result


def base_result(
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
        "notes": install_action.get("notes", []),
        "commands": commands,
    }
    if detect is not None:
        result["detect"] = detect
    if healthcheck is not None:
        result["healthcheck"] = healthcheck
    return result


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
) -> None:
    upsert_lock(
        repo_root,
        manifest,
        release=release,
        install={
            "installed_at": now_iso(),
            "install_status": status,
            "mode": mode,
            "commands": commands,
            "detect": detect,
            "healthcheck": healthcheck,
            "docs_url": install_action.get("docs_url"),
            "notes": install_action.get("notes", []),
        },
    )


def execute_install_commands(repo_root: Path, commands: list[str]) -> list[dict[str, object]]:
    return [
        {
            "command": result.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
        for result in [run_shell(command, repo_root) for command in commands]
    ]


def install_one(repo_root: Path, manifest: dict[str, object], *, execute: bool) -> dict[str, object]:
    install_action = manifest["lifecycle"]["install"]
    mode = install_action["mode"]
    commands = install_action.get("commands", [])
    release = probe_release(manifest)

    if mode == "none":
        detect_result, healthcheck_result = detect_and_healthcheck(
            repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
        )
        if execute:
            persist_install_lock(
                repo_root,
                manifest,
                install_action,
                status="noop",
                mode=mode,
                commands=[],
                detect=detect_result,
                healthcheck=healthcheck_result,
                release=release,
            )
        result = base_result(
            manifest,
            install_action,
            status="noop",
            mode=mode,
            commands=[],
            detect=detect_result,
            healthcheck=healthcheck_result,
        )
        if release is not None:
            result["release"] = release
        return result

    if mode == "manual":
        detect_result, healthcheck_result = detect_and_healthcheck(
            repo_root, manifest, failure_reason="detect failed; healthcheck skipped"
        )
        status = "already-installed" if detect_result["ok"] and healthcheck_result["ok"] else "manual"
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
            )
        result = base_result(
            manifest,
            install_action,
            status=status,
            mode=mode,
            commands=[],
            detect=detect_result,
            healthcheck=healthcheck_result,
        )
        if release is not None:
            result["release"] = release
        return result

    if not execute:
        result = base_result(manifest, install_action, status="dry-run", mode=mode, commands=commands)
        if release is not None:
            result["release"] = release
        return result

    command_results = execute_install_commands(repo_root, commands)
    detect_result, healthcheck_result = detect_and_healthcheck(
        repo_root, manifest, failure_reason="detect failed after install"
    )
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
    )
    result = base_result(
        manifest,
        install_action,
        status=status,
        mode=mode,
        commands=command_results,
        detect=detect_result,
        healthcheck=healthcheck_result,
    )
    if release is not None:
        result["release"] = release
    return result


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
