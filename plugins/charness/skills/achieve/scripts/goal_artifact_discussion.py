"""Before-phase operator discussion readiness for achieve goals."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

DISCUSSION_LABEL = "Discuss before activation"

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_SUMMARY_HEADING = re.compile(r"^(#{2,4})[ \t]+Discuss before activation\b.*$", re.IGNORECASE | re.MULTILINE)
_SUMMARY_LINE = re.compile(r"^[ \t]*(?:[-*][ \t]*)?Discuss before activation:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
_N_A = re.compile(r"^(?:n/?a|none|no consequential|not applicable)\b", re.IGNORECASE)
_RESOLVED = re.compile(r"^(?:resolved|confirmed|approved)\b", re.IGNORECASE)

# Consumer-axis deploy / irreversible-side-effect verbs. The portable DEFAULT is the
# English set; a consumer's achieve adapter (`discussion_deploy_vocab`) replaces it so
# charness does not hardcode one consumer's boundary vocabulary. Option A
# (behavior-preserving): no adapter -> byte-identical triggers; dropping the default
# would lose the guard for an unconfigured consumer.
_DEFAULT_DEPLOY_VOCAB: tuple[str, ...] = ("apply/restart", "restart", "deploy")
# charness-neutral concept alternants (raw regex) that always apply, independent of the
# consumer's deploy vocabulary.
_PRODUCTION_CONCEPTS = ("prod(?:uction)?", "live proof", "real github lookup")
_IRREVERSIBLE_CONCEPTS = ("irreversible", "external side effect", "production contact")


def _deploy_trigger(name: str, concepts: tuple[str, ...], vocab: tuple[str, ...]) -> tuple[str, re.Pattern[str]]:
    alternants = list(concepts) + [re.escape(token) for token in vocab]
    return (name, re.compile(r"\b(" + "|".join(alternants) + r")\b", re.IGNORECASE))


def build_triggers(deploy_vocab: tuple[str, ...] | list[str] | None = None) -> tuple[tuple[str, re.Pattern[str]], ...]:
    """Build the pre-activation discussion triggers. ``deploy_vocab`` (an adapter's
    ``discussion_deploy_vocab``) replaces the English default for the two deploy /
    irreversible-side-effect triggers; the neutral concepts and the other three
    triggers are invariant. ``None``/empty -> the byte-preserving English default."""
    vocab = tuple(deploy_vocab) if deploy_vocab else _DEFAULT_DEPLOY_VOCAB
    return (
        _deploy_trigger("production_or_live_proof", _PRODUCTION_CONCEPTS, vocab),
        ("issue_close_or_split", re.compile(r"\b(close[sd]?|closing|split|leave open|defer(?:red)?)\b.{0,60}#\d+|#\d+.{0,60}\b(close[sd]?|closing|split|leave open|defer(?:red)?)\b", re.IGNORECASE)),
        ("broad_bundle_scope", re.compile(r"\b(bundle[sd]?|broad(?:ly)? bundled|selected bundle|combined|together|all (?:\d+|\w+) proposed)\b|#\d+.{0,60}#\d+", re.IGNORECASE)),
        ("proof_nonclaim_or_downgrade", re.compile(r"\b(proof|verification|live|external).{0,40}\b(non-claim|not run|skipped|fixture-only|downgrad(?:e|ed)|without live|no live)\b|\b(non-claim|fixture-only|without live|no live)\b", re.IGNORECASE)),
        _deploy_trigger("irreversible_side_effect", _IRREVERSIBLE_CONCEPTS, vocab),
    )


# Module-level default triggers (back-compat for importers); adapter-overridden per call.
TRIGGERS: tuple[tuple[str, re.Pattern[str]], ...] = build_triggers()

SECTIONS = (
    "Non-Goals",
    "Boundaries",
    "Agent Verification Plan",
    "Interview Decisions",
    "Plan Critique Findings",
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402


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


def discussion_readiness(text: str, *, deploy_vocab: tuple[str, ...] | list[str] | None = None) -> dict[str, Any]:
    bodies = _section_bodies(text)
    combined = "\n".join(bodies.get(section, "") for section in SECTIONS)
    active = build_triggers(deploy_vocab) if deploy_vocab else TRIGGERS
    triggers = [name for name, pattern in active if pattern.search(combined)]
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
