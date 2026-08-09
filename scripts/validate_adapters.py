#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_adapter_lib_module = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _scripts_adapter_lib_module.load_yaml_file
validate_adapter_version = _scripts_adapter_lib_module.validate_adapter_version
_scripts_cautilus_adapter_lib_module = import_repo_module(__file__, "scripts.cautilus_adapter_lib")
load_cautilus_adapter = _scripts_cautilus_adapter_lib_module.load_cautilus_adapter
_scripts_critique_adapter_lib_module = import_repo_module(__file__, "scripts.critique_adapter_lib")
load_critique_adapter = _scripts_critique_adapter_lib_module.load_adapter
def _load_retro_resolver_module():
    for relative in (
        Path("skills/public/retro/scripts/resolve_adapter.py"),
        Path("skills/retro/scripts/resolve_adapter.py"),
    ):
        candidate = REPO_ROOT / relative
        if candidate.is_file():
            return load_path_module("validate_adapters_retro_resolver", candidate)
    raise ImportError("retro resolve_adapter.py not found in source or exported skill layout")


_skills_public_retro_resolve_adapter_module = _load_retro_resolver_module()
load_retro_adapter = _skills_public_retro_resolve_adapter_module.load_adapter
_scripts_quality_adapter_lib_module = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter_strict = _scripts_quality_adapter_lib_module.load_quality_adapter_strict
_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
_scripts_adapter_key_registry_module = import_repo_module(__file__, "scripts.adapter_key_registry")
_scripts_adapter_warn_tier_module = import_repo_module(__file__, "scripts.adapter_warn_tier")
unreconciled_keys = _scripts_adapter_warn_tier_module.unreconciled_keys
unestablished_corpus_reason = _scripts_adapter_warn_tier_module.unestablished_corpus_reason
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
    if (root / "skills" / "public").is_dir():
        patterns = ("skills/public/*/scripts/resolve_adapter.py",)
    elif (root / "skills").is_dir():
        patterns = ("skills/*/scripts/resolve_adapter.py",)
    else:
        patterns = (
            "skills/public/*/scripts/resolve_adapter.py",
            "skills/*/scripts/resolve_adapter.py",
        )
    return iter_matching_repo_files(
        root,
        patterns,
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


def _require_declared_version(path: Path) -> None:
    """The commit-time version floor, hoisted ABOVE the per-adapter early returns.

    Left below them, `cautilus-adapter.yaml` and `critique-adapter.yaml` returned before
    ever reaching it, so the floor covered 14 of 16 `.agents/*-adapter.yaml` files while
    reading as if it covered all of them. Their resolvers treat an absent version as
    legal -- correctly, for a resolver -- so those two files had no required-version
    verdict anywhere. Running first also means the version answer does not depend on
    which resolver branch a filename happens to match.
    """
    # No not-a-mapping branch: this repo's loader always returns a mapping (a top-level
    # list parses to `{}`), so the guard was unreachable and read as though a real hazard
    # were handled. A list-shaped adapter is still refused here -- as a missing version --
    # and the shape check below owns the clearer message.
    data = load_yaml_file(path)
    errors: list[str] = []
    validate_adapter_version(data, {}, errors, required=True)
    if errors:
        raise ValidationError(f"{path}: {'; '.join(errors)}")


def validate_adapter_yaml(path: Path) -> None:
    _require_declared_version(path)
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
    # `_require_declared_version` above already read and refused this file, and this
    # repo's loader always returns a mapping, so the not-a-mapping branch that used to
    # sit here was unreachable twice over once the version floor was hoisted.
    data = load_yaml_file(path)
    # The version verdict now runs in `_require_declared_version`, above the early
    # returns. It was the 18th site and the one that disagreed hardest: the predicate it
    # used to carry accepted every value the resolvers refuse -- `version: 9` (a positive
    # integer) and `version: true` (`isinstance(True, int)` is True and `True < 1` is
    # False). This gate is also the ONLY version verdict `.agents/cautilus-adapters/*.yaml
    # ` gets, since those files have no per-skill resolver. A commit-time gate that passes
    # what every runtime reader refuses is a false green on the surface whose whole job is
    # to catch a bad adapter BEFORE it ships.
    repo = data.get("repo")
    if not isinstance(repo, str) or not repo:
        raise ValidationError(f"{path}: `repo` must be a non-empty string")
    validate_charness_quality_adapter_contract(path, data)


def iter_warn_scope_adapters(root: Path, *, require_git: bool = False) -> list[Path]:
    """Every adapter the WARN tier reads -- DELIBERATELY WIDER than `iter_adapter_yaml`.

    Round-1 bounded review caught this as a blocker, and it was the slice's own defect
    class turned on itself. `iter_adapter_yaml` globs 18 files (`.agents/`); the fire-rate
    measurement that justified arming covered 37, because `adapter_key_registry.ADAPTER_GLOBS`
    also reaches `skills/public/*/adapter.example.yaml` and `integrations/*/adapter.example.yaml`.
    Arming the narrower set while reporting the wider set's zero is a check claiming a
    scope it never read -- the exact shape this tier exists to warn about. Reproduced
    before repairing: a typo'd key added to `skills/public/handoff/adapter.example.yaml`
    produced `0 unreconciled declared key(s)` and left all 40 tests green.

    Shipped examples are the ones that MATTER here: they are what a consumer copies, so a
    typo in one propagates to every repo that adopts it. They are excluded from
    `iter_adapter_yaml` for a good reason that does not apply to this pass -- they are
    templates, so `validate_adapter_yaml`'s `repo` and version floors would refuse them --
    but a warn-only read has no such objection.

    Widening ships with its measured upper bound in the same commit, per this repo's most
    transferable lesson: over the 19 added shipped-example files (218 declared keys), the
    tier fires 0 times. That zero is PINNED by `test_this_repo_warns_about_nothing`, which
    reads this function's own output; the 19 and 218 are prose and are not.

    Listed through `iter_matching_repo_files`, like every other surface in this file, and
    NOT through a bare `root.glob`. Round-2 review caught the bare glob: it silently
    abandoned the `git ls-files` filter that `--require-git-file-listing` exists to
    enforce, so a generated or gitignored example could produce a WARNING naming a file
    that is not part of the repo -- an unactionable warning, which is the wolf-crier the
    whole tier decision was made to avoid. One scope difference from `iter_adapter_yaml`
    (the glob set) was intended; a second, undisclosed one (the listing mechanism) was the
    fixed class riding along in the fix.

    The `skills/*/adapter.example.yaml` pattern is the INSTALLED layout, and it is here for
    the same reason `iter_resolvers` carries it. The export flattens `skills/public/<id>/`
    to `skills/<id>/`, so without it the warn scope finds zero shipped examples in exactly
    the layout consumers receive -- the summary would report a confident file count that is
    accurate about what it read and useless for the population the widening names. It adds
    nothing in this repo (`skills/` here holds `public/`, `shared/`, `support/`), so the
    measured bound above is unchanged.
    """
    globs = (*_scripts_adapter_key_registry_module.ADAPTER_GLOBS, "skills/*/adapter.example.yaml")
    return iter_matching_repo_files(root, globs, require_git=require_git)


def report_unreconciled_keys(root: Path, warn_scope: list[Path]) -> Any:
    """WARN -- never refuse -- on a declared key no module reads (#530).

    This is the tier the operator chose, and the distinction is the whole point. Every
    other verdict in this file raises `ValidationError` and fails the gate; this one
    prints and returns 0, because the population that matters is consumer adapters this
    repo has never seen, and `docs/deferred-decisions.md` D46 refuses to escalate a
    REFUSAL from a repo-local zero. The zero is literal: `unknown` fires 0 times across
    the 445 declared keys in this repo's 37 adapters, which is why the warned input is
    CONSTRUCTED in the tests rather than observed here.

    The count goes in the SUMMARY line, not only in the warnings, and the line names the
    number of files read. A gate that prints nothing when it finds nothing leaves an
    operator unable to tell "checked, clean" from "never ran", and one that prints a count
    without its scope cannot distinguish "clean across 37" from "clean across 18" -- which
    is precisely how this function shipped its first round. `0 unreconciled declared
    key(s) across 37 declaring file(s)` is a claim; silence is not, and a bare zero is
    only half of one.
    """
    result = unreconciled_keys(root, warn_scope)
    for dropped in result.uninterpreted:
        print(f"WARNING {dropped['adapter']}: {dropped['detail']}", file=sys.stderr)
    for warning in result.findings:
        print(
            f"WARNING {warning['adapter']}: `{warning['key']}` is {warning['state']} -- {warning['detail']}",
            file=sys.stderr,
        )
    if not result.scope_established:
        # Said out loud, because the alternative is the exact confusion the paragraph
        # above refuses: with the key pass skipped, `0 unreconciled` would be a clean bill
        # of health for a pass that never ran. This line is what the summary's count means
        # when it says `not established`.
        print(
            f"WARNING adapter key reconciliation did not run: {unestablished_corpus_reason(root)}. "
            "This tier cannot tell an unread key from a reader it cannot see, so declared keys "
            "were left unclassified; uninterpreted lines were still reported.",
            file=sys.stderr,
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    resolvers = iter_resolvers(root, require_git=args.require_git_file_listing)
    adapter_yaml = iter_adapter_yaml(root, require_git=args.require_git_file_listing)
    warned_files = iter_warn_scope_adapters(root, require_git=args.require_git_file_listing)
    # `warned_files` joins the emptiness test because the warn scope is WIDER than
    # `adapter_yaml`. A repo holding only shipped examples -- no `.agents/` and no
    # resolvers -- used to take the early return and print `No adapter surfaces found.`
    # over a tree full of declared keys, which is the "never ran" reading this whole tier
    # exists to make impossible.
    if not resolvers and not adapter_yaml and not warned_files:
        print("No adapter surfaces found.")
        return 0

    for resolver in resolvers:
        validate_resolver(resolver, root)
    for path in adapter_yaml:
        validate_adapter_yaml(path)
        validate_adapter_integration_schema(path)

    result = report_unreconciled_keys(root, warned_files)
    # The count and the SCOPE of the count travel together, per this function's own
    # standing rule that a bare zero is only half a claim. `not established` is the third
    # reading the old two-state line could not express: not "clean across 37" and not
    # "clean across 18", but "no key verdict was rendered at all".
    reconciled = (
        f"{len(result.findings)} unreconciled declared key(s)"
        if result.scope_established
        else "declared keys not reconciled (reader corpus not established)"
    )
    print(
        f"Validated {len(resolvers)} adapter resolvers and {len(adapter_yaml)} adapter YAML file(s); "
        f"{reconciled} across {len(warned_files)} declaring file(s); "
        f"{len(result.uninterpreted)} uninterpreted line(s)."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
