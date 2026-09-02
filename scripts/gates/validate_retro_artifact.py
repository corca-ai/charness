#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path


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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
_prepare_packet_markdown_kind = import_repo_module(__file__, "scripts.gates_support.prepare_packet_markdown_kind")
# One home for "what date does this artifact grandfather on" across every dated
# artifact family; see `_retro_observed_date`.
_enforcement_scope = import_repo_module(__file__, "scripts.review.critique_enforcement_scope")
# One home for "the lines of a markdown section", shared with the critique and
# ideation validators.
_sections = import_repo_module(__file__, "scripts.core.markdown_sections")
_skill_markdown_lib = import_repo_module(__file__, "scripts.core.skill_markdown_lib")
# Where this repo keeps its retros, resolved from its own adapter rather than from a
# literal written here. `retro_artifact_prefix` is used below; `DEFAULT_RETRO_ARTIFACT_PREFIX`
# is re-exported for tests that assert the fallback identity. An earlier comment claimed
# `plan_retro_run` and `seed_retro_memory` needed one import site for these.
_output_dir = import_repo_module(__file__, "scripts.retro_output_dir_lib")
DEFAULT_RETRO_ARTIFACT_PREFIX = _output_dir.DEFAULT_RETRO_ARTIFACT_PREFIX
retro_artifact_prefix = _output_dir.retro_artifact_prefix
_adapter_version_verdict = import_repo_module(__file__, "scripts.adapter_version_verdict")


def _unspeakable_adapter_version(repo_root: Path) -> str | None:
    """Refuse before scoping when this repo's retro adapter declares an unreadable
    version. Without it, `retro_artifact_prefix` silently resolves to the shipped
    default, `candidate_paths` filters every named artifact out as unowned, and the run
    reports `Validated 0 retro artifact(s).` exit 0 over a retro it was handed."""
    return _adapter_version_verdict.unspeakable_version_message(
        _output_dir.load_retro_adapter, repo_root, adapter_name="retro-adapter.yaml"
    )
# Which dated floors are switched on for this repo. Re-exported because
# `plan_retro_run` loads this module.
_floor_scope = import_repo_module(__file__, "scripts.retro_floor_scope_lib")
NEXT_IMPROVEMENTS_HEADING = _floor_scope.NEXT_IMPROVEMENTS_HEADING
RECURRENCE_LINEAGE_RULE_DATE = _floor_scope.RECURRENCE_LINEAGE_RULE_DATE
PERSISTED_FORM_RULE_DATE = _floor_scope.PERSISTED_FORM_RULE_DATE
NORTH_STAR_RULE_DATE = _floor_scope.NORTH_STAR_RULE_DATE
NORTH_STAR_HEADING = _floor_scope.NORTH_STAR_HEADING
date_activated_rules = _floor_scope.date_activated_rules
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
# so the retro `## Next Improvements` floor never forks achieve parsing.
disposition_form = import_repo_module(__file__, "scripts.core.disposition_form")

DISPOSITION_FORM_REFERENCE = "skills/public/achieve/references/goal-artifact.md (#329 disposition-form floor)"
#: The path `north_star_reference` names when the repo being validated has this file.
#: Deliberately NOT charness's internal `<authoring-repo>/...` spelling: a consuming
#: author reads that as a directory they do not have, and the refusal message is the
#: surface they hit when they fail, which is when a readable path matters most. The
#: comment here used to describe the constant as "superseded", which read as a warning
#: against the live value it sits on; the superseded thing was the other spelling.
NORTH_STAR_DOC = "docs/design-north-star.md"
_PERSISTED_LINE = re.compile(r"^Persisted:\s+(yes|no):\s+\S.+$")
RETRO_PREPARE_PACKET_KIND = "charness.retro_prepare_packet"
RETRO_PREPARE_PACKET_TITLE_RE = re.compile(r"^# Retro Prepare Packet(?:\s+—\s+\S.*)?$")

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


