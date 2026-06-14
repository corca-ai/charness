#!/usr/bin/env python3

from __future__ import annotations

import argparse
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
    if any(is_trivial_short_circuit(line) for line in section):
        return
    for line in section:
        lowered = line.lower()
        for marker in (NO_CROSS_FILE_SIBLING_MARKER, CROSS_FILE_MARKER):
            position = lowered.find(marker)
            if position != -1 and lowered[position + len(marker) :].strip():
                return
    raise ValidationError(
        "current debug artifact `## Sibling Search` must declare cross-file scope: add "
        "`cross-file: <path-or-axis>` naming a sibling outside the subject file, or "
        "`no cross-file sibling: <reason>` as a justified escape (the trivial-fix "
        f"short-circuit also satisfies it); see {SIBLING_SOURCE_REFERENCE}."
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
        lambda: validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="debug artifact"),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--report-all",
        action="store_true",
        help="Report every rule violation per artifact in one pass instead of failing on the first.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    output_dir = repo_root / adapter["data"]["output_dir"]
    if not output_dir.is_dir():
        print(f"No debug output directory at {output_dir.relative_to(repo_root)}.", file=sys.stderr)
        return 1
    artifacts = sorted(output_dir.glob("*.md"))
    if not artifacts:
        print(f"No debug artifacts found in {output_dir.relative_to(repo_root)}.", file=sys.stderr)
        return 1
    errors: list[str] = []
    for artifact_path in artifacts:
        artifact_label = artifact_path.relative_to(repo_root)
        try:
            validate_debug_artifact(artifact_path, collect_all=args.report_all)
        except ValidationError as exc:
            errors.append(f"Invalid debug artifact {artifact_label}: {exc}")
            continue
        print(f"Validated debug artifact {artifact_label}.")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
