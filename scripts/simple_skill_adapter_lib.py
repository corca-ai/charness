from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from scripts.adapter_lib import load_yaml_file, optional_string
from scripts.artifact_naming_lib import ARTIFACT_CLASSES, RECORD_PATTERN

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
ValidateAdapter = Callable[[dict[str, Any], Path], tuple[dict[str, Any], list[str], list[str]]]
InferDefaults = Callable[[Path], dict[str, Any]]
ExtraPayload = Callable[[dict[str, Any], dict[str, Any], bool], dict[str, Any]]


def adapter_candidates(skill_id: str) -> tuple[Path, ...]:
    return (
        Path(f".agents/{skill_id}-adapter.yaml"),
        Path(f".codex/{skill_id}-adapter.yaml"),
        Path(f".claude/{skill_id}-adapter.yaml"),
        Path(f"docs/{skill_id}-adapter.yaml"),
        Path(f"{skill_id}-adapter.yaml"),
    )


def searched_adapter_paths(repo_root: Path, skill_id: str) -> list[str]:
    return [str((repo_root / candidate).resolve()) for candidate in adapter_candidates(skill_id)]


def find_adapter(repo_root: Path, skill_id: str) -> Path | None:
    return next(
        (repo_root / candidate for candidate in adapter_candidates(skill_id) if (repo_root / candidate).is_file()),
        None,
    )


def artifact_path(output_dir: str, artifact_filename: str) -> str:
    return str(Path(output_dir) / artifact_filename)


def record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def load_adapter_contract(
    repo_root: Path,
    *,
    skill_id: str,
    infer_defaults: InferDefaults,
    validate_adapter_data: ValidateAdapter,
    missing_warnings: tuple[str, ...],
    artifact_filename: str | None = None,
    artifact_class_key: str | None = "artifact_class",
    extra_payload: ExtraPayload | None = None,
) -> dict[str, Any]:
    searched_paths = searched_adapter_paths(repo_root, skill_id)
    adapter_path = find_adapter(repo_root, skill_id)
    if adapter_path is None:
        data = infer_defaults(repo_root)
        payload: dict[str, Any] = {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "errors": [],
            "warnings": list(missing_warnings),
            "searched_paths": searched_paths,
        }
        _add_artifact_payload(payload, data, artifact_filename, artifact_class_key)
        if extra_payload is not None:
            payload.update(extra_payload(data, {}, False))
        return payload

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / f"{skill_id}-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    payload = {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
    _add_artifact_payload(payload, data, artifact_filename, artifact_class_key)
    if extra_payload is not None:
        payload.update(extra_payload(data, raw_data, True))
    return payload


def _add_artifact_payload(
    payload: dict[str, Any],
    data: dict[str, Any],
    artifact_filename: str | None,
    artifact_class_key: str | None,
) -> None:
    if artifact_filename is None:
        return
    payload["artifact_filename"] = artifact_filename
    if artifact_class_key and artifact_class_key in data:
        payload["artifact_class"] = data[artifact_class_key]
    payload["artifact_path"] = artifact_path(data["output_dir"], artifact_filename)
    payload["record_artifact_pattern"] = record_artifact_pattern(data["output_dir"])


def infer_simple_adapter_defaults(repo_root: Path, *, output_dir: str) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": output_dir,
    }


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
        value = optional_string(data.get(field), field, errors)
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
    def infer_defaults(root: Path) -> dict[str, Any]:
        data = infer_simple_adapter_defaults(root, output_dir=default_output_dir)
        data["artifact_class"] = artifact_class
        return data

    def validate(data: dict[str, Any], root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
        validated, errors, warnings = validate_simple_adapter_data(
            data, repo_root=root, output_dir=default_output_dir
        )
        validated["artifact_class"] = artifact_class
        configured_artifact_class = data.get("artifact_class")
        if isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
            validated["artifact_class"] = configured_artifact_class
        elif configured_artifact_class is not None:
            errors.append("artifact_class must be one of: current, history, rolling")
        return validated, errors, warnings

    return load_adapter_contract(
        repo_root,
        skill_id=skill_id,
        infer_defaults=infer_defaults,
        validate_adapter_data=validate,
        missing_warnings=missing_warnings,
        artifact_filename=artifact_filename,
    )
