#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.control_plane_lib import evaluate_version, read_lock, run_check
from scripts.control_plane_lifecycle_lib import (
    disabled_by_cautilus_adapter,
    disabled_check_payload,
    evaluate_readiness,
    render_repo_followup,
)
from scripts.repo_layout import discovery_stub_dir, generated_support_dir
from scripts.support_sync_lib import (
    inspect_support_sync,
    support_link_name,
    support_materialized_roots,
    support_state_for_manifest,
)


def install_route_for_manifest(repo_root: Path, capability: dict[str, Any]) -> dict[str, Any]:
    install = capability.get("lifecycle", {}).get("install", {})
    return {
        "mode": install.get("mode"),
        "commands": install.get("commands", []),
        "docs_url": install.get("docs_url"),
        "install_url": install.get("install_url"),
        "repo_followup": render_repo_followup(repo_root, install),
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
            f"Run `{suggested_command}` to materialize the upstream or wrapper support skill into the installed Charness plugin."
        )
    else:
        guidance = (
            "Previously materialized support skill paths are missing. "
            f"Run `{suggested_command}` to rematerialize the installed plugin support surface."
        )
    return {
        **support_sync,
        "action_required": True,
        "suggested_command": suggested_command,
        "guidance": guidance,
    }, [guidance]


