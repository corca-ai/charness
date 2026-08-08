"""Presence-only phase-routing closeout floor for achieve goal artifacts."""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

PHASE_ROUTING_FLOOR_RULE_DATE = date(2026, 6, 4)
# From this date a goal DECLARES which phases its work crossed, instead of the
# floor guessing from prose. Dated separately so goals shaped before it keep
# exactly the floor they were authored against.
DECLARED_PHASES_RULE_DATE = date(2026, 8, 9)

COORDINATION_SECTION = "Coordination Cues"
CONTEXT_SOURCES_SECTION = "Context Sources"
RECORDED_WORK_SECTIONS = ("Slice Log", "Final Verification")

# The phases an author declares. `impl` and `issue` are absent on purpose: both
# are already triggered by a STRUCTURAL record (a `What changed:`/`Commits:` line,
# a literal `closes #N`), which is a declaration the author made, not a guess
# about what their prose was about.
DECLARABLE_PHASES = ("debug", "quality")

_IMPL_RECORD = re.compile(r"^[\s>*-]*(?:What\s+changed|Commits)\s*:\s*\S", re.MULTILINE | re.IGNORECASE)
# The two prose guesses that used to live here are DELETED, not tuned:
#
#   _DEBUG_RECORD   \b(?:bug-class|debug artifact|hypothesis|root[- ]cause|rca)\b
#   _QUALITY_RECORD \b(?:quality|gate|validator|pytest|...)\b
#
# They decided what work a goal DID by matching words in its prose, then refused
# `Status: complete` on the guess -- wrong in both directions. Real debug work
# written in plain English ("traced the failure to an off-by-one") did not fire;
# the word `hypothesis` in passing did; an `airport gate` metaphor demanded a
# quality route. Measured over the 185 checked-in goal artifacts, the quality
# guess fired on 157 of them, mostly on the word "gate" -- a trigger that fires
# on 85% of a corpus is not discriminating between goals, it is describing the
# vocabulary of the repo.
#
# What replaces them is not a better guess. The author names the phases in a
# `Phases:` cue, and this floor checks the DECLARATION's form.


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import (  # noqa: E402
    MIN_OPTOUT_REASON,  # noqa: E402
    is_floor_in_scope,
    issue_closeout_triggered,
)
from goal_artifact_floor_grammar import SATISFYING_CUE_KINDS as _SATISFYING  # noqa: E402
from goal_artifact_floor_grammar import classify_cue_line as _classify_cue_line  # noqa: E402
from goal_artifact_floor_grammar import cue_pattern as _cue_pattern  # noqa: E402
from goal_artifact_floor_grammar import joined_section_body as _joined_section_body  # noqa: E402
from goal_artifact_floor_grammar import parse_created_date as goal_created_date  # noqa: E402
from goal_artifact_floor_grammar import section_body as _section_body  # noqa: E402
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402

# Markup-tolerant per the shared cue grammar: a backticked or bolded `Routing:`
# line is the same cue as a bare one.
_ROUTING_REF = _cue_pattern("Routing")


_PHASES_REF = _cue_pattern("Phases")


def phase_routing_floor_applies(text: str) -> bool:
    return is_floor_in_scope(goal_created_date(text), PHASE_ROUTING_FLOOR_RULE_DATE)


def declaration_required(text: str) -> bool:
    """Does this goal owe a `Phases:` declaration at all?

    Only from the declaration rule date, and only once it records work. A goal
    with an empty `## Slice Log` has nothing to declare yet, and asking for the
    line before there is work to describe is ceremony, not a floor.

    Deliberately fails OPEN on an unreadable `Created:` date, unlike the routing
    floor around it, which fails closed. The two are different questions. "Did you
    route the work you recorded?" applies to any goal whatever its header says, so
    an unparseable date must not dodge it. "Do you owe this NEW authoring field?"
    is a dated contract change, and demanding it from an artifact whose date cannot
    be established would refuse a goal for a broken header rather than for an
    unrouted phase -- while its `impl` and `issue` teeth, which need no
    declaration, still apply.
    """
    created = goal_created_date(text)
    if created is None or created < DECLARED_PHASES_RULE_DATE:
        return False
    return recorded_work_present(text)


