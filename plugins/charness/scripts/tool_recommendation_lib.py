#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

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
        "notes": install.get("notes", []),
    }


def verify_command(tool_id: str) -> str:
    return f"python3 scripts/doctor.py --repo-root . --json --tool-id {tool_id}"


def build_tool_recommendation(repo_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    state = inspect_capability_state(repo_root, manifest)
    return {
        "tool_id": manifest["tool_id"],
        "display_name": manifest["display_name"],
        "kind": manifest["kind"],
        "summary": manifest.get("summary", ""),
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
    }


def recommendations_for_public_skill(
    repo_root: Path,
    manifests: list[dict[str, Any]],
    *,
    skill_id: str,
) -> list[dict[str, Any]]:
    return [
        build_tool_recommendation(repo_root, manifest)
        for manifest in manifests
        if skill_id in manifest.get("supports_public_skills", [])
    ]