def support_discovery_state(
    repo_root: Path,
    capability: dict[str, Any],
    support_state: str,
    previous_lock: dict[str, Any] | None = None,
    *,
    plugin_root: Path | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    local_support_path = capability.get("support_skill_path")
    if isinstance(local_support_path, str) and local_support_path and (repo_root / local_support_path).is_file():
        guidance = (
            f"Support skill is available at `{local_support_path}`. "
            "Use `find-skills` to surface it on demand or inspect that path directly."
        )
        return {
            "status": "native",
            "support_skill_path": local_support_path,
            "layer": "support skill",
            "intent_triggers": capability.get("intent_triggers", []),
            "guidance": guidance,
        }, [guidance]

    if support_state not in {"upstream-consumed", "wrapped-upstream"}:
        return None, []

    support = previous_lock.get("support") if previous_lock else None
    if isinstance(support, dict):
        if plugin_root is not None and support.get("materialized_kind") == "installed-plugin-copy":
            materialized_base = support.get("materialized_base")
            if not isinstance(materialized_base, str) or Path(materialized_base).resolve() != plugin_root.resolve():
                support = None

    if isinstance(support, dict):
        for materialized_root in support_materialized_roots(repo_root, support):
            materialized_path = materialized_root / "SKILL.md"
            if not materialized_path.is_file():
                continue
            rendered_path = str(materialized_path)
            materialized_kind = support.get("materialized_kind") or "materialized"
            guidance = (
                f"Support skill is available at `{rendered_path}`. "
                "Use the installed Charness plugin support surface for this upstream-consumed skill."
            )
            return {
                "status": "materialized",
                "support_skill_path": rendered_path,
                "layer": "installed support skill" if materialized_kind == "installed-plugin-copy" else "synced support skill",
                "intent_triggers": capability.get("intent_triggers", []),
                "materialized_base": support.get("materialized_base"),
                "materialized_kind": materialized_kind,
                "guidance": guidance,
            }, [guidance]

    materialized_path = generated_support_dir(repo_root) / support_link_name(capability) / "SKILL.md"
    if not materialized_path.is_file():
        return None, []

    rendered_path = str(materialized_path.relative_to(repo_root))
    discovery = {
        "status": "materialized",
        "support_skill_path": rendered_path,
        "layer": "synced support skill",
        "intent_triggers": capability.get("intent_triggers", []),
    }
    guidance_parts = [f"Support skill is available at `{rendered_path}`."]
    discovery_stub = discovery_stub_dir(repo_root) / f"{capability['tool_id']}.md"
    if discovery_stub.is_file():
        rendered_stub_path = str(discovery_stub.relative_to(repo_root))
        discovery["discovery_stub_path"] = rendered_stub_path
        guidance_parts.append(
            f"Repo-local discovery stub is available at `{rendered_stub_path}` for host-repo grep and cold-start pickup."
        )
    guidance_parts.append(
        "Use `find-skills` to surface it on demand or inspect that path directly."
    )
    if discovery.get("discovery_stub_path"):
        guidance_parts.append("You can also grep the discovery stub from the host repo.")
    guidance = " ".join(guidance_parts)
    discovery["guidance"] = guidance
    return discovery, [guidance]


def inspect_support_state(
    repo_root: Path,
    capability: dict[str, Any],
    *,
    plugin_root: Path | None,
) -> tuple[dict[str, Any] | None, str, dict[str, Any], dict[str, Any] | None, list[str]]:
    previous_lock = read_lock(repo_root, capability["tool_id"])
    support_state = support_state_for_manifest(capability)
    support_sync = inspect_support_sync(repo_root, previous_lock, plugin_root=plugin_root)
    support_sync, next_steps = support_sync_guidance(capability, support_state, support_sync)
    support_discovery, discovery_steps = support_discovery_state(
        repo_root,
        capability,
        support_state,
        previous_lock,
        plugin_root=plugin_root,
    )
    next_steps.extend(discovery_steps)
    return previous_lock, support_state, support_sync, support_discovery, next_steps


def inspect_capability_state(repo_root: Path, capability: dict[str, Any], *, plugin_root: Path | None = None) -> dict[str, Any]:
    disabled = disabled_by_cautilus_adapter(repo_root, capability)
    if disabled is not None:
        disabled_payload = disabled_check_payload(disabled)
        previous_lock, support_state, support_sync, support_discovery, next_steps = inspect_support_state(
            repo_root,
            capability,
            plugin_root=plugin_root,
        )
        next_steps.append(f"Cautilus is disabled by repo adapter: {disabled['reason']}")
        return {
            "kind": capability["kind"],
            "access_modes": capability["access_modes"],
            "capability_requirements": capability.get("capability_requirements", {}),
            "install_route": install_route_for_manifest(repo_root, capability),
            "support_state": support_state,
            "detect": disabled_payload,
            "healthcheck": disabled_payload,
            "readiness": {"ok": False, "checks": [], "failed_checks": []},
            "version": {
                "status": "unknown",
                "constraint": capability["version_expectation"]["constraint"],
                "observed_version": None,
            },
            "support_sync": support_sync,
            "support_discovery": support_discovery,
            "doctor_status": "disabled",
            "doctor_disposition": "disabled-by-adapter",
            "next_steps": next_steps,
            "previous_lock_present": previous_lock is not None,
        }

    detect_result = run_check(capability["checks"]["detect"], repo_root)
    healthcheck_result = run_check(capability["checks"]["healthcheck"], repo_root) if detect_result["ok"] else {
        "ok": False,
        "results": [],
        "failure_details": ["detect failed; healthcheck skipped"],
        "failure_hint": capability["checks"]["healthcheck"].get("failure_hint"),
    }
    readiness_result = evaluate_readiness(capability, repo_root)
    version_result = evaluate_version(capability, detect_result)
    previous_lock, support_state, support_sync, support_discovery, next_steps = inspect_support_state(
        repo_root,
        capability,
        plugin_root=plugin_root,
    )

    install_route = install_route_for_manifest(repo_root, capability)

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

    doctor_policy = capability.get("doctor_policy") or "required"

    if doctor_status == "ok":
        doctor_disposition = "ready"
    elif doctor_status == "missing" and (install_route.get("mode") == "manual" or doctor_policy == "advisory"):
        doctor_disposition = "advisory-install-needed"
    elif doctor_status == "support-missing":
        doctor_disposition = "blocking-support-sync-needed"
    elif doctor_status == "missing":
        doctor_disposition = "blocking-install-needed"
    else:
        doctor_disposition = "blocking-failure"

    return {
        "kind": capability["kind"],
        "access_modes": capability["access_modes"],
        "capability_requirements": capability.get("capability_requirements", {}),
        "install_route": install_route,
        "support_state": support_state,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
        "version": version_result,
        "support_sync": support_sync,
        "support_discovery": support_discovery,
        "doctor_status": doctor_status,
        "doctor_disposition": doctor_disposition,
        "next_steps": next_steps,
        "previous_lock_present": previous_lock is not None,
    }
