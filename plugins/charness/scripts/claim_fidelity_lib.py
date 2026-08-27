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
    # A DUP/INLINE tag asserts the ref is redundant or belongs inlined. Since
    # 2026-08-11 it weakens NO blocking floor: it only narrows the advisory
    # coverage denominator in scripts/agent-runtime/build-skill-execution-observation.mjs
    # (referenceClass). The one place it still has teeth is the opposite direction --
    # _validate_floor_channel refuses a DUP/INLINE tag on a live
    # requiredCommandFragments ref, because a re-read floor asserts the ref IS
    # load-bearing and the tag says it is not.
    return engagement, class_tag


def _refuse_blank_entries(spec_path: str, field: str, value: list[str]) -> None:
    """A BLANK entry is a token that asserts nothing, and worse than an absent one.

    In a fragment channel, `"".includes` is true for every transcript, so it grades
    green unconditionally AND makes the channel count as populated -- which
    suppresses `_validate_floor_move`. That is the cheapest way to reintroduce
    #583's class, and it leaves nothing a reviewer can grep for. Found by a bounded
    round-1 reviewer; hoisted out of the optional-list helper by round 2, so the
    strict sibling cannot reintroduce the hole for the next field routed through it.
    """
    blank = [item for item in value if not item.strip()]
    if blank:
        raise ValidationError(
            f"{spec_path}: `{field}` has blank entries {blank}; a blank entry matches every "
            "transcript, so it is an always-true floor. Empty the channel instead of flooring on nothing."
        )


def _validate_string_list(spec_path: str, field: str, value: object) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{spec_path}: `{field}` must be a non-empty string list")
    if len(value) != len(set(value)):
        raise ValidationError(f"{spec_path}: `{field}` has duplicate entries")
    _refuse_blank_entries(spec_path, field, value)
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
    _refuse_blank_entries(spec_path, field, value)
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


FLOOR_MOVE_FIELD = "deterministicFloorMovedTo"


def _validate_floor_move(spec_path: str, spec: dict, substance_floor: Path) -> None:
    """An emptied deterministic floor must NAME the instrument that carries the claim.

    [#583](https://github.com/corca-ai/charness/issues/583)'s class is a verification
    surface that silently stops verifying what it claims to. Its recorded instance
    is #568: the `pickup` / `pickup-ambiguous` arms were built to DISCRIMINATE, an
    upstream planner change collapsed both to the same outcome, and neither arm
    hard-fails, so nothing flagged it.

    The sibling check above requires only that an outcome-assertions.json EXISTS,
    and says so in its own docstring. Existence is satisfied by a file shared with
    every other spec in the directory, so it binds an emptied floor to nothing in
    particular. This binds it: name the assertion ids that replace the floor, and
    each must resolve in that file and be a `judge` assertion -- a floor moving
    sideways onto another deterministic check in the same file is not a move to a
    substance instrument.

    What this does NOT check, stated rather than implied: whether the named judge
    assertion actually covers the discrimination the floor lost. It proves the
    pointer resolves to a real substance instrument, not that the instrument is
    sufficient. And it cannot see #568's actual accident -- two arms converging
    while both floors stay populated. That remainder is recorded with the guard.
    """
    declared = spec.get(FLOOR_MOVE_FIELD)
    remedy = (
        f'Add `"{FLOOR_MOVE_FIELD}": {{"assertionIds": ["<id>", ...]}}` naming the '
        f"`kind: judge` assertions in {substance_floor.name} that carry this claim now."
    )
    if not isinstance(declared, dict):
        raise ValidationError(
            f"{spec_path}: every deterministic floor channel is empty, so the claim rests on the "
            f"sibling substance set -- but the spec does not say WHICH assertions replaced it. {remedy}"
        )
    # OPTIONAL-list validation, then the emptiness check below: the strict helper
    # refuses an empty list with a shape message, which would make the branch that
    # carries the remedy unreachable. A test found exactly that.
    declared_file = declared.get("outcomeAssertions")
    if declared_file is not None and declared_file != substance_floor.name:
        # Otherwise the key is decorative: validation silently runs against the
        # resolved sibling while a human reader trusts the declared path.
        raise ValidationError(
            f"{spec_path}: `{FLOOR_MOVE_FIELD}.outcomeAssertions` names `{declared_file}`, but the "
            f"substance floor resolves to `{substance_floor.name}` beside the spec. A declared path "
            "that is not the validated one misleads every reader of this spec."
        )
    ids = _validate_optional_string_list(spec_path, f"{FLOOR_MOVE_FIELD}.assertionIds", declared.get("assertionIds"))
    if not ids:
        raise ValidationError(f"{spec_path}: `{FLOOR_MOVE_FIELD}.assertionIds` must name at least one assertion. {remedy}")
    payload = _load_json(substance_floor)
    if not isinstance(payload, dict) or not isinstance(payload.get("assertions"), list):
        raise ValidationError(f"{spec_path}: {substance_floor.name} carries no `assertions` list to move a floor onto")
    by_id = {
        assertion.get("id"): assertion
        for assertion in payload["assertions"]
        if isinstance(assertion, dict)
    }
    for assertion_id in ids:
        assertion = by_id.get(assertion_id)
        if assertion is None:
            raise ValidationError(
                f"{spec_path}: `{FLOOR_MOVE_FIELD}` names `{assertion_id}`, which does not exist in "
                f"{substance_floor.name}. A floor moved onto nothing is the collapse this field exists to refuse."
            )
        if assertion.get("kind") != "judge":
            raise ValidationError(
                f"{spec_path}: `{FLOOR_MOVE_FIELD}` names `{assertion_id}`, whose kind is "
                f"`{assertion.get('kind')}`. A deterministic floor moving onto another deterministic "
                "check is not a move to a substance instrument."
            )


