#!/usr/bin/env python3

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
_prepare_packet_markdown_kind = import_repo_module(__file__, "scripts.prepare_packet_markdown_kind")
_skill_markdown_lib = import_repo_module(__file__, "scripts.skill_markdown_lib")
ValidationError = _scripts_artifact_validator_module.ValidationError
report_validation_failure = _scripts_artifact_validator_module.report_validation_failure
git_changed_paths = _scripts_artifact_validator_module.git_changed_paths
run_validation_checks = _scripts_artifact_validator_module.run_validation_checks
run_changed_artifact_validator = _scripts_artifact_validator_module.run_changed_artifact_validator
validate_sibling_followups = _scripts_artifact_validator_module.validate_sibling_followups
# Colon-anchored so prose discussing the concept is not mistaken for a tag; the
# capture is deliberately permissive (anything up to whitespace/punctuation) because
# this scanner must SEE the malformed slugs that the strict parser rejects.
_RECURRENCE_CLASS_TAG = re.compile(r"(?i)\brecurrence-class[ \t]*:[ \t]*(?P<value>[^\s)\]]*)")
# The shape the index's parser accepts, anchored as a FULL match by the caller.
_STRICT_SLUG = re.compile(r"(?i)[a-z0-9][a-z0-9-]*")
file_is_prepare_packet_markdown_kind = _prepare_packet_markdown_kind.file_is_prepare_packet_markdown_kind

# Shared single source of the disposition-form grammar (#329); imported same-root
# so the session-retro `## Next Improvements` floor never forks achieve parsing.
disposition_form = import_repo_module(__file__, "scripts.disposition_form")

NEXT_IMPROVEMENTS_HEADING = "## Next Improvements"
DISPOSITION_FORM_REFERENCE = "skills/public/achieve/references/goal-artifact.md (#329 disposition-form floor)"
# Recurrence-lineage floor for standalone retros: the symmetric extension of the
# achieve rung 1d to a session retro's `## Next Improvements`. Its own enforce-from
# date lands the day after this floor so every existing retro (all dated on or
# before the landing day) is grandfathered and the broad gate stays green; only
# retros dated on/after it must carry a lineage marker on issue-form dispositions.
RECURRENCE_LINEAGE_RULE_DATE = date(2026, 6, 9)
PERSISTED_FORM_RULE_DATE = date(2026, 6, 25)
_DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\b")
_PERSISTED_LINE = re.compile(r"^Persisted:\s+(yes|no):\s+\S.+$")
RETRO_PREPARE_PACKET_KIND = "charness.retro_prepare_packet"
RETRO_PREPARE_PACKET_TITLE_RE = re.compile(r"^# Retro Prepare Packet(?:\s+—\s+\S.*)?$")

RETRO_ARTIFACT_PREFIX = "charness-artifacts/retro/"
GENERATED_DIGEST = "recent-lessons.md"
SIBLING_BOUNDARY_HEADINGS = (
    "## Context",
    "## Window",
    "## Evidence Summary",
    "## Waste",
    "## Critical Decisions",
    "## Trends vs Last Retro",
    "## Expert Counterfactuals",
    "## Next Improvements",
    "## Persisted",
)
SIBLING_SOURCE_REFERENCE = "skills/public/retro/references/waste-sibling-scan.md"
PERSISTED_FORM_REFERENCE = "skills/public/retro/references/trigger-and-persistence.md"


def changed_paths(repo_root: Path) -> list[str]:
    return git_changed_paths(repo_root, artifact_label="retro")


def _is_session_artifact(relpath: str) -> bool:
    if not relpath.startswith(RETRO_ARTIFACT_PREFIX) or not relpath.endswith(".md"):
        return False
    tail = relpath[len(RETRO_ARTIFACT_PREFIX) :]
    if "/" in tail:  # skip history/ and other nested archives
        return False
    return tail != GENERATED_DIGEST


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        return [
            path
            for path in sorted(
                path
                for path in (repo_root / RETRO_ARTIFACT_PREFIX).glob("*.md")
                if path.name != GENERATED_DIGEST
            )
            if not file_is_prepare_packet_markdown_kind(
                path,
                expected_kind=RETRO_PREPARE_PACKET_KIND,
                expected_title_re=RETRO_PREPARE_PACKET_TITLE_RE,
            )
        ]
    candidates: list[Path] = []
    for relpath in paths:
        if _is_session_artifact(relpath):
            path = repo_root / relpath
            if not file_is_prepare_packet_markdown_kind(
                path,
                expected_kind=RETRO_PREPARE_PACKET_KIND,
                expected_title_re=RETRO_PREPARE_PACKET_TITLE_RE,
            ) and path.is_file():
                candidates.append(path)
    return sorted(candidates)


