#!/usr/bin/env python3

"""Inventory costly local standing gates whose proof CI fully re-runs.

This is the explicit counterweight to `inventory_ci_local_gate_parity.py` (the
local-proof guardrail). It cross-references each costly local standing gate —
ranked by measured local wall-clock from the runtime signals / command-timing
log — against the repo's CI workflow `run:` steps, and flags the gates CI fully
re-runs as candidates to move OFF the local hot path. Gates CI does not re-run
are reported as `keep-local` and are never recommended for moving.

Advisory only: no exit-code gate. The operator confirms each candidate against
the declared interpretation question before moving proof off the local path.

Silent-ish when there is no cost signal: with no runtime_budgets, no
runtime-signals.json samples, and no command_timing_log, there are no ranked
gates to triage, and the report says so (mirroring render_runtime_summary).
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
runtime_budget_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_lib")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_local_gate_parity_lib as parity_lib  # noqa: E402
import ci_recoverable_gates_lib as lens_lib  # noqa: E402


def _load_workflows(root: Path, glob_pattern: str, *, require_git: bool) -> list[dict[str, Any]]:
    workflows: list[dict[str, Any]] = []
    for path in parity_lib.iter_workflow_files(root, glob_pattern, require_git=require_git):
        parsed = parity_lib.parse_workflow(path, load_yaml_file)
        workflows.append(
            {
                "workflow": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
                "data": parsed["data"],
                "gate_policy": parity_lib.read_gate_policy(parsed["text"], workflow_label=str(path)),
            }
        )
    return workflows


def build_report(root: Path, *, glob_pattern: str, runtime_profile: str | None, require_git: bool) -> dict[str, Any]:
    runtime_report = runtime_budget_lib.evaluate(root, load_adapter, runtime_profile=runtime_profile)
    gates = lens_lib.gates_from_runtime_report(runtime_report)
    workflows = _load_workflows(root, glob_pattern, require_git=require_git)
    corpus = lens_lib.ci_step_corpus(workflows)
    classified = lens_lib.classify_gates(gates, corpus)
    return {
        "runtime_profile": runtime_report["runtime_profile"],
        "commands_source": runtime_report.get("commands_source", "none"),
        "workflows_scanned": len(workflows),
        "gates_considered": len(gates),
        "candidates": classified["candidates"],
        "keep_local": classified["keep_local"],
        "interpretation": dict(lens_lib.INTERPRETATION),
    }


def _format_ms(ms: int | None) -> str:
    if ms is None:
        return "wall-clock unknown"
    return f"{ms / 1000:.1f}s" if ms >= 1000 else f"{ms}ms"


def _print_text(report: dict[str, Any]) -> None:
    print(
        f"CI-recoverable gate triage: {report['workflows_scanned']} workflow(s) scanned; "
        f"{report['gates_considered']} cost-ranked gate(s); "
        f"{len(report['candidates'])} CI-recoverable candidate(s); "
        f"{len(report['keep_local'])} keep-local."
    )
    if not report["gates_considered"]:
        print(
            "  no cost-ranked standing gates: configure `runtime_budgets`, capture "
            "`.charness/quality/runtime-signals.json` samples, or declare a "
            "`command_timing_log` adapter key so gates can be ranked by wall-clock."
        )
        return
    for cand in report["candidates"]:
        policies = ", ".join(cand.get("ci_gate_policies") or []) or "no gate-policy marker"
        steps = "; ".join(
            f"{s['workflow']}::{s['job']}" + (f" ({s['name']})" if s.get("name") else "")
            for s in cand.get("ci_steps", [])
        )
        print(
            f"  candidate {cand['label']} [{_format_ms(cand['wall_clock_ms'])}] — "
            f"CI re-runs via {steps} [{policies}]"
        )
    if report["candidates"]:
        print(
            "  confirm each candidate against the interpretation question before moving "
            "proof off the local hot path; keep the CI step as the backstop."
        )
    for gate in report["keep_local"]:
        print(f"  keep-local {gate['label']} [{_format_ms(gate['wall_clock_ms'])}] — no CI step re-runs this proof")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root for the CI-recoverable gate triage")
    parser.add_argument(
        "--workflow-glob",
        default=parity_lib.DEFAULT_WORKFLOW_GLOB,
        help=f"glob for CI workflow files (default: {parity_lib.DEFAULT_WORKFLOW_GLOB})",
    )
    parser.add_argument(
        "--runtime-profile",
        help="Named machine/runner profile for wall-clock ranking. Defaults to CHARNESS_RUNTIME_PROFILE or adapter default.",
    )
    parser.add_argument("--require-git-file-listing", action="store_true", help="Fail when git ls-files is unavailable for workflow discovery")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    report = build_report(
        root,
        glob_pattern=args.workflow_glob,
        runtime_profile=args.runtime_profile,
        require_git=args.require_git_file_listing,
    )
    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _print_text(report)
        print(
            "  interpretation (inference-layer trend, not a verdict): "
            f"measures {report['interpretation']['measures']}; "
            f"blind spots: {report['interpretation']['blind_spots']}. "
            f"Answer first: {report['interpretation']['interpretation_question']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
