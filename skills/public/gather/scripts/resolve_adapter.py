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
    __file__, "scripts.adapters.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
optional_string = _scripts_adapter_lib_module.optional_string
declared_fields_after_version_check = _scripts_adapter_lib_module.declared_fields_after_version_check

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"

GATHER_PROVIDER_SOURCES = ("github", "google_workspace")
GATHER_PROVIDER_MODES = ("direct-cli", "host-mediated", "none")
DEFAULT_GATHER_PROVIDER_MODE = "none"
# Plain gather is public-source only. Credentialed organizational data (Slack,
# Notion, private Google Workspace, and similar) is NOT a gather source: it flows
# through the consuming runtime's own capability/connector surface, never a
# charness-owned provider CLI or raw token route. `github` is standard dev
# tooling that reaches public content, so it keeps `direct-cli`. Google Workspace
# has no repo-owned direct CLI; its private content is a host/runtime capability
# concern, so it defaults to `none` (stop with a missing-capability explanation)
# until an adapter opts into a `host-mediated` route.
DEFAULT_GATHER_PROVIDER_MODES = {
    "github": "direct-cli",
    "google_workspace": "none",
}


def default_gather_provider() -> dict[str, dict[str, str]]:
    return {
        source: {"mode": DEFAULT_GATHER_PROVIDER_MODES.get(source, DEFAULT_GATHER_PROVIDER_MODE)}
        for source in GATHER_PROVIDER_SOURCES
    }


def _parse_gather_provider(raw: Any, errors: list[str]) -> dict[str, dict[str, str]]:
    resolved = default_gather_provider()
    if raw is None:
        return resolved
    if not isinstance(raw, dict):
        errors.append("gather_provider must be a mapping")
        return resolved
    for source, entry in raw.items():
        if source not in GATHER_PROVIDER_SOURCES:
            errors.append(
                f"gather_provider.{source} is not a known source; allowed: {sorted(GATHER_PROVIDER_SOURCES)}"
            )
            continue
        if not isinstance(entry, dict):
            errors.append(f"gather_provider.{source} must be a mapping")
            continue
        mode = entry.get("mode")
        if mode is None:
            continue
        if not isinstance(mode, str) or mode not in GATHER_PROVIDER_MODES:
            errors.append(
                f"gather_provider.{source}.mode must be one of: {', '.join(GATHER_PROVIDER_MODES)}"
            )
            continue
        resolved[source]["mode"] = mode
    return resolved


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/gather",
        "artifact_class": ARTIFACT_CLASS,
        "gather_provider": default_gather_provider(),
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

    validated["gather_provider"] = _parse_gather_provider(data.get("gather_provider"), errors)

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "gather")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="gather",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No gather adapter found. Using default durable artifact location.",
            "Create .agents/gather-adapter.yaml to move the artifact path or record preset provenance.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="gather resolve_adapter", repo_root_help="Repo root whose gather adapter should be resolved")


if __name__ == "__main__":
    main()
