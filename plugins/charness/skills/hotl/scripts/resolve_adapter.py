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

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
OPTIONAL_PATH_FIELDS = ("ledger_path", "ledger_schema", "completion_audit_command")
PROOF_COMMAND_KINDS = ("readiness", "readback", "live", "audit")
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "current"


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/hotl",
        "artifact_class": ARTIFACT_CLASS,
        "surfaces": [],
        "proof_commands": [],
    }


def _validate_proof_command(entry: Any, index: int, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        errors.append(f"proof_commands[{index}] must be a mapping")
        return None
    command_id = entry.get("id")
    command = entry.get("command")
    kind = entry.get("kind")
    if not isinstance(command_id, str) or not command_id.strip():
        errors.append(f"proof_commands[{index}].id must be a non-empty string")
        return None
    if not isinstance(command, str) or not command.strip():
        errors.append(f"proof_commands[{index}].command must be a non-empty string")
        return None
    if kind not in PROOF_COMMAND_KINDS:
        errors.append(f"proof_commands[{index}].kind must be one of: " + ", ".join(PROOF_COMMAND_KINDS))
        return None
    boundary = entry.get("boundary_reason_required", kind == "live")
    if not isinstance(boundary, bool):
        errors.append(f"proof_commands[{index}].boundary_reason_required must be a boolean")
        return None
    return {"id": command_id, "command": command, "kind": kind, "boundary_reason_required": boundary}


def _validate_proof_surface(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    surfaces = data.get("surfaces")
    if surfaces is not None:
        if isinstance(surfaces, list) and all(isinstance(item, str) and item.strip() for item in surfaces):
            validated["surfaces"] = surfaces
        else:
            errors.append("surfaces must be a list of non-empty strings")

    proof_commands = data.get("proof_commands")
    if proof_commands is not None:
        if isinstance(proof_commands, list):
            entries = [_validate_proof_command(entry, index, errors) for index, entry in enumerate(proof_commands)]
            if all(entry is not None for entry in entries):
                validated["proof_commands"] = entries
        else:
            errors.append("proof_commands must be a list of mappings")


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

    _validate_proof_surface(data, validated, errors)

    for field in OPTIONAL_PATH_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    placeholder_ids = [entry["id"] for entry in validated["proof_commands"] if "<" in entry["command"]]
    if placeholder_ids:
        warnings.append(
            "proof command(s) still carry placeholder text: "
            + ", ".join(placeholder_ids)
            + " — replace with the repo-owned invocations before citing them in a proof packet"
        )
    if not validated["proof_commands"]:
        warnings.append(
            "proof_commands is empty: live proof routes through manual action packets "
            "or `blocked-needs-capability` entries until the repo declares its proof surface"
        )

    return validated, errors, warnings


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="hotl",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No hotl adapter found. Continuing with visible inferred defaults; live proof commands stay undeclared.",
            "Create .agents/hotl-adapter.yaml to declare surfaces, proof commands, and ledger facts.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="hotl resolve_adapter", repo_root_help="Repo root whose hotl adapter should be resolved")


if __name__ == "__main__":
    main()
