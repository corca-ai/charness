from __future__ import annotations

import copy
import re
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    optional_int,
    optional_string,
    optional_string_list,
    resolve_adapter_payload,
)
from scripts.adapters.quality_bootstrap_absence import remove_nested_absences  # noqa: E402
from scripts.adapters.quality_bootstrap_lib import ADAPTER_CANDIDATES  # noqa: E402
from scripts.adapters.quality_dup_ratchet_policy import (  # noqa: E402
    DEFAULT_DUP_RATCHET,
    validate_dup_ratchet,
)
from scripts.adapters.quality_policy_defaults import (  # noqa: E402
    DEFAULT_CHANGED_LINE_MUTATION_GATE,
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_MUTATION_TESTING,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES,
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR,
    DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS,
    DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    DEFAULT_STANDING_DOC_PROVENANCE,
    validate_changed_line_mutation_gate,
    validate_coverage_floor_policy,
    validate_mutation_testing,
    validate_prompt_asset_policy,
    validate_skill_ergonomics_gate_rules,
    validate_standing_doc_provenance,
)
from scripts.adapters.quality_universes_lib import DEFAULT_UNIVERSES  # noqa: E402
from scripts.artifact_naming_lib import ARTIFACT_CLASSES, RECORD_PATTERN  # noqa: E402

ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"


def _load_adapter_validators():
    repo_root = Path(__file__).resolve().parents[2]
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts",
        repo_root / "skills" / "quality" / "scripts",
    )
    for candidate in candidates:
        if not (candidate / "adapter_validators.py").is_file():
            continue
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        import adapter_validators

        return adapter_validators
    raise FileNotFoundError("quality adapter_validators.py not found")


adapter_validators = _load_adapter_validators()


def _float_value(value: Any, field: str, errors: list[str]) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        errors.append(f"{field} must be a number")
        return None
    result = float(value)
    if result >= 0:
        return result
    errors.append(f"{field} must be greater than or equal to 0")
    return None


def _int_value(value: Any, field: str, errors: list[str], *, minimum: int = 0) -> int | None:
    # Delegates to the shared vocabulary rather than re-implementing it: this
    # hand-rolled copy predated `optional_int` and is exactly the drift that made a
    # numeric adapter field look like per-skill work instead of a missing primitive.
    return optional_int(value, field, errors, minimum=minimum)


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def infer_quality_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/quality",
        "artifact_class": ARTIFACT_CLASS,
        "preset_lineage": [],
        "coverage_fragile_margin_pp": 1.0,
        "coverage_floor_policy": dict(DEFAULT_COVERAGE_FLOOR_POLICY),
        "specdown_smoke_patterns": [],
        "spec_pytest_reference_format": DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
        "public_spec_section_exemptions": list(DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS),
        "public_spec_implementation_ref_density_floor": DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR,
        "public_spec_implementation_guard_min_lines": DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES,
        "public_spec_pointer_proof_markers": list(DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS),
        "prompt_asset_roots": [],
        "adapter_review_sources": [],
        "acknowledged_recommendations": [],
        "gate_design_review_globs": [],
        "product_surfaces": [],
        "nose_inventory_paths": [],
        "skill_ergonomics_skill_paths": [],
        "skill_ergonomics_runtime_install_skill_paths": [],
        "vendored_paths": [],
        "cli_skill_surface_probe_commands": [],
        "cli_skill_surface_command_docs": [],
        "cli_skill_surface_skill_paths": [],
        "cli_skill_surface_change_globs": [],
        "canonical_markdown_surfaces": ["AGENTS.md", "CLAUDE.md"],
        "prompt_asset_policy": dict(DEFAULT_PROMPT_ASSET_POLICY),
        "skill_ergonomics_gate_rules": list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
        "runtime_profile_default": "default",
        "runtime_budgets": {},
        "runtime_budget_profiles": {},
        "runtime_budget_intent": {"always": [], "conditional": {}, "external": {}},
        "runtime_budget_universe": {},
        "command_timing_log": {},
        "test_file_discovery": {"command": "", "patterns": [], "patterns_mode": "extend"},
        "lint_ignore_discovery": {"directives": []},
        "startup_probes": [],
        "quality_phases": [],
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "review_commands": [],
        "security_commands": [],
        "mutation_testing": copy.deepcopy(DEFAULT_MUTATION_TESTING),
        "standing_doc_provenance": copy.deepcopy(DEFAULT_STANDING_DOC_PROVENANCE),
        "changed_line_mutation_gate": copy.deepcopy(DEFAULT_CHANGED_LINE_MUTATION_GATE),
        "dup_ratchet": copy.deepcopy(DEFAULT_DUP_RATCHET),
        "universes": copy.deepcopy(DEFAULT_UNIVERSES),
    }


