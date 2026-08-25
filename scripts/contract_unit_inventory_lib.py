"""Discover canonical H2 units from the always-loaded contract sources."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

UNIT_PATHS = (
    "AGENTS.md",
    "docs/implementation-discipline.md",
    "docs/operating-contract.md",
)


def _fail(message: str) -> None:
    raise ValueError(f"contract register invalid: {message}")


def heading_slug(heading: str) -> str:
    value = unicodedata.normalize("NFKC", heading).strip().lower()
    value = re.sub(r"[\W_]+", "-", value, flags=re.UNICODE).strip("-")
    if not value:
        _fail("contract heading normalizes to an empty slug")
    return value


def unit_id(path: str, heading: str) -> str:
    return f"{path}#{heading_slug(heading)}"


def _unfenced_h2s(path: Path) -> list[str]:
    fence_character: str | None = None
    fence_length = 0
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if fence_character is not None:
            if re.match(
                rf"^[ ]{{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*$", line
            ):
                fence_character = None
                fence_length = 0
            continue
        fence_match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", line)
        if fence_match:
            fence_character = fence_match.group(1)[0]
            fence_length = len(fence_match.group(1))
            continue
        match = re.match(r"^[ ]{0,3}##[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$", line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def build_contract_units(repo_root: Path) -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    seen: set[str] = set()
    for relative in UNIT_PATHS:
        path = repo_root / relative
        if not path.is_file():
            _fail(f"missing contract source `{relative}`")
        for heading in _unfenced_h2s(path):
            identifier = unit_id(relative, heading)
            if identifier in seen:
                _fail(f"contract path `{relative}` has colliding H2 identity `{identifier}`")
            seen.add(identifier)
            units.append({"unit_id": identifier, "path": relative, "heading": heading})
    return sorted(units, key=lambda item: item["unit_id"])
