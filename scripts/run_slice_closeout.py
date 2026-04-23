#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
_scripts_plan_cautilus_proof_module = import_repo_module(__file__, "scripts.plan_cautilus_proof")
plan_cautilus_proof = _scripts_plan_cautilus_proof_module.plan_cautilus_proof
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
plan_risk_interrupt = _scripts_risk_interrupt_lib_module.plan_risk_interrupt


def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
    result = subprocess.run(
        ["/bin/bash", "-lc", command],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "phase": phase,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _emit_payload(payload: dict[str, object], *, as_json: bool, stderr_message: str | None = None) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
        if stderr_message is not None:
            print(stderr_message, file=sys.stderr)
    return 0 if payload["status"] not in {"blocked", "failed"} else 1


def _print_list(label: str, values: list[str]) -> None:
    if values:
        print(f"{label}:")
        for value in values:
            print(f"- {value}")
        return
    print(f"{label}: none")


def _cautilus_plan_has_visible_work(cautilus_plan: dict[str, object]) -> bool:
    return bool(
        cautilus_plan.get("required")
        or cautilus_plan.get("scenario_registry_review_required")
        or cautilus_plan.get("skill_validation_recommendations")
        or cautilus_plan.get("recommended_followups")
    )


def _print_cautilus_plan(cautilus_plan: dict[str, object]) -> None:
    print("Cautilus proof:")
    print(f"- run_mode: {cautilus_plan['run_mode']}")
    proof_kinds = cautilus_plan.get("proof_kinds", [])
    print(f"- proof_kinds: {', '.join(proof_kinds) if proof_kinds else 'none'}")
    print(f"- next_action: {cautilus_plan['next_action']}")
    changed_public_skills = cautilus_plan.get("changed_public_skills", [])
    if changed_public_skills:
        print(f"- changed_public_skills: {', '.join(changed_public_skills)}")
    if cautilus_plan.get("scenario_registry_review_required"):
        print("- scenario_registry_review_required: true")
    for note in cautilus_plan.get("notes", []):
        print(f"- note: {note}")
    for recommendation in cautilus_plan.get("skill_validation_recommendations", []):
        if isinstance(recommendation, dict):
            print(
                "- skill_review: "
                f"{recommendation.get('skill_id')} ({recommendation.get('validation_tier')})"
            )
    for followup in cautilus_plan.get("recommended_followups", []):
        print(f"- followup: {followup}")


def _print_risk_interrupt_plan(risk_interrupt_plan: dict[str, object]) -> None:
    print("Risk interrupt:")
    print(f"- status: {risk_interrupt_plan['status']}")
    for key in (
        "artifact_path",
        "interrupt_id",
        "handoff_artifact",
        "chosen_next_step",
        "impl_status",
        "next_action",
    ):
        value = risk_interrupt_plan.get(key)
        if value:
            print(f"- {key}: {value}")
    for reason in risk_interrupt_plan.get("reasons", []):
        print(f"- reason: {reason}")


def _print_executed_commands(payload: dict[str, object]) -> None:
    if not payload["executed_commands"]:
        return
    print("Executed commands:")
    for step in payload["executed_commands"]:
        status = "PASS" if step["returncode"] == 0 else "FAIL"
        print(f"- [{step['phase']}] {status} {step['command']}")
        if step["returncode"] != 0:
            if step["stdout"]:
                print(step["stdout"], end="" if step["stdout"].endswith("\n") else "\n")
            if step["stderr"]:
                print(step["stderr"], end="" if step["stderr"].endswith("\n") else "\n")


def print_text(payload: dict[str, object]) -> None:
    print(f"Closeout status: {payload['status']}")
    _print_list("Changed paths", payload["changed_paths"])
    matched_surfaces = [
        f"{surface['surface_id']}: {surface['description']}" for surface in payload["matched_surfaces"]
    ]
    _print_list("Matched surfaces", matched_surfaces)
    if payload["unmatched_paths"]:
        _print_list("Unmatched paths", payload["unmatched_paths"])

    cautilus_plan = payload.get("cautilus_plan")
    if isinstance(cautilus_plan, dict) and _cautilus_plan_has_visible_work(cautilus_plan):
        _print_cautilus_plan(cautilus_plan)

    risk_interrupt_plan = payload.get("risk_interrupt_plan")
    if isinstance(risk_interrupt_plan, dict) and risk_interrupt_plan.get("status") != "not-applicable":
        _print_risk_interrupt_plan(risk_interrupt_plan)

    _print_executed_commands(payload)


def _maybe_block_on_unmatched(payload: dict[str, object], *, allow_unmatched: bool, as_json: bool) -> int | None:
    if not payload["unmatched_paths"] or allow_unmatched:
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        "changed paths are not covered by the surfaces manifest; "
        "add the missing coverage or rerun with --allow-unmatched"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def _maybe_block_on_cautilus(
    repo_root: Path, payload: dict[str, object], *, as_json: bool, ack_skill_review: bool
) -> int | None:
    cautilus_plan = plan_cautilus_proof(repo_root, payload["changed_paths"])
    payload["cautilus_plan"] = cautilus_plan
    if not (cautilus_plan["required"] and not cautilus_plan["artifact_changed"]):
        if cautilus_plan["skill_validation_recommendations"] and not ack_skill_review:
            payload["status"] = "blocked"
            payload["error"] = (
                "public-skill validation review is required for this slice; inspect the dogfood/scenario "
                "follow-ups in `cautilus_plan` and rerun with --ack-cautilus-skill-review after recording "
                "the decision"
            )
            return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        f"cautilus proof is required for this slice; next_action=`{cautilus_plan['next_action']}` "
        f"and `{cautilus_plan['artifact_path']}` is not refreshed yet"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def _maybe_block_on_risk_interrupt(
    repo_root: Path, payload: dict[str, object], *, as_json: bool
) -> int | None:
    risk_interrupt_plan = plan_risk_interrupt(repo_root, payload["changed_paths"])
    payload["risk_interrupt_plan"] = risk_interrupt_plan
    if risk_interrupt_plan["status"] != "blocked":
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        f"risk interrupt is blocking ordinary closeout; next_action=`{risk_interrupt_plan['next_action']}`"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument("--plan-only", action="store_true", help="Print obligations without executing commands.")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument(
        "--ack-cautilus-skill-review",
        action="store_true",
        help=(
            "Acknowledge that public-skill dogfood/scenario review follow-ups from the Cautilus planner "
            "were inspected and the scenario-registry decision was recorded."
        ),
    )
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Proceed even when changed files are not covered by the surfaces manifest.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["executed_commands"] = []

    if not payload["changed_paths"]:
        payload["status"] = "noop"
        return _emit_payload(payload, as_json=args.json)

    blocked = _maybe_block_on_unmatched(payload, allow_unmatched=args.allow_unmatched, as_json=args.json)
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_cautilus(
        repo_root,
        payload,
        as_json=args.json,
        ack_skill_review=args.ack_cautilus_skill_review,
    )
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_risk_interrupt(repo_root, payload, as_json=args.json)
    if blocked is not None:
        return blocked

    command_plan: list[tuple[str, str]] = []
    if not args.skip_sync:
        command_plan.extend(("sync", command) for command in payload["sync_commands"])
    if not args.skip_verify:
        command_plan.extend(("verify", command) for command in payload["verify_commands"])

    if args.plan_only:
        payload["status"] = "planned"
        payload["planned_commands"] = [
            {"phase": phase, "command": command} for phase, command in command_plan
        ]
        return _emit_payload(payload, as_json=args.json)

    for phase, command in command_plan:
        result = run_command(repo_root, command, phase)
        payload["executed_commands"].append(result)
        if result["returncode"] != 0:
            payload["status"] = "failed"
            return _emit_payload(payload, as_json=args.json)

    payload["status"] = "completed"
    return _emit_payload(payload, as_json=args.json)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
