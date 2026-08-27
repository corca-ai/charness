#!/usr/bin/env python3
"""Text-mode rendering of the slice-closeout payload.

Extracted verbatim from run_slice_closeout.py (behavior-preserving) so the
orchestrator stays under its length limit. ``print_text`` is the single
entrypoint the orchestrator calls; the ``_print_*`` helpers and
The only cross-module dependency is ``print_broad_pytest_policy`` from
``slice_closeout_broad_gate``, imported the same parent-walk way the orchestrator
does so it resolves in both the source tree and the exported plugin.
"""
from __future__ import annotations

from runtime_bootstrap import import_repo_module

_slice_closeout_broad_gate = import_repo_module(__file__, "scripts.slice_closeout_broad_gate")
print_broad_pytest_policy = _slice_closeout_broad_gate.print_broad_pytest_policy
_proof_receipt = import_repo_module(__file__, "scripts.proof_receipt")
closeout_receipt = _proof_receipt.closeout_receipt
render_closeout_verdict = _proof_receipt.render_closeout_verdict


def _print_list(label: str, values: list[str]) -> None:
    if values:
        print(f"{label}:")
        for value in values:
            print(f"- {value}")
        return
    print(f"{label}: none")


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


def _print_mutation_coverage_proof(payload: dict[str, object]) -> None:
    proof = payload.get("mutation_coverage_changed_line_proof")
    if not isinstance(proof, dict) or proof.get("status") != "not_checked":
        return
    print("Mutation changed-line proof: NOT CHECKED")
    if proof.get("reason"):
        print(f"- reason: {proof['reason']}")
    files = proof.get("uncommitted_eligible_files")
    if isinstance(files, list):
        print(f"- excluded eligible files: {', '.join(str(path) for path in files)}")
    if proof.get("command"):
        print(f"- consumer command: {proof['command']}")


def print_text(payload: dict[str, object]) -> None:
    print(f"Closeout status: {payload['status']}")
    _print_list("Changed paths", payload["changed_paths"])
    matched_surfaces = [
        f"{surface['surface_id']}: {surface['description']}" for surface in payload["matched_surfaces"]
    ]
    _print_list("Matched surfaces", matched_surfaces)
    if payload["unmatched_paths"]:
        _print_list("Unmatched paths", payload["unmatched_paths"])

    risk_interrupt_plan = payload.get("risk_interrupt_plan")
    if isinstance(risk_interrupt_plan, dict) and risk_interrupt_plan.get("status") != "not-applicable":
        _print_risk_interrupt_plan(risk_interrupt_plan)

    _print_headroom(payload)
    print_broad_pytest_policy(payload)
    _print_mutation_coverage_proof(payload)
    _print_executed_commands(payload)
    _print_final_verdict(payload)


def _print_final_verdict(payload: dict[str, object]) -> None:
    """Repeat the semantic closeout receipt last for truncating readers."""
    effective_exit_code = int(
        payload.get("effective_exit_code", 1 if payload.get("status") in {"blocked", "failed"} else 0)
    )
    receipt = closeout_receipt(payload, effective_exit_code=effective_exit_code)
    print(render_closeout_verdict(receipt))
