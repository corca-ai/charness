#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scripts.public_skill_dogfood_lib import (
    DOGFOOD_PATH,
    VALID_REVIEW_STATUSES,
    build_matrix,
)
from scripts.public_skill_validation_lib import public_skill_ids


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
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValidationError(f"{field} must be a non-empty list of strings")
    return value


def _require_optional_string(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a string or null")
    return value


def _validate_review_date(value: object, *, field: str) -> str:
    rendered = _require_string(value, field=field)
    try:
        date.fromisoformat(rendered)
    except ValueError as exc:
        raise ValidationError(f"{field} must be an ISO date like YYYY-MM-DD") from exc
    return rendered


def _scaffold_rows_for_cases(repo_root: Path, raw_cases: list[object]) -> dict[str, dict[str, object]]:
    skill_ids = sorted(
        {
            case.get("skill_id")
            for case in raw_cases
            if isinstance(case, dict) and isinstance(case.get("skill_id"), str)
        }
    )
    matrix = build_matrix(repo_root, skill_ids)["matrix"]
    return {row["skill_id"]: row for row in matrix if isinstance(row, dict)}


def _load_case_status_metadata(raw_case: dict[str, object], *, field: str, review_status: str) -> dict[str, object]:
    if review_status == "reviewed":
        return {
            "reviewed_on": _validate_review_date(raw_case.get("reviewed_on"), field=f"{field}.reviewed_on"),
            "observed_evidence": _require_string_list(
                raw_case.get("observed_evidence"),
                field=f"{field}.observed_evidence",
            ),
        }

    reviewed_on = _require_optional_string(
        raw_case.get("reviewed_on"),
        field=f"{field}.reviewed_on",
    )
    observed = raw_case.get("observed_evidence")
    if observed is None or observed == []:
        observed_evidence: list[str] = []
    else:
        observed_evidence = _require_string_list(
            observed,
            field=f"{field}.observed_evidence",
        )
    return {"reviewed_on": reviewed_on, "observed_evidence": observed_evidence}


def _validate_case_scaffold(
    case: dict[str, object],
    *,
    scaffold: dict[str, object],
    skill_id: str,
    field: str,
) -> None:
    for key in (
        "prompt",
        "repo_shape",
        "expected_skill",
        "expected_artifact",
        "validation_tier",
        "adapter_requirement",
        "acceptance_evidence",
    ):
        if case[key] != scaffold[key]:
            raise ValidationError(
                f"{field}.{key} drifted from current scaffold for `{skill_id}`; "
                f"refresh with `python3 scripts/suggest-public-skill-dogfood.py --repo-root . --skill-id {skill_id} --json`"
            )


def _validate_case(
    raw_case: object,
    *,
    index: int,
    all_skills: set[str],
    seen_skills: set[str],
    scaffold_rows: dict[str, dict[str, object]],
) -> dict[str, object]:
    field = f"{DOGFOOD_PATH}.cases[{index}]"
    if not isinstance(raw_case, dict):
        raise ValidationError(f"{field} must be an object")

    skill_id = _require_string(raw_case.get("skill_id"), field=f"{field}.skill_id")
    if skill_id not in all_skills:
        raise ValidationError(f"{field}.skill_id references unknown public skill `{skill_id}`")
    if skill_id in seen_skills:
        raise ValidationError(f"{DOGFOOD_PATH}: duplicate dogfood case for `{skill_id}`")
    seen_skills.add(skill_id)

    scaffold = scaffold_rows.get(skill_id)
    if scaffold is None:
        raise ValidationError(f"{field}: could not scaffold current dogfood contract for `{skill_id}`")

    review_status = _require_string(raw_case.get("review_status"), field=f"{field}.review_status")
    if review_status not in VALID_REVIEW_STATUSES:
        rendered = ", ".join(f"`{item}`" for item in VALID_REVIEW_STATUSES)
        raise ValidationError(f"{field}.review_status must be one of {rendered}")

    case = {
        "skill_id": skill_id,
        "prompt": _require_string(raw_case.get("prompt"), field=f"{field}.prompt"),
        "repo_shape": _require_string(raw_case.get("repo_shape"), field=f"{field}.repo_shape"),
        "expected_skill": _require_string(raw_case.get("expected_skill"), field=f"{field}.expected_skill"),
        "expected_artifact": _require_optional_string(
            raw_case.get("expected_artifact"),
            field=f"{field}.expected_artifact",
        ),
        "validation_tier": _require_string(raw_case.get("validation_tier"), field=f"{field}.validation_tier"),
        "adapter_requirement": _require_string(
            raw_case.get("adapter_requirement"),
            field=f"{field}.adapter_requirement",
        ),
        "acceptance_evidence": _require_string_list(
            raw_case.get("acceptance_evidence"),
            field=f"{field}.acceptance_evidence",
        ),
        "review_status": review_status,
        **_load_case_status_metadata(raw_case, field=field, review_status=review_status),
    }
    _validate_case_scaffold(case, scaffold=scaffold, skill_id=skill_id, field=field)
    return case


def _validate_required_review_coverage(
    *,
    review_required_skills: list[str],
    seen_skills: set[str],
    all_skills: set[str],
    validated_cases: list[dict[str, object]],
) -> None:
    missing_required = sorted(set(review_required_skills) - seen_skills)
    if missing_required:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in missing_required)
        raise ValidationError(f"{DOGFOOD_PATH}: missing required reviewed dogfood case(s) for {rendered}")

    for skill_id in review_required_skills:
        if skill_id not in all_skills:
            raise ValidationError(f"{DOGFOOD_PATH}: `review_required_skills` references unknown public skill `{skill_id}`")

    for case in validated_cases:
        if case["skill_id"] in review_required_skills and case["review_status"] != "reviewed":
            raise ValidationError(
                f"{DOGFOOD_PATH}: required dogfood case `{case['skill_id']}` must use `reviewed` status"
            )


def validate_registry(data: dict[str, object], repo_root: Path) -> dict[str, object]:
    if data.get("schema_version") != 1:
        raise ValidationError(f"{DOGFOOD_PATH}: schema_version must be 1")

    raw_required = data.get("review_required_skills")
    if not isinstance(raw_required, list) or not all(isinstance(item, str) for item in raw_required):
        raise ValidationError(f"{DOGFOOD_PATH}: `review_required_skills` must be a list of skill ids")
    review_required_skills = sorted(raw_required)

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list):
        raise ValidationError(f"{DOGFOOD_PATH}: `cases` must be a list")

    all_skills = set(public_skill_ids(repo_root))
    scaffold_rows = _scaffold_rows_for_cases(repo_root, raw_cases)

    validated_cases: list[dict[str, object]] = []
    seen_skills: set[str] = set()
    for index, raw_case in enumerate(raw_cases):
        validated_cases.append(
            _validate_case(
                raw_case,
                index=index,
                all_skills=all_skills,
                seen_skills=seen_skills,
                scaffold_rows=scaffold_rows,
            )
        )

    _validate_required_review_coverage(
        review_required_skills=review_required_skills,
        seen_skills=seen_skills,
        all_skills=all_skills,
        validated_cases=validated_cases,
    )

    return {
        "review_required_skills": review_required_skills,
        "cases": validated_cases,
    }
