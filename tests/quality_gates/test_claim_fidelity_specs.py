from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.claim_fidelity_lib import validate_registry
from scripts.public_skill_validation_lib import ValidationError, public_skill_ids

ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ea(rationale: str = "always", class_tag: str | None = None) -> dict[str, str]:
    entry = {"engagement": "engage-always", "rationale": rationale}
    if class_tag is not None:
        entry["classTag"] = class_tag
    return entry


def _od(rationale: str = "narrow", trigger: str = "when X", class_tag: str | None = None) -> dict[str, str]:
    entry = {"engagement": "on-demand", "rationale": rationale, "trigger": trigger}
    if class_tag is not None:
        entry["classTag"] = class_tag
    return entry


def _scaffold_skill(
    repo: Path,
    skill: str,
    engagement: dict[str, dict],
    *,
    declared=None,
    rcf=None,
    rsf=None,
    scenario: str = "default",
    prompt: str | None = None,
) -> dict:
    """Write a public skill + its references (one file per engagement key) + spec. Returns a registry entry."""
    declared = list(engagement) if declared is None else declared
    _write(repo / "skills" / "public" / skill / "SKILL.md", f"# {skill}\n")
    for ref in engagement:  # on-disk truth is the engagement keys
        _write(repo / "skills" / "public" / skill / "references" / ref, f"# {ref}\n")
    if rcf is None:
        rcf = [ref for ref, value in engagement.items() if value["engagement"] == "engage-always"][:1]
    is_default = scenario == "default"
    filename = "spec.json" if is_default else f"{scenario}.spec.json"
    evaluation_id = f"execution-{skill}-claim-fidelity" if is_default else f"execution-{skill}-{scenario}-claim-fidelity"
    spec = {
        "skillId": skill,
        "skillDisplayName": skill,
        "evaluationId": evaluation_id,
        "targetKind": "public_skill",
        "targetId": skill,
        "prompt": prompt if prompt is not None else f"/charness:{skill}",
        "requiredCommandFragments": rcf,
        "requiredSummaryFragments": [] if rsf is None else rsf,
        "declaredReferences": declared,
        "referenceEngagement": engagement,
    }
    if not is_default:
        spec["scenarioId"] = scenario
    _write(repo / "evals" / "cautilus" / f"{skill}-claim-fidelity" / filename, json.dumps(spec) + "\n")
    entry = {"skill_id": skill, "spec_path": f"evals/cautilus/{skill}-claim-fidelity/{filename}", "fan_out_fit": "no"}
    if not is_default:
        entry["scenario_id"] = scenario
    return entry


def _write_registry(repo: Path, entries: list[dict]) -> None:
    _write(
        repo / "evals" / "cautilus" / "claim-fidelity-registry.json",
        json.dumps({"schema_version": 1, "specs": entries}) + "\n",
    )


def test_repo_registry_validates_and_covers_every_public_skill() -> None:
    result = validate_registry(ROOT)
    covered = {entry["skill_id"] for entry in result["results"]}
    # Every public skill (all ship references) must have a claim-fidelity spec.
    assert set(public_skill_ids(ROOT)) <= covered
    assert "quality" in covered and "impl" in covered


