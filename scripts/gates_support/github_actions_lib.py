from __future__ import annotations

import re
from pathlib import Path
from typing import Any

WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<action>[^@\s#]+)@(?P<ref>[^\s#]+)")
MAJOR_RE = re.compile(r"^v(?P<major>\d+)(?:$|[.-].*)")

ACTION_BASELINES: dict[str, dict[str, Any]] = {
    "actions/checkout": {
        "current_major": 6,
        "node24_major": 5,
        "source_url": "https://raw.githubusercontent.com/actions/checkout/main/README.md",
        "note": "v5 moved to Node 24; the current README examples use v6.",
    },
    "actions/setup-node": {
        "current_major": 6,
        "node24_major": 5,
        "source_url": "https://raw.githubusercontent.com/actions/setup-node/main/README.md",
        "note": "v5 moved to Node 24; the current README examples use v6.",
    },
    "actions/setup-go": {
        "current_major": 6,
        "node24_major": 6,
        "source_url": "https://raw.githubusercontent.com/actions/setup-go/main/README.md",
        "note": "v6 moved to Node 24 and is the current documented major.",
    },
    "actions/setup-python": {
        "current_major": 6,
        "node24_major": 6,
        "source_url": "https://raw.githubusercontent.com/actions/setup-python/main/README.md",
        "note": "v6 moved to Node 24 and is the current documented major.",
    },
    "actions/cache": {
        "current_major": 5,
        "node24_major": 5,
        "source_url": "https://raw.githubusercontent.com/actions/cache/main/README.md",
        "note": "v5 moved to Node 24 and is the current documented major.",
    },
    "actions/github-script": {
        "current_major": 8,
        "node24_major": 8,
        "source_url": "https://raw.githubusercontent.com/actions/github-script/main/README.md",
        "note": "v8 moved to Node 24 and is the current documented major.",
    },
}


def _workflow_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in WORKFLOW_GLOBS:
        files.extend(repo_root.glob(pattern))
    return sorted({path.resolve() for path in files})


def _normalize_action_id(raw_action: str) -> str | None:
    if raw_action.startswith("./") or raw_action.startswith("docker://"):
        return None
    parts = raw_action.split("/")
    if len(parts) < 2:
        return None
    return "/".join(parts[:2])


def _parse_major(reference: str) -> int | None:
    match = MAJOR_RE.match(reference)
    if match is None:
        return None
    return int(match.group("major"))


def _collect_findings_for_file(workflow_path: Path, repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    skipped_refs: list[dict[str, Any]] = []
    for line_number, line in enumerate(workflow_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        match = USES_RE.match(line)
        if match is None:
            continue
        raw_action = match.group("action")
        normalized = _normalize_action_id(raw_action)
        if normalized is None or normalized not in ACTION_BASELINES:
            continue
        reference = match.group("ref")
        major = _parse_major(reference)
        baseline = ACTION_BASELINES[normalized]
        if major is None:
            skipped_refs.append(
                {
                    "path": str(workflow_path.relative_to(repo_root)),
                    "line": line_number,
                    "action": raw_action,
                    "reference": reference,
                    "reason": "reference is not a simple `vN` major pin",
                }
            )
            continue
        if major >= baseline["current_major"]:
            continue
        category = "node24_incompatible" if major < baseline["node24_major"] else "baseline_lag"
        findings.append(
            {
                "path": str(workflow_path.relative_to(repo_root)),
                "line": line_number,
                "action": raw_action,
                "normalized_action": normalized,
                "reference": reference,
                "current_major": baseline["current_major"],
                "node24_major": baseline["node24_major"],
                "recommended_reference": f"v{baseline['current_major']}",
                "category": category,
                "source_url": baseline["source_url"],
                "note": baseline["note"],
            }
        )
    return findings, skipped_refs


def collect_github_actions_drift(repo_root: Path) -> dict[str, Any]:
    workflow_files = _workflow_files(repo_root)
    findings: list[dict[str, Any]] = []
    skipped_refs: list[dict[str, Any]] = []
    for workflow_path in workflow_files:
        file_findings, file_skipped = _collect_findings_for_file(workflow_path, repo_root)
        findings.extend(file_findings)
        skipped_refs.extend(file_skipped)
    return {
        "workflow_files": [str(path.relative_to(repo_root)) for path in workflow_files],
        "checked_actions": sorted(ACTION_BASELINES),
        "findings": findings,
        "skipped_refs": skipped_refs,
        "guidance": {
            "preferred_fix": "Upgrade workflow pins directly to the current documented action major.",
            "temporary_env_vars": [
                {
                    "name": "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24",
                    "use": "short-lived runner-readiness validation before or during the upgrade rollout",
                },
                {
                    "name": "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION",
                    "use": "temporary emergency fallback only while removing old action majors",
                },
            ],
            "runner_floor": "Node 24 JavaScript actions generally require Actions Runner v2.327.1 or later.",
        },
    }


def render_github_actions_report(payload: dict[str, Any]) -> str:
    workflow_files = payload["workflow_files"]
    findings = payload["findings"]
    if not workflow_files:
        return "No GitHub Actions workflows detected."
    if not findings:
        return f"Validated GitHub Actions majors in {len(workflow_files)} workflow file(s)."

    lines = ["GitHub Actions major drift detected:"]
    for finding in findings:
        reason = (
            "below the Node 24-ready floor"
            if finding["category"] == "node24_incompatible"
            else "behind the current documented major"
        )
        lines.append(
            "- "
            f"{finding['path']}:{finding['line']} uses `{finding['action']}@{finding['reference']}`; "
            f"use `@{finding['recommended_reference']}` instead ({reason}; Node 24 floor is `v{finding['node24_major']}`)."
        )
    lines.extend(
        [
            "",
            "Guidance:",
            "- Prefer direct major upgrades in the workflow file.",
            "- Use `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` only as a short-lived rollout check.",
            "- Use `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` only as a temporary escape hatch while removing old majors.",
        ]
    )
    return "\n".join(lines)
