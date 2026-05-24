#!/usr/bin/env python3
"""Validate-then-append one RCA event to the conversion ledger.

An invalid event is refused before any write (validate-before-append), so a
malformed input never mutates the ledger. The tie-break default is
converted=false: ambiguous events inflate the denominator rather than being
silently dropped.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from scripts import rca_ledger_lib as lib
except ImportError:
    import rca_ledger_lib as lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append one validated RCA event to the ledger.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ledger", default=None, help="Override ledger path (defaults to canonical).")
    parser.add_argument("--source", required=True, choices=["debug", "issue", "retro"])
    parser.add_argument(
        "--event-kind", required=True, choices=["bug", "repeated_correction", "weak_proof"]
    )
    parser.add_argument(
        "--converted",
        action="store_true",
        help="Set only when a recurrence-preventing durable artifact was produced.",
    )
    parser.add_argument(
        "--durable-kind",
        default="none",
        choices=["gate", "spec", "test", "issue", "retro_lesson", "none"],
    )
    parser.add_argument("--class-key", required=True)
    parser.add_argument("--caught-by", default=None, choices=["agent", "human", "gate"])
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--ref", default=None)
    parser.add_argument("--note", default=None)
    parser.add_argument("--ts", default=None, help="UTC ISO8601 ...Z timestamp; defaults to now.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def build_record(args: argparse.Namespace) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": 1,
        "ts": args.ts or lib.now_ts(),
        "source": args.source,
        "event_kind": args.event_kind,
        "converted": bool(args.converted),
        "durable_kind": args.durable_kind,
        "class_key": args.class_key,
    }
    if args.caught_by is not None:
        record["caught_by"] = args.caught_by
    if args.seed:
        record["seed"] = True
    if args.ref is not None:
        record["ref"] = args.ref
    if args.note is not None:
        record["note"] = args.note
    return record


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    ledger_path = lib.resolve_ledger_path(repo_root, Path(args.ledger) if args.ledger else None)
    record = build_record(args)

    import jsonschema

    try:
        lib.validate_record(record, lib.load_schema())
    except jsonschema.ValidationError as exc:
        result = {"status": "rejected", "appended": False, "error": exc.message}
        print(json.dumps(result, indent=2) if args.json else f"rejected: {exc.message}", file=sys.stderr)
        return 1

    if lib.ledger_contains_event_identity(ledger_path, record):
        result = {
            "status": "duplicate",
            "appended": False,
            "ledger_path": lib.portable_path(repo_root, ledger_path),
            "class_key": record["class_key"],
        }
        print(json.dumps(result, indent=2) if args.json else f"duplicate: {result['ledger_path']}")
        return 0

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    result = {
        "status": "appended",
        "appended": True,
        "ledger_path": lib.portable_path(repo_root, ledger_path),
        "class_key": record["class_key"],
    }
    print(json.dumps(result, indent=2) if args.json else f"appended: {result['ledger_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
