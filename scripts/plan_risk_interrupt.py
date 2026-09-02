#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    repo_root_from_script,
    require_repo_local_helper,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

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
    parser.add_argument(
        "--detail", action="store_true", help="Emit the full risk-interrupt plan as YAML."
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Optional repo-relative changed paths for current-slice affinity.",
    )
    args = parser.parse_args()

    target_root = args.repo_root.resolve()
    # This planner is also reached through an installed plugin's shared shim.
    # Refuse a stale installed copy before it can interpret or persist source-tree
    # state; ordinary consumer repos remain allowed by the provenance guard.
    require_repo_local_helper(__file__, target_root, scan="tree")
    plan = plan_risk_interrupt(target_root, changed_paths=args.paths)
    if args.detail:
        emit_yaml(plan)
    else:
        _print_text(plan)
    return 0 if plan["status"] != "blocked" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
