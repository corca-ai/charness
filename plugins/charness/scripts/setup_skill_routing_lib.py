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


def skill_routing_declares_charness_management(section_body: str) -> bool:
    """Recognize a Charness routing surface before judging its completeness."""
    text = " ".join(section_body.lower().split())
    signals = (
        "docs/handoff.md" in text and "workflow trigger" in text,
        "installed skill metadata" in text and "model judgment" in text,
        "read-only" in text and bool(COMPACT_SKILL_ROUTING_CALL_RE.search(text)),
        "gather" in text and "external" in text and ("url" in text or "source" in text),
        "quality" in text and "validation" in text,
        "sessionstart" in text and "context-only" in text,
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
