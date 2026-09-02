#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.control_plane_lib import load_manifests_for_discovery, staged_tool_ids  # noqa: E402
from scripts.doctor_lib import inspect_capability_state  # noqa: E402


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
    return f"python3 scripts/doctor.py --repo-root . --tool-id {tool_id}"


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


def role_recommendation_payload(
    repo_root: Path, *, recommendation_role: str, next_skill_id: str, include_ready: bool
) -> dict[str, Any]:
    """The role-recommendation CLI payload shared by the per-skill
    list_tool_recommendations.py mains. The argparse surface (defaults/help) stays
    per-skill; only this invariant payload build is shared. Loads discovery manifests
    via the already-imported control plane, so callers do not re-wire the dependency."""
    return {
        "recommendation_role": recommendation_role,
        "next_skill_id": next_skill_id,
        "tool_recommendations": recommendations_for_role(
            repo_root,
            load_manifests_for_discovery(repo_root),
            recommendation_role=recommendation_role,
            next_skill_id=next_skill_id,
            only_blocking=not include_ready,
        ),
    }
