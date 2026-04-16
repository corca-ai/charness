#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

from scripts.public_skill_validation_lib import (
    load_policy,
    public_skill_ids,
    validate_policy,
)

DOGFOOD_PATH = Path("docs/public-skill-dogfood.json")
VALID_REVIEW_STATUSES = ("planned", "reviewed")

REPO_SHAPE_HINTS = {
    "announcement": "repo with recent checked-in changes and one clear delivery context such as release notes or a team update",
    "create-cli": "tooling repo where ad hoc shell or Python entrypoints already exist and the command surface needs to be normalized",
    "create-skill": "skills repo with adjacent public/support surfaces, references, and packaging constraints already present",
    "debug": "active repo slice with a reproducible failure, existing logs or tests, and enough local state to preserve a durable debug artifact",
    "find-skills": "repo with multiple public and support skills where the user names a capability instead of a file path",
    "gather": "repo that already keeps gathered artifacts and a source identity that may need refresh-in-place behavior",
    "handoff": "mature repo with an existing handoff artifact and enough adjacent state that the next pickup path can be ambiguous",
    "hitl": "repo with a bounded review target and a decision that must stay explicitly human-owned",
    "ideation": "minimal or loosely defined repo context where the request is still concept-shaping rather than implementation-ready",
    "impl": "repo with an active build slice, existing code or config surfaces, and at least one verification path",
    "init-repo": "partially initialized mature repo with divergent but valid naming and intentionally missing optional surfaces",
    "narrative": "repo with existing source-of-truth docs that drift from the current product or project story",
    "premortem": "repo with a non-trivial pending decision whose main risk is choosing the wrong plan too early",
    "quality": "mature repo with standing local gates, some drift or fragility, and at least one final stop-before-finish command",
    "release": "repo with checked-in version or packaging surfaces and a maintainer-facing release workflow",
    "retro": "repo that just completed a meaningful slice or exposed a missed issue that should feed repeat-trap memory",
    "spec": "repo with an under-specified change request and enough current docs or code to refine a build contract",
}

PROMPT_HINTS = {
    "announcement": "Summarize the latest repo changes into a chat-ready update and keep the draft scoped to what changed.",
    "create-cli": "We keep adding ad hoc scripts here; normalize this into one repo-owned CLI before the command surface sprawls further.",
    "create-skill": "Improve this skill package first so the trigger, references, and helper surface stay portable.",
    "debug": "Investigate this regression and leave a durable record of what actually failed before changing code.",
    "find-skills": "Which skill should handle this named capability, and what existing support surface already covers it?",
    "gather": "Fetch this external source into a durable local artifact instead of giving me a one-turn summary.",
    "handoff": "Use docs/handoff.md as the pickup surface and continue the next highest-leverage workflow from there.",
    "hitl": "Set up a bounded human review loop for this target so the agent does not auto-decide the final judgment.",
    "ideation": "The concept is still fuzzy; help shape the workflow before we commit to a spec or implementation.",
    "impl": "Implement the smallest meaningful slice now and verify it against the current repo contract.",
    "init-repo": "Normalize this partially initialized repo without pretending it needs a greenfield rewrite.",
    "narrative": "Tighten the repo's durable story first, then derive one concise brief from that source of truth.",
    "premortem": "Stress this pending decision before we lock it in and separate real blockers from over-worry.",
    "quality": "Review the current quality posture and install the next deterministic gate if the move is obvious.",
    "release": "Verify and advance the checked-in release surface without hand-editing generated packaging artifacts.",
    "retro": "Run a short retro on this slice and persist the repeat trap if the workflow should have caught it.",
    "spec": "Turn this vague request into a living implementation contract before code changes spread.",
}

EVIDENCE_OVERRIDES = {
    "create-skill": [
        "treats the public skill frontmatter and core trigger as classifier input, not only documentation",
        "keeps `SKILL.md` as selection/sequence core and pushes bulky nuance into references or scripts",
    ],
    "find-skills": [
        "uses the named skill or capability lookup path before falling back to broad filesystem search",
    ],
    "handoff": [
        "reads the current workflow trigger before broad repo exploration and keeps the baton pass continuation-first",
    ],
    "quality": [
        "runs or names the existing repo-owned quality gates before proposing new ones",
        "uses one realistic consumer prompt when the risk is public-skill routing or artifact behavior",
    ],
}


class ValidationError(Exception):
    pass


