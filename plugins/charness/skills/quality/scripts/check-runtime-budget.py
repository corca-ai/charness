#!/usr/bin/env python3
# ruff: noqa: E402
"""Enforce per-command runtime budgets recorded in runtime-signals.json.

Reads the adapter's `runtime_budgets` mapping (label -> max_elapsed_ms) and
compares it against the latest elapsed_ms recorded under
`.charness/quality/runtime-signals.json`. Exits non-zero on any violation.
Labels without a recorded sample are reported as warnings, not failures,
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
    missing_samples: list[str] = []
    checked: list[dict[str, Any]] = []

    for label, max_ms in sorted(budgets.items()):
        entry = commands.get(label)
        latest = entry.get("latest") if isinstance(entry, dict) else None
        elapsed = latest.get("elapsed_ms") if isinstance(latest, dict) else None
        if not isinstance(elapsed, int):
            missing_samples.append(label)
            checked.append({"label": label, "budget_ms": max_ms, "elapsed_ms": None, "status": "no-sample"})
            continue
        status = "ok" if elapsed <= max_ms else "exceeded"
        checked.append({"label": label, "budget_ms": max_ms, "elapsed_ms": elapsed, "status": status})
        if status == "exceeded":
            violations.append({"label": label, "budget_ms": max_ms, "elapsed_ms": elapsed})

    return {
        "signals_path": str(signals_path),
        "adapter_path": adapter.get("path"),
        "budgets_configured": len(budgets),
        "checked": checked,
        "violations": violations,
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
        lines.append(f"{status.upper():<8} {label}: {entry['elapsed_ms']}ms (budget {budget}ms)")
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
                    f"runtime budget exceeded: {v['label']} took {v['elapsed_ms']}ms (budget {v['budget_ms']}ms)",
                    file=sys.stderr,
                )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
