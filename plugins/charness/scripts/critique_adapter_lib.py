"""Critique adapter loader + validator.

The adapter is optional. Without it, `critique` runs with inferred
defaults and consumes no prepare packet. With one or more
`packet_sections` declared, the prepare runner becomes the consumer
contract for fresh-eye reviewers.

Schema lives in
`skills/public/critique/references/adapter-contract.md`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file

DEFAULT_OUTPUT_DIR = "charness-artifacts/critique"
ADAPTER_CANDIDATES = (
    Path(".agents/critique-adapter.yaml"),
    Path(".codex/critique-adapter.yaml"),
    Path(".claude/critique-adapter.yaml"),
    Path("docs/critique-adapter.yaml"),
    Path("critique-adapter.yaml"),
)
STRING_FIELDS = ("repo", "language", "output_dir")
VALID_CONTENT_KINDS = ("static", "script")
VALID_REVIEWER_TIERS = ("high-leverage", "standard")
REVIEWER_TIER_FIELDS = ("model", "reasoning_effort", "service_tier")


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
        "output_dir": DEFAULT_OUTPUT_DIR,
        "packet_sections": [],
    }


def _validate_section_identity(
    raw: dict[str, Any],
    *,
    field: str,
    seen_ids: set[str],
    errors: list[str],
) -> dict[str, Any]:
    section: dict[str, Any] = {}
    section_id = _string(raw.get("id"), f"{field}.id", errors)
    if section_id is None:
        errors.append(f"{field}.id is required")
    else:
        if section_id in seen_ids:
            errors.append(f"{field}.id duplicates earlier section `{section_id}`")
        else:
            seen_ids.add(section_id)
        section["id"] = section_id
    title = _string(raw.get("title"), f"{field}.title", errors)
    if title is None:
        errors.append(f"{field}.title is required")
    else:
        section["title"] = title
    return section


def _validate_section_kind(
    raw: dict[str, Any], *, field: str, errors: list[str]
) -> str | None:
    content_kind = _string(raw.get("content_kind"), f"{field}.content_kind", errors)
    if content_kind is None:
        errors.append(f"{field}.content_kind is required")
        return None
    if content_kind not in VALID_CONTENT_KINDS:
        errors.append(
            f"{field}.content_kind must be one of: {', '.join(VALID_CONTENT_KINDS)}"
        )
        return None
    return content_kind


def _validate_section_payload(
    raw: dict[str, Any],
    *,
    field: str,
    content_kind: str | None,
    errors: list[str],
) -> dict[str, Any] | None:
    populated_fields = [name for name in ("content", "content_path", "command") if name in raw]
    if len(populated_fields) != 1:
        errors.append(
            f"{field} must declare exactly one of `content`, `content_path`, `command`; "
            f"got {populated_fields or 'none'}"
        )
        return None
    populated = populated_fields[0]
    if content_kind == "script" and populated != "command":
        errors.append(f"{field}.content_kind=script requires `command`, not `{populated}`")
        return None
    if content_kind == "static" and populated == "command":
        errors.append(f"{field}.content_kind=static requires `content` or `content_path`, not `command`")
        return None
    if populated == "command":
        command = _string(raw.get("command"), f"{field}.command", errors)
        if not command:
            errors.append(f"{field}.command must be a non-empty string")
            return None
        return {"command": command}
    if populated == "content_path":
        content_path = _string(raw.get("content_path"), f"{field}.content_path", errors)
        if not content_path:
            errors.append(f"{field}.content_path must be a non-empty string")
            return None
        return {"content_path": content_path}
    content = raw.get("content")
    if isinstance(content, str):
        return {"content": content}
    if isinstance(content, list) and all(isinstance(item, str) for item in content):
        return {"content": "\n".join(content)}
    errors.append(f"{field}.content must be a string or list of strings")
    return None


def _validate_section(
    raw: Any,
    *,
    index: int,
    seen_ids: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    field = f"packet_sections[{index}]"
    if not isinstance(raw, dict):
        errors.append(f"{field} must be a mapping")
        return None
    section = _validate_section_identity(raw, field=field, seen_ids=seen_ids, errors=errors)
    content_kind = _validate_section_kind(raw, field=field, errors=errors)
    if content_kind is not None:
        section["content_kind"] = content_kind
    payload = _validate_section_payload(raw, field=field, content_kind=content_kind, errors=errors)
    if payload is None:
        return None
    section.update(payload)
    return section


def _validate_reviewer_tiers(
    raw: Any, *, errors: list[str], warnings: list[str]
) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        errors.append("reviewer_tiers must be a mapping")
        return None
    tiers: dict[str, Any] = {}
    for name, spec in raw.items():
        field = f"reviewer_tiers.{name}"
        if not isinstance(spec, dict):
            errors.append(f"{field} must be a mapping")
            continue
        if name not in VALID_REVIEWER_TIERS:
            warnings.append(
                f"{field} is not a known reviewer tier "
                f"({', '.join(VALID_REVIEWER_TIERS)})"
            )
        entry: dict[str, str] = {}
        for key, value in spec.items():
            if key not in REVIEWER_TIER_FIELDS:
                errors.append(
                    f"{field}.{key} is not a valid reviewer-tier field "
                    f"({', '.join(REVIEWER_TIER_FIELDS)})"
                )
                continue
            text = _string(value, f"{field}.{key}", errors)
            if text is not None:
                entry[key] = text
        tiers[name] = entry
    return tiers


def validate_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
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

    sections_raw = data.get("packet_sections")
    if sections_raw is None:
        pass
    elif not isinstance(sections_raw, list):
        errors.append("packet_sections must be a list")
    else:
        seen_ids: set[str] = set()
        sections: list[dict[str, Any]] = []
        for index, raw_section in enumerate(sections_raw):
            section = _validate_section(
                raw_section, index=index, seen_ids=seen_ids, errors=errors
            )
            if section is not None:
                sections.append(section)
        validated["packet_sections"] = sections

    tiers_raw = data.get("reviewer_tiers")
    if tiers_raw is not None:
        tiers = _validate_reviewer_tiers(tiers_raw, errors=errors, warnings=warnings)
        if tiers is not None:
            validated["reviewer_tiers"] = tiers

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

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
            "errors": [],
            "warnings": [
                "No critique adapter found. The prepare-packet contract is opt-in;"
                " critique runs with inferred defaults and no packet consumption.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    canonical = repo_root / ".agents" / "critique-adapter.yaml"
    if adapter_path.resolve() != canonical.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def adapter_has_sections(adapter: dict[str, Any]) -> bool:
    """The opt-in signal: at least one declared packet section."""
    sections = adapter.get("data", {}).get("packet_sections", [])
    return bool(sections)
