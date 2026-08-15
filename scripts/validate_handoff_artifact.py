#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import (
    import_repo_module,
    load_path_module,
    repo_root_from_script,
    skill_script,
)

REPO_ROOT = repo_root_from_script(__file__)


def _skill_script(repo_root: Path, name: str) -> Path:
    return skill_script(repo_root, "handoff", name)


def _resolver_path(repo_root: Path) -> Path:
    return _skill_script(repo_root, "resolve_adapter.py")


DOMINANCE_REGISTRY_PATH = Path(".agents/command-dominance.yaml")


_handoff_resolve_adapter = load_path_module("handoff_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _handoff_resolve_adapter.load_adapter
# The canonical sections and the content-line counting rule are ONE decision
# (which lines the artifact must have -> which lines the budget must not charge
# for), owned by the skill package so the run planner forecasts with the same
# count this gate enforces. Only the enforced ceiling stays here.
_budget = load_path_module(
    "handoff_content_budget", _skill_script(REPO_ROOT, "handoff_content_budget.py")
)
content_lines = _budget.content_lines
REQUIRED_SECTIONS = _budget.REQUIRED_SECTIONS
OPTIONAL_SECTIONS = _budget.OPTIONAL_SECTIONS
CANONICAL_SECTIONS = _budget.CANONICAL_SECTIONS
# Ownership is the skill's authoring contract, not this repo's house style, so
# the predicate ships with the skill for the same reason the budget does: the
# run planner and this gate must agree on what counts as an owner.
_ownership = load_path_module(
    "handoff_bullet_ownership", _skill_script(REPO_ROOT, "handoff_bullet_ownership.py")
)
unowned_entries = _ownership.unowned_entries
has_unclosed_fence = _ownership.has_unclosed_fence
OWNED_SECTIONS = _ownership.OWNED_SECTIONS
_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
add_one_pass_args = _scripts_artifact_validator_module.add_one_pass_args
add_artifact_path_arg = _scripts_artifact_validator_module.add_artifact_path_arg
resolve_artifact_override = _scripts_artifact_validator_module.resolve_artifact_override
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
report_validation_failure = _scripts_artifact_validator_module.report_validation_failure
run_validation_checks = _scripts_artifact_validator_module.run_validation_checks
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
validate_title = _scripts_artifact_validator_module.validate_title

# 78, operator-raised from 58 on 2026-08-11. The re-base that produced 58 fixed the
# right defect -- 13 of the 14 handoffs before it landed at 69-70 against a raw cap of
# 70, a distribution pinned AT the ceiling, while those same files carried only ~50
# CONTENT lines, so the raw count was measuring formatting and penalising long
# reference links while a diary of short lines cost nothing. That correction stands;
# only the ceiling moved.
#
# What moved it: 58 started REFUSING content that changed the next action. The
# 2026-08-11 handoff hit 59/58 while carrying six live operator rulings, and the cut
# that fit it was a real lesson, not padding. A cap that forces the author to choose
# between two load-bearing lines has stopped being a diary guard.
#
# The TARGET stays 25-50 in SKILL.md deliberately, so the gap between target and
# ceiling widens rather than the goal moving. This is a failure guard, not a budget to
# spend: the operator's stated position is that a one-line link plus well-placed
# content should still come in far under it, and the recurring fix remains spilling
# durable detail to its owning artifact rather than filling the new headroom.
MAX_CONTENT_LINES = _budget.DEFAULT_MAX_CONTENT_LINES
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
# Addresses are not claims: an artifact path or release URL may legitimately carry
# a version, and the doc-link gate already keeps repo paths resolvable. All three
# markdown link syntaxes are scrubbed, plus inline code -- the rule tells the author
# to carry a command, so it must not then reject the command it asked for. Link TEXT
# stays in scope, because that is prose the reader believes.
LINK_TARGET_RE = re.compile(r"(?<=\])\([^)]*\)")
URL_RE = re.compile(r"<?\bhttps?://\S+>?")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
# Facts a command regenerates decay in place; the handoff carries the command
# instead. Issue ids are deliberately absent -- an id is a stable identifier, not a
# snapshot, and the artifact already tells the reader to re-check its state.
#
# NO RULE_DATE grandfather, deliberately. Every RULE_DATE precedent in this repo
# guards a DATED, append-only artifact (critiques, retros, goals) where old files
# persist and must not retroactively fail. The handoff is a single rolling document
# rewritten each session, so there is no landing date to key a floor on and nothing
# historical to protect -- the next rewrite is the migration.
REGENERABLE_PATTERNS = (
    (
        # `v` prefix allows a two-component version (`v1.2` goes stale just as
        # fast); without it three components are required, so a bare ratio like
        # "1.4x the budget" is not a version claim.
        re.compile(r"\b(?:v\d+\.\d+(?:\.\d+)?|\d+\.\d+\.\d+)\b"),
        "a release or tool version",
        "`git describe --tags --abbrev=0`, or link the release artifact",
    ),
    (
        # Hex-only, 7-40 chars, carrying BOTH a digit and an a-f letter, so English
        # words that happen to be hex (`defaced`, `acceded`) do not fire.
        # Case-insensitive: a sha pasted from a web UI arrives uppercase. Known
        # escape: an all-digit short sha (~3.7% of 7-char shas) reads as a plain
        # number and is deliberately let through rather than firing on every
        # 7-digit integer.
        re.compile(
            r"\b(?=[0-9a-fA-F]{7,40}\b)(?=[0-9a-fA-F]*\d)(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{7,40}\b"
        ),
        "a commit sha",
        "`git log --oneline -1`, or name the change instead of its hash",
    ),
    (
        # The lookbehind keeps identifiers and date fragments out of the count
        # rule: `#371 issue` names an issue, and `2026-07-25 docs` is a date, not
        # "25 docs". The noun list is a closed enumeration by design -- it catches
        # the common shapes, not every possible count, and widening it trades
        # false negatives for false positives on ordinary prose.
        re.compile(
            r"(?<![#\w.\-])\d+\s+(?:tests?|files?|docs?|lines?|commits?|issues?|skills?|scripts?|cases?|artifacts?)\b"
        ),
        "an as-of count",
        "the command that recounts it, or the owning artifact that holds the measurement",
    ),
)
FORBIDDEN_SUBAGENT_BLOCKER_PHRASES = (
    "did not explicitly allow subagents",
    "explicit subagent allowance",
)


def ordered_present_sections(lines: list[str]) -> tuple[str, ...]:
    """Canonical sections present in this artifact, in document order.

    `validate_nonempty_sections` bounds each section by the NEXT entry it is given,
    so an optional section left out of that list would be silently absorbed into
    the preceding section's content and never checked for emptiness.
    """
    return tuple(line.strip() for line in lines if line.strip() in CANONICAL_SECTIONS)


def validate_no_regenerable_facts(path: Path) -> None:
    """Reject facts the reader could regenerate, because they decay in place.

    The handoff is a continuation pointer. A transcribed version, sha, or count is
    true only on the day it is written, and a stale one is worse than an absent
    one: the next operator acts on it instead of checking.

    Scans prose only. Fenced blocks and inline code carry the commands this rule
    asks the author to write, so scanning them would reject the replacement it
    just recommended.
    """
    for _lineno, raw, in_fence in iter_doc_lines(path):
        if in_fence:
            continue
        scrubbed = INLINE_CODE_RE.sub("", URL_RE.sub("", LINK_TARGET_RE.sub("", raw)))
        for pattern, label, replacement in REGENERABLE_PATTERNS:
            match = pattern.search(scrubbed)
            if match is None:
                continue
            raise ValidationError(
                f"handoff artifact transcribes {label} (`{match.group(0).strip()}`); a fact a command "
                f"can regenerate goes stale in place. Carry the command instead: {replacement}."
            )


def validate_references(lines: list[str]) -> None:
    start = find_index(lines, "## References") + 1
    section_lines = [line.strip() for line in lines[start:] if line.strip()]
    if not any(MARKDOWN_LINK_RE.search(line) for line in section_lines):
        raise ValidationError("`## References` must contain at least one markdown link")


# What remains of a line once its markdown links are gone. Link TEXT goes with
# the link: `- [deferred-decisions.md](./deferred-decisions.md)` names the file
# twice and still says nothing about the relationship, which is the whole
# finding. Punctuation-only remainders (`- [x](y).`) do not count either.
_DESCRIPTOR_TEXT_RE = re.compile(r"[A-Za-z0-9]")


def _descriptorless_reference_lines(lines: list[str], start: int) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for offset, raw in enumerate(lines[start:], start=start + 1):
        stripped = raw.strip()
        # STOP at the next H2. The exact-H2 check asserts membership, not ORDER,
        # and `## Continuation Capability` is optional and legal anywhere -- so a
        # handoff that puts `## References` before `## Discuss` was having its
        # Discuss bullets refused, under a message calling them References
        # entries. Scanning to EOF made the docstring's "scoped to `## References`"
        # false for every artifact whose References section is not last.
        if stripped.startswith("## "):
            break
        if not MARKDOWN_LINK_RE.search(stripped):
            continue
        remainder = MARKDOWN_LINK_RE.sub("", stripped).lstrip("-*").strip()
        if not _DESCRIPTOR_TEXT_RE.search(remainder):
            found.append((offset, stripped))
    return found


def validate_reference_descriptors(lines: list[str]) -> None:
    """Refuse a `## References` link that carries no context on its OWN line.

    The section is exempt from the content-line ceiling and is required to hold a
    link, so it is where links pool — a budget-free, link-required section is
    exactly where context-free links collect. Two consumer repos measured their
    `docs/handoff.md` as a leading contributor to a wiki linter's
    `link_only_lines` count, and neither could fix it locally: the next handoff
    run rewrites the section from the scaffold.

    SAME-LINE deliberately, not same-entry. A descriptor wrapped onto the
    following line reads fine to a human and still leaves a physical line whose
    entire content is one link, which is what the linter judges and what makes a
    grep hit uninterpretable. So wrap AFTER the first words of the descriptor,
    not before it. Markdownlint's line-length rule is off in this repo
    (`.markdownlint-cli2.jsonc` sets `MD013: false`), so the long line this
    sometimes produces is not trading one gate for another.

    Scoped to `## References` because that is the section this validator's own
    contract shapes. `## Current State` and `## Next Session` are already held by
    the stronger ownership rule.
    """
    start = find_index(lines, "## References") + 1
    found = _descriptorless_reference_lines(lines, start)
    if not found:
        return
    detail = "; ".join(f"line {lineno}: {text[:60]}" for lineno, text in found)
    raise ValidationError(
        f"{len(found)} `## References` entry(s) carry a link and no descriptor on the link's own "
        f"line — {detail}. Add a short phrase saying what the linked document HOLDS, on the same "
        "physical line as the link (`- [name](path) — what it holds`), and wrap after those words "
        "rather than before them. A line whose whole content is one link gives a reader no local "
        "context and makes a grep hit uninterpretable."
    )


def validate_closed_fences(lines: list[str]) -> None:
    """Refuse an artifact whose fence never closes.

    Not a style rule. An unclosed fence makes every later line read as fenced,
    so the ownership scan silently sees no entries at all and the artifact
    passes green. Markdownlint has no rule for this — CommonMark closes the
    fence at EOF and the document is valid — so nothing else in the stack
    notices.
    """
    if has_unclosed_fence(lines):
        raise ValidationError(
            "handoff artifact: code fence delimiters could not be paired; every line after the "
            "unpaired one reads as fenced, so the ownership rule would scan an empty section and "
            "pass. Close the fence, or move a fence-delimiter line that is meant as content."
        )


def validate_bullet_ownership(lines: list[str]) -> None:
    """Reject state/next-action entries the reader cannot open, run, or look up.

    Reports every unowned entry at once. The one-pass contract exists because a
    draft violating N rules used to cost N gate runs, and ownership is the rule
    most likely to be violated several times in one rewrite.
    """
    found = unowned_entries(lines)
    if not found:
        return
    detail = "; ".join(f"{section} line {lineno}: {text[:60]}" for section, lineno, text in found)
    raise ValidationError(
        f"{len(found)} entry(s) in {' and '.join(OWNED_SECTIONS)} carry no owner — {detail}. "
        "A state or next-action claim needs something the next operator can check: a markdown "
        "link to the artifact that owns the detail, an inline command that regenerates the fact, "
        "or an issue id. Prose describing another artifact's contents without pointing at it is "
        "the shape that goes stale in place."
    )


def validate_subagent_blocker_reasoning(lines: list[str]) -> None:
    for raw in lines:
        lowered = raw.lower()
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in lowered:
                raise ValidationError(
                    "handoff artifact must not treat missing explicit subagent allowance as the canonical blocker; "
                    "name the capability probe rule and the concrete host signal instead"
                )


def _dominance_registry(repo_root: Path):
    """The repo's dominated-command registry, or None when it has none.

    ABSENCE IS NOT A FAILURE, and that is load-bearing rather than lenient: this
    validator ships to consumers through `plugins/charness/`, and a consumer has
    no `.agents/command-dominance.yaml`. Raising here would hand every consuming
    repo a red handoff gate on upgrade — the stranded-consumer shape the export
    slice before this one was built to end. A malformed registry IS refused,
    because that is a repo that tried to arm the rule and failed.
    """
    registry_path = repo_root / DOMINANCE_REGISTRY_PATH
    if not registry_path.is_file():
        return None, None
    # REPO_ROOT, not `repo_root`: the library ships beside this validator, while
    # the registry belongs to the tree being validated. Mixing them makes the rule
    # unreachable for any caller pointing at another tree.
    dominance = load_path_module(
        "command_dominance_lib_for_handoff",
        skill_script(REPO_ROOT, "quality", "command_dominance_lib.py"),
    )
    adapter = import_repo_module(__file__, "scripts.adapter_lib")
    # `load_yaml_file_report`, matching the dominance gate. The first version used
    # `load_yaml_file` while this function's own docstring promised a malformed
    # registry IS refused -- and the adapter parser DROPS what it cannot
    # interpret, so a registry written in flow style parsed to zero rules here,
    # `scan_document` returned nothing, and every handoff prescribing a dominated
    # command passed while the sibling gate refused the same file loudly. Two
    # readers of one proof surface disagreeing is the class this release already
    # reconciled once.
    data, uninterpreted = adapter.load_yaml_file_report(registry_path)
    if uninterpreted:
        raise ValidationError(
            f"{DOMINANCE_REGISTRY_PATH} has line(s) this reader dropped, so the "
            "dominated-command rule would run over a registry it did not fully read:\n  "
            + "\n  ".join(adapter.uninterpreted_warnings(uninterpreted))
        )
    return dominance, dominance.parse_registry(data)


def validate_no_dominated_commands(path: Path, repo_root: Path) -> None:
    """Refuse a handoff that PRESCRIBES a command a cheaper one dominates (SC14).

    The instance this exists for passed fresh-eye review three times, because it
    was TRUE: `python3 -m pytest tests/ -q --no-header` really does re-prove the
    suite, in ~22 minutes, and three slices paid it without asking. Review is
    aimed at falsity; a dominated-but-true instruction needs a reader that asks
    about cost instead.

    Two honest limits, stated here rather than left for a reader to discover.
    The registry is a DENYLIST: an unregistered slow command passes, so a green
    handoff is not a cheap one. And only fenced blocks and inline code are read
    (`command_dominance_lib.iter_document_commands`), so a handoff that names a
    command in prose is invisible to this rule.
    """
    try:
        dominance, registry = _dominance_registry(repo_root)
    except FileNotFoundError:
        # The quality skill is not installed beside this validator. Nothing to
        # arm; the same reasoning as an absent registry.
        return
    except ValueError as exc:
        # `RegistryError` subclasses ValueError. Without this the validator DIED
        # with a traceback on a registry naming an unknown version or a duplicate
        # rule id -- rendering no verdict at all, which is what the sibling gate's
        # `test_the_entrypoint_renders_a_named_error_rather_than_a_traceback`
        # exists to prevent and this seam had no counterpart for. Found by a
        # round-2 reviewer.
        raise ValidationError(
            f"{DOMINANCE_REGISTRY_PATH} cannot be read as a dominance registry: {exc}"
        ) from exc
    if registry is None:
        return
    findings = dominance.scan_document(
        path.read_text(encoding="utf-8"), registry, site=_display_path(path, repo_root)
    )
    blocking = [finding for finding in findings if not finding.exempt]
    if not blocking:
        return
    raise ValidationError(
        "handoff artifact prescribes a command a cheaper one dominates:\n  "
        + "\n  ".join(dominance.finding_message(finding) for finding in blocking)
    )


def _display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative when the artifact is inside the repo, absolute otherwise.

    `--artifact-path` accepts a draft outside the tree (a temp dir), so an
    unconditional `relative_to` would raise on the success path.
    """
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def validate_max_content_lines(lines: list[str]) -> None:
    counted = content_lines(lines)
    if len(counted) <= MAX_CONTENT_LINES:
        return
    raise ValidationError(
        f"handoff artifact has {len(counted)} content lines (limit {MAX_CONTENT_LINES}); "
        f"cut ~{len(counted) - MAX_CONTENT_LINES}. Blank lines, the required `##` headings, "
        "and the whole `## References` block are NOT counted, so trimming formatting or "
        "shortening reference links will not help — drop state that does not change the "
        "next operator's first action, or spill durable detail to its owning artifact."
    )


def validate_handoff_artifact(
    path: Path, *, collect_all: bool = False, repo_root: Path | None = None
) -> None:
    lines = read_lines(path)
    # Defaulted rather than required: every existing caller passes a path alone,
    # and REPO_ROOT is what they all meant. A required parameter here would be a
    # breaking signature change for a validator that ships to consumers.
    root = (repo_root or REPO_ROOT).resolve()
    checks = (
        lambda: validate_title(
            lines,
            title_predicate=lambda line: line.startswith("# ") and "handoff" in line.lower(),
            error_message="handoff artifact must start with a `# ... Handoff` heading",
        ),
        lambda: validate_max_content_lines(lines),
        lambda: validate_exact_h2_sections(
            lines, REQUIRED_SECTIONS, optional_sections=OPTIONAL_SECTIONS
        ),
        lambda: validate_nonempty_sections(lines, ordered_present_sections(lines)),
        lambda: validate_references(lines),
        lambda: validate_reference_descriptors(lines),
        lambda: validate_closed_fences(lines),
        lambda: validate_bullet_ownership(lines),
        lambda: validate_no_regenerable_facts(path),
        lambda: validate_subagent_blocker_reasoning(lines),
        lambda: validate_no_dominated_commands(path, root),
    )
    # collect_all surfaces every violation in one pass (the CLI default) so a
    # multi-rule draft is fixed in one edit instead of one rule per gate run --
    # a counted limit is a planning input, not a retry loop. --fail-fast opts
    # back into stopping at the first violation.
    run_validation_checks(checks, collect_all=collect_all, artifact_label="handoff artifact")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    add_artifact_path_arg(parser, surface="handoff")
    add_one_pass_args(
        parser,
        fail_fast_help="Stop at the first rule violation instead of reporting every violation in one pass.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.artifact_path is not None:
        artifact_path = args.artifact_path
        if not artifact_path.is_absolute():
            artifact_path = repo_root / artifact_path
        if not artifact_path.is_file():
            print(f"No handoff artifact at {artifact_path}.", file=sys.stderr)
            return 1
    else:
        adapter = load_adapter(repo_root)
        artifact_path = repo_root / adapter["artifact_path"]
    validate_handoff_artifact(artifact_path, collect_all=not args.fail_fast, repo_root=repo_root)
    print(f"Validated handoff artifact {_display_path(artifact_path, repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        sys.exit(report_validation_failure(str(exc), artifact_type="handoff"))
        sys.exit(1)
