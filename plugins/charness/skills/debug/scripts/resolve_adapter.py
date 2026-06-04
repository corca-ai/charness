#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
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

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/debug",
        "artifact_class": ARTIFACT_CLASS,
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

    configured_artifact_class = data.get("artifact_class")
    if configured_artifact_class is None:
        validated["artifact_class"] = ARTIFACT_CLASS
    elif isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
        validated["artifact_class"] = configured_artifact_class
    else:
        errors.append("artifact_class must be one of: current, history, rolling")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "debug")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="debug",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No debug adapter found. Using default durable artifact location.",
            "Create .agents/debug-adapter.yaml to move the artifact path or record preset provenance.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
    )


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="debug resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for resolving the debug adapter")
    try:
        args = parser.parse_args()
        sys.stdout.write(
            json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
