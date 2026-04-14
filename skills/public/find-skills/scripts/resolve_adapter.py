#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
sys.path.insert(0, str(REPO_ROOT))

from scripts.adapter_lib import load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/find-skills-adapter.yaml"),
    Path(".codex/find-skills-adapter.yaml"),
    Path(".claude/find-skills-adapter.yaml"),
    Path("docs/find-skills-adapter.yaml"),
    Path("find-skills-adapter.yaml"),
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
BOOLEAN_FIELDS = ("prefer_local_first", "allow_external_registry")
ARTIFACT_FILENAME = "find-skills.md"


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
        "output_dir": "skill-outputs/find-skills",
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


def _bootstrap_expectations(data: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_path": _artifact_path(data["output_dir"]),
        "what_you_get_after_one_run": "A local-first capability inventory plus the smallest next usable path.",
        "artifact_meaning": "The artifact shows what this repo can already do today across public skills, support skills, synced support, and integrations.",
        "what_this_does_not_do": "It does not search arbitrary external registries unless trusted roots or registry access are explicitly configured.",
    }


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
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
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "bootstrap_expectations": _bootstrap_expectations(data),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    sys.stdout.write(
        json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
