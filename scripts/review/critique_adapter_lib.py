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


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    declared_fields_after_version_check,
    optional_string,
    resolve_adapter_payload,
)

DEFAULT_OUTPUT_DIR = "charness-artifacts/critique"
ADAPTER_CANDIDATES = (
    Path(".agents/critique-adapter.yaml"),
)
STRING_FIELDS = ("repo", "language", "output_dir")
VALID_CONTENT_KINDS = ("static", "script")
VALID_REVIEWER_TIERS = ("high-leverage", "medium", "standard")
REVIEWER_TIER_FIELDS = ("model", "reasoning_effort", "service_tier", "fork_turns")
VALID_REVIEWER_RUNNER_MODES = ("file-backed-worker", "typed-subagent")
VALID_REVIEWER_BACKENDS = ("codex_exec", "claude_p", "host-defaulted")
REVIEWER_RUNNER_FIELDS = ("mode", "backend", "timeout_seconds")


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": DEFAULT_OUTPUT_DIR,
        "packet_sections": [],
        "reviewer_runner": {
            "mode": "file-backed-worker",
            "backend": "host-defaulted",
            "timeout_seconds": 900,
        },
    }


def _validate_section_identity(
    raw: dict[str, Any],
    *,
    field: str,
    seen_ids: set[str],
    errors: list[str],
) -> dict[str, Any]:
    section: dict[str, Any] = {}
    section_id = optional_string(raw.get("id"), f"{field}.id", errors)
    if section_id is None:
        errors.append(f"{field}.id is required")
    else:
        if section_id in seen_ids:
            errors.append(f"{field}.id duplicates earlier section `{section_id}`")
        else:
            seen_ids.add(section_id)
        section["id"] = section_id
    title = optional_string(raw.get("title"), f"{field}.title", errors)
    if title is None:
        errors.append(f"{field}.title is required")
    else:
        section["title"] = title
    return section


def _validate_section_kind(
    raw: dict[str, Any], *, field: str, errors: list[str]
) -> str | None:
    content_kind = optional_string(raw.get("content_kind"), f"{field}.content_kind", errors)
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
        command = optional_string(raw.get("command"), f"{field}.command", errors)
        if not command:
            errors.append(f"{field}.command must be a non-empty string")
            return None
        return {"command": command}
    if populated == "content_path":
        content_path = optional_string(raw.get("content_path"), f"{field}.content_path", errors)
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
            text = optional_string(value, f"{field}.{key}", errors)
            if text is not None:
                entry[key] = text
        tiers[name] = entry
    return tiers


def _validate_reviewer_runner(raw: Any, *, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        errors.append("reviewer_runner must be a mapping")
        return None
    for key in sorted(set(raw) - set(REVIEWER_RUNNER_FIELDS)):
        errors.append(
            f"reviewer_runner.{key} is not a valid runner field "
            f"({', '.join(REVIEWER_RUNNER_FIELDS)})"
        )
    mode = optional_string(raw.get("mode"), "reviewer_runner.mode", errors)
    backend = optional_string(raw.get("backend"), "reviewer_runner.backend", errors)
    timeout = raw.get("timeout_seconds", 900)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        errors.append("reviewer_runner.timeout_seconds must be a positive integer")
        timeout = 900
    if mode is not None and mode not in VALID_REVIEWER_RUNNER_MODES:
        errors.append(
            f"reviewer_runner.mode must be one of: {', '.join(VALID_REVIEWER_RUNNER_MODES)}"
        )
    if backend is not None and backend not in VALID_REVIEWER_BACKENDS:
        errors.append(
            f"reviewer_runner.backend must be one of: {', '.join(VALID_REVIEWER_BACKENDS)}"
        )
    return {
        "mode": mode or "file-backed-worker",
        "backend": backend or "host-defaulted",
        "timeout_seconds": timeout,
    }


def validate_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    data = declared_fields_after_version_check(data, validated, errors)

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
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

    runner_raw = data.get("reviewer_runner")
    if runner_raw is not None:
        runner = _validate_reviewer_runner(runner_raw, errors=errors)
        if runner is not None:
            validated["reviewer_runner"] = runner

    # Repo-owned cross-surface probe for the boundary-ownership checkpoint
    # (#408). The critique validator's severity upgrade reads these through this
    # one adapter. Keys mirror scripts/evidence/boundary_probe_lib.py
    # (BOUNDARY_GLOBS_KEY / BOUNDARY_SURFACES_KEY).
    for key in ("boundary_cross_surface_globs", "boundary_cross_surface_surfaces"):
        raw_list = data.get(key)
        if raw_list is None:
            continue
        # `[]` is the explicit-empty spelling, and it is the ONLY one. A bare `key:`
        # parses to an empty MAPPING, which is deliberately refused here: the parser
        # also renders `key:` followed by dash-less children as `{}` (each child has no
        # mapping separator, so it is silently dropped), and accepting `{}` as an
        # opt-out would read a probe config the author clearly meant to declare as a
        # deliberate "no probe" -- exit 0 over a broken config, which is the defect this
        # whole surface exists to remove. Measured: `list_field_state` classifies `{}`
        # as `configured` and only `[]` as `explicit-empty`, and this repo's own adapter
        # spells the empty declaration `boundary_cross_surface_surfaces: []`.
        if isinstance(raw_list, list) and all(isinstance(item, str) for item in raw_list):
            validated[key] = list(raw_list)
        else:
            errors.append(f"{key} must be a list of strings")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def load_adapter(repo_root: Path) -> dict[str, Any]:
    # `resolve_adapter_payload`, NOT a hand-written pair of branches around
    # `load_yaml_file`. The bare loader RAISES on a document the parser refuses and DISCARDS
    # the uninterpreted-line sink, so `parse_refused` and `declarations_dropped` were both
    # structurally dead for this skill's consumers (#673).
    return resolve_adapter_payload(
        repo_root,
        candidates=ADAPTER_CANDIDATES,
        infer_defaults=infer_repo_defaults,
        validate=validate_adapter_data,
        absent_warnings=lambda _data: [
            "No critique adapter found. The prepare-packet contract is opt-in;"
            " critique runs with inferred defaults and no packet consumption.",
        ],
    )


def adapter_has_sections(adapter: dict[str, Any]) -> bool:
    """The opt-in signal: at least one declared packet section."""
    sections = adapter.get("data", {}).get("packet_sections", [])
    return bool(sections)
