"""Before-phase operator discussion readiness for achieve goals."""
from __future__ import annotations

import re
from typing import Any

DISCUSSION_LABEL = "Discuss before activation"

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_SUMMARY_HEADING = re.compile(r"^(#{2,4})[ \t]+Discuss before activation\b.*$", re.IGNORECASE | re.MULTILINE)
_SUMMARY_LINE = re.compile(r"^[ \t]*(?:[-*][ \t]*)?Discuss before activation:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
_N_A = re.compile(r"^(?:n/?a|none|no consequential|not applicable)\b", re.IGNORECASE)
_RESOLVED = re.compile(r"^(?:resolved|confirmed|approved)\b", re.IGNORECASE)

TRIGGERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("production_or_live_proof", re.compile(r"\b(prod(?:uction)?|live proof|real github lookup|apply/restart|restart|deploy)\b", re.IGNORECASE)),
    ("issue_close_or_split", re.compile(r"\b(close[sd]?|closing|split|leave open|defer(?:red)?)\b.{0,60}#\d+|#\d+.{0,60}\b(close[sd]?|closing|split|leave open|defer(?:red)?)\b", re.IGNORECASE)),
    ("broad_bundle_scope", re.compile(r"\b(bundle[sd]?|broad(?:ly)? bundled|selected bundle|combined|together|all (?:\d+|\w+) proposed)\b|#\d+.{0,60}#\d+", re.IGNORECASE)),
    ("proof_nonclaim_or_downgrade", re.compile(r"\b(proof|verification|live|external).{0,40}\b(non-claim|not run|skipped|fixture-only|downgrad(?:e|ed)|without live|no live)\b|\b(non-claim|fixture-only|without live|no live)\b", re.IGNORECASE)),
    ("irreversible_side_effect", re.compile(r"\b(irreversible|external side effect|production contact|apply/restart|restart|deploy)\b", re.IGNORECASE)),
)

SECTIONS = (
    "Non-Goals",
    "Boundaries",
    "Agent Verification Plan",
    "Interview Decisions",
    "Plan Critique Findings",
)


def _mask_fences(text: str) -> str:
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    return text if in_fence else "".join(masked)


def _section_bodies(text: str) -> dict[str, str]:
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    bodies: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name not in SECTIONS:
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        bodies[name] = masked[body_start + 1 if body_start != -1 else match.end():body_end]
    return bodies


def _summary_content(text: str) -> str:
    masked = _mask_fences(text).split("\n## Slice Log", 1)[0]
    line = _SUMMARY_LINE.search(masked)
    if line:
        return line.group(1).strip()
    heading = _SUMMARY_HEADING.search(masked)
    if heading is None:
        return ""
    level = len(heading.group(1))
    stop = re.search(rf"^#{{1,{level}}}[ \t]+", masked[heading.end():], re.MULTILINE)
    body_end = heading.end() + stop.start() if stop else len(masked)
    return masked[heading.end():body_end].strip()


def _has_summary_content(text: str) -> bool:
    body = text.strip()
    if not body or _N_A.match(body):
        return False
    return any(
        line.strip() and not re.match(r"#{1,6}[ \t]+", line.lstrip())
        for line in body.splitlines()
    )


def discussion_readiness(text: str) -> dict[str, Any]:
    bodies = _section_bodies(text)
    combined = "\n".join(bodies.get(section, "") for section in SECTIONS)
    triggers = [name for name, pattern in TRIGGERS if pattern.search(combined)]
    required = bool(triggers)
    summary = _summary_content(text)
    present = _has_summary_content(summary)
    resolved = (not required) or (present and bool(_RESOLVED.match(summary)))
    return {
        "discussion_required": required,
        "discussion_ready": resolved,
        "discussion_resolved": resolved,
        "discussion_summary_present": present,
        "discussion_triggers": triggers,
    }
