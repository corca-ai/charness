#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:  # reuse the portable-path helper rather than reinventing it
    from scripts.slice_closeout_usage_episode import _portable_path
except ImportError:  # standalone invocation (scripts/ on sys.path[0])
    from slice_closeout_usage_episode import _portable_path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = Path(__file__).resolve().parent / "rca_event.schema.json"
LEDGER_PATH = Path("charness-artifacts/metrics/rca-ledger.jsonl")
IDEMPOTENCY_FIELDS = ("source", "event_kind", "class_key")

# Slice 2 wired auto-append into the debug/issue/retro closeout prompts via
# skills/shared/references/rca-ledger-append.md, so the banner reads ON. The
# baseline figure stays n/a until live (non-seed) events accrue; the
# seed-excluded rate keys off non-seed event presence, not off this flag.
AUTO_APPEND_WIRED = True
AUTO_APPEND_OFF_BANNER = "auto_append: OFF (slice 2 not wired)"
AUTO_APPEND_ON_BANNER = "auto_append: ON (prompt-enforced; denominator self-reported, not gate-verified)"
NA = "n/a"

# #184 numeric target (set 2026-06-13 at the baseline review, from the matured
# 2026-05-24..06-11 seed-excluded window): a floor on the rolling seed-excluded
# rate plus the zero-falsified-conversion tripwire. The window anchors on the
# latest non-seed event ts so the verdict is reproducible from the ledger alone.
TARGET_FLOOR = 0.70
TARGET_WINDOW_DAYS = 28
TARGET_MIN_EVENTS = 10

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

    jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
    if isinstance(record, dict):
        _validate_timestamp_calendar(record.get("ts"))


def _validate_timestamp_calendar(value: object) -> None:
    if not isinstance(value, str):
        return
    import jsonschema

    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise jsonschema.ValidationError(f"{value!r} is not a valid RFC3339 date-time") from exc


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
            jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
            _validate_timestamp_calendar(record.get("ts") if isinstance(record, dict) else None)
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


def event_identity(record: dict[str, object]) -> tuple[str, str, str] | None:
    values = tuple(record.get(field) for field in IDEMPOTENCY_FIELDS)
    if all(isinstance(value, str) for value in values):
        return values  # type: ignore[return-value]
    return None


def has_existing_event_identity(
    events: list[dict[str, object]], record: dict[str, object]
) -> bool:
    identity = event_identity(record)
    if identity is None:
        return False
    return any(event_identity(event) == identity for event in events)


def ledger_contains_event_identity(ledger_path: Path, record: dict[str, object]) -> bool:
    identity = event_identity(record)
    if identity is None or not ledger_path.is_file():
        return False
    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event_identity(event) == identity:
            return True
    return False


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


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return None


def falsified_conversions(events: list[dict[str, object]]) -> list[dict[str, object]]:
    """List exact class_key recurrences after a converted=true event.

    A recurrence after conversion means the recorded durable artifact did not
    prevent the class — the #184 tripwire. Seed events participate: a converted
    seed whose class recurs live is still a falsified conversion. Recurrences of
    never-converted classes are not listed; they are ordinary unconverted events.
    """
    ordered = sorted(
        (event for event in events if isinstance(event.get("class_key"), str)),
        key=lambda event: str(event.get("ts", "")),
    )
    first_converted: dict[str, str] = {}
    found: list[dict[str, object]] = []
    for event in ordered:
        key = str(event["class_key"])
        if key in first_converted:
            found.append(
                {
                    "class_key": key,
                    "converted_ts": first_converted[key],
                    "recurrence_ts": str(event.get("ts", "")),
                    "recurrence_ref": event.get("ref"),
                }
            )
        elif event.get("converted") is True:
            first_converted[key] = str(event.get("ts", ""))
    return found


def evaluate_target(events: list[dict[str, object]]) -> dict[str, object]:
    """Judge the #184 numeric target: rolling floor + zero-falsified tripwire."""
    non_seed = [event for event in events if event.get("seed") is not True]
    falsified = falsified_conversions(events)
    payload: dict[str, object] = {
        "floor": TARGET_FLOOR,
        "window_days": TARGET_WINDOW_DAYS,
        "min_events": TARGET_MIN_EVENTS,
        "falsified_conversions": falsified,
    }
    stamps = [ts for event in non_seed if (ts := _parse_ts(event.get("ts"))) is not None]
    if not stamps:
        payload["window"] = None
        payload["status"] = "no-live-events"
        payload["reasons"] = ["no live (non-seed) events yet; the target is judged on live data only"]
        return payload
    window_end = max(stamps)
    cutoff = window_end - timedelta(days=TARGET_WINDOW_DAYS)
    in_window = [
        event for event in non_seed if (ts := _parse_ts(event.get("ts"))) is not None and ts >= cutoff
    ]
    total = len(in_window)
    converted = sum(1 for event in in_window if event.get("converted") is True)
    rate = _rate(converted, total)
    tripped = [
        entry
        for entry in falsified
        if (ts := _parse_ts(entry["recurrence_ts"])) is not None and ts >= cutoff
    ]
    payload["window"] = {
        "end": window_end.isoformat().replace("+00:00", "Z"),
        "total": total,
        "converted": converted,
        "rate": rate,
        "falsified_in_window": len(tripped),
    }
    reasons: list[str] = []
    if total < TARGET_MIN_EVENTS:
        payload["status"] = "insufficient-n"
        reasons.append(
            f"window holds {total} live events; the floor is judged only at n>={TARGET_MIN_EVENTS}"
        )
    else:
        if isinstance(rate, float) and rate < TARGET_FLOOR:
            reasons.append("rate below floor")
        if tripped:
            reasons.append("falsified conversion in window (tripwire)")
        payload["status"] = "met" if not reasons else "not-met"
    payload["reasons"] = reasons
    return payload


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
        "target": evaluate_target(events),
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
    lines.extend(_render_target(payload["target"]))  # type: ignore[arg-type]
    return "\n".join(lines)


def _render_target(target: dict[str, object]) -> list[str]:
    floor = f"{TARGET_FLOOR * 100:.0f}%"
    lines = [
        f"target (#184, set 2026-06-13): >={floor} rolling {TARGET_WINDOW_DAYS}d seed-excluded"
        f" (judged at n>={TARGET_MIN_EVENTS}) + zero falsified conversions",
    ]
    window = target["window"]
    if isinstance(window, dict):
        lines.append(
            f"    window ending {window['end']}: {window['converted']}/{window['total']} "
            f"({_format_rate(window['rate'])})"  # type: ignore[arg-type]
        )
    falsified = target["falsified_conversions"]
    assert isinstance(falsified, list)
    lines.append(f"    falsified conversions (all-time, tripwire input): {len(falsified)}")
    for entry in falsified:
        lines.append(
            f"      {entry['class_key']}: converted {entry['converted_ts'][:10]}, "
            f"recurred {entry['recurrence_ts'][:10]}"
        )
    status = target["status"]
    reasons = target["reasons"]
    assert isinstance(reasons, list)
    suffix = f" — {'; '.join(reasons)}" if reasons else ""
    lines.append(f"    status: {status}{suffix}")
    return lines