def _validate_floor_channel(
    repo_root: Path,
    spec_path: str,
    spec: dict,
    engage_always: set[str],
    class_tags: dict[str, str | None],
) -> None:
    """RCF/RSF/read floor channel: a spec proves its claim via the command log
    (requiredCommandFragments), an actual opened reference
    (requiredOpenedReferences), OR the final summary (requiredSummaryFragments).
    Each channel may be empty; all three may be empty ONLY when a sibling
    outcome-assertions.json substance floor carries the claim instead — the honest
    floor for a script/committing skill whose faithful run opens no doc and emits no
    distinctive token (gather public-URL #411, setup #413). The substance set's own
    validity is owned by validate_outcome_assertions.py (the same claim-fidelity-specs
    changed-surface obligation); here we only require it exists so the spec still
    asserts SOMETHING. (The historical rule pinned RCF non-empty, forcing a doc-open
    proxy even when a summary-token or substance assertion was the honest floor.)"""
    required = _validate_optional_string_list(spec_path, "requiredCommandFragments", spec.get("requiredCommandFragments"))
    required_opened = _validate_optional_string_list(
        spec_path, "requiredOpenedReferences", spec.get("requiredOpenedReferences")
    )
    summary_required = _validate_optional_string_list(spec_path, "requiredSummaryFragments", spec.get("requiredSummaryFragments"))
    if not required and not required_opened and not summary_required:
        substance_floor = (repo_root / spec_path).parent / "outcome-assertions.json"
        if not substance_floor.is_file():
            raise ValidationError(
                f"{spec_path}: at least one of `requiredCommandFragments`, `requiredOpenedReferences`, or `requiredSummaryFragments` "
                "must be non-empty (the claim floor channel), OR a sibling outcome-assertions.json "
                "substance floor must exist"
            )
        _validate_floor_move(spec_path, spec, substance_floor)
    not_engage_always = [ref for ref in [*required, *required_opened] if ref not in engage_always]
    if not_engage_always:
        raise ValidationError(
            f"{spec_path}: required command/opened references must be engage-always declaredReferences: "
            f"{not_engage_always}"
        )
    # A re-read floor asserts the ref is load-bearing enough to force opening;
    # tagging it DUP/INLINE contradicts that. Tolerant: DEPTH or untagged pass.
    downgraded_floor = [ref for ref in [*required, *required_opened] if class_tags.get(ref) in ("DUP", "INLINE")]
    if downgraded_floor:
        raise ValidationError(
            f"{spec_path}: required command/opened references must not be DUP/INLINE-tagged "
            f"(a re-read floor must be load-bearing/DEPTH): {downgraded_floor}"
        )


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

    _validate_floor_channel(repo_root, spec_path, spec, engage_always, class_tags)

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
