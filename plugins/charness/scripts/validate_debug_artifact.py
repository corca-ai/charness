#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "debug" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "debug" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("debug resolve_adapter.py not found")


_debug_resolve_adapter = load_path_module("debug_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _debug_resolve_adapter.load_adapter
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
report_validation_failure = _scripts_artifact_validator_module.report_validation_failure
run_changed_artifact_validator = _scripts_artifact_validator_module.run_changed_artifact_validator
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_date_line = _scripts_artifact_validator_module.validate_date_line
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
validate_max_lines = _scripts_artifact_validator_module.validate_max_lines
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
validate_section_order = _scripts_artifact_validator_module.validate_section_order
validate_title = _scripts_artifact_validator_module.validate_title
validate_sibling_followups = _scripts_artifact_validator_module.validate_sibling_followups
is_trivial_short_circuit = _scripts_artifact_validator_module.is_trivial_short_circuit
run_validation_checks = _scripts_artifact_validator_module.run_validation_checks

# Single source of truth for the Seam Risk taxonomy: reuse the enums the
# downstream consumer (`risk_interrupt_lib.parse_debug_interrupt`, run via
# `run_slice_closeout.py`) enforces instead of hand-copying them here, so the
# author-time validator can never drift below the closeout consumer (#366).
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
ALLOWED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.ALLOWED_RISK_CLASSES
FORCED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.FORCED_RISK_CLASSES
ALLOWED_GENERALIZATION_PRESSURE = _scripts_risk_interrupt_lib_module.ALLOWED_GENERALIZATION_PRESSURE
_parse_risk_classes = _scripts_risk_interrupt_lib_module._parse_risk_classes

SIBLING_BOUNDARY_HEADINGS = (
    "## Seam Risk",
    "## Interrupt Decision",
    "## Prevention",
    "## Related Prior Incidents",
)
SIBLING_SEARCH_HEADING = "## Sibling Search"
CROSS_FILE_MARKER = "cross-file:"
NO_CROSS_FILE_SIBLING_MARKER = "no cross-file sibling:"
SIBLING_SOURCE_REFERENCE = "skills/public/debug/references/sibling-search.md"

HYPOTHESIS_HEADING = "## Hypothesis"
HYPOTHESIS_BOUNDARY_HEADINGS = ("## Verification", "## Root Cause")
DISCONFIRMER_MARKER = "disconfirmer:"
FALSIFIABLE_SOURCE_REFERENCE = "skills/public/debug/references/disconfirmer-first.md"

MAX_ARTIFACT_LINES = 180
REQUIRED_SECTIONS = (
    "## Problem",
    "## Correct Behavior",
    "## Observed Facts",
    "## Reproduction",
    "## Candidate Causes",
    "## Hypothesis",
    "## Verification",
    "## Root Cause",
    "## Prevention",
)
CURRENT_DIAGNOSIS_SECTIONS = (
    "## Invariant Proof",
    "## Detection Gap",
    "## Sibling Search",
)
CURRENT_INTERRUPT_SECTIONS = (
    "## Seam Risk",
    "## Interrupt Decision",
)
OPTIONAL_SECTIONS = (
    "## Related Prior Incidents",
)


def validate_candidate_causes(lines: list[str]) -> None:
    start = find_index(lines, "## Candidate Causes") + 1
    end = find_index(lines, "## Hypothesis")
    bullets = [line.strip() for line in lines[start:end] if line.strip().startswith("- ")]
    if len(bullets) < 3:
        raise ValidationError("`## Candidate Causes` must list at least three plausible causes")


def section_lines(lines: list[str], heading: str, next_headings: tuple[str, ...]) -> list[str]:
    start = find_index(lines, heading) + 1
    end = len(lines)
    for candidate in next_headings:
        if candidate == heading:
            continue
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start and index < end:
            end = index
    return [line.strip() for line in lines[start:end] if line.strip()]


def extract_prefixed_values(lines: list[str], prefixes: tuple[str, ...]) -> dict[str, str]:
    values: dict[str, str] = {}
    for prefix in prefixes:
        line = next((line for line in lines if line.startswith(prefix)), None)
        if line is None:
            raise ValidationError(f"missing required line `{prefix}...`")
        value = line[len(prefix) :].strip()
        if not value:
            raise ValidationError(f"`{prefix}...` must not be empty")
        values[prefix] = value
    return values


def validate_current_interrupt_sections(lines: list[str]) -> None:
    if "## Seam Risk" not in lines or "## Interrupt Decision" not in lines:
        raise ValidationError("current debug artifact must include `## Seam Risk` and `## Interrupt Decision`")

    seam_lines = section_lines(lines, "## Seam Risk", ("## Seam Risk", "## Interrupt Decision", "## Prevention"))
    interrupt_lines = section_lines(
        lines,
        "## Interrupt Decision",
        ("## Seam Risk", "## Interrupt Decision", "## Prevention", "## Related Prior Incidents"),
    )
    seam_values = extract_prefixed_values(
        seam_lines,
        (
            "- Interrupt ID: ",
            "- Risk Class: ",
            "- Seam: ",
            "- Disproving Observation: ",
            "- What Local Reasoning Cannot Prove: ",
            "- Generalization Pressure: ",
        ),
    )
    interrupt_values = extract_prefixed_values(
        interrupt_lines,
        (
            "- Critique Required: ",
            "- Next Step: ",
            "- Handoff Artifact: ",
        ),
    )
    risk_classes = tuple(part.strip() for part in seam_values["- Risk Class: "].split(",") if part.strip())
    if not risk_classes:
        raise ValidationError("`Risk Class` must list at least one value")
    invalid = [value for value in risk_classes if value not in ALLOWED_RISK_CLASSES]
    if invalid:
        raise ValidationError("`Risk Class` contains unknown values")
    if "none" in risk_classes and len(risk_classes) > 1:
        raise ValidationError("`Risk Class: none` cannot be combined with other values")

    generalization_pressure = seam_values["- Generalization Pressure: "]
    if generalization_pressure not in ALLOWED_GENERALIZATION_PRESSURE:
        raise ValidationError("`Generalization Pressure` must be `none`, `monitor`, or `factor-now`")

    critique_required = interrupt_values["- Critique Required: "]
    if critique_required not in {"yes", "no"}:
        raise ValidationError("`Critique Required` must be `yes` or `no`")
    next_step = interrupt_values["- Next Step: "]
    if next_step not in {"impl", "spec"}:
        raise ValidationError("`Next Step` must be `impl` or `spec`")

    # `Resolution` is OPTIONAL for backward-compat (legacy artifacts predate it):
    # a missing field is read by plan_debug_run.py as an open investigation to
    # continue. When the author DOES declare it, constrain it to the lifecycle
    # enum the planner consumes (`open` to continue, `resolved` to demote the
    # pointer to a prior incident so it stops hijacking a fresh bug).
    resolution_line = next((line for line in interrupt_lines if line.startswith("- Resolution: ")), None)
    if resolution_line is not None:
        # Match the planner's case-folding (plan_debug_run.py lowercases before the
        # `== "resolved"` compare) so the validator never rejects a value the
        # consumer would honor — a producer/consumer mismatch in its own right.
        resolution = resolution_line[len("- Resolution: ") :].strip().lower()
        if resolution not in {"open", "resolved"}:
            raise ValidationError("`Resolution` must be `open` or `resolved`")

    forced = bool(set(risk_classes) & FORCED_RISK_CLASSES or generalization_pressure == "factor-now")
    if forced and critique_required != "yes":
        raise ValidationError("forced risk interrupt must record `Critique Required: yes`")
    if forced and next_step != "spec":
        raise ValidationError("forced risk interrupt must record `Next Step: spec`")
    if forced:
        handoff = interrupt_values["- Handoff Artifact: "]
        if not handoff.startswith("charness-artifacts/spec/") or not handoff.endswith(".md"):
            raise ValidationError("forced risk interrupt must point `Handoff Artifact` at `charness-artifacts/spec/*.md`")


def validate_current_invariant_proof(lines: list[str]) -> None:
    invariant_lines = section_lines(
        lines,
        "## Invariant Proof",
        ("## Invariant Proof", "## Detection Gap", "## Sibling Search", "## Seam Risk"),
    )
    extract_prefixed_values(
        invariant_lines,
        (
            "- Invariant: ",
            "- Producer Proof: ",
            "- Final-Consumer Proof: ",
            "- Interface-Shape Sibling Scan: ",
            "- Non-Claims: ",
        ),
    )


def _section_declares_marker(section: list[str], markers: tuple[str, ...]) -> bool:
    """A section satisfies an authored honesty marker when a trivial-fix
    short-circuit is present, or any line carries one of `markers` followed by a
    non-empty value. Shared by the cross-file-sibling and falsifiable-hypothesis
    marker checks so the two stay one pattern, not drift-prone twins.
    """
    if any(is_trivial_short_circuit(line) for line in section):
        return True
    for line in section:
        lowered = line.lower()
        for marker in markers:
            position = lowered.find(marker)
            if position != -1 and lowered[position + len(marker) :].strip():
                return True
    return False


def validate_cross_file_sibling_marker(lines: list[str]) -> None:
    """Require the current debug artifact's `## Sibling Search` to declare cross-file scope.

    The sibling-search reference requires the scan to leave the subject file (the
    `same layer` and `abstraction up` axes name siblings "in different files,
    different layers"). `validate_sibling_followups` only checks decision and
    `follow-up:` shape, so a within-file-only scan still passes today. This adds an
    explicit author marker, modeled on the `follow-up:` requirement: the section
    must carry either `cross-file: <path-or-axis>` (a named sibling outside the
    subject file) or `no cross-file sibling: <reason>` (a justified escape). The
    marker is authored, not parsed from prose, because the real corpus records
    siblings as free-form axis bullets and the schema has no `Subject:` source-file
    field to diff a foreign `file:line` against — a parser would mass-regress
    correct artifacts or collapse to a gameable "any path mention" check. The
    trivial-fix short-circuit satisfies it, matching `validate_sibling_followups`.
    Like `follow-up:`, this is an honesty contract surfaced for fresh-eye review,
    not an anti-gaming gate.
    """
    section = section_lines(lines, SIBLING_SEARCH_HEADING, SIBLING_BOUNDARY_HEADINGS)
    if _section_declares_marker(section, (NO_CROSS_FILE_SIBLING_MARKER, CROSS_FILE_MARKER)):
        return
    raise ValidationError(
        "current debug artifact `## Sibling Search` must declare cross-file scope: add "
        "`cross-file: <path-or-axis>` naming a sibling outside the subject file, or "
        "`no cross-file sibling: <reason>` as a justified escape (the trivial-fix "
        f"short-circuit also satisfies it); see {SIBLING_SOURCE_REFERENCE}."
    )


def validate_falsifiable_hypothesis_marker(lines: list[str]) -> None:
    """Require the current debug artifact's `## Hypothesis` to record a disconfirmer.

    The proven static-only-RCA gap (debug claim-fidelity 2026-06-30 re-capture, the
    `falsifiable-hypothesis-before-fix` outcome FAIL) is a run that authored a
    conclusion from `static scan only` with no cheapest-refutation check.
    `five-steps.md` step 5 ("verify a FALSIFIABLE hypothesis; don't call intuition a
    diagnosis") and `disconfirmer-first.md` own that rule, but a bare `TODO`
    Hypothesis seed left it un-internalized, so the run filled the section shallowly.
    This moves the rule INTO the artifact structure: the section must carry a
    `disconfirmer: <cheapest refutation>` marker. A justified
    `disconfirmer: n/a — <why no cheap refutation exists>` escape satisfies it
    (some bug classes — e.g. CI-only — have no local repro). Like the cross-file
    sibling marker, this is an honesty contract surfaced for fresh-eye review, NOT an
    anti-gaming gate: the `falsifiable-hypothesis-before-fix` OUTCOME assertion
    (`evals/cautilus/debug-claim-fidelity/outcome-assertions.json`) stays the real
    substance bar, which a `disconfirmer: n/a` static-only run still fails. The
    trivial-fix short-circuit satisfies it, matching `validate_cross_file_sibling_marker`.
    """
    # floor-addition-restraint: keep. Recorded recurrence (static-only RCF FAIL across
    # two debug claim-fidelity captures, 2026-06-30 + re-capture), modeled on the
    # accepted cross-file sibling marker, and absorbed by the existing
    # check_artifact_surface_preflight (the debug validator already runs there), so it
    # is not a new serial end-gate. The OUTCOME assertion remains the real bar; this
    # marker only surfaces the field for the run and for fresh-eye review.
    section = section_lines(lines, HYPOTHESIS_HEADING, HYPOTHESIS_BOUNDARY_HEADINGS)
    if _section_declares_marker(section, (DISCONFIRMER_MARKER,)):
        return
    raise ValidationError(
        "current debug artifact `## Hypothesis` must record a falsifiability check: add "
        "`disconfirmer: <cheapest refutation run before the fix>` (a justified "
        "`disconfirmer: n/a — <why no cheap refutation exists>` escape, or the trivial-fix "
        f"short-circuit, also satisfies it); see {FALSIFIABLE_SOURCE_REFERENCE}."
    )


def validate_dated_seam_risk_enums(lines: list[str]) -> None:
    """Enforce the `risk_interrupt_lib` Risk Class / Generalization Pressure
    taxonomy on dated debug records that carry a `## Seam Risk` section.

    `risk_interrupt_lib.parse_debug_interrupt` — consumed by `plan_risk_interrupt`
    in `run_slice_closeout.py` via the current-pointer `latest.md` — rejects an
    off-taxonomy `Risk Class` / `Generalization Pressure`. The dated author-time
    path did not run that enum check, so an off-taxonomy value passed at write
    time and only surfaced repo-wide at closeout, far from the artifact (#366).
    This applies the same enums the consumer uses (imported, not hand-copied) at
    author time.

    Only the enum subset runs on dated records — forced-interrupt completeness
    (`Critique Required` / `Next Step` / spec `Handoff Artifact`) stays a
    `latest.md` concern — so the historical dated corpus, whose `## Seam Risk`
    values are all in-taxonomy, is not retro-regressed. Records with no
    `## Seam Risk` section (legacy shapes) are unaffected.
    """
    if "## Seam Risk" not in lines:
        return
    seam_lines = section_lines(lines, "## Seam Risk", ("## Seam Risk", "## Interrupt Decision", "## Prevention"))
    seam_values = extract_prefixed_values(
        seam_lines,
        (
            "- Risk Class: ",
            "- Generalization Pressure: ",
        ),
    )
    _parse_risk_classes(seam_values["- Risk Class: "])
    generalization_pressure = seam_values["- Generalization Pressure: "]
    if generalization_pressure not in ALLOWED_GENERALIZATION_PRESSURE:
        raise ValidationError(
            "`Generalization Pressure` must be one of "
            + ", ".join(f"`{value}`" for value in sorted(ALLOWED_GENERALIZATION_PRESSURE))
        )


def validate_debug_artifact(path: Path, *, collect_all: bool = False) -> None:
    lines = read_lines(path)
    base_checks = (
        lambda: validate_title(
            lines,
            title_predicate=lambda line: line.startswith("# ") and "debug" in line.lower(),
            error_message="debug artifact must start with a `# ... Debug ...` heading",
        ),
        lambda: validate_date_line(lines),
        lambda: validate_max_lines(
            lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="debug artifact", artifact_type="debug"
        ),
    )
    if path.name == "latest.md":
        required_sections = (
            REQUIRED_SECTIONS[:8]
            + CURRENT_DIAGNOSIS_SECTIONS
            + CURRENT_INTERRUPT_SECTIONS
            + ("## Prevention",)
        )
        checks = base_checks + (
            lambda: validate_exact_h2_sections(lines, required_sections, optional_sections=OPTIONAL_SECTIONS),
            lambda: validate_nonempty_sections(lines, required_sections),
            lambda: validate_candidate_causes(lines),
            lambda: validate_current_invariant_proof(lines),
            lambda: validate_sibling_followups(
                lines, boundary_headings=SIBLING_BOUNDARY_HEADINGS, source_reference=SIBLING_SOURCE_REFERENCE
            ),
            lambda: validate_cross_file_sibling_marker(lines),
            lambda: validate_falsifiable_hypothesis_marker(lines),
            lambda: validate_current_interrupt_sections(lines),
        )
    else:
        checks = base_checks + (
            lambda: validate_section_order(lines, REQUIRED_SECTIONS),
            lambda: validate_nonempty_sections(lines, REQUIRED_SECTIONS),
            lambda: validate_candidate_causes(lines),
            lambda: validate_sibling_followups(
                lines, boundary_headings=SIBLING_BOUNDARY_HEADINGS, source_reference=SIBLING_SOURCE_REFERENCE
            ),
            lambda: validate_dated_seam_risk_enums(lines),
        )
    run_validation_checks(checks, collect_all=collect_all, artifact_label="debug artifact")


def _selected_artifacts(args, repo_root: Path, output_dir: Path) -> list[Path] | None:
    """Resolve which debug artifacts to validate.

    `--paths` exists so this validator can run CHANGED-SCOPED at the commit
    boundary. Validate-all was the documented reason debug sat outside the
    fail-fast structural sweep: a whole-corpus gate there would block a commit on
    pre-existing siblings the author never touched. Scoped to the paths actually
    being committed, that objection does not apply, and the author learns the
    artifact's shape at commit time instead of at the release gate (the #454
    session discovered it by failing the release-only validator).

    Scoping is OPT-IN, unlike the critique/ideation/retro siblings whose bare
    default is changed-paths. Validate-all stays the default here because every
    existing caller — the broad gate, CI, and this validator's own suite — relies
    on it, and the commit boundary passes `--paths` explicitly, so nothing is
    gained by flipping the default and a lot of working callers would break.
    """
    if args.all or args.paths is None:
        return sorted(output_dir.glob("*.md"))
    prefix = f"{output_dir.relative_to(repo_root).as_posix()}/"
    scoped = [
        repo_root / rel
        for rel in args.paths
        if rel.startswith(prefix) and rel.endswith(".md") and (repo_root / rel).is_file()
    ]
    # No debug artifact in scope is a no-op, not a failure: most commits touch none.
    return scoped or None


def _debug_artifacts(run) -> list[Path] | None:
    """Resolve the batch through debug's own adapter, not changed-path discovery.

    Debug is the one family whose artifact set comes from an adapter-declared
    output directory, so it supplies this instead of `candidate_paths_fn`.

    The two hard-error cases exit 1 DIRECTLY rather than raising
    `ValidationError`: neither is an artifact rule violation, so routing them
    through `report_validation_failure` would append the "start from the owning
    scaffold" hint — advice to author a stub when the real fix is a wrong
    `--repo-root` or an unbootstrapped repo. `None` means "nothing in scope",
    which is a success (most commits touch no debug artifact).
    """
    output_dir = run.repo_root / load_adapter(run.repo_root)["data"]["output_dir"]
    if not output_dir.is_dir():
        _exit_not_a_violation(f"No debug output directory at {output_dir.relative_to(run.repo_root)}.")
    artifacts = _selected_artifacts(run.args, run.repo_root, output_dir)
    if artifacts is None:
        return None
    if not artifacts:
        _exit_not_a_violation(f"No debug artifacts found in {output_dir.relative_to(run.repo_root)}.")
    return artifacts


def _exit_not_a_violation(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked-in debug artifact.",
        artifact_label="debug artifact",
        artifacts_fn=_debug_artifacts,
        validate_factory=lambda run: (
            lambda artifact: validate_debug_artifact(artifact, collect_all=run.collect_all)
        ),
        no_scope_message="No debug artifacts in scope.",
        per_artifact_success=True,
        fail_fast_help=(
            "Stop at the first rule violation instead of reporting every violation in one pass."
        ),
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        sys.exit(report_validation_failure(str(exc), artifact_type="debug"))
