#!/usr/bin/env python3
"""Core-density accounting for a SKILL.md: what counts, what is exempt, and the
audit that keeps the exemption honest.

Split out of `check_skill_surface_preflight.py` because it is one cohesive
concept — how many lines of decision prose a skill core is spending. The
preflight owns the verdict and the CLI; this module owns the count. The quality
inventory and the quality-artifact count check call the same function, so a
quoted `core_nonempty_lines` cannot drift from the authoring cap.

The exemption's contract, in one line: a heading is exempt only up to a budget,
and whatever is exempted is also audited. Exempting more than the audit reads is
what let 60 lines of prose cost nothing (2026-07-28 triage sweep, row S5)."""
from __future__ import annotations

import re


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.skill_markdown_lib import split_fenced_lines, strip_frontmatter  # noqa: E402

# `Closeout Vocabulary` is headroom-exempt so a skill can keep the literal tokens
# a representative run must reproduce VERBATIM for a well-formed / validator-
# passing closeout (status enums, exact substring-matched strings) in core,
# without those tokens paying core decision-prose density. The total
# MAX_SKILL_MD_LINES ceiling still counts them (a file-size guard).
CLOSEOUT_VOCAB_SECTION = "Closeout Vocabulary"
PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References", CLOSEOUT_VOCAB_SECTION}
# A `## Closeout Vocabulary` block is token-shaped: at most this many non-empty
# lines, each a label + one clause, never multi-sentence prose.
CLOSEOUT_VOCAB_MAX_LINES = 9
# The exemption is BOUNDED, per heading and summed across every block carrying
# that heading: a skill gets this many exempt non-empty lines, and every line past
# the budget pays core density like ordinary prose. An unbounded exemption was a
# density hatch — 60 lines of prose under a second `## Closeout Vocabulary`, or
# under the first `## References`, counted as zero. Budgets sit just above the
# live corpus maxima (References 24, Closeout Vocabulary 3, Load-Bearing Anchors
# absent) rather than far above: overflow only charges density, so a tight budget
# costs an over-long list some headroom, never a block.
PRESSURE_EXEMPT_BUDGET = {
    "Load-Bearing Anchors": CLOSEOUT_VOCAB_MAX_LINES,
    "References": 28,
    CLOSEOUT_VOCAB_SECTION: CLOSEOUT_VOCAB_MAX_LINES,
}

# A period/question/exclamation followed by whitespace + a capital letter is a
# sentence boundary. A token line (`ran-fail-deferred <command> <issue|anchor>`,
# a slash-separated enum) never matches; multi-sentence prose does.
_SENTENCE_BOUNDARY_RE = re.compile(r"[.!?]\s+[A-Z]")
# Two shapes match that regex without being prose, and both are ordinary in a
# reference list: an ordered-list marker (`1. Read the ladder`) and an
# abbreviation before a proper noun (`… defaults, e.g. Codex hosts`). Strip the
# marker and blind the abbreviations before deciding, or the audit hard-blocks a
# legitimate skill.
_ORDERED_MARKER_RE = re.compile(r"^\s*(?:[-*+]\s+)?\d+[.)]\s+")
_ABBREVIATIONS = ("e.g.", "i.e.", "cf.", "vs.", "etc.", "et al.")
_ABBREVIATION_RE = re.compile(
    "|".join(re.escape(abbreviation) for abbreviation in _ABBREVIATIONS), re.IGNORECASE
)


def _is_multi_sentence(line: str) -> bool:
    body = _ORDERED_MARKER_RE.sub("", line)
    body = _ABBREVIATION_RE.sub(lambda match: "_" * len(match.group(0)), body)
    return bool(_SENTENCE_BOUNDARY_RE.search(body))


