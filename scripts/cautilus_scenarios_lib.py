#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from scripts.cautilus_adapter_lib import load_cautilus_adapter
from scripts.eval_registry import scenario_ids
from scripts.public_skill_validation_lib import ValidationError, load_policy, validate_policy

REGISTRY_PATH = Path("evals/cautilus/scenarios.json")
WHOLE_REPO_ROUTING_FIXTURE_PATH = Path("evals/cautilus/whole-repo-routing.fixture.json")
ADAPTER_PATH = Path(".agents/cautilus-adapter.yaml")
CHATBOT_PROPOSAL_INPUTS_PATH = Path("evals/cautilus/chatbot-scenario-proposal-inputs.json")
CHATBOT_ADAPTER_PATH = Path(".agents/cautilus-adapters/chatbot-proposals.yaml")
CHATBOT_BENCHMARK_ADAPTER_PATH = Path(".agents/cautilus-adapters/chatbot-benchmark.yaml")


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


def load_instruction_surface_fixture(repo_root: Path, path: Path) -> dict[str, object]:
    full_path = repo_root / path
    if not full_path.is_file():
        raise ValidationError(f"missing `{path}`")
    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: top-level JSON value must be an object")
    return data


def load_whole_repo_routing_fixture(repo_root: Path) -> dict[str, object]:
    return load_instruction_surface_fixture(repo_root, WHOLE_REPO_ROUTING_FIXTURE_PATH)


def instruction_surface_fixture_paths(repo_root: Path) -> list[Path]:
    return sorted(path.relative_to(repo_root) for path in (repo_root / "evals" / "cautilus").glob("*.fixture.json"))


def validate_instruction_surface_fixture(repo_root: Path, path: Path) -> dict[str, object]:
    cases = load_instruction_surface_fixture(repo_root, path)
    if cases.get("schemaVersion") != "cautilus.evaluation_input.v1":
        raise ValidationError(f"{path}: schemaVersion must be `cautilus.evaluation_input.v1`")
    if cases.get("surface") != "dev" or cases.get("preset") != "repo":
        raise ValidationError(f"{path}: must declare `surface: dev` and `preset: repo`")
    suite_id = cases.get("suiteId")
    if not isinstance(suite_id, str) or not suite_id:
        raise ValidationError(f"{path}: `suiteId` must be a non-empty string")
    evaluations = cases.get("cases")
    if not isinstance(evaluations, list) or not evaluations:
        raise ValidationError(f"{path}: `cases` must be a non-empty list")

    _validate_instruction_surface_cases(path, evaluations)

    return cases


def validate_instruction_surface_fixtures(repo_root: Path) -> dict[str, dict[str, object]]:
    return {str(path): validate_instruction_surface_fixture(repo_root, path) for path in instruction_surface_fixture_paths(repo_root)}


def _validate_instruction_surface_cases(path: Path, evaluations: list[object]) -> None:
    seen_ids: set[str] = set()
    for index, evaluation in enumerate(evaluations):
        if not isinstance(evaluation, dict):
            raise ValidationError(f"{path}: case {index} must be an object")
        evaluation_id = _validate_instruction_surface_case_identity(path, evaluation, index, seen_ids)
        _validate_instruction_surface_case_expectations(path, evaluation, evaluation_id)
        seen_ids.add(evaluation_id)


def _validate_instruction_surface_case_identity(
    path: Path, evaluation: dict[str, object], index: int, seen_ids: set[str]
) -> str:
    evaluation_id = evaluation.get("caseId")
    prompt = evaluation.get("prompt")
    if not isinstance(evaluation_id, str) or not evaluation_id:
        raise ValidationError(f"{path}: case {index} needs non-empty string `caseId`")
    if evaluation_id in seen_ids:
        raise ValidationError(f"{path}: duplicate `caseId` `{evaluation_id}`")
    if not isinstance(prompt, str) or not prompt:
        raise ValidationError(f"{path}: `{evaluation_id}` needs non-empty string `prompt`")
    return evaluation_id


