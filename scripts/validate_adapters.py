#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_adapter_lib_module = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _scripts_adapter_lib_module.load_yaml_file
_scripts_cautilus_adapter_lib_module = import_repo_module(__file__, "scripts.cautilus_adapter_lib")
load_cautilus_adapter = _scripts_cautilus_adapter_lib_module.load_cautilus_adapter
_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files


class ValidationError(Exception):
    pass


CHARNESS_QUALITY_ADAPTER_REQUIRED_FIELDS = (
    "product_surfaces",
    "cli_skill_surface_probe_commands",
    "cli_skill_surface_command_docs",
    "cli_skill_surface_change_globs",
    "canonical_markdown_surfaces",
    "runtime_profile_default",
    "runtime_budget_profiles",
    "startup_probes",
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)


def expected_artifact_filename(skill_id: str) -> str:
    return current_artifact_filename(skill_id)


def validate_resolver(path: Path, root: Path) -> None:
    skill_id = path.parent.parent.name
    completed = subprocess.run(
        ["python3", str(path), "--repo-root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValidationError(f"{path}: exited with code {completed.returncode}: {completed.stderr.strip()}")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: did not emit valid JSON") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{path}: JSON output must be an object")
    if data.get("valid") is not True:
        raise ValidationError(f"{path}: expected `valid=true`, got {data.get('valid')!r}")

    expected_filename = expected_artifact_filename(skill_id)
    actual_filename = data.get("artifact_filename")
    if actual_filename is not None and actual_filename != expected_filename:
        raise ValidationError(
            f"{path}: expected artifact_filename `{expected_filename}`, got `{actual_filename}`"
        )

    artifact_path = data.get("artifact_path")
    if artifact_path is not None and not artifact_path.endswith(expected_filename):
        raise ValidationError(
            f"{path}: artifact_path must end with `{expected_filename}`, got `{artifact_path}`"
        )


def iter_resolvers(root: Path) -> list[Path]:
    return iter_matching_repo_files(root, ("skills/public/*/scripts/resolve_adapter.py",))


def iter_adapter_yaml(root: Path) -> list[Path]:
    return iter_matching_repo_files(root, (".agents/*-adapter.yaml", ".agents/cautilus-adapters/*.yaml"))


def validate_charness_quality_adapter_contract(path: Path, data: dict) -> None:
    if path.name != "quality-adapter.yaml" or path.parent.name != ".agents" or data.get("repo") != "charness":
        return

    missing = [field for field in CHARNESS_QUALITY_ADAPTER_REQUIRED_FIELDS if field not in data]
    if missing:
        rendered = ", ".join(f"`{field}`" for field in missing)
        raise ValidationError(f"{path}: mature charness quality adapter must explicitly declare {rendered}")

    product_surfaces = data.get("product_surfaces")
    if not isinstance(product_surfaces, list) or not {"installable_cli", "bundled_skill"}.issubset(product_surfaces):
        raise ValidationError(
            f"{path}: product_surfaces must explicitly include `installable_cli` and `bundled_skill`"
        )

    canonical_surfaces = data.get("canonical_markdown_surfaces")
    required_surfaces = {"AGENTS.md", "CLAUDE.md", "docs/handoff.md"}
    if not isinstance(canonical_surfaces, list) or not required_surfaces.issubset(canonical_surfaces):
        raise ValidationError(
            f"{path}: canonical_markdown_surfaces must explicitly include AGENTS.md, CLAUDE.md, and docs/handoff.md"
        )

    runtime_profiles = data.get("runtime_budget_profiles")
    if not isinstance(runtime_profiles, dict) or "local-linux-aarch64-4cpu" not in runtime_profiles:
        raise ValidationError(
            f"{path}: runtime_budget_profiles must explicitly include `local-linux-aarch64-4cpu`"
        )

    for field in (
        "cli_skill_surface_probe_commands",
        "cli_skill_surface_command_docs",
        "cli_skill_surface_change_globs",
        "startup_probes",
        "preflight_commands",
        "gate_commands",
        "review_commands",
        "security_commands",
    ):
        if not isinstance(data.get(field), list) or not data[field]:
            raise ValidationError(f"{path}: `{field}` must be an explicit non-empty list")


def validate_adapter_yaml(path: Path) -> None:
    if path.name == "cautilus-adapter.yaml" and path.parent.name == ".agents":
        payload = load_cautilus_adapter(path.parent.parent.resolve())
        if not payload["valid"]:
            raise ValidationError(f"{path}: {'; '.join(payload['errors'])}")
        return
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: adapter YAML must parse to a mapping")
    version = data.get("version")
    if not isinstance(version, int) or version < 1:
        raise ValidationError(f"{path}: `version` must be a positive integer")
    repo = data.get("repo")
    if not isinstance(repo, str) or not repo:
        raise ValidationError(f"{path}: `repo` must be a non-empty string")
    validate_charness_quality_adapter_contract(path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    resolvers = iter_resolvers(root)
    adapter_yaml = iter_adapter_yaml(root)
    if not resolvers and not adapter_yaml:
        print("No adapter surfaces found.")
        return 0

    for resolver in resolvers:
        validate_resolver(resolver, root)
    for path in adapter_yaml:
        validate_adapter_yaml(path)

    print(f"Validated {len(resolvers)} adapter resolvers and {len(adapter_yaml)} adapter YAML file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
