#!/usr/bin/env python3
"""Text-mode rendering of the slice-closeout payload.

Extracted verbatim from run_slice_closeout.py (behavior-preserving) so the
orchestrator stays under its length limit. ``print_text`` is the single
entrypoint the orchestrator calls; the ``_print_*`` helpers and
``_cautilus_plan_has_visible_work`` are internal to this module. The only
cross-module dependency is ``print_broad_pytest_policy`` from
``slice_closeout_broad_gate``, imported the same parent-walk way the orchestrator
does so it resolves in both the source tree and the exported plugin.
"""
from __future__ import annotations

from runtime_bootstrap import import_repo_module

_slice_closeout_broad_gate = import_repo_module(__file__, "scripts.slice_closeout_broad_gate")
print_broad_pytest_policy = _slice_closeout_broad_gate.print_broad_pytest_policy


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


def _print_headroom(payload: dict[str, object]) -> None:
    # Advisory (#256): surface changed gated files already near the length limit
    # so the next slice chooses new-module-vs-append before writing. Never blocks.
    rows = payload.get("headroom")
    near = [row for row in rows if row.get("near_limit")] if isinstance(rows, list) else []
    if not near:
        return
    print("WARN: changed files near the length limit (consider a new module before adding more):")
    for row in near:
        print(
            f"- {row['path']}: {row['lines']}/{row['limit']} code lines "
            f"({row['headroom']} left)"
        )


def _print_usage_episode(payload: dict[str, object]) -> None:
    usage_episode = payload.get("usage_episode")
    if not isinstance(usage_episode, dict):
        return
    print("Usage episode:")
    print(f"- status: {usage_episode['status']}")
    if usage_episode.get("records_path"):
        print(f"- records_path: {usage_episode['records_path']}")
    if usage_episode.get("episode_id"):
        print(f"- episode_id: {usage_episode['episode_id']}")
    if usage_episode.get("error"):
        print(f"- error: {usage_episode['error']}")


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

    _print_headroom(payload)
    print_broad_pytest_policy(payload)
    _print_executed_commands(payload)
    _print_usage_episode(payload)