def test_valid_minimal_repo_passes(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    result = validate_registry(tmp_path)
    assert result["results"][0]["skill_id"] == "alpha"


def test_declared_reference_not_on_disk_rejected(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, declared=["a.md", "ghost.md"], rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="ghost.md"):
        validate_registry(tmp_path)


def test_on_demand_without_trigger_rejected(tmp_path: Path) -> None:
    engagement = {"a.md": _ea(), "b.md": {"engagement": "on-demand", "rationale": "narrow"}}
    entry = _scaffold_skill(tmp_path, "alpha", engagement, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="on-demand reference b.md must record a trigger"):
        validate_registry(tmp_path)


def test_gate_sufficient_without_gate_rejected(tmp_path: Path) -> None:
    engagement = {"a.md": _ea(), "b.md": {"engagement": "gate-sufficient", "rationale": "covered"}}
    entry = _scaffold_skill(tmp_path, "alpha", engagement, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="gate-sufficient reference b.md must name a gate"):
        validate_registry(tmp_path)


def test_required_command_fragment_must_be_engage_always(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od()}, rcf=["b.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="requiredCommandFragments must be engage-always"):
        validate_registry(tmp_path)


def test_uncovered_public_skill_rejected(tmp_path: Path) -> None:
    alpha = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"])
    # beta is a public skill with references but is left out of the registry.
    _scaffold_skill(tmp_path, "beta", {"c.md": _ea()}, rcf=["c.md"])
    _write_registry(tmp_path, [alpha])
    with pytest.raises(ValidationError, match="missing a claim-fidelity spec.*beta"):
        validate_registry(tmp_path)


def test_multiple_scenarios_per_skill_pass(tmp_path: Path) -> None:
    # A skill may ship branch-specific fixtures whose RCF is mutually exclusive
    # (setup's greenfield-flow vs normalization-flow): one fixture per branch.
    refs = {"a.md": _ea(), "b.md": _ea(), "c.md": _od()}
    green = _scaffold_skill(tmp_path, "setupish", dict(refs), rcf=["a.md"], scenario="greenfield")
    norm = _scaffold_skill(tmp_path, "setupish", dict(refs), rcf=["b.md"], scenario="normalization")
    _write_registry(tmp_path, [green, norm])
    result = validate_registry(tmp_path)
    pairs = {(entry["skill_id"], entry["scenario_id"]) for entry in result["results"]}
    assert pairs == {("setupish", "greenfield"), ("setupish", "normalization")}


def test_duplicate_scenario_rejected(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"], scenario="greenfield")
    _write_registry(tmp_path, [entry, dict(entry)])
    with pytest.raises(ValidationError, match="duplicate skill/scenario .*alpha.*greenfield"):
        validate_registry(tmp_path)


def test_prompt_with_objective_passes(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"], prompt="/charness:alpha add a --json mode")
    _write_registry(tmp_path, [entry])
    assert validate_registry(tmp_path)["results"][0]["skill_id"] == "alpha"


def test_prompt_wrong_skill_rejected(tmp_path: Path) -> None:
    # `/charness:alphabet` shares a prefix with skill `alpha` but is a different
    # command: the word-boundary guard must reject it.
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"], prompt="/charness:alphabet do X")
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="`prompt` must be"):
        validate_registry(tmp_path)


def test_rsf_only_floor_passes(tmp_path: Path) -> None:
    # RCF-or-RSF channel: an empty requiredCommandFragments is legal as long as a
    # requiredSummaryFragments token carries the floor (the RSF-token claim).
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=[], rsf=["categorized closeout"])
    _write_registry(tmp_path, [entry])
    assert validate_registry(tmp_path)["results"][0]["skill_id"] == "alpha"


def test_both_floor_channels_empty_rejected(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=[], rsf=[])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="at least one of .*requiredCommandFragments.*requiredSummaryFragments"):
        validate_registry(tmp_path)


def test_valid_class_tags_pass(tmp_path: Path) -> None:
    engagement = {"a.md": _ea(), "b.md": _od(class_tag="DUP"), "c.md": _od(class_tag="INLINE")}
    entry = _scaffold_skill(tmp_path, "alpha", engagement, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    assert validate_registry(tmp_path)["results"][0]["skill_id"] == "alpha"


def test_invalid_class_tag_rejected(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(class_tag="BOGUS")}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="classTag must be one of"):
        validate_registry(tmp_path)


def test_required_command_fragment_may_not_be_dup_or_inline_tagged(tmp_path: Path) -> None:
    # A re-read floor asserts the ref is load-bearing; tagging it DUP contradicts that.
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(class_tag="DUP")}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="must not be DUP/INLINE-tagged"):
        validate_registry(tmp_path)
