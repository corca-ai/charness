from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, optional_string, optional_string_list

ADAPTER_PATH = Path(".agents/cautilus-adapter.yaml")
ARTIFACT_PATH = "charness-artifacts/cautilus/latest.md"
VALID_RUN_MODES = ("auto", "ask", "adaptive")
STRING_FIELDS = ("repo", "run_mode", "instruction_surface_command", "profile_default")
LIST_FIELDS = (
    "evaluation_surfaces",
    "baseline_options",
    "required_prerequisites",
    "preflight_commands",
    "instruction_surface_test_command_templates",
    "held_out_command_templates",
    "full_gate_command_templates",
    "artifact_paths",
    "report_paths",
    "comparison_questions",
    "prompt_affecting_patterns",
    "scenario_review_patterns",
    "truth_surface_patterns",
    "cross_repo_issue_patterns",
)
DEFAULT_PROMPT_AFFECTING_PATTERNS = [
    "AGENTS.md",
    ".agents/*-adapter.yaml",
    ".agents/cautilus-adapters/*.yaml",
    "skills/public/*/SKILL.md",
    "skills/public/*/references/**",
    "skills/support/*/SKILL.md",
    "skills/support/*/references/**",
]
DEFAULT_SCENARIO_REVIEW_PATTERNS = [
    "AGENTS.md",
    ".agents/*-adapter.yaml",
    "README.md",
    "docs/public-skill-validation.md",
    "docs/public-skill-validation.json",
    "skills/public/*/SKILL.md",
    "skills/public/narrative/**",
]
DEFAULT_TRUTH_SURFACE_PATTERNS = [
    "README.md",
    "docs/roadmap.md",
    "docs/operator-acceptance.md",
    "docs/handoff.md",
    "docs/public-skill-validation.md",
]
DEFAULT_CROSS_REPO_ISSUE_PATTERNS = [
    "skills/public/narrative/references/cross-repo-issue-shaping.md",
]


def infer_cautilus_defaults(repo_root: Path, *, run_mode: str = "ask") -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "run_mode": run_mode,
        "evaluation_surfaces": [
            "skill portability and metadata integrity",
            "repo-owned validation workflow",
        ],
        "baseline_options": ["compare against a git ref in the same repo via {baseline_ref}"],
        "required_prerequisites": [
            "install Python and Node dependencies before running repo quality gates"
        ],
        "preflight_commands": [
            "python3 scripts/validate_adapters.py --repo-root .",
            "python3 scripts/validate_public_skill_validation.py --repo-root .",
            "python3 scripts/validate_cautilus_scenarios.py --repo-root .",
        ],
        "instruction_surface_command": "cautilus instruction-surface test --repo-root .",
        "instruction_surface_test_command_templates": [
            "node ./scripts/agent-runtime/run-local-instruction-surface-test.mjs --repo-root . --workspace {candidate_repo} --cases-file {instruction_surface_cases_file} --output-file {instruction_surface_input_file} --artifact-dir {output_dir}/instruction-surface-test --backend {backend} --sandbox read-only --timeout-ms 180000 --codex-model gpt-5.4-mini --codex-reasoning-effort low --claude-permission-mode dontAsk"
        ],
        "held_out_command_templates": [
            "python3 scripts/eval_cautilus_scenarios.py --repo-root . --mode held_out --profile {profile} --baseline-ref {baseline_ref} --samples {held_out_samples} --output-dir charness-artifacts/cautilus/held-out"
        ],
        "full_gate_command_templates": [
            "python3 scripts/eval_cautilus_scenarios.py --repo-root . --mode full_gate --profile {profile} --baseline-ref {baseline_ref} --samples {full_gate_samples} --output-dir charness-artifacts/cautilus/full-gate"
        ],
        "artifact_paths": [
            "docs/public-skill-validation.md",
            "docs/public-skill-validation.json",
            "evals/cautilus/scenarios.json",
            "evals/cautilus/instruction-surface-cases.json",
            ARTIFACT_PATH,
            "charness-artifacts/quality/latest.md",
        ],
        "report_paths": [
            "charness-artifacts/cautilus/held-out/summary.json",
            "charness-artifacts/cautilus/full-gate/summary.json",
        ],
        "comparison_questions": ["Which evaluator-required skill scenario improved or regressed?"],
        "human_review_prompts": [
            {"id": "portability", "prompt": "Where would a host repo still find charness brittle or unclear despite green repo-owned gates?"},
            {
                "id": "scenario-registry",
                "prompt": "Did this slice actually change maintained evaluator coverage enough that `evals/cautilus/scenarios.json` should be added, removed, or updated?"
            },
        ],
        "profile_default": "evaluator-required",
        "prompt_affecting_patterns": list(DEFAULT_PROMPT_AFFECTING_PATTERNS),
        "scenario_review_patterns": list(DEFAULT_SCENARIO_REVIEW_PATTERNS),
        "truth_surface_patterns": list(DEFAULT_TRUTH_SURFACE_PATTERNS),
        "cross_repo_issue_patterns": list(DEFAULT_CROSS_REPO_ISSUE_PATTERNS),
    }


