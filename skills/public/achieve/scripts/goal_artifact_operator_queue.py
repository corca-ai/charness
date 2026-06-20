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
_mask_fences = _GRAMMAR.mask_fences
parse_created_date = _GRAMMAR.parse_created_date
is_floor_in_scope = _GRAMMAR.is_floor_in_scope

RULE_DATE = date(2026, 6, 17)
SECTION = "Operator Decision Queue"
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_EMPTY = re.compile(r"^\s*(?:[-*]\s*)?none\s+—\s+\S.{20,}", re.IGNORECASE)
_ITEM = re.compile(r"^\s*(?:[-*]\s*)?Decision:\s+\S", re.MULTILINE)
_SCAFFOLD = re.compile(
    r"Record decisions, confirmations, credential actions, manual proof steps",
    re.IGNORECASE,
)


def applies(text: str) -> bool:
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
        return text[body_start + 1:body_end].strip()
    return None


def check(text: str) -> dict[str, Any]:
    if not applies(text):
        return {"applies": False, "ok": True, "reason": "pre-rule goal"}
    body = _section_body(text, SECTION)
    if body is None:
        return {"applies": True, "ok": False, "reason": f"missing `## {SECTION}` section"}
    if not body.strip():
        return {"applies": True, "ok": False, "reason": "queue section is blank"}
    if _SCAFFOLD.search(body):
        return {"applies": True, "ok": False, "reason": "queue still contains scaffold instructions"}
    if _EMPTY.search(body) or _ITEM.search(body):
        return {"applies": True, "ok": True, "reason": "queue disposition recorded"}
    return {
        "applies": True,
        "ok": False,
        "reason": "queue needs `none — <reason>` or at least one `Decision:` item",
    }


def apply_operator_queue_floor(report: dict[str, Any], text: str) -> None:
    # floor-addition-restraint: keep as a Created-gated complete-state floor, not
    # a global REQUIRED_SECTIONS migration, because queue closeout evidence needs
    # disappearance prevention while historical goal artifacts must stay readable.
    result = check(text)
    report["operator_decision_queue"] = result
    if result["applies"] and not result["ok"]:
        report["ok"] = False
