#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

DEFAULT_TOTAL_BUDGET_BYTES = 10 * 1024 * 1024 * 1024
DEFAULT_PER_SEED_BUDGET_BYTES = 3 * 1024 * 1024 * 1024


def _load_inventory():
    here = Path(__file__).resolve()
    repo_root = here.parents[1]
    target = repo_root / "skills" / "public" / "quality" / "scripts" / "standing_test_economics_lib.py"
    spec = importlib.util.spec_from_file_location("standing_test_economics_lib", target)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _format_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PiB"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce a per-seed and total budget on the pytest temp fixture footprint "
            "observed by inventory_standing_test_economics.py."
        )
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--total-budget-bytes",
        type=int,
        default=DEFAULT_TOTAL_BUDGET_BYTES,
        help=f"Fail when pytest tmp total disk bytes exceed this budget (default {DEFAULT_TOTAL_BUDGET_BYTES}).",
    )
    parser.add_argument(
        "--per-seed-budget-bytes",
        type=int,
        default=DEFAULT_PER_SEED_BUDGET_BYTES,
        help=f"Fail when any single seed prefix exceeds this budget (default {DEFAULT_PER_SEED_BUDGET_BYTES}).",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    lib = _load_inventory()
    footprint = lib._pytest_temp_footprint_quick()
    breaches: list[dict[str, object]] = []
    classification: str
    total_disk_bytes: int | None
    if footprint.get("status") != "available":
        classification = "advisory_only_no_pytest_temp_yet"
        total_disk_bytes = None
    else:
        total_disk_bytes = int(footprint.get("total_disk_bytes") or footprint.get("total_bytes") or 0)
        if total_disk_bytes > args.total_budget_bytes:
            breaches.append({
                "type": "total_budget_exceeded",
                "observed_bytes": total_disk_bytes,
                "budget_bytes": args.total_budget_bytes,
                "remediation": (
                    "Reduce pytest tmp retention or clean stale `pytest-of-*/pytest-*` sessions; "
                    "see inventory_standing_test_economics.py for the per-session breakdown."
                ),
            })
        seed_totals = footprint.get("seed_totals") or {}
        for prefix, totals in seed_totals.items():
            disk = int(totals.get("disk_bytes") or 0)
            if disk > args.per_seed_budget_bytes:
                breaches.append({
                    "type": "per_seed_budget_exceeded",
                    "seed_prefix": prefix,
                    "observed_bytes": disk,
                    "budget_bytes": args.per_seed_budget_bytes,
                    "session_count": int(totals.get("count") or 0),
                    "remediation": (
                        f"Stop materializing `{prefix}-*` per session; share via a content-addressed cache or "
                        f"reduce pytest tmp retention."
                    ),
                })
        classification = "scanned"
    out = {
        "repo_root": str(repo_root),
        "scope_classification": classification,
        "pytest_temp_status": footprint.get("status"),
        "total_disk_bytes": total_disk_bytes,
        "total_budget_bytes": args.total_budget_bytes,
        "per_seed_budget_bytes": args.per_seed_budget_bytes,
        "breaches": breaches,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1 if breaches else 0
    if classification.startswith("advisory_only"):
        print(f"scope_classification={classification}: no pytest tmp directory present yet; gate is advisory-only.")
        return 0
    if not breaches:
        print(
            f"Seed fixture budget within limits: "
            f"total {_format_bytes(total_disk_bytes or 0)} / {_format_bytes(args.total_budget_bytes)}, "
            f"per-seed cap {_format_bytes(args.per_seed_budget_bytes)}."
        )
        return 0
    print(
        f"Seed fixture budget exceeded ({len(breaches)} breach(es)):",
        file=sys.stderr,
    )
    for breach in breaches:
        if breach["type"] == "total_budget_exceeded":
            print(
                f"  total: {_format_bytes(int(breach['observed_bytes']))} "
                f"> {_format_bytes(int(breach['budget_bytes']))}",
                file=sys.stderr,
            )
        else:
            print(
                f"  per-seed `{breach['seed_prefix']}`: "
                f"{_format_bytes(int(breach['observed_bytes']))} "
                f"> {_format_bytes(int(breach['budget_bytes']))} "
                f"(session_count={breach.get('session_count')})",
                file=sys.stderr,
            )
        print(f"    remediation: {breach['remediation']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
