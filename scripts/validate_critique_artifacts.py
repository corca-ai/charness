#!/usr/bin/env python3

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
_prepare_packet_markdown_kind = import_repo_module(__file__, "scripts.prepare_packet_markdown_kind")
ValidationError = _artifact_validator.ValidationError
report_validation_failure = _artifact_validator.report_validation_failure
git_changed_paths = _artifact_validator.git_changed_paths
is_valid_followup_tail = _artifact_validator.is_valid_followup_tail
run_changed_artifact_validator = _artifact_validator.run_changed_artifact_validator
run_validation_checks = _artifact_validator.run_validation_checks
file_is_prepare_packet_markdown_kind = _prepare_packet_markdown_kind.file_is_prepare_packet_markdown_kind

# Cross-surface probe (#408): consulted only when --changed-ref/--changed-path is passed.
_boundary_probe_lib = import_repo_module(__file__, "scripts.boundary_probe_lib")
_reviewed_input_binding = import_repo_module(__file__, "scripts.critique_reviewed_input_binding")
_reviewer_evidence = import_repo_module(__file__, "scripts.critique_reviewer_evidence")
REVIEWER_TIER_HEADING = _reviewer_evidence.REVIEWER_TIER_HEADING
REVIEWER_TIER_REQUIRED_FIELDS = _reviewer_evidence.REVIEWER_TIER_REQUIRED_FIELDS
REVIEWER_TIER_HOST_STATES = _reviewer_evidence.REVIEWER_TIER_HOST_STATES
DELIVERY_STATE_RULE_DATE = _reviewer_evidence.DELIVERY_STATE_RULE_DATE
DELIVERY_STATE_FIELD = _reviewer_evidence.DELIVERY_STATE_FIELD
DELIVERY_STATE_VALUES = _reviewer_evidence.DELIVERY_STATE_VALUES
DELIVERY_STATE_VALUES_SUMMARY = _reviewer_evidence.DELIVERY_STATE_VALUES_SUMMARY

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
CRITIQUE_PREPARE_PACKET_TITLE_RE = re.compile(r"^# Critique Prepare Packet(?:\s+—\s+\S.*)?$")
STRUCTURED_FINDINGS_HEADING = "## Structured Findings"
STRUCTURED_BINS = frozenset({"act-before-ship", "bundle-anyway", "over-worry", "valid-but-defer"})
STRUCTURED_EVIDENCE = frozenset({"strong", "moderate", "weak", "contested"})
STRUCTURED_ACTIONS = frozenset({"fix", "file-issue", "document", "defer"})
STRUCTURED_REQUIRED_FIELDS = ("bin", "evidence", "ref", "action", "note")
# Describe-first: rejections render this canonical entry form so an author fixes
# the whole entry once instead of discovering each required field by serial
# re-runs (the closeout-authoring-churn class).
STRUCTURED_FINDING_FORM = (
    "- <id> | bin: <bin> | evidence: <evidence> | ref: <path-or-line> | "
    "action: <action> | note: <one-line rationale>"
)
PACKET_CONSUMED_RE = re.compile(r"(?im)^\s*packet consumed\s*:\s*(?P<path>\S+)")
CRITIQUE_PREPARE_PACKET_KIND = "charness.critique_prepare_packet"
FORBIDDEN_SUBAGENT_BLOCKER_PHRASES = (
    "did not explicitly allow subagents",
    "explicit subagent allowance",
    "only permits spawning subagents when",
    "only permits spawning subagents after",
    "current session delegation policy",
    "current developer instruction only permits",
)
DELEGATION_CONTRACT_MARKERS = ("subagent delegation", "repo-mandated bounded fresh-eye subagent reviews are already delegated")
SIGNAL_HEADINGS = ("host signal", "tool signal")
PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na", "blocked"}

