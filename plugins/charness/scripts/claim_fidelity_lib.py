#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.public_skill_validation_lib import ValidationError, public_skill_ids

REGISTRY_PATH = Path("evals/cautilus/claim-fidelity-registry.json")
PUBLIC_SKILLS_DIR = Path("skills/public")
ENGAGEMENT_VALUES = ("engage-always", "on-demand", "gate-sufficient")
# Advisory reference-compaction class: DUP (redundant, deletable), INLINE
# (stranded emittable tokens that belong in SKILL.md `## Closeout Vocabulary`),
# DEPTH (load-bearing conditional judgment worth a re-read). Optional and
# tolerant: an untagged reference is treated as DEPTH by the coverage denominator
# in build-skill-execution-observation.mjs, so un-tagged specs stay valid.
CLASS_TAG_VALUES = ("DUP", "INLINE", "DEPTH")
# A skill may ship several scenario fixtures (e.g. setup's greenfield vs
# normalization branches). The default scenario keeps the bare `spec.json`
# filename and `execution-<skill>-claim-fidelity` evaluationId; additional
# scenarios live at `<scenario>.spec.json` and carry a `scenarioId`.
DEFAULT_SCENARIO = "default"
SCENARIO_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


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


def _validate_engagement(spec_path: str, ref: str, value: object) -> tuple[str, str | None]:
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
    class_tag = value.get("classTag")
    if class_tag is not None and class_tag not in CLASS_TAG_VALUES:
        raise ValidationError(
            f"{spec_path}: referenceEngagement[{ref}].classTag must be one of {list(CLASS_TAG_VALUES)} when present"
        )
    # A DUP/INLINE tag asserts the ref is redundant or belongs inlined; the
    # universal rationale requirement above already forces a written reason for
    # that downgrade, so the tag can never silently weaken the floor without a
    # justification (the RCF cross-check in validate_spec closes the other side:
    # a re-read floor may not be tagged DUP/INLINE).
    return engagement, class_tag


def _validate_string_list(spec_path: str, field: str, value: object) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{spec_path}: `{field}` must be a non-empty string list")
    if len(value) != len(set(value)):
        raise ValidationError(f"{spec_path}: `{field}` has duplicate entries")
    return value


def _validate_optional_string_list(spec_path: str, field: str, value: object) -> list[str]:
    """A fragment channel (requiredCommandFragments / requiredSummaryFragments)
    that may be absent or empty, but must be a duplicate-free string list when
    present. The RCF-or-RSF floor guard in validate_spec enforces that at least
    one channel is non-empty; either one on its own may be empty."""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{spec_path}: `{field}` must be a string list")
    if len(value) != len(set(value)):
        raise ValidationError(f"{spec_path}: `{field}` has duplicate entries")
    return value


def _expected_spec_path(skill_id: str, scenario_id: str) -> str:
    base = f"evals/cautilus/{skill_id}-claim-fidelity"
    if scenario_id == DEFAULT_SCENARIO:
        return f"{base}/spec.json"
    return f"{base}/{scenario_id}.spec.json"


def _expected_evaluation_id(skill_id: str, scenario_id: str) -> str:
    if scenario_id == DEFAULT_SCENARIO:
        return f"execution-{skill_id}-claim-fidelity"
    return f"execution-{skill_id}-{scenario_id}-claim-fidelity"


def _validate_prompt(spec_path: str, skill_id: str, value: object) -> None:
    # The prompt must drive the right skill but may carry a representative
    # objective so the run reaches the reference-routing phase (a bare
    # `/charness:<skill>` stalls for skills that need a subject).
    base = f"/charness:{skill_id}"
    if not isinstance(value, str) or not (
        value == base or (value.startswith(base) and value[len(base) : len(base) + 1].isspace())
    ):
        raise ValidationError(
            f"{spec_path}: `prompt` must be `{base}` optionally followed by whitespace + a representative objective"
        )


def _validate_scenario_id(spec_path: str, scenario_id: str, value: object) -> None:
    if scenario_id == DEFAULT_SCENARIO:
        if value is not None and value != DEFAULT_SCENARIO:
            raise ValidationError(f"{spec_path}: `scenarioId` must be `{DEFAULT_SCENARIO}` or omitted for the default scenario")
    elif value != scenario_id:
        raise ValidationError(f"{spec_path}: `scenarioId` must be `{scenario_id}`")


