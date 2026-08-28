#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from scripts.public_skill_validation_lib import (
    POLICY_PATH,
    load_policy,
    validate_policy,
)

DOGFOOD_PATH = Path("docs/public-skill-dogfood.json")


def policy_applicability_report(repo_root: Path) -> dict[str, object] | None:
    """Return a typed consumer-boundary stop when this policy is not owned here."""
    if (repo_root / POLICY_PATH).exists():
        return None
    return {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "applicability": "not-applicable-missing-public-skill-validation-policy",
        "policy_path": str(POLICY_PATH),
        "matrix": [],
        "notes": [
            f"missing `{POLICY_PATH}`; public-skill dogfood policy is owned by the producing repository",
        ],
    }


def build_matrix(repo_root: Path, skill_ids: list[str]) -> dict[str, object]:
    if report := policy_applicability_report(repo_root):
        return report
    validate_policy(load_policy(repo_root), repo_root)
    registry_path = repo_root / DOGFOOD_PATH
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    canonical_cases = {
        case["skill_id"]: case
        for case in registry.get("cases", [])
        if isinstance(case, dict) and isinstance(case.get("skill_id"), str)
    }
    matrix = [canonical_cases[skill_id] for skill_id in skill_ids if skill_id in canonical_cases]
    return {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "applicability": "applicable",
        "matrix": matrix,
    }


def format_human(report: dict[str, object]) -> str:
    if report.get("applicability") != "applicable":
        notes = report.get("notes", [])
        detail = notes[0] if isinstance(notes, list) and notes else "no public-skill dogfood policy is available"
        return f"Public skill consumer dogfood: {report.get('applicability')} — {detail}"
    lines = ["Public skill consumer dogfood matrix:"]
    for row in report["matrix"]:
        assert isinstance(row, dict)
        lines.append(f"- `{row['skill_id']}`: prompt={row['prompt']}")
        for evidence in row["acceptance_evidence"]:
            lines.append(f"  acceptance={evidence}")
    return "\n".join(lines)
