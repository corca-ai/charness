#!/usr/bin/env python3
"""Render quality runtime metrics for a checked-in quality summary."""
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
runtime_budget_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_lib")
_summary_output = SKILL_RUNTIME.load_local_skill_module(__file__, "summary_output_lib")

RUNTIME_SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): the runtime hot-spot ranking is an
# inference-layer trend, so it self-declares blind spots and the question the
# `quality` consumer must answer before budgeting or optimizing a hot spot.
INTERPRETATION = {
    "measures": (
        "recent per-label gate/test elapsed times (latest sample and recent median) "
        "from structured runtime signals, ranked into hot spots"
    ),
    "proxy_for": "where standing runtime cost concentrates — the gates worth budgeting or speeding up",
    "blind_spots": (
        "a sample reflects one machine's state — a cold cache, a noisy neighbor, or a "
        "one-off spike can rank a usually-cheap gate hot; it cannot separate a true "
        "standing dominator from transient machine noise, nor judge whether the cost "
        "buys necessary proof"
    ),
    "interpretation_question": (
        "is this hot spot a real standing cost THIS repo should budget or optimize, or "
        "transient machine noise / a cost that already buys necessary proof?"
    ),
}


def _interpretation_line() -> str:
    return (
        "- runtime interpretation (inference-layer trend, not a verdict): "
        f"measures {INTERPRETATION['measures']}; proxy for {INTERPRETATION['proxy_for']}; "
        f"blind spots: {INTERPRETATION['blind_spots']}. "
        f"Consumer must answer first: {INTERPRETATION['interpretation_question']}"
    )


def _format_elapsed(ms: int | None) -> str:
    if ms is None:
        return "unknown"
    if ms >= 1000:
        return f"{ms / 1000:.1f}s"
    return f"{ms}ms"


def _format_hotspots(items: list[dict[str, object]]) -> str:
    parts: list[str] = []
    for item in items:
        label = str(item["label"])
        latest = _format_elapsed(item.get("latest_elapsed_ms") if isinstance(item.get("latest_elapsed_ms"), int) else None)
        median = _format_elapsed(
            item.get("median_recent_elapsed_ms") if isinstance(item.get("median_recent_elapsed_ms"), int) else None
        )
        budget = item.get("budget_ms")
        budget_text = f", budget {_format_elapsed(budget)}" if isinstance(budget, int) else ""
        parts.append(f"`{label}` {latest} latest / {median} median{budget_text}")
    return "; ".join(parts)


def _format_stale_hotspots(items: list[dict[str, object]]) -> str:
    parts: list[str] = []
    for item in items:
        label = str(item["label"])
        timestamp = item.get("latest_timestamp")
        stale_days = item.get("stale_days")
        timestamp_text = f"latest sample {timestamp}" if isinstance(timestamp, str) else "latest sample unknown"
        stale_text = f", {stale_days}d old" if isinstance(stale_days, int) else ""
        parts.append(f"`{label}` {timestamp_text}{stale_text}")
    return "; ".join(parts)


def _format_visibility(findings: list[dict[str, object]]) -> str:
    if not findings:
        return "- runtime visibility: configured."
    finding_types = ", ".join(f"`{item['type']}`" for item in findings)
    actions = "; ".join(str(item["recommended_action"]).rstrip(".") for item in findings)
    return f"- runtime visibility: weak due to {finding_types}; {actions}."


def _timing_log_info(report: dict[str, object]) -> dict[str, object]:
    info = report.get("timing_log")
    return info if isinstance(info, dict) else {}


