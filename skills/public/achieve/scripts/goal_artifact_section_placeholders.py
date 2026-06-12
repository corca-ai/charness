"""Final-status placeholder floor for achieve goal artifacts."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_markdown():
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_markdown",
        Path(__file__).resolve().parent / "goal_artifact_markdown.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_markdown.py not found beside goal_artifact_section_placeholders.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mask_fences = _load_markdown().mask_fences

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_LEADING_MARKDOWN = re.compile(r"^(?:[ \t>*_`-]+|\d+[.)][ \t]+)+")
_PLACEHOLDER_START = re.compile(
    r"^(?:"
    r"pending(?:\s+until|\s*:)"
    r"|todo\b"
    r"|tbd\b"
    r"|fixme\b"
    r"|to\s+be\s+(?:filled|recorded|completed)\b"
    r")",
    re.IGNORECASE,
)
_LABELED_PLACEHOLDER = re.compile(
    r"^[^:\n]{1,80}:\s*(?P<marker>TODO|TBD|FIXME|<[^>\n]+>)\b",
    re.IGNORECASE,
)


def _clean_line(line: str) -> str:
    cleaned = line.strip()
    while True:
        stripped = _LEADING_MARKDOWN.sub("", cleaned).strip()
        if stripped == cleaned:
            return stripped
        cleaned = stripped


def _first_body_line(masked: str, text: str, start: int, end: int) -> tuple[int, str] | None:
    body = masked[start:end]
    offset = start
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        line_start = offset
        offset += len(line)
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        line_no = text.count("\n", 0, line_start) + 1
        return line_no, text.splitlines()[line_no - 1].strip()
    return None


def final_status_placeholders(text: str) -> list[dict[str, Any]]:
    """Return H2 sections whose first body line is still a closeout placeholder."""
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    findings: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        body_start = masked.find("\n", heading.end())
        if body_start == -1:
            continue
        body_start += 1
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        first = _first_body_line(masked, text, body_start, body_end)
        if first is None:
            continue
        line_no, raw_line = first
        cleaned = _clean_line(raw_line)
        match = _PLACEHOLDER_START.match(cleaned)
        labeled = _LABELED_PLACEHOLDER.match(cleaned)
        if match is None and labeled is None:
            continue
        marker = match.group(0) if match else labeled.group("marker")
        findings.append(
            {
                "section": heading.group(1).strip(),
                "line": line_no,
                "marker": marker,
                "text": raw_line,
            }
        )
    return findings


def apply_final_status_placeholder_floor(report: dict[str, Any], text: str) -> None:
    findings = final_status_placeholders(text)
    report["section_placeholders"] = findings
    if findings:
        report["ok"] = False
