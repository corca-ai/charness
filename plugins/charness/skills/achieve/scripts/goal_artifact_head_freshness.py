"""Mutable-HEAD freshness checks for achieve goal artifacts."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

_HEAD_DIRECT_SHA_RE = re.compile(
    r"\b(?:(?:current\b.{0,80}?\bHEAD\b)|HEAD)\s*(?:is\b|=|at\b)\s*`?(?P<sha>[0-9a-f]{7,40})`?",
    re.IGNORECASE | re.DOTALL,
)
_HEAD_PAREN_SHA_RE = re.compile(
    r"\bHEAD\s+is\b(?P<body>.{0,160}?)\(`?(?P<sha>[0-9a-f]{7,40})`?(?P<context>[^)]*)\)",
    re.IGNORECASE | re.DOTALL,
)
_HISTORICAL_RE = re.compile(
    r"\b(?:historical|previous|former|superseded|not current|at the time)\b",
    re.IGNORECASE,
)
_PAREN_HISTORICAL_RE = re.compile(
    r"\b(?:before|historical|previous|former|superseded|not current|at the time)\b",
    re.IGNORECASE,
)


def _iter_unfenced_lines(text: str):
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line_number, line


def _iter_unfenced_paragraphs(text: str):
    buffered: list[tuple[int, str]] = []
    for line_number, line in _iter_unfenced_lines(text):
        if line.strip():
            buffered.append((line_number, line))
            continue
        if buffered:
            yield buffered
            buffered = []
    if buffered:
        yield buffered


def current_head(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    return result.stdout.strip().lower() if result.returncode == 0 else None


def _matches_current_head(candidate: str, head_sha: str) -> bool:
    candidate = candidate.lower()
    head_sha = head_sha.lower()
    return candidate == head_sha or head_sha.startswith(candidate)


def _line_for_offset(lines: list[tuple[int, str]], offset: int) -> int:
    consumed = 0
    for line_number, line in lines:
        if offset < consumed + len(line):
            return line_number
        consumed += len(line) + 1
    return lines[-1][0]


def _historical_context(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 40):min(len(text), end + 40)]
    return bool(_HISTORICAL_RE.search(context)) and not re.search(r"\bcurrent\s+HEAD\b", context, re.IGNORECASE)


def check_head_freshness(text: str, *, head_sha: str | None) -> dict[str, Any]:
    if not head_sha:
        return {"ok": True, "skip_reason": "git HEAD unavailable", "findings": []}
    findings: list[dict[str, object]] = []
    for lines in _iter_unfenced_paragraphs(text):
        paragraph = "\n".join(line for _, line in lines)
        stale: list[str] = []
        finding_line: int | None = None
        for match in _HEAD_DIRECT_SHA_RE.finditer(paragraph):
            if _historical_context(paragraph, match.start(), match.end()):
                continue
            token = match.group("sha")
            if not _matches_current_head(token, head_sha):
                stale.append(token)
                finding_line = finding_line or _line_for_offset(lines, match.start("sha"))
        for match in _HEAD_PAREN_SHA_RE.finditer(paragraph):
            if _PAREN_HISTORICAL_RE.search(match.group("context")):
                continue
            token = match.group("sha")
            if not _matches_current_head(token, head_sha):
                stale.append(token)
                finding_line = finding_line or _line_for_offset(lines, match.start("sha"))
        if not stale:
            continue
        findings.append(
            {
                "line": finding_line,
                "stale_shas": stale,
                "text": " ".join(paragraph.split()),
            }
        )
    return {"ok": not findings, "head_sha": head_sha, "findings": findings}
