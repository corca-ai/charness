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
optional_string = _scripts_adapter_lib_module.optional_string
optional_string_list = _scripts_adapter_lib_module.optional_string_list
_scripts_artifact_naming_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifact_naming_lib")
RECORD_PATTERN = _scripts_artifact_naming_lib_module.RECORD_PATTERN

ADAPTER_CANDIDATES = (
    Path(".agents/announcement-adapter.yaml"),
    Path(".codex/announcement-adapter.yaml"),
    Path(".claude/announcement-adapter.yaml"),
    Path("docs/announcement-adapter.yaml"),
    Path("announcement-adapter.yaml"),
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from", "product_name", "delivery_kind", "delivery_target", "release_notes_path", "post_command_template", "delivery_capability")
LIST_FIELDS = ("sections", "audience_tags", "omission_lenses")
ARTIFACT_FILENAME = "latest.md"
RECORD_FILENAME = "announcements.jsonl"


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
        "product_name": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/announcement",
        "sections": ["Highlights", "Changes", "Fixes"],
        "audience_tags": [],
        "omission_lenses": [],
        "delivery_kind": "none",
        "delivery_target": "",
        "release_notes_path": "",
        "post_command_template": "",
        "delivery_capability": "",
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

    for field in LIST_FIELDS:
        items = optional_string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items

    if validated["delivery_kind"] == "command":
        validated["delivery_kind"] = "human-backend"
        warnings.append("delivery_kind `command` is deprecated; rename it to `human-backend`.")

    if validated["delivery_kind"] not in ("none", "release-notes", "human-backend"):
        errors.append("delivery_kind must be one of: none, release-notes, human-backend")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["audience_tags"]:
        warnings.append("No audience_tags configured; drafts will omit audience prefixes.")
    if validated["delivery_kind"] == "release-notes" and not validated["release_notes_path"]:
        warnings.append("release-notes delivery_kind is set but release_notes_path is empty.")
    if validated["delivery_kind"] == "human-backend" and not validated["post_command_template"]:
        warnings.append("human-backend delivery_kind is set but post_command_template is empty.")
    if validated["delivery_kind"] == "human-backend" and not validated["delivery_capability"]:
        warnings.append("human-backend delivery_kind is set but delivery_capability is empty.")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return next((path for candidate in ADAPTER_CANDIDATES if (path := repo_root / candidate).is_file()), None)


def _output_path(output_dir: str, filename: str) -> str:
    return str(Path(output_dir) / filename)


def _record_path() -> str:
    return str(Path(".charness") / "announcement" / RECORD_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def _bootstrap_expectations(data: dict[str, Any]) -> dict[str, str]:
    delivery_note = (
        "Delivery stays draft-only until the adapter declares a backend and the user confirms posting."
        if data["delivery_kind"] == "none"
        else "Delivery still requires explicit user confirmation even when the adapter declares a backend."
    )
    return {
        "artifact_path": _output_path(data["output_dir"], ARTIFACT_FILENAME),
        "record_path": _record_path(),
        "what_you_get_after_one_run": "A human-facing draft that explains recent repo value in a stable shape.",
        "artifact_meaning": "The markdown artifact is the visible announcement draft; the hidden JSONL record tracks finalized heads across runs.",
        "what_this_does_not_do": delivery_note,
    }


def _field_state_map(raw_data: dict[str, Any]) -> dict[str, str]:
    return {"audience_tags": _list_field_state(raw_data, "audience_tags"), "omission_lenses": _list_field_state(raw_data, "omission_lenses")}


def _missing_adapter_payload(data: dict[str, Any], searched_paths: list[str]) -> dict[str, Any]:
    return {
        "found": False,
        "valid": True,
        "path": None,
        "data": data,
        "field_state": _field_state_map({}),
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _output_path(data["output_dir"], ARTIFACT_FILENAME),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "record_path": _record_path(),
        "bootstrap_expectations": _bootstrap_expectations(data),
        "errors": [],
        "warnings": [
            "No announcement adapter found. Using draft-first defaults.",
            f"First run leaves `{_output_path(data['output_dir'], ARTIFACT_FILENAME)}` as the visible draft artifact.",
            f"`{_record_path()}` only advances after explicit draft finalization or delivery.",
            "delivery_kind defaults to `none`, so bootstrap is intentionally draft-only until a repo chooses a backend seam.",
            "Create .agents/announcement-adapter.yaml to record section order, audience tags, and human-facing delivery seams.",
        ],
        "searched_paths": searched_paths,
    }


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        data = infer_repo_defaults(repo_root)
        return _missing_adapter_payload(data, searched_paths)

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "announcement-adapter.yaml"
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
        "field_state": _field_state_map(raw_data),
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _output_path(data["output_dir"], ARTIFACT_FILENAME),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "record_path": _record_path(),
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
