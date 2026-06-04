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







_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract

STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
)
STRING_LIST_FIELDS = (
    "verification_tools",
    "ui_verification_tools",
    "verification_install_proposals",
    "truth_surfaces",
)


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


def _list_field_state(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return "unset"
    value = data.get(field)
    if isinstance(value, list) and len(value) == 0:
        return "explicit-empty"
    return "configured"


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/impl",
        "verification_tools": [],
        "ui_verification_tools": [],
        "verification_install_proposals": [],
        "truth_surfaces": [],
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

    for field in STRING_LIST_FIELDS:
        items = _string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    if not validated.get("verification_tools"):
        warnings.append("No verification_tools configured; impl bootstrap must survey repo-local proof paths manually")
    if not validated.get("ui_verification_tools"):
        warnings.append("No ui_verification_tools configured; UI work may rely on weaker generic browser-path discovery")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "impl")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="impl",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No impl adapter found. Using inferred defaults and manual verification discovery.",
            "Create .agents/impl-adapter.yaml to record repo-preferred self-verification tools.",
        ),
        extra_payload=lambda _data, raw_data, _found: {
            "field_state": {
                "verification_tools": _list_field_state(raw_data, "verification_tools"),
                "ui_verification_tools": _list_field_state(raw_data, "ui_verification_tools"),
                "verification_install_proposals": _list_field_state(raw_data, "verification_install_proposals"),
                "truth_surfaces": _list_field_state(raw_data, "truth_surfaces"),
            }
        },
    )


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="impl resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for resolving the impl adapter")
    try:
        args = parser.parse_args()
        sys.stdout.write(
            json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
