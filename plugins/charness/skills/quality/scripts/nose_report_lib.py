#!/usr/bin/env python3
"""Run nose and parse/summarize its versioned JSON report.

Split out of `inventory_nose_clones.py` (cohesion + length cap): turning a nose
invocation into a normalized `{status, families, scope, ranking, ...}` payload —
including the cross-version (0.4 array vs 0.5+ object) schema handling and the
per-family summary shape — is its own concern, separate from command building,
the advisory-interpretation contract, and rendering.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

NOSE_TIMEOUT_SECONDS = 180


def family_summary(family: dict[str, Any]) -> dict[str, Any]:
    locations = family.get("locations", [])
    files = []
    if isinstance(locations, list):
        for location in locations[:6]:
            if not isinstance(location, dict):
                continue
            file = location.get("file")
            if not isinstance(file, str):
                continue
            start = location.get("start_line")
            end = location.get("end_line")
            files.append(
                {
                    "file": file,
                    "start_line": start,
                    "end_line": end,
                    "name": location.get("name"),
                    "kind": location.get("kind"),
                }
            )
    return {
        "value": family.get("value"),
        "members": family.get("members"),
        "files": family.get("files"),
        "modules": family.get("modules"),
        "languages": family.get("languages"),
        "mean_score": family.get("mean_score"),
        "dup_lines": family.get("dup_lines"),
        "shared_lines": family.get("shared_lines"),
        "params": family.get("params"),
        "sample_locations": files,
    }


def run_nose(repo_root: Path, command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=NOSE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": str(exc.stdout or ""),
            "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s",
            "families": [],
            "tool_version": "",
        }
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": f"nose emitted invalid JSON: {exc}; stderr: {completed.stderr.strip()}",
            "families": [],
            "tool_version": "",
        }
    families, tool_version, scope, ranking = extract_report(parsed)
    status = "findings" if families else "clean"
    if completed.returncode != 0:
        status = "error"
    return {
        "status": status,
        "exit_code": completed.returncode,
        "stdout": "",
        "stderr": completed.stderr.strip(),
        "families": families,
        "tool_version": tool_version,
        "scope": scope,
        "ranking": ranking,
    }


def extract_report(parsed: Any) -> tuple[list[dict[str, Any]], str, dict[str, Any], dict[str, Any]]:
    """Return report fields across nose 0.4 and 0.5+ JSON shapes.

    nose 0.5 emits a top-level object ({"families": [...], "tool_version": ...});
    nose 0.4 emitted a bare top-level array. Reading the 0.5 object as a list
    silently yielded zero families, under-reporting the live scan.
    """
    if isinstance(parsed, dict):
        families = parsed.get("families")
        tool_version = str(parsed.get("tool_version") or "")
        scope = parsed.get("scope")
        ranking = parsed.get("ranking")
    elif isinstance(parsed, list):
        families = parsed
        tool_version = ""
        scope = {}
        ranking = {}
    else:
        families = []
        tool_version = ""
        scope = {}
        ranking = {}
    if not isinstance(families, list):
        families = []
    if not isinstance(scope, dict):
        scope = {}
    if not isinstance(ranking, dict):
        ranking = {}
    return [family for family in families if isinstance(family, dict)], tool_version, scope, ranking
