from __future__ import annotations

import re

from scripts.setup_markdown_section_lib import extract_section

COMPACT_SKILL_ROUTING_CALL_RE = re.compile(r"\b(charness\s+catalog|catalog\s+list)\b")
COMPACT_SKILL_ROUTING_NEGATED_CALL_RE = re.compile(
    r"\b(do not|don't|never)\s+(run|use)\s+.*catalog"
)


def skill_routing_semantically_complete(section_body: str) -> bool:
    """Recognize the routing contract by capabilities, not generated prose."""
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


def agents_skill_routing_semantically_complete(agents_text: str) -> bool:
    return skill_routing_semantically_complete(extract_section(agents_text, "## Skill Routing"))
