#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "handoff" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("handoff resolve_adapter.py not found")


_handoff_resolve_adapter = load_path_module("handoff_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _handoff_resolve_adapter.load_adapter
_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
validate_max_lines = _scripts_artifact_validator_module.validate_max_lines
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
validate_title = _scripts_artifact_validator_module.validate_title

MAX_ARTIFACT_LINES = 70
REQUIRED_SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
# The handoff skill's Output Shape lists this section; rejecting it here would make
# following the skill a gate failure. It stays optional because the skill says the
# handoff "should usually contain" it, not always -- but an empty one is a header
# pretending to be a baton, so presence implies content.
OPTIONAL_SECTIONS = ("## Continuation Capability",)
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
    canonical = set(REQUIRED_SECTIONS) | set(OPTIONAL_SECTIONS)
    return tuple(line.strip() for line in lines if line.strip() in canonical)


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


def validate_handoff_artifact(path: Path) -> None:
    lines = read_lines(path)
    validate_title(
        lines,
        title_predicate=lambda line: line.startswith("# ") and "handoff" in line.lower(),
        error_message="handoff artifact must start with a `# ... Handoff` heading",
    )
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="handoff artifact")
    validate_exact_h2_sections(lines, REQUIRED_SECTIONS, optional_sections=OPTIONAL_SECTIONS)
    validate_nonempty_sections(lines, ordered_present_sections(lines))
    validate_references(lines)
    validate_no_regenerable_facts(path)
    validate_subagent_blocker_reasoning(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    artifact_path = repo_root / adapter["artifact_path"]
    validate_handoff_artifact(artifact_path)
    print(f"Validated handoff artifact {artifact_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
