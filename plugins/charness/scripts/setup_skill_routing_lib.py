from __future__ import annotations

import re

from scripts.setup_markdown_section_lib import extract_section

COMPACT_SKILL_ROUTING_CALL_RE = re.compile(r"\b(charness\s+catalog|catalog\s+list)\b")
COMPACT_SKILL_ROUTING_NEGATED_CALL_RE = re.compile(
    r"\b(do not|don't|never)\s+(run|use)\s+.*catalog"
)
# Inflected forms are matched deliberately. These read PROSE an operator wrote, and the
# repo's own guidance describes the block in the third person ("a nonzero result reports a
# command failure") while the generated block uses the imperative ("report the command
# failure"). `\breport\b` matches only the second, so a block written from
# `skills/public/setup/references/default-surfaces.md` was reported as drifted from the
# block that reference describes -- the same reader/writer split as #552, one signal over.
DIRECT_WORKFLOW_ACTION_RE = re.compile(r"\b(start|choose|route|invoke)(s|d|ed|ing)?\b")
CATALOG_FAILURE_ACTION_RE = re.compile(r"\b(report|surface)(s|d|ed|ing)?\b")
NONZERO_RESULT_RE = re.compile(r"\bnon[- ]?zero\b")

# #552: this signal used to require the literal token `context-only`. The renderer that
# actually WRITES the block a `charness setup` repo carries
# (`skills/public/setup/scripts/render_skill_routing.py`, invoked from that skill's
# SKILL.md) says the same thing in different words -- "may inject this context when
# installed; this block is the fallback when it is absent" -- and never emits
# `context-only`. Because the signals below are combined with `all(...)`, that one word
# made `charness_managed` permanently False for every setup-seeded repo, and the two
# AGENTS.md policy findings gated behind it
# (`agents_missing_charness_dynamic_workflow_policy`,
# `agents_missing_subagent_model_policy` in `scripts/setup_agent_docs_lib.py`) could
# never fire in the repos they were written for. A gate that cannot fire is a permanent
# green.
#
# The claim this signal exists to recognize is not a spelling: it is that the routing
# block names the SessionStart hook AND declares that the hook is not the authority --
# the block stands on its own when the hook is absent. Both shipped spellings assert
# that, so both are accepted. The detector deliberately does NOT compare against the
# renderer's output: it must keep reading hand-written AGENTS.md too. The
# renderer-to-reader reconciliation belongs in a test that pins the renderer's REAL
# output (see `tests/quality_gates/test_setup_render_skill_routing.py`), because every
# fixture for this predicate spelled it `context-only` and that is how this hid.
#
# Two parts, each matched inside ONE segment, where a segment is a line or a sentence.
#
# Searching the section as one blob does not work, and neither does requiring both parts
# in a single sentence. A bounded review found both failure directions, and both are the
# SAME defect class this signal was repaired for:
#
#   * Blob search lets the polarity word be about anything. Signal 4 already requires
#     `gather` in the section, and this repo's own gather prose says "browser-mediated
#     fallback", so a block whose hook sentence declares the hook AUTHORITATIVE reads as a
#     valid declaration on the strength of a word about acquisition paths.
#   * One-sentence-carries-everything breaks on punctuation, not on meaning. Markdown
#     bullets carry no terminal period, so a bulleted block collapses to a single
#     "sentence" and silently degenerates to blob search -- while a correct block that
#     spells the claim as two sentences ("The SessionStart hook may inject this context.
#     This block is the fallback when the hook is absent.") gets REFUSED.
#
# So the polarity claim must instead name its own subject: `denies_authority` requires a
# segment carrying a polarity token AND the word `hook` or `block`. That is what makes the
# gather line fail -- it is about URLs -- without depending on where a period lands. The
# two parts may live in different segments, because a claim spanning two bullets is still
# the claim.
#
# KNOWN LIMITS, stated rather than implied, because a check that overstates its reach is
# the same defect one layer up:
#   * Substring matching has no polarity WITHIN a segment. "the hook is authoritative, so
#     this block is not a fallback" satisfies `denies_authority` and passes.
#   * A section written as one unpunctuated run-on line is one segment, so it gets the
#     coarse behavior above. Bulleted and sentence-terminated prose -- every shipped and
#     hand-written form seen so far -- segments correctly.
#   * The hook tokens are the two real spellings plus `session start`; a routing block
#     that calls it something else entirely is not recognized.
SESSION_START_HOOK_RE = re.compile(r"\bsessionstart\b|\bsession[- ]start\b")
HOOK_NOUN_RE = re.compile(r"\bhook\b")
HOOK_IS_NOT_AUTHORITATIVE_RE = re.compile(r"\bcontext[- ]only\b|\bfallback\b")
# What the polarity claim must be ABOUT for it to count as a claim about this contract.
POLARITY_SUBJECT_RE = re.compile(r"\bhook\b|\bblock\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _routing_segments(section_body: str) -> list[str]:
    """Lines first, then sentences: a markdown bullet is a segment even with no period."""
    segments = []
    for line in section_body.lower().splitlines():
        for sentence in SENTENCE_SPLIT_RE.split(line):
            collapsed = " ".join(sentence.split())
            if collapsed:
                segments.append(collapsed)
    return segments


def _declares_session_start_hook_is_not_authoritative(section_body: str) -> bool:
    """The block must name the session-start hook and deny it authority over the block."""
    segments = _routing_segments(section_body)
    names_hook = any(
        SESSION_START_HOOK_RE.search(segment) and HOOK_NOUN_RE.search(segment)
        for segment in segments
    )
    denies_authority = any(
        HOOK_IS_NOT_AUTHORITATIVE_RE.search(segment) and POLARITY_SUBJECT_RE.search(segment)
        for segment in segments
    )
    return names_hook and denies_authority


def skill_routing_declares_charness_management(section_body: str) -> bool:
    """Recognize a Charness routing surface before judging its completeness."""
    text = " ".join(section_body.lower().split())
    signals = (
        "docs/handoff.md" in text and "workflow trigger" in text,
        "installed skill metadata" in text and "model judgment" in text,
        "read-only" in text and bool(COMPACT_SKILL_ROUTING_CALL_RE.search(text)),
        "gather" in text and "external" in text and ("url" in text or "source" in text),
        "quality" in text and "validation" in text,
        # Passed the RAW body, not `text`: collapsing whitespace destroys the line breaks
        # that make a bulleted block segmentable.
        _declares_session_start_hook_is_not_authoritative(section_body),
    )
    return all(signals)


def skill_routing_semantically_complete(section_body: str) -> bool:
    """Recognize the complete routing contract by capabilities, not generated prose."""
    text = " ".join(section_body.lower().split())
    return skill_routing_declares_charness_management(section_body) and all(
        (
            "direct" in text
            and bool(DIRECT_WORKFLOW_ACTION_RE.search(text))
            and ("workflow" in text or "skill" in text),
            bool(NONZERO_RESULT_RE.search(text))
            and bool(CATALOG_FAILURE_ACTION_RE.search(text))
            and "failure" in text,
        )
    )


def agents_skill_routing_semantically_complete(agents_text: str) -> bool:
    return skill_routing_semantically_complete(extract_section(agents_text, "## Skill Routing"))
