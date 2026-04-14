#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.control_plane_lib import evaluate_version, read_lock, run_check
from scripts.support_sync_lib import inspect_support_sync, support_state_for_manifest


def install_route_for_manifest(capability: dict[str, Any]) -> dict[str, Any]:
    install = capability.get("lifecycle", {}).get("install", {})
    return {
        "mode": install.get("mode"),
        "commands": install.get("commands", []),
        "docs_url": install.get("docs_url"),
        "install_url": install.get("install_url"),
        "notes": install.get("notes", []),
    }


def support_sync_guidance(capability: dict[str, Any], support_state: str, support_sync: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    status = support_sync["status"]
    if support_state not in {"upstream-consumed", "wrapped-upstream"} or status not in {"not-tracked", "missing"}:
        return support_sync, []

    suggested_command = f"charness tool sync-support {capability['tool_id']}"
    if status == "not-tracked":
        guidance = (
            "Local support skill surface is not materialized yet. "
            f"Run `{suggested_command}` if you want the upstream or wrapper support skill available in this repo."
        )
    else:
        guidance = (
            "Previously materialized support skill paths are missing. "
            f"Run `{suggested_command}` to rematerialize the local support surface."
        )
    return {
        **support_sync,
        "action_required": True,
        "suggested_command": suggested_command,
        "guidance": guidance,
    }, [guidance]


def evaluate_readiness(capability: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for check in capability.get("readiness_checks", []):
        result = run_check(check, repo_root)
        checks.append({"check_id": check["check_id"], "summary": check["summary"], **result})
    return {
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["ok"]],
    }


def inspect_capability_state(repo_root: Path, capability: dict[str, Any]) -> dict[str, Any]:
    detect_result = run_check(capability["checks"]["detect"], repo_root)
    healthcheck_result = run_check(capability["checks"]["healthcheck"], repo_root) if detect_result["ok"] else {
        "ok": False,
        "results": [],
        "failure_details": ["detect failed; healthcheck skipped"],
        "failure_hint": capability["checks"]["healthcheck"].get("failure_hint"),
    }
    readiness_result = evaluate_readiness(capability, repo_root)
    version_result = evaluate_version(capability, detect_result)
    previous_lock = read_lock(repo_root, capability["tool_id"])
    support_state = support_state_for_manifest(capability)
    support_sync = inspect_support_sync(repo_root, previous_lock)
    support_sync, next_steps = support_sync_guidance(capability, support_state, support_sync)

    if support_sync["status"] == "missing":
        doctor_status = "support-missing"
    elif not detect_result["ok"]:
        doctor_status = "missing"
    elif not healthcheck_result["ok"]:
        doctor_status = "unhealthy"
    elif not readiness_result["ok"]:
        doctor_status = "not-ready"
    elif version_result["status"] not in {"advisory", "matched", "unknown"}:
        doctor_status = "version-mismatch"
    else:
        doctor_status = "ok"

    return {
        "kind": capability["kind"],
        "access_modes": capability["access_modes"],
        "capability_requirements": capability.get("capability_requirements", {}),
        "install_route": install_route_for_manifest(capability),
        "support_state": support_state,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
        "version": version_result,
        "support_sync": support_sync,
        "doctor_status": doctor_status,
        "next_steps": next_steps,
        "previous_lock_present": previous_lock is not None,
    }
