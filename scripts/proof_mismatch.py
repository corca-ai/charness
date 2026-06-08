"""Proof-mismatch closeout detection (#339, the core of the issue).

Generalizes the residual-ledger floor with the adapter's proof semantics. A
closeout that declares a ``## Proof Ledger`` (rows of *acceptance class* ->
*reached proof level* -> *disposition*) is checked against the optional
proof-semantics adapter and BLOCKED when a proof gap is left undispositioned. The
three blocking conditions, pinned by the #339 maintainer evidence-update comment:

  (i)   a declared acceptance class has NO evaluated proof entry (empty Reached);
  (ii)  the reached proof level does NOT satisfy the acceptance class
        (via the adapter's ``level_satisfies``); and
  (iii) the resulting gap lacks an explicit disposition
        (``issue #N`` / ``applied:`` / ``accepted-risk:`` / ``out-of-scope:``).

Portable + domain-blind: Charness never infers a domain acceptance class. The
closeout AUTHOR declares the (class, reached) rows it is claiming; the ADAPTER
declares the proof semantics; Charness only does the generic comparison plus the
presence/form disposition check. Fires only on a present ``## Proof Ledger`` (no
over-fire; no existing artifact carries one, so no date gate is needed). A
missing/empty adapter map degrades — Charness cannot verify satisfaction, so every
declared row is treated as needing a disposition rather than passing silently — and
a found-but-INVALID adapter blocks (fails closed).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.disposition_form import evaluate_residual_disposition_form
from scripts.proof_semantics_adapter_lib import (
    acceptance_map_available,
    level_satisfies,
    load_adapter,
    min_level_for_acceptance,
)

_PROOF_LEDGER_HEADING = re.compile(r"(?im)^(#{2,6})[ \t]+Proof[ \t]+Ledger\b[^\n]*$")
_TABLE_ROW = re.compile(r"^[ \t]*\|(.+)\|[ \t]*$")
_SEPARATOR = re.compile(r"^[ \t]*\|[\s:|-]+\|[ \t]*$")
_PLACEHOLDER = re.compile(r"^(?:TODO|TBD|FIXME)\b|^<[^>\n]*>$", re.IGNORECASE)

# The valid gap dispositions are the residual-ledger forms (placeholder excluded —
# a detected gap must carry a REAL disposition at closeout, not an unfilled cell).
_GAP_DISPOSITION_KINDS = ("applied", "issue", "accepted-risk", "out-of-scope")


def _mask_fences(text: str) -> str:
    """Blank fenced code-block regions (length/newlines preserved), so a fenced
    example ``## Proof Ledger`` table is inert. Self-contained mirror of the
    sibling gates' masker."""
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    return text if in_fence else "".join(masked)


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _proof_ledger_body(text: str) -> str | None:
    """The body of the ``## Proof Ledger`` section (heading excluded), fences
    masked; ``None`` when absent."""
    masked = _mask_fences(text)
    head = _PROOF_LEDGER_HEADING.search(masked)
    if head is None:
        return None
    level = len(head.group(1))
    body_start = masked.find("\n", head.end())
    if body_start == -1:
        return ""
    nxt = re.compile(rf"(?m)^#{{1,{level}}}[ \t]+\S").search(masked, body_start + 1)
    return masked[body_start + 1 : nxt.start() if nxt else len(masked)]


def _column_index(header: list[str], *needles: str) -> int | None:
    for index, name in enumerate(header):
        if any(needle in name.lower() for needle in needles):
            return index
    return None


def _judge_table(table: list[str], rows: list[dict]) -> None:
    """Append parsed (class, reached, disposition) rows from one contiguous table.

    Judged only when the header names an acceptance/class column AND a
    reached/proof column (the disposition column is optional). A leading
    non-proof table in the same section is passed over without masking a following
    proof table.
    """
    data_rows = [line for line in table if not _SEPARATOR.match(line)]
    if not data_rows:
        return
    header = _split_table_row(data_rows[0])
    class_idx = _column_index(header, "acceptance", "class")
    reached_idx = _column_index(header, "reached", "proof")
    if class_idx is None or reached_idx is None:
        return
    disp_idx = _column_index(header, "disposition")
    for line in data_rows[1:]:
        cells = _split_table_row(line)
        if class_idx >= len(cells) or reached_idx >= len(cells):
            continue
        disposition = cells[disp_idx] if disp_idx is not None and disp_idx < len(cells) else ""
        rows.append(
            {
                "acceptance_class": cells[class_idx],
                "reached": cells[reached_idx],
                "disposition": disposition,
                "row": line.strip(),
            }
        )