def _retro_date(lines: list[str]) -> date | None:
    """Parse the retro's ``Date: YYYY-MM-DD`` line; ``None`` when absent/malformed."""
    for line in lines[:5]:
        match = _DATE_LINE.match(line.strip())
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
    return None


def _date_from_filename(path: Path) -> date | None:
    """The leading ``YYYY-MM-DD`` of the retro filename, ``None`` when absent."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _retro_observed_date(path: Path, lines: list[str]) -> date | None:
    """The retro's effective date for grandfathering: the in-body ``Date:`` line,
    else the leading ``YYYY-MM-DD`` of the filename. Many frozen historical retros
    predate the ``Date:`` header convention but are still dated by filename, so the
    filename fallback keeps them grandfathered (Goodhart Non-Goal). Only a retro
    with neither falls through to ``None`` -> fail-closed enforcement, which also
    blocks dodging the floor by stripping the date line of a current-dated file."""
    return _retro_date(lines) or _date_from_filename(path)


def _next_improvements_body(lines: list[str]) -> str:
    """Return the ``## Next Improvements`` section body (heading excluded), from
    its heading to the next ``## `` heading or EOF. Empty string when absent."""
    start = None
    for index, line in enumerate(lines):
        if line.strip() == NEXT_IMPROVEMENTS_HEADING:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def validate_disposition_forms(lines: list[str], observed_date: date | None) -> None:
    """Fail when an in-scope retro's ``## Next Improvements`` carries a disposition
    line in an invalid form (#329). Grandfathered for retros dated before the
    form rule date; form/enum only — substance stays the reviewer's job."""
    if not disposition_form.is_form_enforced(observed_date):
        return
    invalid = disposition_form.invalid_dispositions(_next_improvements_body(lines))
    if not invalid:
        return
    offenders = "; ".join(f"`{entry['marker']}: {entry['value'][:80]}`" for entry in invalid)
    raise ValidationError(
        f"`{NEXT_IMPROVEMENTS_HEADING}` has {len(invalid)} disposition line(s) in an invalid form "
        f"(offenders: {offenders}); each disposition must be one of "
        f"{disposition_form.VALID_FORM_SUMMARY} — a bare `memory`/prose-only disposition is rejected. "
        f"See {DISPOSITION_FORM_REFERENCE}."
    )


def validate_recurrence_lineage(lines: list[str], observed_date: date | None) -> None:
    """Fail when an in-scope retro's ``## Next Improvements`` routes an improvement
    to ``issue #N`` without a recurrence-lineage marker — the standalone-retro
    extension of the achieve de-launder (rung 1d). Presence/enum only via the shared
    ``has_recurrence_lineage``; whether a ``novel:`` claim is true stays the
    reviewer's job, never this floor's (the content-classifier guardrail). Its own
    enforce-from date grandfathers every retro frozen before it; fail-CLOSED on an
    undatable retro mirrors the form floor."""
    enforced = observed_date is None or observed_date >= RECURRENCE_LINEAGE_RULE_DATE
    if not enforced:
        return
    missing = [
        entry
        for entry in disposition_form.scan_dispositions(_next_improvements_body(lines))
        if entry["verdict"]["kind"] == "issue" and not disposition_form.has_recurrence_lineage(entry["value"])
    ]
    if not missing:
        return
    offenders = "; ".join(f"`{entry['marker']}: {entry['value'][:80]}`" for entry in missing)
    raise ValidationError(
        f"`{NEXT_IMPROVEMENTS_HEADING}` has {len(missing)} `issue` disposition(s) lacking "
        f"{disposition_form.RECURRENCE_LINEAGE_SUMMARY} (offenders: {offenders}); each issue-routed "
        "disposition must carry it (e.g. `issue #N (novel: <why no matching recurring class>)` or "
        "`issue #N (recurs: <lineage>)`) so a re-file of a known recurring class cannot launder as a "
        "fresh narrow issue. Presence-only — the reviewer judges whether a `novel:` claim is a re-file."
    )


