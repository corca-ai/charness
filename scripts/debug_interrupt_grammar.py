"""Grammar for a debug artifact's `## Seam Risk` / `## Interrupt Decision` blocks.

Split out of ``validate_debug_artifact.py`` when the #636 one-pass reporting work
pushed that file past its length cap. The grouping is the concept, not the spill:
everything here answers "does this marker/enum block spell the interrupt contract",
and the validator keeps artifact-level shape (sections, dates, pointers, CLI).

Reporting contract (#636): marker and enum deviations are COLLECTED into one
report — each message naming the observed value or the case near-miss — so one
gate run teaches the full accepted shape instead of one repair cycle per line.
Blind class: the near-miss detection only sees CASE variants of the exact prefix
text; a reworded marker, a marker missing its ``- `` bullet, or a marker in the
wrong section still reports as plainly missing.

Enum single-sourcing (#366): the Risk Class / Generalization Pressure taxonomy is
imported from ``risk_interrupt_lib`` — the closeout consumer — never hand-copied.
"""

from __future__ import annotations


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index

_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
ALLOWED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.ALLOWED_RISK_CLASSES
FORCED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.FORCED_RISK_CLASSES
ALLOWED_GENERALIZATION_PRESSURE = _scripts_risk_interrupt_lib_module.ALLOWED_GENERALIZATION_PRESSURE
_parse_risk_classes = _scripts_risk_interrupt_lib_module._parse_risk_classes


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
    """Extract every `- Marker: value` line, reporting ALL marker problems at once.

    One raise per missing marker made an author repair the same section once per
    gate run (#636): the first missing prefix hid its siblings, and a natural
    case variant (`- Non-claims:` for `- Non-Claims:`) read as "missing" with no
    hint that the line was already there. Blind class: see the module docstring.
    """
    values: dict[str, str] = {}
    problems: list[str] = []
    for prefix in prefixes:
        line = next((line for line in lines if line.startswith(prefix)), None)
        if line is None:
            near_miss = next(
                (line for line in lines if line.lower().startswith(prefix.lower())), None
            )
            if near_miss is not None:
                problems.append(
                    f"missing required line `{prefix}...` (found `{near_miss.split(':')[0]}:` — "
                    "marker prefixes are case-sensitive)"
                )
            else:
                problems.append(f"missing required line `{prefix}...`")
            continue
        value = line[len(prefix) :].strip()
        if not value:
            problems.append(f"`{prefix}...` must not be empty")
            continue
        values[prefix] = value
    if problems:
        raise ValidationError("; ".join(problems))
    return values


def _extract_interrupt_marker_values(
    seam_lines: list[str], interrupt_lines: list[str], problems: list[str]
) -> tuple[dict[str, str], dict[str, str]]:
    """Extract both marker blocks, merging their reports instead of racing them.

    A raise from the first extraction used to hide the second block's problems
    entirely (#636); here each block contributes to the same one-pass report.
    """
    seam_values: dict[str, str] = {}
    interrupt_values: dict[str, str] = {}
    try:
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
    except ValidationError as exc:
        problems.append(str(exc))
    try:
        interrupt_values = extract_prefixed_values(
            interrupt_lines,
            (
                "- Critique Required: ",
                "- Next Step: ",
                "- Handoff Artifact: ",
            ),
        )
    except ValidationError as exc:
        problems.append(str(exc))
    return seam_values, interrupt_values


def _forced_interrupt_problems(
    *,
    risk_classes: tuple[str, ...],
    generalization_pressure: str,
    critique_required: str,
    next_step: str,
    interrupt_values: dict[str, str],
) -> list[str]:
    """The forced-interrupt floor, reported as a batch beside the enum checks."""
    forced = bool(
        set(risk_classes) & FORCED_RISK_CLASSES or generalization_pressure == "factor-now"
    )
    if not forced:
        return []
    problems: list[str] = []
    if critique_required != "yes":
        problems.append("forced risk interrupt must record `Critique Required: yes`")
    if next_step != "spec":
        problems.append("forced risk interrupt must record `Next Step: spec`")
    handoff = interrupt_values.get("- Handoff Artifact: ", "")
    # A missing Handoff marker is already in the report from extraction; only a
    # PRESENT value with the wrong shape earns its own line.
    if handoff and (
        not handoff.startswith("charness-artifacts/spec/") or not handoff.endswith(".md")
    ):
        problems.append(
            "forced risk interrupt must point `Handoff Artifact` at `charness-artifacts/spec/*.md`"
        )
    return problems