def validate_spec(repo_root: Path, skill_id: str, scenario_id: str, spec_path: str) -> dict[str, object]:
    expected_path = _expected_spec_path(skill_id, scenario_id)
    if spec_path != expected_path:
        raise ValidationError(f"`{skill_id}`/`{scenario_id}`: spec_path must be `{expected_path}`, got `{spec_path}`")
    spec = _load_json(repo_root / spec_path)
    if not isinstance(spec, dict):
        raise ValidationError(f"{spec_path}: spec must be an object")
    for key, expected in (
        ("skillId", skill_id),
        ("targetId", skill_id),
        ("targetKind", "public_skill"),
        ("evaluationId", _expected_evaluation_id(skill_id, scenario_id)),
    ):
        if spec.get(key) != expected:
            raise ValidationError(f"{spec_path}: `{key}` must be `{expected}`")
    _validate_prompt(spec_path, skill_id, spec.get("prompt"))
    _validate_scenario_id(spec_path, scenario_id, spec.get("scenarioId"))

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
    class_tags: dict[str, str | None] = {}
    for ref in declared:
        if ref not in engagement:
            raise ValidationError(f"{spec_path}: declaredReference {ref} has no referenceEngagement entry")
        engagement_value, class_tag = _validate_engagement(spec_path, ref, engagement[ref])
        if engagement_value == "engage-always":
            engage_always.add(ref)
        class_tags[ref] = class_tag

    # RCF-or-RSF floor channel: a spec proves its claim via the command log
    # (requiredCommandFragments) OR the final summary (requiredSummaryFragments).
    # Either channel may be empty, but not both — a spec with no floor asserts
    # nothing. (The historical rule pinned RCF non-empty, which forced a doc-open
    # proxy even when a summary-token assertion was the honest floor.)
    required = _validate_optional_string_list(spec_path, "requiredCommandFragments", spec.get("requiredCommandFragments"))
    summary_required = _validate_optional_string_list(spec_path, "requiredSummaryFragments", spec.get("requiredSummaryFragments"))
    if not required and not summary_required:
        raise ValidationError(
            f"{spec_path}: at least one of `requiredCommandFragments` or `requiredSummaryFragments` "
            "must be non-empty (the claim floor channel)"
        )
    not_engage_always = [ref for ref in required if ref not in engage_always]
    if not_engage_always:
        raise ValidationError(f"{spec_path}: requiredCommandFragments must be engage-always declaredReferences: {not_engage_always}")
    # A re-read floor asserts the ref is load-bearing enough to force opening;
    # tagging it DUP/INLINE contradicts that. Tolerant: DEPTH or untagged pass.
    downgraded_floor = [ref for ref in required if class_tags.get(ref) in ("DUP", "INLINE")]
    if downgraded_floor:
        raise ValidationError(
            f"{spec_path}: requiredCommandFragments must not be DUP/INLINE-tagged "
            f"(a re-read floor must be load-bearing/DEPTH): {downgraded_floor}"
        )

    thresholds = spec.get("thresholds")
    if thresholds is not None and not isinstance(thresholds, dict):
        raise ValidationError(f"{spec_path}: thresholds must be an object when present")

    return {
        "skill_id": skill_id,
        "scenario_id": scenario_id,
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

    seen_skills: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    results: list[dict[str, object]] = []
    for item in specs:
        if not isinstance(item, dict):
            raise ValidationError(f"{REGISTRY_PATH}: each `specs` entry must be an object")
        skill_id = item.get("skill_id")
        spec_path = item.get("spec_path")
        if not isinstance(skill_id, str) or not isinstance(spec_path, str):
            raise ValidationError(f"{REGISTRY_PATH}: each entry needs string `skill_id` and `spec_path`")
        scenario_id = item.get("scenario_id", DEFAULT_SCENARIO)
        if not isinstance(scenario_id, str) or not SCENARIO_ID_RE.match(scenario_id):
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}` has an invalid `scenario_id`: {scenario_id!r}")
        if not isinstance(item.get("fan_out_fit"), str) or not item["fan_out_fit"].strip():
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}`/`{scenario_id}` needs a non-empty `fan_out_fit` note")
        pair = (skill_id, scenario_id)
        if pair in seen_pairs:
            raise ValidationError(f"{REGISTRY_PATH}: duplicate skill/scenario `{skill_id}`/`{scenario_id}`")
        seen_pairs.add(pair)
        seen_skills.add(skill_id)
        results.append(validate_spec(repo_root, skill_id, scenario_id, spec_path))

    expected = expected_public_skills(repo_root)
    missing = sorted(expected - seen_skills)
    if missing:
        raise ValidationError(f"{REGISTRY_PATH}: public skills missing a claim-fidelity spec: {missing}")
    unknown = sorted(seen_skills - expected)
    if unknown:
        raise ValidationError(f"{REGISTRY_PATH}: registered skills are not public skills with references: {unknown}")

    return {"registry": registry, "results": results}