def _is_session_artifact(relpath: str, prefix: str) -> bool:
    if not relpath.startswith(prefix) or not relpath.endswith(".md"):
        return False
    tail = relpath[len(prefix) :]
    if "/" in tail:  # skip history/ and other nested archives
        return False
    return tail != GENERATED_DIGEST


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    prefix = retro_artifact_prefix(repo_root)
    if all_artifacts:
        # A missing output directory is refused, never reported as a clean sweep. The
        # debug sibling ignores its adapter's `valid` flag for good reasons this module
        # copied -- but what made that safe there is `_debug_artifacts` exiting 1 on a
        # directory that does not exist, and copying the permissive read without the
        # backstop meant one typo'd `output_dir` (`[unclosed` parses to a plain STRING
        # with `valid: True`) globbed nothing and printed green over the whole corpus.
        # `--all` IS the corpus audit; it must not be satisfiable by looking nowhere.
        directory = repo_root / prefix.rstrip("/")
        if not directory.is_dir():
            print(
                f"No retro output directory at {prefix.rstrip('/')} (repo root {repo_root}). "
                "This is not a clean corpus: nothing was opened. Check the retro adapter's "
                "`output_dir`, or the --repo-root this run was given.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        return [
            path
            for path in sorted(
                path
                for path in (repo_root / prefix).glob("*.md")
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
        if _is_session_artifact(relpath, prefix):
            path = repo_root / relpath
            if not file_is_prepare_packet_markdown_kind(
                path,
                expected_kind=RETRO_PREPARE_PACKET_KIND,
                expected_title_re=RETRO_PREPARE_PACKET_TITLE_RE,
            ) and path.is_file():
                candidates.append(path)
    return sorted(candidates)


def _retro_observed_date(path: Path, lines: list[str]) -> date | None:
    """The retro's effective date for grandfathering, through the shared rule.

    This used to be a body-first ``or`` chain over its own two parsers, which is
    the exact shape C2 replaced on the critique surface: every floor below
    grandfathers on ``date < RULE_DATE``, so whichever channel reads EARLIER buys
    the exemption — and the body ``Date:`` line is author-written. A retro could
    date itself out of the disposition-form, recurrence-lineage and persisted-form
    floors at once with one line, while its filename said today. The rule is now
    the LATER of the two channels, single-sourced with the critique surface so the
    two halves cannot drift again.

    Frozen historical retros that predate the ``Date:`` header are still dated by
    filename and stay grandfathered (Goodhart Non-Goal). A retro with NEITHER
    channel falls through to ``None`` -> fail-closed enforcement, which also blocks
    dodging a floor by stripping the date line off a current-dated file.
    """
    return _enforcement_scope.observed_date(path, "\n".join(lines))


def _next_improvements_body(lines: list[str]) -> str:
    """Return the ``## Next Improvements`` section body (heading excluded), from
    its heading to the next ``## `` heading or EOF. Empty string when absent.

    Through the shared section reader, which additionally ignores a heading inside a
    fenced block — a retro that QUOTES the disposition form in a fence was having the
    quoted example read as its own declarations."""
    return "\n".join(_sections.section_lines(lines, NEXT_IMPROVEMENTS_HEADING))


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


def _repo_root_for(path: Path) -> Path | None:
    """The repo root a retro artifact at ``<root>/charness-artifacts/retro/x.md`` implies.

    ``None`` when the path is not in that layout -- a test fixture, an ad-hoc file --
    because guessing a root there would name a design doc that has nothing to do with
    the artifact being validated.
    """
    resolved = path.resolve()
    if len(resolved.parents) < 3 or resolved.parent.name != "retro":
        return None
    if resolved.parents[1].name != "charness-artifacts":
        return None
    return resolved.parents[2]


def north_star_reference(repo_root: Path | None) -> str:
    """How the refusal message names the governing design standard, per repo.

    Mirrors the scaffold's `_north_star_prompt`: name the real file when the repo
    being validated has one, and otherwise describe what to go find with no
    placeholder at all. The two surfaces disagreed for one commit -- the scaffold
    dropped `<authoring-repo>/` while the refusal kept it -- which put the discarded
    spelling on the surface a consuming author reads when they fail.
    """
    if repo_root is not None and (repo_root / NORTH_STAR_DOC).is_file():
        return f"`{NORTH_STAR_DOC}` in this repo"
    return "whatever this repo names as its own (design principles, invariants)"


def validate_north_star_alignment(
    lines: list[str], observed_date: date | None, repo_root: Path | None = None
) -> None:
    """Fail a retro that never asked what the north star says about this work.

    The design standard is the repo's governing frame, so a retrospective that
    does not consult it is reviewing the work against nothing but itself. This
    is the cheapest possible floor -- a section with content -- and it
    deliberately does not judge the content: naming which facets held, which
    were mis-applied, and which failure signature the run walked into is
    judgment work, and a validator that scored it would be pretending.
    """
    enforced = observed_date is not None and observed_date >= NORTH_STAR_RULE_DATE
    if not enforced:
        return
    section = [
        line.strip()
        for line in _skill_markdown_lib.extract_h2_section_lines(
            "\n".join(lines), NORTH_STAR_HEADING
        )
        if line.strip()
    ]
    substantive = [line for line in section if not line.startswith(("<!--", "TODO", "TBD"))]
    if not substantive:
        raise ValidationError(
            f"retro artifact has no `## {NORTH_STAR_HEADING}` section with content; every retro "
            f"consults its governing design standard ({north_star_reference(repo_root)}) "
            "and records what it found — which "
            "facets held, which were mis-applied, and any failure signature the run walked into. "
            "Prose in the skill was not enough: two consecutive retros shipped without it."
        )

def validate_retro_artifact(
    path: Path,
    *,
    collect_all: bool = False,
    repo_root: Path | None = None,
) -> None:
    """Validate one retro artifact.

    ``repo_root`` is the RUN's, bound once by the factory below rather than re-derived
    per artifact: re-resolving the adapter per artifact is the x150 regression the debug
    sibling records.
    """
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
        # Repo root derived from the artifact's OWN location rather than from this
        # script's, because the two differ exactly where it matters: an exported copy
        # validating a consuming repo's retro would otherwise resolve `REPO_ROOT` to the
        # plugin tree and name charness's design doc at a consumer.
        # The RUN's root when there is one: `--repo-root` is the repo being validated,
        # while `_repo_root_for` can only infer it from a canonical layout and returns
        # None for every consumer that declares another `output_dir` -- which silently
        # dropped the per-repo design-doc name this argument exists to carry.
        lambda: validate_north_star_alignment(
            lines, observed_date, repo_root if repo_root is not None else _repo_root_for(path)
        ),
    )
    # collect_all surfaces every violation in one pass (the CLI default) so a
    # multi-rule retro draft is fixed in one edit instead of one rule per gate
    # run. --fail-fast opts back into stopping at the first violation.
    run_validation_checks(checks, collect_all=collect_all, artifact_label="retro artifact")


def _validate_factory(run):
    """Bind the per-RUN adapter resolution once, not once per artifact.

    The debug sibling measured a per-artifact adapter read at ~150 reloads on a
    full sweep. One resolution per run keeps the candidate scope stable without
    adding another per-artifact lookup.
    """
    repo_root = run.repo_root
    return lambda artifact: validate_retro_artifact(
        artifact, collect_all=run.collect_all, repo_root=repo_root
    )


def main() -> int:
    # Collect on BOTH axes: every rule inside one retro, and every failing retro
    # in the batch. Stopping at the first of either makes the author pay one gate
    # run per problem.
    try:
        return run_changed_artifact_validator(
            default_repo_root=REPO_ROOT,
            all_help="Validate every checked retro artifact.",
            artifact_label="retro artifact",
            changed_paths_fn=changed_paths,
            candidate_paths_fn=candidate_paths,
            validate_factory=_validate_factory,
            fail_fast_help=(
                "Stop at the first rule violation instead of reporting every violation in one pass."
            ),
            # A CALLABLE, resolved after `--repo-root` is parsed: the prefix this
            # validator owns is the one the repo being validated declares, not the one
            # this file was written in.
            owned_prefix=retro_artifact_prefix,
            preflight=_unspeakable_adapter_version,
        )
    except ValidationError as exc:
        return report_validation_failure(str(exc), artifact_type="retro")


if __name__ == "__main__":
    raise SystemExit(main())
