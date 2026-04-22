#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
ValidationError = _scripts_risk_interrupt_lib_module.ValidationError
plan_risk_interrupt = _scripts_risk_interrupt_lib_module.plan_risk_interrupt


def _print_text(plan: dict[str, object]) -> None:
    print(f"Status: {plan['status']}")
    if "artifact_path" in plan:
        print(f"Artifact: {plan['artifact_path']}")
    if "interrupt_id" in plan:
        print(f"Interrupt ID: {plan['interrupt_id']}")
    if "risk_classes" in plan:
        print("Risk Classes: " + ", ".join(plan["risk_classes"]))
    if "handoff_artifact" in plan:
        print(f"Handoff Artifact: {plan['handoff_artifact']}")
    if "chosen_next_step" in plan:
        print(f"Chosen Next Step: {plan['chosen_next_step']}")
    if "impl_status" in plan:
        print(f"Impl Status: {plan['impl_status']}")
    if "next_action" in plan:
        print(f"Next Action: {plan['next_action']}")
    for reason in plan.get("reasons", []):
        print(f"- {reason}")
    if "reason" in plan:
        print(plan["reason"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="*", help="Optional repo-relative changed paths for current-slice affinity.")
    args = parser.parse_args()

    plan = plan_risk_interrupt(args.repo_root.resolve(), changed_paths=args.paths)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        _print_text(plan)
    return 0 if plan["status"] != "blocked" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
