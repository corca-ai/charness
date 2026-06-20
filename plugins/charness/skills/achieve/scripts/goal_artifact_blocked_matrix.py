"""Pre-block remaining-boundary-matrix floor for achieve goal artifacts.

`blocked` is a whole-goal status, not a per-lane one. Before a goal flips to
``blocked`` it must classify **every** external/live proof lane it mentions in a
``## Remaining Boundary Matrix`` so one blocked boundary (e.g. GitHub
publication awaiting approval) cannot silently mark the whole goal stuck while a
runnable lane (e.g. a repo-preauthorized ``instance`` apply/restart) remains.

The floor is **presence + no-runnable-contradiction only**: it proves the lanes
were enumerated and that none is self-classified runnable, never that a
classification is *honest* — that is the fresh-eye reviewer's and the human's
call. This is the Operator Decision Queue rule ("stop only when the decision
blocks ALL safe next slices") applied to the goal status flip. The honest escape
from a runnable-but-not-worth-continuing lane is to classify it ``dispositioned``
with a reason, never to mislabel it ``blocked``.
"""
from __future__ import annotations

import importlib.util
import re
from datetime import date
from pathlib import Path
from typing import Any


def _load_floor_grammar():
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_floor_grammar",
        Path(__file__).resolve().parent / "goal_artifact_floor_grammar.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_floor_grammar.py not found beside goal_artifact_blocked_matrix.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GRAMMAR = _load_floor_grammar()
_mask_fences = _GRAMMAR.mask_fences
parse_created_date = _GRAMMAR.parse_created_date
is_floor_in_scope = _GRAMMAR.is_floor_in_scope

RULE_DATE = date(2026, 6, 18)
SECTION = "Remaining Boundary Matrix"

# A lane that can still make progress under repo policy. Marking the *whole* goal
# blocked while one of these remains is the false-handoff bug this floor closes.
# `approved` is runnable because external approval was already granted, so the
# lane can proceed now — blocking the goal would re-strand an approved action.
RUNNABLE_TOKENS = frozenset({"runnable", "preauthorized-runnable", "approved"})
# A lane that genuinely cannot proceed now (so it does not force staying active).
BLOCKING_TOKENS = frozenset({"approval-required", "read-only", "blocked"})
# A lane already settled this run; neither runnable nor blocking.
SETTLED_TOKENS = frozenset({"verified", "dispositioned"})
ALL_TOKENS = RUNNABLE_TOKENS | BLOCKING_TOKENS | SETTLED_TOKENS

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_LANE = re.compile(
    r"^\s*(?:[-*]\s*)?Lane:\s*(?P<name>[^|\n]{2,}?)\s*\|\s*classification:\s*(?P<token>[a-z][a-z-]*)\b",
    re.MULTILINE | re.IGNORECASE,
)


def applies(text: str) -> bool:
    """Gate goals ``Created:`` on/after the rule landing date; fail closed.

    A missing/malformed ``Created:`` line returns ``True`` (the gate applies) so a
    goal cannot dodge the floor by corrupting one line. Clone-safe: it reads
    in-file content, never mtime.
    """
    return is_floor_in_scope(parse_created_date(text), RULE_DATE)


def _section_body(text: str, heading: str) -> str | None:
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    for index, match in enumerate(headings):
        if match.group(1).strip() != heading:
            continue
        body_start = masked.find("\n", match.end())
        if body_start == -1:
            return ""
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        # Parse the fence-masked slice so an illustrative fenced lane line cannot
        # satisfy the floor; real matrices are plain list items.
        return masked[body_start + 1:body_end].strip()
    return None


def _lanes(body: str) -> list[dict[str, str]]:
    return [
        {"name": match.group("name").strip(), "classification": match.group("token").strip().casefold()}
        for match in _LANE.finditer(body)
    ]


def check(text: str) -> dict[str, Any]:
    """Whether a goal may flip to ``blocked`` now.

    Presence (the matrix names ≥1 validly-classified lane) plus
    no-runnable-contradiction (no lane self-classified runnable). Pre-rule goals
    pass through unconditionally.
    """
    if not applies(text):
        return {"applies": False, "ok": True, "reason": "pre-rule goal"}
    body = _section_body(text, SECTION)
    if body is None:
        return {
            "applies": True,
            "ok": False,
            "reason": f"missing `## {SECTION}` section — classify every external/live proof lane before blocking",
        }
    lanes = _lanes(body)
    if not lanes:
        return {
            "applies": True,
            "ok": False,
            "lanes": [],
            "reason": "matrix needs at least one `Lane: <name> | classification: <token>` line",
        }
    invalid = sorted({lane["classification"] for lane in lanes if lane["classification"] not in ALL_TOKENS})
    if invalid:
        return {
            "applies": True,
            "ok": False,
            "lanes": lanes,
            "reason": f"invalid classification token(s): {', '.join(invalid)}; use one of {sorted(ALL_TOKENS)}",
        }
    runnable = [lane for lane in lanes if lane["classification"] in RUNNABLE_TOKENS]
    if runnable:
        names = ", ".join(f"{lane['name']} ({lane['classification']})" for lane in runnable)
        return {
            "applies": True,
            "ok": False,
            "lanes": lanes,
            "runnable_lanes": runnable,
            "reason": (
                f"runnable lane(s) remain: {names} — keep the goal active and continue them "
                "instead of marking the whole goal blocked (classify `dispositioned` with a "
                "reason if a runnable lane is genuinely not worth continuing)"
            ),
        }
    return {"applies": True, "ok": True, "lanes": lanes, "reason": "every lane classified; no runnable lane remains"}


def flip_refusal(text: str, rel: str, current_status: str | None) -> dict[str, Any] | None:
    """Refusal dict when a `blocked` flip lacks a clean remaining-boundary matrix.

    Returns ``None`` when the flip is allowed. ``current_status`` is the goal's
    status before the flip; a goal already ``blocked`` is not re-gated. Kept here
    (not in ``goal_artifact_lib``) so the near-limit lib stays slim and the floor
    logic lives beside the check it wraps.
    """
    # floor-addition-restraint: keep (new blocking floor). Recorded recurrence: a
    # goal falsely marked blocked while a preauthorized lane remained, forcing
    # operator recovery; prose ("record the blocker") already existed and did not
    # prevent it. Goal-conditional floor on the `blocked` flip, not the `complete`
    # path the static describe-first preflight catalogs — a `keep`, not an `absorb`.
    if current_status == "blocked":
        return None
    report = check(text)
    if report["ok"]:
        return None
    return {
        "action": "refused",
        "path": rel,
        "status": current_status or "unknown",
        "requested_status": "blocked",
        "note": (
            "refused to flip to blocked: before marking a goal blocked, classify every "
            "external/live proof lane in a `## Remaining Boundary Matrix` "
            "(`Lane: <name> | classification: <token>`). If any lane is runnable, "
            "preauthorized-runnable, or approved under repo policy, keep the goal active and "
            "continue that lane instead of blocking the whole goal. " + report["reason"]
        ),
        "blocked_matrix_report": report,
    }
