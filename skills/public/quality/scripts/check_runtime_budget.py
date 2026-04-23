#!/usr/bin/env python3
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
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"
SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _smoothing_entry(commands: dict[str, Any], label: str) -> dict[str, Any]:
    entry = commands.get(label)
    return entry if isinstance(entry, dict) else {}


def _advisory_ewma(entry: dict[str, Any]) -> tuple[float | None, float | None, int | None]:
    if entry.get("advisory") is not True:
        return None, None, None
    ewma = entry.get("ewma_elapsed_ms")
    alpha = entry.get("alpha_last")
    samples = entry.get("samples")
    ewma_value = float(ewma) if isinstance(ewma, (int, float)) else None
    alpha_value = float(alpha) if isinstance(alpha, (int, float)) else None
    samples_value = int(samples) if isinstance(samples, int) else None
    return ewma_value, alpha_value, samples_value


def evaluate(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    budgets: dict[str, int] = data.get("runtime_budgets", {}) or {}
    signals_path = repo_root / SIGNALS_PATH
    smoothing_path = repo_root / SMOOTHING_PATH
    signals = _load_json(signals_path)
    smoothing = _load_json(smoothing_path)
    commands = signals.get("commands", {}) if isinstance(signals, dict) else {}
    smoothing_commands = smoothing.get("commands", {}) if isinstance(smoothing, dict) else {}

    violations: list[dict[str, Any]] = []
    latest_spikes: list[dict[str, Any]] = []
    missing_samples: list[str] = []
    checked: list[dict[str, Any]] = []

    for label, max_ms in sorted(budgets.items()):
        entry = commands.get(label)
        smoothing_entry = _smoothing_entry(smoothing_commands, label)
        ewma, alpha, smoothing_samples = _advisory_ewma(smoothing_entry)
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
                    "ewma_advisory_elapsed_ms": ewma,
                    "ewma_alpha": alpha,
                    "ewma_samples": smoothing_samples,
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
                "ewma_advisory_elapsed_ms": ewma,
                "ewma_alpha": alpha,
                "ewma_samples": smoothing_samples,
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
        "smoothing_path": str(smoothing_path),
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
        ewma = entry["ewma_advisory_elapsed_ms"]
        if ewma is not None:
            detail += f", ewma {ewma:.1f}ms advisory"
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
