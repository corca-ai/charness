from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"
SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"
DEFAULT_TOP_RUNTIME_COUNT = 5


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _advisory_ewma(entry: dict[str, Any]) -> tuple[float | None, float | None, int | None]:
    if entry.get("advisory") is not True:
        return None, None, None
    ewma = entry.get("ewma_elapsed_ms")
    alpha = entry.get("alpha_last")
    samples = entry.get("samples")
    return (
        float(ewma) if isinstance(ewma, (int, float)) else None,
        float(alpha) if isinstance(alpha, (int, float)) else None,
        int(samples) if isinstance(samples, int) else None,
    )


def _elapsed_summary(label: str, entry: dict[str, Any], budgets: dict[str, int]) -> dict[str, Any] | None:
    latest = entry.get("latest")
    elapsed = latest.get("elapsed_ms") if isinstance(latest, dict) else None
    if not isinstance(elapsed, int):
        return None
    median_recent = entry.get("median_recent_elapsed_ms")
    max_recent = entry.get("max_recent_elapsed_ms")
    budget = budgets.get(label)
    return {
        "label": label,
        "latest_elapsed_ms": elapsed,
        "median_recent_elapsed_ms": median_recent if isinstance(median_recent, int) else elapsed,
        "max_recent_elapsed_ms": max_recent if isinstance(max_recent, int) else None,
        "budget_ms": budget if isinstance(budget, int) else None,
        "budgeted": isinstance(budget, int),
    }


def _runtime_hotspots(
    commands: dict[str, Any],
    budgets: dict[str, int],
    *,
    count: int,
) -> list[dict[str, Any]]:
    summaries = [
        summary
        for label, entry in commands.items()
        if isinstance(label, str)
        and isinstance(entry, dict)
        and (summary := _elapsed_summary(label, entry, budgets)) is not None
    ]
    summaries.sort(
        key=lambda item: (
            int(item["latest_elapsed_ms"]),
            int(item["median_recent_elapsed_ms"]),
            str(item["label"]),
        ),
        reverse=True,
    )
    return summaries[:count]


def _checked_entry(label: str, max_ms: int, entry: Any, smoothing_entry: dict[str, Any]) -> dict[str, Any]:
    ewma, alpha, smoothing_samples = _advisory_ewma(smoothing_entry)
    latest = entry.get("latest") if isinstance(entry, dict) else None
    elapsed = latest.get("elapsed_ms") if isinstance(latest, dict) else None
    median_recent = entry.get("median_recent_elapsed_ms") if isinstance(entry, dict) else None
    max_recent = entry.get("max_recent_elapsed_ms") if isinstance(entry, dict) else None
    basis_elapsed = median_recent if isinstance(median_recent, int) else elapsed
    status = "no-sample" if not isinstance(elapsed, int) else "ok"
    if isinstance(basis_elapsed, int) and basis_elapsed > max_ms:
        status = "exceeded"
    elif isinstance(elapsed, int) and elapsed > max_ms:
        status = "latest-spike"
    return {
        "label": label,
        "budget_ms": max_ms,
        "latest_elapsed_ms": elapsed if isinstance(elapsed, int) else None,
        "median_recent_elapsed_ms": basis_elapsed if isinstance(basis_elapsed, int) else None,
        "max_recent_elapsed_ms": max_recent if isinstance(max_recent, int) else None,
        "ewma_advisory_elapsed_ms": ewma,
        "ewma_alpha": alpha,
        "ewma_samples": smoothing_samples,
        "status": status,
    }


def evaluate(
    repo_root: Path,
    load_adapter: Callable[[Path], dict[str, Any]],
    *,
    top_runtime_count: int = DEFAULT_TOP_RUNTIME_COUNT,
) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    budgets: dict[str, int] = adapter["data"].get("runtime_budgets", {}) or {}
    signals_path = repo_root / SIGNALS_PATH
    smoothing_path = repo_root / SMOOTHING_PATH
    signals = _load_json(signals_path)
    smoothing = _load_json(smoothing_path)
    commands = signals.get("commands", {}) if isinstance(signals, dict) else {}
    smoothing_commands = smoothing.get("commands", {}) if isinstance(smoothing, dict) else {}

    checked: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    latest_spikes: list[dict[str, Any]] = []
    missing_samples: list[str] = []

    for label, max_ms in sorted(budgets.items()):
        entry = commands.get(label)
        smoothing_entry = smoothing_commands.get(label)
        if not isinstance(smoothing_entry, dict):
            smoothing_entry = {}
        checked_entry = _checked_entry(label, max_ms, entry, smoothing_entry)
        checked.append(checked_entry)
        if checked_entry["status"] == "no-sample":
            missing_samples.append(label)
        elif checked_entry["status"] == "latest-spike":
            latest_spikes.append(
                {
                    "label": label,
                    "budget_ms": max_ms,
                    "latest_elapsed_ms": checked_entry["latest_elapsed_ms"],
                    "median_recent_elapsed_ms": checked_entry["median_recent_elapsed_ms"],
                }
            )
        elif checked_entry["status"] == "exceeded":
            violations.append(
                {
                    "label": label,
                    "budget_ms": max_ms,
                    "median_recent_elapsed_ms": checked_entry["median_recent_elapsed_ms"],
                    "latest_elapsed_ms": checked_entry["latest_elapsed_ms"],
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
        "runtime_hotspots": _runtime_hotspots(commands, budgets, count=top_runtime_count),
    }


def format_human(report: dict[str, Any]) -> str:
    lines: list[str] = []
    if not report["budgets_configured"]:
        lines.append("No runtime_budgets configured in adapter; nothing to check.")
    for entry in report["checked"]:
        if entry["status"] == "no-sample":
            lines.append(f"WARN  {entry['label']}: no sample yet (budget {entry['budget_ms']}ms)")
            continue
        detail = f"latest {entry['latest_elapsed_ms']}ms, median {entry['median_recent_elapsed_ms']}ms"
        if entry["max_recent_elapsed_ms"] is not None:
            detail += f", max {entry['max_recent_elapsed_ms']}ms"
        if entry["ewma_advisory_elapsed_ms"] is not None:
            detail += f", ewma {entry['ewma_advisory_elapsed_ms']:.1f}ms advisory"
        lines.append(f"{entry['status'].upper():<12} {entry['label']}: {detail} (budget {entry['budget_ms']}ms)")
    hotspots = report.get("runtime_hotspots")
    if isinstance(hotspots, list) and hotspots:
        lines.append("Runtime hot spots:")
        for item in hotspots:
            budget = item.get("budget_ms")
            budget_text = f"budget {budget}ms" if isinstance(budget, int) else "unbudgeted"
            lines.append(
                f"HOTSPOT      {item['label']}: latest {item['latest_elapsed_ms']}ms, "
                f"median {item['median_recent_elapsed_ms']}ms ({budget_text})"
            )
    return "\n".join(lines)
