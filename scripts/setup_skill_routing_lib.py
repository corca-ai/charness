from __future__ import annotations

import re

from scripts.setup_markdown_section_lib import extract_section

COMPACT_SKILL_ROUTING_CALL_RE = re.compile(r"\b(charness\s+catalog|catalog\s+list)\b")
COMPACT_SKILL_ROUTING_NEGATED_CALL_RE = re.compile(
    r"\b(do not|don't|never)\s+(run|use)\s+.*catalog"
)
DIRECT_WORKFLOW_ACTION_RE = re.compile(r"\b(start|choose|route|invoke)\b")
CATALOG_FAILURE_ACTION_RE = re.compile(r"\b(report|surface)\b")
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
# The claim is matched PER SENTENCE, not across the whole section. Searching the two
# halves independently would let the polarity word be about anything: this repo's own
# `gather` prose pairs "gather" with "browser-mediated fallback", and signal 4 already
# requires `gather` in the section, so an uncoupled search would read
# "...route through `gather`, escalating to the browser-mediated fallback..." plus a
# sentence declaring the hook AUTHORITATIVE as a valid declaration. One sentence must
# carry all three parts. Semicolons deliberately do not split a sentence -- both shipped
# spellings join the hook and its standing with one.
#
# KNOWN LIMIT, stated rather than implied: like its sibling signals this is substring
# matching, so it has no polarity WITHIN a sentence -- "the hook is authoritative, so
# this block is not a fallback" carries all three parts and passes. What the check buys
# is narrow and real: the surface `setup` writes is no longer excluded from its own
# policy checks, and a polarity word about an unrelated subject no longer counts.
SESSION_START_HOOK_RE = re.compile(r"\bsessionstart\b|\bsession[- ]start\b|\bstartup\b")
HOOK_NOUN_RE = re.compile(r"\bhook\b")
HOOK_IS_NOT_AUTHORITATIVE_RE = re.compile(r"\bcontext[- ]only\b|\bfallback\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _declares_session_start_hook_is_not_authoritative(text: str) -> bool:
    """One sentence must name the session-start hook AND deny it authority."""
    return any(
        SESSION_START_HOOK_RE.search(sentence)
        and HOOK_NOUN_RE.search(sentence)
        and HOOK_IS_NOT_AUTHORITATIVE_RE.search(sentence)
        for sentence in SENTENCE_SPLIT_RE.split(text)
    )


def skill_routing_declares_charness_management(section_body: str) -> bool:
    """Recognize a Charness routing surface before judging its completeness."""
    text = " ".join(section_body.lower().split())
    signals = (
        "docs/handoff.md" in text and "workflow trigger" in text,
        "installed skill metadata" in text and "model judgment" in text,
        "read-only" in text and bool(COMPACT_SKILL_ROUTING_CALL_RE.search(text)),
        "gather" in text and "external" in text and ("url" in text or "source" in text),
        "quality" in text and "validation" in text,
        _declares_session_start_hook_is_not_authoritative(text),
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
