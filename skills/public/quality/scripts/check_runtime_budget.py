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
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)
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
        "status": (
            "configuration-error"
            if report.get("profile_config_errors")
            else "violations"
            if violations
            else "ok"
        ),
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
    # First-class in the SUMMARY, not only in --detail: "how many committed bars are
    # unenforceable on this machine" is a triage question, and triage output is what a
    # reviewer reads. The label list rides the SAME `bounded_list` every other list in
    # this summary uses -- it already emits a count alongside the truncated sample, so
    # bounding it loses nothing the dict below does not also carry.
    summary.update(bounded_list(report, "missing_samples"))
    summary["unenforceable_budgets"] = report.get("unenforceable_budgets", {})
    summary["advisory_contracts"] = report.get("advisory_contracts", {})
    summary["runtime_budget_universe"] = report.get("runtime_budget_universe", {})
    return summary


def _refuse_unhonored_adapter(repo_root: Path) -> None:
    """Both of this CLI's adapter reads go through `runtime_budget_lib` /
    `runtime_budget_sizing_lib`, which take the loader INJECTED and so cannot know which
    adapter they are reading or refuse for it. That seam is deliberate, so the guard lives
    here, at the point the loader is handed over.

    Measured at `00c50ed3f`: a repo declaring `runtime_budgets` and a `startup_probes`
    entry under `version: 9` was told `quality adapter has no effective runtime budget for
    the selected profile` and `quality adapter has no startup_probes`, exit 0 -- two
    advisory-shaped findings asserting the OPPOSITE of what the repo declared. `main()`
    branches on `profile_config_errors` and never on the adapter's own `errors`, so
    nothing downstream could have caught it.
    """
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="quality-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)


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
        "--state-root",
        type=Path,
        help="External quality runtime-state directory; defaults to <repo>/.charness/quality.",
    )
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Report median budget violations without failing; configuration errors still fail.",
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
    state_root = args.state_root.resolve() if args.state_root else None
    if state_root is not None:
        repo_root = args.repo_root.resolve()
        if state_root == repo_root or repo_root in state_root.parents:
            parser.error("--state-root must be outside --repo-root")

    if args.suggest_budgets:
        # The output is a YAML fragment with comments carrying the evidence depth.
        # Summary/detail would replace the comment-carrying fragment with the
        # ordinary report shape, so the combination is a usage error.
        if args.summary or args.detail:
            parser.error("--suggest-budgets emits a YAML fragment; it cannot be combined with --summary/--detail")
        _refuse_unhonored_adapter(args.repo_root.resolve())
        profile, suggestions, commands_source = runtime_budget_sizing_lib.suggest_budgets(
            args.repo_root.resolve(),
            load_adapter,
            runtime_budget_lib.load_signals,
            runtime_profile=args.runtime_profile,
            state_root=state_root,
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

    _refuse_unhonored_adapter(args.repo_root.resolve())
    report = runtime_budget_lib.evaluate(
        args.repo_root.resolve(),
        load_adapter,
        runtime_profile=args.runtime_profile,
        top_runtime_count=max(args.top_runtime_count, 0),
        state_root=state_root,
    )
    if not emit_selected(report, args, summarize=summarize):
        print(runtime_budget_lib.format_human(report))

    if report["profile_config_errors"]:
        for error in report["profile_config_errors"]:
            print(f"runtime profile configuration error: {error}", file=sys.stderr)
        return 1
    if report["violations"]:
        for v in report["violations"]:
            print(
                ("ADVISORY: " if args.advisory else "")
                + "runtime budget exceeded: "
                f"{v['label']} recent median {v['median_recent_elapsed_ms']}ms "
                f"(latest {v['latest_elapsed_ms']}ms, budget {v['budget_ms']}ms)",
                file=sys.stderr,
            )
        if not args.advisory:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
