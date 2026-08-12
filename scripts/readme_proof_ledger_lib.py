"""Validate the path-binding contract of README proof-ledger Evidence cells."""

from __future__ import annotations

import re
from pathlib import Path

MARKDOWN_LINK = re.compile(r'\[[^\]]+\]\(([^()\s]+)(?:\s+(?:"[^"]*"|\'[^\']*\'|\([^)]*\)))?\)')


class LedgerEvidenceError(ValueError):
    """Raised when a reader-facing proof-ledger row has no usable evidence path."""


def _evidence_targets(cell: str, *, source_path: Path, repo_root: Path) -> list[Path]:
    targets = MARKDOWN_LINK.findall(cell)
    residue = MARKDOWN_LINK.sub("", cell).replace(",", "").strip()
    if not targets or residue:
        raise LedgerEvidenceError(
            "Evidence must contain only one or more relative Markdown references, without free-text residue"
        )
    resolved: list[Path] = []
    for target in targets:
        if "://" in target or "#" in target:
            raise LedgerEvidenceError(f"Evidence reference must be repo-relative, got {target!r}")
        target_path = (source_path.parent / target).resolve()
        try:
            target_path.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise LedgerEvidenceError(f"Evidence reference escapes the repository: {target!r}") from exc
        if not target_path.exists():
            raise LedgerEvidenceError(f"Evidence reference does not exist: {target!r}")
        resolved.append(target_path)
    return resolved


def claim_ledger_rows(text: str) -> list[list[str]]:
    """Return exactly the eight-cell README rows within the Claim Ledger table."""
    rows: list[list[str]] = []
    in_claim_ledger = False
    for line in text.splitlines():
        if line == "## Claim Ledger":
            in_claim_ledger = True
            continue
        if in_claim_ledger and line.startswith("## "):
            break
        if not in_claim_ledger:
            continue
        if not line.startswith("| README-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            raise LedgerEvidenceError(f"Expected eight ledger cells, got {len(cells)}: {line}")
        rows.append(cells)
    if not rows:
        raise LedgerEvidenceError("Expected one or more README ledger rows")
    return rows


def validate_ledger_rows(text: str, *, source_path: Path, repo_root: Path) -> list[tuple[str, list[Path]]]:
    """Return validated README ledger row IDs and their existing evidence targets."""
    validated: list[tuple[str, list[Path]]] = []
    for cells in claim_ledger_rows(text):
        validated.append((cells[0], _evidence_targets(cells[4], source_path=source_path, repo_root=repo_root)))
    return validated
