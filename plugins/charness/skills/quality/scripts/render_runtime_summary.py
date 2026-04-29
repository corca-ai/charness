#!/usr/bin/env python3
"""Render quality runtime metrics for a checked-in quality summary."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


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
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
runtime_budget_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_lib")

RUNTIME_SIGNALS_PATH = Path(".charness") / "quality" / "runtime-signals.json"


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


def render_markdown_lines(report: dict[str, object], *, repo_root: Path, signals_present: bool) -> list[str]:
    profile = str(report["runtime_profile"])
    hotspots = report.get("runtime_hotspots")
    if not isinstance(hotspots, list):
        hotspots = []

    if hotspots:
        recorder = repo_root / "scripts" / "record_quality_runtime.py"
        provenance = (
            " via `scripts/record_quality_runtime.py`"
            if recorder.is_file()
            else ""
        )
        source = (
            "- runtime source: structured metrics from "
            f"`{RUNTIME_SIGNALS_PATH}` rendered by `render_runtime_summary.py`{provenance}; profile `{profile}`."
        )
        hot_spots = f"- runtime hot spots: {_format_hotspots(hotspots)}."
        return [source, hot_spots]

    if signals_present:
        return [
            "- runtime source: structured metrics file "
            f"`{RUNTIME_SIGNALS_PATH}` has no samples for profile `{profile}`.",
            "- runtime hot spots: unavailable until structured runtime metrics have samples.",
        ]
    return [
        "- runtime source: not configured; add structured timing capture before reporting timing trends.",
        "- runtime hot spots: unavailable until structured runtime metrics have samples.",
    ]


def build_report(repo_root: Path, *, runtime_profile: str | None, top_runtime_count: int) -> dict[str, object]:
    report = runtime_budget_lib.evaluate(
        repo_root,
        load_adapter,
        runtime_profile=runtime_profile,
        top_runtime_count=max(top_runtime_count, 0),
    )
    signals_present = (repo_root / RUNTIME_SIGNALS_PATH).is_file()
    lines = render_markdown_lines(report, repo_root=repo_root, signals_present=signals_present)
    return {
        "runtime_profile": report["runtime_profile"],
        "signals_path": str(RUNTIME_SIGNALS_PATH),
        "signals_present": signals_present,
        "runtime_hotspots": report.get("runtime_hotspots", []),
        "missing_samples": report.get("missing_samples", []),
        "markdown_lines": lines,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
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
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n".join(str(line) for line in report["markdown_lines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
