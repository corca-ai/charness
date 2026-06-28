#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from scripts.public_skill_validation_lib import ValidationError, public_skill_ids

REGISTRY_PATH = Path("evals/cautilus/claim-fidelity-registry.json")
PUBLIC_SKILLS_DIR = Path("skills/public")
ENGAGEMENT_VALUES = ("engage-always", "on-demand", "gate-sufficient")


def _load_json(path: Path) -> object:
    if not path.is_file():
        raise ValidationError(f"missing `{path}`")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def reference_basenames(repo_root: Path, skill_id: str) -> set[str]:
    ref_dir = repo_root / PUBLIC_SKILLS_DIR / skill_id / "references"
    if not ref_dir.is_dir():
        return set()
    return {path.name for path in ref_dir.glob("*.md")}


def expected_public_skills(repo_root: Path) -> set[str]:
    return {skill_id for skill_id in public_skill_ids(repo_root) if reference_basenames(repo_root, skill_id)}


def _validate_engagement(spec_path: str, ref: str, value: object) -> str:
    if not isinstance(value, dict):
        raise ValidationError(f"{spec_path}: referenceEngagement[{ref}] must be an object")
    engagement = value.get("engagement")
    if engagement not in ENGAGEMENT_VALUES:
        raise ValidationError(f"{spec_path}: referenceEngagement[{ref}].engagement must be one of {list(ENGAGEMENT_VALUES)}")
    if not isinstance(value.get("rationale"), str) or not value["rationale"].strip():
        raise ValidationError(f"{spec_path}: referenceEngagement[{ref}] needs a non-empty rationale")
    if engagement == "on-demand" and not str(value.get("trigger") or "").strip():
        raise ValidationError(f"{spec_path}: on-demand reference {ref} must record a trigger")
    if engagement == "gate-sufficient" and not str(value.get("gate") or "").strip():
        raise ValidationError(f"{spec_path}: gate-sufficient reference {ref} must name a gate")
    return engagement


def _validate_string_list(spec_path: str, field: str, value: object) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{spec_path}: `{field}` must be a non-empty string list")
    if len(value) != len(set(value)):
        raise ValidationError(f"{spec_path}: `{field}` has duplicate entries")
    return value


def validate_spec(repo_root: Path, skill_id: str, spec_path: str) -> dict[str, object]:
    expected_path = f"evals/cautilus/{skill_id}-claim-fidelity/spec.json"
    if spec_path != expected_path:
        raise ValidationError(f"`{skill_id}`: spec_path must be `{expected_path}`, got `{spec_path}`")
    spec = _load_json(repo_root / spec_path)
    if not isinstance(spec, dict):
        raise ValidationError(f"{spec_path}: spec must be an object")
    for key, expected in (
        ("skillId", skill_id),
        ("targetId", skill_id),
        ("targetKind", "public_skill"),
        ("prompt", f"/charness:{skill_id}"),
        ("evaluationId", f"execution-{skill_id}-claim-fidelity"),
    ):
        if spec.get(key) != expected:
            raise ValidationError(f"{spec_path}: `{key}` must be `{expected}`")

    declared = _validate_string_list(spec_path, "declaredReferences", spec.get("declaredReferences"))
    engagement = spec.get("referenceEngagement")
    if not isinstance(engagement, dict):
        raise ValidationError(f"{spec_path}: referenceEngagement must be an object")

    fs_refs = reference_basenames(repo_root, skill_id)
    phantom = sorted(set(declared) - fs_refs)
    if phantom:
        raise ValidationError(f"{spec_path}: declaredReferences not present under references/: {phantom}")
    undeclared_engagement = sorted(set(engagement) - set(declared))
    if undeclared_engagement:
        raise ValidationError(f"{spec_path}: referenceEngagement has undeclared references: {undeclared_engagement}")

    engage_always: set[str] = set()
    for ref in declared:
        if ref not in engagement:
            raise ValidationError(f"{spec_path}: declaredReference {ref} has no referenceEngagement entry")
        if _validate_engagement(spec_path, ref, engagement[ref]) == "engage-always":
            engage_always.add(ref)

    required = _validate_string_list(spec_path, "requiredCommandFragments", spec.get("requiredCommandFragments"))
    not_engage_always = [ref for ref in required if ref not in engage_always]
    if not_engage_always:
        raise ValidationError(f"{spec_path}: requiredCommandFragments must be engage-always declaredReferences: {not_engage_always}")

    thresholds = spec.get("thresholds")
    if thresholds is not None and not isinstance(thresholds, dict):
        raise ValidationError(f"{spec_path}: thresholds must be an object when present")

    return {
        "skill_id": skill_id,
        "declared": len(declared),
        "engage_always": sorted(engage_always),
        "undeclared_on_disk": sorted(fs_refs - set(declared)),
    }


def validate_registry(repo_root: Path) -> dict[str, object]:
    registry = _load_json(repo_root / REGISTRY_PATH)
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        raise ValidationError(f"{REGISTRY_PATH}: `schema_version` must be 1")
    specs = registry.get("specs")
    if not isinstance(specs, list) or not specs:
        raise ValidationError(f"{REGISTRY_PATH}: `specs` must be a non-empty list")

    seen: set[str] = set()
    results: list[dict[str, object]] = []
    for item in specs:
        if not isinstance(item, dict):
            raise ValidationError(f"{REGISTRY_PATH}: each `specs` entry must be an object")
        skill_id = item.get("skill_id")
        spec_path = item.get("spec_path")
        if not isinstance(skill_id, str) or not isinstance(spec_path, str):
            raise ValidationError(f"{REGISTRY_PATH}: each entry needs string `skill_id` and `spec_path`")
        if not isinstance(item.get("fan_out_fit"), str) or not item["fan_out_fit"].strip():
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}` needs a non-empty `fan_out_fit` note")
        if skill_id in seen:
            raise ValidationError(f"{REGISTRY_PATH}: duplicate skill `{skill_id}`")
        seen.add(skill_id)
        results.append(validate_spec(repo_root, skill_id, spec_path))

    expected = expected_public_skills(repo_root)
    missing = sorted(expected - seen)
    if missing:
        raise ValidationError(f"{REGISTRY_PATH}: public skills missing a claim-fidelity spec: {missing}")
    unknown = sorted(seen - expected)
    if unknown:
        raise ValidationError(f"{REGISTRY_PATH}: registered skills are not public skills with references: {unknown}")

    return {"registry": registry, "results": results}
