#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.control_plane_lib import staged_tool_ids
from scripts.doctor_lib import inspect_capability_state


def recommendation_status_for_doctor_status(doctor_status: str) -> str:
    if doctor_status == "ok":
        return "ready"
    if doctor_status == "missing":
        return "install-needed"
    if doctor_status == "not-ready":
        return "setup-needed"
    return "repair-needed"


def install_route(manifest: dict[str, Any]) -> dict[str, Any]:
    install = manifest["lifecycle"]["install"]
    return {
        "mode": install["mode"],
        "commands": install.get("commands", []),
        "docs_url": install.get("docs_url"),
        "install_url": install.get("install_url"),
        "notes": install.get("notes", []),
    }


def verify_command(tool_id: str) -> str:
    return f"python3 scripts/doctor.py --repo-root . --json --tool-id {tool_id}"


def why_recommended(manifest: dict[str, Any], *, next_skill_id: str) -> str:
    role = manifest.get("recommendation_role")
    if role == "validation":
        return (
            f"Recommended because `{next_skill_id}` can use this tool for stronger validation when "
            "repo-native deterministic proof is not enough."
        )
    if role == "runtime":
        return f"Recommended because `{next_skill_id}` can use this tool as a supported runtime path."
    return f"Recommended because `{next_skill_id}` declares this tool as a supported external route."


def _staged_value(repo_root: Path, tool_id: str, *, staged_ids: set[str] | None) -> bool | None:
    if staged_ids is None:
        return None
    return tool_id in staged_ids


def build_tool_recommendation(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    next_skill_id: str,
    staged_ids: set[str] | None = None,
) -> dict[str, Any]:
    state = inspect_capability_state(repo_root, manifest)
    return {
        "tool_id": manifest["tool_id"],
        "display_name": manifest["display_name"],
        "kind": manifest["kind"],
        "summary": manifest.get("summary", ""),
        "why_recommended": why_recommended(manifest, next_skill_id=next_skill_id),
        "supports_public_skills": manifest.get("supports_public_skills", []),
        "recommendation_role": manifest.get("recommendation_role"),
        "recommendation_status": recommendation_status_for_doctor_status(state["doctor_status"]),
        "doctor_status": state["doctor_status"],
        "support_state": state["support_state"],
        "support_sync_status": state["support_sync"]["status"],
        "detect_ok": state["detect"]["ok"],
        "healthcheck_ok": state["healthcheck"]["ok"],
        "readiness_ok": state["readiness"]["ok"],
        "install": install_route(manifest),
        "verify_command": verify_command(manifest["tool_id"]),
        "next_skill_id": next_skill_id,
        "manifest_origin": manifest.get("_manifest_origin", "user-repo"),
        "staged": _staged_value(repo_root, manifest["tool_id"], staged_ids=staged_ids),
    }


def recommendations_for_public_skill(
    repo_root: Path,
    manifests: list[dict[str, Any]],
    *,
    skill_id: str,
) -> list[dict[str, Any]]:
    staged_ids = staged_tool_ids(repo_root)
    return [
        build_tool_recommendation(repo_root, manifest, next_skill_id=skill_id, staged_ids=staged_ids)
        for manifest in manifests
        if skill_id in manifest.get("supports_public_skills", [])
    ]


def recommendations_for_role(
    repo_root: Path,
    manifests: list[dict[str, Any]],
    *,
    recommendation_role: str,
    next_skill_id: str,
    only_blocking: bool = False,
) -> list[dict[str, Any]]:
    staged_ids = staged_tool_ids(repo_root)
    recommendations = [
        build_tool_recommendation(repo_root, manifest, next_skill_id=next_skill_id, staged_ids=staged_ids)
        for manifest in manifests
        if manifest.get("recommendation_role") == recommendation_role
        and next_skill_id in manifest.get("supports_public_skills", [])
    ]
    if not only_blocking:
        return recommendations
    return [item for item in recommendations if item["recommendation_status"] != "ready"]


def _task_text_matches(task_text: str, candidate: str) -> bool:
    normalized = candidate.casefold().strip()
    return bool(normalized) and normalized in task_text.casefold()


def _manifest_task_triggers(manifest: dict[str, Any]) -> list[str]:
    raw = [
        manifest.get("tool_id"),
        manifest.get("display_name"),
        *manifest.get("intent_triggers", []),
    ]
    seen: set[str] = set()
    triggers: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            continue
        normalized = item.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        triggers.append(item)
    return triggers


def _task_next_skill_id(manifest: dict[str, Any], next_skill_id: str | None) -> str:
    if next_skill_id:
        return next_skill_id
    supports = manifest.get("supports_public_skills", [])
    if isinstance(supports, list):
        for skill_id in supports:
            if isinstance(skill_id, str) and skill_id:
                return skill_id
    return "quality"


def _manifest_supports_skill(manifest: dict[str, Any], skill_id: str) -> bool:
    supports = manifest.get("supports_public_skills", [])
    return isinstance(supports, list) and skill_id in supports


def recommendations_for_task(
    repo_root: Path,
    manifests: list[dict[str, Any]],
    *,
    task_text: str,
    next_skill_id: str | None = None,
    only_blocking: bool = False,
) -> list[dict[str, Any]]:
    staged_ids = staged_tool_ids(repo_root)
    recommendations: list[dict[str, Any]] = []
    for manifest in manifests:
        if next_skill_id and not _manifest_supports_skill(manifest, next_skill_id):
            continue
        triggers = _manifest_task_triggers(manifest)
        matched = [trigger for trigger in triggers if _task_text_matches(task_text, trigger)]
        if not matched:
            continue
        item = build_tool_recommendation(
            repo_root,
            manifest,
            next_skill_id=_task_next_skill_id(manifest, next_skill_id),
            staged_ids=staged_ids,
        )
        item["matched_triggers"] = matched
        recommendations.append(item)
    if not only_blocking:
        return recommendations
    return [item for item in recommendations if item["recommendation_status"] != "ready"]
