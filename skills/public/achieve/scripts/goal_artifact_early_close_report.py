"""Early-close report evidence floor for achieve goal artifacts."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

EARLY_CLOSE_REPORT_EVIDENCE = "early_close_report"

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_REPORT_LABEL = re.compile(r"early[- ]close[- ]report", re.IGNORECASE)
_EARLY_CLOSE_REASON = re.compile(
    r"^[ \t>]*(?:[-*][ \t]+)?(?:No safe next slice|Early close rationale|Stop condition\s*:\s*(?:no_safe_next_slice|blocked|user_stop)\b\s*[:\-])\s*\S",
    re.MULTILINE | re.IGNORECASE,
)
_REPORT_SECTIONS = {
    "why_early_closeout": re.compile(r"\bwhy\b.*\b(early|ended|closeout|close)\b", re.IGNORECASE),
    "user_decisions_needed": re.compile(
        r"\b(user|human)\b.*\b(decisions?|needed|requires?)\b", re.IGNORECASE
    ),
    "waste_retro": re.compile(r"\b(waste|retro|retrospective)\b", re.IGNORECASE),
}
_MIN_SECTION_CHARS = 20


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


def _section_body(masked: str, heading: str) -> str | None:
    headings = list(_H2.finditer(masked))
    for index, match in enumerate(headings):
        if match.group(1).strip().lower() != heading.lower():
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        return masked[body_start + 1 if body_start != -1 else match.end() : body_end]
    return None


def is_report_label(label: str) -> bool:
    return _REPORT_LABEL.fullmatch(label.strip()) is not None


def report_required(text: str) -> bool:
    body = _section_body(_mask_fences(text), "Final Verification") or ""
    return _EARLY_CLOSE_REASON.search(body) is not None


def reject_skip(report: dict[str, Any]) -> None:
    for entry in report.get("skipped", []):
        if entry.get("name") != EARLY_CLOSE_REPORT_EVIDENCE:
            continue
        report.setdefault("invalid_skips", []).append(
            {
                "name": EARLY_CLOSE_REPORT_EVIDENCE,
                "reason": "early-close reports cannot be skipped",
            }
        )
        report["ok"] = False


def validate_report_shape(path: Path) -> list[dict[str, str]]:
    try:
        masked = _mask_fences(path.read_text(encoding="utf-8", errors="ignore"))
    except OSError as exc:
        return [{"section": "<file>", "reason": f"could not read report: {exc}"}]
    headings = list(_H2.finditer(masked))
    failures: list[dict[str, str]] = []
    for section, pattern in _REPORT_SECTIONS.items():
        body = _matching_section_body(masked, headings, pattern)
        if body is None:
            failures.append({"section": section, "reason": "required section heading missing"})
            continue
        if len(re.sub(r"\s+", "", body)) < _MIN_SECTION_CHARS:
            failures.append({"section": section, "reason": "required section body is hollow"})
    return failures


def _matching_section_body(
    masked: str, headings: list[re.Match[str]], pattern: re.Pattern[str]
) -> str | None:
    for index, match in enumerate(headings):
        if not pattern.search(match.group(1).strip()):
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        return masked[body_start + 1 if body_start != -1 else match.end() : body_end]
    return None


def apply_report_shape(report: dict[str, Any]) -> None:
    invalid_reports: list[dict[str, Any]] = []
    for entry in report.get("satisfied", []):
        if entry.get("name") != EARLY_CLOSE_REPORT_EVIDENCE:
            continue
        failures = validate_report_shape(Path(entry["path"]))
        if failures:
            invalid_reports.append({"path": entry["path"], "failures": failures})
    report["invalid_early_close_reports"] = invalid_reports
    if invalid_reports:
        report["ok"] = False
