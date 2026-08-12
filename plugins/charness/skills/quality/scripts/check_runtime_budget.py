#!/usr/bin/env python3
"""Enforce per-command runtime budgets recorded in runtime-signals.json."""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, bounded_list, emit_selected  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
runtime_budget_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_lib")
runtime_budget_sizing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_sizing_lib")


def summarize(report: dict) -> dict:
    checked = report.get("checked", [])
    violations = report.get("violations", [])
    summary = {
        "summary_note": "summary is triage output; use --detail for all checked runtime samples",
        "runtime_profile": report.get("runtime_profile"),
        "budgets_configured": report.get("budgets_configured"),
        "commands_observed": report.get("commands_observed"),
        "status": "violations" if violations else "ok",
        "checked_status_counts": {
            "ok": sum(1 for item in checked if item.get("status") == "ok"),
            "other": sum(1 for item in checked if item.get("status") != "ok"),
        },
    }
    for key in (
        "violations",
        "budget_slack_findings",
        "latest_spikes",
        "profile_config_errors",
        "runtime_visibility_findings",
    ):
        summary.update(bounded_list(report, key))
    summary["advisory_contracts"] = report.get("advisory_contracts", {})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root whose runtime-signals.json budgets should be enforced")
    add_output_args(
        parser,
        summary_help="Emit compact YAML runtime-budget status and violations",
        detail_help="Emit the full runtime-budget report as YAML",
    )
    parser.add_argument(
        "--runtime-profile",
        help="Named machine/runner profile to enforce. Defaults to CHARNESS_RUNTIME_PROFILE or adapter default.",
    )
    parser.add_argument(
        "--suggest-budgets",
        action="store_true",
        help="Print a paste-ready runtime_budget_profiles block derived from this profile's recorded samples, then exit.",
    )
    parser.add_argument(
        "--top-runtime-count",
        type=int,
        default=runtime_budget_lib.DEFAULT_TOP_RUNTIME_COUNT,
        help="Number of recent runtime hot spots to include in the report.",
    )
    args = parser.parse_args()

    if args.suggest_budgets:
        # The output is a YAML fragment with comments carrying the evidence depth.
        # Honoring `--json`/`--summary` here would either drop those comments or emit
        # YAML to a caller that parses JSON, so the combination is a usage error
        # rather than a silently wrong shape.
        if args.json or args.summary or args.detail:
            parser.error("--suggest-budgets emits a YAML fragment; it cannot be combined with --json/--summary/--detail")
        profile, suggestions, commands_source = runtime_budget_sizing_lib.suggest_budgets(
            args.repo_root.resolve(),
            load_adapter,
            runtime_budget_lib.load_signals,
            runtime_profile=args.runtime_profile,
        )
        if not suggestions:
            print(
                f"runtime profile `{profile}` has no recorded samples to derive budgets from; "
                f"run the gates once on a machine that records under `{profile}` first "
                "(running them here files samples under THIS machine's profile, which "
                "produces nothing for a profile you named explicitly)",
                file=sys.stderr,
            )
            return 1
        print(runtime_budget_sizing_lib.format_budget_suggestion(profile, suggestions, commands_source=commands_source))
        return 0

    report = runtime_budget_lib.evaluate(
        args.repo_root.resolve(),
        load_adapter,
        runtime_profile=args.runtime_profile,
        top_runtime_count=max(args.top_runtime_count, 0),
    )
    if not emit_selected(report, args, summarize=summarize):
        print(runtime_budget_lib.format_human(report))

    if report["profile_config_errors"]:
        if not args.json:
            for error in report["profile_config_errors"]:
                print(f"runtime profile configuration error: {error}", file=sys.stderr)
        return 1
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
