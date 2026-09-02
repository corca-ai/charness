#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


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

# The sibling scope module is resolved the same way every other repo script
# resolves a sibling: a bare `from artifact_run_scope import ...` binds only when
# `scripts/` happens to be on sys.path, which is true in the repo and false in the
# exported plugin layout — where it silently degrades a consumer's scaffold.
_run_scope = import_repo_module(__file__, "scripts.artifact_run_scope")
ChangedArtifactRun = _run_scope.ChangedArtifactRun
ValidationError = _run_scope.ValidationError
add_changed_artifact_args = _run_scope.add_changed_artifact_args
add_one_pass_args = _run_scope.add_one_pass_args
add_artifact_path_arg = _run_scope.add_artifact_path_arg
resolve_artifact_override = _run_scope.resolve_artifact_override
git_changed_paths = _run_scope.git_changed_paths
selected_changed_paths = _run_scope.selected_changed_paths
unresolvable_named_paths = _run_scope.unresolvable_named_paths
safe_repo_relative_path = _run_scope.safe_repo_relative_path

# Re-exported so every validator keeps importing its selection surface from one
# place; the split moved where the code lives, not what callers import.
__all__ = [
    "ChangedArtifactRun",
    "ValidationError",
    "add_changed_artifact_args",
    "add_one_pass_args",
    "add_artifact_path_arg",
    "resolve_artifact_override",
    "git_changed_paths",
    "selected_changed_paths",
    "unresolvable_named_paths",
    "safe_repo_relative_path",
]

H2_RE = re.compile(r"^##\s+.+$")

# The violation-reporting surface (the scaffold hint and the failure printer) lives in
# its own module; re-exported here so every validator keeps its single import point.
_violation_report = import_repo_module(__file__, "scripts.artifact_violation_report")
_scaffold_rel = _violation_report._scaffold_rel
# The size measurement and its refusal live in their own module: they are one
# cohesive decision, and the reasoning that has to travel with the unit did not fit
# under this file's code-length cap. Re-exported so every existing call site keeps
# importing size enforcement from the validator it already loads.
_size_budget = import_repo_module(__file__, "scripts.artifact_size_budget")
artifact_words = _size_budget.artifact_words
validate_max_words = _size_budget.validate_max_words
word_ceiling_enforced = _size_budget.word_ceiling_enforced
validate_max_words_when_dated_in_scope = _size_budget.validate_max_words_when_dated_in_scope
_skill_id = _violation_report._skill_id
_skill_id_from_scaffold = _violation_report._skill_id_from_scaffold
scaffold_hint = _violation_report.scaffold_hint
report_validation_failure = _violation_report.report_validation_failure


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        raise ValidationError(f"missing artifact `{path}`")
    return path.read_text(encoding="utf-8").splitlines()


def resolve_adapter_line_budget(
    load_adapter: Callable[[Path], dict], repo_root: Path, *, field: str, default: int
) -> int:
    """The artifact's size ceiling as the CONSUMING repo declared it, else the default.

    Generic over the unit: callers pass `field` and `default`, and every prose family
    now declares WORDS. Only the function NAME still says line -- it is a named row in
    the adapter-consumer census, so renaming it would churn a proof surface.

    Every family that owns a ceiling resolves it through here, so a repo that raises
    one gets the same behavior from the validator that enforces it and the scaffold
    that forecasts it. The forecast is the point: a ceiling discovered only after
    writing long is the wasted draft the issue reported.

    Deliberately NOT keyed on the adapter's `valid` flag, for the reason
    `_adapter_output_dir` records at length in the debug validator: a validator
    populates the fields it could resolve even when an unrelated field failed, so
    gating on `valid` would drop a perfectly good ceiling because of a typo'd
    `repo`. A field the resolver REFUSED is absent from `data` -- the refusal is
    reported by `resolve_adapter`, and falling back to the default here is the
    conservative arm, never a silent honoring of the bad value.

    The isinstance re-check is not redundant with the resolver: a consuming repo can
    vendor a resolver older than its validator, and this module must not turn that
    skew into a ceiling of `True`.
    """
    try:
        data = load_adapter(repo_root).get("data") or {}
    except Exception:
        # An unreadable adapter is already reported by the caller's own artifact
        # discovery; degrading to the default keeps the ceiling enforced rather than
        # failing open, and never invents a number the repo did not declare.
        return default
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return default
    return value


def validate_title(
    lines: Sequence[str],
    *,
    title_predicate: Callable[[str], bool],
    error_message: str,
) -> None:
    if not lines or not title_predicate(lines[0].strip()):
        raise ValidationError(error_message)