def _validate_required_concepts(path: Path, evaluation: dict[str, object], evaluation_id: str) -> None:
    required_concepts = evaluation.get("requiredConcepts")
    if required_concepts is None:
        return
    if not isinstance(required_concepts, list):
        raise ValidationError(f"{path}: `{evaluation_id}` `requiredConcepts` must be a list")
    allowed_fields = {"summary", "routingDecision.reasonSummary"}
    for index, concept in enumerate(required_concepts):
        if not isinstance(concept, dict):
            raise ValidationError(f"{path}: `{evaluation_id}` requiredConcepts[{index}] must be an object")
        concept_id = concept.get("id")
        if not isinstance(concept_id, str) or not concept_id:
            raise ValidationError(f"{path}: `{evaluation_id}` requiredConcepts[{index}].id must be a non-empty string")
        terms = concept.get("terms")
        if not isinstance(terms, list) or not terms or not all(isinstance(term, str) and term for term in terms):
            raise ValidationError(f"{path}: `{evaluation_id}` requiredConcepts[{index}].terms must be a non-empty string list")
        source_fields = concept.get("sourceFields", ["summary", "routingDecision.reasonSummary"])
        if not isinstance(source_fields, list) or not source_fields or not all(isinstance(item, str) for item in source_fields):
            raise ValidationError(f"{path}: `{evaluation_id}` requiredConcepts[{index}].sourceFields must be a string list")
        unknown = sorted(set(source_fields) - allowed_fields)
        if unknown:
            rendered = ", ".join(f"`{item}`" for item in unknown)
            raise ValidationError(f"{path}: `{evaluation_id}` requiredConcepts[{index}] has unsupported source field(s): {rendered}")


def _validate_instruction_surface_case_expectations(evaluation_path: Path, evaluation: dict[str, object], evaluation_id: str) -> None:
    expected_routing = evaluation.get("expectedRouting")
    if expected_routing is not None:
        if not isinstance(expected_routing, dict):
            raise ValidationError(f"{evaluation_path}: `{evaluation_id}` `expectedRouting` must be an object")
        if not any(
            isinstance(expected_routing.get(key), str) and expected_routing.get(key)
            for key in ("selectedSkill", "bootstrapHelper", "workSkill", "selectedSupport", "firstToolCallPattern")
        ):
            raise ValidationError(
                f"{evaluation_path}: `{evaluation_id}` `expectedRouting` must declare at least one expectation"
            )
    _validate_required_concepts(evaluation_path, evaluation, evaluation_id)
    instruction_surface = evaluation.get("instructionSurface")
    if instruction_surface is None:
        return
    if not isinstance(instruction_surface, dict):
        raise ValidationError(f"{evaluation_path}: `{evaluation_id}` `instructionSurface` must be an object")
    files = instruction_surface.get("files")
    if not isinstance(files, list) or not files:
        raise ValidationError(
            f"{evaluation_path}: `{evaluation_id}` `instructionSurface.files` must be a non-empty list"
        )


def validate_whole_repo_routing_fixture(repo_root: Path) -> dict[str, object]:
    return validate_instruction_surface_fixture(repo_root, WHOLE_REPO_ROUTING_FIXTURE_PATH)


