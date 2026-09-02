#!/usr/bin/env python3

from __future__ import annotations

import sys
from functools import partial
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

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    load_path_module,
    repo_root_from_script,
)

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
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifacts.artifact_validator")
_adversarial_evidence = import_repo_module(__file__, "scripts.review.adversarial_evidence")
# The #548 SINGLE OWNER of what a current pointer resolves to. Imported rather than
# re-derived: five private copies of this rule were consolidated into it precisely
# because nothing forced them to agree, and the role test below is where a seventh
# would have gone.
_scaffold_artifact_lib = import_repo_module(__file__, "scripts.core.scaffold_artifact_lib")
_adapter_version_verdict = import_repo_module(__file__, "scripts.adapters.adapter_version_verdict")
# The rule-date scope for the word ceiling, owned by the module that owns the
# measurement so debug and quality cannot drift apart (they shipped as byte-identical
# copies for one commit, and the duplicate gate caught it).
_validate_size = _scripts_artifact_validator_module.validate_max_words_when_dated_in_scope
ValidationError = _scripts_artifact_validator_module.ValidationError
report_validation_failure = _scripts_artifact_validator_module.report_validation_failure
run_changed_artifact_validator = _scripts_artifact_validator_module.run_changed_artifact_validator
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_date_line = _scripts_artifact_validator_module.validate_date_line
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
resolve_adapter_line_budget = _scripts_artifact_validator_module.resolve_adapter_line_budget
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
validate_section_order = _scripts_artifact_validator_module.validate_section_order
validate_title = _scripts_artifact_validator_module.validate_title
validate_sibling_followups = _scripts_artifact_validator_module.validate_sibling_followups
is_trivial_short_circuit = _scripts_artifact_validator_module.is_trivial_short_circuit
run_validation_checks = _scripts_artifact_validator_module.run_validation_checks


validate_adversarial_evidence = partial(
    _adversarial_evidence.validate_for_artifact, error_cls=ValidationError
)

# Single source of truth for the Seam Risk taxonomy: reuse the enums the
# downstream consumer (`risk_interrupt_lib.parse_debug_interrupt`) enforces
# instead of hand-copying them here, so the author-time validator can never
# drift below the artifact consumer (#366).
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.gates_support.risk_interrupt_lib")
ALLOWED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.ALLOWED_RISK_CLASSES
FORCED_RISK_CLASSES = _scripts_risk_interrupt_lib_module.FORCED_RISK_CLASSES
ALLOWED_GENERALIZATION_PRESSURE = _scripts_risk_interrupt_lib_module.ALLOWED_GENERALIZATION_PRESSURE
_parse_risk_classes = _scripts_risk_interrupt_lib_module._parse_risk_classes

# The interrupt/seam grammar lives in its own module (split at the length cap
# during #636's one-pass reporting work); re-exported here so callers and tests
# keep one import surface for debug validation.
_scripts_debug_interrupt_grammar_module = import_repo_module(__file__, "scripts.retro_debug.debug_interrupt_grammar")
section_lines = _scripts_debug_interrupt_grammar_module.section_lines
extract_prefixed_values = _scripts_debug_interrupt_grammar_module.extract_prefixed_values
validate_current_interrupt_sections = _scripts_debug_interrupt_grammar_module.validate_current_interrupt_sections
validate_dated_seam_risk_enums = _scripts_debug_interrupt_grammar_module.validate_dated_seam_risk_enums

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

# The DEFAULT ceiling, in WORDS since 2026-08-19. A consuming repo raises or lowers it
# with `max_artifact_words` in `.agents/debug-adapter.yaml`; the run resolves it once in
# `_validate_factory` via `resolve_adapter_line_budget`, so a repo whose investigations
# are legitimately multi-cause is not forced into content-free re-wrapping -- which the
# LINE ceiling this replaces actively rewarded, since rewrapping was the cheapest way
# under it. 1200 is chosen against the corpus, not converted: all 145 checked-in debug
# artifacts fit the 180-line cap and they range 276 to 1487 words, a 5.4x spread, so no
# word number reproduces the old bar. 1200 sits just above this corpus's p90 of 1129,
# and the seven above it are grandfathered as dated records. Kept
# exported: the scaffold, this module's tests and the drift guard all name the DEFAULT,
# and only the default.
MAX_ARTIFACT_WORDS = 1200
# `getattr` with the literal default, not a bare attribute read: the two halves are
# loaded from separate trees (the resolver by PATH, honoring CHARNESS_REPO_ROOT), so a
# consumer can pair a stale resolver with this validator. A bare read turns that skew
# into an AttributeError at IMPORT -- a traceback and no verdict on a proof surface,
# outside the ValidationError handler. The literal is the same one the resolver
# declares; quality already spells its field locally for this reason.
WORD_BUDGET_FIELD = getattr(_debug_resolve_adapter, "WORD_BUDGET_FIELD", "max_artifact_words")
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
    "## Evidence Disposition",
    "## Adversarial Verification",
)


