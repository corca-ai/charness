#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

VALID_TIERS = ("smoke-only", "hitl-recommended", "evaluator-required")
VALID_ADAPTER_REQUIREMENTS = ("required", "adapter-free")
POLICY_PATH = Path("docs/public-skill-validation.json")


class ValidationError(Exception):
    pass


def public_skill_ids(repo_root: Path) -> list[str]:
    skills_root = repo_root / "skills" / "public"
    if not skills_root.exists():
        return []
    return sorted(path.name for path in skills_root.iterdir() if path.is_dir() and path.name != "generated")


def load_policy(repo_root: Path) -> dict[str, object]:
    path = repo_root / POLICY_PATH
    if not path.is_file():
        raise ValidationError(f"missing `{POLICY_PATH}`")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{POLICY_PATH}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{POLICY_PATH}: top-level JSON value must be an object")
    return data


def _normalized_skill_list(value: object, *, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{field} must be a list of skill ids")
    return sorted(value)


def _render_expected_locations(field: str, categories: tuple[str, ...]) -> str:
    rendered = ", ".join(f"`{field}.{category}`" for category in categories)
    return f"Add each missing skill to exactly one of {rendered} in `{POLICY_PATH}`"


def partition_missing_skills(
    assignments: dict[str, list[str]],
    *,
    all_skills: list[str],
) -> list[str]:
    seen: set[str] = set()
    for skill_ids in assignments.values():
        seen.update(skill_ids)
    return sorted(set(all_skills) - seen)


def _validate_partition(
    assignments: dict[str, list[str]],
    *,
    expected_categories: tuple[str, ...],
    all_skills: list[str],
    field: str,
) -> None:
    if set(assignments) != set(expected_categories):
        raise ValidationError(
            f"{field} must define exactly these categories: {', '.join(expected_categories)}"
        )

    seen: dict[str, str] = {}
    for category in expected_categories:
        for skill_id in assignments[category]:
            if skill_id not in all_skills:
                raise ValidationError(f"{field}.{category} references unknown public skill `{skill_id}`")
            previous = seen.get(skill_id)
            if previous is not None:
                raise ValidationError(
                    f"public skill `{skill_id}` appears in both `{field}.{previous}` and `{field}.{category}`"
                )
            seen[skill_id] = category

    missing = partition_missing_skills(assignments, all_skills=all_skills)
    if missing:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in missing)
        guidance = _render_expected_locations(field, expected_categories)
        raise ValidationError(
            f"{field} does not classify every public skill; missing {rendered}. {guidance}."
        )


def validate_policy(data: dict[str, object], repo_root: Path) -> dict[str, dict[str, list[str]]]:
    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise ValidationError(f"{POLICY_PATH}: schema_version must be 1")

    raw_tiers = data.get("tiers")
    if not isinstance(raw_tiers, dict):
        raise ValidationError(f"{POLICY_PATH}: `tiers` must be an object")
    tiers = {
        tier: _normalized_skill_list(raw_tiers.get(tier), field=f"tiers.{tier}")
        for tier in VALID_TIERS
    }

    raw_requirements = data.get("adapter_requirements")
    if not isinstance(raw_requirements, dict):
        raise ValidationError(f"{POLICY_PATH}: `adapter_requirements` must be an object")
    adapter_requirements = {
        requirement: _normalized_skill_list(
            raw_requirements.get(requirement),
            field=f"adapter_requirements.{requirement}",
        )
        for requirement in VALID_ADAPTER_REQUIREMENTS
    }

    all_skills = public_skill_ids(repo_root)
    _validate_partition(tiers, expected_categories=VALID_TIERS, all_skills=all_skills, field="tiers")
    _validate_partition(
        adapter_requirements,
        expected_categories=VALID_ADAPTER_REQUIREMENTS,
        all_skills=all_skills,
        field="adapter_requirements",
    )
    return {"tiers": tiers, "adapter_requirements": adapter_requirements}