def _validate_human_review_prompts(
    value: Any, errors: list[str], warnings: list[str]
) -> list[dict[str, str]] | None:
    if value is None:
        return None
    if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
        warnings.append(
            "human_review_prompts uses list-of-maps YAML that the lightweight loader only reads approximately; keeping inferred defaults for validation."
        )
        return None
    if not isinstance(value, list):
        errors.append("human_review_prompts must be a list")
        return None
    prompts: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"human_review_prompts[{index}] must be an object")
            continue
        prompt_id = item.get("id")
        prompt_text = item.get("prompt")
        if not isinstance(prompt_id, str) or not prompt_id:
            errors.append(f"human_review_prompts[{index}].id must be a non-empty string")
            continue
        if not isinstance(prompt_text, str) or not prompt_text:
            errors.append(f"human_review_prompts[{index}].prompt must be a non-empty string")
            continue
        prompts.append({"id": prompt_id, "prompt": prompt_text})
    return prompts


def validate_cautilus_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_cautilus_defaults(repo_root, run_mode="adaptive")

    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            validated["version"] = version
        else:
            errors.append("version must be an integer")

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in LIST_FIELDS:
        value = optional_string_list(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    prompts = _validate_human_review_prompts(data.get("human_review_prompts"), errors, warnings)
    if prompts is not None:
        validated["human_review_prompts"] = prompts

    if validated["run_mode"] not in VALID_RUN_MODES:
        errors.append(f"run_mode must be one of {', '.join(VALID_RUN_MODES)}")
    if not validated["instruction_surface_test_command_templates"]:
        errors.append("instruction_surface_test_command_templates must not be empty")
    if not validated["prompt_affecting_patterns"]:
        errors.append("prompt_affecting_patterns must not be empty")
    if not validated["artifact_paths"] or ARTIFACT_PATH not in validated["artifact_paths"]:
        errors.append(f"artifact_paths must include {ARTIFACT_PATH}")
    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def load_cautilus_adapter(repo_root: Path) -> dict[str, Any]:
    adapter_path = repo_root / ADAPTER_PATH
    if not adapter_path.is_file():
        data = infer_cautilus_defaults(repo_root, run_mode="ask")
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_path": ARTIFACT_PATH,
            "errors": [],
            "warnings": [
                "No cautilus adapter found. Using safe ask-before-run defaults.",
                "Prompt-affecting proof may still be required, but explicit operator confirmation is the default without a repo adapter.",
                "Create .agents/cautilus-adapter.yaml to choose `auto`, `ask`, or `adaptive` and to declare scenario-review patterns.",
            ],
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    data, errors, extra_warnings = validate_cautilus_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_path": ARTIFACT_PATH,
        "errors": errors,
        "warnings": warnings,
    }
