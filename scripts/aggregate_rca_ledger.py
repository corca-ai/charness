#!/usr/bin/env python3
"""Report the RCA-to-learning conversion rate from the ledger.

Reports the rate twice: including seed events (sanity) and excluding them (the
figure a baseline target is set from). Auto-append is wired (slice 2), so the
banner reads ON; the baseline honesty guards still hold — it emits `n/a` (not
0%) for an empty seed-excluded window and refuses to print a non-seed baseline
rate while zero non-seed events exist.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts import rca_ledger_lib as lib
    from scripts.yaml_output import emit_yaml
except ImportError:
    import rca_ledger_lib as lib

    from yaml_output import emit_yaml


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate the RCA conversion rate.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ledger", default=None, help="Override ledger path (defaults to canonical).")
    return parser.parse_args(argv)


def report(payload: dict[str, object]) -> dict[str, object]:
    """Fold the reading caveats into the payload this command actually emits.

    Output is unconditionally YAML, so anything a reader needs has to live in the
    payload. These three lines existed only inside the text rendering: the
    seed-included figure is a sanity number that has been misquoted as the
    baseline, an empty seed-excluded window is `n/a` rather than 0%, and the
    target is a two-part criterion whose second half (zero falsified conversions)
    is invisible from the floor alone. Emitting the bare aggregate would have
    deleted all three while leaving every number intact.
    """
    enriched = dict(payload)
    enriched["seed_included_caveat"] = (
        "sanity only — not the baseline; do not quote as the conversion rate"
    )
    if not payload["baseline_rate_available"]:
        enriched["baseline_rate_note"] = (
            "n/a, not 0%: there are 0 non-seed events yet. Auto-append is wired; the "
            "baseline figure stays n/a until live closeout events accrue."
        )
    target = payload["target"]
    if isinstance(target, dict):
        enriched["target_definition"] = (
            f"#184, set 2026-06-13: >={float(target['floor']) * 100:.0f}% rolling "
            f"{target['window_days']}d seed-excluded (judged at n>={target['min_events']}) "
            "+ zero falsified conversions"
        )
    return enriched


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    ledger_path = lib.resolve_ledger_path(repo_root, Path(args.ledger) if args.ledger else None)
    payload = lib.aggregate(lib.read_events(ledger_path))

    emit_yaml(report(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
