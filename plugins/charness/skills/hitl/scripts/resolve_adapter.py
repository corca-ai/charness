#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_scripts_artifact_naming_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifact_naming_lib")
ARTIFACT_CLASSES = _scripts_artifact_naming_lib_module.ARTIFACT_CLASSES
_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
optional_string = _scripts_adapter_lib_module.optional_string

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from", "default_scope")
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "current"


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/hitl",
        "artifact_class": ARTIFACT_CLASS,
        "default_scope": "all",
        "chunk_target_lines": 100,
        "require_explicit_apply": True,
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
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    configured_artifact_class = data.get("artifact_class")
    if configured_artifact_class is None:
        validated["artifact_class"] = ARTIFACT_CLASS
    elif isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
        validated["artifact_class"] = configured_artifact_class
    else:
        errors.append("artifact_class must be one of: current, history, rolling")

    chunk_target_lines = data.get("chunk_target_lines")
    if chunk_target_lines is not None:
        if isinstance(chunk_target_lines, int) and chunk_target_lines > 0:
            validated["chunk_target_lines"] = chunk_target_lines
        else:
            errors.append("chunk_target_lines must be a positive integer")

    require_explicit_apply = data.get("require_explicit_apply")
    if require_explicit_apply is not None:
        if isinstance(require_explicit_apply, bool):
            validated["require_explicit_apply"] = require_explicit_apply
        else:
            errors.append("require_explicit_apply must be a boolean")

    if validated["default_scope"] not in ("all", "code", "docs"):
        errors.append("default_scope must be one of: all, code, docs")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "hitl")


def _runtime_dir(output_dir: str) -> str:
    return str(Path(".charness") / "hitl" / "runtime")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="hitl",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No hitl adapter found. Using resumable review defaults.",
            "Create .agents/hitl-adapter.yaml to record scope defaults and chunk sizing.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
        extra_payload=lambda data, _raw_data, _found: {"runtime_dir": _runtime_dir(data["output_dir"])},
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="hitl resolve_adapter", repo_root_help="Repo root whose HITL adapter should be resolved")


if __name__ == "__main__":
    main()
