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
ALLOWED_RISK_CLASSES = frozenset(
    {
        "none",
        "external-seam",
        "host-disproves-local",
        "repeated-symptom",
        "operator-visible-recovery",
        "contract-freeze-risk",
    }
)
FORCED_RISK_CLASSES = frozenset(
    {
        "external-seam",
        "host-disproves-local",
        "repeated-symptom",
    }
)
ALLOWED_GENERALIZATION_PRESSURE = frozenset({"none", "monitor", "factor-now"})


def validate_candidate_causes(lines: list[str]) -> None:
    start = find_index(lines, "## Candidate Causes") + 1
    end = find_index(lines, "## Hypothesis")
    bullets = [line.strip() for line in lines[start:end] if line.strip().startswith("- ")]
    if len(bullets) < 3:
        raise ValidationError("`## Candidate Causes` must list at least three plausible causes")


SIBLING_DECISION_FOLLOWUP = "valid follow-up outside the slice"
SIBLING_TRIVIAL_SHORT_CIRCUIT = "n/a"  # the bullet must contain "n/a" plus "trivial fix" + "no plausible siblings"


def _is_sibling_decision_bullet(line: str) -> bool:
    """Bullet entries are `- ...` lines that carry a `decision:` field.

    Prose paragraphs that mention the decision phrase are excluded so authors
    can quote the rule in commentary without tripping the validator.
    """
    stripped = line.lstrip()
    return stripped.startswith("- ") and "decision:" in stripped.lower()


def _is_trivial_short_circuit(line: str) -> bool:
    """`n/a — trivial fix; no plausible siblings` short-circuit, dash-agnostic."""
    lowered = line.lower()
    return (
        "n/a" in lowered
        and "trivial fix" in lowered
        and "no plausible siblings" in lowered
    )


def validate_sibling_followups(lines: list[str]) -> None:
    """Fail when a `valid follow-up outside the slice` sibling lacks a follow-up id.

    `## Sibling Search` is a list of `- <axis>: <location> | decision: ... | proof: ...`
    bullets. When `decision: valid follow-up outside the slice` appears on a
    bullet line, the same bullet must also carry a `follow-up: <issue-url>` or
    `follow-up: deferred <anchor>` field. The follow-up may also be expressed
    on the immediately following continuation line.

    Prose paragraphs that mention the decision phrase outside a bullet are
    ignored so authors can cite the rule itself. Decision matching is
    case-insensitive so `Valid Follow-Up Outside The Slice` cannot bypass.
    """
    try:
        start = find_index(lines, "## Sibling Search") + 1
    except ValidationError:
        return
    end = len(lines)
    for candidate in ("## Seam Risk", "## Interrupt Decision", "## Prevention", "## Related Prior Incidents"):
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start:
            end = min(end, index)
    section = lines[start:end]
    if any(_is_trivial_short_circuit(line) for line in section):
        return
    for index, raw in enumerate(section):
        line = raw.rstrip()
        if not _is_sibling_decision_bullet(line):
            continue
        if SIBLING_DECISION_FOLLOWUP not in line.lower():
            continue
        if _line_has_valid_followup(line):
            continue
        peek = section[index + 1] if index + 1 < len(section) else ""
        if _line_has_valid_followup(peek):
            continue
        offender = line.strip().lstrip("- ").strip()
        raise ValidationError(
            "`## Sibling Search` entry classified `valid follow-up outside the slice` must record a "
            "`follow-up: <issue-url>` or `follow-up: deferred <handoff-anchor>` identifier on the same "
            f"bullet (offender: `{offender[:120]}`); see "
            "skills/public/debug/references/sibling-search.md."
        )


def _line_has_valid_followup(line: str) -> bool:
    lower = line.lower()
    if "follow-up:" not in lower:
        return False
    tail = lower.split("follow-up:", 1)[1].strip()
    return _is_valid_followup_tail(tail)


def _is_valid_followup_tail(tail: str) -> bool:
    """`follow-up:` payload must name an identifier or `deferred <anchor>`.

    Bare tokens like `deferred` (without an anchor) silently re-export the
    follow-up to the next session — that is the exact failure the rule blocks.
    """
    parts = tail.split(None, 1)
    if not parts:
        return False
    if parts[0] == "deferred":
        return len(parts) > 1 and bool(parts[1].strip())
    return True


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


def validate_debug_artifact(path: Path) -> None:
    lines = read_lines(path)
    validate_title(
        lines,
        title_predicate=lambda line: line.startswith("# ") and "debug" in line.lower(),
        error_message="debug artifact must start with a `# ... Debug ...` heading",
    )
    validate_date_line(lines)
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="debug artifact")
    if path.name == "latest.md":
        required_sections = (
            REQUIRED_SECTIONS[:8]
            + CURRENT_DIAGNOSIS_SECTIONS
            + CURRENT_INTERRUPT_SECTIONS
            + ("## Prevention",)
        )
        validate_exact_h2_sections(lines, required_sections, optional_sections=OPTIONAL_SECTIONS)
        validate_nonempty_sections(lines, required_sections)
        validate_candidate_causes(lines)
        validate_sibling_followups(lines)
        validate_current_interrupt_sections(lines)
        return

    validate_section_order(lines, REQUIRED_SECTIONS)
    validate_nonempty_sections(lines, REQUIRED_SECTIONS)
    validate_candidate_causes(lines)
    validate_sibling_followups(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
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
            validate_debug_artifact(artifact_path)
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
