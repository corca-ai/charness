#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SECTION_HEADER_PATTERN = re.compile(r"^##\s+source\s+surfaces\s*$", re.IGNORECASE)
COLLECTED_PATTERN = re.compile(r"\bcollected\b", re.IGNORECASE)
UNAVAILABLE_PATTERN = re.compile(r"\bunavailable\b", re.IGNORECASE)


def _entry_identifier(entry: dict[str, Any]) -> str:
    kind = entry["kind"]
    for field in ("path", "summary", "query"):
        if entry.get(field):
            return f"{kind}:{entry[field]}"
    return kind


def _entry_match_tokens(entry: dict[str, Any]) -> list[str]:
    tokens = [entry["kind"]]
    for field in ("path", "summary", "query"):
        value = entry.get(field)
        if value:
            tokens.append(str(value))
    return tokens


def _section_lines(text: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if SECTION_HEADER_PATTERN.match(line.strip()):
            captured: list[str] = []
            for follow in lines[index + 1:]:
                stripped = follow.lstrip()
                if stripped.startswith("# ") or stripped.startswith("## "):
                    break
                captured.append(follow)
            return captured
    return None


def _classify_line(line: str, tokens: list[str]) -> str | None:
    line_lower = line.lower()
    if not all(token.lower() in line_lower for token in tokens):
        return None
    if COLLECTED_PATTERN.search(line):
        return "collected"
    if UNAVAILABLE_PATTERN.search(line):
        return "unavailable"
    return None


def _surface_record(entry: dict[str, Any], status: str, evidence: str | None) -> dict[str, Any]:
    return {
        "id": _entry_identifier(entry),
        "kind": entry["kind"],
        "status": status,
        "evidence": evidence,
    }


def preflight_sources(adapter_data: dict[str, Any], draft_path: Path) -> dict[str, Any]:
    sources = adapter_data.get("in_progress_sources") or []
    base: dict[str, Any] = {}
    base["draft_path"] = str(draft_path)
    base["draft_exists"] = draft_path.exists()
    base["section_present"] = False
    if not sources:
        return {**base, "ok": True, "delivery_blocked": False, "surfaces": []}
    if not base["draft_exists"]:
        surfaces = [_surface_record(entry, "unverified", None) for entry in sources]
        return {**base, "ok": False, "delivery_blocked": True, "surfaces": surfaces}
    text = draft_path.read_text(encoding="utf-8")
    section_lines = _section_lines(text)
    if section_lines is None:
        surfaces = [_surface_record(entry, "unverified", None) for entry in sources]
        return {**base, "ok": False, "delivery_blocked": True, "surfaces": surfaces}
    base["section_present"] = True
    surfaces: list[dict[str, Any]] = []
    for entry in sources:
        tokens = _entry_match_tokens(entry)
        status = "unverified"
        evidence: str | None = None
        for raw_line in section_lines:
            classified = _classify_line(raw_line, tokens)
            if classified:
                status = classified
                evidence = raw_line.strip()
                break
        surfaces.append(_surface_record(entry, status, evidence))
    blocked = any(item["status"] == "unverified" for item in surfaces)
    return {**base, "ok": not blocked, "delivery_blocked": blocked, "surfaces": surfaces}
