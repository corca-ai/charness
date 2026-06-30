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

_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file
list_field_state = _adapter_lib.list_field_state
optional_string = _adapter_lib.optional_string
optional_string_list = _adapter_lib.optional_string_list

ADAPTER_CANDIDATES = (
    Path(".agents/create-skill-adapter.yaml"),
    Path(".codex/create-skill-adapter.yaml"),
    Path(".claude/create-skill-adapter.yaml"),
    Path("docs/create-skill-adapter.yaml"),
    Path("create-skill-adapter.yaml"),
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
STRING_LIST_FIELDS = (
    "implementation_identity_terms",
    "placement_terms",
    "intentional_fork_signals",
    "topology_verification_hints",
)
HOST_EXTENSION_FIELD = "host_extensions"
SUPPORTED_VERSION = 1
KNOWN_FIELDS = ("version", *STRING_FIELDS, *STRING_LIST_FIELDS, HOST_EXTENSION_FIELD)


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/create-skill",
        "implementation_identity_terms": [],
        "placement_terms": [],
        "intentional_fork_signals": [],
        "topology_verification_hints": [],
        HOST_EXTENSION_FIELD: {},
    }


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            if version == SUPPORTED_VERSION:
                validated["version"] = version
            else:
                errors.append(f"version must be {SUPPORTED_VERSION}")
        else:
            errors.append("version must be an integer")

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in STRING_LIST_FIELDS:
        value = optional_string_list(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if HOST_EXTENSION_FIELD in data:
        value = data[HOST_EXTENSION_FIELD]
        if isinstance(value, dict):
            validated[HOST_EXTENSION_FIELD] = value
        else:
            errors.append(f"{HOST_EXTENSION_FIELD} must be a mapping")

    for field, value in data.items():
        if isinstance(field, str) and field.startswith("x-"):
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    if not validated["implementation_identity_terms"]:
        warnings.append("No implementation_identity_terms configured; use generic implementation identity wording.")
    if not validated["topology_verification_hints"]:
        warnings.append("No topology_verification_hints configured; report topology using generic shared-vs-fork wording.")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)


def _field_state(data: dict[str, Any]) -> dict[str, str]:
    state = {field: list_field_state(data, field) for field in STRING_LIST_FIELDS}
    if HOST_EXTENSION_FIELD in data:
        state[HOST_EXTENSION_FIELD] = "explicit-empty" if data.get(HOST_EXTENSION_FIELD) == {} else "configured"
    else:
        state[HOST_EXTENSION_FIELD] = "unset"
    return state


def _mapping_shape_error(adapter_path: Path, data: dict[str, Any]) -> str | None:
    meaningful_lines = [
        line.strip()
        for line in adapter_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not meaningful_lines:
        return "adapter file is empty; expected a create-skill adapter mapping"
    if meaningful_lines[0].startswith("- "):
        return "adapter file must contain a top-level mapping, not a list"
    if not data:
        return "adapter file did not contain supported create-skill adapter mapping entries"
    if not any(field in data for field in KNOWN_FIELDS) and not any(
        isinstance(field, str) and field.startswith("x-") for field in data
    ):
        return "adapter file did not contain recognized create-skill adapter fields"
    return None


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
            "field_state": _field_state({}),
            "errors": [],
            "warnings": [
                "No create-skill adapter found. Using generic topology vocabulary.",
                "Create .agents/create-skill-adapter.yaml to record repo-owned skill topology terms.",
                'Run python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . to scaffold one.',
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    errors: list[str] = []
    canonical_path = repo_root / ".agents" / "create-skill-adapter.yaml"
    shape_error = _mapping_shape_error(adapter_path, raw_data)
    if shape_error is not None:
        errors.append(shape_error)
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, validation_errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    errors.extend(validation_errors)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "field_state": _field_state(raw_data),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="create-skill resolve_adapter", repo_root_help="Repo root for resolving the create-skill adapter")


if __name__ == "__main__":
    main()
