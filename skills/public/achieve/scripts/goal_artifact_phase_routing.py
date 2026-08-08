"""Presence-only phase-routing closeout floor for achieve goal artifacts."""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

PHASE_ROUTING_FLOOR_RULE_DATE = date(2026, 6, 4)

COORDINATION_SECTION = "Coordination Cues"
CONTEXT_SOURCES_SECTION = "Context Sources"
RECORDED_WORK_SECTIONS = ("Slice Log", "Final Verification")

_IMPL_RECORD = re.compile(r"^[\s>*-]*(?:What\s+changed|Commits)\s*:\s*\S", re.MULTILINE | re.IGNORECASE)
_DEBUG_RECORD = re.compile(r"\b(?:bug-class|debug artifact|hypothesis|root[- ]cause|rca)\b", re.IGNORECASE)
_QUALITY_RECORD = re.compile(
    r"\b(?:quality|gate|validator|pytest|run_slice_closeout|validate_skills|check_goal_artifact|check_doc_links)\b",
    re.IGNORECASE,
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import SATISFYING_CUE_KINDS as _SATISFYING  # noqa: E402
from goal_artifact_floor_grammar import classify_cue_line as _classify_cue_line  # noqa: E402
from goal_artifact_floor_grammar import cue_pattern as _cue_pattern  # noqa: E402
from goal_artifact_floor_grammar import (  # noqa: E402
    is_floor_in_scope,
    issue_closeout_triggered,
)
from goal_artifact_floor_grammar import joined_section_body as _joined_section_body  # noqa: E402
from goal_artifact_floor_grammar import parse_created_date as goal_created_date  # noqa: E402
from goal_artifact_floor_grammar import section_body as _section_body  # noqa: E402
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402

# Markup-tolerant per the shared cue grammar: a backticked or bolded `Routing:`
# line is the same cue as a bare one.
_ROUTING_REF = _cue_pattern("Routing")


def phase_routing_floor_applies(text: str) -> bool:
    return is_floor_in_scope(goal_created_date(text), PHASE_ROUTING_FLOOR_RULE_DATE)


def phase_route_triggers(text: str) -> dict[str, bool]:
    """Return phase skills whose recorded work needs routing evidence."""
    masked = _mask_fences(text)
    work = "\n".join(_section_body(masked, heading) or "" for heading in RECORDED_WORK_SECTIONS)
    return {
        "impl": _IMPL_RECORD.search(work) is not None,
        "debug": _DEBUG_RECORD.search(work) is not None,
        "quality": _QUALITY_RECORD.search(work) is not None,
        "issue": issue_closeout_triggered(text),
    }


def _skill_named(value: str, skill: str) -> bool:
    return re.search(rf"\b{re.escape(skill)}\b", value, re.IGNORECASE) is not None


def _parse_routing_step(section_body: str | None, skill: str) -> tuple[str | None, str | None]:
    if not section_body:
        return None, None
    first: tuple[str | None, str | None] = (None, None)
    for match in _ROUTING_REF.finditer(section_body):
        kind, value = _classify_cue_line(match.group(1))
        if kind is None:
            continue  # empty or still-a-placeholder reference: not a routing line
        if kind == "optout":
            return kind, value
        if kind == "ref" and _skill_named(value, skill):
            return kind, value
        if first[0] is None:
            first = (kind if kind != "ref" else "ref_incomplete", value)
    return first


def apply_phase_routing_floor(report: dict[str, Any], text: str) -> None:
    """Attach the phase-routing floor verdict to ``report``.

    Installed skill metadata/model judgment owns the route decision. This floor only proves
    that recorded implementation/debug/quality/issue work did not remain
    ``achieve``-only at closeout.
    """
    in_scope = phase_routing_floor_applies(text)
    triggers = phase_route_triggers(text) if in_scope else {}
    required_routes = [skill for skill, triggered in triggers.items() if triggered]
    # Joined section body so a `Routing:` value whose routed skill name wrapped
    # onto a continuation physical line is matched, not false-rejected.
    section = _joined_section_body(text, COORDINATION_SECTION)
    route_evidence: dict[str, str | None] = {}
    missing_routes: list[str] = []
    for skill in required_routes:
        kind, _ = _parse_routing_step(section, skill)
        route_evidence[skill] = kind
        if kind not in _SATISFYING:
            missing_routes.append(skill)
    report["phase_routing_floor"] = {
        "in_scope": in_scope,
        "rule_date": PHASE_ROUTING_FLOOR_RULE_DATE.isoformat(),
        "triggered": bool(required_routes),
        "required": required_routes,
        "satisfied": not missing_routes,
        "evidence": route_evidence,
    }
    if missing_routes:
        reason = (
        "this goal's recorded work crossed phase boundaries ("
            + ", ".join(missing_routes)
            + ") but `## Coordination Cues` records no `Routing:` line that names "
            "the routed skill, and no `Routing: n/a — <reason>` opt-out (>=30 chars); "
            "choose the phase route from installed skill metadata/model judgment and record it "
            "before flipping to complete"
        )
        report["phase_routing_floor"]["reason"] = reason
        missing = report.setdefault("coordination_missing", [])
        missing.append({"floor": "phase_routing", "reason": reason})
        report["ok"] = False
