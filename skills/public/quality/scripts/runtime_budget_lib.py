from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from runtime_profile_lib import profile_budgets, profile_commands, selected_runtime_profile
from runtime_timing_log_lib import evaluate_timing_log
from runtime_visibility_lib import runtime_visibility_findings

SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"
SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"
DEFAULT_TOP_RUNTIME_COUNT = 5
STALE_HOTSPOT_SAMPLE_DAYS = 14
# A runtime budget only ever moves one way on its own: a violation forces a raise,
# and nothing ever reports that the raise is no longer needed. That makes a stale
# budget invisible — the gate keeps passing precisely because it can no longer fail
# (charness's own `check-coverage` sat at 55000ms against a 7835ms observed max).
# This advisory closes the loop by naming budgets whose worst recent run is far
# under the bar. Advisory, never blocking: retuning a budget is reversible work, so
# it forces the question and leaves the judgment to the operator (north star P1/P5).
BUDGET_SLACK_FACTOR = 3.0
# Below this, ordinary scheduling jitter dominates and a slack ratio is noise.
MIN_SLACK_ADVISORY_BUDGET_MS = 1000
# Headroom retained when suggesting a retune: 1.4x the worst observed run still
# absorbs normal variance while letting a genuine 2x regression trip.
SLACK_SUGGESTION_HEADROOM = 1.4


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


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _reference_time(payload: dict[str, Any]) -> datetime:
    parsed = _parse_timestamp(payload.get("updated_at"))
    return parsed or datetime.now(timezone.utc)


def _elapsed_summary(
    label: str,
    entry: dict[str, Any],
    budgets: dict[str, int],
    *,
    reference_time: datetime,
) -> dict[str, Any] | None:
    latest = entry.get("latest")
    elapsed = latest.get("elapsed_ms") if isinstance(latest, dict) else None
    if not isinstance(elapsed, int):
        return None
    latest_timestamp = latest.get("timestamp") if isinstance(latest, dict) else None
    parsed_latest = _parse_timestamp(latest_timestamp)
    stale_days: int | None = None
    if parsed_latest is not None:
        age = reference_time - parsed_latest
        stale_days = max(age.days, 0)
    median_recent = entry.get("median_recent_elapsed_ms")
    max_recent = entry.get("max_recent_elapsed_ms")
    budget = budgets.get(label)
    return {
        "label": label,
        "latest_timestamp": latest_timestamp if isinstance(latest_timestamp, str) else None,
        "latest_elapsed_ms": elapsed,
        "median_recent_elapsed_ms": median_recent if isinstance(median_recent, int) else elapsed,
        "max_recent_elapsed_ms": max_recent if isinstance(max_recent, int) else None,
        "budget_ms": budget if isinstance(budget, int) else None,
        "budgeted": isinstance(budget, int),
        "stale": stale_days is not None and stale_days > STALE_HOTSPOT_SAMPLE_DAYS,
        "stale_days": stale_days,
    }


def _runtime_hotspot_summaries(
    commands: dict[str, Any],
    budgets: dict[str, int],
    *,
    reference_time: datetime,
) -> list[dict[str, Any]]:
    summaries = [
        summary
        for label, entry in commands.items()
        if isinstance(label, str)
        and isinstance(entry, dict)
        and (summary := _elapsed_summary(label, entry, budgets, reference_time=reference_time)) is not None
    ]
    summaries.sort(
        key=lambda item: (
            int(item["latest_elapsed_ms"]),
            int(item["median_recent_elapsed_ms"]),
            str(item["label"]),
        ),
        reverse=True,
    )
    return summaries