def split_pressure_exempt_sections(
    lines: list[str],
) -> tuple[list[str], dict[str, list[list[str]]]]:
    """Partition body lines into non-exempt lines and every exempt section's blocks.

    `exempt_blocks[section]` holds one list of body lines per `## <section>`
    occurrence — *every* occurrence, not just the first, so the exemption and its
    audit read the same blocks.

    Inside a code fence, heading DETECTION is suppressed — a documentation skill
    teaching SKILL.md shape carries a literal `## References` in a fence, and
    treating that as a real heading would exempt everything after it. The fenced
    lines themselves are still counted: dropping them would hand back exactly the
    free-prose hatch this module exists to close."""
    kept: list[str] = []
    exempt_blocks: dict[str, list[list[str]]] = {}
    current: list[str] | None = None
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        elif stripped.startswith("## ") and not in_fence:
            section = stripped[3:].strip()
            current = None
            if section in PRESSURE_EXEMPT_H2_SECTIONS:
                current = []
                exempt_blocks.setdefault(section, []).append(current)
                continue
        if current is not None:
            current.append(line)
        else:
            kept.append(line)
    return kept, exempt_blocks


def pressure_exempt_overflow(exempt_blocks: dict[str, list[list[str]]]) -> dict[str, int]:
    """Exempt lines charged back to core density, per heading.

    Two ways an exempt line pays. Past the heading's budget, any line pays. And a
    FENCED line inside an exempt block always pays, whatever the budget: the audit
    excuses fenced lines (they are quoted examples, not the author's assertions),
    so charging them is what keeps a fence from being a window that is both
    uncharged and unread."""
    overflow: dict[str, int] = {}
    for section, blocks in exempt_blocks.items():
        fenced = sum(1 for block in blocks for line in split_fenced_lines(block)[1] if line.strip())
        nonempty = sum(1 for block in blocks for line in block if line.strip())
        # The budget covers the lines the audit actually reads; fenced lines are
        # excused from the audit, so they never consume budget and always pay.
        budget = PRESSURE_EXEMPT_BUDGET.get(section, 0)
        charged = fenced + max(nonempty - fenced - budget, 0)
        if charged:
            overflow[section] = charged
    return overflow





def core_nonempty_lines(text: str) -> int:
    kept, exempt_blocks = split_pressure_exempt_sections(strip_frontmatter(text).splitlines())
    core = sum(1 for line in kept if line.strip())
    return core + sum(pressure_exempt_overflow(exempt_blocks).values())


def pressure_exempt_findings(text: str) -> list[str]:
    """Anti-abuse for every headroom-exempt section, and for every block of it.

    The exemption exists so emittable literal tokens and reference links can live
    in core without paying decision-prose density; it must not become a prose hatch
    that dodges the core-nonempty gate. Audit whatever is exempted: flag an
    over-budget heading (counted across all its blocks) and any line that is
    multi-sentence prose rather than a token or a reference entry.

    Auditing only the FIRST `## Closeout Vocabulary` while exempting every one of
    them was the defect: a second block of the same heading, or an unaudited
    sibling heading, was exempt and unread.

    Going over budget is NOT a finding: the overflow already pays core density
    (`core_nonempty_lines`), and the density ceiling is the verdict that owns it.
    A finding here blocks, so raising one for an over-long-but-token-shaped
    reference list would block a legitimate skill on a rule whose own message says
    it merely costs density."""
    exempt_blocks = split_pressure_exempt_sections(strip_frontmatter(text).splitlines())[1]
    findings: list[str] = []
    for section in sorted(exempt_blocks):
        for block in exempt_blocks[section]:
            # A fenced example is the author quoting the shape a run must emit —
            # `## Closeout Vocabulary` exists to carry exactly that — so it is not
            # the author's own prose. Fenced lines still PAY density; they are only
            # excused from the prose audit, which blocks.
            for line in split_fenced_lines(block)[0]:
                if line.strip() and _is_multi_sentence(line):
                    findings.append(
                        f"`## {section}` line is multi-sentence prose, not a token: "
                        f"{line.strip()[:80]!r}"
                    )
    return findings
