#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from scripts.eval_registry import scenario_ids
from scripts.public_skill_validation_lib import ValidationError, load_policy, validate_policy

REGISTRY_PATH = Path("evals/cautilus/scenarios.json")
ADAPTER_PATH = Path(".agents/cautilus-adapter.yaml")


def load_registry(repo_root: Path) -> dict[str, object]:
    path = repo_root / REGISTRY_PATH
    if not path.is_file():
        raise ValidationError(f"missing `{REGISTRY_PATH}`")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{REGISTRY_PATH}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{REGISTRY_PATH}: top-level JSON value must be an object")
    return data


def validate_registry(repo_root: Path) -> dict[str, object]:
    policy = validate_policy(load_policy(repo_root), repo_root)
    registry = load_registry(repo_root)
    if registry.get("schema_version") != 1:
        raise ValidationError(f"{REGISTRY_PATH}: schema_version must be 1")

    profiles = registry.get("profiles")
    if not isinstance(profiles, dict):
        raise ValidationError(f"{REGISTRY_PATH}: `profiles` must be an object")
    evaluator = profiles.get("evaluator-required")
    if not isinstance(evaluator, dict):
        raise ValidationError(f"{REGISTRY_PATH}: `profiles.evaluator-required` must be an object")
    skills = evaluator.get("skills")
    if not isinstance(skills, list):
        raise ValidationError(f"{REGISTRY_PATH}: `profiles.evaluator-required.skills` must be a list")

    known_scenarios = scenario_ids()
    expected_skills = sorted(policy["tiers"]["evaluator-required"])
    seen: set[str] = set()
    for item in skills:
        if not isinstance(item, dict):
            raise ValidationError(f"{REGISTRY_PATH}: each evaluator-required entry must be an object")
        skill_id = item.get("skill_id")
        scenario_list = item.get("scenario_ids")
        if not isinstance(skill_id, str):
            raise ValidationError(f"{REGISTRY_PATH}: each evaluator-required entry needs string `skill_id`")
        if not isinstance(scenario_list, list) or not scenario_list or not all(isinstance(value, str) for value in scenario_list):
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}` must declare one or more string `scenario_ids`")
        if skill_id not in expected_skills:
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}` is not in the evaluator-required tier")
        if skill_id in seen:
            raise ValidationError(f"{REGISTRY_PATH}: duplicate evaluator-required skill `{skill_id}`")
        unknown = sorted(set(scenario_list) - known_scenarios)
        if unknown:
            rendered = ", ".join(f"`{value}`" for value in unknown)
            raise ValidationError(f"{REGISTRY_PATH}: `{skill_id}` references unknown eval scenario(s): {rendered}")
        seen.add(skill_id)

    missing = sorted(set(expected_skills) - seen)
    if missing:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in missing)
        raise ValidationError(f"{REGISTRY_PATH}: evaluator-required registry is missing {rendered}")

    adapter = repo_root / ADAPTER_PATH
    if not adapter.is_file():
        raise ValidationError(f"missing `{ADAPTER_PATH}`")
    adapter_text = adapter.read_text(encoding="utf-8")
    required_snippets = (
        "profile_default: evaluator-required",
        "held_out_command_templates:",
        "full_gate_command_templates:",
        "evals/cautilus/scenarios.json",
        "scripts/eval_cautilus_scenarios.py",
    )
    missing_snippets = [snippet for snippet in required_snippets if snippet not in adapter_text]
    if missing_snippets:
        rendered = ", ".join(f"`{snippet}`" for snippet in missing_snippets)
        raise ValidationError(f"{ADAPTER_PATH}: missing cautilus scenario wiring snippet(s): {rendered}")

    return {"policy": policy, "registry": registry}
