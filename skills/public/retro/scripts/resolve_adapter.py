#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path, PurePosixPath
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
string_field_state = _scripts_adapter_lib_module.string_field_state
declared_fields_after_version_check = _scripts_adapter_lib_module.declared_fields_after_version_check
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
    "summary_path",
)
STRING_LIST_FIELDS = (
    "evidence_paths",
    "metrics_commands",
    "artifact_sections",
    "auto_session_trigger_surfaces",
    "auto_session_trigger_path_globs",
)


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/retro",
        "summary_path": "charness-artifacts/retro/recent-lessons.md",
        "evidence_paths": [],
        "metrics_commands": [],
        "artifact_sections": [],
        "packet_sections": [],
        "auto_session_trigger_surfaces": [],
        "auto_session_trigger_path_globs": [],
    }


def canonicalize_output_dir(validated: dict[str, Any], errors: list[str]) -> None:
    """Give `output_dir` ONE canonical spelling, in place.

    Owned here because both consumers read the value from here and neither can
    normalise for the other. The scaffold builds its write path with a raw f-string
    (`f"{output_dir}/{date}-{slug}.md"`) while the validator derives its prefix through
    a `Path`. For any non-canonical value the two silently disagreed:
    `charness-artifacts/retro/` made the scaffold emit `charness-artifacts/retro//x.md`,
    whose tail then held a `/` and was dropped as a nested archive -- `Validated 0 retro
    artifact(s).` and exit 0 over a path the caller NAMED. `./x` and `x//y` diverged the
    same way. Normalising once, before either side sees the value, removes the class;
    refusing instead would break consumers whose adapters are merely untidy.

    An absolute or repo-escaping directory IS refused, because every consumer joins this
    value to the repo root: a value resolving outside cannot be made to mean anything,
    and falling back silently would validate a directory the repo never declared.
    """
    output_dir = validated.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir.strip():
        return
    normalized = PurePosixPath(output_dir.strip()).as_posix().rstrip("/")
    if not normalized or normalized.startswith(("/", "..")):
        errors.append(f"output_dir must be a repo-relative directory; got {output_dir!r}")
        return
    validated["output_dir"] = normalized


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    data = declared_fields_after_version_check(data, validated, errors)

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    # `summary_path: null` is an OPT-OUT, not an omission. A consumer whose
    # lesson ledger is the sole surface could not decline the Markdown projection:
    # the contract called the field optional, but omitting it and nulling it both
    # resolved to the same default, so the next retro silently recreated a second
    # lesson owner the repo had deliberately removed. An empty string is not the
    # spelling -- it stays a string and resolves to the repository root.
    if string_field_state(data, "summary_path") == "explicit-null":
        validated["summary_path"] = None

    canonicalize_output_dir(validated, errors)

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

    # `weekly_window_days`, `default_mode`, and `snapshot_path` were retired with the
    # weekly mode. A consumer adapter that still carries them is not an error: unknown
    # keys pass through ignored, so an upgrade never breaks a stale adapter.

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    if not validated.get("metrics_commands"):
        warnings.append("No metrics_commands configured; the retro may stay narrative-only")

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
            "No retro adapter found. The retro can proceed with inferred defaults.",
            "Create .agents/retro-adapter.yaml for metrics or durable artifact policy.",
        ),
        extra_payload=lambda _data, raw_data, _found: {
            "field_state": {
                "summary_path": string_field_state(raw_data, "summary_path"),
                "evidence_paths": list_field_state(raw_data, "evidence_paths"),
                "metrics_commands": list_field_state(raw_data, "metrics_commands"),
                "artifact_sections": list_field_state(raw_data, "artifact_sections"),
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