def render_markdown_lines(report: dict[str, object], *, repo_root: Path, signals_present: bool) -> list[str]:
    profile = str(report["runtime_profile"])
    hotspots = report.get("runtime_hotspots")
    if not isinstance(hotspots, list):
        hotspots = []
    stale_hotspots = report.get("stale_runtime_hotspots")
    if not isinstance(stale_hotspots, list):
        stale_hotspots = []
    findings = report.get("runtime_visibility_findings")
    if not isinstance(findings, list):
        findings = []
    visibility = _format_visibility(findings)
    timing_log = _timing_log_info(report)

    if hotspots:
        if report.get("commands_source") == "command_timing_log":
            source = (
                "- runtime source: repo-declared command-timing log "
                f"`{timing_log.get('path')}` ingested via the `command_timing_log` adapter key "
                f"({timing_log.get('samples_total')} samples); profile `{profile}`."
            )
        else:
            recorder = repo_root / "scripts" / "gates_support" / "record_quality_runtime.py"
            provenance = (
                " via `scripts/gates_support/record_quality_runtime.py`"
                if recorder.is_file()
                else ""
            )
            source = (
                "- runtime source: structured metrics from "
                f"`{RUNTIME_SIGNALS_PATH}` rendered by `render_runtime_summary.py`{provenance}; profile `{profile}`."
            )
        hot_spots = f"- runtime hot spots: {_format_hotspots(hotspots)}."
        lines = [source, hot_spots]
        if stale_hotspots:
            lines.append(f"- stale runtime hot spots excluded: {_format_stale_hotspots(stale_hotspots)}.")
        lines.extend([visibility, _interpretation_line()])
        return lines

    # No hot spots: prefer the most specific source explanation available.
    if timing_log.get("configured") and not timing_log.get("file_present"):
        source_line = (
            "- runtime source: command-timing log "
            f"`{timing_log.get('path')}` declared but not found yet; "
            f"`{RUNTIME_SIGNALS_PATH}` also has no samples for profile `{profile}`."
        )
    elif timing_log.get("configured"):
        if stale_hotspots:
            source_line = (
                "- runtime source: command-timing log "
                f"`{timing_log.get('path')}` has no fresh usable samples for profile `{profile}`."
            )
        else:
            source_line = (
                "- runtime source: command-timing log "
                f"`{timing_log.get('path')}` has no usable samples for profile `{profile}`."
            )
    elif signals_present:
        if stale_hotspots:
            source_line = (
                "- runtime source: structured metrics file "
                f"`{RUNTIME_SIGNALS_PATH}` has no fresh samples for profile `{profile}`."
            )
        else:
            source_line = (
                "- runtime source: structured metrics file "
                f"`{RUNTIME_SIGNALS_PATH}` has no samples for profile `{profile}`."
            )
    else:
        source_line = (
            "- runtime source: not configured; add structured timing capture "
            "(or a `command_timing_log` adapter key) before reporting timing trends."
        )
    lines = [source_line]
    if stale_hotspots:
        lines.append(f"- stale runtime hot spots excluded: {_format_stale_hotspots(stale_hotspots)}.")
    lines.extend([
        "- runtime hot spots: unavailable until structured runtime metrics have samples.",
        visibility,
    ])
    return lines