def _runtime_hotspots(
    commands: dict[str, Any],
    budgets: dict[str, int],
    *,
    count: int,
    reference_time: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summaries = _runtime_hotspot_summaries(commands, budgets, reference_time=reference_time)
    fresh = [
        {key: value for key, value in summary.items() if key not in {"latest_timestamp", "stale", "stale_days"}}
        for summary in summaries
        if summary.get("stale") is not True
    ]
    stale = [summary for summary in summaries if summary.get("stale") is True]
    return fresh[:count], stale


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


def budget_slack_findings(checked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Name budgets whose worst recent run is far under the bar.

    Presence/report only — it never changes an exit code. The point is that a
    budget which cannot fail is not evidence of health, and without this the only
    signal a budget ever emits is "raise me".
    """
    findings: list[dict[str, Any]] = []
    for entry in checked:
        budget = entry.get("budget_ms")
        worst = entry.get("max_recent_elapsed_ms")
        if not isinstance(budget, int) or not isinstance(worst, int):
            continue
        if budget < MIN_SLACK_ADVISORY_BUDGET_MS or worst <= 0:
            continue
        ratio = budget / worst
        if ratio < BUDGET_SLACK_FACTOR:
            continue
        findings.append(
            {
                "label": entry["label"],
                "budget_ms": budget,
                "max_recent_elapsed_ms": worst,
                "slack_ratio": round(ratio, 1),
                "suggested_budget_ms": int(worst * SLACK_SUGGESTION_HEADROOM),
            }
        )
    return sorted(findings, key=lambda item: item["slack_ratio"], reverse=True)


def evaluate(
    repo_root: Path,
    load_adapter: Callable[[Path], dict[str, Any]],
    *,
    runtime_profile: str | None = None,
    top_runtime_count: int = DEFAULT_TOP_RUNTIME_COUNT,
) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    adapter_data = adapter["data"]
    selected_profile = selected_runtime_profile(adapter_data, runtime_profile)
    budgets, profile_config_errors = profile_budgets(adapter_data, selected_profile)
    signals_path = repo_root / SIGNALS_PATH
    smoothing_path = repo_root / SMOOTHING_PATH
    signals = _load_json(signals_path)
    smoothing = _load_json(smoothing_path)
    commands = profile_commands(signals, selected_profile) if isinstance(signals, dict) else {}
    smoothing_commands = profile_commands(smoothing, selected_profile) if isinstance(smoothing, dict) else {}
    runtime_reference_time = _reference_time(signals) if isinstance(signals, dict) else datetime.now(timezone.utc)

    # When runtime-signals.json has no samples for the selected profile, fall back
    # to a repo-declared command-timing log (inert when unconfigured). Config-shape
    # errors ride profile_config_errors so check_runtime_budget fails loud.
    timing_log = evaluate_timing_log(repo_root, adapter_data, selected_profile)
    profile_config_errors = list(profile_config_errors) + timing_log["errors"]
    commands_source = "runtime_signals" if commands else "none"
    if not commands and timing_log["commands"]:
        commands = timing_log["commands"]
        commands_source = "command_timing_log"

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

    runtime_hotspots, stale_runtime_hotspots = _runtime_hotspots(
        commands,
        budgets,
        count=top_runtime_count,
        reference_time=runtime_reference_time,
    )

    return {
        "signals_path": str(signals_path),
        "smoothing_path": str(smoothing_path),
        "adapter_path": adapter.get("path"),
        "runtime_profile": selected_profile,
        "profile_config_errors": profile_config_errors,
        "budgets_configured": len(budgets),
        "checked": checked,
        "violations": violations,
        "budget_slack_findings": budget_slack_findings(checked),
        "latest_spikes": latest_spikes,
        "missing_samples": missing_samples,
        "runtime_hotspots": runtime_hotspots,
        "stale_runtime_hotspots": stale_runtime_hotspots,
        "runtime_visibility_findings": runtime_visibility_findings(adapter_data, budgets),
        "commands_source": commands_source,
        "timing_log": {
            "configured": timing_log["configured"],
            "path": timing_log["path"],
            "file_present": timing_log["file_present"],
            "samples_total": timing_log["samples_total"],
            "recent_window": timing_log.get("recent_window"),
            "source_used": commands_source == "command_timing_log",
        },
    }


def _render_hotspot(item: dict[str, Any]) -> str:
    budget = item.get("budget_ms")
    budget_text = f"budget {budget}ms" if isinstance(budget, int) else "unbudgeted"
    return (
        f"HOTSPOT      {item['label']}: latest {item['latest_elapsed_ms']}ms, "
        f"median {item['median_recent_elapsed_ms']}ms ({budget_text})"
    )


def _render_slack(item: dict[str, Any]) -> str:
    return (
        f"SLACK        {item['label']}: budget {item['budget_ms']}ms vs worst recent "
        f"{item['max_recent_elapsed_ms']}ms ({item['slack_ratio']}x); "
        f"consider {item['suggested_budget_ms']}ms"
    )


def _render_stale_hotspot(item: dict[str, Any]) -> str:
    return (
        f"STALE       {item['label']}: latest sample {item.get('latest_timestamp') or 'unknown'} "
        f"({item.get('stale_days')}d old)"
    )


def _append_section(
    lines: list[str],
    report: dict[str, Any],
    key: str,
    header: str,
    render: Callable[[dict[str, Any]], str],
) -> None:
    """Append `header` plus one rendered line per item, or nothing when empty."""
    items = report.get(key)
    if not isinstance(items, list) or not items:
        return
    lines.append(header)
    lines.extend(render(item) for item in items)


def format_human(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Runtime profile: {report['runtime_profile']}")
    for error in report.get("profile_config_errors", []):
        lines.append(f"ERROR {error}")
    for finding in report.get("runtime_visibility_findings", []):
        lines.append(f"WEAK  {finding['type']}: {finding['message']}")
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
    for key, header, render in (
        ("runtime_hotspots", "Runtime hot spots:", _render_hotspot),
        ("budget_slack_findings", "Budget slack (advisory: these budgets can no longer fail):", _render_slack),
        ("stale_runtime_hotspots", "Stale runtime hot spots excluded:", _render_stale_hotspot),
    ):
        _append_section(lines, report, key, header, render)
    return "\n".join(lines)
