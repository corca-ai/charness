#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _skill_script(repo_root: Path, name: str) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "handoff" / "scripts" / name,
        repo_root / "skills" / "handoff" / "scripts" / name,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"handoff {name} not found")


def _resolver_path(repo_root: Path) -> Path:
    return _skill_script(repo_root, "resolve_adapter.py")


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


def validate_subagent_blocker_reasoning(lines: list[str]) -> None:
    for raw in lines:
        lowered = raw.lower()
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in lowered:
                raise ValidationError(
                    "handoff artifact must not treat missing explicit subagent allowance as the canonical blocker; "
                    "name the capability probe rule and the concrete host signal instead"
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


def validate_handoff_artifact(path: Path, *, collect_all: bool = False) -> None:
    lines = read_lines(path)
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
        lambda: validate_no_regenerable_facts(path),
        lambda: validate_subagent_blocker_reasoning(lines),
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
    validate_handoff_artifact(artifact_path, collect_all=not args.fail_fast)
    print(f"Validated handoff artifact {_display_path(artifact_path, repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        sys.exit(report_validation_failure(str(exc), artifact_type="handoff"))
        sys.exit(1)
