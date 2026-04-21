from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, optional_string, optional_string_list
from scripts.artifact_naming_lib import RECORD_PATTERN

ADAPTER_CANDIDATES = (
    Path(".agents/narrative-adapter.yaml"),
    Path(".codex/narrative-adapter.yaml"),
    Path(".claude/narrative-adapter.yaml"),
    Path("docs/narrative-adapter.yaml"),
    Path("narrative-adapter.yaml"),
)
STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
    "quick_start_execution_model",
    "remote_name",
)
LIST_FIELDS = (
    "source_documents",
    "mutable_documents",
    "brief_template",
    "scenario_surfaces",
    "scenario_block_template",
    "primary_reader_profiles",
    "preserve_intents",
    "terms_to_avoid_in_opening",
    "special_entrypoints",
    "skill_grouping_rules",
    "owner_doc_boundaries",
    "landing_danger_checks",
)
ARTIFACT_FILENAME = "latest.md"
SOURCE_DOCUMENT_CANDIDATES = (
    "README.md",
    "docs/master-plan.md",
    "docs/specs/index.spec.md",
    "docs/specs/current-product.spec.md",
    "docs/consumer-readiness.md",
    "docs/external-consumer-onboarding.md",
    "docs/roadmap.md",
    "docs/decisions.md",
    "docs/control-plane.md",
    "docs/operator-acceptance.md",
    "docs/handoff.md",
)


def _infer_source_documents(repo_root: Path) -> list[str]:
    inferred = [path for path in SOURCE_DOCUMENT_CANDIDATES if (repo_root / path).is_file()]
    return inferred or ["README.md"]


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def _bootstrap_expectations(data: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_path": _artifact_path(data["output_dir"]),
        "what_you_get_after_one_run": "A durable truth-surface alignment artifact plus one audience-neutral brief skeleton.",
        "artifact_meaning": "The artifact is a maintained narrative alignment output, not generic writing scratch space.",
        "what_this_does_not_do": "It does not handle audience-specific adaptation or delivery transport; hand off to announcement for that.",
    }


def infer_narrative_defaults(repo_root: Path) -> dict[str, Any]:
    inferred_docs = _infer_source_documents(repo_root)
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/narrative",
        "source_documents": inferred_docs,
        "mutable_documents": inferred_docs,
        "brief_template": [],
        "scenario_surfaces": [],
        "scenario_block_template": [
            "What You Bring",
            "Input (CLI)",
            "Input (For Agent)",
            "What Happens",
            "What Comes Back",
            "Next Action",
        ],
        "primary_reader_profiles": [],
        "preserve_intents": [],
        "terms_to_avoid_in_opening": [],
        "quick_start_execution_model": "",
        "special_entrypoints": [],
        "skill_grouping_rules": [],
        "owner_doc_boundaries": [],
        "landing_danger_checks": [],
        "remote_name": "origin",
    }


def validate_narrative_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_narrative_defaults(repo_root)

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

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["source_documents"]:
        errors.append("source_documents must not be empty")
    if not validated["mutable_documents"]:
        errors.append("mutable_documents must not be empty")

    return validated, errors, warnings


def load_narrative_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        data = infer_narrative_defaults(repo_root)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
            "bootstrap_expectations": _bootstrap_expectations(data),
            "errors": [],
            "warnings": [
            "No narrative adapter found. Using inferred source-of-truth defaults.",
            f"First run leaves `{_artifact_path(data['output_dir'])}` as the durable truth-surface alignment artifact.",
            "High-leverage README or landing rewrites should pin .agents/narrative-adapter.yaml before editing in earnest instead of relying on fallback inference.",
            "Create .agents/narrative-adapter.yaml to pin the truth surface and mutable documents.",
        ],
        "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "narrative-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_narrative_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "bootstrap_expectations": _bootstrap_expectations(data),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
