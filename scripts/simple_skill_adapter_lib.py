from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file
from scripts.artifact_naming_lib import ARTIFACT_CLASSES, RECORD_PATTERN

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")


def infer_simple_adapter_defaults(repo_root: Path, *, output_dir: str) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": output_dir,
    }


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def validate_simple_adapter_data(
    data: dict[str, Any], *, repo_root: Path, output_dir: str
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_simple_adapter_defaults(repo_root, output_dir=output_dir)

    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            validated["version"] = version
        else:
            errors.append("version must be an integer")

    for field in STRING_FIELDS:
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def load_simple_adapter(
    repo_root: Path,
    *,
    skill_id: str,
    artifact_filename: str,
    default_output_dir: str,
    artifact_class: str = "history",
    missing_warnings: tuple[str, ...],
) -> dict[str, Any]:
    if artifact_class not in ARTIFACT_CLASSES:
        raise ValueError(f"artifact_class must be one of: {', '.join(sorted(ARTIFACT_CLASSES))}")
    candidates = (
        Path(f".agents/{skill_id}-adapter.yaml"),
        Path(f".codex/{skill_id}-adapter.yaml"),
        Path(f".claude/{skill_id}-adapter.yaml"),
        Path(f"docs/{skill_id}-adapter.yaml"),
        Path(f"{skill_id}-adapter.yaml"),
    )
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in candidates]
    adapter_path = next((repo_root / candidate for candidate in candidates if (repo_root / candidate).is_file()), None)

    if adapter_path is None:
        data = infer_simple_adapter_defaults(repo_root, output_dir=default_output_dir)
        data["artifact_class"] = artifact_class
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_filename": artifact_filename,
            "artifact_class": artifact_class,
            "artifact_path": str(Path(data["output_dir"]) / artifact_filename),
            "record_artifact_pattern": str(Path(data["output_dir"]) / RECORD_PATTERN),
            "errors": [],
            "warnings": list(missing_warnings),
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / f"{skill_id}-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_simple_adapter_data(raw_data, repo_root=repo_root, output_dir=default_output_dir)
    data["artifact_class"] = artifact_class
    configured_artifact_class = raw_data.get("artifact_class")
    if isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
        data["artifact_class"] = configured_artifact_class
    elif configured_artifact_class is not None:
        errors.append("artifact_class must be one of: current, history, rolling")
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": artifact_filename,
        "artifact_class": data["artifact_class"],
        "artifact_path": str(Path(data["output_dir"]) / artifact_filename),
        "record_artifact_pattern": str(Path(data["output_dir"]) / RECORD_PATTERN),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