def validate_current_interrupt_sections(lines: list[str]) -> None:
    if "## Seam Risk" not in lines or "## Interrupt Decision" not in lines:
        raise ValidationError(
            "current debug artifact must include `## Seam Risk` and `## Interrupt Decision`"
        )

    seam_lines = section_lines(
        lines, "## Seam Risk", ("## Seam Risk", "## Interrupt Decision", "## Prevention")
    )
    interrupt_lines = section_lines(
        lines,
        "## Interrupt Decision",
        ("## Seam Risk", "## Interrupt Decision", "## Prevention", "## Related Prior Incidents"),
    )
    # Collected, not raised one at a time: sequential raises made every marker
    # and enum deviation cost its own repair/validate cycle (#636). The two
    # extractions merge their reports, and each enum message names the observed
    # value, so one report teaches the full accepted shape. An enum whose marker
    # is missing is skipped rather than guessed at — its message is already in
    # the report as the missing marker itself.
    problems: list[str] = []
    seam_values, interrupt_values = _extract_interrupt_marker_values(
        seam_lines, interrupt_lines, problems
    )
    risk_classes = tuple(
        part.strip() for part in seam_values.get("- Risk Class: ", "").split(",") if part.strip()
    )
    if "- Risk Class: " in seam_values and not risk_classes:
        problems.append("`Risk Class` must list at least one value")
    invalid = [value for value in risk_classes if value not in ALLOWED_RISK_CLASSES]
    if invalid:
        problems.append(f"`Risk Class` contains unknown values (found `{', '.join(invalid)}`)")
    if "none" in risk_classes and len(risk_classes) > 1:
        problems.append("`Risk Class: none` cannot be combined with other values")

    generalization_pressure = seam_values.get("- Generalization Pressure: ", "")
    if seam_values and generalization_pressure not in ALLOWED_GENERALIZATION_PRESSURE:
        problems.append(
            "`Generalization Pressure` must be `none`, `monitor`, or `factor-now` "
            f"(found `{generalization_pressure}`)"
        )

    critique_required = interrupt_values.get("- Critique Required: ", "")
    if interrupt_values and critique_required not in {"yes", "no"}:
        problems.append(f"`Critique Required` must be `yes` or `no` (found `{critique_required}`)")
    next_step = interrupt_values.get("- Next Step: ", "")
    if interrupt_values and next_step not in {"impl", "spec"}:
        problems.append(f"`Next Step` must be `impl` or `spec` (found `{next_step}`)")

    # `Resolution` is OPTIONAL for backward-compat (legacy artifacts predate it):
    # a missing field is read by plan_debug_run.py as an open investigation to
    # continue. When the author DOES declare it, constrain it to the lifecycle
    # enum the planner consumes (`open` to continue, `resolved` to demote the
    # pointer to a prior incident so it stops hijacking a fresh bug).
    resolution_line = next(
        (line for line in interrupt_lines if line.startswith("- Resolution: ")), None
    )
    if resolution_line is not None:
        # Match the planner's case-folding (plan_debug_run.py lowercases before the
        # `== "resolved"` compare) so the validator never rejects a value the
        # consumer would honor — a producer/consumer mismatch in its own right.
        resolution = resolution_line[len("- Resolution: ") :].strip().lower()
        if resolution not in {"open", "resolved"}:
            problems.append(f"`Resolution` must be `open` or `resolved` (found `{resolution}`)")

    problems.extend(
        _forced_interrupt_problems(
            risk_classes=risk_classes,
            generalization_pressure=generalization_pressure,
            critique_required=critique_required,
            next_step=next_step,
            interrupt_values=interrupt_values,
        )
    )
    if problems:
        raise ValidationError("; ".join(problems))


def validate_dated_seam_risk_enums(lines: list[str]) -> None:
    """Enforce the `risk_interrupt_lib` Risk Class / Generalization Pressure
    taxonomy on dated debug records that carry a `## Seam Risk` section.

    `risk_interrupt_lib.parse_debug_interrupt` — consumed by the quality
    artifact validators via the current-pointer `latest.md` — rejects an
    off-taxonomy `Risk Class` / `Generalization Pressure`. The dated author-time
    path did not run that enum check, so an off-taxonomy value passed at write
    time and only surfaced repo-wide later, far from the artifact (#366).
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
    seam_lines = section_lines(
        lines, "## Seam Risk", ("## Seam Risk", "## Interrupt Decision", "## Prevention")
    )
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
