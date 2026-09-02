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







_scripts_artifact_naming_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifacts.artifact_naming_lib")
ARTIFACT_CLASSES = _scripts_artifact_naming_lib_module.ARTIFACT_CLASSES
_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
optional_int = _scripts_adapter_lib_module.optional_int
optional_string = _scripts_adapter_lib_module.optional_string
declared_fields_after_version_check = _scripts_adapter_lib_module.declared_fields_after_version_check

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
# Raw FILE words, matching what `validate_debug_artifact.py` counts. Named for the
# artifact rather than for "content" because handoff's neighbouring budget excludes
# blank lines, required headings and the whole `## References` block -- one shared
# name would have meant two different measurements. Both charge WORDS now; the
# SELECTION of which text counts still differs, so the names stay apart.
WORD_BUDGET_FIELD = "max_artifact_words"
# Retired 2026-08-19 when the budget changed unit. Refused, not ignored: a dropped key
# leaves a consuming repo's declared ceiling inert under `valid: true`, and 180 read as
# a word ceiling would refuse every real artifact. The parser cannot see this class --
# a well-formed key the SCHEMA stopped reading parses perfectly.
RETIRED_BUDGET_FIELD = "max_artifact_lines"
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/debug",
        "artifact_class": ARTIFACT_CLASS,
    }


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    data = declared_fields_after_version_check(data, validated, errors)

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    # Absent means "use the validator's default"; the field is written into `validated`
    # only when the repo declared one, so the validator's `data.get` fallback stays the
    # single place the default number lives. `minimum=1` because a ceiling of 0 refuses
    # every possible artifact, including the scaffold's own stub.
    max_artifact_words = optional_int(data.get(WORD_BUDGET_FIELD), WORD_BUDGET_FIELD, errors, minimum=1)
    if max_artifact_words is not None:
        validated[WORD_BUDGET_FIELD] = max_artifact_words
    if RETIRED_BUDGET_FIELD in data:
        errors.append(
            f"`{RETIRED_BUDGET_FIELD}` was retired and is no longer read; use "
            f"`{WORD_BUDGET_FIELD}` instead. The budget now charges WORDS, not lines, "
            "because a line count measured the author's wrap width; a line ceiling "
            "cannot be converted automatically (the old bar admitted a 5.4x spread of "
            "words across this repo's own corpus), so restate the bar you want in words"
        )

    configured_artifact_class = data.get("artifact_class")
    if configured_artifact_class is None:
        validated["artifact_class"] = ARTIFACT_CLASS
    elif isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
        validated["artifact_class"] = configured_artifact_class
    else:
        errors.append("artifact_class must be one of: current, history, rolling")

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "debug")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="debug",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No debug adapter found. Using default durable artifact location.",
            "Create .agents/debug-adapter.yaml to move the artifact path or record preset provenance.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="debug resolve_adapter", repo_root_help="Repo root for resolving the debug adapter")


if __name__ == "__main__":
    main()