def _recorded_work_body(text: str) -> str:
    """The archive sections' text, fence-masked. One reader, so the two callers
    below cannot disagree about which sections count as recorded work."""
    masked = _mask_fences(text)
    return "\n".join(_section_body(masked, heading) or "" for heading in RECORDED_WORK_SECTIONS)


def recorded_work_present(text: str) -> bool:
    """Structural: do the archive sections carry any content?

    This asks whether anything is written there, never what it is about.
    """
    for line in _recorded_work_body(text).splitlines():
        stripped = line.strip().lstrip("#>*-").strip()
        if stripped and not stripped.startswith("("):
            return True
    return False


# The declaration is a LIST, read as tokens -- never a prose search for phase
# names. Searching the value is the same defect one layer up: this floor's own
# first draft read "no debug phase was entered" as DECLARING debug, because the
# word was present. Everything after the first separator is the author's reason
# and is not scanned.
_PHASE_LIST_HEAD = re.compile(r"^([^—–]*?)(?:\s+[-–—]\s+|—|–|$)")


def _phase_tokens(value: str) -> list[str]:
    head = _PHASE_LIST_HEAD.match(value.strip())
    listed = (head.group(1) if head else value).strip()
    tokens = {token.strip().strip("`*_.").lower() for token in re.split(r"[,\s/]+", listed) if token.strip()}
    return [phase for phase in DECLARABLE_PHASES if phase in tokens]


def declared_phases(text: str) -> tuple[str | None, list[str], str]:
    """Read the author's `Phases:` cue: ``(kind, phases, value)``.

    ``kind`` is the shared cue grammar's verdict (``ref`` / ``optout`` /
    ``optout_short`` / ``None`` for absent-or-placeholder), so this line is
    classified exactly like every other cue in the artifact.
    """
    section = _joined_section_body(text, COORDINATION_SECTION)
    if not section:
        return None, [], ""
    for match in _PHASES_REF.finditer(section):
        kind, value = _classify_cue_line(match.group(1))
        if kind is None:
            continue
        if kind != "ref":
            return kind, [], value
        return kind, _phase_tokens(value), value
    return None, [], ""


def phase_route_triggers(text: str) -> dict[str, bool]:
    """Return phase skills whose recorded work needs routing evidence.

    `impl` and `issue` come from structural records the author wrote; `debug` and
    `quality` come from the author's own `Phases:` declaration. Nothing here reads
    the prose to decide what the work was about.
    """
    work = _recorded_work_body(text)
    _kind, declared, _value = declared_phases(text)
    triggers = {
        "impl": _IMPL_RECORD.search(work) is not None,
        "issue": issue_closeout_triggered(text),
    }
    for phase in DECLARABLE_PHASES:
        triggers[phase] = phase in declared
    return triggers


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
    # The declaration is FORCED, not offered. Without it, replacing the guess
    # would hand every author a silent bypass: say nothing about debug or quality
    # work and nothing is required. A gate may force a question; this is that
    # question, and `n/a — <reason>` is a legitimate answer to it.
    declaration_kind, _declared, _value = declared_phases(text)
    declaration_owed = in_scope and declaration_required(text)
    declaration_missing = declaration_owed and declaration_kind not in _SATISFYING
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
        "declaration_rule_date": DECLARED_PHASES_RULE_DATE.isoformat(),
        "declaration_owed": declaration_owed,
        "declaration": declaration_kind,
        "triggered": bool(required_routes),
        "required": required_routes,
        "satisfied": not missing_routes and not declaration_missing,
        "evidence": route_evidence,
    }
    if declaration_missing:
        reason = (
            "this goal records work but `## Coordination Cues` carries no `Phases:` line "
            "declaring which phases it crossed. The floor no longer guesses that from your "
            "prose -- it was wrong in both directions -- so name them "
            f"(`Phases: {', '.join(DECLARABLE_PHASES)}`, whichever apply) or opt out with "
            f"`Phases: n/a — <reason>` (>={MIN_OPTOUT_REASON} chars) before flipping to complete"
        )
        report["phase_routing_floor"]["reason"] = reason
        report.setdefault("coordination_missing", []).append(
            {"floor": "phase_routing", "reason": reason}
        )
        report["ok"] = False
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