def parse_proof_ledger(section_text: str) -> list[dict]:
    """Parse every ``## Proof Ledger`` data row into
    ``{"acceptance_class", "reached", "disposition", "row"}``. Tables are grouped
    by contiguity and judged by their own header. Fences masked."""
    masked = _mask_fences(section_text)
    rows: list[dict] = []
    table: list[str] = []
    for line in masked.splitlines():
        if _TABLE_ROW.match(line):
            table.append(line)
            continue
        _judge_table(table, rows)
        table = []
    _judge_table(table, rows)
    return rows


def _empty_or_placeholder(value: str) -> bool:
    return not value.strip() or bool(_PLACEHOLDER.match(value.strip()))


def evaluate_row(row: dict, data: dict[str, Any], map_available: bool) -> dict:
    """Classify one proof-ledger row's gap + disposition (presence/form only).

    ``gap_kind`` is one of ``degraded`` (no domain map), ``unmapped-class`` (class
    not in the adapter map), ``no-proof-entry`` (condition i), or
    ``proof-below-acceptance`` (condition ii); ``None`` when the reached proof
    satisfies the class. A gap row's disposition must be a real residual
    disposition form (placeholder/empty/prose is not a disposition)."""
    acceptance_class, reached = row["acceptance_class"], row["reached"]
    gap_kind: str | None = None
    required: str | None = None
    if not map_available:
        gap_kind = "degraded"
    else:
        required = min_level_for_acceptance(data, acceptance_class)
        if required is None:
            gap_kind = "unmapped-class"
        elif _empty_or_placeholder(reached):
            gap_kind = "no-proof-entry"
        elif level_satisfies(data, reached, required) is not True:
            gap_kind = "proof-below-acceptance"
    result = {**row, "required": required, "gap": gap_kind is not None, "gap_kind": gap_kind}
    if gap_kind is None:
        result["disposition_ok"] = True
        return result
    verdict = evaluate_residual_disposition_form(row["disposition"])
    result["disposition_ok"] = verdict["kind"] in _GAP_DISPOSITION_KINDS
    return result


def proof_mismatch_report(repo_root: Path | str, text: str) -> dict[str, Any]:
    """Full proof-mismatch verdict for a closeout body.

    Returns ``{"problem", "present", "adapter_found", "adapter_valid",
    "map_available", "degraded", "rows", "undispositioned", "reason"?}``. ``problem``
    is ``"invalid-adapter"`` (a found-but-invalid adapter with a ledger present),
    ``"mismatch"`` (≥1 gap row lacks a real disposition), or ``None``.
    """
    adapter = load_adapter(Path(repo_root))
    map_available = acceptance_map_available(adapter)
    body = _proof_ledger_body(text)
    scope = {
        "present": body is not None,
        "adapter_found": adapter["found"],
        "adapter_valid": adapter["valid"],
        "map_available": map_available,
        "degraded": not map_available,
    }
    if body is None:
        return {"problem": None, "rows": [], "undispositioned": [], **scope}
    if adapter["found"] and not adapter["valid"]:
        return {
            "problem": "invalid-adapter",
            "rows": [],
            "undispositioned": [],
            "reason": (
                "a `## Proof Ledger` is present but the proof-semantics adapter is invalid "
                "(fails closed): " + "; ".join(adapter["errors"])
            ),
            **scope,
        }
    rows = [evaluate_row(row, adapter["data"], map_available) for row in parse_proof_ledger(body)]
    undispositioned = [r for r in rows if r["gap"] and not r["disposition_ok"]]
    if undispositioned:
        return {
            "problem": "mismatch",
            "rows": rows,
            "undispositioned": [
                {"acceptance_class": r["acceptance_class"], "reached": r["reached"], "gap_kind": r["gap_kind"]}
                for r in undispositioned
            ],
            "reason": (
                "one or more `## Proof Ledger` rows leave a proof gap (missing proof entry, "
                "reached proof below the acceptance class, or no domain map to verify) without an "
                "explicit disposition; each gap must carry one of "
                "`applied: <change>` / `issue #N` / `accepted-risk: <reason>` / `out-of-scope: <reason>`"
            ),
            **scope,
        }
    return {"problem": None, "rows": rows, "undispositioned": [], **scope}


def apply_proof_mismatch_floor(report: dict[str, Any], repo_root: Path | str, text: str) -> None:
    """Attach the proof-mismatch verdict to a closeout ``report`` (mutates in
    place); sets ``report["ok"] = False`` on a block. Used by achieve and issue
    closeout. Inert when no ``## Proof Ledger`` is present (no over-fire)."""
    verdict = proof_mismatch_report(repo_root, text)
    report["proof_mismatch_scope"] = {
        "present": verdict["present"],
        "adapter_found": verdict["adapter_found"],
        "adapter_valid": verdict["adapter_valid"],
        "map_available": verdict["map_available"],
        "degraded": verdict["degraded"],
    }
    if verdict.get("problem"):
        report["proof_mismatch"] = verdict
        report["ok"] = False