def _load_json_object(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValidationError(f"missing `{path}`")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: top-level JSON value must be an object")
    return data


def _validate_nonempty_string_list(path: Path, data: dict[str, object], key: str) -> list[str]:
    values = data.get(key)
    if not isinstance(values, list) or not values or not all(isinstance(value, str) and value for value in values):
        raise ValidationError(f"{path}: `{key}` must be a non-empty list of strings")
    return values


def _validate_chatbot_candidate(path: Path, candidate: object, index: int, families: list[str], seen_keys: set[str]) -> None:
    if not isinstance(candidate, dict):
        raise ValidationError(f"{path}: candidate {index} must be an object")
    for key in ("proposalKey", "title", "family", "name", "description", "brief"):
        value = candidate.get(key)
        if not isinstance(value, str) or not value:
            raise ValidationError(f"{path}: candidate {index} needs non-empty string `{key}`")
    proposal_key = candidate["proposalKey"]
    assert isinstance(proposal_key, str)
    if proposal_key in seen_keys:
        raise ValidationError(f"{path}: duplicate `proposalKey` `{proposal_key}`")
    family = candidate["family"]
    assert isinstance(family, str)
    if family not in families:
        raise ValidationError(f"{path}: `{proposal_key}` references unknown family `{family}`")
    evidence = candidate.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValidationError(f"{path}: `{proposal_key}` needs non-empty list `evidence`")
    seen_keys.add(proposal_key)


def validate_chatbot_proposal_inputs(repo_root: Path) -> dict[str, object]:
    path = repo_root / CHATBOT_PROPOSAL_INPUTS_PATH
    data = _load_json_object(path)
    if data.get("schemaVersion") != "cautilus.scenario_proposal_inputs.v1":
        raise ValidationError(f"{path}: schemaVersion must be `cautilus.scenario_proposal_inputs.v1`")
    families = _validate_nonempty_string_list(path, data, "families")
    candidates = data.get("proposalCandidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValidationError(f"{path}: `proposalCandidates` must be a non-empty list")
    seen_keys: set[str] = set()
    for index, candidate in enumerate(candidates):
        _validate_chatbot_candidate(path, candidate, index, families, seen_keys)
    registry = data.get("existingScenarioRegistry")
    if not isinstance(registry, list):
        raise ValidationError(f"{path}: `existingScenarioRegistry` must be a list")
    coverage = data.get("scenarioCoverage")
    if not isinstance(coverage, list):
        raise ValidationError(f"{path}: `scenarioCoverage` must be a list")
    now = data.get("now")
    if not isinstance(now, str) or not now:
        raise ValidationError(f"{path}: `now` must be a non-empty string")
    return data


def _load_registry_context(repo_root: Path) -> tuple[dict[str, object], dict[str, object], dict[str, dict[str, object]]]:
    policy = validate_policy(load_policy(repo_root), repo_root)
    registry = load_registry(repo_root)
    instruction_surface_cases = validate_instruction_surface_fixtures(repo_root)
    return policy, registry, instruction_surface_cases


def _evaluator_required_skills(
    registry: dict[str, object],
) -> list[dict[str, object]]:
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
    return skills


def _validate_registry_skill_entries(
    skills: list[object],
    expected_skills: list[str],
    known_scenarios: set[str],
) -> set[str]:
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
    return seen


def _validate_registry_skill_coverage(expected_skills: list[str], seen: set[str]) -> None:
    missing = sorted(set(expected_skills) - seen)
    if missing:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in missing)
        raise ValidationError(f"{REGISTRY_PATH}: evaluator-required registry is missing {rendered}")


def _validate_adapter_wiring(repo_root: Path) -> None:
    adapter = repo_root / ADAPTER_PATH
    if not adapter.is_file():
        raise ValidationError(f"missing `{ADAPTER_PATH}`")
    adapter_payload = load_cautilus_adapter(repo_root)
    if not adapter_payload["valid"]:
        raise ValidationError(f"{ADAPTER_PATH}: {'; '.join(adapter_payload['errors'])}")
    adapter_text = adapter.read_text(encoding="utf-8")
    required_snippets = (
        "profile_default: evaluator-required",
        "run_mode:",
        "prompt_affecting_patterns:",
        "scenario_review_patterns:",
        "evaluation_input_default:",
        "eval_test_command_templates:",
        "held_out_command_templates:",
        "full_gate_command_templates:",
        "evals/cautilus/scenarios.json",
        "evals/cautilus/whole-repo-routing.fixture.json",
        "scripts/eval_cautilus_scenarios.py",
        "scripts/agent-runtime/run-local-eval-test.mjs",
    )
    missing_snippets = [snippet for snippet in required_snippets if snippet not in adapter_text]
    if missing_snippets:
        rendered = ", ".join(f"`{snippet}`" for snippet in missing_snippets)
        raise ValidationError(f"{ADAPTER_PATH}: missing cautilus scenario wiring snippet(s): {rendered}")

    required_runtime_files = (
        "scripts/agent-runtime/contract-versions.mjs",
        "scripts/agent-runtime/codex-eval-runtime.mjs",
        "scripts/agent-runtime/instruction-surface-case-suite.mjs",
        "scripts/agent-runtime/instruction-surface-support.mjs",
        "scripts/agent-runtime/run-local-eval-test.mjs",
        "scripts/agent-runtime/skill-test-telemetry.mjs",
    )
    missing_runtime_files = [path for path in required_runtime_files if not (repo_root / path).is_file()]
    if missing_runtime_files:
        rendered = ", ".join(f"`{path}`" for path in missing_runtime_files)
        raise ValidationError(f"{ADAPTER_PATH}: missing whole-repo eval runtime file(s): {rendered}")

    chatbot_adapter = repo_root / CHATBOT_ADAPTER_PATH
    if not chatbot_adapter.is_file():
        raise ValidationError(f"missing `{CHATBOT_ADAPTER_PATH}`")
    chatbot_adapter_text = chatbot_adapter.read_text(encoding="utf-8")
    chatbot_required_snippets = (
        "scripts/eval_cautilus_chatbot_proposals.py",
        "evals/cautilus/chatbot-scenario-proposal-inputs.json",
        "charness-artifacts/cautilus/chatbot-proposals/held-out",
        "charness-artifacts/cautilus/chatbot-proposals/full-gate",
    )
    missing_chatbot_snippets = [snippet for snippet in chatbot_required_snippets if snippet not in chatbot_adapter_text]
    if missing_chatbot_snippets:
        rendered = ", ".join(f"`{snippet}`" for snippet in missing_chatbot_snippets)
        raise ValidationError(f"{CHATBOT_ADAPTER_PATH}: missing chatbot proposal wiring snippet(s): {rendered}")

    chatbot_runner = repo_root / "scripts" / "eval_cautilus_chatbot_proposals.py"
    if not chatbot_runner.is_file():
        raise ValidationError("missing `scripts/eval_cautilus_chatbot_proposals.py`")

    chatbot_benchmark_adapter = repo_root / CHATBOT_BENCHMARK_ADAPTER_PATH
    if not chatbot_benchmark_adapter.is_file():
        raise ValidationError(f"missing `{CHATBOT_BENCHMARK_ADAPTER_PATH}`")
    chatbot_benchmark_text = chatbot_benchmark_adapter.read_text(encoding="utf-8")
    benchmark_required_snippets = (
        "comparison_command_templates:",
        "scripts/eval_cautilus_chatbot_compare.py",
        "--baseline-repo {baseline_repo}",
        "--candidate-repo {candidate_repo}",
        "charness-artifacts/cautilus/chatbot-benchmark/latest.json",
    )
    missing_benchmark_snippets = [snippet for snippet in benchmark_required_snippets if snippet not in chatbot_benchmark_text]
    if missing_benchmark_snippets:
        rendered = ", ".join(f"`{snippet}`" for snippet in missing_benchmark_snippets)
        raise ValidationError(f"{CHATBOT_BENCHMARK_ADAPTER_PATH}: missing chatbot benchmark wiring snippet(s): {rendered}")

    chatbot_compare_runner = repo_root / "scripts" / "eval_cautilus_chatbot_compare.py"
    if not chatbot_compare_runner.is_file():
        raise ValidationError("missing `scripts/eval_cautilus_chatbot_compare.py`")


def validate_registry(repo_root: Path) -> dict[str, object]:
    policy, registry, instruction_surface_cases = _load_registry_context(repo_root)
    skills = _evaluator_required_skills(registry)
    expected_skills = sorted(policy["tiers"]["evaluator-required"])
    seen = _validate_registry_skill_entries(skills, expected_skills, scenario_ids())
    _validate_registry_skill_coverage(expected_skills, seen)
    chatbot_proposal_inputs = validate_chatbot_proposal_inputs(repo_root)
    _validate_adapter_wiring(repo_root)
    return {
        "policy": policy,
        "registry": registry,
        "instruction_surface_cases": instruction_surface_cases,
        "chatbot_proposal_inputs": chatbot_proposal_inputs,
    }