def validate_candidate_causes(lines: list[str]) -> None:
    start = find_index(lines, "## Candidate Causes") + 1
    end = find_index(lines, "## Hypothesis")
    bullets = [line.strip() for line in lines[start:end] if line.strip().startswith("- ")]
    if len(bullets) < 3:
        raise ValidationError("`## Candidate Causes` must list at least three plausible causes")


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

    The proven static-only-RCA gap (debug review re-capture, a
    `falsifiable-hypothesis-before-fix` failure) is a run that authored a
    conclusion from `static scan only` with no cheapest-refutation check.
    `five-steps.md` step 5 ("verify a FALSIFIABLE hypothesis; don't call intuition a
    diagnosis") and `disconfirmer-first.md` own that rule, but a bare `TODO`
    Hypothesis seed left it un-internalized, so the run filled the section shallowly.
    This moves the rule INTO the artifact structure: the section must carry a
    `disconfirmer: <cheapest refutation>` marker. A justified
    `disconfirmer: n/a — <why no cheap refutation exists>` escape satisfies it
    (some bug classes — e.g. CI-only — have no local repro). Like the cross-file
    sibling marker, this is an honesty contract surfaced for review, NOT a
    replacement for the disconfirmer itself; a `disconfirmer: n/a` static-only run
    still records that no cheap local refutation exists. The
    trivial-fix short-circuit satisfies it, matching `validate_cross_file_sibling_marker`.
    """
    # floor-addition-restraint: keep. Recorded recurrence (static-only RCF FAIL across
    # two debug review captures, modeled on the
    # accepted cross-file sibling marker, and absorbed by the existing
    # check_artifact_surface_preflight (the debug validator already runs there), so it
    # is not a new serial end-gate. The marker only surfaces the field for the run
    # and for review.
    section = section_lines(lines, HYPOTHESIS_HEADING, HYPOTHESIS_BOUNDARY_HEADINGS)
    if _section_declares_marker(section, (DISCONFIRMER_MARKER,)):
        return
    raise ValidationError(
        "current debug artifact `## Hypothesis` must record a falsifiability check: add "
        "`disconfirmer: <cheapest refutation run before the fix>` (a justified "
        "`disconfirmer: n/a — <why no cheap refutation exists>` escape, or the trivial-fix "
        f"short-circuit, also satisfies it); see {FALSIFIABLE_SOURCE_REFERENCE}."
    )


def _same_resolved_path(left: Path, right: Path) -> bool:
    """Do these two names designate one file, with a symlink loop answered rather than raised.

    RuntimeError is not redundant alongside OSError: CPython's `Path.resolve()` catches
    the ELOOP `OSError` and re-raises `RuntimeError("Symlink loop from ...")`. An
    `except OSError` alone therefore lets a looping pointer crash this validator with a
    traceback instead of rendering a verdict -- on a surface whose whole job is to render
    one. Measured on a two-link loop, not inferred from the docs.
    """
    try:
        return left.resolve() == right.resolve()
    except (OSError, RuntimeError):
        return False


def is_current_artifact(path: Path, current_pointer: Path | None = None) -> bool:
    """Does the CURRENT (strict) schema govern this file, or the legacy dated one?"""
    # Keyed on ROLE, not on filename. The filename test alone gave the same bytes two
    # different verdicts depending on which name reached them: `--paths <the pointer>` ran
    # the strict checks and `--paths <what the pointer designates>` ran only the legacy
    # ones. That was invisible while every emitted command was unscoped -- the corpus glob
    # yields the pointer too, so the strict checks always ran on the current content under
    # SOME name. Scoping the emitted command to the artifact being authored removed that
    # other name, so an artifact the scaffold writes in the current shape was judged by the
    # legacy rules and a missing `disconfirmer:` or `cross-file:` marker passed.
    #
    # BOTH supported pointer layouts are covered, and the first repair covered only one.
    # `refresh_current_pointer.py` resolves `auto` to a symlink where the filesystem allows
    # it and to a byte COPY otherwise, so a regular-file pointer is a first-class layout,
    # not a degenerate case -- and a repair that bailed on `not is_symlink()` left the
    # original defect verbatim for every repo on the copy path (and for a hard link, which
    # is the same shape). The symlink arm delegates to `current_pointer_state`, the #548
    # single owner of what a pointer resolves to, rather than re-deriving it here for a
    # seventh time; the copy arm compares bytes, which is the only identity a copy has.
    #
    # Blind class: this reads the pointer as it stands NOW. A run that validates a record
    # before the pointer is refreshed onto it sees a legacy record and says so -- correct
    # for what is on disk. On the copy layout it also cannot distinguish "this record IS
    # the current artifact" from "this record happens to be byte-identical to it"; both get
    # the strict schema, which is the safe direction and, for identical bytes, the same
    # verdict either way.
    if current_pointer is None:
        return path.name == "latest.md"
    if _same_resolved_path(path, current_pointer):
        return True
    try:
        state = _scaffold_artifact_lib.current_pointer_state(
            current_pointer.parent, Path(current_pointer.name)
        )
    except (OSError, RuntimeError):
        # The #548 owner resolves the target through `portable_path`, so a LOOPING
        # pointer raises out of it. Guarded here rather than in the owner: that function
        # has five callers and hardening it is a change to their behavior too, which
        # belongs in its own slice with its own proof. Recorded so the next reader knows
        # this guard is standing in for a gap upstream, not decorating an impossible case.
        return False
    if state["current_pointer_is_symlink"]:
        # Already answered by the identity check above; a symlink that did not match is
        # pointing somewhere else, and reading its target's bytes would make an unrelated
        # copy look current.
        return False
    if not current_pointer.is_file():
        return False
    try:
        return current_pointer.read_bytes() == path.read_bytes()
    except OSError:
        return False


def validate_debug_artifact(
    path: Path,
    *,
    collect_all: bool = False,
    current_pointer: Path | None = None,
    max_words: int | None = None,
    evidence_mode: bool = False,
    repo_root: Path | None = None,
) -> None:
    """`max_words` None means the built-in default, NOT "unlimited".

    The adapter-resolved ceiling is bound once per run by `_validate_factory`, the
    same place `current_pointer` is bound, because resolving it per artifact would
    re-read and re-parse the adapter for every file in the corpus.
    """
    ceiling = MAX_ARTIFACT_WORDS if max_words is None else max_words
    lines = read_lines(path)
    base_checks = (
        lambda: validate_title(
            lines,
            title_predicate=lambda line: line.startswith("# ") and "debug" in line.lower(),
            error_message="debug artifact must start with a `# ... Debug ...` heading",
        ),
        lambda: validate_date_line(lines),
        # Grandfathered on the unit change; `word_ceiling_enforced` owns why. Live, not
        # latent: `run-quality.sh` runs this gate UNSCOPED over the whole corpus, and
        # seven checked-in artifacts went red at the cutover.
        lambda: _validate_size(
            path, lines, max_words=ceiling, artifact_label="debug artifact", artifact_type="debug"
        ),
        lambda: validate_adversarial_evidence(
            "\n".join(lines),
            artifact_label="debug artifact",
            evidence_mode=evidence_mode,
            repo_root=repo_root,
        ),
    )
    if is_current_artifact(path, current_pointer):
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
        # Deduplicated by resolved identity. With a symlinked pointer the glob yields the
        # pointer AND its target, and now that both take the same (strict) branch a
        # violation was reported TWICE -- with identical text and identical labels, since
        # the reporter resolves the path, so the pointer's own name never appeared. One
        # file, one entry; the pointer's name is kept because it is the role-bearing one.
        seen: dict[Path, Path] = {}
        for candidate in sorted(output_dir.glob("*.md")):
            key = candidate.resolve() if candidate.exists() else candidate
            seen.setdefault(key, candidate)
        return sorted(seen.values())
    prefix = f"{output_dir.relative_to(repo_root).as_posix()}/"
    scoped = [
        repo_root / rel
        for rel in args.paths
        if rel.startswith(prefix) and rel.endswith(".md") and (repo_root / rel).is_file()
    ]
    # No debug artifact in scope is a no-op, not a failure: most commits touch none.
    return scoped or None


def _unspeakable_adapter_version(repo_root: Path) -> str | None:
    """Refuse before scoping when the debug adapter declares an unreadable version.

    Without it this validator would resolve BOTH halves of its own scope from charness
    defaults: `_owned_prefix` would invent `charness-artifacts/debug/` for a repo that
    declared elsewhere -- exactly the "prefix this repo never declared" its own docstring
    refuses -- and `resolve_adapter_line_budget` would enforce the shipped 180 over a
    repo that declared 60, silently raising a ceiling it was told to lower.
    """
    return _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="debug-adapter.yaml"
    )


def _adapter_output_dir(repo_root: Path) -> str | None:
    """The output directory, read exactly as `_debug_artifacts` reads it."""
    # Deliberately NOT keyed on the adapter's `valid` flag, which the first repair tried
    # and which was a net regression. Two reasons, both measured against the real resolver:
    #
    # * It does not catch what it was written for. `output_dir: [unclosed` parses to the
    # plain STRING `[unclosed` with no errors -- `valid: True` -- so the garbage prefix
    # passed the check anyway. What actually stops that run is `_debug_artifacts`
    # refusing a directory that does not exist, which fired before any of this.
    # * In the direction it DID bite, it disarmed the repair it was part of. Debug's
    # `validate_adapter_data` still populates a perfectly good `output_dir` when the
    # adapter is invalid for an unrelated reason (a bad `repo` type), so a one-line
    # adapter typo made this return None -- which silently turned the named-path refusal
    # back off AND left every artifact on the legacy ruleset, with nothing printed,
    # because `_debug_artifacts` never inspects `valid` either. A refusal disabled by a
    # typo is the exact class this whole slice exists to close.
    #
    # `version: 9` USED to be an example in that second bullet and no longer is: a
    # version this reader cannot speak now honors no declared field at all, so this
    # would read the shipped default rather than the repo's directory. That case is
    # refused by `_unspeakable_adapter_version` before any scoping runs, which is why
    # `valid` is still the wrong predicate here and a refused VERSION is a different
    # question from an invalid adapter.
    #
    # Reading the same value `_debug_artifacts` uses is what keeps the two paths from
    # disagreeing about one adapter. The blank guard below stays, because that one is real.
    output_dir = load_adapter(repo_root).get("data", {}).get("output_dir")
    # An adapter declaring `output_dir: ""` (or whitespace) validates clean, and an empty
    # prefix would make EVERY named path look owned -- the refusal would then fire on
    # paths belonging to no debug family at all, breaking ordinary commits. That is the
    # opposite failure from the one the prefix exists to prevent, so it is guarded here
    # rather than left to the directory check.
    if not isinstance(output_dir, str) or not output_dir.strip():
        return None
    return output_dir


def _owned_prefix(repo_root: Path) -> str | None:
    """The artifact directory this validator owns, resolved after `--repo-root` is parsed.

    A callable, not a constant, because debug is the one family whose output directory is
    adapter-declared. Inventing a prefix when the adapter cannot be trusted would refuse
    named paths against a directory this repo never declared; the adapter failure itself
    is reported by `_debug_artifacts`.
    """
    output_dir = _adapter_output_dir(repo_root)
    if output_dir is None:
        return None
    return f"{Path(output_dir).as_posix().rstrip('/')}/"


def _current_pointer(repo_root: Path) -> Path | None:
    """The adapter-declared current-pointer path, for the strict-vs-legacy role test."""
    output_dir = _adapter_output_dir(repo_root)
    if output_dir is None:
        return None
    return repo_root / output_dir / "latest.md"


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


def _validate_factory(run):
    """Bind the per-RUN state once, not once per artifact.

    `_current_pointer` reads and parses the adapter, and inlining it in the inner lambda
    ran that find-read-parse-validate cycle for every artifact in the corpus -- ~150
    times on a full sweep, on the repo's own commit-boundary latency budget. It is
    per-run state; the outer factory is where per-run state belongs.
    """
    current_pointer = _current_pointer(run.repo_root)
    max_words = resolve_adapter_line_budget(
        load_adapter, run.repo_root, field=WORD_BUDGET_FIELD, default=MAX_ARTIFACT_WORDS
    )
    return lambda artifact: validate_debug_artifact(
        artifact,
        collect_all=run.collect_all,
        current_pointer=current_pointer,
        max_words=max_words,
        evidence_mode=run.args.evidence_mode,
        repo_root=run.repo_root,
    )


def _exit_not_a_violation(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _add_validator_args(parser) -> None:
    parser.add_argument(
        "--evidence-led",
        dest="evidence_mode",
        action="store_true",
        help="Require and validate the typed evidence-led sections.",
    )


def main() -> int:
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked-in debug artifact.",
        artifact_label="debug artifact",
        # Without an owned prefix, `unresolvable_named_paths` owns nothing and the
        # named-path refusal cannot fire: `--paths <a path that does not exist>` printed
        # "No debug artifacts in scope." and exited 0, having validated nothing. That was
        # harmless while every emitted command was unscoped, and became a silent pass the
        # moment the planner and scaffold started naming the artifact being authored --
        # run the emitted gate before writing the file, or after writing it somewhere
        # else, and it went green. `retro`, `ideation` and `critique` all declare theirs;
        # debug is the family that had scoping without the refusal that makes it safe.
        #
        # Resolved from the adapter rather than a constant because debug is the one
        # family whose output directory is adapter-declared. A repo with no readable
        # adapter yields None, which restores the previous own-nothing behavior -- the
        # adapter failure is reported by `_debug_artifacts`, and inventing a prefix here
        # would refuse paths against a directory this repo never declared.
        owned_prefix=_owned_prefix,
        preflight=_unspeakable_adapter_version,
        artifacts_fn=_debug_artifacts,
        validate_factory=_validate_factory,
        extra_args=_add_validator_args,
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