def validate_date_line(lines: Sequence[str]) -> None:
    if len(lines) < 2 or not lines[1].startswith("Date: "):
        raise ValidationError("artifact must record `Date: YYYY-MM-DD` on line 2")


def find_index(lines: Sequence[str], heading: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index
    raise ValidationError(f"missing required section `{heading}`")


def validate_section_order(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    indices = [find_index(lines, heading) for heading in required_sections]
    if indices != sorted(indices):
        raise ValidationError("required sections must stay in canonical order")


def iter_h2_headings(lines: Sequence[str]) -> list[str]:
    return [line.strip() for line in lines if H2_RE.match(line.strip())]


def validate_exact_h2_sections(
    lines: Sequence[str],
    required_sections: Sequence[str],
    *,
    optional_sections: Sequence[str] = (),
) -> None:
    headings = iter_h2_headings(lines)
    allowed = list(required_sections) + list(optional_sections)
    for heading in headings:
        if heading not in allowed:
            raise ValidationError(
                "artifact must use only the canonical sections: "
                + ", ".join(f"`{heading}`" for heading in allowed)
            )
    for required in required_sections:
        if required not in headings:
            raise ValidationError(f"missing required section `{required}`")


def validate_nonempty_sections(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    for index, heading in enumerate(required_sections):
        start = find_index(lines, heading) + 1
        end = len(lines)
        if index + 1 < len(required_sections):
            end = find_index(lines, required_sections[index + 1])
        section_lines = [line.strip() for line in lines[start:end] if line.strip()]
        if not section_lines:
            raise ValidationError(f"`{heading}` must not be empty")


SIBLING_SEARCH_HEADING = "## Sibling Search"
SIBLING_DECISION_FOLLOWUP = "valid follow-up outside the slice"
SIBLING_DECISION_DIAGNOSTIC_ONLY = "same class, diagnostic-only for this slice"
ABSTRACTION_UP_AXIS_RE = re.compile(r"^[-*]\s+abstraction[ -]up(?:\s+axis)?\s*:", re.IGNORECASE)
UNRESOLVED_STRUCTURAL_RE = re.compile(
    r"\b(unresolved|deferred|not fix(?:ed|ing)?|outside (?:this|the) slice|"
    r"repo-level|structural (?:work|class)|broader (?:class|structural))\b",
    re.IGNORECASE,
)
NO_ACTION_REASON_RE = re.compile(
    r"\b(no action (?:needed|required)|bounded|already (?:covered|owned|handled)|"
    r"distinct (?:surface|contract|case)|not an? (?:instance|sibling)|intentional boundary)\b",
    re.IGNORECASE,
)


def is_sibling_decision_bullet(line: str) -> bool:
    """Bullet entries are markdown list items that carry a `decision:` field.

    Prose paragraphs that mention the decision phrase are excluded so authors
    can quote the rule in commentary without tripping the validator.
    """
    stripped = line.lstrip()
    return bool(re.match(r"^[-*]\s+", stripped)) and "decision:" in stripped.lower()


def is_trivial_short_circuit(line: str) -> bool:
    """`n/a — trivial fix; no plausible siblings` short-circuit, dash-agnostic."""
    lowered = line.lower()
    return "n/a" in lowered and "trivial fix" in lowered and "no plausible siblings" in lowered


def is_valid_followup_tail(tail: str) -> bool:
    """`follow-up:` payload must name an identifier or `deferred <anchor>`.

    Bare tokens like `deferred` (without an anchor) silently re-export the
    follow-up to the next session — that is the exact failure the rule blocks.
    """
    parts = tail.split(None, 1)
    if not parts:
        return False
    if parts[0].rstrip(".,;:") == "deferred":
        return len(parts) > 1 and bool(parts[1].strip())
    return True


def line_has_valid_followup(line: str) -> bool:
    lower = line.lower()
    if "follow-up:" not in lower:
        return False
    tail = lower.split("follow-up:", 1)[1].strip()
    return is_valid_followup_tail(tail)


def continuation_lines(section: Sequence[str], index: int) -> list[str]:
    lines: list[str] = []
    for candidate in section[index + 1 :]:
        if re.match(r"^\s*[-*]\s+", candidate):
            break
        if candidate.strip():
            lines.append(candidate.strip())
    return lines


def line_has_no_action_reason(line: str) -> bool:
    return bool(NO_ACTION_REASON_RE.search(line))


def is_abstraction_up_diagnostic_only(line: str) -> bool:
    stripped = line.lstrip()
    return (
        bool(ABSTRACTION_UP_AXIS_RE.match(stripped))
        and is_sibling_decision_bullet(stripped)
        and SIBLING_DECISION_DIAGNOSTIC_ONLY in stripped.lower()
    )


def validate_sibling_followups(
    lines: Sequence[str],
    *,
    boundary_headings: Sequence[str],
    source_reference: str,
) -> None:
    """Fail when a `valid follow-up outside the slice` sibling lacks a follow-up id.

    `## Sibling Search` is a list of `- <axis>: <location> | decision: ... | proof: ...`
    bullets. When `decision: valid follow-up outside the slice` appears on a
    bullet line, the same bullet (or the next continuation line) must carry a
    `follow-up: <issue-url>` or `follow-up: deferred <anchor>` identifier.

    The section is opt-in: artifacts without a `## Sibling Search` heading pass.
    `boundary_headings` are the headings that may follow the section; whichever
    appears first ends it. `source_reference` is the skill reference cited in the
    failure message. Decision matching is case-insensitive so a title-cased
    decision phrase cannot bypass the rule.
    """
    try:
        start = find_index(lines, SIBLING_SEARCH_HEADING) + 1
    except ValidationError:
        return
    end = len(lines)
    for candidate in boundary_headings:
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start:
            end = min(end, index)
    section = list(lines[start:end])
    if any(is_trivial_short_circuit(line) for line in section):
        return
    for index, raw in enumerate(section):
        line = raw.rstrip()
        if not is_sibling_decision_bullet(line):
            continue
        continuations = continuation_lines(section, index)
        full_entry = " ".join([line, *continuations])
        if is_abstraction_up_diagnostic_only(line):
            has_followup = line_has_valid_followup(line) or any(
                line_has_valid_followup(cont) for cont in continuations
            )
            if UNRESOLVED_STRUCTURAL_RE.search(full_entry) and not has_followup:
                offender = line.strip().lstrip("- ").strip()
                raise ValidationError(
                    "`## Sibling Search` abstraction-up diagnostic-only entry describes unresolved "
                    "structural work but has no `follow-up:` issue URL or handoff anchor "
                    f"(offender: `{offender[:120]}`); see {source_reference}."
                )
            if not (line_has_no_action_reason(full_entry) or has_followup):
                offender = line.strip().lstrip("- ").strip()
                raise ValidationError(
                    "`## Sibling Search` abstraction-up diagnostic-only entry must include a "
                    "proof-backed no-action reason or a `follow-up:` identifier "
                    f"(offender: `{offender[:120]}`); see {source_reference}."
                )
        if SIBLING_DECISION_FOLLOWUP not in line.lower():
            continue
        if line_has_valid_followup(line):
            continue
        if any(line_has_valid_followup(cont) for cont in continuations):
            continue
        offender = line.strip().lstrip("- ").strip()
        raise ValidationError(
            "`## Sibling Search` entry classified `valid follow-up outside the slice` must record a "
            "`follow-up: <issue-url>` or `follow-up: deferred <handoff-anchor>` identifier on the same "
            f"bullet (offender: `{offender[:120]}`); see {source_reference}."
        )


def parse_single_artifact_validator_args(*, surface: str, default_repo_root: Path):
    """The argument surface every SINGLE-artifact validator parses.

    `run_changed_artifact_validator` already owns this for the changed-path family; the
    two validators that resolve exactly one artifact (quality, handoff) hand-rolled the
    same parser, down to a copy of the `--fail-fast` help string. A duplication gate
    caught it the moment a fourth shared line was added to both. Argument plumbing only:
    it parses nothing new and changes no verdict, which is why the two mains keep their
    own bodies below it.
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    add_artifact_path_arg(parser, surface=surface)
    add_one_pass_args(
        parser,
        fail_fast_help="Stop at the first rule violation instead of reporting every violation in one pass.",
    )
    return parser.parse_args()


def run_changed_artifact_validator(
    *,
    default_repo_root: Path,
    all_help: str,
    artifact_label: str,
    validate_factory: Callable[[ChangedArtifactRun], Callable[[Path], None]],
    fail_fast_help: str,
    changed_paths_fn: Callable[[Path], list[str]] | None = None,
    candidate_paths_fn: Callable[..., list[Path]] | None = None,
    artifacts_fn: Callable[[ChangedArtifactRun], list[Path] | None] | None = None,
    extra_args: Callable[..., None] | None = None,
    no_scope_message: str | None = None,
    per_artifact_success: bool = False,
    owned_prefix: str | Callable[[Path], str | None] | None = None,
    error_cls: type[Exception] = ValidationError,
    on_complete: Callable[[ChangedArtifactRun, Sequence[Path]], None] | None = None,
    preflight: Callable[[Path], str | None] | None = None,
) -> int:
    """The whole `main()` for a changed-path artifact validator, in one place.

    Every such validator parses the same three selection args plus the one-pass
    control, resolves an artifact set, validates each one collecting failures,
    and reports. Forking that shape per validator is what let the one-pass
    contract land in some validators and not others (D28); sharing it means a new
    artifact family cannot be born already inconsistent.

    The optional hooks exist so the two validators that used to justify their own
    `main()` fit here rather than beside here:

    - `owned_prefix` is the artifact directory this validator owns. It scopes the
      named-path refusal below: without it, a validator keeps its previous
      behavior of passing on a named path that resolved to nothing.
    - `extra_args` adds validator-specific flags (critique's `--changed-ref` /
      `--changed-path` cross-surface probe).
    - `artifacts_fn` replaces the default changed-path resolution entirely (debug
      resolves its output directory through its own adapter). Returning `None`
      means "nothing in scope", reported via `no_scope_message` as a success.
    - `per_artifact_success` prints one line per validated artifact instead of a
      count. Reporting verbosity only — it changes no verdict and no exit code.
    - `on_complete` reports what the PASSING run actually evaluated. A count of
      validated artifacts reads as coverage while saying nothing about which
      conditional floors were live, and a floor that is off emits nothing by
      construction; a validator whose enforcement varies by mode, date or probe
      config uses this to name its scope. Called only on success — a failing run
      already carries a signal. Reporting only: it changes no verdict.
    - `preflight` refuses BEFORE any scoping, returning a message or None. It runs
      first because the condition it reports is the one that makes every later answer
      meaningless: a validator whose adapter could not be read at its declared version
      resolves its output directory AND its size ceiling from charness defaults, so it
      scopes itself to a directory the repo does not write to and reports
      `Validated 0 <label>(s).` as a pass. That refusal must precede discovery, not
      follow it.
    """
    import argparse

    parser = argparse.ArgumentParser()
    add_changed_artifact_args(parser, default_repo_root=default_repo_root, all_help=all_help)
    add_one_pass_args(parser, fail_fast_help=fail_fast_help)
    if extra_args is not None:
        extra_args(parser)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if preflight is not None and (refusal := preflight(repo_root)) is not None:
        # Exits 1 DIRECTLY rather than raising `error_cls`, for the reason
        # `_debug_artifacts` records about its own two hard errors: this is not an
        # artifact rule violation, so routing it through `report_validation_failure`
        # would append the "start from the owning scaffold" hint — advice to author a
        # stub when the real fix is one line in an adapter.
        print(refusal, file=sys.stderr)
        return 1
    selected_paths = (
        selected_changed_paths(args, repo_root, changed_paths_fn=changed_paths_fn)
        if changed_paths_fn is not None
        else list(args.paths or [])
    )
    run = ChangedArtifactRun(
        args=args,
        repo_root=repo_root,
        collect_all=not args.fail_fast,
        selected_paths=selected_paths,
        explicit_paths=args.paths is not None,
    )

    if artifacts_fn is not None:
        artifacts = artifacts_fn(run)
    elif candidate_paths_fn is not None:
        artifacts = candidate_paths_fn(repo_root, selected_paths, all_artifacts=args.all)
    else:
        raise TypeError("run_changed_artifact_validator needs candidate_paths_fn or artifacts_fn")
    if artifacts is None and not run.explicit_paths:
        print(no_scope_message or f"No {artifact_label}s in scope.")
        return 0
    if run.explicit_paths and not artifacts:
        # A CALLABLE is accepted for the one family whose artifact directory is
        # adapter-declared rather than constant (debug): a constant cannot express it,
        # and the value is not knowable until `--repo-root` is parsed. Omitting the
        # prefix costs the refusal below entirely, which is a silent pass -- not a
        # missing nicety -- for any validator whose emitted command NAMES a path. A
        # resolver returning None owns nothing, which is the previous behavior.
        resolved_prefix = owned_prefix(repo_root) if callable(owned_prefix) else owned_prefix
        unresolvable = unresolvable_named_paths(
            repo_root, list(args.paths or []), owned_prefix=resolved_prefix
        )
        if unresolvable:
            # A DISCOVERED empty set is legitimate (this commit touched no artifact
            # of this family) and stays the cheap no-op below. A named path that
            # cannot resolve at all is not: nothing was validated and
            # `Validated 0 <label>(s).` would report that as a pass.
            #
            # The discriminator is deliberately narrow, because `--paths` is fed by
            # TOOLS as often as by people: the surface preflight and the closeout
            # sweep pass a slice of the changed set, which legitimately contains
            # paths a validator's own content filter drops (a generated packet) and
            # paths that no longer exist (a deletion or an archival move). Failing
            # those would break normal commits, which is worse than the hole this
            # closes. Only a path that exists nowhere — not on disk, not as a
            # deletion git knows about — is a real typo or stale reference.
            named = ", ".join(unresolvable)
            print(
                f"named {artifact_label} path(s) resolve to nothing: {named}; "
                "nothing was validated. If you have not written the artifact yet, write it "
                "first -- a scoped gate names its path before the file exists. Otherwise check "
                "the spelling and that the path is (or was) a real file in this repo.",
                file=sys.stderr,
            )
            return 1
    if artifacts is None:
        print(no_scope_message or f"No {artifact_label}s in scope.")
        return 0

    # `validate_factory` is where a validator resolves per-run inputs, and those
    # can shell out (critique's cross-surface probe runs `git diff` on a ref). An
    # EMPTY artifact set must stay the cheap no-op it was before this shared
    # runner existed: the common commit touches no artifact of a given family,
    # and a probe failure there would turn a silent pass into a crash.
    if artifacts:
        try:
            validate_each_artifact(
                artifacts,
                validate_factory(run),
                collect_all=run.collect_all,
                artifact_label=artifact_label,
                repo_root=repo_root,
                error_cls=error_cls,
                on_success=(
                    (
                        lambda artifact: print(
                            f"Validated {artifact_label} {_artifact_label(artifact, repo_root)}."
                        )
                    )
                    if per_artifact_success
                    else None
                ),
            )
        except error_cls:
            # The scope record belongs on a FAILING run too. A failure carries a
            # signal about the failures; it carries nothing about the floors that
            # were off for the other 649 artifacts, which is the silence the
            # record exists to break.
            if on_complete is not None:
                on_complete(run, artifacts)
            raise
    if not per_artifact_success:
        print(f"Validated {len(artifacts)} {artifact_label}(s).")
    if on_complete is not None:
        on_complete(run, artifacts)
    return 0


def validate_each_artifact(
    artifacts: Sequence[Path],
    validate: Callable[[Path], None],
    *,
    collect_all: bool,
    artifact_label: str,
    repo_root: Path | None = None,
    error_cls: type[Exception] = ValidationError,
    on_success: Callable[[Path], None] | None = None,
) -> None:
    """Validate a batch, reporting every FAILING ARTIFACT instead of only the first.

    `run_validation_checks` collects across rules within one artifact; this
    collects across the artifacts themselves. Both axes matter for the same
    reason: a batch that stops at the first failure makes the author pay one gate
    run per problem, which is the retry loop the one-pass contract removes.

    Callers that want the old stop-at-first behavior pass `collect_all=False`.
    That path still names the offending artifact: several rule messages (retro's,
    for one) never embed the path, so a bare re-raise would report a violation
    without saying which file to open.
    """
    errors: list[str] = []
    for artifact in artifacts:
        try:
            validate(artifact)
        except error_cls as exc:
            labeled = f"Invalid {artifact_label} {_artifact_label(artifact, repo_root)}: {exc}"
            if not collect_all:
                raise error_cls(labeled) from exc
            errors.append(labeled)
            continue
        if on_success is not None:
            on_success(artifact)
    if errors:
        raise error_cls("\n".join(errors))


def _artifact_label(artifact: Path, repo_root: Path | None) -> str:
    """Repo-relative when resolvable, else the path as given."""
    if repo_root is not None:
        try:
            return artifact.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            pass
    return str(artifact)


def run_validation_checks(
    checks: Sequence[Callable[[], None]],
    *,
    collect_all: bool,
    artifact_label: str,
    error_cls: type[Exception] = ValidationError,
) -> None:
    """Run checks fail-fast, or collect every violation when `collect_all` is set.

    Artifact validators run this collecting BY DEFAULT so a multi-rule draft is
    fixed in one pass instead of one rule per gate run; `--fail-fast` is the only
    control that opts back into stop-at-first (see `add_one_pass_args`).
    """
    if not collect_all:
        for check in checks:
            check()
        return
    violations: list[str] = []
    for check in checks:
        try:
            check()
        except error_cls as exc:
            # Overlapping checks (e.g. exact-section + nonempty-section) can
            # surface the same message; keep the first occurrence only.
            message = str(exc)
            if message not in violations:
                violations.append(message)
    if violations:
        joined = "\n".join(f"- {message}" for message in violations)
        raise error_cls(f"{len(violations)} {artifact_label} rule violation(s):\n{joined}")
