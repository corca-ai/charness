#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.public_skill_validation_lib import (
    POLICY_PATH,
    VALID_ADAPTER_REQUIREMENTS,
    VALID_TIERS,
    load_policy,
    partition_missing_skills,
    public_skill_ids,
)


def build_report(repo_root: Path) -> dict[str, object]:
    policy = load_policy(repo_root)
    all_skills = public_skill_ids(repo_root)
    tiers = policy.get("tiers") if isinstance(policy.get("tiers"), dict) else {}
    adapter_requirements = (
        policy.get("adapter_requirements")
        if isinstance(policy.get("adapter_requirements"), dict)
        else {}
    )
    missing_tiers = partition_missing_skills(
        {category: list(tiers.get(category, [])) for category in VALID_TIERS},
        all_skills=all_skills,
    )
    missing_adapter_requirements = partition_missing_skills(
        {
            category: list(adapter_requirements.get(category, []))
            for category in VALID_ADAPTER_REQUIREMENTS
        },
        all_skills=all_skills,
    )
    missing_skills = sorted(set(missing_tiers) | set(missing_adapter_requirements))
    suggestions = []
    for skill_id in missing_skills:
        suggestions.append(
            {
                "skill_id": skill_id,
                "missing_fields": {
                    "tiers": skill_id in missing_tiers,
                    "adapter_requirements": skill_id in missing_adapter_requirements,
                },
                "choose_one_of": {
                    "tiers": [f"tiers.{category}" for category in VALID_TIERS]
                    if skill_id in missing_tiers
                    else [],
                    "adapter_requirements": [
                        f"adapter_requirements.{category}"
                        for category in VALID_ADAPTER_REQUIREMENTS
                    ]
                    if skill_id in missing_adapter_requirements
                    else [],
                },
            }
        )
    return {
        "policy_path": str(POLICY_PATH),
        "all_public_skills": all_skills,
        "missing_tiers": missing_tiers,
        "missing_adapter_requirements": missing_adapter_requirements,
        "suggestions": suggestions,
    }


def _format_human(report: dict[str, object]) -> str:
    suggestions = report["suggestions"]
    if not suggestions:
        return f"No public skill policy gaps found in `{report['policy_path']}`."
    lines = [f"Public skill policy gaps in `{report['policy_path']}`:"]
    for item in suggestions:
        lines.append(f"- `{item['skill_id']}`")
        if item["choose_one_of"]["tiers"]:
            lines.append(
                "  tiers: choose one of "
                + ", ".join(f"`{value}`" for value in item["choose_one_of"]["tiers"])
            )
        if item["choose_one_of"]["adapter_requirements"]:
            lines.append(
                "  adapter requirements: choose one of "
                + ", ".join(
                    f"`{value}`"
                    for value in item["choose_one_of"]["adapter_requirements"]
                )
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report))
    return 1 if report["suggestions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
