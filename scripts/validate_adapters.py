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
_scripts_critique_adapter_lib_module = import_repo_module(__file__, "scripts.critique_adapter_lib")
load_critique_adapter = _scripts_critique_adapter_lib_module.load_adapter
_skills_public_retro_resolve_adapter_module = import_repo_module(
    __file__, "skills.public.retro.scripts.resolve_adapter"
)
load_retro_adapter = _skills_public_retro_resolve_adapter_module.load_adapter
_scripts_quality_adapter_lib_module = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter_strict = _scripts_quality_adapter_lib_module.load_quality_adapter_strict
_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
_scripts_check_coverage_lib_module = import_repo_module(__file__, "scripts.check_coverage_lib")
PER_FILE_MIN_COVERAGE = _scripts_check_coverage_lib_module.PER_FILE_MIN_COVERAGE
PER_FILE_MIN_STATEMENTS = _scripts_check_coverage_lib_module.PER_FILE_MIN_STATEMENTS
PER_FILE_WARN_BELOW = _scripts_check_coverage_lib_module.PER_FILE_WARN_BELOW


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


def iter_resolvers(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(
        root,
        ("skills/public/*/scripts/resolve_adapter.py",),
        require_git=require_git,
    )


def iter_adapter_yaml(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (".agents/*-adapter.yaml", ".agents/cautilus-adapters/*.yaml"),
        require_git=require_git,
    )


def validate_charness_quality_commands(path: Path, data: dict) -> None:
    if data.get("gate_commands") != ["./scripts/run-quality.sh"]:
        raise ValidationError(f"{path}: gate_commands must exactly name the standing quality gate")
    if data.get("review_commands") != ["./scripts/run-quality.sh --review"]:
        raise ValidationError(f"{path}: review_commands must exactly name the quality review gate")


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
    if not isinstance(runtime_profiles, dict) or not runtime_profiles:
        raise ValidationError(
            f"{path}: runtime_budget_profiles must declare at least one observed host profile "
            f"(e.g. `local-linux-x86_64-36cpu`); profile names follow `<os>-<arch>-<cpu>` and "
            "should match an actual maintainer machine, not an aspirational target."
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

    validate_charness_quality_commands(path, data)

    coverage_policy = data.get("coverage_floor_policy")
    expected_fail_pct = PER_FILE_MIN_COVERAGE * 100
    expected_warn_pct = PER_FILE_WARN_BELOW * 100
    if not isinstance(coverage_policy, dict):
        raise ValidationError(f"{path}: coverage_floor_policy must be an explicit mapping")
    if coverage_policy.get("min_statements_threshold") != PER_FILE_MIN_STATEMENTS:
        raise ValidationError(
            f"{path}: coverage_floor_policy.min_statements_threshold must match check_coverage.py "
            f"({PER_FILE_MIN_STATEMENTS})"
        )
    try:
        fail_below_pct = float(coverage_policy.get("fail_below_pct", -1.0))
        warn_ceiling_pct = float(coverage_policy.get("warn_ceiling_pct", -1.0))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{path}: coverage_floor_policy thresholds must be numeric") from exc
    if fail_below_pct != expected_fail_pct:
        raise ValidationError(
            f"{path}: coverage_floor_policy.fail_below_pct must match check_coverage.py "
            f"({expected_fail_pct:.1f})"
        )
    if warn_ceiling_pct != expected_warn_pct:
        raise ValidationError(
            f"{path}: coverage_floor_policy.warn_ceiling_pct must match check_coverage.py "
            f"({expected_warn_pct:.1f})"
        )
    if coverage_policy.get("gate_script_pattern") != "scripts/check_coverage.py":
        raise ValidationError(
            f"{path}: coverage_floor_policy.gate_script_pattern must name the actual coverage gate"
        )


def integration_schema_path(path: Path) -> Path | None:
    """Return the integration manifest schema owning this adapter, if any.

    `.agents/<name>-adapter.yaml` pairs with
    `integrations/<name>/manifest.schema.json` (usage-episodes, t-events,
    worktree). `.agents/cautilus-adapters/*.yaml` is excluded by the
    parent-dir guard; a repo without the schema file inherits nothing.
    """
    if path.parent.name != ".agents" or not path.name.endswith("-adapter.yaml"):
        return None
    name = path.name.removesuffix("-adapter.yaml")
    candidate = path.parent.parent / "integrations" / name / "manifest.schema.json"
    return candidate if candidate.is_file() else None


def validate_adapter_integration_schema(path: Path) -> None:
    """#342: an adapter file has two validation owners — the generic shape
    checks here and the owning integration's jsonschema consumed at runtime.
    Run the stronger owner at every validate-adapters timing (commit-time
    dispatcher + broad gate share this command) so a schema-rejected adapter
    edit cannot land as a clean commit and fail slices later at the emitter."""
    schema_path = integration_schema_path(path)
    if schema_path is None:
        return
    try:
        import jsonschema
        import yaml
    except ImportError:
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{schema_path}: integration manifest schema is unreadable: {exc}") from exc
    # Parse with yaml.safe_load like the runtime consumers (not the minimal
    # adapter_lib parser) so the commit-time verdict matches the runtime owner.
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(f"{path}: adapter YAML failed to parse: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: adapter YAML must parse to a mapping")
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        raise ValidationError(f"{path}: rejected by integration schema {schema_path}: {exc.message}") from exc


def validate_adapter_yaml(path: Path) -> None:
    if path.name == "cautilus-adapter.yaml" and path.parent.name == ".agents":
        payload = load_cautilus_adapter(path.parent.parent.resolve())
        if not payload["valid"]:
            raise ValidationError(f"{path}: {'; '.join(payload['errors'])}")
        return
    if path.name == "critique-adapter.yaml" and path.parent.name == ".agents":
        payload = load_critique_adapter(path.parent.parent.resolve())
        if not payload["valid"]:
            raise ValidationError(f"{path}: {'; '.join(payload['errors'])}")
        return
    if path.name == "retro-adapter.yaml" and path.parent.name == ".agents":
        payload = load_retro_adapter(path.parent.parent.resolve())
        if not payload["valid"]:
            raise ValidationError(f"{path}: {'; '.join(payload['errors'])}")
    if path.name == "quality-adapter.yaml" and path.parent.name == ".agents":
        payload = load_quality_adapter_strict(path.parent.parent.resolve())
        if not payload["valid"]:
            raise ValidationError(f"{path}: {'; '.join(payload['errors'])}")
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
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    resolvers = iter_resolvers(root, require_git=args.require_git_file_listing)
    adapter_yaml = iter_adapter_yaml(root, require_git=args.require_git_file_listing)
    if not resolvers and not adapter_yaml:
        print("No adapter surfaces found.")
        return 0

    for resolver in resolvers:
        validate_resolver(resolver, root)
    for path in adapter_yaml:
        validate_adapter_yaml(path)
        validate_adapter_integration_schema(path)

    print(f"Validated {len(resolvers)} adapter resolvers and {len(adapter_yaml)} adapter YAML file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
