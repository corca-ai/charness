"""Complete-state floor for the achieve Operator Decision Queue."""
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
        raise ImportError("goal_artifact_floor_grammar.py not found beside goal_artifact_operator_queue.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GRAMMAR = _load_floor_grammar()
parse_created_date = _GRAMMAR.parse_created_date
is_floor_in_scope = _GRAMMAR.is_floor_in_scope
grandfathered_report = _GRAMMAR.grandfathered_report

RULE_DATE = date(2026, 6, 17)
SECTION = "Operator Decision Queue"
# The empty-queue reason floor, as a NAMED number rather than a digit retyped
# into a regex and then into two prose surfaces. The pattern below and every
# sentence that quotes the floor are built from this one value, so moving it
# moves them (`describe_goal_closeout_shape.py` renders from it too).
MIN_EMPTY_QUEUE_REASON = 21
_EMPTY = re.compile(
    rf"^\s*(?:[-*]\s*)?none\s+—\s+\S.{{{MIN_EMPTY_QUEUE_REASON - 1},}}", re.IGNORECASE
)
_ITEM = re.compile(r"^\s*(?:[-*]\s*)?Decision:\s+\S", re.MULTILINE)
_SCAFFOLD = re.compile(
    r"Record decisions, confirmations, credential actions, manual proof steps",
    re.IGNORECASE,
)


def applies(text: str) -> bool:
    return is_floor_in_scope(parse_created_date(text), RULE_DATE)


_section_body = _GRAMMAR.masked_section_body


def check(text: str) -> dict[str, Any]:
    if not applies(text):
        # Not a pass: the floor never ran, and the shared payload says so. It
        # discloses its basis (`evaluated: False`, the observed `created`, and the
        # `rule_date` that excluded it) rather than reporting a bare `ok` that
        # reads like a satisfied floor — the S15 repair. Grandfathering itself
        # stays: the checked-in corpus is majority pre-rule and refusing it would
        # be a mass false refusal.
        return grandfathered_report(text, RULE_DATE, "complete-state queue")
    # Describe-first rejections: every refusal names the target shape to author,
    # not just the violation, so the author fixes once instead of reverse-
    # engineering the parser. The satisfying forms are `none — <reason>` (a
    # substantive empty-queue reason) or at least one `- Decision: <…>` item.
    _TARGET = (
        f"record `none — <reason>` (a substantive reason, >= {MIN_EMPTY_QUEUE_REASON} chars) "
        "when the queue is empty, or at least one `- Decision: <operator-only decision>` item"
    )
    body = _section_body(text, SECTION)
    if body is None:
        return {"applies": True, "ok": False,
                "reason": f"missing `## {SECTION}` section; add it and {_TARGET}"}
    if not body.strip():
        return {"applies": True, "ok": False,
                "reason": f"`## {SECTION}` is blank; {_TARGET}"}
    if _SCAFFOLD.search(body):
        return {"applies": True, "ok": False,
                "reason": ("`## " + SECTION + "` still contains the seeded scaffold prose "
                           "(`Record decisions, confirmations, ...`); replace it before "
                           "`complete` — " + _TARGET)}
    if _EMPTY.search(body) or _ITEM.search(body):
        return {"applies": True, "ok": True, "reason": "queue disposition recorded"}
    return {"applies": True, "ok": False,
            "reason": f"`## {SECTION}` has content but no recognized disposition; {_TARGET}"}


def apply_operator_queue_floor(report: dict[str, Any], text: str) -> None:
    # floor-addition-restraint: keep as a Created-gated complete-state floor, not
    # a global REQUIRED_SECTIONS migration, because queue closeout evidence needs
    # disappearance prevention while historical goal artifacts must stay readable.
    result = check(text)
    report["operator_decision_queue"] = result
    if result["applies"] and not result["ok"]:
        report["ok"] = False
