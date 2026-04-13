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
    Path(".agents/announcement-adapter.yaml"),
    Path(".codex/announcement-adapter.yaml"),
    Path(".claude/announcement-adapter.yaml"),
    Path("docs/announcement-adapter.yaml"),
    Path("announcement-adapter.yaml"),
)

STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
    "product_name",
    "delivery_kind",
    "delivery_target",
    "release_notes_path",
    "post_command_template",
    "delivery_capability",
)
LIST_FIELDS = ("sections", "audience_tags", "omission_lenses")
ARTIFACT_FILENAME = "announcement.md"
RECORD_FILENAME = "announcements.jsonl"


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
        "product_name": repo_root.name,
        "language": "en",
        "output_dir": "skill-outputs/announcement",
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
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in LIST_FIELDS:
        items = _string_list(data.get(field), field, errors)
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
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_path(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_FILENAME)


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
            "field_state": {
                "audience_tags": "unset",
                "omission_lenses": "unset",
            },
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_path": _record_path(data["output_dir"]),
            "errors": [],
            "warnings": [
                "No announcement adapter found. Using draft-first defaults.",
                "Create .agents/announcement-adapter.yaml to record section order, audience tags, and human-facing delivery seams.",
            ],
            "searched_paths": searched_paths,
        }

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
        "field_state": {
            "audience_tags": _list_field_state(raw_data, "audience_tags"),
            "omission_lenses": _list_field_state(raw_data, "omission_lenses"),
        },
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_path": _record_path(data["output_dir"]),
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
