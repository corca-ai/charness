#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, optional_string, optional_string_list
from scripts.artifact_naming_lib import RECORD_PATTERN

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
    "format_rules_path",
)
LIST_FIELDS = ("sections", "audience_tags", "omission_lenses")
INT_FIELDS = ("message_size_limit",)
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"
RECORD_FILENAME = "announcements.jsonl"

VALID_DELIVERY_ROLES = {"single", "parent", "thread_reply"}


def _list_field_state(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return "unset"
    value = data.get(field)
    if isinstance(value, list) and len(value) == 0:
        return "explicit-empty"
    return "configured"


def _validate_outputs(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("outputs must be a list of output specs")
        return None
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            errors.append(f"outputs[{index}] must be a mapping")
            continue
        output_id = raw.get("id")
        if not isinstance(output_id, str) or not output_id:
            errors.append(f"outputs[{index}].id must be a non-empty string")
            continue
        if output_id in seen_ids:
            errors.append(f"outputs[{index}].id `{output_id}` is duplicated")
            continue
        seen_ids.add(output_id)
        audience_tags = raw.get("audience_tags", [])
        if not isinstance(audience_tags, list) or not all(isinstance(item, str) for item in audience_tags):
            errors.append(f"outputs[{index}].audience_tags must be a list of strings")
            continue
        delivery_role = raw.get("delivery_role", "single")
        if delivery_role not in VALID_DELIVERY_ROLES:
            errors.append(
                f"outputs[{index}].delivery_role must be one of: {', '.join(sorted(VALID_DELIVERY_ROLES))}"
            )
            continue
        normalized.append(
            {
                "id": output_id,
                "audience_tags": list(audience_tags),
                "delivery_role": delivery_role,
            }
        )
    return normalized


def _validate_in_progress_sources(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("in_progress_sources must be a list of source specs")
        return None
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            errors.append(f"in_progress_sources[{index}] must be a mapping")
            continue
        kind = raw.get("kind")
        if kind not in {"handoff", "issues", "path"}:
            errors.append(
                f"in_progress_sources[{index}].kind must be one of: handoff, issues, path"
            )
            continue
        entry: dict[str, Any] = {"kind": kind}
        path_value = raw.get("path")
        if isinstance(path_value, str) and path_value:
            entry["path"] = path_value
        elif kind == "path":
            errors.append(f"in_progress_sources[{index}] of kind=path requires a non-empty `path`")
            continue
        query = raw.get("query")
        if isinstance(query, str) and query:
            entry["query"] = query
        normalized.append(entry)
    return normalized


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


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
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_path": _record_path(),
        "what_you_get_after_one_run": "A human-facing draft that explains recent repo value in a stable shape.",
        "artifact_meaning": "The markdown artifact is the visible announcement draft; the hidden JSONL record tracks finalized heads across runs.",
        "what_this_does_not_do": delivery_note,
    }


def _field_state_map(raw_data: dict[str, Any]) -> dict[str, str]:
    return {
        "audience_tags": _list_field_state(raw_data, "audience_tags"),
        "omission_lenses": _list_field_state(raw_data, "omission_lenses"),
        "outputs": _list_field_state(raw_data, "outputs"),
        "in_progress_sources": _list_field_state(raw_data, "in_progress_sources"),
    }


def infer_announcement_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "product_name": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/announcement",
        "artifact_class": ARTIFACT_CLASS,
        "sections": ["Highlights", "Changes", "Fixes"],
        "audience_tags": [],
        "omission_lenses": [],
        "in_progress_sources": [],
        "delivery_kind": "none",
        "delivery_target": "",
        "release_notes_path": "",
        "post_command_template": "",
        "delivery_capability": "",
        "format_rules_path": "",
        "message_size_limit": 0,
        "outputs": [],
    }


def _apply_simple_fields(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> None:
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
    for field in INT_FIELDS:
        raw_value = data.get(field)
        if raw_value is None:
            continue
        if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value < 0:
            errors.append(f"{field} must be a non-negative integer (0 disables splitting)")
            continue
        validated[field] = raw_value


def _apply_structured_fields(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> None:
    outputs = _validate_outputs(data.get("outputs"), errors)
    if outputs is not None:
        validated["outputs"] = outputs
    in_progress_sources = _validate_in_progress_sources(data.get("in_progress_sources"), errors)
    if in_progress_sources is not None:
        validated["in_progress_sources"] = in_progress_sources


def _delivery_warnings(
    data: dict[str, Any], validated: dict[str, Any], warnings: list[str], errors: list[str]
) -> None:
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


def validate_announcement_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_announcement_defaults(repo_root)
    _apply_simple_fields(data, validated, errors)
    _apply_structured_fields(data, validated, errors)
    _delivery_warnings(data, validated, warnings, errors)
    return validated, errors, warnings


def load_announcement_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        data = infer_announcement_defaults(repo_root)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "field_state": _field_state_map({}),
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_class": data["artifact_class"],
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
            "record_path": _record_path(),
            "bootstrap_expectations": _bootstrap_expectations(data),
            "errors": [],
            "warnings": [
                "No announcement adapter found. Using draft-first defaults.",
                f"First run leaves `{_artifact_path(data['output_dir'])}` as the visible draft artifact.",
                f"`{_record_path()}` only advances after explicit draft finalization or delivery.",
                "delivery_kind defaults to `none`, so bootstrap is intentionally draft-only until a repo chooses a backend seam.",
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
    data, errors, extra_warnings = validate_announcement_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "field_state": _field_state_map(raw_data),
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_class": data["artifact_class"],
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
        "record_path": _record_path(),
        "bootstrap_expectations": _bootstrap_expectations(data),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
