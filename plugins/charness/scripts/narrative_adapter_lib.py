from __future__ import annotations

import re
from difflib import get_close_matches
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
)
RECOMMENDED_LANDING_FIELDS = (
    "primary_reader_profiles",
    "preserve_intents",
    "owner_doc_boundaries",
    "landing_danger_checks",
)
VOLATILE_PATH_PARTS = {"internal", "archive", "archived"}
VOLATILE_FILENAMES = {"handoff.md"}
PATH_SUGGESTION_SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


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


def _finding(
    finding_type: str,
    severity: str,
    message: str,
    *,
    path: str | None = None,
    recommended_action: str | None = None,
) -> dict[str, str]:
    result = {
        "type": finding_type,
        "severity": severity,
        "message": message,
    }
    if path is not None:
        result["path"] = path
    if recommended_action is not None:
        result["recommended_action"] = recommended_action
    return result


def _is_volatile_path(path: str) -> bool:
    candidate = Path(path)
    parts = {part.lower() for part in candidate.parts}
    if candidate.name.lower() in VOLATILE_FILENAMES or bool(parts & VOLATILE_PATH_PARTS):
        return True
    tokens = {
        token
        for part in parts
        for token in re.split(r"[^a-z0-9]+", part)
        if token
    }
    return bool(tokens & VOLATILE_PATH_PARTS)


def _looks_like_path(value: str) -> bool:
    candidate = Path(value)
    return len(candidate.parts) > 1 or candidate.suffix != ""


def _existing_paths(repo_root: Path, paths: list[str]) -> set[str]:
    return {path for path in paths if (repo_root / path).exists()}


def _repo_file_paths(repo_root: Path) -> list[str]:
    files: list[str] = []
    for candidate in repo_root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(repo_root)
        if any(part in PATH_SUGGESTION_SKIP_DIRS for part in relative.parts):
            continue
        files.append(relative.as_posix())
    return files


def _suggest_existing_path(repo_root: Path, missing_path: str) -> str | None:
    existing = _repo_file_paths(repo_root)
    missing_name = Path(missing_path).name.lower()
    same_name = [path for path in existing if Path(path).name.lower() == missing_name]
    if same_name:
        return min(same_name, key=len)
    matches = get_close_matches(missing_path, existing, n=1, cutoff=0.58)
    return matches[0] if matches else None


def review_narrative_adapter(repo_root: Path) -> dict[str, Any]:
    adapter = load_narrative_adapter(repo_root)
    data = adapter["data"]
    findings: list[dict[str, str]] = []

    if not adapter["found"]:
        findings.append(
            _finding(
                "missing_adapter",
                "block",
                "No narrative adapter is pinned, so a high-leverage README rewrite would rely on inferred defaults.",
                recommended_action=(
                    "Create .agents/narrative-adapter.yaml with primary readers, stable source docs, "
                    "mutable docs, owner boundaries, and landing danger checks before rewriting."
                ),
            )
        )

    for error in adapter["errors"]:
        findings.append(
            _finding(
                "invalid_adapter",
                "block",
                error,
                recommended_action="Repair the adapter before trusting repo-local narrative guidance.",
            )
        )

    path_fields = ("source_documents", "mutable_documents")
    for field in path_fields:
        for path in data.get(field, []):
            if not (repo_root / path).exists():
                suggestion = _suggest_existing_path(repo_root, path)
                recommended_action = "Fix the adapter path or create the owning document before rewriting."
                if suggestion:
                    recommended_action = (
                        f"Fix the adapter path or create the owning document before rewriting. "
                        f"Closest existing path: `{suggestion}`."
                    )
                findings.append(
                    _finding(
                        "missing_adapter_path",
                        "block",
                        f"`{field}` references a path that does not exist.",
                        path=path,
                        recommended_action=recommended_action,
                    )
                )

    source_documents = list(data.get("source_documents", []))
    mutable_documents = list(data.get("mutable_documents", []))
    special_entrypoints = list(data.get("special_entrypoints", []))
    source_set = set(source_documents)

    for path in source_documents:
        if _is_volatile_path(path):
            findings.append(
                _finding(
                    "volatile_source_document",
                    "warn",
                    "A source document looks volatile or maintainer-internal; use it as context only if it should shape the durable landing story.",
                    path=path,
                    recommended_action="Prefer stable public/operator truth docs for README rewrites.",
                )
            )

    for path in mutable_documents:
        if _is_volatile_path(path):
            findings.append(
                _finding(
                    "volatile_mutable_document",
                    "block",
                    "A mutable document looks volatile or maintainer-internal; rewriting it as part of durable narrative alignment can leak session pickup into public truth.",
                    path=path,
                    recommended_action="Move volatile pickup notes out of mutable_documents unless the task is explicitly a handoff/internal-doc rewrite.",
                )
            )

    for path in special_entrypoints:
        if not _looks_like_path(path):
            continue
        if not (repo_root / path).exists():
            suggestion = _suggest_existing_path(repo_root, path)
            recommended_action = "Fix the adapter path or keep this entrypoint as a non-path label."
            if suggestion:
                recommended_action = (
                    f"Fix the adapter path or keep this entrypoint as a non-path label. "
                    f"Closest existing path: `{suggestion}`."
                )
            findings.append(
                _finding(
                    "missing_adapter_path",
                    "block",
                    "`special_entrypoints` references a path that does not exist.",
                    path=path,
                    recommended_action=recommended_action,
                )
            )
        elif path not in source_set:
            findings.append(
                _finding(
                    "entrypoint_not_in_sources",
                    "warn",
                    "A special entrypoint is not in source_documents, so it may be linked but not used to shape the landing structure.",
                    path=path,
                    recommended_action="Add it to source_documents when it should influence the README, or remove it from special_entrypoints.",
                )
            )

    for field in RECOMMENDED_LANDING_FIELDS:
        if not data.get(field):
            findings.append(
                _finding(
                    "thin_landing_adapter",
                    "warn",
                    f"`{field}` is empty, so the agent must infer part of the first-touch README contract.",
                    recommended_action=f"Fill `{field}` when README, landing, or operator-facing narrative quality matters.",
                )
            )

    if len(source_documents) > 8:
        findings.append(
            _finding(
                "broad_source_set",
                "warn",
                "source_documents is broad enough that current implementation detail may crowd out the first-touch story.",
                recommended_action="Keep the default README rewrite source set stable and curated; move volatile or deep owner docs behind links.",
            )
        )

    existing_sources = _existing_paths(repo_root, source_documents)
    status = "ok"
    if any(finding["severity"] == "block" for finding in findings):
        status = "needs-repair"
    elif findings:
        status = "review"

    return {
        "adapter": {
            "found": adapter["found"],
            "valid": adapter["valid"],
            "path": adapter["path"],
            "warnings": adapter["warnings"],
        },
        "status": status,
        "source_documents_existing": sorted(existing_sources),
        "findings": findings,
    }
