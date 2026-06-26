#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()

_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
optional_string = _scripts_adapter_lib_module.optional_string
optional_string_list = _scripts_adapter_lib_module.optional_string_list

STRING_FIELDS = (
    "repo", "language", "output_dir", "preset_id", "preset_version", "customized_from",
    "package_id", "packaging_manifest_path", "checked_in_plugin_root", "sync_command",
    "quality_command", "post_publish_install_refresh", "post_publish_distinct_channel_probe",
    "requested_review_policy",
)
LIST_FIELDS = (
    "update_instructions", "real_host_required_surfaces", "real_host_required_path_globs", "real_host_checklist",
    "requested_review_commands", "review_unavailable_patterns", "review_waiver_phrases", "product_surfaces",
    "cli_skill_surface_probe_commands", "cli_skill_surface_command_docs", "cli_skill_surface_skill_paths",
    "cli_skill_surface_change_globs", "fresh_checkout_probes",
)
ARTIFACT_FILENAME = "latest.md"

_release_backend_module = SKILL_RUNTIME.load_local_skill_module(__file__, "release_backend")
default_release_backend = _release_backend_module.default_release_backend
_parse_release_backend = _release_backend_module.parse_release_backend


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    package_id = repo_root.name
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/release",
        "artifact_class": "history",
        "package_id": package_id,
        "packaging_manifest_path": f"packaging/{package_id}.json",
        "checked_in_plugin_root": f"plugins/{package_id}",
        "sync_command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
        "quality_command": "./scripts/run-quality.sh",
        "post_publish_install_refresh": "",
        "post_publish_distinct_channel_probe": "",
        "update_instructions": [],
        "real_host_required_surfaces": [],
        "real_host_required_path_globs": [],
        "real_host_checklist": [],
        "requested_review_commands": [],
        "requested_review_policy": "warn-if-unconfigured",
        "review_unavailable_patterns": [
            "review unavailable", "requested review unavailable", "review gate unavailable",
            "review skipped because", "executor_variants", "no executor_variants",
        ],
        "review_waiver_phrases": [
            "review waiver:", "explicit review waiver:", "requested review waiver:",
        ],
        "product_surfaces": [],
        "cli_skill_surface_probe_commands": [],
        "cli_skill_surface_command_docs": [],
        "cli_skill_surface_skill_paths": [],
        "cli_skill_surface_change_globs": [],
        "fresh_checkout_probes": [],
        "release_backend": default_release_backend(),
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
        value = optional_string_list(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["sync_command"]:
        errors.append("sync_command must not be empty")
    if not validated["quality_command"]:
        errors.append("quality_command must not be empty")
    if validated["requested_review_policy"] not in {"warn-if-unconfigured", "advisory-only"}:
        errors.append("requested_review_policy must be 'warn-if-unconfigured' or 'advisory-only'")

    validated["release_backend"] = _parse_release_backend(data.get("release_backend"), errors, warnings)

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "release")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="release",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No release adapter found. Using inferred packaging defaults.",
            "Create .agents/release-adapter.yaml to record the canonical packaging manifest, sync command, and user update steps.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
        artifact_class_key=None,
    )
def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="release resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to locate the release adapter")
    try:
        args = parser.parse_args()
        sys.stdout.write(json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    finally:
        cancel_timeout()
if __name__ == "__main__":
    main()
