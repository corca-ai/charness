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







_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
list_field_state = _scripts_adapter_lib_module.list_field_state
optional_string = _scripts_adapter_lib_module.optional_string
optional_string_list = _scripts_adapter_lib_module.optional_string_list
_scripts_critique_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.critique_adapter_lib"
)

STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
    "default_mode",
    "snapshot_path",
    "summary_path",
)
STRING_LIST_FIELDS = (
    "evidence_paths",
    "metrics_commands",
    "auto_session_trigger_surfaces",
    "auto_session_trigger_path_globs",
)


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/retro",
        "default_mode": "session",
        "weekly_window_days": 7,
        "summary_path": "charness-artifacts/retro/recent-lessons.md",
        "evidence_paths": [],
        "metrics_commands": [],
        "packet_sections": [],
        "auto_session_trigger_surfaces": [],
        "auto_session_trigger_path_globs": [],
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

    for field in STRING_LIST_FIELDS:
        items = optional_string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items

    sections_raw = data.get("packet_sections")
    if sections_raw is not None:
        packet_data, packet_errors, _packet_warnings = (
            _scripts_critique_adapter_lib_module.validate_adapter_data(
                {"version": 1, "packet_sections": sections_raw}, repo_root
            )
        )
        errors.extend(packet_errors)
        validated["packet_sections"] = packet_data.get("packet_sections", [])

    window = data.get("weekly_window_days")
    if window is not None:
        if isinstance(window, int) and window > 0:
            validated["weekly_window_days"] = window
        else:
            errors.append("weekly_window_days must be a positive integer")

    if validated["default_mode"] not in ("session", "weekly", "auto"):
        errors.append("default_mode must be one of: session, weekly, auto")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    if not validated.get("metrics_commands"):
        warnings.append("No metrics_commands configured; weekly retros may stay narrative-only")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "retro")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="retro",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No retro adapter found. Session mode can proceed with inferred defaults.",
            "Create .agents/retro-adapter.yaml for weekly metrics or durable artifact policy.",
        ),
        extra_payload=lambda _data, raw_data, _found: {
            "field_state": {
                "evidence_paths": list_field_state(raw_data, "evidence_paths"),
                "metrics_commands": list_field_state(raw_data, "metrics_commands"),
                "packet_sections": list_field_state(raw_data, "packet_sections"),
                "auto_session_trigger_surfaces": list_field_state(raw_data, "auto_session_trigger_surfaces"),
                "auto_session_trigger_path_globs": list_field_state(raw_data, "auto_session_trigger_path_globs"),
            }
        },
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="retro resolve_adapter", repo_root_help="Repo root to load the retro adapter from")


if __name__ == "__main__":
    main()