# Distinct-observer presence floor (counterweight-verified: an artifact with no
# `Fresh-eye satisfaction:` line skips every observer check below — the #386
# same-observer rubber stamp in file form). Enforce-from-date mirrors the
# established `disposition_form.DISPOSITION_FORM_RULE_DATE` /
# `validate_retro_artifact.RECURRENCE_LINEAGE_RULE_DATE` shape: this floor lands
# 2026-07-04, so enforcement begins the next day and every artifact dated
# on/before the landing day is grandfathered. Clone-safe: an in-file constant,
# not mtime.
FRESH_EYE_PRESENCE_RULE_DATE = date(2026, 7, 5)
# `nested-delegated` has no downstream evidence-linking check today (unlike
# `parent-delegated` -> Reviewer Tier Evidence, `blocked` -> host/tool signal
# detail) — presence/form-only per this floor's own boundary, so this is a
# known, accepted gap rather than a missed one; adding a required nested-run
# citation is a separate floor-addition call, not folded in here.
FRESH_EYE_TYPED_VALUES = ("parent-delegated", "nested-delegated", "blocked")
FRESH_EYE_TYPED_VALUES_SUMMARY = "`parent-delegated` / `nested-delegated` / `blocked <host-signal>`"
# Adversarial-review finding: a typed value whose remainder still carries an
# unedited `todo` (e.g. a scaffolded `parent-delegated (TODO confirm ...)`)
# must not satisfy the floor — that is an unedited stub silently claiming
# delegation, the exact same-observer rubber stamp (#386) this floor exists to
# stop. Mirrors this file's own `PLACEHOLDER_VALUES`/`"missing "` treatment.
FRESH_EYE_TODO_MARKER = "todo"
# Boundary-ownership presence floor (#408/#414/#416): every critique artifact
# records a typed `Verdict:` so a producer/consumer ownership decision cannot be
# silently skipped. Presence + typed-value only; correctness stays reviewer
# judgment (same boundary as the fresh-eye floor + the D34 announcement posture).
# `RULE_DATE = landing_day + 1` grandfather shape (lands 2026-07-05, enforced the
# next day). See skills/shared/references/boundary-ownership-brief.md.
BOUNDARY_OWNERSHIP_RULE_DATE = date(2026, 7, 6)
BOUNDARY_OWNERSHIP_HEADING = "## Boundary Ownership"
BOUNDARY_VERDICT_VALUES = ("single-surface", "owned-correctly", "moved-to-owner", "escalated-to-issue-spec")
BOUNDARY_VERDICT_SUMMARY = "`single-surface` / `owned-correctly` / `moved-to-owner` / `escalated-to-issue-spec`"
# Undatable critique artifacts present when the boundary floor landed — a closed
# allowlist, NOT fail-open (a NEW undatable artifact is still enforced; the
# scaffold always emits a dated filename). Kept separate from the fresh-eye
# allowlist so grandfathering here never weakens that floor's own enforcement.
BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS = frozenset({"release-0-55-0-full-packet.md", "release-0-55-1-packet.md", "release-0-55-1-critique.md"})
# Closed, explicit allowlist — NOT a fail-open default. Every other undatable
# critique artifact is now enforced as if post-cutoff (a new artifact with no
# parseable date is itself the anomaly); only these two legacy prepare-packets,
# frozen before this floor existed and never carrying a `Fresh-eye
# satisfaction:` line, are named exceptions. Extending this set requires the
# same care as extending a `boundary-bypass-exemptions.txt` entry: one
# artifact, one reason (this file has both — no date, pre-floor legacy).
LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS = frozenset({"release-0-55-0-full-packet.md", "release-0-55-1-packet.md"})
_CRITIQUE_DATE_LINE = re.compile(r"^date:\s*(\d{4}-\d{2}-\d{2})\b")
# Leading markdown/quote markup stripped before matching a typed token, so a
# backtick-wrapped or bulleted value (`` `parent-delegated`. `` — the observed
# in-corpus convention) still matches; mirrors `disposition_form._MARKDOWN_LEAD`.
_LEADING_MARKUP_RE = re.compile(r"^[\s`*_\"'>\-]+")


def changed_paths(repo_root: Path) -> list[str]:
    return git_changed_paths(repo_root, artifact_label="critique")


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        return [
            path
            for path in sorted((repo_root / CRITIQUE_ARTIFACT_PREFIX).glob("*.md"))
            if not file_is_prepare_packet_markdown_kind(
                path,
                expected_kind=CRITIQUE_PREPARE_PACKET_KIND,
                expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
            )
        ]
    candidates: list[Path] = []
    for relpath in paths:
        if relpath.startswith(CRITIQUE_ARTIFACT_PREFIX) and relpath.endswith(".md"):
            path = repo_root / relpath
            if not file_is_prepare_packet_markdown_kind(
                path,
                expected_kind=CRITIQUE_PREPARE_PACKET_KIND,
                expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
            ) and path.is_file():
                candidates.append(path)
    return sorted(candidates)