def _load_frontmatter(skill_path: Path) -> dict[str, str]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _resolve_artifact(repo_root: Path, skill_id: str) -> str | None:
    resolve_script = repo_root / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    if not resolve_script.is_file():
        return None
    result = subprocess.run(
        ["python3", str(resolve_script), "--repo-root", str(repo_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    payload = json.loads(result.stdout)
    artifact_path = payload.get("artifact_path")
    if isinstance(artifact_path, str) and artifact_path:
        return artifact_path
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    for key in ("summary_path", "output_dir", "state_dir"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _index_partition(partition: dict[str, list[str]]) -> dict[str, str]:
    indexed: dict[str, str] = {}
    for label, skill_ids in partition.items():
        for skill_id in skill_ids:
            indexed[skill_id] = label
    return indexed


def _acceptance_evidence(
    skill_id: str,
    *,
    expected_artifact: str | None,
    tier: str,
    adapter_requirement: str,
) -> list[str]:
    evidence = [
        f"routes the prompt to `{skill_id}` instead of an adjacent public skill",
    ]
    if expected_artifact is not None:
        evidence.append(
            f"names or refreshes `{expected_artifact}` when the skill persists durable state"
        )
    elif adapter_requirement == "adapter-free":
        evidence.append(
            "does not invent host-specific adapter state when repo inspection alone should be enough"
        )
    if tier == "evaluator-required":
        evidence.append(
            "handles the skill's load-bearing contract without needing the user to restate obvious repo context"
        )
    else:
        evidence.append(
            "produces an output that a maintainer could review directly without re-deriving the whole request"
        )
    evidence.extend(EVIDENCE_OVERRIDES.get(skill_id, []))
    return evidence


def build_matrix(repo_root: Path, skill_ids: list[str]) -> dict[str, object]:
    policy = validate_policy(load_policy(repo_root), repo_root)
    tier_by_skill = _index_partition(policy["tiers"])
    adapter_by_skill = _index_partition(policy["adapter_requirements"])

    matrix: list[dict[str, object]] = []
    for skill_id in skill_ids:
        skill_path = repo_root / "skills" / "public" / skill_id / "SKILL.md"
        frontmatter = _load_frontmatter(skill_path)
        expected_artifact = _resolve_artifact(repo_root, skill_id)
        tier = tier_by_skill[skill_id]
        adapter_requirement = adapter_by_skill[skill_id]
        matrix.append(
            {
                "skill_id": skill_id,
                "description": frontmatter.get("description", ""),
                "prompt": PROMPT_HINTS.get(skill_id, frontmatter.get("description", "")),
                "repo_shape": REPO_SHAPE_HINTS.get(
                    skill_id,
                    "repo shape not yet classified; add a concrete mature or cold-start fixture before relying on this row",
                ),
                "expected_skill": skill_id,
                "expected_artifact": expected_artifact,
                "validation_tier": tier,
                "adapter_requirement": adapter_requirement,
                "acceptance_evidence": _acceptance_evidence(
                    skill_id,
                    expected_artifact=expected_artifact,
                    tier=tier,
                    adapter_requirement=adapter_requirement,
                ),
            }
        )
    return {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "matrix": matrix,
    }


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
    scaffold_rows = {
        row["skill_id"]: row
        for row in build_matrix(repo_root, sorted({case.get("skill_id") for case in raw_cases if isinstance(case, dict) and isinstance(case.get("skill_id"), str)}))["matrix"]
    }

    validated_cases: list[dict[str, object]] = []
    seen_skills: set[str] = set()
    for index, raw_case in enumerate(raw_cases):
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
            "review_status": _require_string(raw_case.get("review_status"), field=f"{field}.review_status"),
        }
        if case["review_status"] not in VALID_REVIEW_STATUSES:
            rendered = ", ".join(f"`{item}`" for item in VALID_REVIEW_STATUSES)
            raise ValidationError(f"{field}.review_status must be one of {rendered}")
        if case["review_status"] == "reviewed":
            case["reviewed_on"] = _validate_review_date(raw_case.get("reviewed_on"), field=f"{field}.reviewed_on")
            case["observed_evidence"] = _require_string_list(
                raw_case.get("observed_evidence"),
                field=f"{field}.observed_evidence",
            )
        else:
            case["reviewed_on"] = _require_optional_string(
                raw_case.get("reviewed_on"),
                field=f"{field}.reviewed_on",
            )
            observed = raw_case.get("observed_evidence")
            if observed is not None and observed != []:
                case["observed_evidence"] = _require_string_list(
                    observed,
                    field=f"{field}.observed_evidence",
                )
            else:
                case["observed_evidence"] = []

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
        validated_cases.append(case)

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

    return {
        "review_required_skills": review_required_skills,
        "cases": validated_cases,
    }