def build_report(repo_root: Path, *, runtime_profile: str | None, top_runtime_count: int) -> dict[str, object]:
    # GUARDED AT THE READ SITE, which for this family is where `load_adapter` is HANDED to
    # `runtime_budget_lib`. The lib takes the loader injected -- that seam is deliberate,
    # and it means the lib cannot know which adapter it is reading or refuse for it. So the
    # guard belongs here, in each caller, and `runtime_budget_lib` / `runtime_budget_sizing_lib`
    # stay classified unguarded rather than credited with a property their callers supply.
    #
    # WHAT IT COSTS TO BE UNGUARDED, measured at `00c50ed3f`: a repo declaring
    # `runtime_budgets` and a `startup_probes` entry under `version: 9` was told
    # `quality adapter has no effective runtime budget for the selected profile` and
    # `quality adapter has no startup_probes`, exit 0 -- advisory-shaped findings asserting
    # the OPPOSITE of what the repo declared, on the surface that decides whether a gate's
    # cost is visible at all.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="quality-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    report = runtime_budget_lib.evaluate(
        repo_root,
        load_adapter,
        runtime_profile=runtime_profile,
        top_runtime_count=max(top_runtime_count, 0),
    )
    signals_present = (repo_root / RUNTIME_SIGNALS_PATH).is_file()
    lines = render_markdown_lines(report, repo_root=repo_root, signals_present=signals_present)
    hotspots = report.get("runtime_hotspots") or []
    summary = {
        "runtime_profile": report["runtime_profile"],
        "signals_path": str(RUNTIME_SIGNALS_PATH),
        "signals_present": signals_present,
        "runtime_hotspots": hotspots,
        "stale_runtime_hotspots": report.get("stale_runtime_hotspots", []),
        "runtime_visibility_findings": report.get("runtime_visibility_findings", []),
        "missing_samples": report.get("missing_samples", []),
        # The reviewer-facing surface is the stated final consumer of the runtime
        # advisories, and it carried every per-label list while never carrying the
        # one number the count exists to make legible.
        "unenforceable_budgets": report.get("unenforceable_budgets", {}),
        "commands_source": report.get("commands_source", "none"),
        "timing_log": report.get("timing_log", {}),
        "markdown_lines": lines,
    }
    # Inference-layer self-declaration rides the hot-spot ranking only; absent when
    # there are no hot spots so it never attaches to an empty/verified report.
    if hotspots:
        summary["interpretation"] = dict(INTERPRETATION)
    return summary


def summarize(report: dict[str, object], *, sample_limit: int = 5) -> dict[str, object]:
    hotspots = report.get("runtime_hotspots", [])
    stale_hotspots = report.get("stale_runtime_hotspots", [])
    return {
        "summary_note": "summary is triage output; use --detail for markdown evidence and all runtime hot spots",
        "runtime_profile": report["runtime_profile"],
        "signals_path": report["signals_path"],
        "signals_present": report["signals_present"],
        "commands_source": report["commands_source"],
        "runtime_hotspot_count": len(hotspots) if isinstance(hotspots, list) else 0,
        "runtime_hotspots_sample": hotspots[:sample_limit] if isinstance(hotspots, list) else [],
        "stale_runtime_hotspot_count": len(stale_hotspots) if isinstance(stale_hotspots, list) else 0,
        "stale_runtime_hotspots_sample": stale_hotspots[:sample_limit] if isinstance(stale_hotspots, list) else [],
        "runtime_visibility_finding_count": len(report["runtime_visibility_findings"]),
        "runtime_visibility_findings_sample": report["runtime_visibility_findings"][:sample_limit],
        "runtime_visibility_findings_truncated": len(report["runtime_visibility_findings"]) > sample_limit,
        "missing_sample_count": len(report["missing_samples"]),
        "missing_samples_sample": report["missing_samples"][:sample_limit],
        "missing_samples_truncated": len(report["missing_samples"]) > sample_limit,
        "unenforceable_budgets": report.get("unenforceable_budgets", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root whose runtime-signals.json should be rendered into a quality summary")
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML runtime hot-spot counts and samples",
        detail_help="Emit the full runtime summary as YAML",
    )
    parser.add_argument(
        "--runtime-profile",
        help="Named machine/runner profile to summarize. Defaults to CHARNESS_RUNTIME_PROFILE or adapter default.",
    )
    parser.add_argument(
        "--top-runtime-count",
        type=int,
        default=runtime_budget_lib.DEFAULT_TOP_RUNTIME_COUNT,
        help="Number of runtime hot spots to include.",
    )
    args = parser.parse_args()

    report = build_report(
        args.repo_root.resolve(),
        runtime_profile=args.runtime_profile,
        top_runtime_count=args.top_runtime_count,
    )
    if not _summary_output.emit_selected(report, args, summarize=summarize):
        print("\n".join(str(line) for line in report["markdown_lines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
