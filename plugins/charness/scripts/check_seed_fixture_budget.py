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
    # Two layouts, one script: this repo keeps the lib under `skills/public/`,
    # the plugin export flattens it to `skills/`. Hard-coding the first made the
    # exported copy die with a bare FileNotFoundError from exec_module.
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "standing_test_economics_lib.py",
        repo_root / "skills" / "quality" / "scripts" / "standing_test_economics_lib.py",
    )
    target = next((candidate for candidate in candidates if candidate.is_file()), None)
    if target is None:
        raise ImportError(
            "standing_test_economics_lib.py not found in either layout: "
            + ", ".join(str(candidate) for candidate in candidates)
        )
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
    parser.add_argument(
        "--advisory-on-scan-failure",
        action="store_true",
        help=(
            "Report a failed pytest tmp scan without blocking. The escape hatch for a box "
            "whose scan breaks for a reason this gate cannot classify; strictly narrower "
            "than `git push --no-verify`, which disables every gate instead of this one."
        ),
    )
    return parser.parse_args()


def classify_scan(footprint: dict, advisory_on_scan_failure: bool) -> str:
    """Name what this run actually learned about the seed footprint.

    A failed scan is not an absent tree, and it is not automatically forgivable
    either. The scan accepts a partial walk and retries one that died early, so a
    failure that survives all of that means this run measured nothing -- and a
    gate that reports "nothing to measure" as success is a gate a permanently
    broken `du` passes forever.

    The exception is a capability gap: a `du` that is absent, not executable, or
    too old to accept `-B` is something this box cannot do, not a measurement
    that broke. A portable harness must not block a push on it, and no retry
    would change the answer.
    """
    status = footprint.get("status")
    if status == "available":
        return "scanned"
    if status != "unavailable":
        return "advisory_only_no_pytest_temp_yet"
    if footprint.get("capability_gap"):
        return "advisory_only_du_unavailable"
    if advisory_on_scan_failure:
        return "advisory_only_scan_failure_waived"
    return "blocking_pytest_temp_scan_failed"


def collect_breaches(footprint: dict, args: argparse.Namespace) -> tuple[list[dict[str, object]], int]:
    # `pytest_temp_footprint_quick` is the only producer here and it reports
    # `total_disk_bytes`; the old `total_bytes` fallback belonged to the slow
    # scan and could never fire from this call site.
    total_disk_bytes = int(footprint.get("total_disk_bytes") or 0)
    breaches: list[dict[str, object]] = []
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
    for prefix, totals in (footprint.get("seed_totals") or {}).items():
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
    return breaches, total_disk_bytes


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    lib = _load_inventory()
    footprint = lib._pytest_temp_footprint_quick()
    classification = classify_scan(footprint, args.advisory_on_scan_failure)
    if classification == "scanned":
        breaches, total_disk_bytes = collect_breaches(footprint, args)
    else:
        breaches, total_disk_bytes = [], None
    scan_failed = classification == "blocking_pytest_temp_scan_failed"
    out = {
        "repo_root": str(repo_root),
        "scope_classification": classification,
        "pytest_temp_status": footprint.get("status"),
        "pytest_temp_scan_reason": footprint.get("reason"),
        "pytest_temp_scan_attempts": footprint.get("attempts"),
        "pytest_temp_scan_partial": footprint.get("partial"),
        "total_disk_bytes": total_disk_bytes,
        "total_budget_bytes": args.total_budget_bytes,
        "per_seed_budget_bytes": args.per_seed_budget_bytes,
        "breaches": breaches,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1 if breaches or scan_failed else 0
    if scan_failed:
        print(
            f"scope_classification={classification}: the pytest tmp scan failed "
            f"{footprint.get('attempts')}x (root {footprint.get('root')}, "
            f"reason {footprint.get('reason')}); nothing was measured, so this run proves "
            "nothing about the seed budget.",
            file=sys.stderr,
        )
        print(
            "    remediation: run `du -d 4 -B1 "
            f"{footprint.get('root')}` to see why the walk dies before printing the root "
            "total. A vanished entry is already tolerated and an early death is already "
            "retried, so a failure here is a real one. To report it without blocking, pass "
            "--advisory-on-scan-failure directly, or set CHARNESS_SEED_FIXTURE_ADVISORY=1 "
            "when this runs inside run-quality.sh (where the argv is fixed).",
            file=sys.stderr,
        )
        return 1
    if classification == "advisory_only_du_unavailable":
        print(
            f"scope_classification={classification}: `du` cannot run this measurement on "
            f"this box ({footprint.get('reason')}), so the seed footprint is unmeasurable "
            "here; gate is advisory-only."
        )
        return 0
    if classification == "advisory_only_scan_failure_waived":
        print(
            f"scope_classification={classification}: the pytest tmp scan failed "
            f"({footprint.get('reason')}) and --advisory-on-scan-failure waived the block; "
            "nothing was measured, so this run proves nothing about the seed budget."
        )
        return 0
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
