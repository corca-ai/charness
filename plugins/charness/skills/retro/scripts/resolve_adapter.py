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

ADAPTER_CANDIDATES = (
    Path(".agents/retro-adapter.yaml"),
    Path(".codex/retro-adapter.yaml"),
    Path(".claude/retro-adapter.yaml"),
    Path("docs/retro-adapter.yaml"),
    Path("retro-adapter.yaml"),
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
        "output_dir": "charness-artifacts/retro",
        "default_mode": "session",
        "weekly_window_days": 7,
        "summary_path": "charness-artifacts/retro/recent-lessons.md",
        "evidence_paths": [],
        "metrics_commands": [],
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
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in STRING_LIST_FIELDS:
        items = _string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items

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
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": infer_repo_defaults(repo_root),
            "field_state": {
                "evidence_paths": "unset",
                "metrics_commands": "unset",
                "auto_session_trigger_surfaces": "unset",
                "auto_session_trigger_path_globs": "unset",
            },
            "errors": [],
            "warnings": [
                "No retro adapter found. Session mode can proceed with inferred defaults.",
                "Create .agents/retro-adapter.yaml for weekly metrics or durable artifact policy.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "retro-adapter.yaml"
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
        "field_state": {
            "evidence_paths": _list_field_state(raw_data, "evidence_paths"),
            "metrics_commands": _list_field_state(raw_data, "metrics_commands"),
            "auto_session_trigger_surfaces": _list_field_state(raw_data, "auto_session_trigger_surfaces"),
            "auto_session_trigger_path_globs": _list_field_state(raw_data, "auto_session_trigger_path_globs"),
        },
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="retro resolve_adapter")
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
