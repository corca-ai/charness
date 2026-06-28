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


def _ea(rationale: str = "always") -> dict[str, str]:
    return {"engagement": "engage-always", "rationale": rationale}


def _od(rationale: str = "narrow", trigger: str = "when X") -> dict[str, str]:
    return {"engagement": "on-demand", "rationale": rationale, "trigger": trigger}


def _scaffold_skill(repo: Path, skill: str, engagement: dict[str, dict], *, declared=None, rcf=None) -> dict:
    """Write a public skill + its references (one file per engagement key) + spec.json. Returns a registry entry."""
    declared = list(engagement) if declared is None else declared
    _write(repo / "skills" / "public" / skill / "SKILL.md", f"# {skill}\n")
    for ref in engagement:  # on-disk truth is the engagement keys
        _write(repo / "skills" / "public" / skill / "references" / ref, f"# {ref}\n")
    if rcf is None:
        rcf = [ref for ref, value in engagement.items() if value["engagement"] == "engage-always"][:1]
    spec = {
        "skillId": skill,
        "skillDisplayName": skill,
        "evaluationId": f"execution-{skill}-claim-fidelity",
        "targetKind": "public_skill",
        "targetId": skill,
        "prompt": f"/charness:{skill}",
        "requiredCommandFragments": rcf,
        "requiredSummaryFragments": [],
        "declaredReferences": declared,
        "referenceEngagement": engagement,
    }
    _write(repo / "evals" / "cautilus" / f"{skill}-claim-fidelity" / "spec.json", json.dumps(spec) + "\n")
    return {"skill_id": skill, "spec_path": f"evals/cautilus/{skill}-claim-fidelity/spec.json", "fan_out_fit": "no"}


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