def has_repo_delegation_contract(repo_root: Path) -> bool:
    agents_path = repo_root / "AGENTS.md"
    return agents_path.is_file() and all(
        marker in agents_path.read_text(encoding="utf-8").lower()
        for marker in DELEGATION_CONTRACT_MARKERS
    )


def _date_from_filename(path: Path) -> date | None:
    """The leading ``YYYY-MM-DD`` of the artifact filename, ``None`` when absent."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _date_from_body(text: str) -> date | None:
    """The in-body ``Date: YYYY-MM-DD`` line (first 5 lines), ``None`` when absent."""
    for line in text.splitlines()[:5]:
        match = _CRITIQUE_DATE_LINE.match(line.strip().lower())
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
    return None


def critique_observed_date(path: Path, text: str) -> date | None:
    """The artifact's effective date for grandfathering: the in-body ``Date:``
    line, else the leading ``YYYY-MM-DD`` of the filename — same fallback order
    as ``validate_retro_artifact._retro_observed_date``. ``None`` when neither is
    parseable. Callers must NOT treat ``None`` as fail-open by default: only the
    explicit ``LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS`` allowlist is grandfathered
    on absence; every other undatable artifact is enforced as if post-cutoff."""
    return _date_from_body(text) or _date_from_filename(path)


def fresh_eye_satisfaction_status(text: str) -> str | None:
    lines = text.splitlines()
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower()
        if "fresh-eye satisfaction" not in lowered and "fresh-eye satisfaction" not in lowered.replace("_", "-"):
            continue
        if ":" in lowered:
            return lowered.split(":", 1)[1].strip()
        section_lines: list[str] = []
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if stripped.startswith("## "):
                break
            if stripped:
                section_lines.append(stripped.lower())
                if len(section_lines) >= 3:
                    break
        return " ".join(section_lines)
    return None


def _substantive_signal(value: str) -> bool:
    signal_text = value.strip().strip("-*`._:;,#[](){}<>!/?\\|\"' ")
    normalized = " ".join(value.strip().lower().split())
    return (
        bool(signal_text)
        and any(character.isalnum() for character in signal_text)
        and normalized not in PLACEHOLDER_VALUES
        and not normalized.startswith("missing ")
    )


def has_blocked_signal_detail(text: str) -> bool:
    lines = text.splitlines()
    for raw in lines:
        lowered = raw.strip().lower().lstrip("-*").strip()
        for heading in SIGNAL_HEADINGS:
            marker = f"{heading}:"
            if lowered.startswith(marker) and _substantive_signal(lowered.removeprefix(marker)):
                return True
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower().rstrip(":")
        if lowered.startswith("#"):
            lowered = lowered.lstrip("#").strip()
        if lowered not in SIGNAL_HEADINGS:
            continue
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if stripped.startswith("## "):
                break
            if _substantive_signal(stripped):
                return True
    return False


def _structured_findings_lines(text: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == STRUCTURED_FINDINGS_HEADING)
    except StopIteration:
        return []
    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return [line for line in section if line.strip().startswith("- ")]


def _parse_structured_finding(raw: str) -> dict[str, str]:
    body = raw.strip().lstrip("- ").strip()
    parts = [chunk.strip() for chunk in body.split("|") if chunk.strip()]
    if not parts:
        return {}
    fields: dict[str, str] = {}
    head = parts[0]
    if ":" not in head:
        fields["id"] = head
        rest = parts[1:]
    else:
        rest = parts
    for chunk in rest:
        if ":" not in chunk:
            continue
        key, _, value = chunk.partition(":")
        fields[key.strip().lower()] = value.strip()
    return fields


def _is_valid_followup_value(value: str) -> bool:
    """Same grammar as `debug` sibling follow-up: identifier or `deferred <anchor>`.

    Delegates to the shared `artifact_validator.is_valid_followup_tail` so the
    follow-up grammar lives in one place (the Closeout Schema Rule in
    `create-skill/references/portable-authoring.md` requires reusing it).
    """
    return is_valid_followup_tail(value.strip().lower())


def validate_structured_findings(path: Path, text: str) -> None:
    bullets = _structured_findings_lines(text)
    if not bullets:
        return
    seen_ids: set[str] = set()
    for index, raw in enumerate(bullets, start=1):
        finding = _parse_structured_finding(raw)
        finding_id = finding.get("id", f"<line {index}>")
        for field in STRUCTURED_REQUIRED_FIELDS:
            if not finding.get(field):
                raise ValidationError(
                    f"{path}: `## Structured Findings` entry {finding_id} missing required field `{field}`; "
                    f"every entry needs all of {list(STRUCTURED_REQUIRED_FIELDS)} — target form: "
                    f"`{STRUCTURED_FINDING_FORM}`"
                )
        if "id" in finding:
            if finding["id"] in seen_ids:
                raise ValidationError(
                    f"{path}: `## Structured Findings` duplicate id `{finding['id']}`"
                )
            seen_ids.add(finding["id"])
        if finding["bin"] not in STRUCTURED_BINS:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown bin `{finding['bin']}`; "
                f"allowed: {sorted(STRUCTURED_BINS)}"
            )
        if finding["evidence"] not in STRUCTURED_EVIDENCE:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown evidence `{finding['evidence']}`; "
                f"allowed: {sorted(STRUCTURED_EVIDENCE)}"
            )
        if finding["action"] not in STRUCTURED_ACTIONS:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown action `{finding['action']}`; "
                f"allowed: {sorted(STRUCTURED_ACTIONS)}"
            )
        followup_value = finding.get("follow-up", "")
        if finding["action"] == "file-issue":
            if not _is_valid_followup_value(followup_value):
                raise ValidationError(
                    f"{path}: `## Structured Findings` entry {finding_id} has `action: file-issue` "
                    "but no parseable `follow-up:` field; record the issue URL or "
                    "`follow-up: deferred <handoff-anchor>` per "
                    "skills/public/critique/references/counterweight-triage.md."
                )
        elif followup_value and not _is_valid_followup_value(followup_value):
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has malformed `follow-up:` value "
                "(bare `deferred` without an anchor)."
            )


def _section_field_map(text: str, heading: str) -> dict[str, str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return {}
    fields: dict[str, str] = {}
    for raw in lines[start + 1 :]:
        if raw.startswith("## "):
            break
        stripped = raw.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, _, value = stripped.lstrip("- ").partition(":")
        normalized_key = key.replace("*", "").strip().lower()
        fields[normalized_key] = value.strip().strip("`")
    return fields


def _opens_with_typed_value(value: str, allowed: tuple[str, ...]) -> bool:
    """Whether ``value`` opens with one of ``allowed`` (after stripping
    backtick/quote/bullet markup) AND the remainder is not still an unedited
    ``todo`` placeholder. The shared presence/form check behind both the
    fresh-eye and boundary-ownership floors: it proves the artifact committed to
    a falsifiable claim *type*, never whether the claim is true — that stays
    reviewer judgment. The ``todo``-in-remainder rejection is the narrow
    exception: a scaffolded ``<typed> (TODO ...)`` is an unedited stub, not a
    claim, and accepting it would let an unedited default silently satisfy the
    floor (the same-observer rubber stamp, #386, these floors exist to stop)."""
    token = _LEADING_MARKUP_RE.sub("", value.strip().lower())
    matched = next((candidate for candidate in allowed if token.startswith(candidate)), None)
    if matched is None:
        return False
    return FRESH_EYE_TODO_MARKER not in token[len(matched) :]


def validate_reviewer_tier_evidence(path: Path, text: str) -> None:
    _reviewer_evidence.validate_reviewer_tier_evidence(
        path, text, section_field_map=_section_field_map
    )


validate_delivery_state = _reviewer_evidence.validate_delivery_state
validate_reviewed_input_binding = _reviewed_input_binding.validate_reviewed_input_binding


def check_boundary_ownership_typed_presence(
    path: Path, text: str, observed_date: date | None, *, cross_surface_hit: bool = False
) -> None:
    """The boundary-ownership presence floor. Module-level (not a nested closure)
    so it does not add to ``validate_critique_artifact``'s cyclomatic complexity.
    Grandfather mirrors the fresh-eye floor (dated-before-cutoff or legacy-undatable
    allowlist). Typed-presence only — EXCEPT that when ``cross_surface_hit`` is True
    the repo probe matched the changed paths, so a bare ``single-surface`` verdict
    is rejected: the objective path-match overrides the self-assertion (#408)."""
    if observed_date is not None and observed_date < BOUNDARY_OWNERSHIP_RULE_DATE:
        return
    if observed_date is None and path.name in BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS:
        return
    verdict = _section_field_map(text, BOUNDARY_OWNERSHIP_HEADING).get("verdict", "")
    if not verdict:
        raise ValidationError(
            f"{path}: critique artifact has no `## Boundary Ownership` section with a typed "
            f"`Verdict:` line; every critique artifact must record one of {BOUNDARY_VERDICT_SUMMARY} "
            "(run the producer/consumer brief at "
            "skills/shared/references/boundary-ownership-brief.md) — an omitted disposition "
            "silently skips the producer/consumer ownership question (#408)."
        )
    if not _opens_with_typed_value(verdict, BOUNDARY_VERDICT_VALUES):
        raise ValidationError(
            f"{path}: `## Boundary Ownership` verdict `{verdict[:80]}` does not open with one of "
            f"{BOUNDARY_VERDICT_SUMMARY}, or still carries an unedited `todo` after the typed value "
            "— either way it is not a real disposition."
        )
    normalized = _LEADING_MARKUP_RE.sub("", verdict.strip().lower())
    if cross_surface_hit and normalized.startswith("single-surface"):
        raise ValidationError(
            f"{path}: the changed paths match this repo's cross-surface probe, so a bare "
            "`single-surface` boundary verdict is rejected — record `owned-correctly` / "
            "`moved-to-owner` / `escalated-to-issue-spec` (the #408 objective override). See "
            "skills/shared/references/boundary-ownership-brief.md."
        )


def validate_critique_artifact(
    path: Path,
    *,
    repo_has_delegation_contract: bool,
    require_tier_evidence: bool,
    collect_all: bool = False,
    cross_surface_hit: bool = False,
    check_current_binding: bool = True,
) -> None:
    text = path.read_text(encoding="utf-8")
    status = fresh_eye_satisfaction_status(text)
    status_lowered = status.lower() if status is not None else ""
    observed_date = critique_observed_date(path, text)

    def _check_fresh_eye_typed_presence() -> None:
        # Grandfather is narrow, not fail-open: a dated artifact before the
        # cutoff is grandfathered; an undatable artifact is grandfathered ONLY
        # by the explicit legacy allowlist. Every other undatable artifact —
        # including any new artifact that never picks up a `Date:` line or a
        # dated filename — is enforced exactly as if dated post-cutoff, since
        # an undatable NEW artifact is itself the anomaly, not a safe default.
        if observed_date is not None and observed_date < FRESH_EYE_PRESENCE_RULE_DATE:
            return
        if observed_date is None and path.name in LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS:
            return
        # floor-addition-restraint: irreversible-boundary P4 floor, typed-presence-only
        if not status_lowered:
            raise ValidationError(
                f"{path}: critique artifact has no `Fresh-eye satisfaction:` line; every "
                f"critique artifact must record one of {FRESH_EYE_TYPED_VALUES_SUMMARY} — an "
                "omitted line otherwise skips every distinct-observer check below (the #386 "
                "same-observer rubber stamp in file form)."
            )
        if not _opens_with_typed_value(status_lowered, FRESH_EYE_TYPED_VALUES):
            raise ValidationError(
                f"{path}: `Fresh-eye satisfaction` value `{status_lowered[:80]}` does not open with "
                f"one of the typed values {FRESH_EYE_TYPED_VALUES_SUMMARY}, or still carries an "
                "unedited `todo` after the typed value — either way it is not a real record."
            )

    def _check_forbidden_blocker_phrases() -> None:
        if not repo_has_delegation_contract:
            return
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in status_lowered:
                raise ValidationError(
                    f"{path}: critique artifact must not treat missing explicit subagent delegation "
                    "as the canonical blocker; honor repo `Subagent Delegation` instructions, then cite "
                    "the concrete spawn-tool refusal, missing tool surface, or exhausted host budget if "
                    "delegation is still blocked"
                )

    def _check_blocked_signal_detail() -> None:
        if status_lowered and "blocked" in status_lowered and "parent-delegated" not in status_lowered:
            if not has_blocked_signal_detail(text):
                raise ValidationError(
                    f"{path}: blocked critique fresh-eye satisfaction must cite `host signal:` or `tool signal:`"
                )

    def _check_reviewer_tier_evidence() -> None:
        requires_tier_evidence = require_tier_evidence and (
            "parent-delegated" in status_lowered or PACKET_CONSUMED_RE.search(text)
        )
        if requires_tier_evidence or _section_field_map(text, REVIEWER_TIER_HEADING):
            validate_reviewer_tier_evidence(path, text)
            _reviewer_evidence.validate_delivery_state(
                path,
                text,
                observed_date,
                section_field_map=_section_field_map,
                opens_with_typed_value=_opens_with_typed_value,
                legacy_undatable=BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS,
            )

    checks = (
        _check_fresh_eye_typed_presence,
        lambda: check_boundary_ownership_typed_presence(
            path, text, observed_date, cross_surface_hit=cross_surface_hit
        ),
        _check_forbidden_blocker_phrases,
        _check_blocked_signal_detail,
        lambda: validate_structured_findings(path, text),
        _check_reviewer_tier_evidence,
        lambda: validate_reviewed_input_binding(
            path,
            text,
            observed_date,
            check_current=check_current_binding,
        ),
    )
    run_validation_checks(
        checks, collect_all=collect_all, artifact_label="critique artifact", error_cls=ValidationError
    )


def _resolve_cross_surface_hit(
    repo_root: Path, changed_ref: str | None, changed_path: list[str] | None
) -> bool:
    """False unless --changed-ref/--changed-path was passed AND those paths match
    this repo's configured probe (the #408 override; logic in boundary_probe_lib)."""
    if not changed_ref and not changed_path:
        return False
    return _boundary_probe_lib.resolve_hit(
        repo_root, changed_path=changed_path, changed_ref=changed_ref
    )[0]


def _add_cross_surface_args(parser) -> None:
    parser.add_argument(
        "--changed-ref",
        help="Git ref/range whose changed paths are tested against the repo cross-surface probe; "
        "a hit rejects a bare `single-surface` boundary verdict (#408 override).",
    )
    parser.add_argument(
        "--changed-path",
        nargs="*",
        help="Explicit changed paths for the cross-surface probe (bypasses git; wins over --changed-ref).",
    )


def _validate_factory(run):
    """Bind the per-run inputs the shared runner does not model itself.

    The cross-surface probe (which shells out to git) and the delegation-contract
    lookup (which reads AGENTS.md) are resolved ONCE per run, not once per
    artifact: a 100-artifact `--all` sweep would otherwise pay for both 100
    times. Neither reads the artifact, so hoisting cannot change a verdict.
    `require_tier_evidence` stays per artifact because it keys off whether THAT
    path was selected.
    """
    cross_surface_hit = _resolve_cross_surface_hit(run.repo_root, run.args.changed_ref, run.args.changed_path)
    repo_has_delegation = has_repo_delegation_contract(run.repo_root)
    require_tier_paths = set(run.selected_paths)

    def validate(artifact: Path) -> None:
        relpath = artifact.relative_to(run.repo_root).as_posix()
        validate_critique_artifact(
            artifact,
            repo_has_delegation_contract=repo_has_delegation,
            require_tier_evidence=run.explicit_paths or relpath in require_tier_paths,
            collect_all=run.collect_all,
            cross_surface_hit=cross_surface_hit,
            check_current_binding=not run.args.all,
        )

    return validate


def main() -> int:
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked critique artifact.",
        artifact_label="critique artifact",
        changed_paths_fn=changed_paths,
        candidate_paths_fn=candidate_paths,
        validate_factory=_validate_factory,
        extra_args=_add_cross_surface_args,
        fail_fast_help=(
            "Stop at the first rule violation instead of reporting every violation in one pass."
        ),
        owned_prefix=CRITIQUE_ARTIFACT_PREFIX,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        raise SystemExit(report_validation_failure(str(exc), artifact_type="critique"))
