#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from scripts.gates_support.public_skill_dogfood_lib import (
    DOGFOOD_PATH,
)
from scripts.gates_support.public_skill_validation_lib import public_skill_ids


class ValidationError(Exception):
    pass


def load_registry(repo_root: Path) -> dict[str, object]:
    path = repo_root / DOGFOOD_PATH
    if not path.is_file():
        raise ValidationError(f"missing `{DOGFOOD_PATH}`")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{DOGFOOD_PATH}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{DOGFOOD_PATH}: top-level JSON value must be an object")
    return data


def _require_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: object, *, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        raise ValidationError(f"{field} must be a non-empty list of strings")
    return value


def _validate_case(
    raw_case: object,
    *,
    index: int,
    all_skills: set[str],
    seen_skills: set[str],
) -> dict[str, object]:
    field = f"{DOGFOOD_PATH}.cases[{index}]"
    if not isinstance(raw_case, dict):
        raise ValidationError(f"{field} must be an object")

    expected_keys = {"skill_id", "prompt", "acceptance_evidence"}
    unexpected_keys = sorted(set(raw_case) - expected_keys)
    if unexpected_keys:
        rendered = ", ".join(f"`{key}`" for key in unexpected_keys)
        raise ValidationError(f"{field} has unexpected field(s): {rendered}")

    skill_id = _require_string(raw_case.get("skill_id"), field=f"{field}.skill_id")
    if skill_id not in all_skills:
        raise ValidationError(f"{field}.skill_id references unknown public skill `{skill_id}`")
    if skill_id in seen_skills:
        raise ValidationError(f"{DOGFOOD_PATH}: duplicate dogfood case for `{skill_id}`")
    seen_skills.add(skill_id)

    case = {
        "skill_id": skill_id,
        "prompt": _require_string(raw_case.get("prompt"), field=f"{field}.prompt"),
        "acceptance_evidence": _require_string_list(
            raw_case.get("acceptance_evidence"),
            field=f"{field}.acceptance_evidence",
        ),
    }
    return case


def _validate_required_review_coverage(
    *,
    review_required_skills: list[str],
    seen_skills: set[str],
    all_skills: set[str],
) -> None:
    missing_required = sorted(set(review_required_skills) - seen_skills)
    if missing_required:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in missing_required)
        raise ValidationError(f"{DOGFOOD_PATH}: missing required dogfood case(s) for {rendered}")

    for skill_id in review_required_skills:
        if skill_id not in all_skills:
            raise ValidationError(
                f"{DOGFOOD_PATH}: `review_required_skills` references unknown public skill `{skill_id}`"
            )


def validate_registry(data: dict[str, object], repo_root: Path) -> dict[str, object]:
    if data.get("schema_version") != 1:
        raise ValidationError(f"{DOGFOOD_PATH}: schema_version must be 1")

    raw_required = data.get("review_required_skills")
    if not isinstance(raw_required, list) or not all(
        isinstance(item, str) for item in raw_required
    ):
        raise ValidationError(
            f"{DOGFOOD_PATH}: `review_required_skills` must be a list of skill ids"
        )
    review_required_skills = sorted(raw_required)

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list):
        raise ValidationError(f"{DOGFOOD_PATH}: `cases` must be a list")

    all_skills = set(public_skill_ids(repo_root))
    validated_cases: list[dict[str, object]] = []
    seen_skills: set[str] = set()
    for index, raw_case in enumerate(raw_cases):
        validated_cases.append(
            _validate_case(
                raw_case,
                index=index,
                all_skills=all_skills,
                seen_skills=seen_skills,
            )
        )

    _validate_required_review_coverage(
        review_required_skills=review_required_skills,
        seen_skills=seen_skills,
        all_skills=all_skills,
    )

    return {
        "review_required_skills": review_required_skills,
        "cases": validated_cases,
    }
