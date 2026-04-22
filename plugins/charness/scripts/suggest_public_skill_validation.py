#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_public_skill_validation_lib_module = import_repo_module(__file__, "scripts.public_skill_validation_lib")
POLICY_PATH = _scripts_public_skill_validation_lib_module.POLICY_PATH
VALID_ADAPTER_REQUIREMENTS = _scripts_public_skill_validation_lib_module.VALID_ADAPTER_REQUIREMENTS
VALID_FALLBACK_POLICIES = _scripts_public_skill_validation_lib_module.VALID_FALLBACK_POLICIES
VALID_TIERS = _scripts_public_skill_validation_lib_module.VALID_TIERS
load_policy = _scripts_public_skill_validation_lib_module.load_policy
partition_missing_skills = _scripts_public_skill_validation_lib_module.partition_missing_skills
public_skill_ids = _scripts_public_skill_validation_lib_module.public_skill_ids


def build_report(repo_root: Path) -> dict[str, object]:
    policy = load_policy(repo_root)
    all_skills = public_skill_ids(repo_root)
    tiers = policy.get("tiers") if isinstance(policy.get("tiers"), dict) else {}
    adapter_requirements = (
        policy.get("adapter_requirements")
        if isinstance(policy.get("adapter_requirements"), dict)
        else {}
    )
    fallback_policy = (
        policy.get("fallback_policy")
        if isinstance(policy.get("fallback_policy"), dict)
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
    missing_fallback_policy = partition_missing_skills(
        {
            category: list(fallback_policy.get(category, []))
            for category in VALID_FALLBACK_POLICIES
        },
        all_skills=all_skills,
    )
    missing_skills = sorted(
        set(missing_tiers) | set(missing_adapter_requirements) | set(missing_fallback_policy)
    )
    suggestions = []
    for skill_id in missing_skills:
        suggestions.append(
            {
                "skill_id": skill_id,
                "missing_fields": {
                    "tiers": skill_id in missing_tiers,
                    "adapter_requirements": skill_id in missing_adapter_requirements,
                    "fallback_policy": skill_id in missing_fallback_policy,
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
                    "fallback_policy": [
                        f"fallback_policy.{category}"
                        for category in VALID_FALLBACK_POLICIES
                    ]
                    if skill_id in missing_fallback_policy
                    else [],
                },
            }
        )
    return {
        "policy_path": str(POLICY_PATH),
        "all_public_skills": all_skills,
        "missing_tiers": missing_tiers,
        "missing_adapter_requirements": missing_adapter_requirements,
        "missing_fallback_policy": missing_fallback_policy,
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
        if item["choose_one_of"]["fallback_policy"]:
            lines.append(
                "  fallback policy: choose one of "
                + ", ".join(
                    f"`{value}`" for value in item["choose_one_of"]["fallback_policy"]
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
