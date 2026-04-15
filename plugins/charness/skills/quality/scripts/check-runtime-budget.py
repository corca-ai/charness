#!/usr/bin/env python3
# ruff: noqa: E402
"""Enforce per-command runtime budgets recorded in runtime-signals.json.

Reads the adapter's `runtime_budgets` mapping (label -> max_elapsed_ms) and
compares it against recent runtime samples recorded under
`.charness/quality/runtime-signals.json`. When a command has recent summary
stats, the gate fails on recent median drift instead of a single latest-sample
spike. Labels without a recorded sample are reported as warnings, not failures,
so a budget can be defined before its first observed run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT_FOR_IMPORT = _runtime_root()
sys.path.insert(0, str(REPO_ROOT_FOR_IMPORT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from resolve_adapter import load_adapter

SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"


def _load_signals(signals_path: Path) -> dict[str, Any]:
    if not signals_path.is_file():
        return {}
    try:
        return json.loads(signals_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def evaluate(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    budgets: dict[str, int] = data.get("runtime_budgets", {}) or {}
    signals_path = repo_root / SIGNALS_PATH
    signals = _load_signals(signals_path)
    commands = signals.get("commands", {}) if isinstance(signals, dict) else {}

    violations: list[dict[str, Any]] = []
    latest_spikes: list[dict[str, Any]] = []
    missing_samples: list[str] = []
    checked: list[dict[str, Any]] = []

    for label, max_ms in sorted(budgets.items()):
        entry = commands.get(label)
        latest = entry.get("latest") if isinstance(entry, dict) else None
        elapsed = latest.get("elapsed_ms") if isinstance(latest, dict) else None
        if not isinstance(elapsed, int):
            missing_samples.append(label)
            checked.append(
                {
                    "label": label,
                    "budget_ms": max_ms,
                    "latest_elapsed_ms": None,
                    "median_recent_elapsed_ms": None,
                    "max_recent_elapsed_ms": None,
                    "status": "no-sample",
                }
            )
            continue

        median_recent = entry.get("median_recent_elapsed_ms") if isinstance(entry, dict) else None
        max_recent = entry.get("max_recent_elapsed_ms") if isinstance(entry, dict) else None
        basis_elapsed = median_recent if isinstance(median_recent, int) else elapsed
        status = "ok" if basis_elapsed <= max_ms else "exceeded"
        if status == "ok" and elapsed > max_ms:
            status = "latest-spike"
            latest_spikes.append(
                {
                    "label": label,
                    "budget_ms": max_ms,
                    "latest_elapsed_ms": elapsed,
                    "median_recent_elapsed_ms": basis_elapsed,
                }
            )
        checked.append(
            {
                "label": label,
                "budget_ms": max_ms,
                "latest_elapsed_ms": elapsed,
                "median_recent_elapsed_ms": basis_elapsed,
                "max_recent_elapsed_ms": max_recent if isinstance(max_recent, int) else None,
                "status": status,
            }
        )
        if status == "exceeded":
            violations.append(
                {
                    "label": label,
                    "budget_ms": max_ms,
                    "median_recent_elapsed_ms": basis_elapsed,
                    "latest_elapsed_ms": elapsed,
                }
            )

    return {
        "signals_path": str(signals_path),
        "adapter_path": adapter.get("path"),
        "budgets_configured": len(budgets),
        "checked": checked,
        "violations": violations,
        "latest_spikes": latest_spikes,
        "missing_samples": missing_samples,
    }


def _format_human(report: dict[str, Any]) -> str:
    lines: list[str] = []
    if not report["budgets_configured"]:
        lines.append("No runtime_budgets configured in adapter; nothing to check.")
        return "\n".join(lines)
    for entry in report["checked"]:
        label = entry["label"]
        budget = entry["budget_ms"]
        status = entry["status"]
        if status == "no-sample":
            lines.append(f"WARN  {label}: no sample yet (budget {budget}ms)")
            continue
        latest = entry["latest_elapsed_ms"]
        median = entry["median_recent_elapsed_ms"]
        max_recent = entry["max_recent_elapsed_ms"]
        detail = f"latest {latest}ms, median {median}ms"
        if max_recent is not None:
            detail += f", max {max_recent}ms"
        lines.append(f"{status.upper():<12} {label}: {detail} (budget {budget}ms)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = evaluate(repo_root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report))

    if report["violations"]:
        if not args.json:
            for v in report["violations"]:
                print(
                    "runtime budget exceeded: "
                    f"{v['label']} recent median {v['median_recent_elapsed_ms']}ms "
                    f"(latest {v['latest_elapsed_ms']}ms, budget {v['budget_ms']}ms)",
                    file=sys.stderr,
                )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
