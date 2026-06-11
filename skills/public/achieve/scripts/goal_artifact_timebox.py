"""Timebox closeout checks for achieve goal artifacts."""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TIMEBOX = re.compile(r"^(?:[-*]\s*)?Timebox:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
_ACTIVATION_TIME = re.compile(
    r"^(?:[-*]\s*)?(?:Activation time|Activated at|Started at):\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_RESERVE = re.compile(r"^(?:[-*]\s*)?Closeout reserve:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
_DONE_EARLY = re.compile(r"^(?:[-*]\s*)?Done-early policy:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
_DURATION_TOKEN = re.compile(r"(\d+)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)", re.IGNORECASE)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_EARLY_EVIDENCE = (
    ("no_safe_next_slice", re.compile(r"^(?:[-*]\s*)?No safe next slice:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)),
    ("early_close_rationale", re.compile(r"^(?:[-*]\s*)?Early close rationale:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)),
    (
        "stop_condition",
        re.compile(
            r"^(?:[-*]\s*)?Stop condition:\s*(?:no_safe_next_slice|blocked|user_stop)\b\s*[:\-]\s*(.+?)\s*$",
            re.MULTILINE | re.IGNORECASE,
        ),
    ),
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _parse_duration(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = value.strip()
    total = 0
    position = 0
    seen_units: set[str] = set()
    for match in _DURATION_TOKEN.finditer(cleaned):
        if cleaned[position:match.start()].strip():
            return None
        amount, unit = match.groups()
        family = "h" if unit.lower().startswith("h") else "m"
        if family in seen_units:
            return None
        seen_units.add(family)
        minutes = int(amount)
        total += minutes * 60 if family == "h" else minutes
        position = match.end()
    if cleaned[position:].strip() or total <= 0:
        return None
    return total


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _evidence(text: str) -> str | None:
    for name, pattern in _EARLY_EVIDENCE:
        value = _first(pattern, text)
        if value and len(value) >= 30 and "<" not in value and ">" not in value:
            return name
    return None


def _section(text: str, heading: str) -> str:
    headings = list(_H2.finditer(text))
    for index, match in enumerate(headings):
        if match.group(1).strip() != heading:
            continue
        body_start = text.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        return text[body_start + 1 if body_start != -1 else match.end():body_end]
    return ""


def _iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def check_timebox_closeout(text: str, *, now: datetime | None = None) -> dict[str, Any]:
    """Return whether a timeboxed goal may close now.

    Non-timeboxed artifacts pass through. Timeboxed artifacts with
    ``Done-early policy: continue_next_improvement`` cannot close before the
    closeout reserve window unless the artifact records a falsifiable reason.
    """
    masked = _mask_fences(text)
    timebox_value = _first(_TIMEBOX, masked)
    reserve_value = _first(_RESERVE, masked) or "20m"
    policy = _first(_DONE_EARLY, masked)
    report: dict[str, Any] = {
        "applies": bool(timebox_value),
        "ok": True,
        "status": "not_timeboxed",
        "timebox_minutes": None,
        "reserve_minutes": None,
        "activation_time": None,
        "deadline": None,
        "closeout_window_started": None,
        "remaining_minutes": None,
        "evidence": None,
        "issues": [],
    }
    if not timebox_value:
        return report

    report["status"] = "ready"
    duration = _parse_duration(timebox_value)
    reserve = _parse_duration(reserve_value)
    activation = _parse_time(_first(_ACTIVATION_TIME, masked))
    report["timebox_minutes"] = duration
    report["reserve_minutes"] = reserve
    report["activation_time"] = _iso(activation)
    if duration is None:
        report["issues"].append("invalid `Timebox:` duration")
    if reserve is None:
        report["issues"].append("invalid `Closeout reserve:` duration")
    if activation is None:
        report["issues"].append("missing or invalid `Activation time:`")
    if not policy:
        report["issues"].append("missing `Done-early policy:`")
    if duration is not None and reserve is not None and reserve >= duration:
        report["issues"].append("`Closeout reserve:` must be shorter than `Timebox:`")
    if report["issues"]:
        report["ok"] = False
        report["status"] = "invalid"
        return report
    if "continue_next_improvement" not in policy.lower():
        report["status"] = "non_continuing_policy"
        return report

    assert activation is not None and duration is not None and reserve is not None
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    deadline = activation.timestamp() + duration * 60
    closeout_start = datetime.fromtimestamp(deadline - reserve * 60, tz=timezone.utc)
    deadline_dt = datetime.fromtimestamp(deadline, tz=timezone.utc)
    report["deadline"] = _iso(deadline_dt)
    report["closeout_window_started"] = _iso(closeout_start)
    report["remaining_minutes"] = round((deadline_dt - now_utc).total_seconds() / 60, 2)
    if now_utc < activation:
        report["ok"] = False
        report["status"] = "invalid"
        report["issues"].append("activation time is in the future")
        return report
    if now_utc >= closeout_start:
        return report
    evidence = _evidence(_section(masked, "Final Verification"))
    report["evidence"] = evidence
    if evidence:
        report["status"] = "early_close_with_evidence"
        return report
    report["ok"] = False
    report["status"] = "early_close_blocked"
    report["issues"].append(
        "timebox closeout window has not started; continue a safe next slice or record `No safe next slice:` / `Early close rationale:`"
    )
    return report
