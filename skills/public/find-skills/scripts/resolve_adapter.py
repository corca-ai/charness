#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
load_yaml_file = _scripts_adapter_lib_module.load_yaml_file
_scripts_artifact_naming_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifact_naming_lib")
RECORD_PATTERN = _scripts_artifact_naming_lib_module.RECORD_PATTERN

ADAPTER_CANDIDATES = (
    Path(".agents/find-skills-adapter.yaml"),
    Path(".codex/find-skills-adapter.yaml"),
    Path(".claude/find-skills-adapter.yaml"),
    Path("docs/find-skills-adapter.yaml"),
    Path("find-skills-adapter.yaml"),
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
BOOLEAN_FIELDS = ("prefer_local_first", "allow_external_registry")
ARTIFACT_FILENAME = "latest.md"


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def _string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def _boolean(value: Any, field: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        errors.append(f"{field} must be a boolean")
        return None
    return value


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/find-skills",
        "trusted_skill_roots": [],
        "prefer_local_first": True,
        "allow_external_registry": False,
    }


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

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

    trusted_roots = _string_list(data.get("trusted_skill_roots"), "trusted_skill_roots", errors)
    legacy_roots = _string_list(data.get("official_skill_roots"), "official_skill_roots", errors)
    if trusted_roots is not None:
        validated["trusted_skill_roots"] = trusted_roots
        if legacy_roots is not None and legacy_roots != trusted_roots:
            warnings.append("Both trusted_skill_roots and official_skill_roots are set; using trusted_skill_roots.")
    elif legacy_roots is not None:
        validated["trusted_skill_roots"] = legacy_roots
        warnings.append("official_skill_roots is deprecated; rename it to trusted_skill_roots.")

    for field in BOOLEAN_FIELDS:
        value = _boolean(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["trusted_skill_roots"]:
        warnings.append("No trusted_skill_roots configured; discovery stays local-first only.")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def _bootstrap_expectations(data: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_path": _artifact_path(data["output_dir"]),
        "what_you_get_after_one_run": "A local-first capability inventory in latest.md/latest.json plus the smallest next usable path.",
        "artifact_meaning": "The artifacts show what this repo can already do today across public skills, support skills, synced support, and integrations.",
        "what_this_does_not_do": "It does not search arbitrary external registries unless trusted roots or registry access are explicitly configured.",
    }


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [candidate.as_posix() for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        data = infer_repo_defaults(repo_root)
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
                "No find-skills adapter found. Using local-first discovery defaults.",
                f"First run leaves `{_artifact_path(data['output_dir'])}` as the current capability inventory artifact.",
                "With no trusted roots configured, discovery stays inside this repo and its declared integrations only.",
                "Create .agents/find-skills-adapter.yaml to declare trusted skill roots or registry policy.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "find-skills-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path.relative_to(repo_root).as_posix()}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": adapter_path.relative_to(repo_root).as_posix(),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "bootstrap_expectations": _bootstrap_expectations(data),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="find-skills resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    try:
        args = parser.parse_args()
        sys.stdout.write(
            json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