def validate_recurrence_class_slugs(lines: list[str]) -> None:
    """Fail a `recurrence-class:` tag whose slug the index cannot parse.

    The tag is the machine identity that lets a re-worded lesson keep its recurrence
    count, so a typo must be loud rather than silent: an unparseable slug simply does
    not match `RECURRENCE_CLASS_RE`, and the lesson would fall back to surface-text
    grouping -- the exact defect the tag exists to remove, but now invisible because
    the author believes they tagged it.

    Anchored on the token FOLLOWED BY A COLON, so prose that merely discusses
    "a recurrence-class that has bitten K times" is not a tag and is not scanned.
    Slug shape only; whether two bullets really share a concept stays the author's
    and reviewer's judgment.
    """
    offenders: list[str] = []
    for raw in lines:
        for match in _RECURRENCE_CLASS_TAG.finditer(raw):
            # Full-match the whole authored value, not just "does the parser find
            # something". `recurrence-class: Bad_Slug!` parses to the class `bad`
            # because the strict pattern happily matches a PREFIX -- so a typo would
            # silently create a wrong class instead of failing, which is worse than
            # no tag at all.
            if not _STRICT_SLUG.fullmatch(match.group("value")):
                offenders.append(match.group(0).strip())
    if not offenders:
        return
    joined = "; ".join(f"`{offender}`" for offender in offenders)
    raise ValidationError(
        f"{len(offenders)} malformed `recurrence-class:` tag(s) (offenders: {joined}); the slug must "
        "be lowercase alphanumeric with internal hyphens (e.g. `recurrence-class: derived-surface-batching`) "
        "or the lesson-selection index silently falls back to surface-text grouping and the tag buys nothing"
    )


def validate_persisted_form(lines: list[str], observed_date: date | None) -> None:
    """Fail future retros whose persisted status is not machine-readable.

    Historical retro artifacts used several human-readable shapes, including
    undated legacy files, so the rule is grandfathered by observable date. A
    current-dated filename still triggers the rule even if the body omits
    `Date:`.
    """
    enforced = observed_date is not None and observed_date >= PERSISTED_FORM_RULE_DATE
    if not enforced:
        return
    section = [
        line.strip()
        for line in _skill_markdown_lib.extract_h2_section_lines("\n".join(lines), "Persisted")
        if line.strip()
    ]
    if not section:
        raise ValidationError(
            f"`## Persisted` must state `Persisted: yes: <path>` or `Persisted: no: <reason>`. "
            f"See {PERSISTED_FORM_REFERENCE}."
        )
    persisted_lines = [line for line in section if line.startswith("Persisted:")]
    if len(persisted_lines) != 1 or not _PERSISTED_LINE.match(persisted_lines[0]):
        offenders = "; ".join(persisted_lines) if persisted_lines else "<missing>"
        raise ValidationError(
            f"`## Persisted` has invalid persisted status ({offenders}); use "
            f"`Persisted: yes: <path>` or `Persisted: no: <reason>`. "
            f"See {PERSISTED_FORM_REFERENCE}."
        )


def validate_retro_artifact(path: Path, *, collect_all: bool = False) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    observed_date = _retro_observed_date(path, lines)
    checks = (
        lambda: validate_sibling_followups(
            lines,
            boundary_headings=SIBLING_BOUNDARY_HEADINGS,
            source_reference=SIBLING_SOURCE_REFERENCE,
        ),
        lambda: validate_disposition_forms(lines, observed_date),
        lambda: validate_recurrence_lineage(lines, observed_date),
        lambda: validate_persisted_form(lines, observed_date),
        lambda: validate_recurrence_class_slugs(lines),
    )
    # collect_all surfaces every violation in one pass (the CLI default) so a
    # multi-rule retro draft is fixed in one edit instead of one rule per gate
    # run. --fail-fast opts back into stopping at the first violation.
    run_validation_checks(checks, collect_all=collect_all, artifact_label="retro artifact")


def main() -> int:
    # Collect on BOTH axes: every rule inside one retro, and every failing retro
    # in the batch. Stopping at the first of either makes the author pay one gate
    # run per problem.
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked retro session artifact.",
        artifact_label="retro artifact",
        changed_paths_fn=changed_paths,
        candidate_paths_fn=candidate_paths,
        validate_factory=lambda run: (
            lambda artifact: validate_retro_artifact(artifact, collect_all=run.collect_all)
        ),
        fail_fast_help=(
            "Stop at the first rule violation instead of reporting every violation in one pass."
        ),
        owned_prefix=RETRO_ARTIFACT_PREFIX,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        raise SystemExit(report_validation_failure(str(exc), artifact_type="retro"))
