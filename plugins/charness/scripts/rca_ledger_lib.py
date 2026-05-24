#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

try:  # reuse the portable-path helper rather than reinventing it
    from scripts.slice_closeout_usage_episode import _portable_path
except ImportError:  # standalone invocation (scripts/ on sys.path[0])
    from slice_closeout_usage_episode import _portable_path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = Path(__file__).resolve().parent / "rca_event.schema.json"
LEDGER_PATH = Path("charness-artifacts/metrics/rca-ledger.jsonl")

# Slice 2 wired auto-append into the debug/issue/retro closeout prompts via
# skills/shared/references/rca-ledger-append.md, so the banner reads ON. The
# baseline figure stays n/a until live (non-seed) events accrue; the
# seed-excluded rate keys off non-seed event presence, not off this flag.
AUTO_APPEND_WIRED = True
AUTO_APPEND_OFF_BANNER = "auto_append: OFF (slice 2 not wired)"
AUTO_APPEND_ON_BANNER = "auto_append: ON (prompt-enforced; denominator self-reported, not gate-verified)"
NA = "n/a"

portable_path = _portable_path


def now_ts() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def resolve_ledger_path(repo_root: Path, ledger: Path | None) -> Path:
    if ledger is not None:
        return ledger if ledger.is_absolute() else (repo_root / ledger)
    return repo_root / LEDGER_PATH


def validate_record(record: object, schema: dict[str, object]) -> None:
    """Raise jsonschema.ValidationError when record is not a schema-valid event."""
    import jsonschema

    jsonschema.validate(record, schema)


def validate_ledger(ledger_path: Path, schema: dict[str, object]) -> list[dict[str, object]]:
    """Return a list of per-line errors; empty list means every line is valid.

    Blocks only on malformed lines (changed-surface scope). The conversion rate
    is never evaluated here.
    """
    import jsonschema

    errors: list[dict[str, object]] = []
    if not ledger_path.is_file():
        return [{"line": 0, "error": "ledger file not found"}]
    for lineno, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append({"line": lineno, "error": f"invalid JSON: {exc.msg}"})
            continue
        try:
            jsonschema.validate(record, schema)
        except jsonschema.ValidationError as exc:
            errors.append({"line": lineno, "error": exc.message})
    return errors


def read_events(ledger_path: Path) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    if not ledger_path.is_file():
        return events
    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            events.append(json.loads(raw))
    return events


def _rate(converted: int, total: int) -> float | str:
    return converted / total if total else NA


def _breakdown(events: list[dict[str, object]], key: str) -> dict[str, dict[str, object]]:
    buckets: dict[str, dict[str, int]] = {}
    for event in events:
        name = str(event.get(key))
        bucket = buckets.setdefault(name, {"total": 0, "converted": 0})
        bucket["total"] += 1
        if event.get("converted") is True:
            bucket["converted"] += 1
    return {
        name: {
            "total": bucket["total"],
            "converted": bucket["converted"],
            "rate": _rate(bucket["converted"], bucket["total"]),
        }
        for name, bucket in sorted(buckets.items())
    }


def _summary(events: list[dict[str, object]]) -> dict[str, object]:
    total = len(events)
    converted = sum(1 for event in events if event.get("converted") is True)
    return {
        "total": total,
        "converted": converted,
        "rate": _rate(converted, total),
        "by_source": _breakdown(events, "source"),
        "by_event_kind": _breakdown(events, "event_kind"),
    }


def aggregate(events: list[dict[str, object]]) -> dict[str, object]:
    non_seed = [event for event in events if event.get("seed") is not True]
    baseline_available = bool(non_seed)
    return {
        "auto_append_wired": AUTO_APPEND_WIRED,
        "auto_append": AUTO_APPEND_ON_BANNER if AUTO_APPEND_WIRED else AUTO_APPEND_OFF_BANNER,
        "total_events": len(events),
        "baseline_rate_available": baseline_available,
        "seed_included": _summary(events),
        "seed_excluded": _summary(non_seed),
    }


def _format_rate(rate: float | str) -> str:
    if isinstance(rate, str):
        return rate
    return f"{rate * 100:.1f}%"


def _render_breakdown(label: str, breakdown: dict[str, dict[str, object]]) -> list[str]:
    lines = [f"    by {label}:"]
    if not breakdown:
        lines.append("      (none)")
    for name, bucket in breakdown.items():
        rate = _format_rate(bucket["rate"])  # type: ignore[arg-type]
        lines.append(f"      {name}: {bucket['converted']}/{bucket['total']} ({rate})")
    return lines


def render_text(payload: dict[str, object]) -> str:
    lines = [payload["auto_append"]]  # type: ignore[list-item]
    included = payload["seed_included"]  # type: ignore[assignment]
    lines.append("seed-included (sanity only — not the baseline; do not quote):")
    lines.append(
        f"    overall: {included['converted']}/{included['total']} "  # type: ignore[index]
        f"({_format_rate(included['rate'])})"  # type: ignore[index]
    )
    lines.extend(_render_breakdown("source", included["by_source"]))  # type: ignore[index]
    lines.extend(_render_breakdown("event_kind", included["by_event_kind"]))  # type: ignore[index]
    lines.append("seed-excluded (baseline figure):")
    if not payload["baseline_rate_available"]:
        lines.append(
            "    overall: n/a (0 non-seed events yet; auto-append is wired, "
            "baseline figure stays n/a until live closeout events accrue)"
        )
    else:
        excluded = payload["seed_excluded"]  # type: ignore[assignment]
        lines.append(
            f"    overall: {excluded['converted']}/{excluded['total']} "  # type: ignore[index]
            f"({_format_rate(excluded['rate'])})"  # type: ignore[index]
        )
        lines.extend(_render_breakdown("source", excluded["by_source"]))  # type: ignore[index]
        lines.extend(_render_breakdown("event_kind", excluded["by_event_kind"]))  # type: ignore[index]
    return "\n".join(lines)