def _apply_policy_fields(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> None:
    coverage_fragile_margin_pp = _float_value(
        data.get("coverage_fragile_margin_pp"), "coverage_fragile_margin_pp", errors
    )
    if coverage_fragile_margin_pp is not None:
        validated["coverage_fragile_margin_pp"] = coverage_fragile_margin_pp

    coverage_floor_policy = validate_coverage_floor_policy(
        data.get("coverage_floor_policy"), errors
    )
    if coverage_floor_policy is not None:
        validated["coverage_floor_policy"] = coverage_floor_policy

    specdown_smoke_patterns = optional_string_list(
        data.get("specdown_smoke_patterns"), "specdown_smoke_patterns", errors
    )
    if specdown_smoke_patterns is not None:
        validated["specdown_smoke_patterns"] = specdown_smoke_patterns

    spec_pytest_reference_format = optional_string(
        data.get("spec_pytest_reference_format"), "spec_pytest_reference_format", errors
    )
    if spec_pytest_reference_format is not None:
        validated["spec_pytest_reference_format"] = spec_pytest_reference_format

    public_spec_implementation_ref_density_floor = _float_value(
        data.get("public_spec_implementation_ref_density_floor"),
        "public_spec_implementation_ref_density_floor",
        errors,
    )
    if public_spec_implementation_ref_density_floor is not None:
        validated["public_spec_implementation_ref_density_floor"] = (
            public_spec_implementation_ref_density_floor
        )

    # Raw FILE words, matching what `validate_quality_artifact.py` counts. Written only
    # when the repo declared
    # one, so the DEFAULT number keeps living in the validator that enforces it;
    # `minimum=1` because a ceiling of 0 refuses every possible artifact.
    max_artifact_words = _int_value(
        data.get("max_artifact_words"), "max_artifact_words", errors, minimum=1
    )
    if max_artifact_words is not None:
        validated["max_artifact_words"] = max_artifact_words
    # Retired 2026-08-19. An ERROR, not a drop: a dropped key leaves a consuming repo's
    # declared ceiling inert while the adapter still resolves `valid: true`, and 140 read
    # as a word ceiling would refuse every real artifact.
    if "max_artifact_lines" in data:
        errors.append(
            "`max_artifact_lines` was retired and is no longer read; use "
            "`max_artifact_words` instead. The budget now charges WORDS, not lines, "
            "because a line count measured the author's wrap width; a line ceiling "
            "cannot be converted automatically (the old bar admitted a 7.5x spread of "
            "words across this repo's own corpus), so restate the bar you want in words"
        )

    public_spec_implementation_guard_min_lines = _int_value(
        data.get("public_spec_implementation_guard_min_lines"),
        "public_spec_implementation_guard_min_lines",
        errors,
    )
    if public_spec_implementation_guard_min_lines is not None:
        validated["public_spec_implementation_guard_min_lines"] = (
            public_spec_implementation_guard_min_lines
        )

    prompt_asset_policy = validate_prompt_asset_policy(data.get("prompt_asset_policy"), errors)
    if prompt_asset_policy is not None:
        validated["prompt_asset_policy"] = prompt_asset_policy

    skill_ergonomics_gate_rules = validate_skill_ergonomics_gate_rules(
        data.get("skill_ergonomics_gate_rules"), errors
    )
    if skill_ergonomics_gate_rules is not None:
        validated["skill_ergonomics_gate_rules"] = skill_ergonomics_gate_rules

    adapter_validators.apply_runtime_fields(data, validated, errors)


def _apply_mutation_testing(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_mutation_testing(data.get("mutation_testing"), errors, warnings)
    if block is not None:
        validated["mutation_testing"] = block


def _apply_standing_doc_provenance(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_standing_doc_provenance(data.get("standing_doc_provenance"), errors, warnings)
    if block is not None:
        validated["standing_doc_provenance"] = block


def _apply_changed_line_mutation_gate(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_changed_line_mutation_gate(
        data.get("changed_line_mutation_gate"), errors, warnings
    )
    if block is not None:
        validated["changed_line_mutation_gate"] = block


def _apply_dup_ratchet(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = validate_dup_ratchet(data.get("dup_ratchet"), errors, warnings)
    if block is not None:
        validated["dup_ratchet"] = block


def _apply_universes(data: dict[str, Any], validated: dict[str, Any], errors: list[str]) -> None:
    block = adapter_validators.validate_universes(data.get("universes"), errors)
    if block is not None:
        validated["universes"] = block
    validated["_universes_declared"] = (
        copy.deepcopy(data.get("universes")) if "universes" in data else None
    )


def _apply_test_file_discovery(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = adapter_validators.test_file_discovery(
        data.get("test_file_discovery"), errors, warnings
    )
    if block is not None:
        validated["test_file_discovery"] = block


def _apply_lint_ignore_discovery(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    block = adapter_validators.lint_ignore_discovery(
        data.get("lint_ignore_discovery"), errors, warnings
    )
    if block is not None:
        validated["lint_ignore_discovery"] = block


# A structural field is refused outright by the bootstrap, so naming one here as
# "still resolving to a default" would report a declaration that can never be honored.
ABSENCE_STRUCTURAL_FIELDS = frozenset(
    "version repo language output_dir preset_id customized_from deliberately_absent".split()
)


# THE RULER, stated once as code. Three statements of "what counts as a path" (a
# comment, a test helper, and a reference doc) is how the first version of this guard
# came to admit a narrower set than it documented — a partial rule presented as a
# complete one, which is the class this whole field exists to close. The test imports
# this rather than restating it; its independence is in re-deriving over the LIVE
# defaults, not in re-implementing the predicate.
_PATH_EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{1,8}$")


def names_a_filesystem_location(value: Any) -> bool:
    """Whether this string names a file or directory rather than merely mentioning `/`.

    The no-whitespace clause is what excludes a cron expression and a regex that happen
    to contain a slash.
    """
    return (
        isinstance(value, str)
        and bool(value)
        and not any(char.isspace() for char in value)
        and ("/" in value or bool(_PATH_EXTENSION_RE.search(value)))
    )


def path_bearing_entries(value: Any, prefix: str = "") -> dict[str, str]:
    """`<dotted/indexed key>` -> the path-naming string, walking dicts AND lists.

    Recursing both shapes is load-bearing: a nested key or a list-of-mappings that this
    walker cannot reach is a phantom path the warning would silently omit while reading
    as exhaustive.
    """
    found: dict[str, str] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            found.update(path_bearing_entries(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.update(path_bearing_entries(item, f"{prefix}[{index}]"))
    elif names_a_filesystem_location(value):
        found[prefix] = value
    return found


# Fields whose PRESET DEFAULT names a filesystem location. Only the FIELD set is
# hand-maintained; which keys within it are path-bearing is derived by the ruler above,
# so a renamed or newly nested path key cannot make an entry silently inert. Structural
# fields are excluded because declaring one absent is refused outright.
#
# These are the only fields where a resolved default can send a reader hunting for a
# file the repo does not have, which is the harm the reporter named. Other
# declared-absent fields keep their default untouched: thresholds, rule names, and
# markers assert nothing about the filesystem.
PATH_BEARING_ABSENCE_FIELDS = frozenset(
    "coverage_floor_policy changed_line_mutation_gate dup_ratchet mutation_testing "
    "canonical_markdown_surfaces universes".split()
)


def is_deliberately_absent(data: dict[str, Any], field: str) -> bool:
    """Whether `field` was declared absent on purpose by the repo.

    The one call a consumer makes before premising anything on that field's resolved
    value. Resolution still returns the preset default (changing that would alter what
    every field means at resolution time and break consumers that index them), so a
    consumer that is about to treat a resolved path as real has to ask.
    """
    declared = data.get("deliberately_absent")
    return isinstance(declared, dict) and field in declared


def unasserted_paths(validated: dict[str, Any], honored: dict[str, str]) -> dict[str, str]:
    """`<field>.<key>` / `<field>[<i>]` -> the resolved path the repo does NOT claim exists."""
    found: dict[str, str] = {}
    # Filter structural fields the same way the warning does. Without this, a structural
    # path-bearing field would populate the data key with no warning naming it — the data
    # saying one thing and the prose another.
    for field in sorted(PATH_BEARING_ABSENCE_FIELDS & set(honored) - ABSENCE_STRUCTURAL_FIELDS):
        found.update(path_bearing_entries(validated.get(field), field))
    return found


def _apply_deliberate_absence(
    data: dict[str, Any], validated: dict[str, Any], warnings: list[str]
) -> None:
    """Carry the operator's declared absences through resolution, and mark the phantom paths.

    Keeping the bootstrap from rewriting the field is only half the job: this resolver
    still fills every unset field from `infer_quality_defaults`, so a repo that declared
    `coverage_floor_policy` absent still resolves to the preset default naming
    `lefthook.yml`. Changing what a resolved field MEANS would break consumers that index
    it, so the default stays — but the specific values that assert a file exists are
    listed as unasserted, because "the next session goes hunting for gates that do not
    exist" is the harm, and only path-bearing values can cause it.
    """
    declared = data.get("deliberately_absent")
    if declared is None:
        return
    # Dropping a malformed declaration in silence would re-create the exact failure this
    # field exists to close: the file says something, the resolver acts as if it did not,
    # and nothing tells the operator which reading won. The bootstrap refuses these
    # outright; the resolver only warns, because refusing here would break loading a repo
    # that the bootstrap has not yet been run against.
    if not isinstance(declared, dict):
        warnings.append(
            "deliberately_absent must be a mapping of field name to reason; "
            f"got {type(declared).__name__}, so no declaration was honored."
        )
        return
    honored = {
        field: reason
        for field, reason in declared.items()
        if isinstance(field, str) and isinstance(reason, str)
    }
    if discarded := sorted(str(field) for field in declared if field not in honored):
        warnings.append(
            "deliberately_absent entries ignored because the field name or reason is not a "
            f"string: {', '.join(discarded)}."
        )
    if not honored:
        return
    validated["deliberately_absent"] = honored
    remove_nested_absences(validated, honored)
    still_defaulted = sorted(
        field
        for field in honored
        if field not in ABSENCE_STRUCTURAL_FIELDS and validated.get(field) not in (None, {}, [], "")
    )
    unasserted = unasserted_paths(validated, honored)
    if unasserted:
        validated["deliberately_absent_unasserted_paths"] = unasserted
    if still_defaulted:
        warning = (
            "deliberately_absent declares "
            + ", ".join(still_defaulted)
            + " absent, but resolution still returns a repo default for each; treat those "
            "values as a preset default rather than as this repo's own declaration."
        )
        if unasserted:
            warning += (
                " These resolved values name PATHS this repo does not claim exist, so do not go "
                "looking for them: "
                + ", ".join(f"{ref} ({path})" for ref, path in sorted(unasserted.items()))
                + "."
            )
        warnings.append(warning)


def _apply_regenerable_facts(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    """Carry the forward-looking prose surfaces and their reasoned exemptions.

    An exemption without a reason is refused rather than honoured: the whole rule
    exists to remove unfalsifiable claims from prose, so an unexplained escape
    hatch reintroduces one at the gate level.
    """
    block = data.get("regenerable_facts")
    if block is None:
        return
    if not isinstance(block, dict):
        errors.append("regenerable_facts must be a mapping")
        return
    surfaces = block.get("surfaces")
    exemptions = block.get("exemptions") or {}
    if surfaces is not None and (
        not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces)
    ):
        errors.append("regenerable_facts.surfaces must be a list of glob strings")
        return
    if not isinstance(exemptions, dict):
        errors.append("regenerable_facts.exemptions must be a mapping of path -> reason")
        return
    unreasoned = sorted(
        path for path, reason in exemptions.items() if not str(reason or "").strip()
    )
    if unreasoned:
        errors.append("regenerable_facts.exemptions needs a reason for: " + ", ".join(unreasoned))
        return
    resolved = {"exemptions": {str(k): str(v).strip() for k, v in exemptions.items()}}
    # Absence and an explicit empty list are different declarations. Writing
    # `surfaces: []` for an exemptions-only block made the final gate treat
    # defaults as an explicitly empty scope (or, before #575, silently refill
    # them). Preserve the producer's state through the adapter transport.
    if "surfaces" in block:
        resolved["surfaces"] = list(surfaces) if surfaces else []
    validated["regenerable_facts"] = resolved


def validate_quality_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_quality_defaults(repo_root)
    # Rebinding `data` is the containment: every pass below reads it, and quality's
    # adapter carries the widest trust surface in the repo (`gate_commands`,
    # `cli_skill_surface_probe_commands`), so a version this reader cannot interpret
    # must leave none of it selectable.
    data = adapter_validators.validate_version_field(data, validated, errors)
    adapter_validators.apply_string_fields(data, validated, errors)
    configured_artifact_class = data.get("artifact_class")
    if configured_artifact_class is None:
        validated["artifact_class"] = ARTIFACT_CLASS
    elif (
        isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES
    ):
        validated["artifact_class"] = configured_artifact_class
    else:
        errors.append("artifact_class must be one of: current, history, rolling")
    _apply_policy_fields(data, validated, errors)
    adapter_validators.apply_list_fields(data, validated, errors)
    nose_inventory_paths = adapter_validators.nose_inventory_paths(
        validated.get("nose_inventory_paths"), errors
    )
    if nose_inventory_paths is not None:
        validated["nose_inventory_paths"] = nose_inventory_paths
    _apply_mutation_testing(data, validated, errors, warnings)
    _apply_standing_doc_provenance(data, validated, errors, warnings)
    _apply_changed_line_mutation_gate(data, validated, errors, warnings)
    _apply_dup_ratchet(data, validated, errors, warnings)
    _apply_universes(data, validated, errors)
    _apply_test_file_discovery(data, validated, errors, warnings)
    _apply_lint_ignore_discovery(data, validated, errors, warnings)
    _apply_regenerable_facts(data, validated, errors, warnings)

    _apply_deliberate_absence(data, validated, warnings)
    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["gate_commands"]:
        warnings.append(
            "No gate_commands configured; quality will rely on repo detection and proposals."
        )
    return validated, errors, warnings


def _quality_derived(data: dict[str, Any]) -> dict[str, Any]:
    """The four keys this skill adds, computed from `data` in ONE place rather than once
    per branch — which is how the found and absent arms drift apart."""
    return {
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_class": data["artifact_class"],
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
    }


def load_quality_adapter(repo_root: Path) -> dict[str, Any]:
    # `resolve_adapter_payload`, NOT a hand-written pair of branches around
    # `load_yaml_file`. The bare loader RAISES on a document the parser refuses and DISCARDS
    # the uninterpreted-line sink, so `parse_refused` and `declarations_dropped` were both
    # structurally dead for this skill's consumers (#673).
    payload = resolve_adapter_payload(
        repo_root,
        candidates=ADAPTER_CANDIDATES,
        infer_defaults=infer_quality_defaults,
        validate=validate_quality_adapter_data,
        absent_warnings=lambda _data: [
            "No quality adapter found. Using default durable artifact location.",
            "Create .agents/quality-adapter.yaml to record gate commands and preset lineage.",
        ],
        derive=_quality_derived,
    )
    data = payload.get("data")
    if isinstance(data, dict):
        declared = data.pop("_universes_declared", None)
    else:
        declared = None
    payload["_universes_declared"] = declared if payload.get("found") else None
    return payload


def load_quality_adapter_strict(repo_root: Path) -> dict[str, Any]:
    """Load the quality adapter for validators and gates.

    Strict callers should fail when the returned payload has `valid: false`.
    Keeping the helper separate from advisory inventory call sites makes that
    intent explicit without changing the base payload shape.
    """
    payload = load_quality_adapter(repo_root)
    payload["load_mode"] = "strict"
    return payload


def load_quality_adapter_permissive(repo_root: Path) -> dict[str, Any]:
    """Load the quality adapter for advisory inventories.

    Advisory inventories may still produce useful partial evidence from
    validated defaults and other readable fields when one adapter field is
    invalid. They must surface this degraded state instead of silently treating
    it as a clean inventory.
    """
    payload = load_quality_adapter(repo_root)
    payload["load_mode"] = "permissive"
    if payload.get("valid") is not True:
        warnings = list(payload.get("warnings", []))
        warnings.append(
            "Quality adapter is invalid; advisory inventory is using validated defaults "
            "and readable fields. Treat findings as best-effort until adapter errors are repaired."
        )
        payload["warnings"] = warnings
    return payload
